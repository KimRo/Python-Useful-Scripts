# Markdown Utilities

A small collection of Python scripts for converting and repairing Markdown files.

## Scripts

| Script | Description |
|--------|-------------|
| [md_to_pdf.py](md_to_pdf.py) | Convert Markdown files to PDF. Supports interactive menu, batch mode, and silent/automated mode. Automatically falls back to `md_repair` when conversion fails. → [docs](doc/md_to_pdf.md) |
| [md_to_odt.py](md_to_odt.py) | Convert Markdown files to ODT (Open Document Text) via pandoc. Same interface as `md_to_pdf.py`, including repair fallback. → [docs](doc/md_to_odt.md) |
| [md_repair.py](md_repair.py) | Clean and repair Markdown files: fix Unicode characters, correct heading structure, and renumber headings hierarchically. Can be used standalone or imported by the converter scripts. → [docs](doc/md_repair.md) |

## Requirements

- Python 3.10+
- [`markdown-pdf`](https://pypi.org/project/markdown-pdf/) — required by `md_to_pdf.py`
- [pandoc](https://pandoc.org/installing.html) — required by `md_to_odt.py`
- [`markdown-heading-numbering`](https://pypi.org/project/markdown-heading-numbering/) — optional, used by `md_repair.py` for heading renumbering

## Quick Start

```bash
# Convert a single file to PDF
python md_to_pdf.py --file report.md

# Convert all Markdown files in a folder to ODT
python md_to_odt.py docs/ --all

# Repair a Markdown file in place
python md_repair.py report.md --inplace
```
