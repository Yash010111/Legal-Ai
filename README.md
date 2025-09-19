# Legal Mind AI

An intelligent legal assistant platform designed to streamline legal document processing and analysis.

### Project Report
- Whole common project continuous report: [Google Doc](https://docs.google.com/document/d/1ujIPLa_VAtKPUq2dBzsqleXNELAGpozhfcepXkx0Z_E/edit?tab=t.0)

## Features

### PDF → Word Converter
- Convert a single PDF or an entire folder of PDFs
- Preserves text, basic layout, and tables (best-effort)
- Fully offline and free (uses `pdf2docx`)
- Optimized for legal documents

### Requirements
- Python 3.9+ (Windows, macOS, Linux)

### Setup

#### First time setup (install uv - one time only)
```bash
pip install uv
```

#### Install dependencies
```bash
uv sync
```

**Note:** Run `uv sync` every time a new dependency is added to the project.

## Usage

### PDF → Word Converter

#### 1) Convert all PDFs in `Testing pdfs` (default)
```bash
python convert_pdf_to_word.py
```

#### 2) Convert a specific folder
```bash
python convert_pdf_to_word.py "E:\mp\Legal-Ai\Testing pdfs"
```

### Notes
- Free/offline library used: `pdf2docx`. For complex legal layouts, results vary by file; review critical outputs.
- For best performance on large datasets, run on SSD and process subfolders in parallel sessions.

### License
This project is licensed under the MIT License. See `LICENSE` for details.
