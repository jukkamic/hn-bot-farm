---
status: completed
priority: p1
issue_id: 001
tags: [code-review, python, bug, security]
dependencies: []
---

# Mutable Default Argument Bug

## Problem Statement

The `FetchHNCommentsTool._run()` method uses a mutable default argument `comment_ids: list[int] = []`. This is a classic Python bug where the default list is shared across all method invocations, potentially causing state leakage and unexpected behavior.

## Findings

- **Location**: `/workspaces/hn-bot-farm/hn_farm.py:100`
- **Severity**: CRITICAL - Can cause bugs in production
- **Identified by**: kieran-python-reviewer, security-sentinel, code-simplicity-reviewer, agent-native-reviewer

### Current Code:
```python
def _run(self, story_id: int, comment_ids: list[int] = []) -> str:
```

### Issue:
The default empty list is created once at function definition time and shared across all calls. If the function modifies the list, subsequent calls will see those modifications.

## Proposed Solutions

### Solution 1: Use None with Conversion (Recommended)
**Pros**: Standard Python idiom, handles None correctly
**Cons**: Slightly more verbose
**Effort**: Small
**Risk**: Low

```python
def _run(self, story_id: int, comment_ids: list[int] | None = None) -> str:
    if comment_ids is None:
        comment_ids = []
```

### Solution 2: Use Pydantic Default Factory
**Pros**: Consistent with Pydantic patterns
**Cons**: Requires restructuring, may not work with BaseTool
**Effort**: Medium
**Risk**: Medium

## Technical Details

- **Affected Files**: `hn_farm.py`
- **Lines**: 100

## Acceptance Criteria

- [ ] Mutable default argument replaced with None
- [ ] Unit test verifies isolation between calls
- [ ] No state leakage between invocations

## Work Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-03-07 | Issue identified | Found by 4 review agents |

## Resources

- Python docs: https://docs.python-guide.org/writing/gotchas/#mutable-default-arguments
