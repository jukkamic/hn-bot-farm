"""Markdown to HTML converter with Sakura CSS styling."""

import html
import re
import sys
from pathlib import Path

import markdown2

# --- Module-level Configuration ---
SAKURA_CDN = "https://cdn.jsdelivr.net/npm/sakura.css/css/sakura.css"
MAX_INPUT_SIZE = 10 * 1024 * 1024  # 10MB limit

# Explicit extras for better performance and correct fenced code block handling
MARKDOWN_EXTRAS = [
    "fenced-code-blocks",
    "tables",
    "code-friendly",
    "cuddled-lists",
]

# Patterns for XSS sanitization
_DANGEROUS_TAG_PATTERN = re.compile(
    r'<(script|style|iframe|object|embed|form|input|button|textarea|select|meta|link|base|svg|animate)[^>]*>.*?</\1>',
    re.IGNORECASE | re.DOTALL
)
_DANGEROUS_TAG_OPEN_PATTERN = re.compile(
    r'<(script|style|iframe|object|embed|form|input|button|textarea|select|meta|link|base|svg|animate)[^>]*>',
    re.IGNORECASE
)
_JS_URL_PATTERN = re.compile(
    r'(href|src|action)\s*=\s*["\']?\s*javascript:',
    re.IGNORECASE
)
# Match event handlers with or without quotes: onclick="x" or onclick=x
_EVENT_HANDLER_PATTERN = re.compile(
    r'\s+on\w+\s*=\s*(["\'][^"\']*["\']|[^\s>]+)',
    re.IGNORECASE
)

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


def _validate_css_url(css_cdn: str) -> str:
    """Validate CSS URL to prevent injection attacks.

    Args:
        css_cdn: URL to validate

    Returns:
        Validated URL or default SAKURA_CDN if invalid
    """
    # Only allow https:// or absolute paths (not protocol-relative //)
    if css_cdn.startswith("https://"):
        return css_cdn
    if css_cdn.startswith("/") and not css_cdn.startswith("//"):
        return css_cdn
    return SAKURA_CDN


def _sanitize_html(html_content: str) -> str:
    """Sanitize HTML content to prevent XSS attacks.

    Removes dangerous tags and event handlers while preserving
    safe markdown-generated HTML.

    Args:
        html_content: HTML content to sanitize

    Returns:
        Sanitized HTML content
    """
    # Remove dangerous tag pairs (script, style, etc.)
    html_content = _DANGEROUS_TAG_PATTERN.sub('', html_content)
    # Remove any remaining dangerous opening tags
    html_content = _DANGEROUS_TAG_OPEN_PATTERN.sub('', html_content)
    # Remove javascript: URLs
    html_content = _JS_URL_PATTERN.sub(
        lambda m: m.group(0).replace('javascript:', '#blocked:'),
        html_content
    )
    # Remove event handlers (onclick, onload, etc.)
    html_content = _EVENT_HANDLER_PATTERN.sub('', html_content)
    return html_content


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
        ValueError: If markdown_text is empty, None, or exceeds size limit

    Example:
        >>> html = convert_markdown_to_html("# Hello", title="Greeting")
        >>> "<h1>Hello</h1>" in html
        True
    """
    # Validate input
    if markdown_text is None:
        raise ValueError("markdown_text is required (received None)")
    if not markdown_text.strip():
        raise ValueError("markdown_text cannot be empty or whitespace-only")
    if len(markdown_text) > MAX_INPUT_SIZE:
        raise ValueError(
            f"Input exceeds maximum size of {MAX_INPUT_SIZE:,} bytes"
        )

    # Convert markdown to HTML
    html_content = markdown2.markdown(
        markdown_text,
        extras=MARKDOWN_EXTRAS,
    )

    # Sanitize to prevent XSS
    html_content = _sanitize_html(html_content)

    # Wrap in HTML template with escaped title and validated CSS URL
    return HTML_TEMPLATE.format(
        css_cdn=_validate_css_url(css_cdn),
        title=html.escape(title),
        content=html_content
    )


def convert_file(
    input_path: str | Path,
    output_path: str | Path | None = None,
    title: str | None = None
) -> Path:
    """Convert a Markdown file to HTML.

    Args:
        input_path: Path to input .md file
        output_path: Path to output .html file (default: same name with .html)
        title: Document title (default: derived from filename)

    Returns:
        Path to generated HTML file

    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If input is a symlink or file exceeds size limit
    """
    input_file = Path(input_path)

    # Security: reject symlinks to prevent LFI (check BEFORE resolve)
    if input_file.is_symlink():
        raise ValueError("Symlinks are not allowed for security reasons")

    # Resolve to absolute path after symlink check
    input_file = input_file.resolve()

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Check file size before reading
    file_size = input_file.stat().st_size
    if file_size > MAX_INPUT_SIZE:
        raise ValueError(
            f"File exceeds maximum size of {MAX_INPUT_SIZE:,} bytes"
        )

    # Read markdown with encoding error handling
    try:
        markdown_text = input_file.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        raise ValueError(f"File encoding error in {input_path}: {e}") from e

    # Determine output path and title
    if output_path is None:
        output_file = input_file.with_suffix(".html")
    else:
        output_file = Path(output_path)

    if title is None:
        # Improved title derivation: handle multiple separators
        title = re.sub(r"[-_]+", " ", input_file.stem).title()

    # Convert and write
    html_output = convert_markdown_to_html(markdown_text, title=title)
    output_file.write_text(html_output, encoding="utf-8")

    # Verify write succeeded
    if not output_file.exists():
        raise IOError(f"Failed to write output file: {output_file}")

    return output_file


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python md_converter.py <input.md> [output.html]")
        sys.exit(2)  # Exit code 2 for usage errors

    try:
        output = convert_file(
            sys.argv[1],
            sys.argv[2] if len(sys.argv) > 2 else None
        )
        print(f"Generated: {output}")
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
