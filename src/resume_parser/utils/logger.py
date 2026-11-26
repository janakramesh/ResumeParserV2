
import logging
from pathlib import Path


def setup_logger(log_folder: Path):

    log_folder = Path(log_folder)
    log_folder.mkdir(parents=True, exist_ok=True)

    log_file = log_folder / "resume_parser.log"

    logger = logging.getLogger("ResumeParser")
    logger.setLevel(logging.INFO)

    if not logger.handlers:

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        )

        file_handler = logging.FileHandler(
            log_file,
            encoding="utf-8"
        )

        console_handler = logging.StreamHandler()

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
