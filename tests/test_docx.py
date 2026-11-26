
from pathlib import Path

from src.resume_parser.extractors.docx_extractor import (
    extract_docx_text
)


RESUME_FOLDER = Path(__file__).resolve().parent / "resume"


def main():

    docx_files = list(RESUME_FOLDER.glob("*.docx"))

    if not docx_files:
        print("No DOCX files found!")
        return

    for docx_file in docx_files:

        print("\n" + "=" * 60)
        print(f"Processing: {docx_file.name}")
        print("=" * 60)

        result = extract_docx_text(docx_file)

        if result.successful:

            print("Status: SUCCESS")

            print(
                f"Paragraphs: {result.total_paragraphs}"
            )

            print(
                f"Tables: {result.total_tables}"
            )

            print(
                f"Extracted characters: "
                f"{len(result.extracted_text)}"
            )

            print("\nExtracted Text:\n")

            print(result.extracted_text)

        else:

            print("Status: FAILED")
            print(f"Error: {result.error}")


if __name__ == "__main__":
    main()
