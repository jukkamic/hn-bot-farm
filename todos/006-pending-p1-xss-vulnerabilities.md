---
status: complete
priority: p1
issue_id: 006
tags: [security, xss, code-review]
dependencies: []
---

# XSS Vulnerabilities in Markdown-to-HTML Converter

## Problem Statement

The converter has multiple Cross-Site Scripting (XSS) vulnerabilities that allow attackers to execute arbitrary JavaScript in users' browsers. This is a critical security issue that could lead to cookie theft, session hijacking, and complete application compromise.

## Findings

### 1. Raw HTML Injection
**Location:** `utils/md_converter.py:43`

```python
html_content = markdown2.markdown(markdown_text, extras=["all"])
```

Markdown2 passes raw HTML through by default. Malicious input like `<script>alert(1)</script>` is rendered as-is.

### 2. JavaScript Protocol in Links
**Location:** `utils/md_converter.py:43`

Markdown links with `javascript:` protocol are converted to clickable links without sanitization:
```python
'[Click](javascript:alert(1))' → '<a href="javascript:alert(1)">Click</a>'
```

### 3. Template Injection via Title
**Location:** `utils/md_converter.py:46-49`

The `title` parameter is inserted into HTML without escaping:
```python
title='</title><script>alert(1)</script>' → XSS
```

### 4. CSS CDN Injection
**Location:** `utils/md_converter.py:6,46`

The `css_cdn` parameter accepts `javascript:` URLs:
```python
css_cdn='javascript:alert(1)' → XSS
```

## Proposed Solutions

### Option A: Enable markdown2 safe_mode + HTML escaping (Recommended)

**Pros:**
- Uses built-in markdown2 features
- Minimal code changes
- Standard library only

**Cons:**
- safe_mode is deprecated in some markdown libraries
- May not catch all edge cases

**Effort:** Small
**Risk:** Low

```python
import html

# Line 43 - enable safe mode
html_content = markdown2.markdown(
    markdown_text,
    extras=["fenced-code-blocks", "tables"],
    safe_mode='escape'
)

# Lines 46-49 - escape title and validate css_cdn
return HTML_TEMPLATE.format(
    css_cdn=css_cdn if css_cdn.startswith('https://') else SAKURA_CDN,
    title=html.escape(title),
    content=html_content
)
```

### Option B: Add bleach/nh3 sanitization layer

**Pros:**
- More comprehensive protection
- Industry-standard approach

**Cons:**
- Adds new dependency
- More code changes

**Effort:** Medium
**Risk:** Low

### Option C: Allowlist approach

**Pros:**
- Most secure - only known-safe HTML allowed
- Complete control over output

**Cons:**
- May break legitimate markdown features
- More complex to implement

**Effort:** Large
**Risk:** Medium

## Recommended Action

Implement Option A immediately - it provides protection with minimal changes.

## Technical Details

**Affected Files:**
- `utils/md_converter.py` (lines 43, 46-49)

**Components:**
- `convert_markdown_to_html()` function
- `HTML_TEMPLATE` constant

## Acceptance Criteria

- [ ] `markdown2.markdown()` called with `safe_mode='escape'`
- [ ] Title parameter HTML-escaped with `html.escape()`
- [ ] CSS CDN validated to start with `https://` or use default
- [ ] Test cases added for XSS vectors
- [ ] No `<script>` tags in output from malicious input
- [ ] No `javascript:` protocol in links

## Work Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-03-07 | Finding identified | Security review by security-sentinel agent |

## Resources

- markdown2 safe_mode docs: https://github.com/trentm/python-markdown2#safe-mode
- OWASP XSS Prevention: https://owasp.org/www-community/xss-filter-evasion-cheatsheet
