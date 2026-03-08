---
status: pending
priority: p2
issue_id: "018"
tags: [code-review, simplification, yagni]
dependencies: []
---

# Problem Statement

The current implementation uses a two-tier comment system (`lead_quote` + `notable_comments`) with a complex string-matching mechanism. This is over-engineered for what the output actually needs: quotes with links to comments.

## Findings

**Location:** `hn_farm.py` lines 328-351 (sentiment_task), 374-377 (edit_task)

**Current Complexity:**
1. `lead_quote` - ONE "most representative" comment (special treatment)
2. `notable_comments` - 1-2 ADDITIONAL comments with `quote_snippet` matching
3. Deduplication logic ("SKIP if comment_id matches lead_quote.comment_id")
4. CRITICAL warnings about exact phrase matching

**Why It's Over-Engineered:**
- The output just shows blockquotes with links - no need for dual classification
- The string replacement mechanism is fragile
- The "context" field in notable_comments is never used in output
- Adds cognitive load for LLM without value

**Source:** code-simplicity-reviewer (YAGNI Violations)

## Proposed Solutions

### Solution 1: Single Array of Notable Comments (Recommended)
**Approach:** Replace lead_quote + notable_comments with a single array.

```json
"notable_comments": [
  {"comment_id": 123, "excerpt": "..."},
  {"comment_id": 456, "excerpt": "..."}
]
```

Editor:
- First comment becomes the blockquote
- Remaining comments get linked inline

**Pros:** Simpler structure, no deduplication, no special cases
**Cons:** Changes data contract
**Effort:** Medium
**Risk:** Low

### Solution 2: Keep Current Structure but Remove quote_snippet
**Approach:** Keep lead_quote, remove quote_snippet mechanism from notable_comments.

Editor links to notable comments at the end of reasoning:
```
[reasoning text]

See also: [comment 1](link), [comment 2](link)
```

**Pros:** Simpler linking, no phrase matching
**Cons:** Changes output format
**Effort:** Small
**Risk:** Low

### Solution 3: Status Quo with Documentation
**Approach:** Keep current design but document the rationale.

**Pros:** No changes
**Cons:** Doesn't address complexity
**Effort:** Trivial
**Risk:** None

## Recommended Action

Consider Solution 1 or 2 during a refactor. The current design works but is more complex than necessary.

## Technical Details

**Affected Files:** `hn_farm.py`
**Components:** `sentiment_task` description, `edit_task` description
**Database Changes:** None

## Acceptance Criteria

- [ ] Simpler data structure
- [ ] No fragile string matching
- [ ] Same or better output quality

## Work Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-03-08 | Finding identified | Code simplicity review |

## Resources

- PR: feat/analysis): add lead quotes and comment links to story analysis
- Related: todos/015 (brittle string replacement)
