
"""Local OCR helpers for scanned resume pages and image resumes.

Requires the Tesseract executable plus the Python packages pytesseract and Pillow.
OpenCV is optional; when installed it is used for deskewing.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageEnhance, ImageFilter, ImageOps, UnidentifiedImageError

logger = logging.getLogger("ResumeParser")


@dataclass(frozen=True)
class OCRConfig:
    language: str = "eng"
    dpi: int = 300
    min_native_chars: int = 35
    min_alpha_ratio: float = 0.35
    psm: int = 3
    oem: int = 3
    upscale_factor: float = 1.5
    auto_rotate: bool = True
    deskew: bool = True
    denoise: bool = True
    threshold: bool = False
    tesseract_cmd: str | None = None
    timeout_seconds: int = 45
    calculate_confidence: bool = False


@dataclass
class OCRResult:
    extracted_text: str
    successful: bool
    confidence: float = 0.0
    error: str = ""


def _load_tesseract(config: OCRConfig):
    try:
        import pytesseract
    except ImportError as exc:
        raise RuntimeError(
            "OCR dependency missing. Install pytesseract and Pillow, "
            "and install the Tesseract executable."
        ) from exc
    command = config.tesseract_cmd or os.environ.get("TESSERACT_CMD")
    if not command:
        installed_command = Path(r"C:\Games\tesseract\tesseract.exe")
        if installed_command.is_file():
            command = str(installed_command)
    if command:
        pytesseract.pytesseract.tesseract_cmd = command
    return pytesseract


def _correct_orientation(image: Image.Image, pytesseract: Any) -> Image.Image:
    """Use Tesseract OSD when it can confidently identify page rotation."""
    try:
        osd = pytesseract.image_to_osd(image, output_type=pytesseract.Output.DICT)
        rotation = int(osd.get("rotate", 0)) % 360
        if rotation:
            image = image.rotate(-rotation, expand=True, fillcolor="white")
    except Exception as exc:  # OSD often fails on sparse pages; OCR can continue.
        logger.debug("OCR orientation detection unavailable: %s", exc)
    return image


def _deskew(image: Image.Image) -> Image.Image:
    """Deskew with optional OpenCV; safely retain the image if unavailable."""
    try:
        import cv2
        import numpy as np

        array = np.array(image.convert("L"))
        _, binary = cv2.threshold(array, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        coordinates = np.column_stack(np.where(binary > 0))
        if len(coordinates) < 100:
            return image
        angle = cv2.minAreaRect(coordinates)[-1]
        angle = -(90 + angle) if angle < -45 else -angle
        if abs(angle) < 0.4 or abs(angle) > 12:
            return image
        height, width = array.shape
        matrix = cv2.getRotationMatrix2D((width / 2, height / 2), angle, 1.0)
        rotated = cv2.warpAffine(
            array, matrix, (width, height),
            flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT,
            borderValue=255,
        )
        return Image.fromarray(rotated)
    except ImportError:
        logger.debug("OpenCV not installed; skipping advanced deskew")
    except Exception:
        logger.exception("Optional OCR deskew failed; continuing without it")
    return image


def preprocess_image(image: Image.Image, config: OCRConfig, pytesseract: Any | None = None) -> Image.Image:
    """Normalize, upscale, orient and improve contrast for OCR."""
    image = ImageOps.exif_transpose(image).convert("RGB")
    image = ImageOps.grayscale(image)
    image = ImageOps.autocontrast(image)
    if config.upscale_factor > 1:
        image = image.resize(
            (max(1, int(image.width * config.upscale_factor)),
             max(1, int(image.height * config.upscale_factor))),
            Image.Resampling.LANCZOS,
        )
    image = ImageEnhance.Contrast(image).enhance(1.35)
    if config.denoise:
        image = image.filter(ImageFilter.MedianFilter(size=3))
    if config.deskew:
        image = _deskew(image)
    if config.auto_rotate and pytesseract is not None:
        image = _correct_orientation(image, pytesseract)
    if config.threshold:
        image = image.point(lambda pixel: 255 if pixel > 175 else 0)
    return image


def extract_image_text(image: Image.Image | str | Path, config: OCRConfig | None = None) -> OCRResult:
    """OCR a PIL image or supported image file without propagating file errors."""
    config = config or OCRConfig()
    try:
        pytesseract = _load_tesseract(config)
        if isinstance(image, (str, Path)):
            with Image.open(image) as opened:
                source = opened.copy()
        else:
            source = image.copy()
        if source.width < 2 or source.height < 2:
            raise ValueError("Image is empty or has invalid dimensions")
        prepared = preprocess_image(source, config, pytesseract)
        tess_config = f"--oem {config.oem} --psm {config.psm}"
        text = pytesseract.image_to_string(
            prepared, lang=config.language, config=tess_config,
            timeout=config.timeout_seconds,
        ).strip()
        confidence = 0.0
        if config.calculate_confidence:
            try:
                data = pytesseract.image_to_data(
                    prepared, lang=config.language, config=tess_config,
                    output_type=pytesseract.Output.DICT,
                    timeout=config.timeout_seconds,
                )
                scores = [float(value) for value in data.get("conf", []) if str(value) not in {"-1", ""}]
                confidence = sum(scores) / len(scores) if scores else 0.0
            except Exception as exc:
                logger.debug("Could not calculate OCR confidence: %s", exc)
        return OCRResult(text, True, confidence)
    except (UnidentifiedImageError, OSError, ValueError, RuntimeError) as exc:
        logger.warning("OCR could not process image: %s", exc)
        return OCRResult("", False, error=str(exc))
    except Exception as exc:
        logger.exception("Unexpected OCR failure")
        return OCRResult("", False, error=str(exc))
