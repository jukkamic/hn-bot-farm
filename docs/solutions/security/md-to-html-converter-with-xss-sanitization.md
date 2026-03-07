---
title: "Markdown to HTML Converter with XSS Sanitization"
type: security
date: 2026-03-07
tags:
  - markdown
  - html-converter
  - xss-prevention
  - input-validation
  - lfi-prevention
  - sanitization
  - markdown2
  - sakura-css
related:
  - docs/solutions/feature-development/sentiment-analyst-agent-optimization.md
---

# Markdown to HTML Converter with XSS Sanitization

## Problem Statement

The hn-bot-farm project generates Markdown newsletters (`output/hn_daily.md`). A converter utility was needed to transform these into styled HTML for:
- Visual preview in browsers
- Email-ready HTML output
- Styled publication rendering

The original implementation had critical security vulnerabilities that could allow arbitrary JavaScript execution.

## Symptoms

### Security Issues Found in Code Review
1. **XSS via Raw HTML**: `<script>` tags passed through unmodified
2. **XSS via JavaScript Protocol**: Links with `javascript:` URLs were clickable
3. **XSS via Template Injection**: Title parameter not HTML-escaped
4. **XSS via CSS CDN Injection**: Accepted `javascript:` URLs for CSS
5. **XSS via Unquoted Event Handlers**: `onclick=alert(1)` not caught by regex
6. **XSS via SVG Animate**: `<svg><animate>` tags not in dangerous list
7. **DoS Risk**: No input size limits - 100MB file could exhaust memory
8. **LFI via Symlinks**: Could read `/etc/passwd` via symlink

### Functional Issue
- Fenced code blocks rendered incorrectly using `extras=["all"]`

## Root Cause Analysis

### Issue 1: XSS Vulnerabilities

**Cause**: `markdown2.markdown()` was called with `extras=["all"]` but without any sanitization. Raw HTML passed through unmodified.

**Vectors**:
- Script tags: `<script>alert(1)</script>`
- JS protocol: `[Click](javascript:alert(1))`
- Event handlers: `<img onerror=alert(1)>`
- Template injection: `title='</title><script>...'`

### Issue 2: DoS Risk

**Cause**: No size validation on input strings or files.

**Impact**: 10MB file creates ~30MB peak memory (3 copies: input, converted HTML, final document)

### Issue 3: LFI via Symlinks

**Cause**: `Path.resolve()` follows symlinks before `is_symlink()` check.

### Issue 4: Fenced Code Blocks

**Cause**: `extras=["all"]` doesn't properly enable fenced code blocks. The extra must be explicit.

## Solution

### Working Implementation

**File**: `/workspaces/hn-bot-farm/utils/md_converter.py`

```python
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

# Patterns for XSS sanitization (pre-compiled for performance)
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
_EVENT_HANDLER_PATTERN = re.compile(
    r'\s+on\w+\s*=\s*(["\'][^"\']*["\']|[^\s>]+)',
    re.IGNORECASE
)


def _validate_css_url(css_cdn: str) -> str:
    """Validate CSS URL - only https:// or absolute paths (not protocol-relative //)."""
    if css_cdn.startswith("https://"):
        return css_cdn
    if css_cdn.startswith("/") and not css_cdn.startswith("//"):
        return css_cdn
    return SAKURA_CDN


def _sanitize_html(html_content: str) -> str:
    """Sanitize HTML to prevent XSS attacks."""
    html_content = _DANGEROUS_TAG_PATTERN.sub('', html_content)
    html_content = _DANGEROUS_TAG_OPEN_PATTERN.sub('', html_content)
    html_content = _JS_URL_PATTERN.sub(
        lambda m: m.group(0).replace('javascript:', '#blocked:'),
        html_content
    )
    html_content = _EVENT_HANDLER_PATTERN.sub('', html_content)
    return html_content


def convert_markdown_to_html(
    markdown_text: str,
    title: str = "Document",
    css_cdn: str = SAKURA_CDN
) -> str:
    """Convert Markdown text to styled HTML."""
    # Validate input
    if markdown_text is None:
        raise ValueError("markdown_text is required (received None)")
    if not markdown_text.strip():
        raise ValueError("markdown_text cannot be empty or whitespace-only")
    if len(markdown_text) > MAX_INPUT_SIZE:
        raise ValueError(f"Input exceeds maximum size of {MAX_INPUT_SIZE:,} bytes")

    # Convert markdown to HTML
    html_content = markdown2.markdown(markdown_text, extras=MARKDOWN_EXTRAS)

    # Sanitize to prevent XSS
    html_content = _sanitize_html(html_content)

    # Wrap in template with escaped title and validated CSS URL
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
    """Convert a Markdown file to HTML."""
    input_file = Path(input_path)

    # Security: reject symlinks BEFORE resolve()
    if input_file.is_symlink():
        raise ValueError("Symlinks are not allowed for security reasons")

    input_file = input_file.resolve()

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Check file size before reading
    file_size = input_file.stat().st_size
    if file_size > MAX_INPUT_SIZE:
        raise ValueError(f"File exceeds maximum size of {MAX_INPUT_SIZE:,} bytes")

    # ... rest of implementation
```

