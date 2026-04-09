# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Installation

```bash
pip install -e .
```

This registers five CLI commands: `md-to-pdf`, `md-to-odt`, `pdf-to-md`, `odt-to-md`, `md-repair`.

External tools must be installed separately: `markdown-pdf`, `pymupdf` (v1.24+), `pandoc`, and optionally `markdown-heading-numbering`.

## Architecture

All scripts live in `src/`. Each is a standalone module (not a package) registered via `pyproject.toml` entry points. Documentation lives in `doc/`.

### Script relationships

- `md_to_pdf.py` and `md_to_odt.py` both import `md_repair` as a fallback: if the first conversion attempt fails, they call `md_repair.repair()` to clean the Markdown and retry once.
- `md_repair.py` is the only shared library. It exposes a `repair(path, silent, **kwargs)` public API and a `REPAIR_PIPELINE` list of step functions. Adding a new repair step means writing a `repair_<name>(text, stem, **kwargs) -> str | None` function and appending it to `REPAIR_PIPELINE`.
- `pdf_to_md.py` and `odt_to_md.py` have no repair fallback — they are one-way converters with no shared dependencies.

### Shared CLI pattern

All five scripts follow the same interface shape:
- Positional `folder` (optional, defaults to `.`) or `--file FILE` for single-file mode
- `--all` to skip the interactive menu
- `--silent` for fully non-interactive use (implies `--all`)
- ANSI colour helpers `_red` / `_yellow` with a Windows ANSI init guard
- A `_BANNER` string printed in interactive mode
- `main()` as the entry point

### Path conventions

When adding or updating a script, keep three things in sync:
1. The script in `src/`
2. Its doc page in `doc/`
3. The entry in `README.md` (scripts table, Requirements, Quick Start)
