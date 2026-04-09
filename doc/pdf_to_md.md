# pdf_to_md.py

Convert PDF files to Markdown using the `pymupdf` library.

## Requirements

```bash
pip install pymupdf
```

Requires pymupdf v1.24 or later.

## Limitations

PDF is a layout format, not a semantic one. Output quality depends on how the PDF was created:

- **Text-based PDFs** (exported from Word, LibreOffice, etc.) convert well, with headings and structure reasonably preserved.
- **Scanned / image-only PDFs** will produce little or no text. Use an OCR tool first.

## Usage

```bash
# Interactive menu — pick a file from the folder
pdf-to-md [folder]

# Convert all files in a folder without a menu
pdf-to-md [folder] --all

# Convert a single specific file
pdf-to-md --file report.pdf

# Fully non-interactive (for automation/scripts)
pdf-to-md [folder] --silent
```

## Options

| Flag | Description |
|------|-------------|
| `folder` | Directory containing `.pdf` files (default: current directory) |
| `--file FILE` | Convert a single file by name or path |
| `--all` | Convert all `.pdf` files without the selection menu |
| `--silent` | Non-interactive mode — implies `--all` and suppresses all prompts |

## Output Format

Each page is separated by a `---` horizontal rule. Headings, bold, italic, and lists are inferred from the PDF's visual structure by pymupdf.

## Examples

```bash
# Convert all PDF files in the current directory silently
pdf-to-md --silent

# Convert all files in a specific folder
pdf-to-md docs/ --all

# Convert one file interactively
pdf-to-md --file report.pdf
```
