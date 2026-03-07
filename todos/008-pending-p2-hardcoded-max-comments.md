---
status: pending
priority: p2
issue_id: 008
tags: [code-review, agent-native, flexibility]
dependencies: []
---

# Hardcoded max_comments Limit Reduces Agent Autonomy

## Problem Statement

The `max_comments = 5` is hardcoded in `FetchHNCommentsTool`, limiting agent autonomy. Agents cannot analyze more comments even if deeper analysis would improve sentiment accuracy.

## Findings

- **Location**: `/workspaces/hn-bot-farm/hn_farm.py:123`
- **Severity**: MEDIUM - Reduces agent flexibility
- **Identified by**: agent-native-reviewer

### Current Code:
```python
comments = []
errors = []
max_comments = 5  # Hardcoded

for comment_id in comment_ids[:max_comments]:
```

### Impact:
- Agents cannot override the 5-comment limit
- May miss important context from additional comments
- Reduces adaptability for different use cases

## Proposed Solutions

### Solution 1: Make max_comments Configurable (Recommended)
**Pros**: Agent can adjust based on needs, maintains reasonable default
**Cons**: Slightly larger API
**Effort**: Small
**Risk**: Low

```python
class FetchHNCommentsInput(BaseModel):
    story_id: int = Field(description="The HN story ID")
    comment_ids: list[int] = Field(default=[], description="List of comment IDs")
    max_comments: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum comments to return (1-20)"
    )

def _run(self, story_id: int, comment_ids: list[int], max_comments: int = 5) -> str:
    for comment_id in comment_ids[:max_comments]:
```

### Solution 2: Class Constant with Override
**Pros**: Clear intent, documented limit
**Cons**: Still requires code change to modify
**Effort**: Small
**Risk**: Low

```python
class FetchHNCommentsTool(BaseTool):
    MAX_COMMENTS = 5  # Class constant, at least self-documenting
```

## Technical Details

- **Affected Files**: `hn_farm.py`
- **Lines**: 82-88 (input schema), 123

## Acceptance Criteria

- [ ] max_comments added to input schema
- [ ] Default of 5 maintained
- [ ] Reasonable upper limit enforced (e.g., 20)
- [ ] Agent can override via tool input

## Work Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-03-07 | Issue identified | Found by agent-native-reviewer |

## Resources

- Agent-native architecture principles
