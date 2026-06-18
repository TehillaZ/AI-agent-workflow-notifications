---
name: create-hook
description: >-
  Create or update Cursor hooks for this project. Use when adding automation,
  guarding provider files, gating git push, or changing hook scripts under
  .cursor/hooks/.
---

# Create Hook (project)

This repo uses project hooks in `.cursor/hooks.json` and `.cursor/hooks/*.py`.

## Existing hooks

| Script | Event | Behavior |
|--------|-------|----------|
| `block_provider_edits.py` | `preToolUse` | Deny Write/StrReplace/Delete under `src/providers/` |
| `guard_git_push.py` | `beforeShellExecution` | Ask before `git push` |
| `session_context.py` | `sessionStart` | Inject AGENTS.md / SPEC.md hard rules |

## When adding hooks

1. Prefer **project hooks** (`.cursor/hooks.json`), not user hooks.
2. Use **Python** scripts for Windows compatibility (`py .cursor/hooks/...`).
3. Read JSON from **stdin**; write JSON to **stdout**; exit 0 on success.
4. Use narrow **matchers** on `preToolUse` / `beforeShellExecution` when possible.
5. Test with echo-piped sample JSON before relying on the hook in Cursor.
6. Do not block legitimate work on `processor.py`, `storage.py`, `main.py`, `models.py`, `segmenter.py`.

## Hook output fields

- `preToolUse` / `beforeShellExecution`: `permission` (`allow` | `deny` | `ask`), optional `user_message`, `agent_message`
- `sessionStart`: `additional_context` (string)

## Reference

Follow Cursor hook conventions documented in the built-in create-hook skill. After edits, reload hooks via saving `hooks.json` or **Developer: Reload Window**.
