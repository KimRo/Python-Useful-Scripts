# md_to_pdf.py — Convert Markdown files to PDF.
#
# Usage:
#   python md_to_pdf.py [folder]              interactive menu to pick a file
#   python md_to_pdf.py [folder] --all        convert all files without menu
#   python md_to_pdf.py --file report.md      convert a single specific file
#   python md_to_pdf.py [folder] --silent     fully non-interactive (for automation)
#
# Silent-mode options (only applied when repair is triggered after a failed conversion):
#   --fix-headings shift|insert|skip   how to handle a missing H1 heading
#   --renumber / --no-renumber         whether to renumber headings hierarchically
#
# On first attempt the raw markdown is used.  If the PDF library fails, md_repair.py
# is called automatically to clean the content and the conversion is retried once.

import argparse
import sys
from pathlib import Path
from markdown_pdf import MarkdownPdf, Section

# ANSI color helpers (no-op when stdout is not a terminal)
if sys.platform == "win32":
    import os; os.system("")  # enable ANSI processing on Windows
def _red(msg: str)    -> str: return f"\033[31m{msg}\033[0m" if sys.stdout.isatty() else msg
def _yellow(msg: str) -> str: return f"\033[33m{msg}\033[0m" if sys.stdout.isatty() else msg


def get_md_files(folder: Path) -> list[Path]:
    return sorted(folder.glob("*.md"))


def _pdf_from_text(text: str, out_path: Path) -> None:
    """Create a PDF from markdown *text* and write it to *out_path*."""
    pdf = MarkdownPdf(toc_level=2)
    pdf.add_section(Section(text))
    pdf.save(out_path)


