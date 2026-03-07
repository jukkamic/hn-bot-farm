---
status: pending
priority: p3
issue_id: 012
tags: [enhancement, code-review]
dependencies: []
---

# Nice-to-Have Enhancements

## Problem Statement

Several minor improvements that would enhance the utility but aren't critical for functionality.

## Findings

### 1. No Atomic Writes
**Location:** `utils/md_converter.py:85`

Direct write without atomicity - partial writes on crash leave corrupt files.

### 2. External CDN Dependency
**Location:** `utils/md_converter.py:6`

CDN dependency creates availability and supply chain risks. Consider SRI hash.

### 3. No Encoding Error Handling
**Location:** `utils/md_converter.py:75`

`UnicodeDecodeError` on non-UTF8 files has poor context.

### 4. CLI Exit Codes Not Specific
**Location:** `utils/md_converter.py:93-95`

Exit code 1 for all errors - can't distinguish error types.

### 5. No Logging/Verbose Mode
CLI has minimal feedback for debugging.

### 6. Title Derivation Could Be Smarter
**Location:** `utils/md_converter.py:80-81`

Double separators create double spaces; numbers in titles handled oddly.

## Proposed Solutions

### Option A: Implement all as incremental improvements

**Pros:**
- Better user experience
- Better debugging

**Cons:**
- Not urgent
- Scope creep risk

**Effort:** Medium
**Risk:** Low

### Option B: Defer to future work

**Pros:**
- Focus on critical issues first

**Cons:**
- May never happen

**Effort:** None
**Risk:** None

## Recommended Action

Defer P3 items until P1/P2 are resolved. Create follow-up issues if desired.

## Technical Details

**Affected Files:**
- `utils/md_converter.py` (multiple locations)

## Acceptance Criteria

- [ ] Atomic writes with temp file + rename
- [ ] SRI hash on CDN link (or bundle locally)
- [ ] Encoding errors wrapped with context
- [ ] Distinct CLI exit codes
- [ ] Optional verbose logging
- [ ] Improved title derivation

## Work Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-03-07 | Finding identified | Multiple review agents |

## Resources

- SRI Hash Generator: https://www.sitemural.com/sri-hash-generator/
