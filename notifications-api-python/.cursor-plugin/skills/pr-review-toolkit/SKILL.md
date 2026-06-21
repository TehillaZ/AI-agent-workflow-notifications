---
name: pr-review-toolkit
description: >-
  Run structured PR or pre-push review for this repo using specialized review
  agents (comments, tests, error handling, types, code quality, simplification).
  Use before opening a PR, after significant changes, or when the user asks to
  review changes. Never modify src/providers/ (external vendor APIs).
---

# PR Review Toolkit

## When to use

- Before creating a pull request or pushing to GitHub
- After fixing bugs in `processor.py`, `storage.py`, `main.py`, or `models.py`
- When the user asks for a code review, PR review, or pre-submit check

## Hard rules for this project

- **Do not modify** anything under `src/providers/`
- Follow `AGENTS.md` and `SPEC.md`
- README additions must be written by the candidate without AI

## Review workflow

1. Gather scope: `git diff`, changed files, and user intent.
2. Choose one or more review agents from `.cursor-plugin/agents/`:
   - `code-reviewer` — AGENTS.md compliance, bugs, quality (start here)
   - `pr-test-analyzer` — test gaps and edge cases
   - `silent-failure-hunter` — error handling (especially `processor.py` status mapping)
   - `comment-analyzer` — comment accuracy
   - `type-design-analyzer` — model/data shape design
   - `code-simplifier` — clarity after fixes land
3. Run targeted manual checks from `AGENTS.md`:
   - `GET /notifications`, send-one, send-bulk as relevant
4. Summarize findings: Critical → Important → Notes
5. Fix critical issues before push; re-run affected checks.

## Suggested commands

```bash
git status
git diff
git diff origin/main...HEAD
```

## Output format

- List files reviewed
- Findings grouped by severity with file references
- Explicit note if `src/providers/` was correctly left untouched
