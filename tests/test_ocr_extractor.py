import os
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image

from src.resume_parser.extractors.ocr_extractor import (
    OCRConfig, _load_tesseract, extract_image_text, preprocess_image,
)


class FakeOutput:
    DICT = "dict"


class FakeTesseract:
    Output = FakeOutput

    class pytesseract:
        tesseract_cmd = None

    @staticmethod
    def image_to_string(image, **kwargs):
        return "Jane Doe\nPython Developer"

    @staticmethod
    def image_to_data(image, **kwargs):
        return {"conf": ["90", "80", "-1"]}


class OCRExtractorTests(unittest.TestCase):
    @patch.dict(os.environ, {"TESSERACT_CMD": ""})
    @patch("src.resume_parser.extractors.ocr_extractor.Path.is_file", return_value=True)
    def test_load_tesseract_finds_games_install(self, _is_file):
        import pytesseract

        with patch.object(pytesseract.pytesseract, "tesseract_cmd", "tesseract"):
            loaded = _load_tesseract(OCRConfig())
        self.assertIs(loaded, pytesseract)
        self.assertEqual(
            loaded.pytesseract.tesseract_cmd,
            str(Path(r"C:\Games\tesseract\tesseract.exe")),
        )

    def test_preprocessing_returns_grayscale_image(self):
        image = Image.new("RGB", (100, 80), "white")
        result = preprocess_image(image, OCRConfig(upscale_factor=2, auto_rotate=False, deskew=False))
        self.assertEqual(result.mode, "L")
        self.assertEqual(result.size, (200, 160))

    @patch("src.resume_parser.extractors.ocr_extractor._load_tesseract", return_value=FakeTesseract)
    def test_image_ocr_success(self, _mock):
        result = extract_image_text(
            Image.new("RGB", (100, 100), "white"),
            OCRConfig(auto_rotate=False, deskew=False),
        )
        self.assertTrue(result.successful)
        self.assertIn("Jane Doe", result.extracted_text)
        self.assertEqual(result.confidence, 85)

    def test_corrupt_image_fails_without_raising(self):
        result = extract_image_text("/path/that/does/not/exist.png")
        self.assertFalse(result.successful)
        self.assertTrue(result.error)


if __name__ == "__main__":
    unittest.main()
