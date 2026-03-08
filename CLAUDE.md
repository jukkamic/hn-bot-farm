## Python Environment
Always use the virtual environment's Python when running Python scripts. Prefer running scripts as `.venv/bin/python script.py` over activating virtual environment and then running plain `python` command.

## Git Workflow 
Commit all changes with a good message. For git push operations, provide manual instructions rather than attempting to push directly, as GitHub authentication requires user credentials. You do not have access to git origin.

## CrewAI/Groq/Z.AI
When working with CrewAI and any LLM, validate tool schemas early and test with a simple agent before expanding to multi-agent workflows.

## Registered Skills

### Skill Markdown Converter: 
Located at utils/md_to_html.py.

Usage: Run via ./.venv/bin/python utils/md_to_html.py <input.md> <output.html>.

Policy: Always run this skill after any task that updates hn_daily.md.

### Skill: Verified Citations
Whenever extracting sentiment or summaries, always require the agent to provide the direct source URL for any 'representative' example. Never allow the agent to 'search' for a link after the fact.