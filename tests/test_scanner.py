
from pathlib import Path

from src.resume_parser.ingestion.file_scanner import (
    scan_resume_folder
)

RESUME_FOLDER = Path(__file__).resolve().parent / "resume"


def main():

    report = scan_resume_folder(RESUME_FOLDER)

    print("\n========== SCAN RESULTS ==========\n")

    print(f"Valid resumes: {len(report.valid_files)}")

    for resume in report.valid_files:
        print(f"[VALID] {resume.path.name} - {resume.file_type}")

    print(f"\nSkipped files: {len(report.skipped_files)}")

    for filename, reason in report.skipped_files:
        print(f"[SKIPPED] {filename} - {reason}")


if __name__ == "__main__":
    main()
