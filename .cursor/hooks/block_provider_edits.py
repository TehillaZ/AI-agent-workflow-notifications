"""Block agent edits to src/providers/ (external vendor API stubs)."""
import json
import sys


def normalize(path):
    return path.replace("\\", "/").lower()


def collect_paths(tool_name, tool_input):
    paths = []
    if tool_name in ("Write", "Delete"):
        path = tool_input.get("path")
        if path:
            paths.append(path)
    elif tool_name == "StrReplace":
        path = tool_input.get("path")
        if path:
            paths.append(path)
    return paths


def is_provider_path(path):
    normalized = normalize(path)
    return "/providers/" in normalized or normalized.endswith("/providers")


def main():
    payload = json.load(sys.stdin)
    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input") or {}

    for path in collect_paths(tool_name, tool_input):
        if is_provider_path(path):
            print(
                json.dumps(
                    {
                        "permission": "deny",
                        "user_message": "Provider files under src/providers/ are read-only (SPEC.md hard rule).",
                        "agent_message": (
                            "Do not modify src/providers/. Improve main.py, storage.py, "
                            "processor.py, models.py, or segmenter.py instead."
                        ),
                    }
                )
            )
            return

    print(json.dumps({"permission": "allow"}))


if __name__ == "__main__":
    main()
