---
status: complete
priority: p2
issue_id: 010
tags: [code-quality, python, code-review]
dependencies: []
---

# Code Quality Improvements Needed

## Problem Statement

Several code quality issues were identified that don't block functionality but should be addressed for maintainability and consistency.

## Findings

### 1. Import Inside Function
**Location:** `utils/md_converter.py:68`

```python
def convert_file(...):
    from pathlib import Path  # Should be at module level
```

Violates PEP 8 - imports should be at top of file.

### 2. Inconsistent Path Handling
**Location:** `utils/md_converter.py:53-55`

Function accepts `str` but uses `Path` internally. Modern Python should accept `str | Path`.

```python
def convert_file(
    input_path: str,  # Should be str | Path
    output_path: str | None = None,  # Should be str | Path | None
) -> str:  # Should return Path
```

### 3. Missing __all__ Export
**Location:** `utils/__init__.py:1`

Empty file should export public API:

```python
from utils.md_converter import convert_markdown_to_html, convert_file
__all__ = ["convert_markdown_to_html", "convert_file"]
```

### 4. Test File Relative Import
**Location:** `utils/test_converter.py:4`

```python
from md_converter import convert_markdown_to_html  # Won't work from project root
```

Should be: `from utils.md_converter import ...`

## Proposed Solutions

### Option A: Fix all issues in one commit (Recommended)

**Pros:**
- Clean codebase
- Consistent style
- Better test discoverability

**Cons:**
- Multiple changes at once

**Effort:** Small
**Risk:** Low

## Recommended Action

Fix all issues together as a code quality pass.

## Technical Details

**Affected Files:**
- `utils/md_converter.py` (imports, type hints)
- `utils/__init__.py` (exports)
- `utils/test_converter.py` (import fix)

## Acceptance Criteria

- [ ] `pathlib.Path` import at module level
- [ ] Function signatures accept `str | Path`
- [ ] `__all__` defined in `__init__.py`
- [ ] Test import works from project root
- [ ] All tests pass after changes

## Work Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-03-07 | Finding identified | Code review by kieran-python-reviewer |

## Resources

- PEP 8 Imports: https://peps.python.org/pep-0008/#imports
