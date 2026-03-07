"""Test script for md_converter module."""

import tempfile
from pathlib import Path

from utils.md_converter import convert_markdown_to_html, convert_file

# Test markdown content
TEST_MARKDOWN = """# Test Document

This is a **test** document with *various* formatting.

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


def test_conversion() -> None:
    """Test basic markdown to HTML conversion."""
    html = convert_markdown_to_html(TEST_MARKDOWN, title="Test Output")

    # Verify content
    assert "<!DOCTYPE html>" in html, "Missing DOCTYPE"
    assert "sakura.css" in html, "Missing Sakura CSS"
    assert "<h1>Test Document</h1>" in html, "Missing H1 header"
    assert "<strong>test</strong>" in html, "Missing bold text"
    assert "<em>various</em>" in html, "Missing italic text"

    print("[PASS] Basic conversion test")


def test_fenced_code_blocks() -> None:
    """Test that fenced code blocks render correctly as <pre><code>."""
    html = convert_markdown_to_html("```python\nprint(1)\n```")

    assert "<pre>" in html, "Fenced code blocks should render in <pre> tags"
    assert "<code" in html, "Fenced code blocks should contain <code> tags"

    print("[PASS] Fenced code blocks test")


def test_xss_prevention() -> None:
    """Test that XSS attacks are prevented."""
    # Test 1: Raw HTML script injection
    html = convert_markdown_to_html('<script>alert(1)</script>')
    assert "<script>" not in html, "Raw script tags should be removed"
    assert "alert(1)" not in html, "Script content should be removed"

    # Test 2: JavaScript protocol in links
    html = convert_markdown_to_html('[Click](javascript:alert(1))')
    # Check that javascript: is blocked (replaced with #blocked:)
    assert "javascript:alert" not in html or "#blocked:" in html, \
        "JS protocol should be blocked"

    # Test 3: Title injection
    html = convert_markdown_to_html('# Test', title='</title><script>alert(1)</script>')
    assert "<script>" not in html, "Title injection should be escaped"
    assert "&lt;/title&gt;" in html or "</title>" not in html, \
        "Title should be HTML-escaped"

    # Test 4: CSS CDN injection
    html = convert_markdown_to_html('# Test', css_cdn='javascript:alert(1)')
    assert "javascript:" not in html, "Invalid CSS URL should use default"
    assert "sakura.css" in html, "Should use default Sakura CSS"

    print("[PASS] XSS prevention test")


def test_empty_input() -> None:
    """Test that empty input raises ValueError."""
    try:
        convert_markdown_to_html("")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "empty" in str(e).lower()

    try:
        convert_markdown_to_html("   ")
        assert False, "Should have raised ValueError for whitespace"
    except ValueError as e:
        assert "empty" in str(e).lower() or "whitespace" in str(e).lower()

    print("[PASS] Empty input validation test")


def test_size_limit() -> None:
    """Test that oversized input is rejected."""
    large_input = "A" * (11 * 1024 * 1024)  # 11MB

    try:
        convert_markdown_to_html(large_input)
        assert False, "Should have raised ValueError for oversized input"
    except ValueError as e:
        assert "size" in str(e).lower() or "exceeds" in str(e).lower()

    print("[PASS] Size limit test")


def test_convert_file() -> None:
    """Test file-based conversion with tempfile."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create input file
        input_file = Path(tmpdir) / "test.md"
        input_file.write_text("# Test\n\nContent here.")

        # Convert
        output_file = convert_file(input_file)

        # Verify
        assert output_file.exists(), "Output file should exist"
        assert output_file.suffix == ".html", "Output should have .html suffix"

        content = output_file.read_text()
        assert "<h1>Test</h1>" in content, "H1 should be in output"
        assert "Test" in content, "Title should be derived from filename"

        print("[PASS] File conversion test")


def test_symlink_rejection() -> None:
    """Test that symlinks are rejected for security."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a real file and a symlink to it
        real_file = Path(tmpdir) / "real.md"
        real_file.write_text("# Real content")

        symlink = Path(tmpdir) / "link.md"
        symlink.symlink_to(real_file)

        try:
            convert_file(symlink)
            assert False, "Should have rejected symlink"
        except ValueError as e:
            assert "symlink" in str(e).lower()

        print("[PASS] Symlink rejection test")


def test_file_not_found() -> None:
    """Test that missing files raise FileNotFoundError."""
    try:
        convert_file("/nonexistent/path/to/file.md")
        assert False, "Should have raised FileNotFoundError"
    except FileNotFoundError as e:
        assert "not found" in str(e).lower()

    print("[PASS] File not found test")


def main() -> None:
    """Run all tests."""
    print("Running md_converter tests...\\n")

    test_conversion()
    test_fenced_code_blocks()
    test_xss_prevention()
    test_empty_input()
    test_size_limit()
    test_convert_file()
    test_symlink_rejection()
    test_file_not_found()

    print("\\n✅ All tests passed!")


if __name__ == "__main__":
    main()
