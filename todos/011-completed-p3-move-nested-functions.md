---
status: completed
priority: p3
issue_id: 011
tags: [code-review, maintainability, organization]
dependencies: []
---

# Move Nested Functions to Module Level

## Problem Statement

The `strip_html()` function is defined inside `FetchHNCommentsTool._run()`, meaning it's recreated on every tool invocation. Similar issue with nested `fetch_json()` functions.

## Findings

- **Location**: `/workspaces/hn-bot-farm/hn_farm.py:102-119`
- **Severity**: LOW - Code organization and minor performance
- **Identified by**: kieran-python-reviewer, code-simplicity-reviewer

### Current Code:
```python
def _run(self, story_id: int, comment_ids: list[int] = []) -> str:
    import html
    import re

    def fetch_json(url):  # Nested
        ...

    def strip_html(text: str) -> str:  # Nested
        ...
```

### Issues:
1. Functions recreated on every invocation
2. Imports inside method body
3. Harder to test in isolation

## Proposed Solutions

### Solution 1: Move All to Module Level (Recommended)
**Pros**: Better organization, single definition, easier testing
**Cons**: Minor refactoring
**Effort**: Small
**Risk**: Low

```python
# At top of file with other imports
import html
import re

# Module-level functions
HTML_TAG_PATTERN = re.compile(r'<[^>]+>')
WHITESPACE_PATTERN = re.compile(r'\s+')

def fetch_hn_json(url: str, timeout: int = 10) -> dict:
    ...

def strip_html(text: str) -> str:
    ...
```

## Technical Details

- **Affected Files**: `hn_farm.py`
- **Lines**: 102-119

## Acceptance Criteria

- [ ] strip_html moved to module level
- [ ] fetch_json consolidated and moved to module level
- [ ] Imports at top of file
- [ ] No behavior changes

## Work Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-03-07 | Issue identified | Found by 2 review agents |

## Resources

- Python code organization best practices
