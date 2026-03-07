---
title: Plan vs Work Phase Separation
type: workflow
status: completed
date: 2026-03-07
affected_files:
  - docs/plans/2026-03-07-fix-current-date-in-newsletter.md
tags:
  - workflow
  - planning
  - git-branches
  - compound-engineering
---

# Plan vs Work Phase Separation

## Problem Statement

During the `/ce:plan` workflow, the user provided clarifying comments about the plan (date format requirements). Instead of pausing for user approval of the plan, the system proceeded directly to implementation. This caused the commit to be made on `main` instead of a feature branch, requiring post-hoc git manipulation to fix.

## Root Cause

User comments during the planning phase were interpreted as plan refinement, not as the planning phase still being active. The workflow transitioned to implementation without explicit user approval.

## Impact

- Commit landed on `main` branch instead of a feature branch
- Required manual git operations to create feature branch retroactively:
  ```bash
  git branch fix/newsletter-dynamic-date   # Create branch from current commit
  git reset --hard HEAD~1                   # Reset main to previous commit
  git checkout fix/newsletter-dynamic-date  # Switch to feature branch
  ```

## Solution: Workflow Phase Separation

### Planning Phase (`/ce:plan`)

The planning phase MUST:

1. **Accept user comments as plan refinement** - User feedback improves the plan
2. **Pause after plan completion** - Present options, wait for user choice
3. **NOT implement** - No code changes, no commits
4. **Present explicit options** including:
   - "Start /ce:work" to begin implementation
   - "Review and refine" to iterate on the plan
   - Other modifications

### Work Phase (`/ce:work`)

The work phase MUST:

1. **Start from an approved plan** - User explicitly chose to proceed
2. **Create a feature branch first** - Never commit to main/master
3. **Implement the plan** - Make code changes
4. **Commit on feature branch** - Ready for PR

### Key Principle

**User comments during planning = still in planning phase**

Even if the user provides detailed requirements or corrections, this is plan refinement, not approval to proceed. The system must wait for explicit "Start /ce:work" or equivalent confirmation.

## Prevention Strategies

### For the System

1. **After plan file is written**: Always present options via AskUserQuestion
2. **Do not auto-proceed to implementation** based on plan refinement
3. **Check current branch** before any commit - ensure not on main/master
4. **Present branch options** at start of work phase

### For the User

1. **Review plan options** after planning completes
2. **Explicitly select "Start /ce:work"** to begin implementation
3. **Verify branch** before approving commits

## Git Recovery Pattern

When commits accidentally land on main:

```bash
# 1. Create feature branch from current (wrong) commit
git branch <feature-branch-name>

# 2. Reset main to previous commit
git reset --hard HEAD~1

# 3. Switch to feature branch
git checkout <feature-branch-name>

# 4. Verify
git log --oneline -3
git branch -vv
```

## Related

- Plan file: `docs/plans/2026-03-07-fix-current-date-in-newsletter.md`
- Workflow commands: `/ce:plan`, `/ce:work`
