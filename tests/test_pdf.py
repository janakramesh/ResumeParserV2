
from pathlib import Path

from src.resume_parser.extractors.pdf_extractor import (
    extract_pdf_text
)


RESUME_FOLDER = Path(__file__).resolve().parent / "resume"


def main():

    pdf_files = list(RESUME_FOLDER.glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found!")
        return

    for pdf_file in pdf_files:

        print("\n" + "=" * 60)
        print(f"Processing: {pdf_file.name}")
        print("=" * 60)

        result = extract_pdf_text(pdf_file)

        if result.successful:

            print(f"Status: SUCCESS")
            print(f"Pages: {result.total_pages}")
            print(f"Extracted characters: {len(result.extracted_text)}")

            print("\nExtracted Text:\n")
            print(result.extracted_text)

        else:

            print("Status: FAILED")
            print(f"Error: {result.error}")


if __name__ == "__main__":
    main()
