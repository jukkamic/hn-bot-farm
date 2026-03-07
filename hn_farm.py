#!/usr/bin/env python3
"""CrewAI application to fetch Hacker News stories and generate a newsletter."""

import html
import json
import os
import re
import urllib.error
import urllib.request
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from crewai import Agent, Task, Crew, LLM
from crewai.tools import BaseTool
from crewai_tools import FileWriterTool

load_dotenv()

# --- Pre-compiled Regex Patterns (P3-010) ---
HTML_TAG_PATTERN = re.compile(r'<[^>]+>')
WHITESPACE_PATTERN = re.compile(r'\s+')


# --- Module-level Utility Functions ---
API_TIMEOUT_SECONDS = 10
HN_API_BASE = "https://hacker-news.firebaseio.com/v0"


def fetch_hn_json(url: str, timeout: int = API_TIMEOUT_SECONDS) -> dict[str, Any]:
    """Fetch JSON from Hacker News API with proper timeout.

    Args:
        url: The full URL to fetch from
        timeout: Request timeout in seconds (default: 10)

    Returns:
        Parsed JSON response as dictionary

    Raises:
        urllib.error.URLError: Network connectivity issues
        urllib.error.HTTPError: HTTP error responses
        json.JSONDecodeError: Invalid JSON response
    """
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return json.loads(response.read().decode('utf-8'))


def strip_html(text: str) -> str:
    """Remove HTML tags and decode entities from text.

    Args:
        text: Input text potentially containing HTML

    Returns:
        Clean text with HTML removed and entities decoded
    """
    if not text:
        return ""
    # Remove HTML tags using pre-compiled pattern
    text = HTML_TAG_PATTERN.sub(' ', text)
    # Decode HTML entities
    text = html.unescape(text)
    # Clean up whitespace using pre-compiled pattern
    text = WHITESPACE_PATTERN.sub(' ', text).strip()
    return text


# --- LLM Provider Configuration ---
providers = {
    "zai": {
        "api_key": os.getenv("ZAI_API_KEY"),
        # "base_url": "https://api.z.ai/api/paas/v4", # MUST be paas/v4 for Python/LiteLLM
        "base_url": "https://api.z.ai/api/coding/paas/v4",
        "model": "openai/glm-5"  # Tell LiteLLM to treat Z.ai like OpenAI
    },
    "groq": {
        "api_key": os.getenv("GROQ_API_KEY"),
        "base_url": "https://api.groq.com/openai/v1",
        "model": "groq/llama-3.3-70b-versatile"
    }
}

active_provider = providers["zai"]

# CrewAI/LiteLLM standard environment setup
# Note: CrewAI's LLM class requires these env vars for OpenAI-compatible APIs
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
    description: str = "Fetch the top 5 current stories from Hacker News. Returns a JSON string with id, title, url, kids, score, and by for each story."
    args_schema: type[BaseModel] = FetchHNStoriesInput

    def _run(self, query: str = "") -> str:
        """Fetch the top 5 current stories from Hacker News."""
        # P1-002, P2-004: Use module-level function with timeout
        top_stories_url = f"{HN_API_BASE}/topstories.json"
        story_ids = fetch_hn_json(top_stories_url)

        # Fetch details for top 5 stories
        stories = []
        for story_id in story_ids[:5]:
            story_url = f"{HN_API_BASE}/item/{story_id}.json"
            story = fetch_hn_json(story_url)
            stories.append({
                'id': story_id,
                'title': story.get('title', 'No title'),
                'url': story.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
                'kids': story.get('kids', []),
                'score': story.get('score', 0),
                'by': story.get('by', 'unknown')
            })

        return json.dumps(stories, indent=2)


fetch_hn_stories = FetchHNStoriesTool()


# --- Custom Tool for fetching HN comments ---
class FetchHNCommentsInput(BaseModel):
    """Input schema for fetch_hn_comments."""
    story_id: int = Field(description="The HN story ID")
    comment_ids: list[int] = Field(
        default=[],
        description="List of comment IDs to fetch (will fetch up to 5)"
    )


