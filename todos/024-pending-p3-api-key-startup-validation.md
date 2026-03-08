---
status: completed
priority: p3
issue_id: "024"
tags: [code-review, error-handling, developer-experience]
dependencies: []
---

# Problem Statement

API keys are loaded via `os.getenv()` but not validated at startup. If keys are missing, the application fails with a cryptic error at LLM instantiation time rather than a clear configuration error.

## Findings

**Location:** `hn_farm.py` lines 138-152

**Current Code:**
```python
providers = {
    "zai": {
        "api_key": os.getenv("ZAI_API_KEY"),  # Could be None
        "base_url": "https://api.z.ai/api/coding/paas/v4",
        "model": "openai/glm-5"
    },
    "groq": {
        "api_key": os.getenv("GROQ_API_KEY"),  # Could be None
        ...
    }
}
```

**Issues:**
1. Application fails with cryptic error if env vars not set
2. No early detection of configuration issues
3. Debugging the failure might expose sensitive information

**Source:** security-sentinel and kieran-python-reviewer

## Proposed Solutions

### Solution 1: Startup Validation Function (Recommended)
**Approach:** Add validation function that runs at module load.

```python
def validate_provider_config(provider_name: str, config: dict) -> None:
    """Validate provider configuration, raising clear errors for missing keys."""
    if not config.get("api_key"):
        raise ValueError(
            f"Missing API key for provider '{provider_name}'. "
            f"Set the {provider_name.upper()}_API_KEY environment variable."
        )
    if not config.get("base_url"):
        raise ValueError(f"Missing base_url for provider '{provider_name}'")

# Call during initialization
for name, config in providers.items():
    validate_provider_config(name, config)
```

**Pros:** Fail fast with clear error message, easy to debug
**Cons:** Adds code
**Effort:** Small
**Risk:** Low

### Solution 2: Validate Only Active Provider
**Approach:** Only validate the provider being used.

```python
api_key = active_provider.get("api_key")
if not api_key:
    raise ValueError("Missing API key. Set the appropriate environment variable.")
```

**Pros:** Simpler, validates only what's needed
**Cons:** Other providers not validated (may fail later if switched)
**Effort:** Small
**Risk:** Low

### Solution 3: Lazy Validation
**Approach:** Validate on first use of LLM.

**Pros:** Delays error until needed
**Cons:** Error occurs deeper in call stack
**Effort:** Medium
**Risk:** Low

## Recommended Action

Use Solution 2 - Validate only the active provider at startup. Simple, focused, provides clear error messages.

## Technical Details

**Affected Files:** `hn_farm.py` (after line 152)
**Database Changes:** None

## Acceptance Criteria

- [x] Add validation for active provider API key
- [x] Raise clear ValueError with environment variable name
- [x] Test with missing API key (import test passed)

## Work Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-03-08 | Issue identified | Code review of commit e8b322c |

## Resources

- Commit: e8b322c (API key security fix)
