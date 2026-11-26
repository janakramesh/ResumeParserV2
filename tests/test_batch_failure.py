
from pathlib import Path
from tempfile import TemporaryDirectory

import pymupdf

from src.resume_parser.extraction_engine import ResumeExtractionEngine

with TemporaryDirectory() as temp_dir:

    base = Path(temp_dir)

    resume_folder = base / "resume"
    output_folder = base / "output"

    resume_folder.mkdir()

    # Create a valid PDF
    valid_pdf = pymupdf.open()
    page = valid_pdf.new_page()
    page.insert_text((50, 50), "Valid Resume - Python Developer")
    valid_pdf.save(resume_folder / "valid.pdf")
    valid_pdf.close()

    # Create a password-protected PDF
    protected_pdf = pymupdf.open()
    page = protected_pdf.new_page()
    page.insert_text((50, 50), "Protected Resume")
    protected_pdf.save(
        resume_folder / "protected.pdf",
        encryption=pymupdf.PDF_ENCRYPT_AES_256,
        owner_pw="owner123",
        user_pw="user123"
    )
    protected_pdf.close()

    # Create a corrupted PDF
    (resume_folder / "corrupted.pdf").write_bytes(
        b"%PDF-invalid content"
    )

    # Run the extraction engine
    engine = ResumeExtractionEngine(
        resume_folder,
        output_folder
    )

    results = engine.process_all()

    successful = sum(r.successful for r in results)
    failed = sum(not r.successful for r in results)

    print("\n========== FAILURE ISOLATION TEST ==========")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")

    assert len(results) == 2
    assert successful == 1
    assert failed == 1

    assert (output_folder / "cleaned" / "valid__PDF.txt").exists()

    print("\nBATCH FAILURE ISOLATION TEST PASSED!")
    # Close logger handlers before temporary folder cleanup
    for handler in engine.logger.handlers[:]:
        handler.close()
        engine.logger.removeHandler(handler)