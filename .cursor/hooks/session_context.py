"""Inject project hard rules at the start of each agent session."""
import json
import sys

CONTEXT = """Project hard rules (notifications-api-python screening task):
- Do NOT modify or refactor any file under src/providers/ (external vendor APIs).
- README additions must be written by the candidate without AI.
- Ask before: new dependencies, API response format changes, route renames, git push.
- Verify changes manually against Flask endpoints listed in AGENTS.md.
- PR Review Toolkit agents live in .cursor-plugin/agents/; use /pr-review-toolkit or ask for structured review before push."""


def main():
    print(json.dumps({"additional_context": CONTEXT}))


if __name__ == "__main__":
    main()
