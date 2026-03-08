---
name: evidence-based-analysis
description: Performs deep sentiment analysis on HN comments with verified citations.
---
# Evidence-Based Analysis Workflow

## Phase 1: Single-Pass Extraction
1. **Scrape:** Fetch top stories and all top-level comments.
2. **Analyze:** In a single LLM call, generate a JSON object with:
   - `analysis`: 2-3 sentences of mood summary.
   - `lead_quote`: { "text": "...", "id": "12345" }
   - `citations`: List of { "text": "...", "id": "67890", "type": "representative" }

## Phase 2: Citation Validation
For every `id` extracted in Phase 1:
1. Run `./.venv/bin/python utils/citation_validator.py <id>`.
2. **If INVALID:** Claude must discard that quote and re-run Phase 1 for that specific story to find a new, valid link.

## Phase 3: Assembly
1. Convert the validated JSON into the final Markdown format.
2. Ensure the "Lead Quote" links directly to the HN comment URL.