# md_repair.py — Clean and repair Markdown files.
#
# Usage (standalone):
#   python md_repair.py file.md                         interactive repair
#   python md_repair.py file.md --silent                non-interactive, skip bad files
#   python md_repair.py file.md --fix-headings insert   insert H1 from filename if missing
#   python md_repair.py file.md --renumber              renumber headings hierarchically
#   python md_repair.py file.md --inplace               overwrite file with repaired content
#
# Imported by md_to_pdf.py as a fallback when PDF conversion fails.
#
# Extending:
#   1. Write a repair function:  def repair_<name>(text, stem, **kwargs) -> str | None
#      Return the (possibly modified) text, or None to skip the file.
#   2. Append it to REPAIR_PIPELINE near the bottom of this file.

"""
md_repair.py — Markdown cleaning and repair utilities.

Can be used as a standalone script or imported by other tools (e.g. md_to_pdf.py).

Adding a new repair step
------------------------
1. Write a function with the signature:
       def repair_<name>(text: str, stem: str, **kwargs) -> str | None
   Return the (possibly modified) text, or None to signal that the file
   should be skipped entirely.
2. Register it in REPAIR_PIPELINE at the bottom of this file.
"""

import argparse
import re
import sys
from pathlib import Path

# ANSI color helpers (no-op when stdout is not a terminal)
if sys.platform == "win32":
    import os; os.system("")  # enable ANSI processing on Windows
def _red(msg: str)    -> str: return f"\033[31m{msg}\033[0m" if sys.stdout.isatty() else msg
def _yellow(msg: str) -> str: return f"\033[33m{msg}\033[0m" if sys.stdout.isatty() else msg

try:
    from markdown_heading_numbering import format_markdown_text as _apply_heading_numbers
    _HAS_NUMBERING_LIB = True
except ImportError:
    _HAS_NUMBERING_LIB = False

# Heading numbering config
HEADING_NUMBER_START_LEVEL = 2
HEADING_NUMBER_END_LEVEL   = 6
HEADING_NUMBER_INITIAL     = 1

# Default options used when --silent is active and no explicit flag overrides them.
# Change these to alter silent-mode behaviour without touching the rest of the script.
DEFAULT_OPTIONS = {
    "fix_headings": "shift",   # "shift" | "insert" | "skip"
    "renumber":     True,    # True | False
    "inplace":      False,    # True | False
}


# ── Low-level helpers ────────────────────────────────────────────────────────

def get_first_heading_level(text: str) -> int | None:
    """Return the level of the first Markdown heading, or None."""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return len(stripped) - len(stripped.lstrip("#"))
    return None


def shift_headings(text: str, shift: int) -> str:
    """Promote all headings by `shift` levels (e.g. shift=1 turns ## → #)."""
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            new_level = max(1, level - shift)
            lines.append("#" * new_level + stripped[level:])
        else:
            lines.append(line)
    return "\n".join(lines)


def _strip_existing_numbers(heading_text: str) -> str:
    """Remove a leading numeric prefix like '1.', '1.2.', '1.2.3' from heading text."""
    return re.sub(r'^(?:\d+\.)*\d+\.?\s*', '', heading_text)


def _renumber_headings_fallback(text: str) -> str:
    """Hierarchical renumbering without the external library."""
    counters: list[int] = [0] * 7
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            rest  = _strip_existing_numbers(stripped[level:].strip())
            if level < HEADING_NUMBER_START_LEVEL:
                for sub in range(HEADING_NUMBER_START_LEVEL, 7):
                    counters[sub] = 0
                lines.append(line)
            elif level <= HEADING_NUMBER_END_LEVEL:
                counters[level] += 1
                for sub in range(level + 1, 7):
                    counters[sub] = 0
                number = ".".join(
                    str(counters[lvl])
                    for lvl in range(HEADING_NUMBER_START_LEVEL, level + 1)
                )
                lines.append("#" * level + " " + number + " " + rest)
            else:
                lines.append(line)
        else:
            lines.append(line)
    return "\n".join(lines)


def apply_heading_numbers(text: str) -> str:
    """Renumber headings hierarchically (1., 1.1, 1.1.1, …)."""
    if _HAS_NUMBERING_LIB:
        return _apply_heading_numbers(
            text,
            start_from_level=HEADING_NUMBER_START_LEVEL,
            end_at_level=HEADING_NUMBER_END_LEVEL,
            initial_numbering=HEADING_NUMBER_INITIAL,
        )
    return _renumber_headings_fallback(text)


# ── Unicode replacement table ─────────────────────────────────────────────────
# Characters that cause some PDF/Markdown parsers to fail, mapped to safe
# ASCII or HTML-entity equivalents.  Extend this dict as needed.
_UNICODE_REPLACEMENTS: dict[str, str] = {
    "\u2014": "--",   # em dash          —
    "\u2013": "-",    # en dash          –
    "\u2018": "'",    # left single quote '
    "\u2019": "'",    # right single quote '
    "\u201c": '"',    # left double quote "
    "\u201d": '"',    # right double quote "
    "\u2026": "...",  # ellipsis          …
    "\u00a0": " ",    # non-breaking space
    "\u00ad": "",     # soft hyphen
}


# ── Repair steps ─────────────────────────────────────────────────────────────
# Each step receives (text, stem, **kwargs) and returns text | None.
# None means "skip this file".  Add new steps here and register them below.

def repair_unicode(text: str, stem: str, **_) -> str:
    """Replace typographic Unicode characters that some PDF converters reject."""
    for char, replacement in _UNICODE_REPLACEMENTS.items():
        text = text.replace(char, replacement)
    return text

