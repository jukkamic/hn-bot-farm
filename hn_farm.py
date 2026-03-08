#!/usr/bin/env python3
"""CrewAI application to fetch Hacker News stories and generate a newsletter."""

import asyncio
import html
import json
import os
import re
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
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


# --- Module-level Configuration ---
API_TIMEOUT_SECONDS = 10
HN_API_BASE = "https://hacker-news.firebaseio.com/v0"
MAX_WORKERS = 10  # Max concurrent connections


# --- Module-level Utility Functions ---
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


def fetch_hn_item(item_id: int) -> dict[str, Any] | None:
    """Fetch a single HN item (story or comment) by ID.

    Args:
        item_id: The HN item ID

    Returns:
        Item data dict or None if fetch failed
    """
    try:
        url = f"{HN_API_BASE}/item/{item_id}.json"
        return fetch_hn_json(url)
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError):
        return None


def fetch_items_parallel(item_ids: list[int], max_workers: int = MAX_WORKERS) -> list[dict[str, Any] | None]:
    """Fetch multiple HN items in parallel using ThreadPoolExecutor.

    P2-007: Parallel fetching reduces latency from O(n) to O(1) for API calls.

    Args:
        item_ids: List of HN item IDs to fetch
        max_workers: Maximum concurrent threads

    Returns:
        List of item data dicts (same order as input IDs), None for failed fetches
    """
    results = {item_id: None for item_id in item_ids}

    with ThreadPoolExecutor(max_workers=min(max_workers, len(item_ids))) as executor:
        # Submit all fetch tasks
        future_to_id = {executor.submit(fetch_hn_item, item_id): item_id for item_id in item_ids}

        # Collect results as they complete
        for future in as_completed(future_to_id):
            item_id = future_to_id[future]
            try:
                results[item_id] = future.result()
            except Exception:
                results[item_id] = None

    # Return in original order
    return [results[item_id] for item_id in item_ids]


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


def escape_markdown(text: str) -> str:
    """Escape Markdown special characters to prevent injection.

    Args:
        text: Input text potentially containing Markdown syntax

    Returns:
        Text with Markdown special characters escaped
    """
    if not text:
        return ""
    # Escape characters that could break Markdown formatting or inject links
    for char in ['[', ']', '(', ')']:
        text = text.replace(char, f'\\{char}')
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
        # Get top story IDs (single call)
        top_stories_url = f"{HN_API_BASE}/topstories.json"
        story_ids = fetch_hn_json(top_stories_url)[:5]

        # P2-007: Fetch all 5 stories in parallel instead of sequentially
        stories_data = fetch_items_parallel(story_ids)

        # Build stories list
        stories = []
        for i, story in enumerate(stories_data):
            if story is None:
                continue
            story_id = story_ids[i]
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

        max_comments = 5
        ids_to_fetch = comment_ids[:max_comments]

        # P2-007: Fetch all comments in parallel instead of sequentially
        comments_data = fetch_items_parallel(ids_to_fetch)

        comments = []
        errors = []

        for i, comment_data in enumerate(comments_data):
            comment_id = ids_to_fetch[i]

            if comment_data is None:
                errors.append(f"Error fetching comment {comment_id}: Fetch failed")
                continue

            if comment_data.get('deleted') or comment_data.get('dead'):
                continue

            text = comment_data.get('text', '')
            if not text:
                continue

            comments.append({
                'id': comment_id,
                'text': strip_html(text),
                'by': comment_data.get('by', 'unknown'),
                'time': comment_data.get('time', 0)
            })

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
        "and the first 5 comment IDs from its 'kids' field.\n\n"

        "Vibe Score Scale:\n"
        "- 1: Very Negative (hostile, dismissive, critical)\n"
        "- 2: Negative (skeptical, concerned, critical)\n"
        "- 3: Neutral (mixed, factual, indifferent)\n"
        "- 4: Positive (interested, approving, supportive)\n"
        "- 5: Very Positive (enthusiastic, praiseworthy, excited)\n\n"

        "SINGLE-PASS ANALYSIS:\n"
        "As you read each comment, decide if it's NOTABLE. A notable comment:\n"
        "- Perfectly represents the overall mood, OR\n"
        "- Expresses a specific viewpoint worth highlighting, OR\n"
        "- Is particularly well-phrased or memorable\n\n"

        "OUTPUT STRUCTURE:\n"
        "1. lead_quote: The SINGLE MOST representative comment\n"
        "   - comment_id: the HN comment ID\n"
        "   - text: a 1-2 sentence excerpt (this will be the blockquote)\n\n"

        "2. notable_comments: 1-2 ADDITIONAL comments worth linking\n"
        "   - comment_id: the HN comment ID\n"
        "   - quote_snippet: a 2-4 word phrase YOU WILL USE in your reasoning\n"
        "   - context: brief note why this comment is notable\n\n"

        "3. vibe_reasoning: Your analysis text that MUST INCLUDE the quote_snippets\n"
        "   - When you mention a notable comment, use its exact quote_snippet\n"
        "   - Example: If quote_snippet is 'nostalgic memories', write 'shared nostalgic memories'\n\n"

        "CRITICAL: Your vibe_reasoning must contain the exact quote_snippet phrases.\n"
        "The editor will search for these phrases and convert them to links.\n\n"

        "Return a JSON list with each story including:\n"
        "- id, title, url\n"
        "- vibe_score, vibe_label, vibe_reasoning\n"
        "- lead_quote: {comment_id, text}\n"
        "- notable_comments: [{comment_id, quote_snippet, context}]\n"
        "- comments_analyzed\n\n"

        "If a story has no comments, assign vibe_score='N/A' with empty lead_quote and notable_comments."
    ),
    expected_output="A JSON list of stories with vibe scores, lead quotes, and notable comments.",
    agent=sentiment_analyst,
    context=[research_task]
)

