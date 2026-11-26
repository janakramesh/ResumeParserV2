
from pathlib import Path

from src.resume_parser.extraction_engine import ResumeExtractionEngine

# Project directory
BASE_DIR = Path(__file__).resolve().parent

# Input and output directories
RESUME_FOLDER = BASE_DIR / "resume"
OUTPUT_FOLDER = BASE_DIR / "output"


def main():

    print("\n====================================")
    print("       RESUME PARSER V2")
    print("====================================")

    # Check input directory
    if not RESUME_FOLDER.exists():
        print(f"Resume folder not found: {RESUME_FOLDER}")
        return

    # Initialize extraction engine
    engine = ResumeExtractionEngine(
        resume_folder=RESUME_FOLDER,
        output_folder=OUTPUT_FOLDER
    )

    # Process all resumes
    results = engine.process_all()

    print("\nResume processing completed!")

    print("\nOutput directories:")
    print(f"Raw text: {OUTPUT_FOLDER / 'raw'}")
    print(f"Cleaned text: {OUTPUT_FOLDER / 'cleaned'}")


if __name__ == "__main__":
    main()
