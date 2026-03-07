---
status: complete
priority: p2
issue_id: 011
tags: [testing, code-review]
dependencies: []
---

# Test Coverage Improvements Needed

## Problem Statement

The test file has several issues: it's not a proper pytest test, lacks coverage of `convert_file()`, doesn't test error conditions, and the output file is committed to git.

## Findings

### 1. Not Proper pytest Tests
**Location:** `utils/test_converter.py:28-54`

Uses `assert` outside pytest framework - assertions work but don't report properly.

### 2. Zero Coverage of convert_file()
**Location:** `utils/md_converter.py:53-87`

The main file-based conversion function has no tests.

### 3. No Error Condition Tests
No tests for:
- `ValueError` on empty input
- `FileNotFoundError` on missing file
- Edge cases (special characters, malformed markdown)

### 4. Test Output Committed
**Location:** `utils/test_output.html`

Generated file shouldn't be in git - should use tempfile.

## Proposed Solutions

### Option A: Convert to pytest and expand coverage (Recommended)

**Pros:**
- Standard testing framework
- Proper test discovery
- Better error reporting

**Cons:**
- More boilerplate
- Need to add pytest to requirements

**Effort:** Medium
**Risk:** Low

```python
import pytest
from utils.md_converter import convert_markdown_to_html, convert_file

def test_conversion_basic():
    html = convert_markdown_to_html("# Test", title="Test")
    assert "<h1>Test</h1>" in html

def test_empty_input_raises():
    with pytest.raises(ValueError, match="cannot be empty"):
        convert_markdown_to_html("")

def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        convert_file("/nonexistent/path.md")
```

### Option B: Keep simple but add tempfile cleanup

**Pros:**
- No new dependencies
- Quick fix

**Cons:**
- Less structured
- No parametrization

**Effort:** Small
**Risk:** Low

## Recommended Action

Implement Option A - convert to pytest with proper coverage.

## Technical Details

**Affected Files:**
- `utils/test_converter.py` (rewrite)
- `.gitignore` (add test_output.html)
- `requirements.txt` (add pytest if not present)

## Acceptance Criteria

- [ ] Tests use pytest framework
- [ ] `convert_file()` has test coverage
- [ ] Error conditions tested
- [ ] Test output uses tempfile, not committed
- [ ] All tests pass with `pytest utils/`

## Work Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-03-07 | Finding identified | Code review |

## Resources

- pytest docs: https://docs.pytest.org/
