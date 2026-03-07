---
title: Add Developer README.md
type: docs
status: completed
date: 2026-03-07
---

# Add Developer README.md

## Overview

Create a concise README.md for developers who are familiar with development tools but don't want to dig through project files to understand how to run and configure the project.

## Problem Statement / Motivation

No README.md exists. Developers need to:
1. Quickly understand what the project does
2. Set up their environment without reading source code
3. Know where to configure things (LLM provider, API keys)
4. Run the application

## Proposed Solution

Write a focused README that:
- Assumes developer familiarity with tools (VS Code, Python, Git)
- Lists setup steps, not detailed instructions
- Points to key configuration locations in the codebase
- Uses examples like "Ctrl+Shift+P to reload in container"

## Acceptance Criteria

- [x] README.md created at project root
- [ ] Project purpose explained in 1-2 sentences
- [ ] Setup steps listed (not verbose)
- [ ] Dev Container usage mentioned with VS Code tip
- [ ] LLM provider switching documented with code location
- [ ] .env setup explained (rename ".env.example" to .env)
- [ ] Run command shown
- [ ] Output location documented

## Content Structure

### README.md

```markdown
# hn-bot-farm

CrewAI application that fetches top Hacker News stories, analyzes comment sentiment, and generates a Markdown newsletter with "Vibe Scores".

## Quick Start

### Requirements
- VS Code with Dev Containers extension
- Docker Desktop (or compatible runtime)

### Setup

1. Open in VS Code → it should prompt to "Reopen in Container"
   - If not: `Ctrl+Shift+P` → "Dev Containers: Reopen in Container"
2. Copy `.env.example` to `.env` and add your API keys
3. `python hn_farm.py`

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `ZAI_API_KEY` | Z.ai GLM-5 model (default provider) |
| `GROQ_API_KEY` | Groq Llama model (alternative) |

### Switch LLM Provider

Edit `hn_farm.py` line ~84:

```python
active_provider = providers["zai"]  # Change to "groq" to use Groq
```

### Output

Generated at `output/hn_daily.md` with:
- Top 5 HN stories with links
- Vibe Scores (1-5) based on comment sentiment
- Brief sentiment reasoning

## Architecture

3-agent pipeline: **Researcher** (fetches stories) → **Sentiment Analyst** (analyzes comments) → **Editor** (formats output)

## Files

| File | Purpose |
|------|---------|
| `hn_farm.py` | Main application |
| `requirements.txt` | Dependencies |
| `output/hn_daily.md` | Generated newsletter |
```

## Sources & References

- Existing plan: `docs/plans/2026-03-07-feat-sentiment-analyst-agent-plan.md`
- Main code: `hn_farm.py`
- Dev container: `.devcontainer/devcontainer.json`
