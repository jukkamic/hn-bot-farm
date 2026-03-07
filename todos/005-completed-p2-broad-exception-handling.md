---
status: completed
priority: p2
issue_id: 005
tags: [code-review, error-handling, security]
dependencies: []
---

# Overly Broad Exception Handling

## Problem Statement

The exception handler in `FetchHNCommentsTool._run()` catches `Exception`, which is too broad. This can mask unexpected errors and make debugging difficult.

## Findings

- **Location**: `/workspaces/hn-bot-farm/hn_farm.py:144`
- **Severity**: MEDIUM - Can hide bugs
- **Identified by**: kieran-python-reviewer, security-sentinel

### Current Code:
```python
except Exception as e:
    errors.append(f"Error fetching comment {comment_id}: {str(e)}")
    continue
```

### Issues:
1. Catches ALL exceptions including KeyboardInterrupt, SystemExit
2. `str(e)` could expose sensitive information (URLs, internal details)
3. No differentiation between retryable and non-retryable errors

## Proposed Solutions

### Solution 1: Narrow to Specific Exceptions (Recommended)
**Pros**: Better error handling, clear intent
**Cons**: Need to identify all possible exceptions
**Effort**: Small
**Risk**: Low

```python
except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError) as e:
    errors.append(f"Error fetching comment {comment_id}: Network or data error")
    continue
```

### Solution 2: Sanitize Error Messages
**Pros**: Prevents information disclosure
**Cons**: Still catches too broadly
**Effort**: Small
**Risk**: Medium

```python
except Exception as e:
    logging.error(f"Failed to fetch comment {comment_id}: {e}", exc_info=True)
    errors.append(f"Error fetching comment {comment_id}: Unexpected error")
```

## Technical Details

- **Affected Files**: `hn_farm.py`
- **Lines**: 144-146

## Acceptance Criteria

- [ ] Exception handling narrowed to specific types
- [ ] Error messages sanitized (no internal details)
- [ ] Full errors logged internally for debugging

## Work Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-03-07 | Issue identified | Found by 2 review agents |

## Resources

- Python exception handling best practices
