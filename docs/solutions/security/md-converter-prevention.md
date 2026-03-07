---
title: Markdown-to-HTML Converter - Prevention Strategies
type: security
date: 2026-03-07
related_plan: 2026-03-07-feat-md-to-html-converter-plan.md
---

# Prevention Strategies for Markdown-to-HTML Converter

This document outlines prevention strategies, best practices, and test cases that should be maintained for the `utils/md_converter.py` module to ensure ongoing security.

## Overview

The Markdown-to-HTML converter handles untrusted input and produces HTML output, making it a potential vector for Cross-Site Scripting (XSS) and other injection attacks. This document codifies the security measures implemented and provides guidance for future maintenance.

---

## 1. Prevention Strategies

### 1.1 Input Validation

**Strategy:** Validate all inputs before processing to prevent resource exhaustion and injection attacks.

| Check | Implementation | Rationale |
|-------|---------------|-----------|
| Null check | `if markdown_text is None: raise ValueError` | Prevents NoneType errors |
| Empty check | `if not markdown_text.strip(): raise ValueError` | Prevents empty document generation |
| Size limit | `MAX_INPUT_SIZE = 10 * 1024 * 1024` (10MB) | Prevents DoS via large inputs |
| Symlink rejection | `if input_file.is_symlink(): raise ValueError` | Prevents Local File Inclusion (LFI) |

**Code Reference:** `/workspaces/hn-bot-farm/utils/md_converter.py:121-129`, `:170-171`

### 1.2 Output Sanitization

**Strategy:** Sanitize HTML output to remove potentially dangerous elements.

The `_sanitize_html()` function removes:

- **Dangerous tags:** `<script>`, `<style>`, `<iframe>`, `<object>`, `<embed>`, `<form>`, `<input>`, `<button>`, `<textarea>`, `<select>`, `<meta>`, `<link>`, `<base>`, `<svg>`, `<animate>`
- **Event handlers:** All `on*` attributes (onclick, onerror, onload, etc.)
- **JavaScript URLs:** `javascript:` protocol in href/src/action attributes

**Code Reference:** `/workspaces/hn-bot-farm/utils/md_converter.py:72-95`

### 1.3 Template Injection Prevention

**Strategy:** Escape all user-controlled values before inserting into HTML template.

| Value | Escaping Method |
|-------|-----------------|
| Title | `html.escape(title)` |
| CSS URL | `_validate_css_url()` - allows only `https://` or absolute paths starting with `/` |
| Content | `_sanitize_html()` after markdown conversion |

**Code Reference:** `/workspaces/hn-bot-farm/utils/md_converter.py:55-69`, `:141-144`

### 1.4 Markdown Library Configuration

**Strategy:** Use explicit extras list instead of `"all"` to control what HTML is generated.

```python
MARKDOWN_EXTRAS = [
    "fenced-code-blocks",
    "tables",
    "code-friendly",
    "cuddled-lists",
]
```

This prevents unexpected HTML generation from unknown extras.

**Code Reference:** `/workspaces/hn-bot-farm/utils/md_converter.py:15-20`

---

## 2. Best Practices

### 2.1 Defense in Depth

Apply multiple layers of security:

1. **Input validation** (size, type, existence)
2. **Library configuration** (explicit extras)
3. **Output sanitization** (remove dangerous elements)
4. **Template escaping** (escape dynamic values)

### 2.2 Fail Securely

When validation fails, use safe defaults:

```python
def _validate_css_url(css_cdn: str) -> str:
    if css_cdn.startswith("https://"):
        return css_cdn
    if css_cdn.startswith("/") and not css_cdn.startswith("//"):
        return css_cdn
    return SAKURA_CDN  # Safe default instead of error
```

### 2.3 Allowlist Over Blocklist

Where possible, define what is allowed rather than what is blocked:

- CSS URL validation uses allowlist: `https://` or safe absolute paths
- Markdown extras are explicitly listed, not `"all"`

### 2.4 Pre-compiled Regex Patterns

Compile regex patterns at module load for performance and consistency:

```python
_DANGEROUS_TAG_PATTERN = re.compile(
    r'<(script|style|iframe|...)[^>]*>.*?</\1>',
    re.IGNORECASE | re.DOTALL
)
```

### 2.5 Clear Error Messages

