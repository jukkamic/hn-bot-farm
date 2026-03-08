## Environment & Execution
Always use the virtual environment's Python when running scripts.

Prefer running scripts via absolute or relative paths (e.g., .venv/bin/python script.py) rather than activating the virtual environment first.

## Git Workflow
Commit all changes with clear, descriptive commit messages.

No Remote Pushes: You do not have write access to the git remote. Do not attempt to git push. Instead, provide manual instructions for the user to push after a successful commit.

## AI & Agent Architecture (CrewAI/Z.ai/Groq)
Validate tool schemas early.

Always test with a simple, single agent before expanding to multi-agent workflows.

## Global Triggers

Analysis Trigger: Whenever the user asks for "Vibes" or "Sentiment Analysis," automatically invoke the evidence-based-analysis skill to ensure citations are single-pass and validated.