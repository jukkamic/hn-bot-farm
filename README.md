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
3. Run: `python hn_farm.py`

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `LLM_PROVIDER` | LLM provider to use: `zai` (default) or `groq` |
| `ZAI_API_KEY` | Z.ai API key (required if `LLM_PROVIDER=zai`) |
| `GROQ_API_KEY` | Groq API key (required if `LLM_PROVIDER=groq`) |

## Switch LLM Provider

Set the `LLM_PROVIDER` environment variable in your `.env` file:

```bash
LLM_PROVIDER=groq  # Options: zai (default), groq
```

The application validates API keys on startup and will error if the required key is missing.

## Output

Generated at `output/hn_daily.md` with:
- Top 5 HN stories with links
- Vibe Scores (1-5) based on comment sentiment
- Brief sentiment reasoning

## Architecture

3-agent pipeline: **Researcher** (fetches stories) → **Sentiment Analyst** (analyzes comments) → **Editor** (formats output)

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

## Files

| File | Purpose |
|------|---------|
| `hn_farm.py` | Main application |
| `utils/md_converter.py` | Markdown to HTML converter |
| `utils/citation_validator.py` | HN item ID validator |
| `requirements.txt` | Dependencies |
| `output/hn_daily.md` | Generated newsletter |
| `output/hn_daily.html` | HTML version (optional) |
