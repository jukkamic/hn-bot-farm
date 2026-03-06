#!/usr/bin/env python3
"""Fetch and display the top 5 stories from Hacker News."""

import json
import urllib.request
import urllib.error


def fetch_json(url):
    """Fetch JSON data from a URL."""
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read().decode('utf-8'))


def main():
    # Get top story IDs
    top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    story_ids = fetch_json(top_stories_url)

    # Fetch details for top 5 stories
    stories = []
    print("Top 5 Hacker News Stories\n")
    print("-" * 60)

    for i, story_id in enumerate(story_ids[:5], 1):
        story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
        story = fetch_json(story_url)

        title = story.get('title', 'No title')
        url = story.get('url', 'No URL')

        stories.append({
            'id': story_id,
            'title': title,
            'url': url
        })

        print(f"\n{i}. {title}")
        print(f"   URL: {url}")

    print("\n" + "-" * 60)

    # Save to JSON file
    output_file = "hn_stories.json"
    with open(output_file, 'w') as f:
        json.dump(stories, f, indent=2)
    print(f"\nSaved to {output_file}")


if __name__ == "__main__":
    main()
