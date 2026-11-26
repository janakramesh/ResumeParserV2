
import sys
import unittest
from pathlib import Path

# Add src directory to Python import path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_PATH))

from resume_parser.understanding.heading_detector import (
    detect_heading,
    normalize_heading,
)


class TestHeadingDetector(unittest.TestCase):

    def test_basic_headings(self):
        test_cases = {
            "TECHNICAL SKILLS": "technical_skills",
            "Education": "education",
            "PROJECTS": "projects",
            "Professional Experience": "experience",
            "CERTIFICATIONS": "certifications",
        }

        for text, expected in test_cases.items():
            with self.subTest(text=text):
                self.assertEqual(detect_heading(text), expected)

    def test_heading_case_variations(self):
        self.assertEqual(
            detect_heading("technical skills"),
            "technical_skills"
        )

        self.assertEqual(
            detect_heading("Technical Skills"),
            "technical_skills"
        )

        self.assertEqual(
            detect_heading("TECHNICAL SKILLS"),
            "technical_skills"
        )

    def test_heading_punctuation(self):
        self.assertEqual(
            detect_heading("Technical Skills:"),
            "technical_skills"
        )

        self.assertEqual(
            detect_heading("EDUCATION :"),
            "education"
        )

    def test_decorative_underline_suffix(self):
        self.assertEqual(
            detect_heading("Professional Experience________________"),
            "experience"
        )
        self.assertEqual(
            detect_heading("Web Applications________"),
            "projects"
        )

    def test_numbered_headings(self):
        self.assertEqual(
            detect_heading("1. EDUCATION"),
            "education"
        )

        self.assertEqual(
            detect_heading("(2) TECHNICAL SKILLS"),
            "technical_skills"
        )

    def test_bullet_and_markdown_headings(self):
        self.assertEqual(
            detect_heading("- EDUCATION"),
            "education"
        )

        self.assertEqual(
            detect_heading("# PROJECTS"),
            "projects"
        )

    def test_extra_whitespace(self):
        self.assertEqual(
            detect_heading("  TECHNICAL   SKILLS  "),
            "technical_skills"
        )

    def test_normal_sentences_are_not_headings(self):
        sentences = [
            "I have experience in Python",
            "My technical skills include Java",
            "I completed several projects",
            "I studied computer science",
            "Looking for a challenging position",
        ]

        for sentence in sentences:
            with self.subTest(sentence=sentence):
                self.assertIsNone(detect_heading(sentence))

    def test_unknown_headings(self):
        self.assertIsNone(detect_heading("My Favorite Things"))
        self.assertIsNone(detect_heading("Random Text"))
        self.assertIsNone(detect_heading(""))

    def test_invalid_input(self):
        self.assertIsNone(detect_heading(None))
        self.assertIsNone(detect_heading(123))

    def test_normalize_heading(self):
        self.assertEqual(
            normalize_heading("  1. TECHNICAL   SKILLS: "),
            "technical skills"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
