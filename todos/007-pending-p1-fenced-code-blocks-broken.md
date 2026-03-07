---
status: complete
priority: p1
issue_id: 007
tags: [bug, code-quality, code-review]
dependencies: []
---

# Fenced Code Blocks Not Rendering Correctly

## Problem Statement

The `extras=["all"]` flag in markdown2 does not properly enable fenced code block support. Fenced code blocks render as inline `<code>` wrapped in `<p>` tags instead of proper `<pre><code class="language-python">` blocks.

## Findings

**Location:** `utils/md_converter.py:43`

```python
html_content = markdown2.markdown(markdown_text, extras=["all"])
```

**Evidence:** `utils/test_output.html:22-25`
```html
<p><code>python
def hello():
    print("Hello, World!")
</code></p>
```

This is incorrect - fenced code blocks should render as:
```html
<pre><code class="language-python">def hello():
    print("Hello, World!")
</code></pre>
```

**Root Cause:** `markdown2`'s `"all"` extra does not include `fenced-code-blocks` by default. The extra must be explicitly listed.

## Proposed Solutions

### Option A: Explicitly list required extras (Recommended)

**Pros:**
- Clear what extras are enabled
- Better performance (only needed extras)
- Fixes the bug directly

**Cons:**
- May miss some extras users expect

**Effort:** Small
**Risk:** Low

```python
EXTRA_EXTRAS = [
    "fenced-code-blocks",
    "tables",
    "code-friendly",
    "cuddled-lists",
]

html_content = markdown2.markdown(markdown_text, extras=EXTRA_EXTRAS)
```

### Option B: Combine "all" with fenced-code-blocks

**Pros:**
- Maximum compatibility

**Cons:**
- Performance overhead from unused extras
- Still may not work correctly

**Effort:** Small
**Risk:** Medium

## Recommended Action

Implement Option A - explicitly list the extras we need.

## Technical Details

**Affected Files:**
- `utils/md_converter.py:43`
- `utils/test_converter.py` (add test for fenced code blocks)

## Acceptance Criteria

- [ ] Fenced code blocks render as `<pre><code>` not `<p><code>`
- [ ] Language class is preserved (e.g., `class="language-python"`)
- [ ] Test added that verifies `<pre>` tag in output for fenced blocks
- [ ] Existing tests still pass

## Work Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-03-07 | Finding identified | Code review by kieran-python-reviewer |

## Resources

- markdown2 extras: https://github.com/trentm/python-markdown2#extras
