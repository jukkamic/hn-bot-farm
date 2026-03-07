---
status: pending
priority: p2
issue_id: 007
tags: [code-review, performance, scalability]
dependencies: []
---

# Sequential API Calls Performance Bottleneck

## Problem Statement

API calls to Hacker News are made sequentially, creating significant latency. With 5 stories and 5 comments each, there are 31 sequential API calls that could take 6-15+ seconds in ideal conditions, or up to 310 seconds with network issues.

## Findings

- **Location**: `/workspaces/hn-bot-farm/hn_farm.py:63-73`, `125-146`
- **Severity**: MEDIUM - Significant performance issue at scale
- **Identified by**: performance-oracle

### Current Pattern:
```python
# 6 sequential calls for stories
for story_id in story_ids[:5]:
    story = fetch_json(story_url)  # Blocking

# 25 sequential calls for comments
for comment_id in comment_ids[:max_comments]:
    comment_data = fetch_json(url)  # Blocking
```

### Impact at Scale:
| Scale | Total Calls | Sequential Time | Parallel Time |
|-------|-------------|-----------------|---------------|
| Current (5 stories) | 31 | 6-15s | 1-2s |
| 10x (50 stories) | 2,551 | 7+ hours | 15-30s |

## Proposed Solutions

### Solution 1: Async with aiohttp (Recommended)
**Pros**: 5-10x latency reduction, already in dependencies
**Cons**: Requires async refactoring
**Effort**: Medium
**Risk**: Medium

The project already has `aiohttp==3.13.3` in dependencies.

```python
import aiohttp
import asyncio

async def fetch_json_async(url: str, session: aiohttp.ClientSession) -> dict:
    async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
        return await response.json()

async def fetch_all_stories(story_ids: list[int]) -> list[dict]:
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_json_async(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", session)
                 for sid in story_ids[:5]]
        return await asyncio.gather(*tasks)
```

### Solution 2: ThreadPoolExecutor
**Pros**: No async required, simpler changes
**Cons**: Thread overhead, not as efficient as async
**Effort**: Small
**Risk**: Low

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_all_stories(story_ids: list[int]) -> list[dict]:
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(fetch_json, f"...{sid}.json"): sid for sid in story_ids[:5]}
        return [future.result() for future in as_completed(futures)]
```

## Technical Details

- **Affected Files**: `hn_farm.py`
- **Lines**: 63-73, 125-146

## Acceptance Criteria

- [ ] Story fetches parallelized
- [ ] Comment fetches parallelized per story
- [ ] Connection pooling implemented
- [ ] Measurable performance improvement documented

## Work Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-03-07 | Issue identified | Found by performance-oracle |

## Resources

- aiohttp documentation
- Python asyncio guide
