---
status: complete
priority: p1
issue_id: 008
tags: [security, dos, performance, code-review]
dependencies: []
---

# No Input Size Validation (DoS Risk)

## Problem Statement

The converter has no maximum size limit on input markdown. Large inputs can cause memory exhaustion and denial of service, especially in containerized environments with limited memory.

## Findings

**Location:** `utils/md_converter.py:39-40, 75`

```python
# Only validates empty input
if not markdown_text:
    raise ValueError("markdown_text cannot be empty")

# Entire file read into memory
markdown_text = input_file.read_text(encoding="utf-8")
```

**Impact:**
- 10MB markdown file → ~30MB peak memory (3 copies)
- 100MB file → ~300MB peak memory
- Risk of `MemoryError` in memory-constrained containers (256MB limit)

**DoS Vectors:**
- Malformed markdown with deeply nested structures
- Recursive patterns causing exponential regex processing
- Memory exhaustion attacks

## Proposed Solutions

### Option A: Add size limit constant (Recommended)

**Pros:**
- Simple implementation
- Prevents DoS attacks
- Configurable limit

**Cons:**
- May reject legitimate large files
- Requires documentation

**Effort:** Small
**Risk:** Low

```python
# Module-level constant
MAX_INPUT_SIZE = 10 * 1024 * 1024  # 10MB

def convert_markdown_to_html(markdown_text: str, ...) -> str:
    if len(markdown_text) > MAX_INPUT_SIZE:
        raise ValueError(f"Input exceeds maximum size of {MAX_INPUT_SIZE} bytes")
    ...

def convert_file(...):
    file_size = input_file.stat().st_size
    if file_size > MAX_INPUT_SIZE:
        raise ValueError(f"File exceeds maximum size of {MAX_INPUT_SIZE} bytes")
    ...
```

### Option B: Streaming/chunked processing

**Pros:**
- No arbitrary limits
- Better for very large files

**Cons:**
- Complex implementation
- May not work with all markdown features

**Effort:** Large
**Risk:** Medium

## Recommended Action

Implement Option A - add size limit with clear error message.

## Technical Details

**Affected Files:**
- `utils/md_converter.py` (add constant and validation)
- `utils/test_converter.py` (add size limit test)

## Acceptance Criteria

- [ ] `MAX_INPUT_SIZE` constant defined (suggested: 10MB)
- [ ] String input length checked before processing
- [ ] File size checked before reading
- [ ] Clear error message when limit exceeded
- [ ] Test case for oversized input

## Work Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-03-07 | Finding identified | Security and performance reviews |

## Resources

- Related: Performance oracle findings on memory usage