def convert_file(md_path: Path, output_folder: Path, silent: bool = False, fix_headings: str | None = None, renumber: bool | None = None) -> None:
    """
    Convert *md_path* to PDF.

    On first attempt the raw markdown is used.  If the PDF library raises an
    exception, md_repair.repair() is called to clean the content and the
    conversion is retried once.

    silent       : passed straight to md_repair.repair() so it never prompts.
    fix_headings / renumber are forwarded to md_repair when the repair path
    is triggered (None = interactive prompt unless silent=True).
    """
    out_path = output_folder / (md_path.stem + ".pdf")
    text = md_path.read_text(encoding="utf-8")

    try:
        _pdf_from_text(text, out_path)
        print(f"  Saved: {out_path.name}")
        return
    except Exception as first_error:
        print(_yellow(f"  Conversion failed ({first_error}); attempting repair…"))

    # ── Repair and retry ─────────────────────────────────────────────────────
    try:
        import md_repair
    except ImportError:
        print(_red("  Error: md_repair.py not found — cannot repair. Skipping."))
        return

    repaired = md_repair.repair(md_path, silent=silent, fix_headings=fix_headings, renumber=renumber)
    if repaired is None:
        # repair() signalled that the file should be skipped
        return

    try:
        _pdf_from_text(repaired, out_path)
        print(f"  Saved (after repair): {out_path.name}")
    except Exception as second_error:
        print(_red(f"  Error: conversion still failed after repair: {second_error}"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert Markdown files to PDF.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Silent mode examples (no prompts):
  python md_to_pdf.py --silent                       # convert all files in current dir
  python md_to_pdf.py docs/ --silent                 # convert all files in docs/
  python md_to_pdf.py --file report.md --silent      # convert one specific file
  python md_to_pdf.py --silent --renumber            # convert all and renumber headings
  python md_to_pdf.py --silent --fix-headings insert # insert H1 when missing
""",
    )
    parser.add_argument(
        "folder",
        nargs="?",
        default=".",
        help="Directory containing .md files (default: current directory)",
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
        help="Convert all .md files without prompting for selection",
    )
    parser.add_argument(
        "--silent",
        action="store_true",
        help=(
            "Non-interactive mode: implies --all (unless --file is given), "
            "--no-renumber, and --fix-headings=skip unless overridden"
        ),
    )
    parser.add_argument(
        "--fix-headings",
        choices=["shift", "insert", "skip"],
        dest="fix_headings",
        default=None,
        help=(
            "How to handle files whose first heading is not H1. "
            "'shift' promotes all headings, 'insert' adds a new H1 title, "
            "'skip' skips the file. Required when --silent is used and a file lacks H1."
        ),
    )
    renumber_group = parser.add_mutually_exclusive_group()
    renumber_group.add_argument(
        "--renumber",
        action="store_true",
        default=None,
        dest="renumber",
        help="Renumber headings hierarchically (1., 1.1, 1.1.1, …)",
    )
    renumber_group.add_argument(
        "--no-renumber",
        action="store_false",
        dest="renumber",
        help="Do not renumber headings (default in silent mode)",
    )
    return parser.parse_args()


_BANNER = """md_to_pdf.py — Convert Markdown files to PDF.

  Usage:
    python md_to_pdf.py [folder]                       interactive menu
    python md_to_pdf.py [folder] --all                 convert all files
    python md_to_pdf.py --file report.md               convert a single file
    python md_to_pdf.py [folder] --silent              non-interactive (automation)

  Repair options (used when PDF conversion fails and md_repair.py is invoked):
    --fix-headings shift|insert|skip   how to handle a missing H1 heading
    --renumber / --no-renumber         renumber headings hierarchically
"""


def main():
    args = parse_args()

    if not args.silent:
        print(_BANNER)

    _folder_arg = Path(args.folder).resolve()
    if _folder_arg.is_file():
        # Allow: python md_to_pdf.py file.md [--silent ...]
        if args.file:
            print(_red(f"Error: cannot use both a positional file and --file."))
            sys.exit(1)
        args.file = str(_folder_arg)
        folder = _folder_arg.parent
    elif _folder_arg.is_dir():
        folder = _folder_arg
    else:
        print(_red(f"Error: '{_folder_arg}' is not a valid file or directory."))
        sys.exit(1)

    silent = args.silent
    fix_headings: str | None = args.fix_headings
    renumber: bool | None = args.renumber  # None means "ask interactively" (unless silent)

    output_folder = folder

    # ── Single-file mode ────────────────────────────────────────────────────
    if args.file:
        target = Path(args.file)
        if not target.is_absolute():
            target = folder / target
        if not target.exists():
            print(f"Error: '{target}' does not exist.")
            sys.exit(1)
        print(f"Converting '{target.name}'...")
        convert_file(target, output_folder, silent=silent, fix_headings=fix_headings, renumber=renumber)
        print("\nDone.")
        return

    # ── Directory mode ───────────────────────────────────────────────────────
    md_files = get_md_files(folder)
    if not md_files:
        print(f"No .md files found in '{folder}'.")
        sys.exit(0)

    if silent or args.convert_all:
        # Non-interactive: convert all files
        print(f"\nConverting all {len(md_files)} file(s) in: {folder}\n")
        for f in md_files:
            convert_file(f, output_folder, silent=silent, fix_headings=fix_headings, renumber=renumber)
    else:
        # Interactive: present a menu
        print(f"\nMarkdown files in: {folder}\n")
        print("  0. Convert ALL")
        for i, f in enumerate(md_files, start=1):
            print(f"  {i}. {f.name}")

        print()
        try:
            choice = input("Enter number to convert: ").strip()
            selection = int(choice)
        except (ValueError, EOFError):
            print("Invalid input. Exiting.")
            sys.exit(1)

        if selection < 0 or selection > len(md_files):
            print(f"Invalid choice '{selection}'. Must be 0–{len(md_files)}.")
            sys.exit(1)

        print()
        if selection == 0:
            print(f"Converting all {len(md_files)} file(s)...")
            for f in md_files:
                convert_file(f, output_folder, silent=silent, fix_headings=fix_headings, renumber=renumber)
        else:
            target = md_files[selection - 1]
            print(f"Converting '{target.name}'...")
            convert_file(target, output_folder, silent=silent, fix_headings=fix_headings, renumber=renumber)

    print("\nDone.")


if __name__ == "__main__":
    main()
