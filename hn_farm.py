#!/usr/bin/env python3
"""CrewAI application to fetch Hacker News stories and generate a newsletter."""

import os
import json
import urllib.request
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from crewai import Agent, Task, Crew, LLM
from crewai.tools import BaseTool
from crewai_tools import FileWriterTool

load_dotenv()

# --- LLM Provider Configuration ---
providers = {
    "zai": {
        "api_key": os.getenv("ZAI_API_KEY"),
        # "base_url": "https://api.z.ai/api/paas/v4", # MUST be paas/v4 for Python/LiteLLM
        "base_url": "https://api.z.ai/api/coding/paas/v4",
        "model": "openai/glm-5" # Tell LiteLLM to treat Z.ai like OpenAI
    },
    "groq": {
        "api_key": os.getenv("GROQ_API_KEY"),
        "base_url": "https://api.groq.com/openai/v1",
        "model": "groq/llama-3.3-70b-versatile"
    }
}

active_provider = providers["zai"]

# CrewAI/LiteLLM standard environment setup
os.environ["OPENAI_API_KEY"] = active_provider["api_key"]
os.environ["OPENAI_API_BASE"] = active_provider["base_url"]

# Create the LLM instance that your Agents will use
llm = LLM(model=active_provider["model"])

# --- Custom Tool with explicit schema (fixes Groq compatibility) ---
class FetchHNStoriesInput(BaseModel):
    """Input schema for fetch_hn_stories."""
    query: str = Field(
        default="", description="No parameters needed - leave empty")


class FetchHNStoriesTool(BaseTool):
    name: str = "fetch_hn_stories"
    description: str = "Fetch the top 5 current stories from Hacker News. Returns a JSON string with id, title, and url for each story."
    args_schema: type[BaseModel] = FetchHNStoriesInput

    def _run(self, query: str = "") -> str:
        """Fetch the top 5 current stories from Hacker News."""
        def fetch_json(url):
            with urllib.request.urlopen(url) as response:
                return json.loads(response.read().decode('utf-8'))

        # Get top story IDs
        top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        story_ids = fetch_json(top_stories_url)

        # Fetch details for top 5 stories
        stories = []
        for story_id in story_ids[:5]:
            story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
            story = fetch_json(story_url)
            stories.append({
                'id': story_id,
                'title': story.get('title', 'No title'),
                'url': story.get('url', 'No URL')
            })

        return json.dumps(stories, indent=2)


fetch_hn_stories = FetchHNStoriesTool()


# Initialize tools
file_writer_tool = FileWriterTool()

# Define Agents
tech_researcher = Agent(
    role="Tech Researcher",
    goal="Fetch the top 5 trending stories from Hacker News",
    backstory=(
        "You are a skilled tech researcher who specializes in finding "
        "the most relevant and trending tech news from Hacker News."
    ),
    tools=[fetch_hn_stories],
    llm=llm,
    verbose=True
)

newsletter_editor = Agent(
    role="Newsletter Editor",
    goal="Format raw story data into a clean, professional Markdown newsletter",
    backstory=(
        "You are an experienced newsletter editor who transforms raw data "
        "into beautifully formatted, easy-to-read content for tech enthusiasts."
    ),
    tools=[file_writer_tool],
    llm=llm,
    verbose=True
)

# Define Tasks
research_task = Task(
    description="Fetch the top 5 current stories from Hacker News using the fetch_hn_stories tool.",
    expected_output="A JSON list of 5 stories with their titles and URLs.",
    agent=tech_researcher
)

edit_task = Task(
    description=(
        "Take the raw Hacker News story data and format it into a professional "
        "Markdown newsletter. Create a file called 'hn_daily.md' with:\n"
        "- A header with today's date\n"
        "- A brief intro\n"
        "- Numbered list of stories with clickable links\n"
        "- A closing section\n\n"
        "Use the FileWriterTool to save the file."
    ),
    expected_output="A confirmation that hn_daily.md has been created with formatted content.",
    agent=newsletter_editor
)

# Assemble Crew
crew = Crew(
    agents=[tech_researcher, newsletter_editor],
    tasks=[research_task, edit_task],
    memory=False,
    verbose=True
)


def main():
    """Run the CrewAI application."""
    result = crew.kickoff()
    print("\n" + "=" * 60)
    print("Crew Execution Complete!")
    print("=" * 60)
    print(result)


if __name__ == "__main__":
    main()
