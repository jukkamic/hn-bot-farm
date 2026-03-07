---
title: Developer-Focused README Pattern
type: docs
status: completed
date: 2026-03-07
affected_files:
  - README.md
tags:
  - documentation
  - readme
  - developer-experience
---

# Developer-Focused README Pattern

## Problem Statement

README files often fall into two extremes: too detailed (tutorial-style) or too sparse (just a title). Developers familiar with tools don't want verbose instructions but do need quick reference for project-specific configuration.

## Solution Pattern

Structure README for developers who know their tools:

### What Works

| Include | Skip |
|---------|------|
| Setup steps (not tutorials) | "First, download Python..." |
| Configuration locations | Detailed installation guides |
| One-line tips ("Ctrl+Shift+P") | Screenshots of every step |
| Where to change settings | What each dependency does |

### README Structure

```markdown
# project-name

One-sentence description.

## Quick Start

### Requirements
- Tool names (assume familiarity)

### Setup
1. Step with tip: "Ctrl+Shift+P → 'Reopen in Container'"
2. Configuration step: "Copy `.env.example` to `.env`"
3. Run command

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `API_KEY` | Brief description |

## Configuration

Where to change settings:
```python
active_provider = providers["option_a"]  # Line ~42
```

## Output

What gets generated and where.

## Files

| File | Purpose |
|------|---------|
| `main.py` | Brief description |
```

## Key Principles

1. **Assume tool familiarity** - They know Docker, VS Code, Git
2. **Point, don't explain** - "Change line 42" not "Open the file and find..."
3. **Show, don't tell** - Code snippets over prose
4. **Tables over paragraphs** - Environment variables, file lists

## Examples from This Project

- Dev Container tip: "If not: `Ctrl+Shift+P` → 'Dev Containers: Reopen in Container'"
- Config location: "Edit `hn_farm.py` line ~84"
- File list: Simple table instead of verbose descriptions

## Related

- README.md at project root
- `.env.example` template file
