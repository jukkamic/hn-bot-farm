---
status: pending
priority: p2
issue_id: "016"
tags: [code-review, reliability, agent-native]
dependencies: []
---

# Problem Statement

The edit_task prompt assumes `lead_quote` and `notable_comments` always exist with valid data. If the sentiment analyst returns malformed JSON (missing fields, null values, incorrect types), the editor will fail silently or produce broken output.

## Findings

**Location:** `hn_farm.py` lines 365-377 (edit_task description)

**Current Assumptions:**
- `lead_quote` always has `comment_id` and `text`
- `notable_comments` always has items with `comment_id`, `quote_snippet`, `context`
- All IDs are valid integers

**What's Missing:**
- Handling for `lead_quote` being `None` or empty `{}`
- Handling for `notable_comments` being empty `[]`
- Handling for malformed `comment_id` values
- Handling for `quote_snippet` not found in reasoning

**Source:** agent-native-reviewer (Critical Issue #2)

## Proposed Solutions

### Solution 1: Add Explicit Error Handling Instructions (Recommended)
**Approach:** Add error handling section to edit_task description.

```python
"ERROR HANDLING:\n"
"- If lead_quote is missing or empty, skip the blockquote section\n"
"- If notable_comments is empty, use vibe_reasoning as-is without modifications\n"
"- If quote_snippet is not found in vibe_reasoning after 3 attempts, skip that link\n"
"- If comment_id is invalid (not a number), skip that link\n"
```

**Pros:** Comprehensive, explicit, improves reliability
**Cons:** Adds prompt length
**Effort:** Small
**Risk:** Low

### Solution 2: Add Validation Task Between Sentiment and Edit
**Approach:** Create a validation task that checks sentiment output before passing to editor.

**Pros:** Separates concerns, catches errors early
**Cons:** Adds task, increases complexity
**Effort:** Medium
**Risk:** Low

### Solution 3: Use Pydantic Model Validation
**Approach:** Define output schema with Pydantic and enforce validation.

```python
class StoryAnalysis(BaseModel):
    lead_quote: Optional[LeadQuote] = None
    notable_comments: List[NotableComment] = []
```

**Pros:** Type-safe, automatic validation
**Cons:** Requires CrewAI structured output support
**Effort:** Medium
**Risk:** Low

## Recommended Action

Use Solution 1 - Add explicit error handling instructions. Quick, non-breaking, improves reliability immediately.

## Technical Details

**Affected Files:** `hn_farm.py`
**Components:** `edit_task` description
**Database Changes:** None

## Acceptance Criteria

- [ ] Editor gracefully handles missing lead_quote
- [ ] Editor gracefully handles empty notable_comments
- [ ] Editor gracefully handles malformed comment_id
- [ ] Test with various malformed inputs

## Work Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-03-08 | Finding identified | Agent-native architecture review |

## Resources

- PR: feat/analysis): add lead quotes and comment links to story analysis
- Related: todos/015 (brittle string replacement)
