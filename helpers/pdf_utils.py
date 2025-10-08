"""
Helper utilities for Legal Mind AI
Contains PDF conversion and other utility functions
"""

import os
import sys
from typing import Optional


def convert_pdf_to_txt(pdf_path: str, txt_path: str) -> None:
    """
    Convert a PDF file directly to plain text (.txt).
    
    Args:
        pdf_path: Path to the input PDF file
        txt_path: Path to the output TXT file
    
    Raises:
        SystemExit: If PyPDF2 is not installed or PDF file doesn't exist
    """
    try:
        import PyPDF2
    except ImportError as exc:
        print("Dependency missing: PyPDF2. Install it with:", file=sys.stderr)
        print("  pip install PyPDF2", file=sys.stderr)
        raise SystemExit(1) from exc

    if not os.path.isfile(pdf_path):
        print(f"Input PDF not found: {pdf_path}", file=sys.stderr)
        raise SystemExit(1)

    # Ensure destination directory exists
    dest_dir = os.path.dirname(os.path.abspath(txt_path))
    if dest_dir and not os.path.isdir(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)

    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""

    with open(txt_path, "w", encoding="utf-8") as out_file:
        out_file.write(text)


def find_pdf_files(directory: str) -> list[str]:
    """
    Find all PDF files in a directory.
    
    Args:
        directory: Path to the directory to search
        
    Returns:
        List of paths to PDF files found in the directory
    """
    if not os.path.isdir(directory):
        return []
    
    pdf_files = [
        os.path.join(directory, name)
        for name in os.listdir(directory)
        if name.lower().endswith(".pdf") and os.path.isfile(os.path.join(directory, name))
    ]
    
    return sorted(pdf_files)


def ensure_output_path(input_path: str, output_dir: Optional[str] = None, extension: str = ".txt") -> str:
    """
    Generate output path for converted file (default .txt).
    
    Args:
        input_path: Path to the input file
        output_dir: Optional output directory (if None, uses same directory as input)
        extension: File extension for output file
    
    Returns:
        Path for the output file
    """
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(input_path))[0] + extension
        return os.path.abspath(os.path.join(output_dir, base_name))
    else:
        return os.path.splitext(input_path)[0] + extension
