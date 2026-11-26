import unittest

from src.resume_parser.understanding.resume_analyzer import analyze_resume


class TestResumeAnalyzer(unittest.TestCase):

    def test_analyze_complete_resume(self):
        text = """
        JOHN DOE

        TECHNICAL SKILLS
        Python, Java, SQL, Django

        EDUCATION
        B.Tech in Computer Science
        ABC University
        CGPA: 8.5

        PROJECTS
        Developed a resume parser using Python.
        """

        result = analyze_resume(text)

        self.assertEqual(result.total_sections, 3)
        self.assertIn("technical_skills", result.sections)
        self.assertIn("education", result.sections)
        self.assertIn("projects", result.sections)

    def test_validation_results(self):
        text = """
        TECHNICAL SKILLS
        Python, Java, SQL

        EDUCATION
        B.Tech
        ABC University
        """

        result = analyze_resume(text)

        self.assertIn("technical_skills", result.validation)
        self.assertIn("education", result.validation)

    def test_average_confidence(self):
        text = """
        TECHNICAL SKILLS
        Python, Java, SQL
        """

        result = analyze_resume(text)

        self.assertGreater(result.average_confidence, 0)
        self.assertLessEqual(result.average_confidence, 100)

    def test_empty_resume(self):
        result = analyze_resume("")

        self.assertEqual(result.total_sections, 0)
        self.assertEqual(result.average_confidence, 0)

    def test_invalid_input(self):
        with self.assertRaises(TypeError):
            analyze_resume(None)


if __name__ == "__main__":
    unittest.main()