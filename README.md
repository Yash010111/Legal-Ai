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

## 🚀 Quick Start

### Start the Server
```bash
python start_server.py
# OR
python -m mcp_server.server
```

### Start a Client
```bash
python start_client.py
# OR
python client/client.py  # Local client
```

### Test the Setup
```bash
python mcp_server/test_mcp_communication.py
```

## Project Structure

```
Legal-Ai/
├── README.md                    # Project overview & setup
├── CLIENT_SERVER_GUIDE.md       # Client & Server usage guide
├── NGROK_SETUP_GUIDE.md         # Ngrok setup guide
├── pyproject.toml               # Project dependencies
├── requirements.txt             # Legacy dependencies
│
├── mcp_server/                  # MCP Server Files
│   ├── __init__.py
│   ├── server.py                # Main MCP server
│   ├── routes.py                # API routes
│   └── test_mcp_communication.py # Server tests
│
├── client/                      # Client Files
│   ├── __init__.py
│   ├── client.py                # Local client
│   ├── ngrok_client.py          # Remote client (ngrok)
│   └── remote_client.py         # Remote client (network)
│
├── src/                         # Core AI Engine
│   ├── __init__.py
│   ├── ai_engine.py             # Main AI inference logic
│   ├── text_utils.py            # Text cleaning, formatting, parsing
│   └── pdf_converter.py         # PDF to Word converter
│
├── dat/                         # Data Files
│   └── sample_docs/
│       └── constitution_qa.json
│
├── helpers/                     # Helper utilities
│   └── pdf_utils.py
│
├── notebooks/                   # Jupyter notebooks
│   └── demo.ipynb
│
├── tests/                       # Tests
│   └── test_ai_engine.py
│
├── start_server.py              # Server startup script
└── start_client.py              # Client launcher script
```

## Usage

### PDF → Word Converter

#### 1) Convert all PDFs in `Testing pdfs` (default)
```bash
python src/pdf_converter.py
```

#### 2) Convert a specific folder
```bash
python src/pdf_converter.py "path/to/pdf/folder"
```

### AI Engine

#### Basic Usage
```python
from src.ai_engine import LegalMindAI

# Initialize AI engine
ai = LegalMindAI()
ai.load_model()

# Analyze a document
analysis = ai.analyze_document("Your legal document text here")

# Answer legal questions
answer = ai.answer_legal_question("What is a contract?")
```

### MCP Server

#### Start the server
```bash
python mcp_server/server.py
```

The server will be available at `http://localhost:8000` with API documentation at `http://localhost:8000/docs`.

### Notes
- Free/offline library used: `pdf2docx`. For complex legal layouts, results vary by file; review critical outputs.
- For best performance on large datasets, run on SSD and process subfolders in parallel sessions.

### License
This project is licensed under the MIT License. See `LICENSE` for details.
