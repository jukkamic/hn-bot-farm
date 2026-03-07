---
status: pending
priority: p1
issue_id: 003
tags: [code-review, security, secrets]
dependencies: []
---

# API Key Environment Variable Exposure

## Problem Statement

API keys are set as global environment variables, potentially exposing them to child processes, logging, and crash reports. The `verbose=True` setting on agents could also log sensitive information.

## Findings

- **Location**: `/workspaces/hn-bot-farm/hn_farm.py:33-34`
- **Severity**: HIGH - Security risk for credential exposure
- **Identified by**: security-sentinel

### Current Code:
```python
os.environ["OPENAI_API_KEY"] = active_provider["api_key"]
os.environ["OPENAI_API_BASE"] = active_provider["base_url"]
```

### Risks:
1. Environment variables visible in process listings (`ps e`)
2. Can leak through error dumps and crash reports
3. Available to ALL child processes
4. `verbose=True` on agents could log sensitive data

## Proposed Solutions

### Solution 1: Pass API Keys Directly to LLM (Recommended)
**Pros**: Keys not exposed globally
**Cons**: May require CrewAI LLM configuration changes
**Effort**: Small
**Risk**: Low

```python
llm = LLM(
    model=active_provider["model"],
    api_key=active_provider["api_key"],
    base_url=active_provider["base_url"]
)
```

### Solution 2: Use Context Manager for Temporary Env Vars
**Pros**: Scopes exposure, still works if library requires env vars
**Cons**: More complex, still temporary exposure
**Effort**: Medium
**Risk**: Medium

```python
@contextlib.contextmanager
def temporary_env(key, value):
    old_value = os.environ.get(key)
    os.environ[key] = value
    try:
        yield
    finally:
        if old_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = old_value
```

## Technical Details

- **Affected Files**: `hn_farm.py`
- **Lines**: 33-34, 174, 187, 199 (verbose=True)

## Acceptance Criteria

- [ ] API keys not set in global os.environ
- [ ] Keys passed directly to LLM configuration
- [ ] No credential leakage in logs with verbose=True
- [ ] Verify no keys in process listings

## Work Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-03-07 | Issue identified | Found by security-sentinel |

## Resources

- OWASP: https://owasp.org/www-community/vulnerabilities/Information_exposure_through_query_strings_in_GET_request
