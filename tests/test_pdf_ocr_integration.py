import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pymupdf
from PIL import Image

from src.resume_parser.extraction_engine import ResumeExtractionEngine
from src.resume_parser.extractors.ocr_extractor import OCRResult
from src.resume_parser.extractors.pdf_extractor import (
    PDFExtractionResult,
    extract_pdf_text,
)


class PDFOCRIntegrationTests(unittest.TestCase):
    def test_native_pdf_page_does_not_call_ocr(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "digital.pdf"
            doc = pymupdf.open()
            page = doc.new_page()
            page.insert_text((72, 72), "Jane Doe Python Developer " * 8)
            doc.save(path)
            doc.close()
            with patch("src.resume_parser.extractors.pdf_extractor.extract_image_text") as ocr:
                result = extract_pdf_text(path)
            self.assertTrue(result.successful)
            self.assertEqual(result.page_methods, ["native"])
            ocr.assert_not_called()

    def test_scanned_pdf_page_uses_ocr(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "scan.pdf"
            doc = pymupdf.open()
            page = doc.new_page()
            page.insert_image(pymupdf.Rect(40, 40, 550, 750), stream=_png_bytes())
            doc.save(path)
            doc.close()
            with patch(
                "src.resume_parser.extractors.pdf_extractor.extract_image_text",
                return_value=OCRResult("OCR RESUME TEXT", True, 91),
            ) as ocr:
                result = extract_pdf_text(path)
            self.assertTrue(result.successful)
            self.assertEqual(result.ocr_pages, [1])
            self.assertIn("OCR RESUME TEXT", result.extracted_text)
            ocr.assert_called_once()

    def test_scanned_pdf_ocr_text_is_analyzed_into_structured_json(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            resume_path = root / "scan.pdf"
            extracted_text = (
                "HENRY JACKSON\n\n"
                "SUMMARY\n"
                "Experienced technology leader.\n\n"
                "CORE COMPETENCIES\n"
                "Cloud Computing, Software Development\n\n"
                "EXPERIENCE\n"
                "Chief Technology Officer\n\n"
                "EDUCATION\n"
                "Master of Science in Computer Science"
            )
            result = PDFExtractionResult(
                file_name=resume_path.name,
                extracted_text=extracted_text,
                total_pages=1,
                successful=True,
                ocr_pages=[1],
                page_methods=["ocr"],
            )
            with patch(
                "src.resume_parser.extraction_engine.setup_logger"
            ):
                engine = ResumeExtractionEngine(root, root / "output")

            with patch(
                "src.resume_parser.extraction_engine.extract_pdf_text",
                return_value=result,
            ):
                processing_result = engine.process_resume(
                    SimpleNamespace(path=resume_path, file_type="PDF")
                )

            self.assertTrue(processing_result.successful)
            self.assertEqual(processing_result.total_sections, 4)
            self.assertTrue(processing_result.structured_output_path)

            structured_data = json.loads(
                Path(processing_result.structured_output_path).read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(structured_data["name"], "HENRY JACKSON")
            self.assertEqual(
                structured_data["technical_skills"],
                "Cloud Computing, Software Development",
            )
            self.assertIn("Chief Technology Officer", structured_data["experience"])


def _png_bytes():
    import io
    stream = io.BytesIO()
    Image.new("RGB", (400, 600), "white").save(stream, format="PNG")
    return stream.getvalue()


if __name__ == "__main__":
    unittest.main()
