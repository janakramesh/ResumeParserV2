
from src.resume_parser.utils.text_cleaner import (
    normalize_resume_text,
    remove_pdf_line_hyphenation
)


sample_text = """
TECHNICAL SKILLS


Programming Languages:   Python, C

under-
standing

problem-
solving


PROJECTS
"""

print("ORIGINAL TEXT:")
print(sample_text)

cleaned = normalize_resume_text(sample_text)

cleaned = remove_pdf_line_hyphenation(cleaned)

print("\nCLEANED TEXT:")
print(cleaned)