def repair_heading_structure(text: str, stem: str, fix_headings: str | None = None, **_) -> str | None:
    """
    Ensure the document starts with an H1 heading.

    fix_headings : 'shift' | 'insert' | 'skip', or None to ask interactively.
    """
    first_level = get_first_heading_level(text)
    if first_level is None or first_level == 1:
        return text  # Nothing to fix

    if fix_headings is not None:
        if fix_headings == "shift":
            return shift_headings(text, shift=first_level - 1)
        elif fix_headings == "insert":
            return f"# {stem}\n\n{text}"
        else:  # "skip"
            print(_yellow(f"  Skipped (no H1): {stem}.md"))
            return None

    # Interactive
    print(_yellow(f"\n  Warning: '{stem}.md' has no H1 heading (first heading is H{first_level})."))
    print("  How would you like to fix this?")
    print("    1. Shift all headings up so the first heading becomes H1")
    print(f"    2. Insert '# {stem}' as a new H1 at the top")
    print("    3. Skip this file")
    while True:
        choice = input("  Enter 1, 2 or 3: ").strip()
        if choice == "1":
            return shift_headings(text, shift=first_level - 1)
        elif choice == "2":
            return f"# {stem}\n\n{text}"
        elif choice == "3":
            return None
        else:
            print("  Invalid input, please enter 1, 2 or 3.")


def repair_renumber_headings(text: str, stem: str, renumber: bool | None = None, **_) -> str:
    """
    Optionally renumber headings hierarchically.

    renumber : True/False, or None to ask interactively.
    """
    if renumber is True:
        return apply_heading_numbers(text)
    if renumber is False:
        return text

    # Interactive
    while True:
        answer = input("  Renumber headings? (y/n): ").strip().lower()
        if answer == "y":
            return apply_heading_numbers(text)
        elif answer == "n":
            return text
        else:
            print("  Invalid input, please enter y or n.")


# ── Pipeline registry ─────────────────────────────────────────────────────────
# Steps are applied in order.  Add new repair functions to this list.

REPAIR_PIPELINE = [
    repair_unicode,           # sanitize problematic characters first
    repair_heading_structure,
    repair_renumber_headings,
]


# ── Public API ────────────────────────────────────────────────────────────────

def repair(md_path: Path, silent: bool = False, **kwargs) -> str | None:
    """
    Apply all repair steps to *md_path* and return the cleaned text.

    Returns None if any step signals that the file should be skipped.

    silent   : if True, fill in any unset kwargs from DEFAULT_OPTIONS so that
               repair steps never fall through to interactive prompts.
    Remaining keyword arguments are forwarded to every repair step, so you can
    pass fix_headings='shift', renumber=False, etc.
    """
    if silent:
        for key in ("fix_headings", "renumber"):
            if kwargs.get(key) is None:
                kwargs[key] = DEFAULT_OPTIONS[key]

    text = md_path.read_text(encoding="utf-8")
    stem = md_path.stem
    for step in REPAIR_PIPELINE:
        text = step(text, stem, **kwargs)
        if text is None:
            return None
    return text


# ── Standalone CLI ────────────────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clean and repair Markdown files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python md_repair.py report.md                        # interactive
  python md_repair.py report.md --silent               # silent, skip bad files
  python md_repair.py report.md --fix-headings insert --renumber
  python md_repair.py report.md --inplace              # overwrite file
""",
    )
    parser.add_argument("file", help="Markdown file to repair")
    parser.add_argument(
        "--silent",
        action="store_true",
        help="Non-interactive: --fix-headings=skip and --no-renumber unless overridden",
    )
    parser.add_argument(
        "--fix-headings",
        choices=["shift", "insert", "skip"],
        dest="fix_headings",
        default=None,
    )
    renumber_group = parser.add_mutually_exclusive_group()
    renumber_group.add_argument("--renumber",    action="store_true",  default=None, dest="renumber")
    renumber_group.add_argument("--no-renumber", action="store_false", dest="renumber")
    parser.add_argument(
        "--inplace",
        action="store_true",
        help="Overwrite the source file with the repaired content",
    )
    return parser.parse_args()


_BANNER = """md_repair.py — Clean and repair Markdown files.

  Usage:
    python md_repair.py file.md                          interactive repair
    python md_repair.py file.md --silent                 non-interactive, skip bad files
    python md_repair.py file.md --fix-headings insert    insert H1 from filename if missing
    python md_repair.py file.md --renumber               renumber headings hierarchically
    python md_repair.py file.md --inplace                overwrite file with repaired content

  Extending:
    1. Write:  def repair_<name>(text, stem, **kwargs) -> str | None
    2. Append it to REPAIR_PIPELINE at the bottom of this file.
"""


def main() -> None:
    args = _parse_args()

    if not args.silent:
        print(_BANNER)

    md_path = Path(args.file)
    if not md_path.exists():
        print(f"Error: '{md_path}' does not exist.")
        sys.exit(1)

    fix_headings: str | None = args.fix_headings
    renumber: bool | None    = args.renumber

    if args.silent:
        if fix_headings is None:
            fix_headings = DEFAULT_OPTIONS["fix_headings"]
        if renumber is None:
            renumber = DEFAULT_OPTIONS["renumber"]
        if not args.inplace and DEFAULT_OPTIONS["inplace"]:
            args.inplace = True

    result = repair(md_path, fix_headings=fix_headings, renumber=renumber)

    if result is None:
        print("File skipped.")
        sys.exit(0)

    if args.inplace:
        md_path.write_text(result, encoding="utf-8")
        print(f"Repaired: {md_path.name}")
    else:
        print(result)


if __name__ == "__main__":
    main()
