
from dataclasses import dataclass, field
from pathlib import Path

import pymupdf

from ..understanding.layout_analyzer import (
    analyze_page_layout,
    extract_layout_regions,
    reconstruct_reading_order,
)


@dataclass
class PDFExtractionResult:
    file_name: str
    extracted_text: str
    total_pages: int
    successful: bool
    error: str = ""
    text_regions: list[str] = field(default_factory=list)
    hyperlinks: list[dict] = field(default_factory=list)


def extract_pdf_text(file_path: Path) -> PDFExtractionResult:
    """
    Extract text from a digital PDF using spatial layout analysis.

    Reconstructs approximate reading order for single-column
    and two-column pages.
    """

    file_path = Path(file_path)

    try:
        extracted_pages = []
        all_text_regions = []
        all_hyperlinks = []

        with pymupdf.open(file_path) as pdf:

            if pdf.is_encrypted:
                raise ValueError("Password-protected PDF")

            if len(pdf) == 0:
                raise ValueError("PDF contains no pages")

            for page_number, page in enumerate(pdf, start=1):

                # Capture clickable URI annotations (e.g. LinkedIn/GitHub).
                for link in page.get_links():
                    uri = link.get("uri")
                    rect_data = link.get("from")
                    if not uri:
                        continue
                    link_text = ""
                    if rect_data:
                        link_rect = pymupdf.Rect(rect_data)
                        words = page.get_text("words")
                        matched = [
                            word[4] for word in words
                            if pymupdf.Rect(word[:4]).intersects(link_rect)
                        ]
                        link_text = " ".join(matched).strip()
                    all_hyperlinks.append({"url": uri, "text": link_text, "page": page_number})

                layout = analyze_page_layout(
                    page,
                    page_number
                )

                regions = extract_layout_regions(layout)

                for region_number, region_text in enumerate(
                    regions, start=1
                ):
                    all_text_regions.append(
                        f"--- PAGE {page_number} | REGION {region_number} ---\n"
                        f"{region_text}"
                    )

                page_text = reconstruct_reading_order(
                    layout
                )

                extracted_pages.append(
                    f"\n--- PAGE {page_number} ---\n{page_text}"
                )

            full_text = "\n".join(extracted_pages).strip()

            return PDFExtractionResult(
                file_name=file_path.name,
                extracted_text=full_text,
                total_pages=len(pdf),
                successful=True,
                text_regions=all_text_regions,
                hyperlinks=all_hyperlinks
            )

    except Exception as error:

        return PDFExtractionResult(
            file_name=file_path.name,
            extracted_text="",
            total_pages=0,
            successful=False,
            error=str(error)
        )
