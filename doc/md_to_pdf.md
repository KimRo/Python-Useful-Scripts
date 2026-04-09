# md_to_pdf.py

Convert Markdown files to PDF using the `markdown-pdf` library.

## Requirements

```bash
pip install markdown-pdf
```

## Usage

```bash
# Interactive menu — pick a file from the folder
md-to-pdf [folder]

# Convert all files in a folder without a menu
md-to-pdf [folder] --all

# Convert a single specific file
md-to-pdf --file report.md

# Fully non-interactive (for automation/scripts)
md-to-pdf [folder] --silent
```

## Options

| Flag | Description |
|------|-------------|
| `folder` | Directory containing `.md` files (default: current directory) |
| `--file FILE` | Convert a single file by name or path |
| `--all` | Convert all `.md` files without the selection menu |
| `--silent` | Non-interactive mode — implies `--all` and suppresses all prompts |
| `--fix-headings shift\|insert\|skip` | How to handle files whose first heading is not H1 (used during repair) |
| `--renumber` / `--no-renumber` | Renumber headings hierarchically (used during repair) |

## Repair Fallback

On the first attempt, the raw Markdown is used. If the PDF library raises an exception, [`md_repair.py`](md_repair.md) is called automatically to clean the content, and the conversion is retried once.

In `--silent` mode the repair step defaults to `--fix-headings skip` and `--no-renumber` unless you override them explicitly.

## Examples

```bash
# Convert all files silently, inserting an H1 when one is missing
md-to-pdf --silent --fix-headings insert

# Convert all files in docs/ and renumber headings if repair is triggered
md-to-pdf docs/ --silent --renumber

# Convert one file interactively
md-to-pdf --file notes.md
```
