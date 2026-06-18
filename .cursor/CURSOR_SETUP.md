# Cursor setup for this project

## Hooks (create-hook)

Configured in `.cursor/hooks.json`:

| Hook | Event | Purpose |
|------|-------|---------|
| `block_provider_edits.py` | `preToolUse` | Blocks edits to `src/providers/` |
| `guard_git_push.py` | `beforeShellExecution` | Asks before `git push` |
| `session_context.py` | `sessionStart` | Injects SPEC/AGENTS hard rules |

Reload Cursor or save `hooks.json` to activate. Check **Settings → Hooks** or the Hooks output channel if something does not fire.

## PR Review Toolkit plugin

Project plugin manifest: `.cursor-plugin/plugin.json`

- **Skill:** `/pr-review-toolkit` — structured pre-PR review workflow
- **Agents:** `.cursor-plugin/agents/` — code-reviewer, pr-test-analyzer, silent-failure-hunter, comment-analyzer, type-design-analyzer, code-simplifier

### Enable the plugin

1. **Developer: Reload Window** in Cursor
2. Open **Settings → Plugins** and confirm **PR Review Toolkit** appears (project-scoped plugin from `.cursor-plugin/`)
3. If it does not appear, install the official bundle locally:
   - In chat: `/add-plugin cursor-team-kit` or `/add-plugin pr-review-canvas`
   - Or copy `.cursor-plugin/` to `%USERPROFILE%\.cursor\plugins\local\pr-review-toolkit\`

### Optional user-level plugins (already prepared if copied)

- `cursor-team-kit` — review-and-ship, pr-review-canvas, fix-ci, etc.
- `pr-review-canvas` — interactive PR diff canvas

Location: `%USERPROFILE%\.cursor\plugins\local\`
