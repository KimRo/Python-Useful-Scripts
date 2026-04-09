# odt_to_md.py

Convert ODT (Open Document Text) files to Markdown via [pandoc](https://pandoc.org).

## Requirements

- **pandoc** must be installed and available on `PATH`.  
  Download: <https://pandoc.org/installing.html>

## Usage

```bash
# Interactive menu — pick a file from the folder
odt-to-md [folder]

# Convert all files in a folder without a menu
odt-to-md [folder] --all

# Convert a single specific file
odt-to-md --file report.odt

# Fully non-interactive (for automation/scripts)
odt-to-md [folder] --silent
```

## Options

| Flag | Description |
|------|-------------|
| `folder` | Directory containing `.odt` files (default: current directory) |
| `--file FILE` | Convert a single file by name or path |
| `--all` | Convert all `.odt` files without the selection menu |
| `--silent` | Non-interactive mode — implies `--all` and suppresses all prompts |

## Examples

```bash
# Convert all ODT files in the current directory silently
odt-to-md --silent

# Convert all files in a specific folder
odt-to-md docs/ --all

# Convert one file interactively
odt-to-md --file notes.odt
```
