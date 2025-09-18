import argparse
import os
import sys


def convert_pdf_to_docx(pdf_path: str, docx_path: str, start_page: int | None, end_page: int | None) -> None:
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


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a PDF file or a directory of PDFs to Word (.docx) using pdf2docx."
    )
    parser.add_argument(
        "input_path",
        nargs="?",
        help="Path to an input PDF file or a directory containing PDFs (default: 'Testing pdfs' in current directory)",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output_docx",
        help="Path to the output DOCX file (single-file mode only)",
    )
    parser.add_argument(
        "--output-dir",
        dest="output_dir",
        help="Directory to write DOCX files when converting a folder (default: next to each PDF)",
    )
    parser.add_argument(
        "--start-page",
        type=int,
        default=None,
        help="0-based index of the first page to convert (default: 0)",
    )
    parser.add_argument(
        "--end-page",
        type=int,
        default=None,
        help="0-based index of the last page to convert, inclusive (default: last page)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    args = parse_args(argv)

    # Determine input path: file or directory
    default_dir = os.path.abspath(os.path.join(os.getcwd(), "Testing pdfs"))
    input_path = os.path.abspath(args.input_path) if args.input_path else default_dir

    if os.path.isdir(input_path):
        # Directory mode
        pdf_files = [
            os.path.join(input_path, name)
            for name in os.listdir(input_path)
            if name.lower().endswith(".pdf") and os.path.isfile(os.path.join(input_path, name))
        ]

        if not pdf_files:
            print(f"No PDFs found in: {input_path}", file=sys.stderr)
            return 1

        successes = 0
        failures = 0
        for pdf_file in sorted(pdf_files):
            try:
                if args.output_dir:
                    os.makedirs(args.output_dir, exist_ok=True)
                    base_name = os.path.splitext(os.path.basename(pdf_file))[0] + ".docx"
                    output_docx = os.path.abspath(os.path.join(args.output_dir, base_name))
                else:
                    output_docx = os.path.splitext(pdf_file)[0] + ".docx"

                convert_pdf_to_docx(
                    pdf_path=pdf_file,
                    docx_path=output_docx,
                    start_page=args.start_page,
                    end_page=args.end_page,
                )
                print(f"Converted: {pdf_file}\n-> {output_docx}")
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

    if args.output_docx:
        output_docx = os.path.abspath(args.output_docx)
    else:
        base, _ = os.path.splitext(os.path.abspath(input_pdf))
        output_docx = base + ".docx"

    try:
        convert_pdf_to_docx(
            pdf_path=input_pdf,
            docx_path=output_docx,
            start_page=args.start_page,
            end_page=args.end_page,
        )
    except SystemExit as e:
        return int(e.code) if isinstance(e.code, int) else 1
    except Exception as e:  # noqa: BLE001 - provide friendly output
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(f"Converted: {input_pdf}\n-> {output_docx}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


