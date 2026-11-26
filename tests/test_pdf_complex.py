
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import pymupdf

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from resume_parser.extractors.pdf_extractor import extract_pdf_text

with TemporaryDirectory() as temp_dir:

    test_file = Path(temp_dir) / "complex_resume.pdf"

    # Create a two-page PDF
    pdf = pymupdf.open()

    page1 = pdf.new_page()
    page1.insert_text((50, 50), "JOHN DOE")
    page1.insert_text((50, 100), "Email: john@example.com")
    page1.insert_text((50, 150), "Technical Skills: Python, Java")

    page2 = pdf.new_page()
    page2.insert_text((50, 50), "WORK EXPERIENCE")
    page2.insert_text((50, 100), "Software Developer")
    page2.insert_text((50, 150), "ABC Technologies")

    pdf.save(test_file)
    pdf.close()

    result = extract_pdf_text(test_file)

    print("\n========== COMPLEX PDF TEST ==========\n")

    print("Extraction successful:", result.successful)
    print("Total pages:", result.total_pages)
    print("Extracted characters:", len(result.extracted_text))

    print("\nEXTRACTED CONTENT:\n")
    print(result.extracted_text)

    expected = [
        "JOHN DOE",
        "john@example.com",
        "Python",
        "WORK EXPERIENCE",
        "Software Developer",
        "ABC Technologies",
        "PAGE 1",
        "PAGE 2"
    ]

    missing = [
        item for item in expected
        if item.lower() not in result.extracted_text.lower()
    ]

    print("\n========== TEST RESULT ==========")

    if result.successful and result.total_pages == 2 and not missing:
        print("ALL COMPLEX PDF TESTS PASSED!")
    else:
        print("MISSING CONTENT:", missing)
