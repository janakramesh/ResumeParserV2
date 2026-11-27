# Local OCR setup (Python 3.13)

The OCR path uses Tesseract locally. It does not send documents to a cloud service.

## Python packages

Add these to the existing project environment:

```powershell
python -m pip install pytesseract Pillow
```

PyMuPDF is already used by the project. OpenCV is optional; install `opencv-python-headless` only if advanced deskewing is desired.

## Tesseract executable

Install the Tesseract OCR application for Windows. The parser automatically detects `C:\Games\tesseract\tesseract.exe` when present. For another installation location, set the executable path before running the parser:

```powershell
$env:TESSERACT_CMD = "C:\path\to\tesseract.exe"
```

`OCRConfig(tesseract_cmd=...)` can also be used to configure the executable directly; that setting takes precedence over `TESSERACT_CMD`.

The default OCR language is English (`eng`). Install the relevant Tesseract language data before selecting another language in `OCRConfig`.

## Configuration

`OCRConfig` is defined in `src/resume_parser/extractors/ocr_extractor.py`. It controls language, render DPI, minimum native-text threshold, page segmentation mode, preprocessing, timeout, and the executable path. Pass a configured instance to `ResumeExtractionEngine(resume_folder, output_folder, ocr_config=...)`.

## Tests

Run from the project root (the directory containing `src`):

```powershell
python -m unittest discover -s tests -v
```

The OCR unit tests mock Tesseract for deterministic results. PDF integration tests use generated PDFs and mock the OCR call, so the test suite does not require the Tesseract executable to be installed. A separate end-to-end smoke test with a real scanned resume should be performed after installing Tesseract and its language data.
