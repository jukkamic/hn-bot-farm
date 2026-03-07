---
status: completed
priority: p3
issue_id: 010
tags: [code-review, performance, optimization]
dependencies: []
---

# Pre-compile Regex Patterns

## Problem Statement

The `strip_html()` function uses `re.sub()` with string patterns that are compiled on every call. For 25 comments, this means 50 regex compilations.

## Findings

- **Location**: `/workspaces/hn-bot-farm/hn_farm.py:109-119`
- **Severity**: LOW - Minor performance optimization
- **Identified by**: performance-oracle

### Current Code:
```python
def strip_html(text: str) -> str:
    text = re.sub(r'<[^>]+>', ' ', text)  # Compile + match
    text = html.unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()  # Compile + match
    return text
```

### Impact:
- ~50-100 microseconds per compilation
- ~2.5-5ms overhead per run (25 comments × 2 patterns)

## Proposed Solutions

### Solution 1: Module-Level Pre-compilation (Recommended)
**Pros**: Patterns compiled once, cleaner code
**Cons**: Trivial change
**Effort**: Trivial
**Risk**: None

```python
# Module-level compilation
import re
HTML_TAG_PATTERN = re.compile(r'<[^>]+>')
WHITESPACE_PATTERN = re.compile(r'\s+')

def strip_html(text: str) -> str:
    if not text:
        return ""
    text = HTML_TAG_PATTERN.sub(' ', text)
    text = html.unescape(text)
    text = WHITESPACE_PATTERN.sub(' ', text).strip()
    return text
```

## Technical Details

- **Affected Files**: `hn_farm.py`
- **Lines**: 109-119

## Acceptance Criteria

- [ ] Regex patterns compiled at module level
- [ ] Function uses pre-compiled patterns
- [ ] No behavior changes

## Work Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-03-07 | Issue identified | Found by performance-oracle |

## Resources

- Python re module documentation
