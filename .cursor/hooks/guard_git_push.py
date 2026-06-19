"""Guard git push: block secrets and ask for approval on clean pushes (AGENTS.md)."""
import json
import re
import subprocess
import sys

# (compiled pattern, secret type label) — most specific rules first
SECRET_RULES = [
    (re.compile(r"\bghp_[A-Za-z0-9_]{20,}\b"), "github-pat"),
    (re.compile(r"\bgho_[A-Za-z0-9_]{20,}\b"), "github-oauth"),
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"), "github-pat"),
    (re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"), "openai-key"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "aws-access-key"),
    (re.compile(r"(?i)BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY"), "private-key-block"),
    (re.compile(r"(?i)(api[_-]?key|apikey)\s*[:=]\s*['\"]?([^'\"#\s]{8,})"), "api-key"),
    (re.compile(r"(?i)(password|passwd|pwd)\s*[:=]\s*['\"]?([^'\"#\s]{4,})"), "password"),
    (re.compile(r"(?i)(client[_-]?secret|secret[_-]?key)\s*[:=]\s*['\"]?([^'\"#\s]{8,})"), "secret"),
    (re.compile(r"(?i)(access[_-]?token|auth[_-]?token|bearer)\s*[:=]\s*['\"]?([^'\"#\s]{8,})"), "token"),
    (re.compile(r"(?i)(private[_-]?key)\s*[:=]\s*['\"]?([^'\"#\s]{8,})"), "private-key"),
]

PLACEHOLDER_VALUE = re.compile(
    r"(?i)^(your[-_]?(token|key|secret|password|api[-_]?key)[-_a-z0-9]*|"
    r"replace[-_]?me|insert[-_]?here|enter[-_]?here|changeme|example|"
    r"placeholder|dummy|test[-_]?(token|key|secret|password)|"
    r"sample[-_]?(token|key|secret|password)|xxx+|000+|123456|"
    r"password123|secret123|<[^>]+>|\$\{env:|\*\*\*)$"
)

SKIP_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".pdf",
    ".zip",
    ".pyc",
    ".whl",
}


def run_git(args):
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result


def push_diff_range():
    upstream = run_git(["rev-parse", "--abbrev-ref", "@{u}"])
    if upstream.returncode == 0 and upstream.stdout.strip():
        ref = upstream.stdout.strip()
        return f"{ref}..HEAD"

    for candidate in ("origin/HEAD", "origin/main", "origin/master"):
        check = run_git(["rev-parse", "--verify", candidate])
        if check.returncode == 0:
            return f"{candidate}..HEAD"

    return None


def files_in_push():
    diff_range = push_diff_range()
    if diff_range:
        result = run_git(["diff", "--name-only", diff_range])
        if result.returncode == 0 and result.stdout.strip():
            return [f for f in result.stdout.strip().splitlines() if f.strip()]

    result = run_git(["log", "-5", "--name-only", "--pretty=format:"])
    if result.returncode != 0:
        return []

    files = []
    seen = set()
    for line in result.stdout.splitlines():
        path = line.strip()
        if not path or path in seen:
            continue
        seen.add(path)
        files.append(path)
    return files


def file_at_head(path):
    result = run_git(["show", f"HEAD:{path}"])
    if result.returncode != 0:
        return None
    return result.stdout


def is_placeholder(value):
    value = value.strip().strip("'\"")
    if not value or len(value) < 4:
        return True
    if PLACEHOLDER_VALUE.search(value):
        return True
    if value.upper() in {
        "NONE",
        "NULL",
        "TRUE",
        "FALSE",
        "UNDEFINED",
        "YOUR_TOKEN_HERE",
        "YOUR_API_KEY",
    }:
        return True
    return False


def scan_line(line, line_no, path, findings):
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return

    for pattern, label in SECRET_RULES:
        match = pattern.search(line)
        if not match:
            continue

        if label == "private-key-block":
            findings.append((path, line_no, label))
            return

        captured = None
        if match.lastindex and match.lastindex >= 2:
            captured = match.group(2)
        elif match.lastindex and match.lastindex >= 1:
            captured = match.group(match.lastindex)

        if captured and is_placeholder(captured):
            continue

        findings.append((path, line_no, label))
        return


def scan_file(path):
    if any(path.lower().endswith(ext) for ext in SKIP_EXTENSIONS):
        return []

    content = file_at_head(path)
    if content is None:
        return []

    findings = []
    for index, line in enumerate(content.splitlines(), start=1):
        scan_line(line, index, path, findings)
    return findings


def scan_push_for_secrets():
    findings = []
    seen = set()
    for path in files_in_push():
        for item in scan_file(path):
            key = (item[0], item[1], item[2])
            if key not in seen:
                seen.add(key)
                findings.append(item)
    findings.sort(key=lambda x: (x[0], x[1], x[2]))
    return findings


def format_findings(findings):
    lines = ["Push blocked: possible secrets in commits to be pushed:"]
    for path, line_no, label in findings:
        lines.append(f"  - {path}:{line_no} ({label})")
    lines.append("Remove or rotate the secret, then commit the fix before pushing.")
    return "\n".join(lines)


def deny_push(message, agent_message):
    print(
        json.dumps(
            {
                "permission": "deny",
                "user_message": message,
                "agent_message": agent_message,
            }
        )
    )


def ask_push():
    print(
        json.dumps(
            {
                "permission": "ask",
                "user_message": "AGENTS.md requires approval before pushing to GitHub.",
                "agent_message": "No secrets detected in outgoing commits. Confirm with the user before git push.",
            }
        )
    )


def main():
    payload = json.load(sys.stdin)
    command = payload.get("command", "")

    if not re.search(r"\bgit\s+push\b", command, re.IGNORECASE):
        print(json.dumps({"permission": "allow"}))
        return

    try:
        findings = scan_push_for_secrets()
    except Exception as exc:
        deny_push(
            f"Push blocked: secret scan failed ({exc}). Fix the issue or push manually after review.",
            "Secret scan errored; do not push until the user reviews outgoing changes manually.",
        )
        return

    if findings:
        message = format_findings(findings)
        deny_push(
            message,
            "Push blocked due to detected secrets. Report file:line locations to the user and help remove them.",
        )
        return

    ask_push()


if __name__ == "__main__":
    main()
