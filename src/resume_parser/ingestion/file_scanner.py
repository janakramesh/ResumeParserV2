
from pathlib import Path
from dataclasses import dataclass
from zipfile import ZipFile, BadZipFile

import pymupdf


@dataclass
class ResumeFile:
    path: Path
    file_type: str


@dataclass
class ScanReport:
    valid_files: list
    skipped_files: list


SUPPORTED_FORMATS = {".pdf", ".docx"}


def validate_pdf(file_path: Path) -> bool:
    """Check whether a PDF can actually be opened and read."""
    try:
        with pymupdf.open(file_path) as pdf:
            return (
                pdf.is_pdf
                and len(pdf) > 0
            )
    except Exception:
        return False


def validate_docx(file_path: Path) -> bool:
    """Check whether a DOCX is a valid ZIP-based document."""
    try:
        with ZipFile(file_path, "r") as doc:
            return (
                doc.testzip() is None
                and "word/document.xml" in doc.namelist()
            )
    except (BadZipFile, OSError):
        return False


def scan_resume_folder(folder_path: Path) -> ScanReport:
    """Scan the folder and identify valid PDF and DOCX files."""

    valid_files = []
    skipped_files = []

    folder_path = Path(folder_path)

    if not folder_path.exists():
        raise FileNotFoundError(
            f"Resume folder does not exist: {folder_path}"
        )

    if not folder_path.is_dir():
        raise NotADirectoryError(
            f"Expected a directory: {folder_path}"
        )

    for file_path in sorted(folder_path.iterdir()):

        if not file_path.is_file():
            continue

        extension = file_path.suffix.lower()

        if extension not in SUPPORTED_FORMATS:
            skipped_files.append(
                (file_path.name, "Unsupported file format")
            )
            continue

        try:
            if file_path.stat().st_size == 0:
                skipped_files.append(
                    (file_path.name, "Empty file")
                )
                continue
        except OSError:
            skipped_files.append(
                (file_path.name, "Unable to access file")
            )
            continue

        if extension == ".pdf":
            is_valid = validate_pdf(file_path)
            file_type = "PDF"
        else:
            is_valid = validate_docx(file_path)
            file_type = "DOCX"

        if is_valid:
            valid_files.append(
                ResumeFile(
                    path=file_path.resolve(),
                    file_type=file_type
                )
            )
        else:
            skipped_files.append(
                (file_path.name, "Invalid or corrupted file")
            )

    return ScanReport(
        valid_files=valid_files,
        skipped_files=skipped_files
    )
