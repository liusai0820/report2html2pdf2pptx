---
description: Transform a folder of HTML pages into a single merged PDF presentation using Playwright (High Fidelity).
---

# HTML to PDF Presentation Workflow

This workflow converts a directory of HTML slide pages (`page-*.html`) into a single, high-quality PDF presentation. It uses Playwright to ensure the output matches the browser rendering 100% (High Fidelity).

## Prerequisites

Ensure the following Python libraries are installed:

```bash
pip install playwright PyPDF2 rich
playwright install chromium
```

## Usage

Run the `html_to_pdf_agent.py` script located in the `scripts` directory.

### Basic Command

```bash
python scripts/html_to_pdf_agent.py <INPUT_DIRECTORY>
```

- `<INPUT_DIRECTORY>`: The full path to the folder containing your `page-01.html`, `page-02.html`, etc.

### Options

- **Output Filename**: Use `-o filename.pdf` to specify the output name.
- **Text Fix**: Use `--fix-text` to automatically replace "智库解读" with "解读" (legacy tailored feature).

### Examples

**1. Convert a report:**

```bash
python scripts/html_to_pdf_agent.py output/Report_20251230/pages
```

_Result will be saved to `output/Report_20251230/merged_presentation.pdf`_

**2. Convert and fix text:**

```bash
python scripts/html_to_pdf_agent.py output/Report_20251230/pages --fix-text
```

## Troubleshooting

- **Missing Playwright**: If the script complains about missing browsers, run `playwright install chromium`.
- **Permission Denied**: On macOS/Linux, you might need to use `sudo` if writing to protected directories, but usually not required for user home folders.
