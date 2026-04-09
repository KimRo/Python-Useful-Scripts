# pdf_to_md.py — Convert PDF files to Markdown.
#
# Requires pymupdf (v1.24+):
#   pip install pymupdf
#
# Note: PDF does not store semantic structure (headings, lists, etc.) reliably.
# Output quality depends on how the PDF was created. Text-based PDFs work well;
# scanned/image-only PDFs will produce little or no text.
#
# Usage:
#   python src/pdf_to_md.py [folder]              interactive menu to pick a file
#   python src/pdf_to_md.py [folder] --all        convert all files without menu
#   python src/pdf_to_md.py --file report.pdf     convert a single specific file
#   python src/pdf_to_md.py [folder] --silent     fully non-interactive (for automation)

import argparse
import sys
from pathlib import Path

# ANSI color helpers (no-op when stdout is not a terminal)
if sys.platform == "win32":
    import os; os.system("")  # enable ANSI processing on Windows
def _red(msg: str)    -> str: return f"\033[31m{msg}\033[0m" if sys.stdout.isatty() else msg
def _yellow(msg: str) -> str: return f"\033[33m{msg}\033[0m" if sys.stdout.isatty() else msg


def _check_pymupdf() -> None:
    """Exit with a clear message if pymupdf is not installed."""
    try:
        import fitz  # noqa: F401
        if not hasattr(fitz.Page, "get_text"):
            raise ImportError
    except ImportError:
        print(_red("Error: pymupdf is not installed or is too old (requires v1.24+)."))
        print("  Install it with:  pip install pymupdf")
        sys.exit(1)


def get_pdf_files(folder: Path) -> list[Path]:
    return sorted(folder.glob("*.pdf"))


def convert_file(pdf_path: Path, output_folder: Path) -> None:
    """Convert *pdf_path* to Markdown and write it to *output_folder*."""
    import fitz

    out_path = output_folder / (pdf_path.stem + ".md")

    try:
        doc = fitz.open(str(pdf_path))
    except Exception as e:
        print(_red(f"  Error: could not open '{pdf_path.name}': {e}"))
        return

    try:
        pages_md = [page.get_text("markdown") for page in doc]
    except Exception as e:
        print(_red(f"  Error: text extraction failed for '{pdf_path.name}': {e}"))
        return
    finally:
        doc.close()

    text = "\n\n---\n\n".join(pages_md).strip()

    if not text:
        print(_yellow(f"  Warning: no text extracted from '{pdf_path.name}' (scanned/image PDF?). Skipping."))
        return

    out_path.write_text(text, encoding="utf-8")
    print(f"  Saved: {out_path.name}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert PDF files to Markdown.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Silent mode examples (no prompts):
  python src/pdf_to_md.py --silent                       # convert all files in current dir
  python src/pdf_to_md.py docs/ --silent                 # convert all files in docs/
  python src/pdf_to_md.py --file report.pdf --silent     # convert one specific file
""",
    )
    parser.add_argument(
        "folder",
        nargs="?",
        default=".",
        help="Directory containing .pdf files (default: current directory)",
    )
    parser.add_argument(
        "--file",
        metavar="FILE",
        help="Convert a single file by name (relative to folder, or an absolute path)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        dest="convert_all",
        help="Convert all .pdf files without prompting for selection",
    )
    parser.add_argument(
        "--silent",
        action="store_true",
        help="Non-interactive mode: implies --all (unless --file is given)",
    )
    return parser.parse_args()


_BANNER = """pdf_to_md.py — Convert PDF files to Markdown.

  Requires: pymupdf v1.24+  (pip install pymupdf)

  Note: output quality depends on the PDF. Text-based PDFs convert well;
  scanned/image-only PDFs will produce little or no text.

  Usage:
    python src/pdf_to_md.py [folder]                       interactive menu
    python src/pdf_to_md.py [folder] --all                 convert all files
    python src/pdf_to_md.py --file report.pdf              convert a single file
    python src/pdf_to_md.py [folder] --silent              non-interactive (automation)
"""


def main():
    args = parse_args()

    if not args.silent:
        print(_BANNER)

    _check_pymupdf()

    _folder_arg = Path(args.folder).resolve()
    if _folder_arg.is_file():
        # Allow: python src/pdf_to_md.py file.pdf [--silent ...]
        if args.file:
            print(_red("Error: cannot use both a positional file and --file."))
            sys.exit(1)
        args.file = str(_folder_arg)
        folder = _folder_arg.parent
    elif _folder_arg.is_dir():
        folder = _folder_arg
    else:
        print(_red(f"Error: '{_folder_arg}' is not a valid file or directory."))
        sys.exit(1)

    output_folder = folder

    # ── Single-file mode ────────────────────────────────────────────────────
    if args.file:
        target = Path(args.file)
        if not target.is_absolute():
            target = folder / target
        if not target.exists():
            print(_red(f"Error: '{target}' does not exist."))
            sys.exit(1)
        print(f"Converting '{target.name}'...")
        convert_file(target, output_folder)
        print("\nDone.")
        return

    # ── Directory mode ───────────────────────────────────────────────────────
    pdf_files = get_pdf_files(folder)
    if not pdf_files:
        print(f"No .pdf files found in '{folder}'.")
        sys.exit(0)

    if args.silent or args.convert_all:
        print(f"\nConverting all {len(pdf_files)} file(s) in: {folder}\n")
        for f in pdf_files:
            convert_file(f, output_folder)
    else:
        # Interactive: present a menu
        print(f"\nPDF files in: {folder}\n")
        print("  0. Convert ALL")
        for i, f in enumerate(pdf_files, start=1):
            print(f"  {i}. {f.name}")

        print()
        try:
            choice = input("Enter number to convert: ").strip()
            selection = int(choice)
        except (ValueError, EOFError):
            print("Invalid input. Exiting.")
            sys.exit(1)

        if selection < 0 or selection > len(pdf_files):
            print(f"Invalid choice '{selection}'. Must be 0–{len(pdf_files)}.")
            sys.exit(1)

        print()
        if selection == 0:
            print(f"Converting all {len(pdf_files)} file(s)...")
            for f in pdf_files:
                convert_file(f, output_folder)
        else:
            target = pdf_files[selection - 1]
            print(f"Converting '{target.name}'...")
            convert_file(target, output_folder)

    print("\nDone.")


if __name__ == "__main__":
    main()
