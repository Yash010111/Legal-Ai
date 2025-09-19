"""
Helper utilities for Legal Mind AI
Contains PDF conversion and other utility functions
"""

import os
import sys
from typing import Optional


def convert_pdf_to_docx(pdf_path: str, docx_path: str, start_page: Optional[int] = None, end_page: Optional[int] = None) -> None:
    """
    Convert a PDF file to DOCX format using pdf2docx.
    
    Args:
        pdf_path: Path to the input PDF file
        docx_path: Path to the output DOCX file
        start_page: 0-based index of the first page to convert (default: 0)
        end_page: 0-based index of the last page to convert, inclusive (default: last page)
    
    Raises:
        SystemExit: If pdf2docx is not installed or PDF file doesn't exist
    """
    try:
        from pdf2docx import Converter
    except ImportError as exc:
        print("Dependency missing: pdf2docx. Install it with:", file=sys.stderr)
        print("  pip install pdf2docx", file=sys.stderr)
        raise SystemExit(1) from exc

    if not os.path.isfile(pdf_path):
        print(f"Input PDF not found: {pdf_path}", file=sys.stderr)
        raise SystemExit(1)

    # Ensure destination directory exists
    dest_dir = os.path.dirname(os.path.abspath(docx_path))
    if dest_dir and not os.path.isdir(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)

    # pdf2docx uses 0-based indexing for start/end
    # If end_page is provided, make it inclusive as users expect
    start = 0 if start_page is None else max(0, start_page)
    end = None if end_page is None else max(0, end_page)

    converter = Converter(pdf_path)
    try:
        converter.convert(docx_path, start=start, end=end)
    finally:
        converter.close()


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


def ensure_output_path(input_path: str, output_dir: Optional[str] = None, extension: str = ".docx") -> str:
    """
    Generate output path for converted file.
    
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
