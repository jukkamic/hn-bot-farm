---
status: pending
priority: p3
issue_id: "019"
tags: [code-review, performance, llm, optimization]
dependencies: []
---

# Problem Statement

The new prompts significantly increase token usage (~2-3x). While manageable at current scale, this impacts cost and latency. Using Pydantic structured output could reduce prompt length and improve reliability.

## Findings

**Location:** `hn_farm.py` sentiment_task and edit_task

**Token Analysis:**
- Original sentiment_task: ~150 tokens
- New sentiment_task: ~400+ tokens
- Per-request increase: ~250 tokens

**Projected Monthly Cost (20 stories/day):**
- Additional input tokens: ~$4.50/month
- Additional output tokens: ~$1.50/month
- Total increase: ~$6/month

**Source:** performance-oracle (Prompt Token Bloat)

## Proposed Solutions

### Solution 1: Use Pydantic Structured Output (Recommended)
**Approach:** Define output schema with Pydantic models and let CrewAI enforce structure.

```python
class LeadQuote(BaseModel):
    comment_id: int
    text: str = Field(..., max_length=200)

class NotableComment(BaseModel):
    comment_id: int
    quote_snippet: str = Field(..., max_length=50)
    context: str = Field(..., max_length=100)

class StoryAnalysis(BaseModel):
    id: int
    title: str
    url: str
    vibe_score: int | str
    vibe_label: str
    vibe_reasoning: str
    lead_quote: Optional[LeadQuote]
    notable_comments: List[NotableComment]
    comments_analyzed: int

# Simplified prompt
sentiment_task = Task(
    description="Analyze comments for each story...",
    output_pydantic=List[StoryAnalysis],
)
```

**Pros:** Reduces prompt by ~50%, type-safe, automatic validation
**Cons:** Requires CrewAI support check
**Effort:** Medium
**Risk:** Low

### Solution 2: Add Token Budget Constraints
**Approach:** Add explicit length limits in prompt.

```python
"CONSTRAINTS:\n"
"- lead_quote.text: MAX 200 characters\n"
"- quote_snippet: MAX 50 characters (2-4 words)\n"
"- vibe_reasoning: MAX 300 characters\n"
```

**Pros:** Simple, reduces output tokens
**Cons:** LLM may not follow exactly
**Effort:** Small
**Risk:** Low

### Solution 3: Extract Prompts to Separate File
**Approach:** Move long prompts to `prompts.py` for easier maintenance.

**Pros:** Cleaner code, easier to version
**Cons:** Doesn't reduce tokens
**Effort:** Small
**Risk:** Low

## Recommended Action

Implement Solution 2 now (token constraints). Consider Solution 1 (Pydantic) for next iteration.

## Technical Details

**Affected Files:** `hn_farm.py`, potentially new `prompts.py`
**Components:** `sentiment_task`, `edit_task`
**Database Changes:** None

## Acceptance Criteria

- [ ] Token usage reduced by at least 20%
- [ ] Output quality maintained
- [ ] Documented cost savings

## Work Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-03-08 | Finding identified | Performance analysis |

## Resources

- PR: feat/analysis): add lead quotes and comment links to story analysis
- CrewAI structured output documentation
