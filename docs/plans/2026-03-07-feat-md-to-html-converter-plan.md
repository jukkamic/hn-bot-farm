---
title: Implement Markdown-to-HTML Converter Utility
type: feat
status: completed
date: 2026-03-07
---

# Implement Markdown-to-HTML Converter Utility

## Overview

Create a standalone utility module that converts Markdown content to styled HTML using the `markdown2` library with all extras enabled, wrapped in a complete HTML document with Sakura CSS (classless framework) for instant visual polish.

## Problem Statement / Motivation

The hn-bot-farm project generates Markdown newsletters (`output/hn_daily.md`). A converter utility enables:
- Visual preview of generated content in browsers
- Email-ready HTML output
- Styled publication rendering

## Proposed Solution

1. Create `utils/md_converter.py` with a `convert_markdown_to_html()` function
2. Use `markdown2` library with `extras="all"` for full Markdown feature support
3. Inject Sakura CSS CDN link in HTML `<head>` for zero-config styling
4. Create `utils/test_converter.py` to validate conversion and output file existence

## Technical Considerations

### Dependencies
- **markdown2**: Not currently in requirements.txt - needs to be added
- **Sakura CSS**: CDN link only, no local dependency

### Code Patterns (from repo research)
- Module-level constants in ALL_CAPS
- Pre-compiled regex patterns if needed
- Type hints with modern Python syntax (`str | None`)
- Google-style docstrings with Args/Returns/Raises
- Standard `if __name__ == "__main__"` pattern for standalone execution

### File Structure
```
utils/
  __init__.py          # Package marker
  md_converter.py      # Main converter module
  test_converter.py    # Test script generating test_output.html
```

## Acceptance Criteria

- [x] `utils/__init__.py` exists (empty package marker)
- [x] `utils/md_converter.py` implements `convert_markdown_to_html(markdown_text: str) -> str`
- [x] Uses `markdown2.markdown()` with `extras="all"` (or equivalent extra list)
- [x] Output HTML includes complete document structure: `<!DOCTYPE html><html><head>...</head><body>...</body></html>`
- [x] Sakura CSS injected via CDN: `<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/sakura.css/css/sakura.css" />`
- [x] `markdown2` added to `requirements.txt`
- [x] `utils/test_converter.py` exists and can be executed
- [x] Running test_converter.py generates `utils/test_output.html`
- [x] `utils/test_output.html` passes FileExists check
- [x] Generated HTML contains valid Sakura CSS link and converted content

## Success Metrics

**Mission Complete when:** `utils/test_converter.py` generates a valid `utils/test_output.html` and passes a `FileExists` check.

## MVP

### utils/__init__.py

```python
# Utils package marker
```

### utils/md_converter.py

```python
"""Markdown to HTML converter with Sakura CSS styling."""

import markdown2
from typing import Any

# --- Module-level Configuration ---
SAKURA_CDN = "https://cdn.jsdelivr.net/npm/sakura.css/css/sakura.css"
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="{css_cdn}" />
    <title>{title}</title>
</head>
<body>
{content}
</body>
</html>"""

def convert_markdown_to_html(
    markdown_text: str,
    title: str = "Document",
    css_cdn: str = SAKURA_CDN
) -> str:
    """Convert Markdown text to styled HTML.

    Args:
        markdown_text: Raw Markdown content to convert
        title: HTML document title (default: "Document")
        css_cdn: URL to CSS stylesheet (default: Sakura CSS CDN)

    Returns:
        Complete HTML document string with Sakura CSS styling

    Raises:
        ValueError: If markdown_text is empty or None
    """
    if not markdown_text:
        raise ValueError("markdown_text cannot be empty")

    # Convert markdown to HTML with all extras
    html_content = markdown2.markdown(markdown_text, extras=["all"])

    # Wrap in HTML template with CSS
    return HTML_TEMPLATE.format(
        css_cdn=css_cdn,
        title=title,
        content=html_content
    )


def convert_file(
    input_path: str,
    output_path: str | None = None,
    title: str | None = None
) -> str:
    """Convert a Markdown file to HTML.

    Args:
        input_path: Path to input .md file
        output_path: Path to output .html file (default: same name with .html)
        title: Document title (default: derived from filename)

    Returns:
        Path to generated HTML file
    """
    from pathlib import Path

    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Read markdown
    markdown_text = input_file.read_text(encoding="utf-8")

    # Determine output path and title
    if output_path is None:
        output_path = str(input_file.with_suffix(".html"))
    if title is None:
        title = input_file.stem.replace("-", " ").replace("_", " ").title()

    # Convert and write
    html_output = convert_markdown_to_html(markdown_text, title=title)
    Path(output_path).write_text(html_output, encoding="utf-8")

    return output_path


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python md_converter.py <input.md> [output.html]")
        sys.exit(1)

    output = convert_file(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    print(f"Generated: {output}")
```

### utils/test_converter.py

```python
"""Test script for md_converter module."""

from pathlib import Path
from md_converter import convert_markdown_to_html, convert_file

# Test markdown content
TEST_MARKDOWN = """# Test Document

This is a **test** document with _various_ formatting.

## Features

- Bullet points
- [Links](https://example.com)
- `Code blocks`

```python
def hello():
    print("Hello, World!")
```

> A blockquote for good measure.
"""

OUTPUT_FILE = Path(__file__).parent / "test_output.html"


def test_conversion():
    """Test basic markdown to HTML conversion."""
    html = convert_markdown_to_html(TEST_MARKDOWN, title="Test Output")

    # Verify content
    assert "<!DOCTYPE html>" in html, "Missing DOCTYPE"
    assert "sakura.css" in html, "Missing Sakura CSS"
    assert "<h1>Test Document</h1>" in html, "Missing H1 header"
    assert "<strong>test</strong>" in html, "Missing bold text"
    assert "<em>various</em>" in html, "Missing italic text"

    return html


def test_file_exists():
    """Test that output file is created."""
    # Generate HTML
    html = convert_markdown_to_html(TEST_MARKDOWN, title="Test Output")

    # Write to file
    OUTPUT_FILE.write_text(html, encoding="utf-8")

    # Verify file exists
    assert OUTPUT_FILE.exists(), f"Output file not found: {OUTPUT_FILE}"
    print(f"[PASS] File exists: {OUTPUT_FILE}")

    return True


def main():
    """Run all tests."""
    print("Running md_converter tests...")

    # Test 1: Basic conversion
    html = test_conversion()
    print("[PASS] Basic conversion test")

    # Test 2: File exists check
    test_file_exists()

    print(f"\nAll tests passed! Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
```

## Dependencies & Risks

| Dependency | Status | Risk |
|------------|--------|------|
| markdown2 | Not installed | Low - simple pip install |
| Sakura CSS CDN | External | Low - widely available |

**Risk Mitigation:**
- Add markdown2 to requirements.txt before implementation
- CDN fallback: Could bundle minimal CSS if offline needed (out of scope)

## Sources & References

### Internal References
- Python patterns: `hn_farm.py:1-379` (pre-compiled regex, type hints, docstrings)
- Error handling: `hn_farm.py:42-52` (specific exception handling)
- Configuration constants: `hn_farm.py:18-22` (module-level ALL_CAPS)

### External References
- markdown2 documentation: https://github.com/trentm/python-markdown2
- markdown2 extras: https://github.com/trentm/python-markdown2#extras
- Sakura CSS: https://oxal.org/projects/sakura/