Provide actionable error messages without exposing internals:

```python
raise ValueError(f"Input exceeds maximum size of {MAX_INPUT_SIZE:,} bytes")
raise ValueError("Symlinks are not allowed for security reasons")
```

---

## 3. Test Cases to Maintain

The following test cases in `/workspaces/hn-bot-farm/utils/test_converter.py` must be maintained:

### 3.1 Core Functionality Tests

| Test Function | Purpose |
|---------------|---------|
| `test_conversion()` | Verifies basic markdown to HTML conversion |
| `test_fenced_code_blocks()` | Ensures code blocks render as `<pre><code>` |
| `test_convert_file()` | Tests file-based conversion workflow |
| `test_file_not_found()` | Verifies proper error for missing files |

### 3.2 Security Tests - Primary XSS Prevention

| Test Function | Attack Vector | Expected Behavior |
|---------------|---------------|-------------------|
| `test_xss_prevention()` | Raw `<script>` injection | Script tags removed |
| `test_xss_prevention()` | `javascript:` protocol in links | Blocked/replaced with `#blocked:` |
| `test_xss_prevention()` | Title injection via `</title>` | HTML-escaped in output |
| `test_xss_prevention()` | CSS CDN `javascript:` injection | Falls back to default Sakura CSS |

### 3.3 Security Tests - Edge Cases

| Test Function | Attack Vector | Expected Behavior |
|---------------|---------------|-------------------|
| `test_xss_edge_cases()` | Unquoted `onerror=alert(1)` | Event handler removed |
| `test_xss_edge_cases()` | `<svg><animate onbegin=...>` | SVG and animate tags removed |
| `test_xss_edge_cases()` | Protocol-relative `//evil.com/...` | Falls back to default |
| `test_xss_edge_cases()` | `data:` URI in CSS CDN | Falls back to default |

### 3.4 Input Validation Tests

| Test Function | Purpose |
|---------------|---------|
| `test_empty_input()` | Empty and whitespace-only input rejected |
| `test_size_limit()` | Input exceeding 10MB rejected |
| `test_symlink_rejection()` | Symlinked files rejected for security |

### 3.5 Running Tests

```bash
# Activate virtual environment first
source .venv/bin/activate

# Run the test suite
python utils/test_converter.py
```

Expected output:
```
Running md_converter tests...

[PASS] Basic conversion test
[PASS] Fenced code blocks test
[PASS] XSS prevention test
[PASS] XSS edge cases test
[PASS] Empty input validation test
[PASS] Size limit test
[PASS] File conversion test
[PASS] Symlink rejection test
[PASS] File not found test

All tests passed!
```

---

## 4. Security Review Checklist

When modifying `md_converter.py`, verify:

- [ ] All user inputs are validated before use
- [ ] No new HTML is generated without sanitization
- [ ] Template placeholders use proper escaping
- [ ] New configuration options follow allowlist principle
- [ ] File operations reject symlinks
- [ ] Error messages don't expose sensitive paths or data
- [ ] New test cases cover any new attack vectors
- [ ] Size limits are enforced for new input sources

---

## 5. Known Limitations

1. **HTML entities:** The sanitizer may not catch all obfuscated XSS vectors using HTML entities. Future enhancement: use a proper HTML sanitization library like `bleach`.

2. **Unicode attacks:** Certain Unicode normalization attacks may bypass filters. Consider adding Unicode normalization if processing international content.

3. **Markdown HTML passthrough:** If markdown2 is configured with `html-extra` or similar, raw HTML in markdown could bypass sanitization. The current explicit extras list prevents this.

---

## 6. Future Improvements

1. **Library migration:** Consider migrating to `bleach` or `lxml.html.clean` for more robust HTML sanitization.

2. **CSP headers:** When serving generated HTML, use Content-Security-Policy headers as additional defense.

3. **Audit logging:** Log rejected inputs for security monitoring.

4. **Rate limiting:** Add rate limiting for file conversion operations.

---

## References

- Implementation: `/workspaces/hn-bot-farm/utils/md_converter.py`
- Tests: `/workspaces/hn-bot-farm/utils/test_converter.py`
- Plan: `/workspaces/hn-bot-farm/docs/plans/2026-03-07-feat-md-to-html-converter-plan.md`
- OWASP XSS Prevention: https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