class FetchHNCommentsTool(BaseTool):
    name: str = "fetch_hn_comments"
    description: str = (
        "Fetch the top comments for a Hacker News story. "
        "Returns comment text (HTML-stripped), author, and metadata. "
        "Use this to analyze community sentiment."
    )
    args_schema: type[BaseModel] = FetchHNCommentsInput

    # P1-001: Fixed mutable default argument bug
    def _run(self, story_id: int, comment_ids: list[int] | None = None) -> str:
        """Fetch up to 5 comments from HN API."""
        # P1-001: Handle None for mutable default
        if comment_ids is None:
            comment_ids = []

        comments = []
        errors = []
        max_comments = 5

        for comment_id in comment_ids[:max_comments]:
            try:
                url = f"{HN_API_BASE}/item/{comment_id}.json"
                # P2-004: Use module-level function with timeout
                comment_data = fetch_hn_json(url)

                if comment_data is None or comment_data.get('deleted') or comment_data.get('dead'):
                    continue

                text = comment_data.get('text', '')
                if not text:
                    continue

                comments.append({
                    'id': comment_id,
                    'text': strip_html(text),  # P3-010: Use module-level function
                    'by': comment_data.get('by', 'unknown'),
                    'time': comment_data.get('time', 0)
                })

            # P2-005: Narrowed exception handling to specific types
            except (urllib.error.URLError, urllib.error.HTTPError) as e:
                errors.append(f"Error fetching comment {comment_id}: Network error")
            except json.JSONDecodeError:
                errors.append(f"Error fetching comment {comment_id}: Invalid response")
            except TimeoutError:
                errors.append(f"Error fetching comment {comment_id}: Request timed out")

        result = {
            'story_id': story_id,
            'comments': comments,
            'comments_found': len(comments),
            'errors': errors
        }

        return json.dumps(result, indent=2)


fetch_hn_comments = FetchHNCommentsTool()


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

sentiment_analyst = Agent(
    role="Sentiment Analyst",
    goal="Analyze HN comments and assign Vibe Scores to stories",
    backstory=(
        "You are an expert at reading the room. You analyze online discussions "
        "to understand community sentiment. You assign scores on a 1-5 scale "
        "where 1=Very Negative, 2=Negative, 3=Neutral, 4=Positive, 5=Very Positive."
    ),
    tools=[fetch_hn_comments],
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
    description=(
        "Fetch the top 5 current stories from Hacker News using the fetch_hn_stories tool. "
        "Return the EXACT JSON output from the tool without modification. "
        "Do NOT summarize or reformat - pass through the raw JSON which includes id, title, url, kids, score, and by fields."
    ),
    expected_output="The exact JSON list returned by the tool, containing 5 stories with id, title, url, kids (comment IDs), score, and by fields. Do not summarize.",
    agent=tech_researcher
)

sentiment_task = Task(
    description=(
        "Analyze the sentiment of comments for each story. "
        "For each story, use the fetch_hn_comments tool with the story's ID "
        "and the first 5 comment IDs from its 'kids' field. "
        "Assign a Vibe Score (1-5) based on the overall sentiment of the comments. "
        "If a story has no comments, assign 'N/A' with reason 'No comments available'.\n\n"
        "Vibe Score Scale:\n"
        "- 1: Very Negative (hostile, dismissive, critical)\n"
        "- 2: Negative (skeptical, concerned, critical)\n"
        "- 3: Neutral (mixed, factual, indifferent)\n"
        "- 4: Positive (interested, approving, supportive)\n"
        "- 5: Very Positive (enthusiastic, praiseworthy, excited)\n\n"
        "Return a JSON list with each story including: id, title, url, vibe_score, vibe_label, vibe_reasoning, comments_analyzed."
    ),
    expected_output="A JSON list of stories with vibe scores and reasoning.",
    agent=sentiment_analyst,
    context=[research_task]
)

edit_task = Task(
    description=(
        "Take the story data with vibe scores from the context and format it into a professional "
        "Markdown newsletter.\n\n"
        "IMPORTANT: The context contains a JSON list from the sentiment analyst. Each story in that JSON has:\n"
        "- id, title, url\n"
        "- vibe_score (a number 1-5, or 'N/A')\n"
        "- vibe_label (e.g., 'Very Positive', 'Positive', 'Neutral', etc.)\n"
        "- vibe_reasoning (brief explanation)\n"
        "- comments_analyzed (number)\n\n"
        "You MUST extract these vibe_score and vibe_label values from the context JSON and include them in the output.\n\n"
        "Create a file at 'output/hn_daily.md' with:\n"
        "- A header with today's date\n"
        "- A brief intro\n"
        "- Numbered list of stories with:\n"
        "  * Clickable title link\n"
        "  * Vibe score in format '*Vibe: X/5 Label*' (use the actual vibe_score and vibe_label from context)\n"
        "  * Brief reasoning (use vibe_reasoning from context)\n"
        "  * One-line description\n"
        "- A closing section\n\n"
        "Example format for each story:\n"
        "1. **[Title](URL)** *Vibe: 5/5 Very Positive*\n"
        "   Comments show excitement about this discovery.\n\n"
        "Use the FileWriterTool with directory='output' and filename='hn_daily.md'."
    ),
    expected_output="A confirmation that output/hn_daily.md has been created with formatted content including the actual vibe scores from the context.",
    agent=newsletter_editor,
    context=[sentiment_task]
)

# Assemble Crew
crew = Crew(
    agents=[tech_researcher, sentiment_analyst, newsletter_editor],
    tasks=[research_task, sentiment_task, edit_task],
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