edit_task = Task(
    description=(
        "Take the story data from the context and format it into a professional "
        "Markdown newsletter with comment links.\n\n"

        "INPUT STRUCTURE (from sentiment analyst):\n"
        "- id, title, url\n"
        "- vibe_score, vibe_label, vibe_reasoning\n"
        "- lead_quote: {comment_id, text}\n"
        "- notable_comments: [{comment_id, quote_snippet, context}]\n\n"

        "SECURITY - Markdown Escaping:\n"
        "Before embedding quote text in Markdown links, escape special characters:\n"
        "- Replace '[' with '\\\\[' and ']' with '\\\\]'\n"
        "- Replace '(' with '\\\\(' and ')' with '\\\\)'\n"
        "This prevents Markdown injection from comment text.\n\n"

        "LINK FORMATTING:\n"
        "1. Lead Quote (always first, as blockquote):\n"
        "   > \"[escaped_lead_quote.text](https://news.ycombinator.com/item?id=lead_quote.comment_id)\"\n\n"

        "2. Notable Comments (string replacement in reasoning):\n"
        "   - Find each quote_snippet in vibe_reasoning\n"
        "   - Replace with: [quote_snippet](https://news.ycombinator.com/item?id=comment_id)\n"
        "   - SKIP if comment_id matches lead_quote.comment_id (no duplicates)\n\n"

        "FORMAT FOR EACH STORY:\n"
        "1. **[Title](URL)** *Vibe: X/5 Label*\n\n"
        "   > \"[lead_quote with link]\"\n\n"
        "   [vibe_reasoning with notable comment links embedded]\n\n"

        f"Create a file at 'output/hn_daily.md' with:\n"
        f"- Header: 'Hacker News Daily Digest - {{DATE}}'\n"
        "- Brief intro\n"
        "- Numbered list of stories\n"
        "- Closing section\n\n"

        "Use the FileWriterTool with directory='output' and filename='hn_daily.md'."
    ),
    expected_output="Confirmation that output/hn_daily.md has been created with lead quotes and comment links.",
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
    # Compute date at execution time, not import time (P1-013)
    current_date = datetime.now().strftime('%A %B %d, %Y')
    edit_task.description = edit_task.description.replace("{DATE}", current_date)

    result = crew.kickoff()
    print("\n" + "=" * 60)
    print("Crew Execution Complete!")
    print("=" * 60)
    print(result)


if __name__ == "__main__":
    main()
