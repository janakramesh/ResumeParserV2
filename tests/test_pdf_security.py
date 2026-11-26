
from pathlib import Path
from tempfile import TemporaryDirectory

import pymupdf

from src.resume_parser.extractors.pdf_extractor import (
    extract_pdf_text
)


with TemporaryDirectory() as temp_dir:

    pdf_path = Path(temp_dir) / "protected_resume.pdf"

    # Create a password-protected PDF
    pdf = pymupdf.open()

    page = pdf.new_page()
    page.insert_text((50, 50), "Confidential Resume")

    pdf.save(
        pdf_path,
        encryption=pymupdf.PDF_ENCRYPT_AES_256,
        owner_pw="owner123",
        user_pw="user123"
    )

    pdf.close()

    # Attempt extraction without supplying a password
    result = extract_pdf_text(pdf_path)

    print("\n========== PDF SECURITY TEST ==========\n")

    print("Extraction successful:", result.successful)
    print("Error:", result.error)

    if (
        not result.successful
        and "Password-protected PDF" in result.error
    ):
        print("\nPASSWORD PROTECTION TEST PASSED!")
    else:
        print("\nTEST FAILED!")
