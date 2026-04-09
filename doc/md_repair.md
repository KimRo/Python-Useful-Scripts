# md_repair.py

Clean and repair Markdown files. Can be used as a standalone script or imported by other tools (e.g. `md_to_pdf.py`, `md_to_odt.py`).

## Usage

```bash
# Interactive repair (prompts for decisions)
md-repair file.md

# Non-interactive — skip files with problems
md-repair file.md --silent

# Insert an H1 heading from the filename if one is missing
md-repair file.md --fix-headings insert

# Renumber headings hierarchically (1., 1.1, 1.1.1, …)
md-repair file.md --renumber

# Overwrite the source file with the repaired content
md-repair file.md --inplace
```

## Options

| Flag | Description |
|------|-------------|
| `file` | Markdown file to repair |
| `--silent` | Non-interactive: applies defaults for all decisions without prompting |
| `--fix-headings shift\|insert\|skip` | How to handle files whose first heading is not H1 |
| `--renumber` / `--no-renumber` | Renumber headings hierarchically |
| `--inplace` | Overwrite the source file with the repaired content |

### `--fix-headings` values

| Value | Behaviour |
|-------|-----------|
| `shift` | Promote all headings so the first one becomes H1 |
| `insert` | Prepend `# <filename>` as a new H1 at the top |
| `skip` | Leave the file unchanged and skip it |

## Repair Pipeline

Repairs are applied in this order:

1. **Unicode sanitisation** — replaces typographic characters (em dashes, smart quotes, ellipsis, non-breaking spaces) with plain ASCII equivalents that PDF/ODT converters reliably handle.
2. **Heading structure** — ensures the document starts with an H1 heading.
3. **Heading renumbering** — optionally adds hierarchical numbers to headings (1., 1.1, 1.1.1, …).

## Silent-Mode Defaults

When `--silent` is active and no explicit flag overrides a setting, these defaults apply:

| Setting | Default |
|---------|---------|
| `--fix-headings` | `shift` |
| `--renumber` | `True` |
| `--inplace` | `False` |

## Extending

To add a new repair step:

1. Write a function with this signature:
   ```python
   def repair_<name>(text: str, stem: str, **kwargs) -> str | None:
       ...
   ```
   Return the (possibly modified) text, or `None` to skip the file entirely.

2. Append it to `REPAIR_PIPELINE` near the bottom of the script.

## Using as a Library

```python
from pathlib import Path
from md_repair import repair

result = repair(Path("report.md"), silent=True, fix_headings="shift", renumber=True)
if result is not None:
    Path("report_fixed.md").write_text(result, encoding="utf-8")
```
