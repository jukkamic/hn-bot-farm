---
review_agents:
  - kieran-python-reviewer
  - security-sentinel
  - performance-oracle
---

# Code Review Context

This is a Python CrewAI application that generates Hacker News newsletters.

## Current Review Target
Branch: `feat/sentiment-analyst-agent`
Feature: Add Sentiment Analyst agent with Vibe Scores

## Key Areas to Review
1. **New Tool**: `FetchHNCommentsTool` - fetches and processes HN comments
2. **New Agent**: `sentiment_analyst` - analyzes comment sentiment
3. **New Task**: `sentiment_task` - orchestrates sentiment analysis
4. **Updated workflow**: 3-agent pipeline (Researcher -> Sentiment Analyst -> Editor)
