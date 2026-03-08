---
title: Update README.md with New Features and Configuration
type: docs
status: completed
date: 2026-03-08
---

# Update README.md with New Features and Configuration

## Overview

Update README.md to reflect changes made since 2026-03-07, focusing on user-facing setup, installation, and utility features.

## Problem Statement / Motivation

The README.md was last updated on 2026-03-07 (commit `0663dda`). Since then, several commits introduced new user-facing features and configuration options that should be documented:

| Commit | Feature | User-Facing? |
|--------|---------|--------------|
| `da4e18e` | `LLM_PROVIDER` env var for provider switching | Yes |
| `e8b322c` | API key validation | Yes |
| `cbf2f6f` | Markdown-to-HTML converter utility | Yes |
| `e50255e` | Citation validator utility | Yes (dev/debug) |
| `1b7a758` | Lead quotes and comment links in analysis | Internal |

## Proposed Solution

Update README.md sections while maintaining focus on setup, installation, and usage. Avoid documenting all changes - stick to relevant topics.

### Changes to Make

#### 1. Update Environment Variables Table

**Current:**
```markdown
## Environment Variables

| Variable | Purpose |
|----------|---------|
| `ZAI_API_KEY` | Z.ai GLM-5 model (default provider) |
| `GROQ_API_KEY` | Groq Llama model (alternative) |
```

**New:**
```markdown
## Environment Variables

| Variable | Purpose |
|----------|---------|
| `LLM_PROVIDER` | LLM provider to use: `zai` (default) or `groq` |
| `ZAI_API_KEY` | Z.ai API key (required if `LLM_PROVIDER=zai`) |
| `GROQ_API_KEY` | Groq API key (required if `LLM_PROVIDER=groq`) |
```

#### 2. Replace "Switch LLM Provider" Section

**Current (requires code edit):**
```markdown
## Switch LLM Provider

Edit `hn_farm.py` line ~84:

```python
active_provider = providers["zai"]  # Change to "groq" to use Groq
```
```

**New (uses env var):**
```markdown
## Switch LLM Provider

Set the `LLM_PROVIDER` environment variable in your `.env` file:

```bash
LLM_PROVIDER=groq  # Options: zai (default), groq
```

The application validates API keys on startup and will error if the required key is missing.
```

#### 3. Add Utilities Section

**New section:**
```markdown
## Utilities

### Markdown to HTML Converter

Convert the generated newsletter to styled HTML:

```bash
.venv/bin/python utils/md_converter.py output/hn_daily.md
```

Generates `output/hn_daily.html` with Sakura CSS styling.

**Options:**
- Custom output path: `.venv/bin/python utils/md_converter.py input.md output.html`
- XSS-sanitized output (built-in)

### Citation Validator

Validate HN item IDs for citations (development/debug tool):

```bash
.venv/bin/python utils/citation_validator.py <item_id>
```

Returns `VALID` or `INVALID` based on Hacker News API response.
```

#### 4. Update Files Table

**Add utility files:**

```markdown
## Files

| File | Purpose |
|------|---------|
| `hn_farm.py` | Main application |
| `utils/md_converter.py` | Markdown to HTML converter |
| `utils/citation_validator.py` | HN item ID validator |
| `requirements.txt` | Dependencies |
| `output/hn_daily.md` | Generated newsletter |
| `output/hn_daily.html` | HTML version (optional) |
```

## Acceptance Criteria

- [x] Environment variables table includes `LLM_PROVIDER`
- [x] "Switch LLM Provider" section uses env var approach (no code edit required)
- [x] New "Utilities" section documents `md_converter.py` usage
- [x] Files table includes utility files and HTML output
- [x] No documentation of internal changes (lead quotes, code reviews)
- [x] README remains concise and focused on user-facing setup/usage

## Files to Modify

| File | Change Type |
|------|-------------|
| `README.md` | Update |

## Out of Scope

- Documenting internal analysis changes (lead quotes, comment links)
- Documenting code review fixes
- Documenting security hardening details (utilities handle this internally)
- Detailed API documentation
