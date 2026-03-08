---
status: pending
priority: p2
issue_id: "015"
tags: [code-review, reliability, llm]
dependencies: []
---

# Problem Statement

The edit_task requires the newsletter_editor to perform exact string matching of `quote_snippet` phrases within `vibe_reasoning` text to create Markdown links. This mechanism is fragile and prone to silent failures.

## Findings

**Location:** `hn_farm.py` lines 374-377 (edit_task)

**Current Instruction:**
```
"Find each quote_snippet in vibe_reasoning\n"
"Replace with: [quote_snippet](https://news.ycombinator.com/item?id=comment_id)"
```

**Failure Modes:**
1. LLM uses slightly different phrasing ("Nostalgic Memories" vs "nostalgic memories")
2. LLM adds punctuation to the phrase
3. LLM forgets to include the snippet entirely
4. Substring collision (snippet "the" matches many occurrences)

**Source:** security-sentinel (Finding 3), performance-oracle, code-simplicity-reviewer, agent-native-reviewer

## Proposed Solutions

### Solution 1: Use Placeholder Tokens (Recommended)
**Approach:** Use unique placeholders like `{{QUOTE_1}}` instead of substring matching.

In sentiment_task output:
```json
"vibe_reasoning": "Users shared {{QUOTE_1}} about the project and {{QUOTE_2}} about alternatives."
```

Editor replaces deterministically:
```python
for i, nc in enumerate(notable_comments):
    reasoning = reasoning.replace(f"{{{{QUOTE_{i+1}}}}}", link)
```

**Pros:** Deterministic, no substring matching issues
**Cons:** Requires coordination between tasks
**Effort:** Medium
**Risk:** Low

### Solution 2: Add Case-Insensitive Matching + Validation
**Approach:** Instruct editor to use case-insensitive matching and report which snippets were linked.

```python
"Use case-insensitive matching. After formatting, list which snippets were successfully linked."
```

**Pros:** Backward compatible
**Cons:** Still relies on LLM instruction following
**Effort:** Small
**Risk:** Medium

### Solution 3: Simplify to Ordered Comments
**Approach:** Remove snippet matching entirely. Editor formats notable comments as a list after the reasoning.

**Pros:** Eliminates entire failure mode
**Cons:** Changes output format
**Effort:** Small
**Risk:** Low

## Recommended Action

Use Solution 1 or 3. The current string-replacement mechanism is over-engineered for what could be a simpler approach.

## Technical Details

**Affected Files:** `hn_farm.py`
**Components:** `sentiment_task` description, `edit_task` description
**Database Changes:** None

## Acceptance Criteria

- [ ] Link creation is deterministic and reliable
- [ ] No silent failures when LLM slightly modifies text
- [ ] Test coverage for edge cases (punctuation, capitalization)

## Work Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-03-08 | Finding identified | Multiple reviewers flagged this issue |

## Resources

- PR: feat/analysis): add lead quotes and comment links to story analysis
- Related: code-simplicity-reviewer findings on over-engineered design
