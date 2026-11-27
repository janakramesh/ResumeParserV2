import tempfile
import unittest
from pathlib import Path
from PIL import Image

from src.resume_parser.ingestion.file_scanner import scan_resume_folder


class ImageScannerTests(unittest.TestCase):
    def test_scans_valid_image_and_skips_corrupt_image(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            Image.new("RGB", (20, 20), "white").save(root / "resume.png")
            (root / "broken.jpg").write_bytes(b"not an image")
            report = scan_resume_folder(root)
            self.assertEqual(len(report.valid_files), 1)
            self.assertEqual(report.valid_files[0].file_type, "IMAGE")
            self.assertEqual(report.skipped_files[0][0], "broken.jpg")


if __name__ == "__main__":
    unittest.main()
