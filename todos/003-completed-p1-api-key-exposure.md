---
status: completed
priority: p1
issue_id: 003
tags: [code-review, security, secrets]
dependencies: []
updated: 2026-03-08
---

# API Key Environment Variable Exposure

## Problem Statement

API keys are set as global environment variables, potentially exposing them to child processes, logging, and crash reports. The `verbose=True` setting on agents could also log sensitive information.

## Findings

- **Location**: `/workspaces/hn-bot-farm/hn_farm.py:156-160`
- **Severity**: HIGH - Security risk for credential exposure
- **Identified by**: security-sentinel
- **Updated**: 2026-03-08 (line numbers corrected)

### Current Code (lines 154-160):
```python
# CrewAI/LiteLLM standard environment setup
# Note: CrewAI's LLM class requires these env vars for OpenAI-compatible APIs
os.environ["OPENAI_API_KEY"] = active_provider["api_key"]
os.environ["OPENAI_API_BASE"] = active_provider["base_url"]

# Create the LLM instance that your Agents will use
llm = LLM(model=active_provider["model"])
```

### Risks:
1. Environment variables visible in process listings (`ps e`)
2. Can leak through error dumps and crash reports
3. Available to ALL child processes
4. `verbose=True` on agents could log sensitive data

## Proposed Solution

**Pass API Keys Directly to LLM Constructor** (simplified approach)

**Pros**:
- Keys not exposed globally
- Simple one-line change
- No modification to agent configuration needed

**Effort**: Small
**Risk**: Low

```python
# Replace lines 154-160 with:
llm = LLM(
    model=active_provider["model"],
    api_key=active_provider["api_key"],
    base_url=active_provider["base_url"]
)
```

**Note**: The comment about CrewAI requiring env vars is outdated. CrewAI's LLM class accepts `api_key` and `base_url` parameters directly.

## Technical Details

- **Affected Files**: `hn_farm.py`
- **Lines to modify**: 154-160 (remove os.environ calls, update LLM constructor)
- **Lines to delete**: 154-157 (the env var setup and comment)

## Acceptance Criteria

- [x] `os.environ["OPENAI_API_KEY"]` line removed
- [x] `os.environ["OPENAI_API_BASE"]` line removed
- [x] Keys passed directly to LLM constructor
- [x] Verify app still works (run `python hn_farm.py`)
- [x] Verify no API keys in process listings: `ps e | grep -i api_key` returns empty

## Security Verification

After implementation, verify:
```bash
# Run the app
python hn_farm.py &

# Check process environment (should NOT show API keys)
ps e -p $! | grep -i openai

# Should return empty or only show the grep process itself
```

## Work Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-03-07 | Issue identified | Found by security-sentinel |
| 2026-03-08 | Plan updated | Line numbers corrected, simplified to single solution |
| 2026-03-08 | Fix implemented | Removed os.environ calls, passed credentials directly to LLM constructor |

## Resources

- CrewAI LLM documentation: https://docs.crewai.com/concepts/llms
- OWASP Secret Management: https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/09-Testing_for_Weak_Cryptography/04-Testing_for_Weak_Encryption
