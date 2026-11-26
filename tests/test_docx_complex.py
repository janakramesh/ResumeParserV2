
from pathlib import Path
from tempfile import TemporaryDirectory

from docx import Document

from src.resume_parser.extractors.docx_extractor import (
    extract_docx_text
)


with TemporaryDirectory() as temp_dir:

    test_file = Path(temp_dir) / "complex_resume.docx"

    doc = Document()

    # Header
    doc.sections[0].header.paragraphs[0].text = (
        "CANDIDATE RESUME"
    )

    # Main paragraphs
    doc.add_heading("John Doe", level=1)
    doc.add_paragraph("Email: john@example.com")
    doc.add_heading("Technical Skills", level=2)
    doc.add_paragraph("Python, Java, SQL")

    # Main table
    table = doc.add_table(rows=2, cols=2)
    table.cell(0, 0).text = "Degree"
    table.cell(0, 1).text = "University"
    table.cell(1, 0).text = "B.Tech"
    table.cell(1, 1).text = "ABC University"

    # Nested table inside a cell
    nested = table.cell(1, 1).add_table(rows=1, cols=1)
    nested.cell(0, 0).text = "Nested table content"

    # Footer
    doc.sections[0].footer.paragraphs[0].text = (
        "End of Resume"
    )

    doc.save(test_file)

    result = extract_docx_text(test_file)

    print("\n========== COMPLEX DOCX TEST ==========\n")

    print("Extraction successful:", result.successful)
    print("Paragraphs:", result.total_paragraphs)
    print("Tables:", result.total_tables)

    print("\nEXTRACTED CONTENT:\n")
    print(result.extracted_text)

    expected = [
        "John Doe",
        "john@example.com",
        "Python",
        "ABC University",
        "Nested table content",
        "CANDIDATE RESUME",
        "End of Resume"
    ]

    missing = [
        item for item in expected
        if item.lower() not in result.extracted_text.lower()
    ]

    print("\n========== TEST RESULT ==========")

    if result.successful and not missing:
        print("ALL COMPLEX DOCX TESTS PASSED!")
    else:
        print("MISSING CONTENT:", missing)
