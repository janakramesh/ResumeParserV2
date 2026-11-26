import unittest

from src.resume_parser.understanding.section_validator import (
    validate_section,
    validate_sections,
)


class TestSectionValidator(unittest.TestCase):

    def test_valid_technical_skills(self):
        result = validate_section(
            "technical_skills",
            "Python, Java, SQL, Django, FastAPI"
        )
        self.assertTrue(result.is_valid)
        self.assertGreaterEqual(result.confidence, 60)

    def test_valid_education(self):
        result = validate_section(
            "education",
            "B.Tech in Computer Science\nABC University\nCGPA: 8.5"
        )
        self.assertTrue(result.is_valid)

    def test_valid_experience(self):
        result = validate_section(
            "experience",
            "Software Developer\nABC Technologies\n"
            "Developed applications using Python from 2023 to 2025"
        )
        self.assertTrue(result.is_valid)

    def test_valid_projects(self):
        result = validate_section(
            "projects",
            "Developed a resume parser application using Python."
        )
        self.assertTrue(result.is_valid)

    def test_empty_content(self):
        result = validate_section("education", "")
        self.assertFalse(result.is_valid)
        self.assertEqual(result.confidence, 0)

    def test_unknown_section(self):
        result = validate_section("unknown_section", "Some content")
        self.assertFalse(result.is_valid)
        self.assertEqual(result.confidence, 0)

    def test_short_content(self):
        result = validate_section("education", "B.Tech")
        self.assertFalse(result.is_valid)

    def test_unrelated_content(self):
        result = validate_section(
            "education",
            "I enjoy listening to music and playing cricket."
        )
        self.assertFalse(result.is_valid)

    def test_multiple_sections(self):
        sections = {
            "technical_skills": "Python, Java, SQL",
            "education": "B.Tech\nABC University\nCGPA: 8.5",
            "experience": "Software Developer\nDeveloped Python applications",
        }

        results = validate_sections(sections)

        self.assertEqual(len(results), 3)
        self.assertTrue(results["technical_skills"].is_valid)
        self.assertTrue(results["education"].is_valid)
        self.assertTrue(results["experience"].is_valid)

    def test_invalid_input(self):
        with self.assertRaises(TypeError):
            validate_section("education", None)

        with self.assertRaises(TypeError):
            validate_sections("not a dictionary")


if __name__ == "__main__":
    unittest.main()