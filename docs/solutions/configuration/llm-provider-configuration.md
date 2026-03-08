---
problem_type: configuration
component: hn_farm.py
symptoms:
  - Hardcoded provider selection requiring code changes
  - Cryptic errors when API keys are missing
  - Potential for accidental commits with modified settings
date_solved: 2026-03-08
severity: p3
tags: [configuration, error-handling, developer-experience, environment-variables]
related_issues: [003, 022, 023, 024]
commits: [da4e18e, e8b322c]
---

# LLM Provider Configuration and Startup Validation

## Problem Statement

Two related configuration issues in the HN Bot Farm application:

1. **Hardcoded Provider Selection**: The active LLM provider was hardcoded in source code (`active_provider = providers["zai"]`), requiring code modification to switch providers.

2. **Missing API Key Validation**: API keys were loaded via `os.getenv()` but not validated at startup. If keys were missing, the application failed with a cryptic error at LLM instantiation time.

## Symptoms

- Switching LLM providers required editing source code
- Risk of accidental commits with modified provider settings
- Cryptic error messages when environment variables were not set
- No early detection of configuration issues
- Debugging failures could expose sensitive information

## Root Cause Analysis

The original implementation had these issues:

1. **Line 152**: Provider selection was hardcoded:
   ```python
   active_provider = providers["zai"]
   ```

2. **Lines 138-152**: No validation of loaded environment variables:
   ```python
   providers = {
       "zai": {
           "api_key": os.getenv("ZAI_API_KEY"),  # Could be None
           ...
       },
       ...
   }
   ```

This pattern is common in Python applications that use environment variables but fail to validate them early.

## Solution

### Changes Made to `hn_farm.py`

Replace the hardcoded provider selection with environment variable configuration and add startup validation:

```python
# --- LLM Provider Configuration ---
providers = {
    "zai": {
        "api_key": os.getenv("ZAI_API_KEY"),
        "base_url": "https://api.z.ai/api/coding/paas/v4",
        "model": "openai/glm-5"
    },
    "groq": {
        "api_key": os.getenv("GROQ_API_KEY"),
        "base_url": "https://api.groq.com/openai/v1",
        "model": "groq/llama-3.3-70b-versatile"
    }
}

# Select provider from environment variable (023)
provider_name = os.getenv("LLM_PROVIDER", "zai")
if provider_name not in providers:
    raise ValueError(
        f"Unknown LLM provider: '{provider_name}'. "
        f"Available providers: {list(providers.keys())}"
    )
active_provider = providers[provider_name]

# Validate API key for active provider (024)
if not active_provider.get("api_key"):
    raise ValueError(
        f"Missing API key for provider '{provider_name}'. "
        f"Set the {provider_name.upper()}_API_KEY environment variable."
    )
```

### Key Improvements

1. **Environment Variable Selection**: `LLM_PROVIDER` env var with sensible default
2. **Unknown Provider Validation**: Clear error for invalid provider names
3. **API Key Validation**: Fails fast with helpful error message
4. **Clear Error Messages**: Include the specific environment variable name to set

## Verification

### Test Unknown Provider
```bash
$ LLM_PROVIDER=unknown .venv/bin/python -c "import hn_farm"
ValueError: Unknown LLM provider: 'unknown'. Available providers: ['zai', 'groq']
```

### Test Missing API Key
```bash
$ LLM_PROVIDER=zai ZAI_API_KEY= .venv/bin/python -c "import hn_farm"
ValueError: Missing API key for provider 'zai'. Set the ZAI_API_KEY environment variable.
```

### Test Valid Configuration
```bash
$ LLM_PROVIDER=groq GROQ_API_KEY=test_key .venv/bin/python -c "import hn_farm; print(hn_farm.provider_name)"
groq
```

## Prevention Strategies

### 1. Environment Variable Pattern

Always use `os.getenv("VAR_NAME", "default")` with sensible defaults for configuration:

```python
# Good
provider_name = os.getenv("LLM_PROVIDER", "zai")

# Avoid
provider_name = "zai"  # Hardcoded
```

### 2. Fail Fast with Clear Messages

Validate configuration at module load time, not at runtime:

```python
# Good - validates at import time
if not api_key:
    raise ValueError(f"Missing API key. Set {provider.upper()}_API_KEY environment variable.")

# Avoid - fails at runtime with cryptic error
# Let it fail naturally when LLM tries to connect
```

### 3. Use `.env.example` Template

Create a `.env.example` file to document required environment variables:

```bash
# LLM Provider Configuration
LLM_PROVIDER=zai

# API Keys
ZAI_API_KEY=your_zai_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

## Related Issues

- **Issue 003**: API Key Environment Variable Exposure (P1)
- **Issue 022**: Missing `.env.example` file (P3)
- **Issue 023**: Hardcoded Provider Selection (P3)
- **Issue 024**: API Key Startup Validation (P3)

## Code Review Checklist

When reviewing code that uses environment variables:

- [ ] All configuration uses environment variables (not hardcoded values)
- [ ] Sensible defaults provided where appropriate
- [ ] Validation happens at startup (fail fast)
- [ ] Error messages include the specific environment variable name
- [ ] `.env.example` file documents all required variables
- [ ] README.md accurately describes all environment variables

## Resources

- [Python dotenv Best Practices](https://github.com/theskumar/python-dotenv)
- [Twelve-Factor App: Config](https://12factor.net/config)
- CrewAI LLM Documentation: https://docs.crewai.com/concepts/llms