### Key Implementation Decisions

| Decision | Rationale |
|----------|-----------|
| Custom sanitization over bleach/nh3 | Zero new dependencies; adequate for newsletter use case |
| Explicit extras list over `"all"` | Better performance; controlled feature set |
| Reject symlinks before resolve() | Security-first; prevents LFI attacks |
| 10MB size limit | Balances practical use with memory protection |
| Pre-compiled regex patterns | Performance optimization following repo patterns |
| Path return type from `convert_file()` | Modern Python; consistent with pathlib usage |
| Validate CSS URL to https:// only | Prevents protocol-relative (//) and data: URI injection |

## Prevention Strategies

### Defense in Depth
1. **Input Validation Layer**: Null checks, empty checks, size limits, symlink rejection
2. **Output Sanitization Layer**: Regex-based removal of dangerous content
3. **Template Layer**: HTML escaping for title, URL validation for CSS

### Security Checklist for Future Modifications

- [ ] Any new input parameters must be validated
- [ ] Any new HTML output must pass through `_sanitize_html()`
- [ ] Any new URL parameters must use `_validate_css_url()` pattern
- [ ] File operations must check for symlinks
- [ ] Test all new XSS vectors in `test_xss_edge_cases()`

## Test Coverage

**File**: `/workspaces/hn-bot-farm/utils/test_converter.py`

```python
def test_xss_prevention():
    # Script tag injection
    html = convert_markdown_to_html('<script>alert(1)</script>')
    assert "<script>" not in html

    # JavaScript protocol
    html = convert_markdown_to_html('[Click](javascript:alert(1))')
    assert "javascript:alert" not in html or "#blocked:" in html

    # Title injection
    html = convert_markdown_to_html('# Test', title='</title><script>alert(1)</script>')
    assert "<script>" not in html
    assert "&lt;/title&gt;" in html

def test_xss_edge_cases():
    # Unquoted event handlers
    html = convert_markdown_to_html('<img src=x onerror=alert(1)>')
    assert "onerror" not in html

    # SVG animate XSS
    html = convert_markdown_to_html('<svg><animate onbegin=alert(1)>')
    assert "<svg>" not in html
    assert "<animate>" not in html

    # Protocol-relative URLs blocked
    html = convert_markdown_to_html('# Test', css_cdn='//evil.com/style.css')
    assert "//evil.com" not in html

    # data: URIs blocked
    html = convert_markdown_to_html('# Test', css_cdn='data:text/css,body{background:red}')
    assert "data:" not in html
```

All 9 tests pass: `python -m utils.test_converter`

## Known Limitations

1. **Regex-based sanitization**: More sophisticated attacks (HTML entity obfuscation, Unicode normalization) may bypass regex filters
2. **HTML passthrough blocked**: Current configuration prevents any raw HTML in markdown - users cannot embed valid HTML
3. **No CSP headers**: The generated HTML doesn't include Content-Security-Policy meta tags

## Future Improvements

1. **Migrate to `bleach` or `nh3`**: Industry-standard HTML sanitization libraries with better coverage
2. **Add CSP headers**: Include Content-Security-Policy meta tag in generated HTML
3. **Audit logging**: Log sanitization events for security monitoring
4. **Rate limiting**: Add rate limiting for conversion operations in production

## Sources & References

### Internal References
- Python patterns: `hn_farm.py:1-379` (pre-compiled regex, type hints, docstrings)
- Error handling: `hn_farm.py:42-52` (specific exception handling)
- Configuration constants: `hn_farm.py:18-22` (module-level ALL_CAPS)

### External References
- markdown2 documentation: https://github.com/trentm/python-markdown2
- markdown2 extras: https://github.com/trentm/python-markdown2#extras
- Sakura CSS: https://oxal.org/projects/sakura/
- OWASP XSS Prevention: https://owasp.org/www-community/xss-filter-evasion-cheatsheet

### Related Documentation
- [Sentiment Analyst Agent Optimization](/workspaces/hn-bot-farm/docs/solutions/feature-development/sentiment-analyst-agent-optimization.md) - Python patterns used in this project
