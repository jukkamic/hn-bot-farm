---
status: pending
priority: p2
issue_id: "017"
tags: [code-review, security, validation]
dependencies: []
---

# Problem Statement

The LLM outputs `comment_id` values that are used to construct HN URLs. There's no validation that these IDs are valid integers before URL construction. A hallucinated or malformed ID could result in broken links.

## Findings

**Location:** `hn_farm.py` lines 333-336, 372-376

**Current Flow:**
1. Sentiment analyst outputs JSON with `comment_id`
2. Editor constructs URL: `https://news.ycombinator.com/item?id={comment_id}`
3. No validation of `comment_id` format

**Risk:**
- LLM hallucination produces non-numeric ID
- Broken links in newsletter
- Potential for malformed URLs

**Source:** security-sentinel (Finding 2 - MEDIUM)

## Proposed Solutions

### Solution 1: Add Regex Validation Instruction (Recommended)
**Approach:** Add validation instruction to edit_task.

```python
"VALIDATION:\n"
"- Before creating links, verify comment_id is a valid integer\n"
"- If comment_id contains non-numeric characters, skip that link\n"
```

**Pros:** Simple, works within LLM prompt
**Cons:** Relies on LLM compliance
**Effort:** Small
**Risk:** Low

### Solution 2: Post-Processing Validation
**Approach:** Add Python code to validate IDs after LLM output, before file writing.

```python
import re
def validate_comment_id(comment_id) -> bool:
    return bool(re.match(r'^[0-9]+$', str(comment_id)))
```

**Pros:** Programmatic guarantee
**Cons:** Requires code changes, harder to integrate with CrewAI flow
**Effort:** Medium
**Risk:** Low

### Solution 3: Use Citation Validator Tool
**Approach:** Integrate existing `utils/citation_validator.py` as a CrewAI tool.

**Pros:** Leverages existing code, can verify IDs exist on HN
**Cons:** Adds HTTP call, more complex
**Effort:** Medium
**Risk:** Low

## Recommended Action

Use Solution 1 for immediate fix. Consider Solution 3 for comprehensive validation (verifies ID actually exists on HN).

## Technical Details

**Affected Files:** `hn_farm.py`
**Components:** `sentiment_task`, `edit_task`
**Related Files:** `utils/citation_validator.py` (exists but not integrated)
**Database Changes:** None

## Acceptance Criteria

- [ ] Non-numeric comment_ids are caught and handled
- [ ] No broken URLs in newsletter output
- [ ] Test with malformed IDs

## Work Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-03-08 | Finding identified | Security audit |

## Resources

- PR: feat/analysis): add lead quotes and comment links to story analysis
- Related: `utils/citation_validator.py`
