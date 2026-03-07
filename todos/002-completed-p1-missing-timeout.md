---
status: completed
priority: p1
issue_id: 002
tags: [code-review, reliability, api]
dependencies: []
---

# Missing Timeout in FetchHNStoriesTool

## Problem Statement

The `FetchHNStoriesTool.fetch_json()` function has no timeout, while `FetchHNCommentsTool.fetch_json()` has a 10-second timeout. This inconsistency can cause the entire agent pipeline to hang indefinitely on network issues.

## Findings

- **Location**: `/workspaces/hn-bot-farm/hn_farm.py:54`
- **Severity**: CRITICAL - Can cause indefinite blocking
- **Identified by**: performance-oracle, security-sentinel

### Current Code (no timeout):
```python
# In FetchHNStoriesTool (line 54)
def fetch_json(url):
    with urllib.request.urlopen(url) as response:  # NO TIMEOUT
        return json.loads(response.read().decode('utf-8'))
```

### Contrast with FetchHNCommentsTool:
```python
# In FetchHNCommentsTool (line 106)
def fetch_json(url):
    with urllib.request.urlopen(url, timeout=10) as response:  # Has timeout
```

## Proposed Solutions

### Solution 1: Add Consistent Timeout (Recommended)
**Pros**: Simple fix, consistent behavior
**Cons**: May need timeout tuning
**Effort**: Small
**Risk**: Low

```python
def fetch_json(url, timeout=10):
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return json.loads(response.read().decode('utf-8'))
```

### Solution 2: Consolidate Both Functions
**Pros**: Fixes duplication AND timeout issue
**Cons**: More changes required
**Effort**: Medium
**Risk**: Low

Extract to module-level utility with configurable timeout.

## Technical Details

- **Affected Files**: `hn_farm.py`
- **Lines**: 54

## Acceptance Criteria

- [ ] Timeout added to FetchHNStoriesTool.fetch_json()
- [ ] Both tools use consistent timeout value
- [ ] Timeout is configurable or documented

## Work Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-03-07 | Issue identified | Found by performance-oracle |

## Resources

- HN API reliability considerations
