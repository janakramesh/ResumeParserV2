import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from resume_parser.understanding.section_splitter import split_sections_from_regions
from resume_parser.understanding.structured_fields import extract_structured_fields


class TestStructuredFields(unittest.TestCase):

    def test_name_skips_cover_title_and_role(self):
        sections = {
            "header": (
                "Portfolio\n"
                ".\n"
                "Vilas S Khole\n"
                "A Mentor | Leader | Technologist"
            )
        }

        result = extract_structured_fields(sections)

        self.assertEqual(result["name"], "Vilas S Khole")

    def test_education_table_is_extracted_from_column_headers(self):
        regions = [
            """--- PAGE 7 | REGION 2 ---
Year
Examinations Milestone
Board/University
Grade %
2015
M.Sc. (Comp. Sci.)
Dr. BAM University, Aurangabad
I Class - 61%
2007
B.Sc. (Comp. Sci.)
Dr. BAM University, Aurangabad
II Class - 59%"""
        ]

        sections = split_sections_from_regions(regions)
        fields = extract_structured_fields(sections)

        self.assertIn("M.Sc. (Comp. Sci.)", sections["education"])
        self.assertIn("B.Sc. (Comp. Sci.)", fields["education"])
        self.assertNotIn("Grade %", fields["education"])


if __name__ == "__main__":
    unittest.main()
