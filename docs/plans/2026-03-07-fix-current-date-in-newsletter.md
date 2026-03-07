---
title: Fix Newsletter Date to Current Date
type: fix
status: completed
date: 2026-03-07
---

# Fix Newsletter Date to Current Date

## Problem Statement

The newsletter output shows "January 2025 Edition" but we're in March 2026. The LLM is generating stale dates because the task description says "today's date" but the LLM doesn't have actual date context. This is a **daily digest** so it should show the full date (e.g., "Friday March 7, 2026").

## Root Cause

The `edit_task` description in `hn_farm.py:340` says "A header with today's date" - but LLMs don't know the current date unless explicitly provided.

## Proposed Solution

Inject the current date dynamically using Python's `datetime` module into the task description. Format as full daily date: `"Friday March 7, 2026"`.

## Acceptance Criteria

- [x] Import `datetime` at top of file
- [x] Update edit_task description with dynamic date
- [x] Verify output shows full date format: "Friday March 7, 2026"

## Implementation

### hn_farm.py

**Step 1:** Add import at top of file (around line 4):

```python
from datetime import datetime
```

**Step 2:** Update edit_task description (line ~339-340):

Change:
```python
"- A header with today's date\n"
```

To:
```python
f"- A header with 'Hacker News Daily Digest - {datetime.now().strftime('%A %B %d, %Y')}'\n"
```

This produces output like: "Hacker News Daily Digest - Friday March 7, 2026"

### Why Dynamic?

- Date auto-updates on each run
- No code changes needed for future dates
- Standard daily digest format
