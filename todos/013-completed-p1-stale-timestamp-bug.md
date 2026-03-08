---
status: completed
priority: p1
issue_id: "013"
tags: [code-review, correctness, python]
dependencies: []
---

# Problem Statement

The timestamp in the edit_task description is evaluated at **module import time**, not at task execution time. This means if the script runs around midnight or the crew takes time to execute, the newsletter header could display the wrong date.

## Findings

**Location:** `hn_farm.py` line 385

```python
f"- Header: 'Hacker News Daily Digest - {datetime.now().strftime('%A %B %d, %Y')}'\n"
```

**Impact:**
- If script runs at 11:59 PM on March 8th, but finishes on March 9th, header says "March 8th"
- If module is imported for testing, timestamp is baked in prematurely
- Production scheduled jobs will show incorrect dates if there's any delay

**Source:** kieran-python-reviewer (Critical Issue)

## Proposed Solutions

### Solution 1: Dynamic Date in Task Description (Recommended)
**Approach:** Create the task dynamically in `main()` or use a placeholder that gets replaced at runtime.

```python
# Option A: Create task in main()
def main():
    current_date = datetime.now().strftime('%A %B %d, %Y')
    edit_task.description = edit_task.description.replace("{DATE}", current_date)
    result = crew.kickoff()
```

**Pros:** Simple change, preserves existing structure
**Cons:** Slight modification to main() logic
**Effort:** Small
**Risk:** Low

### Solution 2: Let LLM Generate the Date
**Approach:** Instruct the LLM to use the current date in the header.

```python
"- Header: 'Hacker News Daily Digest - [Current Date, use today's date]'"
```

**Pros:** No code changes to main()
**Cons:** Relies on LLM knowing current date (may be unreliable)
**Effort:** Small
**Risk:** Medium

## Recommended Action

Use Solution 1 - Replace the f-string with a placeholder `{DATE}` and replace it dynamically in `main()`.

## Technical Details

**Affected Files:** `hn_farm.py`
**Components:** `edit_task` task definition, `main()` function
**Database Changes:** None

## Acceptance Criteria

- [ ] Date is computed at crew execution time, not import time
- [ ] Running `import hn_farm` does not evaluate the timestamp
- [ ] Test confirms date is correct when script takes time to execute

## Work Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-03-08 | Finding identified | Code review by kieran-python-reviewer |

## Resources

- PR: feat/analysis): add lead quotes and comment links to story analysis
- Branch: feat/analysis-lead-quotes-and-links
