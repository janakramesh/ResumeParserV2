
from pathlib import Path
from tempfile import TemporaryDirectory

import pymupdf
from docx import Document

from src.resume_parser.ingestion.file_scanner import scan_resume_folder


def create_test_files(folder):

    # Valid PDF
    pdf = pymupdf.open()
    page = pdf.new_page()
    page.insert_text((50, 50), "Sample resume")
    pdf.save(folder / "valid.pdf")
    pdf.close()

    # Valid DOCX
    doc = Document()
    doc.add_paragraph("Sample resume")
    doc.save(folder / "valid.docx")

    # Empty file
    (folder / "empty.pdf").write_bytes(b"")

    # Corrupted PDF
    (folder / "corrupted.pdf").write_bytes(
        b"%PDF-This is not a valid PDF"
    )

    # Corrupted DOCX
    (folder / "corrupted.docx").write_bytes(
        b"This is not a valid DOCX"
    )

    # Unsupported format
    (folder / "notes.txt").write_text(
        "This is an unsupported file"
    )


with TemporaryDirectory() as temp_dir:

    test_folder = Path(temp_dir)

    create_test_files(test_folder)

    report = scan_resume_folder(test_folder)

    print("\n========== SCANNER EDGE CASE TEST ==========\n")

    print("VALID FILES:")

    for file in report.valid_files:
        print(f"[VALID] {file.path.name} ({file.file_type})")

    print("\nSKIPPED FILES:")

    for filename, reason in report.skipped_files:
        print(f"[SKIPPED] {filename}: {reason}")

    print("\n========== TEST SUMMARY ==========")

    print(f"Valid files: {len(report.valid_files)}")
    print(f"Skipped files: {len(report.skipped_files)}")

    assert len(report.valid_files) == 2
    assert len(report.skipped_files) == 4

    print("\nALL TESTS PASSED!")
