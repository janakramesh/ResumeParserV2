# Resume Parser V2

A Python-based resume parsing system designed to extract, analyze, and structure information from resumes with a focus on accuracy, reliability, and local processing.

### Features

- **Multi-format Support:** Processes PDF, DOCX, and image-based resumes.
- **OCR Integration:** Uses Tesseract OCR to extract text from scanned PDFs and images.
- **Intelligent Text Extraction:** Handles PDF layouts, DOCX tables, headers, footers, and hyperlinks.
- **Resume Understanding:** Detects and separates sections such as education, experience, and technical skills.
- **Structured Data Extraction:** Extracts candidate names, email addresses, phone numbers, addresses, LinkedIn, GitHub, education, skills, and experience.
- **Input Validation:** Identifies corrupted, empty, and unsupported files.
- **Batch Processing:** Processes multiple resumes while handling individual file failures.
- **Organized Outputs:** Maintains raw text, cleaned text, and structured JSON outputs.

### Tech Stack

- Python 3.13
- PyMuPDF
- python-docx
- Tesseract OCR
- Pytesseract
- Pillow
- OpenCV (optional)
- phonenumbers

### Project Structure

```text
ResumeParserV2/
│
├── src/
│   └── resume_parser/
│       ├── extractors/
│       ├── ingestion/
│       ├── understanding/
│       ├── utils/
│       └── extraction_engine.py
│
├── resume/
│   └── Input resumes
│
├── output/
│   ├── raw/
│   ├── cleaned/
│   └── structured/
│
├── logs/
├── tests/
├── main.py
└── README.md
```

### Processing Pipeline

1. Scan and validate input files.
2. Extract text using native PDF/DOCX extraction or OCR.
3. Clean and normalize extracted text.
4. Detect and split resume sections.
5. Extract structured candidate information.
6. Generate JSON outputs and processing logs.

### Getting Started

1. Clone the repository.
2. Create and activate a Python 3.13 virtual environment.
3. Install the project dependencies.
4. Install Tesseract OCR for scanned document support.
5. Place resumes inside the input folder.
6. Run the application using its entry-point script.

### Output

The system generates:

- **Raw:** Original extracted text.
- **Cleaned:** Normalized resume text.
- **Structured:** Extracted candidate information in JSON format.

### Project Goal

To build a reliable, extensible, and efficient resume parsing system that converts unstructured resumes into structured candidate data.