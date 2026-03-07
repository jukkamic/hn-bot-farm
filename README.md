# hn-bot-farm

CrewAI application that fetches top Hacker News stories, analyzes comment sentiment, and generates a Markdown newsletter with "Vibe Scores".

## Quick Start

### Requirements
- VS Code with Dev Containers extension
- Docker Desktop (or compatible runtime)

### Setup

1. Open in VS Code → it should prompt to "Reopen in Container"
   - If not: `Ctrl+Shift+P` → "Dev Containers: Reopen in Container"
2. Copy `.env example` to `.env` and add your API keys
3. Run: `python hn_farm.py`

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `ZAI_API_KEY` | Z.ai GLM-5 model (default provider) |
| `GROQ_API_KEY` | Groq Llama model (alternative) |

## Switch LLM Provider

Edit `hn_farm.py` line ~84:

```python
active_provider = providers["zai"]  # Change to "groq" to use Groq
```

## Output

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
