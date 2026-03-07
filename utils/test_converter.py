"""Test script for md_converter module."""

from pathlib import Path
from md_converter import convert_markdown_to_html

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
