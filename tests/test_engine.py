
from pathlib import Path

from src.resume_parser.extraction_engine import (
    ResumeExtractionEngine
)


BASE_DIR = Path(__file__).resolve().parent

RESUME_FOLDER = BASE_DIR / "resume"
OUTPUT_FOLDER = BASE_DIR / "output"


def main():

    engine = ResumeExtractionEngine(
        resume_folder=RESUME_FOLDER,
        output_folder=OUTPUT_FOLDER
    )

    engine.process_all()


if __name__ == "__main__":
    main()
