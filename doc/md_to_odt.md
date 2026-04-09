# md_to_odt.py

Convert Markdown files to ODT (Open Document Text) via [pandoc](https://pandoc.org).

## Requirements

- **pandoc** must be installed and available on `PATH`.  
  Download: <https://pandoc.org/installing.html>

## Usage

```bash
# Interactive menu — pick a file from the folder
md-to-odt [folder]

# Convert all files in a folder without a menu
md-to-odt [folder] --all

# Convert a single specific file
md-to-odt --file report.md

# Fully non-interactive (for automation/scripts)
md-to-odt [folder] --silent
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

On the first attempt, the raw Markdown is passed to pandoc. If pandoc returns a non-zero exit code, [`md_repair.py`](md_repair.md) is called automatically to clean the content, and the conversion is retried once.

In `--silent` mode the repair step defaults to `--fix-headings skip` and `--no-renumber` unless you override them explicitly.

## Examples

```bash
# Convert all files silently, inserting an H1 when one is missing
md-to-odt --silent --fix-headings insert

# Convert all files in docs/ and renumber headings if repair is triggered
md-to-odt docs/ --silent --renumber

# Convert one file interactively
md-to-odt --file notes.md
```
