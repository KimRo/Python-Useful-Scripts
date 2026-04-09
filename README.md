# Markdown Utilities

A small collection of Python scripts for converting and repairing Markdown files.

## Scripts

| Script | Description |
|--------|-------------|
| [md_to_pdf.py](src/md_to_pdf.py) | Convert Markdown files to PDF. Supports interactive menu, batch mode, and silent/automated mode. Automatically falls back to `md_repair` when conversion fails. → [docs](doc/md_to_pdf.md) |
| [md_to_odt.py](src/md_to_odt.py) | Convert Markdown files to ODT (Open Document Text) via pandoc. Same interface as `md_to_pdf.py`, including repair fallback. → [docs](doc/md_to_odt.md) |
| [pdf_to_md.py](src/pdf_to_md.py) | Convert PDF files to Markdown. Works well for text-based PDFs; scanned/image PDFs will produce little output. → [docs](doc/pdf_to_md.md) |
| [odt_to_md.py](src/odt_to_md.py) | Convert ODT files to Markdown via pandoc. Same interface as `pdf_to_md.py`. → [docs](doc/odt_to_md.md) |
| [md_repair.py](src/md_repair.py) | Clean and repair Markdown files: fix Unicode characters, correct heading structure, and renumber headings hierarchically. Can be used standalone or imported by the converter scripts. → [docs](doc/md_repair.md) |

## Installation

Install once to make all commands available from any directory:

```bash
pip install -e .
```

### External dependencies

- [`markdown-pdf`](https://pypi.org/project/markdown-pdf/) — required by `md-to-pdf`
- [pandoc](https://pandoc.org/installing.html) — required by `md-to-odt` and `odt-to-md`
- [`pymupdf`](https://pypi.org/project/pymupdf/) (v1.24+) — required by `pdf-to-md`
- [`markdown-heading-numbering`](https://pypi.org/project/markdown-heading-numbering/) — optional, used by `md-repair` for heading renumbering

## Quick Start

After installation, run commands from any directory:

```bash
# Convert a single file to PDF
md-to-pdf --file report.md

# Convert all Markdown files in a folder to ODT
md-to-odt docs/ --all

# Convert a PDF back to Markdown
pdf-to-md --file report.pdf

# Convert an ODT back to Markdown
odt-to-md --file report.odt

# Repair a Markdown file in place
md-repair report.md --inplace
```
