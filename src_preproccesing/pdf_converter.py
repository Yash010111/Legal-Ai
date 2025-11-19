
"""
PDF to Word converter using helper utilities
"""

import argparse
import os
import sys
from typing import Optional

# Import from helpers
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from helpers.pdf_utils import convert_pdf_to_txt, find_pdf_files, ensure_output_path


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Convert a PDF file or a directory of PDFs to plain text (.txt) using PyPDF2."
    )
    parser.add_argument(
        "input_path",
        nargs="?",
        help="Path to an input PDF file or a directory containing PDFs (default: 'Testing pdfs' in current directory)",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output_txt",
        help="Path to the output TXT file (single-file mode only)",
    )
    parser.add_argument(
        "--output-dir",
        dest="output_dir",
        help="Directory to write TXT files when converting a folder (default: next to each PDF)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Main function for PDF to TXT conversion"""
    if argv is None:
        argv = sys.argv[1:]
    args = parse_args(argv)

    # Determine input path: file or directory
    default_dir = os.path.abspath(os.path.join(os.getcwd(), "Testing pdfs"))
    input_path = os.path.abspath(args.input_path) if args.input_path else default_dir

    if os.path.isdir(input_path):
        # Directory mode
        pdf_files = find_pdf_files(input_path)

        if not pdf_files:
            print(f"No PDFs found in: {input_path}", file=sys.stderr)
            return 1

        successes = 0
        failures = 0
        for pdf_file in pdf_files:
            try:
                output_txt = ensure_output_path(pdf_file, args.output_dir, ".txt")
                convert_pdf_to_txt(
                    pdf_path=pdf_file,
                    txt_path=output_txt,
                )
                print(f"Converted: {pdf_file}\n-> {output_txt}")
                successes += 1
            except Exception as e:  # noqa: BLE001
                print(f"Failed: {pdf_file} -> {e}", file=sys.stderr)
                failures += 1

        print(f"Done. Success: {successes}, Failed: {failures}")
        return 0 if failures == 0 else 2

    # Single-file mode
    input_pdf = input_path
    if not input_pdf.lower().endswith(".pdf"):
        print("Input file must be a .pdf", file=sys.stderr)
        return 1

    if args.output_txt:
        output_txt = os.path.abspath(args.output_txt)
    else:
        output_txt = ensure_output_path(input_pdf, extension=".txt")

    try:
        convert_pdf_to_txt(
            pdf_path=input_pdf,
            txt_path=output_txt,
        )
    except SystemExit as e:
        return int(e.code) if isinstance(e.code, int) else 1
    except Exception as e:  # noqa: BLE001 - provide friendly output
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(f"Converted: {input_pdf}\n-> {output_txt}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
