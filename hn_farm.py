#!/usr/bin/env python3
"""CrewAI application to fetch Hacker News stories and generate a newsletter."""

import json
import urllib.request
from crewai import Agent, Task, Crew, tool
from crewai_tools import FileWriterTool

# ============================================================================
# PASTE YOUR CUSTOM GROQ/LLM CONFIGURATION DICTIONARY HERE
# Example:
# llm_config = {
#     "model": "groq/llama-3.1-70b-versatile",
#     "api_key": "your-api-key",
# }
# ============================================================================
llm_config = {}


@tool("Fetch HN Stories")
def fetch_hn_stories() -> str:
    """
    Fetch the top 5 current stories from Hacker News.

    Returns:
        A JSON string containing the top 5 stories with id, title, and url.
    """
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
    verbose=True,
    **llm_config
)

newsletter_editor = Agent(
    role="Newsletter Editor",
    goal="Format raw story data into a clean, professional Markdown newsletter",
    backstory=(
        "You are an experienced newsletter editor who transforms raw data "
        "into beautifully formatted, easy-to-read content for tech enthusiasts."
    ),
    tools=[file_writer_tool],
    verbose=True,
    **llm_config
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
