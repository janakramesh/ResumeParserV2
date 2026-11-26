
from pathlib import Path

from src.resume_parser.extractors.pdf_extractor import extract_pdf_text
from src.resume_parser.extractors.docx_extractor import extract_docx_text


RESUME_FOLDER = Path("resume")


def check_content(file_name, extractor, expected_keywords):

    file_path = RESUME_FOLDER / file_name

    print(f"\nTesting: {file_name}")

    result = extractor(file_path)

    if not result.successful:
        print(f"EXTRACTION FAILED: {result.error}")
        return False

    extracted_text = result.extracted_text.lower()

    missing_keywords = []

    for keyword in expected_keywords:
        if keyword.lower() not in extracted_text:
            missing_keywords.append(keyword)

    print(f"Extracted characters: {len(result.extracted_text)}")

    if missing_keywords:
        print("MISSING CONTENT:", missing_keywords)
        return False

    print("All expected keywords found!")
    return True


tests = [
    (
        "janakramesh.pdf",
        extract_pdf_text,
        ["Python", "C", "education"]
    ),
    (
        "resumepdf1.pdf",
        extract_pdf_text,
        ["experience", "skills", "education"]
    ),
    (
        "resumedocx1.docx",
        extract_docx_text,
        ["experience", "skills", "education"]
    )
]


passed = 0

print("\n========== EXTRACTION QUALITY TEST ==========")

for file_name, extractor, keywords in tests:

    if check_content(file_name, extractor, keywords):
        passed += 1

print("\n========== FINAL RESULT ==========")
print(f"Tests passed: {passed}/{len(tests)}")
print(f"Tests failed: {len(tests) - passed}")
