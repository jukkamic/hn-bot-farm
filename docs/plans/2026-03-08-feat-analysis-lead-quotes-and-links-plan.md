---
title: Add Lead Quotes and Comment Links to Story Analysis
type: feat
status: completed
date: 2026-03-08
revision: 2
change_summary: "Refactored to single-pass design with comment-centric output to avoid cognitive duplication"
---

# Add Lead Quotes and Comment Links to Story Analysis

## Overview

Enhance the HN Daily Digest newsletter by adding lead quotes and comment links to the story analysis section. This makes the analysis more engaging and provides quick access to representative comments.

## Problem Statement / Motivation

The current analysis provides a summary of comment sentiment but lacks:
1. A hook that immediately conveys the "flavor" of the discussion
2. Direct links to specific comments mentioned or representative of the mood

Readers can't quickly verify or explore the reasoning behind the vibe scores.

### Original Plan Issue: Cognitive Duplication

The original plan had the sentiment analyst:
1. Analyze comments → write `vibe_reasoning`
2. Re-read its OWN reasoning → identify phrases to link
3. Map phrases back → find source comment IDs

This creates cognitive overhead and risk of hallucination. The LLM must mentally trace "which comment did 'FAQ parody' come from?" after writing the reasoning.

## Proposed Solution: Comment-Centric Single-Pass Design

**Key insight**: Instead of having the LLM identify phrases in its own output, have it identify NOTABLE COMMENTS directly, then write reasoning that references them.

### Revised Data Flow

```
FetchHNCommentsTool → {id, text, by, time}
    ↓
Sentiment Analyst (single pass):
    - For each comment, decide: is this notable? why?
    - Select lead_quote_comment (most representative)
    - Select 1-2 other notable comments
    - Write vibe_reasoning that EXPLICITLY mentions notable comments
    ↓
{vibe_score, vibe_reasoning, notable_comments: [{id, quote_snippet, why_notable}]}
    ↓
Editor:
    - Renders lead quote as blockquote with link
    - Finds mentioned quote_snippets in reasoning
    - Replaces with markdown links
```

### Why This Works

1. **Single pass through comments**: LLM evaluates each comment once for notability
2. **No self-referential lookup**: LLM doesn't need to parse its own output
3. **Explicit traceability**: Each notable comment has explicit `{id, quote_snippet}` pair
4. **Editor handles linking**: Simple string replacement, no LLM judgment needed

## Technical Considerations

### JSON Output Contract (Revised)

```json
{
  "id": 12345,
  "title": "Story Title",
  "url": "https://...",
  "vibe_score": 4,
  "vibe_label": "Positive",
  "vibe_reasoning": "Comments show enthusiasm. As one user put it, 'This is exactly what I've been waiting for'. Others shared nostalgic memories.",
  "comments_analyzed": 5,
  "lead_quote": {
    "comment_id": 67890,
    "text": "This is exactly what I've been waiting for"
  },
  "notable_comments": [
    {
      "comment_id": 67891,
      "quote_snippet": "nostalgic memories",
      "context": "represents the warm reminiscence theme"
    }
  ]
}
```

### Link Rendering Rules (Editor Task)

1. **Lead quote**: Always rendered as blockquote with link
   ```markdown
   > "[lead_quote.text](https://news.ycombinator.com/item?id=lead_quote.comment_id)"
   ```

2. **Notable comments**: Editor finds `quote_snippet` in `vibe_reasoning` and wraps with link
   - Input: `"Others shared nostalgic memories."`
   - Output: `"Others shared [nostalgic memories](https://news.ycombinator.com/item?id=67891)."`

3. **No duplicates**: If `lead_quote.comment_id` appears in `notable_comments`, skip it

### HN Comment URL Format
```
https://news.ycombinator.com/item?id={comment_id}
```

## System-Wide Impact

- **Interaction graph**: Only affects sentiment_task and edit_task descriptions
- **Error propagation**: If linking fails, fall back to plain text (graceful degradation)
- **State lifecycle risks**: None - purely additive output
- **API surface parity**: Affects only newsletter output format

## Acceptance Criteria

- [x] `sentiment_task` outputs `lead_quote` object with `{comment_id, text}`
- [x] `sentiment_task` outputs `notable_comments` array with `{comment_id, quote_snippet, context}`
- [x] `notable_comments` limited to 1-2 entries (plus lead quote)
- [x] `vibe_reasoning` explicitly mentions the `quote_snippet` phrases
- [x] `edit_task` renders lead quote as blockquote with link
- [x] `edit_task` performs string replacement for `quote_snippet` → markdown link
- [x] No duplicate links (lead quote ID excluded from notable links)
- [x] Mixed reactions include notable comments from both sides

## Success Metrics

- Each story analysis starts with an engaging lead quote
- Analysis contains 1-2 clickable links to actual HN comments
- Links are contextually appropriate (quote snippets match actual reasoning text)
- Reader can quickly verify the vibe score reasoning

## Implementation

### Task 1: Update sentiment_task Description

**File**: `hn_farm.py` lines 309-327

