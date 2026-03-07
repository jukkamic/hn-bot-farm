"""Markdown to HTML converter with Sakura CSS styling."""

import markdown2

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
