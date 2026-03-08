---
status: completed
priority: p3
issue_id: "023"
tags: [code-review, configuration, flexibility]
dependencies: []
---

# Problem Statement

The active LLM provider is hardcoded in source code (`active_provider = providers["zai"]`) rather than being configurable via environment variable. This requires code modification to switch providers.

## Findings

**Location:** `hn_farm.py` line 152

**Current Code:**
```python
active_provider = providers["zai"]
```

**Issues:**
1. Requires code modification to switch providers
2. Could lead to accidental commits with modified provider settings
3. Not a direct security vulnerability but affects operational security
4. Less flexible for testing different providers

**Source:** security-sentinel (Low Severity Finding)

## Proposed Solutions

### Solution 1: Environment Variable Configuration (Recommended)
**Approach:** Use environment variable to select provider.

```python
provider_name = os.getenv("LLM_PROVIDER", "zai")
if provider_name not in providers:
    raise ValueError(f"Unknown provider: {provider_name}. Available: {list(providers.keys())}")
active_provider = providers[provider_name]
```

**Pros:** No code changes needed to switch, testable, standard pattern
**Cons:** One more environment variable
**Effort:** Small
**Risk:** Low

### Solution 2: Command Line Argument
**Approach:** Add CLI argument for provider selection.

```python
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--provider", default="zai")
args = parser.parse_args()
active_provider = providers[args.provider]
```

**Pros:** Explicit per-run selection
**Cons:** More complex, requires CLI changes
**Effort:** Medium
**Risk:** Low

### Solution 3: Keep As-Is
**Approach:** Document that provider selection requires code change.

**Pros:** No code changes needed
**Cons:** Less flexible, potential for accidental commits
**Effort:** None
**Risk:** None

## Recommended Action

Use Solution 1 - Add `LLM_PROVIDER` environment variable with "zai" as default. Simple, standard pattern, improves flexibility.

## Technical Details

**Affected Files:** `hn_farm.py` (line 152)
**Database Changes:** None

## Acceptance Criteria

- [x] Add `LLM_PROVIDER` environment variable
- [x] Add validation for unknown providers
- [ ] Update `.env.example` with new variable (blocked by permission settings)
- [x] Default to "zai" if not set

## Work Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-03-08 | Issue identified | Code review of commit e8b322c |

## Resources

- Commit: e8b322c (API key security fix)