```python
sentiment_task = Task(
    description=(
        "Analyze the sentiment of comments for each story. "
        "For each story, use the fetch_hn_comments tool with the story's ID "
        "and the first 5 comment IDs from its 'kids' field.\n\n"

        "Vibe Score Scale:\n"
        "- 1: Very Negative (hostile, dismissive, critical)\n"
        "- 2: Negative (skeptical, concerned, critical)\n"
        "- 3: Neutral (mixed, factual, indifferent)\n"
        "- 4: Positive (interested, approving, supportive)\n"
        "- 5: Very Positive (enthusiastic, praiseworthy, excited)\n\n"

        "SINGLE-PASS ANALYSIS:\n"
        "As you read each comment, decide if it's NOTABLE. A notable comment:\n"
        "- Perfectly represents the overall mood, OR\n"
        "- Expresses a specific viewpoint worth highlighting, OR\n"
        "- Is particularly well-phrased or memorable\n\n"

        "OUTPUT STRUCTURE:\n"
        "1. lead_quote: The SINGLE MOST representative comment\n"
        "   - comment_id: the HN comment ID\n"
        "   - text: a 1-2 sentence excerpt (this will be the blockquote)\n\n"

        "2. notable_comments: 1-2 ADDITIONAL comments worth linking\n"
        "   - comment_id: the HN comment ID\n"
        "   - quote_snippet: a 2-4 word phrase YOU WILL USE in your reasoning\n"
        "   - context: brief note why this comment is notable\n\n"

        "3. vibe_reasoning: Your analysis text that MUST INCLUDE the quote_snippets\n"
        "   - When you mention a notable comment, use its exact quote_snippet\n"
        "   - Example: If quote_snippet is 'nostalgic memories', write 'shared nostalgic memories'\n\n"

        "CRITICAL: Your vibe_reasoning must contain the exact quote_snippet phrases.\n"
        "The editor will search for these phrases and convert them to links.\n\n"

        "Return a JSON list with each story including:\n"
        "- id, title, url\n"
        "- vibe_score, vibe_label, vibe_reasoning\n"
        "- lead_quote: {comment_id, text}\n"
        "- notable_comments: [{comment_id, quote_snippet, context}]\n"
        "- comments_analyzed\n\n"

        "If a story has no comments, assign vibe_score='N/A' with empty lead_quote and notable_comments."
    ),
    expected_output="A JSON list of stories with vibe scores, lead quotes, and notable comments.",
    agent=sentiment_analyst,
    context=[research_task]
)
```

### Task 2: Update edit_task Description

**File**: `hn_farm.py` lines 329-357

```python
edit_task = Task(
    description=(
        "Take the story data from the context and format it into a professional "
        "Markdown newsletter with comment links.\n\n"

        "INPUT STRUCTURE (from sentiment analyst):\n"
        "- id, title, url\n"
        "- vibe_score, vibe_label, vibe_reasoning\n"
        "- lead_quote: {comment_id, text}\n"
        "- notable_comments: [{comment_id, quote_snippet, context}]\n\n"

        "LINK FORMATTING:\n"
        "1. Lead Quote (always first, as blockquote):\n"
        "   > \"[lead_quote.text](https://news.ycombinator.com/item?id=lead_quote.comment_id)\"\n\n"

        "2. Notable Comments (string replacement in reasoning):\n"
        "   - Find each quote_snippet in vibe_reasoning\n"
        "   - Replace with: [quote_snippet](https://news.ycombinator.com/item?id=comment_id)\n"
        "   - SKIP if comment_id matches lead_quote.comment_id (no duplicates)\n\n"

        "FORMAT FOR EACH STORY:\n"
        "1. **[Title](URL)** *Vibe: X/5 Label*\n\n"
        "   > \"[lead_quote with link]\"\n\n"
        "   [vibe_reasoning with notable comment links embedded]\n\n"

        f"Create a file at 'output/hn_daily.md' with:\n"
        f"- Header: 'Hacker News Daily Digest - {datetime.now().strftime('%A %B %d, %Y')}'\n"
        "- Brief intro\n"
        "- Numbered list of stories\n"
        "- Closing section\n\n"

        "Use the FileWriterTool with directory='output' and filename='hn_daily.md'."
    ),
    expected_output="Confirmation that output/hn_daily.md has been created with lead quotes and comment links.",
    agent=newsletter_editor,
    context=[sentiment_task]
)
```

### Example Output

```markdown
3. **[Dumping Lego NXT firmware off of an existing brick](https://arcanenibble.github.io/...)** *Vibe: 5/5 Very Positive*

   > "[This is exactly the kind of reverse engineering content I come to HN for](https://news.ycombinator.com/item?id=12345)"

   Highly appreciative comments praising the article's writing style. Several users shared [fond memories of Lego Mindstorms](https://news.ycombinator.com/item?id=12346) from their youth, while others discussed the technical aspects of the dump process.
```

## Why This Avoids Duplication

| Original Design | Revised Design |
|-----------------|----------------|
| LLM analyzes comments | LLM analyzes comments (same) |
| LLM writes reasoning | LLM identifies notable comments WHILE analyzing |
| LLM re-reads reasoning to find phrases | LLM picks quote_snippets UPFRONT |
| LLM maps phrases → comment IDs | LLM provides {id, snippet} pairs explicitly |
| 2 cognitive passes | 1 cognitive pass |

The key change: the LLM decides WHAT to link while reading comments, not after writing analysis.

## Dependencies & Risks

| Risk | Mitigation |
|------|------------|
| LLM forgets to include quote_snippet in reasoning | Explicit instruction + example |
| quote_snippet doesn't appear in reasoning | Editor falls back to plain text |
| Too many notable comments | Limit to 1-2 in task description |
| Lead quote too long | Instruction to limit to 1-2 sentences |

## Sources & References

### Internal References
- Sentiment analyst patterns: `hn_farm.py:273-284` (agent), `hn_farm.py:309-327` (task)
- Comment fetching: `hn_farm.py:198-254`
- Editor formatting: `hn_farm.py:286-296` (agent), `hn_farm.py:329-357` (task)
- Solution doc: `docs/solutions/feature-development/sentiment-analyst-agent-optimization.md`

### External References
- HN API: https://github.com/HackerNews/API
- CrewAI Task documentation: https://docs.crewai.com/core-concepts/Tasks
