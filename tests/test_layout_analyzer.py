
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from resume_parser.understanding.layout_analyzer import (
    TextBlock,
    detect_columns,
    extract_page_blocks,
    analyze_pdf_layout,
)

import pymupdf


def make_block(x0, x1, text="Sample"):
    return TextBlock(
        page_number=1,
        text=text,
        x0=x0,
        y0=50,
        x1=x1,
        y1=80,
        font_size=11
    )


class TestLayoutAnalyzer(unittest.TestCase):

    def test_single_column(self):

        blocks = [
            make_block(50, 500),
            make_block(50, 500),
            make_block(50, 500),
        ]

        self.assertEqual(
            detect_columns(blocks, 600),
            1
        )

    def test_two_columns(self):

        blocks = [
            make_block(40, 240),
            make_block(40, 240),
            make_block(340, 550),
            make_block(340, 550),
        ]

        self.assertEqual(
            detect_columns(blocks, 600),
            2
        )

    def test_empty_blocks(self):

        self.assertEqual(
            detect_columns([], 600),
            1
        )

    def test_one_block(self):

        blocks = [make_block(50, 500)]

        self.assertEqual(
            detect_columns(blocks, 600),
            1
        )

    def test_overlapping_columns(self):

        blocks = [
            make_block(40, 350),
            make_block(300, 550),
        ]

        self.assertEqual(
            detect_columns(blocks, 600),
            1
        )

    def test_block_dimensions(self):

        block = make_block(50, 250)

        self.assertEqual(block.width, 200)
        self.assertEqual(block.height, 30)

    def test_extract_page_blocks(self):

        document = pymupdf.open()

        try:
            page = document.new_page()
            page.insert_text((50, 50), "John Doe")

            blocks = extract_page_blocks(page, 1)

            self.assertEqual(len(blocks), 1)
            self.assertIn("John Doe", blocks[0].text)
            self.assertEqual(blocks[0].page_number, 1)

        finally:
            document.close()

    def test_analyze_pdf_layout(self):

        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:

            pdf_path = Path(temp_dir) / "test.pdf"

            document = pymupdf.open()
            page = document.new_page()
            page.insert_text((50, 50), "Resume Test")
            document.save(pdf_path)
            document.close()

            layouts = analyze_pdf_layout(pdf_path)

            self.assertEqual(len(layouts), 1)
            self.assertEqual(layouts[0].page_number, 1)
            self.assertGreater(len(layouts[0].blocks), 0)

    def test_missing_pdf(self):

        with self.assertRaises(Exception):
            analyze_pdf_layout("nonexistent_resume.pdf")


if __name__ == "__main__":
    unittest.main(verbosity=2)
