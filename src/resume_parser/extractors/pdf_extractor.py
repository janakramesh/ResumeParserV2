from dataclasses import dataclass, field
from pathlib import Path

import pymupdf

from ..understanding.layout_analyzer import (
    analyze_page_layout,
    extract_layout_regions,
    reconstruct_reading_order,
)
from .ocr_extractor import OCRConfig, extract_image_text


@dataclass
class PDFExtractionResult:
    file_name: str
    extracted_text: str
    total_pages: int
    successful: bool
    error: str = ""
    text_regions: list[str] = field(default_factory=list)
    hyperlinks: list[dict] = field(default_factory=list)
    ocr_pages: list[int] = field(default_factory=list)
    page_methods: list[str] = field(default_factory=list)
    page_errors: list[dict] = field(default_factory=list)


def _has_usable_native_text(text: str, config: OCRConfig) -> bool:
    compact = " ".join(text.split())
    if len(compact) < config.min_native_chars:
        return False
    visible = [char for char in compact if not char.isspace()]
    if not visible:
        return False
    alpha_numeric = sum(char.isalnum() for char in visible)
    return alpha_numeric / len(visible) >= config.min_alpha_ratio


def extract_pdf_text(file_path: Path, ocr_config: OCRConfig | None = None) -> PDFExtractionResult:
    """Extract each page natively when useful, otherwise render and OCR it."""
    file_path = Path(file_path)
    config = ocr_config or OCRConfig()
    extracted_pages: list[str] = []
    all_text_regions: list[str] = []
    all_hyperlinks: list[dict] = []
    ocr_pages: list[int] = []
    page_methods: list[str] = []
    page_errors: list[dict] = []

    try:
        with pymupdf.open(file_path) as pdf:
            if pdf.is_encrypted:
                raise ValueError("Password-protected PDF")
            if len(pdf) == 0:
                raise ValueError("PDF contains no pages")

            for page_number, page in enumerate(pdf, start=1):
                for link in page.get_links():
                    uri = link.get("uri")
                    rect_data = link.get("from")
                    if not uri:
                        continue
                    link_text = ""
                    if rect_data:
                        link_rect = pymupdf.Rect(rect_data)
                        matched = [
                            word[4] for word in page.get_text("words")
                            if pymupdf.Rect(word[:4]).intersects(link_rect)
                        ]
                        link_text = " ".join(matched).strip()
                    all_hyperlinks.append({"url": uri, "text": link_text, "page": page_number})

                native_text = ""
                regions = []
                try:
                    layout = analyze_page_layout(page, page_number)
                    native_text = reconstruct_reading_order(layout).strip()
                    regions = extract_layout_regions(layout)
                except Exception as exc:
                    page_errors.append({"page": page_number, "stage": "native", "error": str(exc)})

                if _has_usable_native_text(native_text, config):
                    page_text = native_text
                    page_methods.append("native")
                    all_text_regions.extend(
                        f"--- PAGE {page_number} | REGION {idx} ---\n{region}"
                        for idx, region in enumerate(regions, start=1)
                    )
                else:
                    try:
                        pixmap = page.get_pixmap(dpi=config.dpi, alpha=False)
                        image = pixmap.pil_image() if hasattr(pixmap, "pil_image") else None
                        if image is None:
                            from PIL import Image
                            image = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
                        ocr_result = extract_image_text(image, config)
                        if ocr_result.successful and ocr_result.extracted_text.strip():
                            page_text = ocr_result.extracted_text
                            page_methods.append("ocr")
                            ocr_pages.append(page_number)
                        else:
                            page_text = native_text
                            page_methods.append("native_fallback")
                            page_errors.append({
                                "page": page_number, "stage": "ocr",
                                "error": ocr_result.error or "OCR returned no text",
                            })
                    except Exception as exc:
                        page_text = native_text
                        page_methods.append("native_fallback")
                        page_errors.append({"page": page_number, "stage": "render_ocr", "error": str(exc)})

                extracted_pages.append(f"--- PAGE {page_number} ---\n{page_text}".rstrip())

            full_text = "\n\n".join(extracted_pages).strip()
            return PDFExtractionResult(
                file_name=file_path.name, extracted_text=full_text,
                total_pages=len(pdf), successful=True,
                text_regions=all_text_regions, hyperlinks=all_hyperlinks,
                ocr_pages=ocr_pages, page_methods=page_methods,
                page_errors=page_errors,
            )
    except Exception as error:
        return PDFExtractionResult(
            file_name=file_path.name, extracted_text="", total_pages=0,
            successful=False, error=str(error), ocr_pages=ocr_pages,
            page_methods=page_methods, page_errors=page_errors,
        )
