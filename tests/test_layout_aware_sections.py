
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from resume_parser.understanding.section_splitter import (
    split_sections_from_regions,
)
from resume_parser.understanding.resume_analyzer import analyze_resume
from resume_parser.understanding.layout_analyzer import (
    PageLayout,
    TextBlock,
    extract_layout_regions,
)


class TestLayoutAwareSections(unittest.TestCase):

    def test_sections_from_separate_columns_are_merged(self):
        regions = [
            """--- PAGE 1 | REGION 1 ---
EXPERIENCE
Software Developer
ABC Technologies

EDUCATION
B.Tech Computer Science""",

            """--- PAGE 1 | REGION 2 ---
SUMMARY
Experienced Python developer.

SKILLS
Python, Java, SQL""",
        ]

        result = split_sections_from_regions(regions)

        self.assertIn("experience", result)
        self.assertIn("summary", result)
        self.assertIn("education", result)
        self.assertIn("technical_skills", result)

        self.assertIn("Software Developer", result["experience"])
        self.assertIn("Experienced Python developer", result["summary"])
        self.assertIn("B.Tech Computer Science", result["education"])
        self.assertIn("Python, Java, SQL", result["technical_skills"])

    def test_repeated_sections_are_merged(self):
        regions = [
            "EXPERIENCE\nSoftware Developer",
            "EXPERIENCE\nSenior Developer",
        ]

        result = split_sections_from_regions(regions)

        self.assertIn("Software Developer", result["experience"])
        self.assertIn("Senior Developer", result["experience"])

    def test_empty_regions(self):
        self.assertEqual(
            split_sections_from_regions(["", "   "]),
            {}
        )

    def test_analyzer_accepts_layout_regions(self):
        regions = [
            "SUMMARY\nPython developer with experience.",
            "EDUCATION\nBachelor of Computer Science",
        ]

        analysis = analyze_resume(
            "Some extracted resume text",
            text_regions=regions
        )

        self.assertIn("summary", analysis.sections)
        self.assertIn("education", analysis.sections)
        self.assertEqual(analysis.total_sections, 2)

    def test_invalid_regions_raise_type_error(self):
        with self.assertRaises(TypeError):
            split_sections_from_regions("not a list")


    def test_heading_and_content_in_separate_regions(self):
        regions = [
            "KEY SKILLS",
            "Python, Java, SQL",
            "EDUCATION",
            "Bachelor of Computer Science",
        ]

        result = split_sections_from_regions(regions)

        self.assertIn("Python, Java, SQL", result["technical_skills"])
        self.assertIn(
            "Bachelor of Computer Science",
            result["education"]
        )

    def test_short_right_column_headings_stay_with_their_content(self):
        blocks = [
            TextBlock(1, "SKILLS", 30, 100, 75, 112, 12),
            TextBlock(1, "Python, SQL", 30, 120, 180, 135, 10),
            TextBlock(1, "EDUCATION", 30, 200, 90, 212, 12),
            TextBlock(1, "Computer Science degree", 30, 220, 180, 235, 10),
            TextBlock(1, "CERTIFICATIONS", 30, 300, 120, 312, 12),
            TextBlock(1, "Cloud certification", 30, 320, 180, 335, 10),
            TextBlock(1, "SUMMARY", 216, 100, 261, 112, 12),
            TextBlock(1, "Experienced technology leader", 216, 120, 560, 140, 10),
            TextBlock(1, "EXPERIENCE", 216, 180, 269, 192, 12),
            TextBlock(1, "Senior Engineer\nAcme Corp\nBuilt reliable systems", 216, 200, 560, 250, 10),
        ]
        layout = PageLayout(
            page_number=1,
            page_width=596,
            page_height=800,
            blocks=blocks,
            columns=2,
        )

        regions = extract_layout_regions(layout)
        result = split_sections_from_regions(regions)

        self.assertIn("Python, SQL", result["technical_skills"])
        self.assertIn("Experienced technology leader", result["summary"])
        self.assertIn("Senior Engineer", result["experience"])
        self.assertIn("Computer Science degree", result["education"])
        self.assertIn("Cloud certification", result["certifications"])

    def test_multiple_headings_inside_one_region(self):
        regions = [
            """LEADERSHIP ROLES
            Soccer umpire

            INTERESTS/HOBBIES
            Playing soccer

            REFEREES
            John Charles"""
        ]

        result = split_sections_from_regions(regions)

        self.assertIn("Soccer umpire", result["experience"])
        self.assertIn("Playing soccer", result["interests"])
        self.assertIn("John Charles", result["references"])

    def test_decorated_headings_keep_long_portfolio_sections_separate(self):
        regions = [
            """--- PAGE 5 | REGION 1 ---
Professional Summary________________
Twenty years of technology leadership.
Professional Experience________________
Led engineering and operations teams.""",
            """--- PAGE 7 | REGION 1 ---
Language Proficiency
English and Hindi, both fluent.""",
            """--- PAGE 8 | REGION 1 ---
Technology Showcase.
Web Applications________________
Built a customer management platform.
Mobile Applications________________
Created a mobile banking application.""",
            """--- PAGE 11 | REGION 1 ---
Operational Excellence:
Received an organization-wide delivery award.""",
        ]

        result = split_sections_from_regions(regions)

        self.assertEqual(
            result["summary"],
            "Twenty years of technology leadership."
        )
        self.assertIn("Led engineering", result["experience"])
        self.assertEqual(
            result["languages"],
            "English and Hindi, both fluent."
        )
        self.assertIn("customer management platform", result["projects"])
        self.assertIn("mobile banking application", result["projects"])
        self.assertNotIn(
            "customer management platform",
            result["languages"]
        )
        self.assertIn("organization-wide delivery award", result["achievements"])

if __name__ == "__main__":
    unittest.main()
