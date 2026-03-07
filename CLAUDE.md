## Python Environment
Always use the virtual environment's Python when running Python scripts. Prefer running scripts as `.venv/bin/python script.py` over activating virtual environment and then running plain `python` command.

## Git Workflow 
Commit all changes with a good message. For git push operations, provide manual instructions rather than attempting to push directly, as GitHub authentication requires user credentials. You do not have access to git origin.

## CrewAI/Groq/Z.AI
When working with CrewAI and any LLM, validate tool schemas early and test with a simple agent before expanding to multi-agent workflows.
