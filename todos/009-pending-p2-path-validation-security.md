---
status: complete
priority: p2
issue_id: 009
tags: [security, path-traversal, code-review]
dependencies: []
---

# Path Validation Missing (LFI and Arbitrary Write Risks)

## Problem Statement

The `convert_file()` function lacks path validation, allowing symlink-based Local File Inclusion (LFI) and arbitrary file writes to sensitive locations.

## Findings

### Symlink File Disclosure (LFI)
**Location:** `utils/md_converter.py:70-75`

```python
input_file = Path(input_path)
if not input_file.exists():
    raise FileNotFoundError(...)
markdown_text = input_file.read_text(encoding="utf-8")
```

No check for symlinks - attacker can read `/etc/passwd`, SSH keys, etc.

### Arbitrary File Write
**Location:** `utils/md_converter.py:85`

```python
Path(output_path).write_text(html_output, encoding="utf-8")
```

No validation of output path - can write to `/var/www/html/backdoor.html` or overwrite `~/.ssh/authorized_keys`.

## Proposed Solutions

### Option A: Add path validation with allowed directories (Recommended)

**Pros:**
- Comprehensive protection
- Configurable allowlist

**Cons:**
- May limit flexibility
- Requires configuration

**Effort:** Medium
**Risk:** Low

```python
ALLOWED_INPUT_DIRS = [Path.cwd()]
ALLOWED_OUTPUT_DIRS = [Path.cwd() / "output"]

def convert_file(...):
    input_file = Path(input_path).resolve()

    # Reject symlinks
    if input_file.is_symlink():
        raise ValueError("Symlinks are not allowed")

    # Validate input directory
    if not any(input_file.is_relative_to(d) for d in ALLOWED_INPUT_DIRS):
        raise ValueError(f"Input path must be within allowed directories")
    ...
```

### Option B: Simple checks only

**Pros:**
- Minimal code changes
- No configuration needed

**Cons:**
- Less comprehensive
- May not cover all cases

**Effort:** Small
**Risk:** Medium

```python
# Just reject symlinks and existing output files
if input_file.is_symlink():
    raise ValueError("Symlinks are not allowed")
if Path(output_path).exists():
    raise ValueError(f"Output file already exists: {output_path}")
```

## Recommended Action

Implement Option B for now (symlink check + existing file check), consider Option A if used in production.

## Technical Details

**Affected Files:**
- `utils/md_converter.py:70-85`

## Acceptance Criteria

- [ ] Symlink inputs rejected with clear error
- [ ] Output to existing file either rejected or requires explicit flag
- [ ] Tests added for path validation

## Work Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-03-07 | Finding identified | Security review |

## Resources

- OWASP Path Traversal: https://owasp.org/www-community/attacks/Path_Traversal
