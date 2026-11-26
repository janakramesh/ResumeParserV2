
import json
from dataclasses import dataclass
from pathlib import Path

from src.resume_parser.extractors.docx_extractor import extract_docx_text
from src.resume_parser.extractors.pdf_extractor import extract_pdf_text
from src.resume_parser.ingestion.file_scanner import scan_resume_folder
from src.resume_parser.understanding.resume_analyzer import analyze_resume
from src.resume_parser.understanding.structured_fields import extract_structured_fields
from src.resume_parser.utils.logger import setup_logger
from src.resume_parser.utils.text_cleaner import normalize_resume_text


@dataclass
class ProcessingResult:
    file_name: str
    file_type: str
    successful: bool
    extracted_characters: int
    output_path: str = ""
    needs_ocr_review: bool = False
    error: str = ""
    structured_output_path: str = ""
    total_sections: int = 0
    average_confidence: float = 0.0
    analysis_error: str = ""


class ResumeExtractionEngine:

    def __init__(self, resume_folder: Path, output_folder: Path):

        self.resume_folder = Path(resume_folder)
        self.output_folder = Path(output_folder)

        self.raw_folder = self.output_folder / "raw"
        self.cleaned_folder = self.output_folder / "cleaned"
        self.structured_folder = self.output_folder / "structured"

        self.raw_folder.mkdir(parents=True, exist_ok=True)
        self.cleaned_folder.mkdir(parents=True, exist_ok=True)
        self.structured_folder.mkdir(parents=True, exist_ok=True)

        self.logger = setup_logger(
            self.output_folder.parent / "logs"
        )

        self.results = []

    def process_resume(self, resume_file):

        self.logger.info(
            "Starting processing: %s",
            resume_file.path.name
        )

        print(f"\nProcessing: {resume_file.path.name}")

        try:

            if resume_file.file_type == "PDF":

                result = extract_pdf_text(resume_file.path)

                needs_ocr = (
                    result.successful
                    and len(result.extracted_text.strip()) < 20
                )

            elif resume_file.file_type == "DOCX":

                result = extract_docx_text(resume_file.path)
                needs_ocr = False

            else:
                raise ValueError(
                    f"Unsupported type: {resume_file.file_type}"
                )

            if not result.successful:
                raise RuntimeError(result.error)

            if not result.extracted_text.strip():
                raise ValueError("No readable text extracted")

            raw_text = result.extracted_text
            cleaned_text = normalize_resume_text(raw_text)

            file_stem = (
                f"{resume_file.path.stem}"
                f"__{resume_file.file_type}"
            )

            file_name = f"{file_stem}.txt"

            raw_file = self.raw_folder / file_name
            cleaned_file = self.cleaned_folder / file_name

            raw_file.write_text(raw_text, encoding="utf-8")
            cleaned_file.write_text(cleaned_text, encoding="utf-8")

            # Resume understanding and structured JSON generation.
            structured_file = self.structured_folder / f"{file_stem}.json"

            total_sections = 0
            average_confidence = 0.0
            analysis_error = ""
            structured_output_path = ""

            try:

                analysis_regions = None

                if resume_file.file_type == "PDF":
                    analysis_regions = [
                        normalize_resume_text(region)
                        for region in result.text_regions
                    ]

                analysis = analyze_resume(
                    cleaned_text,
                    text_regions=analysis_regions
                )

                validation_data = {
                    section_name: {
                        "confidence": validation.confidence,
                        "is_valid": validation.is_valid,
                        "warnings": validation.warnings
                    }
                    for section_name, validation
                    in analysis.validation.items()
                }

                key_fields = extract_structured_fields(
                    analysis.sections,
                    getattr(result, "hyperlinks", []) or []
                )

                structured_data = {
                    "file_name": resume_file.path.name,
                    **key_fields,
                    "file_type": resume_file.file_type,
                    "sections": analysis.sections,
                    "validation": validation_data,
                    "total_sections": analysis.total_sections,
                    "average_confidence": analysis.average_confidence
                }

                structured_file.write_text(
                    json.dumps(
                        structured_data,
                        indent=4,
                        ensure_ascii=False
                    ),
                    encoding="utf-8"
                )

                total_sections = analysis.total_sections
                average_confidence = analysis.average_confidence
                structured_output_path = str(structured_file)

                self.logger.info(
                    "Resume analysis completed: %s | Sections: %d | "
                    "Average confidence: %.2f",
                    resume_file.path.name,
                    total_sections,
                    average_confidence
                )

                print(f"Sections detected: {total_sections}")
                print(f"Average confidence: {average_confidence}")
                print(f"Structured JSON saved: {structured_file}")

            except Exception as error:

                analysis_error = str(error)

                self.logger.exception(
                    "Resume analysis failed: %s",
                    resume_file.path.name
                )

                print(f"WARNING: Resume analysis failed: {error}")

            processing_result = ProcessingResult(
                file_name=resume_file.path.name,
                file_type=resume_file.file_type,
                successful=True,
                extracted_characters=len(cleaned_text),
                output_path=str(cleaned_file),
                needs_ocr_review=needs_ocr,
                structured_output_path=structured_output_path,
                total_sections=total_sections,
                average_confidence=average_confidence,
                analysis_error=analysis_error
            )

            self.logger.info(
                "SUCCESS: %s | Characters: %d",
                resume_file.path.name,
                len(cleaned_text)
            )

            if needs_ocr:
                self.logger.warning(
                    "Possible scanned PDF: %s",
                    resume_file.path.name
                )

            print(
                f"SUCCESS: {processing_result.extracted_characters} "
                "characters extracted"
            )
            print(f"Raw text saved: {raw_file}")
            print(f"Cleaned text saved: {cleaned_file}")

            return processing_result

        except Exception as error:

            self.logger.exception(
                "FAILED: %s",
                resume_file.path.name
            )

            print(f"FAILED: {error}")

            return ProcessingResult(
                file_name=resume_file.path.name,
                file_type=resume_file.file_type,
                successful=False,
                extracted_characters=0,
                error=str(error)
            )

    def process_all(self):

        self.logger.info("Starting resume batch processing")

        print("\n========== RESUME EXTRACTION ==========\n")

        try:
            report = scan_resume_folder(self.resume_folder)

        except Exception:
            self.logger.exception(
                "Could not scan resume folder"
            )
            raise

        print(f"Valid files found: {len(report.valid_files)}")
        print(f"Skipped files: {len(report.skipped_files)}")

        for filename, reason in report.skipped_files:

            self.logger.warning(
                "Skipped file: %s | Reason: %s",
                filename,
                reason
            )

            print(f"[SKIPPED] {filename}: {reason}")

        for resume_file in report.valid_files:

            result = self.process_resume(resume_file)
            self.results.append(result)

        self.print_summary()

        self.logger.info(
            "Batch completed | Total: %d | Successful: %d | Failed: %d",
            len(self.results),
            sum(result.successful for result in self.results),
            sum(not result.successful for result in self.results)
        )

        return self.results

    def print_summary(self):

        successful = sum(
            result.successful for result in self.results
        )

        failed = len(self.results) - successful

        ocr_review = sum(
            result.needs_ocr_review for result in self.results
        )

        print("\n========== FINAL SUMMARY ==========\n")
        print(f"Total processed: {len(self.results)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Possible scanned PDFs: {ocr_review}")
        print("\n===================================")
