
import sys
from pathlib import Path
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from resume_parser.understanding.layout_analyzer import (
    TextBlock,
    PageLayout,
    extract_layout_regions,
)


class TestLayoutRegions(unittest.TestCase):

    def test_two_column_regions_are_separated(self):
        blocks = [
            TextBlock(1, "Left top", 30, 40, 250, 70, 10),
            TextBlock(1, "Right top", 330, 50, 570, 80, 10),
            TextBlock(1, "Full width heading", 20, 300, 580, 330, 14),
            TextBlock(1, "Left bottom", 30, 350, 250, 380, 10),
            TextBlock(1, "Right bottom", 330, 360, 570, 390, 10),
        ]

        layout = PageLayout(
            page_number=1,
            page_width=600,
            page_height=800,
            blocks=blocks,
            columns=2,
        )

        regions = extract_layout_regions(layout)

        self.assertEqual(
            regions,
            [
                "Left top",
                "Right top",
                "Full width heading",
                "Left bottom",
                "Right bottom",
            ],
        )

    def test_single_column_returns_one_region(self):
        blocks = [
            TextBlock(1, "First paragraph", 30, 40, 570, 70, 10),
            TextBlock(1, "Second paragraph", 30, 100, 570, 130, 10),
        ]

        layout = PageLayout(
            page_number=1,
            page_width=600,
            page_height=800,
            blocks=blocks,
            columns=1,
        )

        regions = extract_layout_regions(layout)

        self.assertEqual(len(regions), 1)
        self.assertIn("First paragraph", regions[0])
        self.assertIn("Second paragraph", regions[0])

    def test_empty_layout_returns_empty_list(self):
        layout = PageLayout(
            page_number=1,
            page_width=600,
            page_height=800,
            blocks=[],
            columns=1,
        )

        self.assertEqual(extract_layout_regions(layout), [])


if __name__ == "__main__":
    unittest.main()
