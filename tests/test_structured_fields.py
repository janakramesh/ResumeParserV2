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

    def test_address_uses_full_resume_and_prefers_permanent_label(self):
        sections = {
            "header": (
                "Vilas S Khole\n"
                "vskhole@yahoo.com\n"
                "+91 855 182 6442"
            ),
            "experience": "Infotech, US",
            "achievements": "100% focus on his Job.",
            "personal_information": (
                "Present Address: 401 Tamkeen Towers, Al Khan Street, "
                "Sharjah (UAE)\n"
                "Permanent Address: G-401, Kubhera Vistas, "
                "Saravanampatti, Coimbatore 641035 [IN]"
            ),
        }

        fields = extract_structured_fields(sections)

        self.assertEqual(
            fields["address"],
            "G-401, Kubhera Vistas, Saravanampatti, "
            "Coimbatore 641035 [IN]",
        )
        self.assertEqual(fields["email"], "vskhole@yahoo.com")
        self.assertEqual(fields["phone_number"], "+918551826442")


if __name__ == "__main__":
    unittest.main()
