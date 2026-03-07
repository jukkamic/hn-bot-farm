---
status: completed
priority: p2
issue_id: 004
tags: [code-review, maintainability, dry]
dependencies: []
---

# Duplicated fetch_json Function

## Problem Statement

The `fetch_json()` function is duplicated between `FetchHNStoriesTool` and `FetchHNCommentsTool`. The functions are nearly identical, differing only in timeout parameter. This violates DRY and creates maintenance burden.

## Findings

- **Location**: `/workspaces/hn-bot-farm/hn_farm.py:53-55` and `105-107`
- **Severity**: MEDIUM - Maintainability issue
- **Identified by**: kieran-python-reviewer, code-simplicity-reviewer

### Current Code (FetchHNStoriesTool):
```python
def fetch_json(url):
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read().decode('utf-8'))
```

### Current Code (FetchHNCommentsTool):
```python
def fetch_json(url):
    with urllib.request.urlopen(url, timeout=10) as response:
        return json.loads(response.read().decode('utf-8'))
```

## Proposed Solutions

### Solution 1: Module-Level Utility Function (Recommended)
**Pros**: Single source of truth, consistent timeout handling
**Cons**: Refactoring required
**Effort**: Small
**Risk**: Low

```python
# Module-level utility
def fetch_hn_json(url: str, timeout: int = 10) -> dict:
    """Fetch JSON from HN API with proper error handling."""
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return json.loads(response.read().decode('utf-8'))
```

### Solution 2: Shared Base Class
**Pros**: OOP pattern, extensible
**Cons**: Over-engineering for 2 tools
**Effort**: Medium
**Risk**: Medium

## Technical Details

- **Affected Files**: `hn_farm.py`
- **Lines**: 53-55, 105-107

## Acceptance Criteria

- [ ] Single fetch_json function at module level
- [ ] Both tools use the shared function
- [ ] Timeout is configurable via parameter
- [ ] No behavior changes

## Work Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-03-07 | Issue identified | Found by 2 review agents |

## Resources

- DRY principle documentation
