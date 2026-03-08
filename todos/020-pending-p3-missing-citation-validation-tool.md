---
status: pending
priority: p3
issue_id: "020"
tags: [code-review, agent-native, tooling]
dependencies: []
---

# Problem Statement

The PR adds lead quotes and notable comments with HN comment IDs, but there is no CrewAI tool for agents to validate these IDs. A `citation_validator.py` utility exists but is not integrated as an agent tool.

## Findings

**Location:** `hn_farm.py` (no tool), `utils/citation_validator.py` (exists but unused)

**Gap:**
- Agents output comment_ids but can't verify them
- No way to check if links will work before publishing
- External `evidence-based-analysis` skill mentions citation validation but it's manual

**Source:** agent-native-reviewer (Critical Issue #1), learnings-researcher

## Proposed Solutions

### Solution 1: Create ValidateHNCommentTool (Recommended)
**Approach:** Wrap citation_validator.py as a CrewAI tool.

```python
class ValidateHNCommentInput(BaseModel):
    comment_id: int = Field(description="The HN comment ID to validate")

class ValidateHNCommentTool(BaseTool):
    name: str = "validate_hn_comment"
    description: str = "Validates that an HN comment ID exists. Returns True/False."
    args_schema: type[BaseModel] = ValidateHNCommentInput

    def _run(self, comment_id: int) -> str:
        # Check if comment exists via HN API
        try:
            url = f"{HN_API_BASE}/item/{comment_id}.json"
            data = fetch_hn_json(url)
            return json.dumps({"valid": data is not None and not data.get('deleted')})
        except:
            return json.dumps({"valid": False})
```

**Pros:** Agent can verify IDs, improves reliability
**Cons:** Adds HTTP call per validation
**Effort:** Medium
**Risk:** Low

### Solution 2: Add Verification Task
**Approach:** Add a fourth verification task after edit_task.

```python
verify_task = Task(
    description="Verify comment links in output/hn_daily.md are valid.",
    agent=verifier_agent,
    tools=[validate_hn_comment],
    context=[edit_task]
)
```

**Pros:** Catches issues before publication
**Cons:** Adds latency, complexity
**Effort:** Medium
**Risk:** Low

### Solution 3: Best-Effort Links (Current Approach)
**Approach:** Accept that some links may be broken.

**Pros:** No changes
**Cons:** Poor user experience
**Effort:** None
**Risk:** None

## Recommended Action

Consider Solution 1 for next iteration. Current implementation is acceptable for MVP but adding validation would improve quality.

## Technical Details

**Affected Files:** `hn_farm.py` (new tool), `utils/citation_validator.py` (reference)
**Components:** New `ValidateHNCommentTool`, potential new `verifier_agent`
**Database Changes:** None

## Acceptance Criteria

- [ ] Tool validates comment IDs against HN API
- [ ] Agent can use tool to verify before/after linking
- [ ] Test coverage for valid/invalid/deleted IDs

## Work Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-03-08 | Finding identified | Agent-native architecture review |

## Resources

- PR: feat/analysis): add lead quotes and comment links to story analysis
- Existing: `utils/citation_validator.py`
