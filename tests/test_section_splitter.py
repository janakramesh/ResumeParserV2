
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_PATH))

from resume_parser.understanding.section_splitter import split_sections


class TestSectionSplitter(unittest.TestCase):

    def test_basic_section_splitting(self):

        text = """
JANAK RAMESH

TECHNICAL SKILLS
Python, Java, Django

EDUCATION
B.Tech Computer Science

PROJECTS
Resume Parser
"""

        result = split_sections(text)

        self.assertEqual(
            result["technical_skills"],
            "Python, Java, Django"
        )

        self.assertEqual(
            result["education"],
            "B.Tech Computer Science"
        )

        self.assertEqual(
            result["projects"],
            "Resume Parser"
        )

        self.assertEqual(result["header"], "JANAK RAMESH")

    def test_multiple_lines_in_section(self):

        text = """
EDUCATION
B.Tech Computer Science
ABC University
2022 - 2026
"""

        result = split_sections(text)

        self.assertEqual(
            result["education"],
            "B.Tech Computer Science\nABC University\n2022 - 2026"
        )

    def test_repeated_sections(self):

        text = """
PROJECTS
Resume Parser

EDUCATION
B.Tech Computer Science

PROJECTS
Student Management System
"""

        result = split_sections(text)

        self.assertIn("Resume Parser", result["projects"])
        self.assertIn("Student Management System", result["projects"])

    def test_empty_sections(self):

        text = """
EDUCATION

PROJECTS
Resume Parser
"""

        result = split_sections(text)

        self.assertIn("education", result)
        self.assertEqual(result["education"], "")

        self.assertEqual(result["projects"], "Resume Parser")

    def test_content_before_first_heading(self):

        text = """
John Doe
Python Developer
john@example.com

EDUCATION
B.Tech
"""

        result = split_sections(text)

        self.assertIn("John Doe", result["header"])
        self.assertIn("Python Developer", result["header"])

    def test_empty_input(self):

        self.assertEqual(split_sections(""), {})
        self.assertEqual(split_sections("   \n  "), {})

    def test_invalid_input(self):

        with self.assertRaises(TypeError):
            split_sections(None)

        with self.assertRaises(TypeError):
            split_sections(123)

    def test_unknown_heading_is_preserved(self):

        text = """
MY CUSTOM SECTION
Some important information

EDUCATION
B.Tech
"""

        result = split_sections(text)

        self.assertIn(
            "MY CUSTOM SECTION",
            result["header"]
        )

        self.assertIn(
            "Some important information",
            result["header"]
        )

    def test_heading_case_variations(self):

        text = """
technical skills
Python, Java

EDUCATION:
B.Tech
"""

        result = split_sections(text)

        self.assertEqual(
            result["technical_skills"],
            "Python, Java"
        )

        self.assertEqual(
            result["education"],
            "B.Tech"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
