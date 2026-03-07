---
status: pending
priority: p2
issue_id: 006
tags: [code-review, security, validation]
dependencies: []
---

# Missing Input Validation

## Problem Statement

The `FetchHNCommentsInput` model lacks proper validation on `story_id` and `comment_ids` parameters. Negative IDs, excessively large values, and other invalid inputs are not rejected.

## Findings

- **Location**: `/workspaces/hn-bot-farm/hn_farm.py:82-88`
- **Severity**: MEDIUM - Security and reliability risk
- **Identified by**: security-sentinel

### Current Code:
```python
class FetchHNCommentsInput(BaseModel):
    """Input schema for fetch_hn_comments."""
    story_id: int = Field(description="The HN story ID")
    comment_ids: list[int] = Field(
        default=[],
        description="List of comment IDs to fetch (will fetch up to 5)"
    )
```

### Issues:
1. No validation that IDs are positive integers
2. No limit on number of comment_ids in input
3. No upper bound on ID values (could cause issues)

## Proposed Solutions

### Solution 1: Add Pydantic Validators (Recommended)
**Pros**: Type-safe, early validation, clear error messages
**Cons**: More code
**Effort**: Small
**Risk**: Low

```python
from pydantic import field_validator

class FetchHNCommentsInput(BaseModel):
    """Input schema for fetch_hn_comments."""
    story_id: int = Field(description="The HN story ID", gt=0)
    comment_ids: list[int] = Field(
        default=[],
        description="List of comment IDs to fetch (will fetch up to 5)",
        max_length=10
    )

    @field_validator('comment_ids')
    @classmethod
    def validate_comment_ids(cls, v):
        for cid in v:
            if cid <= 0:
                raise ValueError(f'Comment ID must be positive, got {cid}')
            if cid > 10**10:
                raise ValueError(f'Comment ID suspiciously large: {cid}')
        return v
```

### Solution 2: Runtime Validation in _run()
**Pros**: More flexible error messages
**Cons**: Validation happens late, less Pythonic
**Effort**: Small
**Risk**: Medium

## Technical Details

- **Affected Files**: `hn_farm.py`
- **Lines**: 82-88

## Acceptance Criteria

- [ ] story_id must be positive integer
- [ ] comment_ids limited to reasonable count
- [ ] Invalid inputs raise clear validation errors
- [ ] Test cases for boundary conditions

## Work Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-03-07 | Issue identified | Found by security-sentinel |

## Resources

- Pydantic validation documentation
