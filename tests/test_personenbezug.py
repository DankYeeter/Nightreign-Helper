"""The repository is public: no tracked file names a real user folder or Steam account."""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PERSONAL = (
    r"[a-z]:[\\/]+users[\\/]+[a-z0-9]"  # a Windows home folder, either slash
    r"|/[a-z]/users/[a-z0-9]"  # the same in Git Bash
    r"|[a-z]--users-[a-z0-9]"  # the same as Claude names its project folder
    r"|7656119[0-9]{10}"  # SteamID64
)
# Made-up values the tests feed to the path and error handling.
INVENTED = re.compile(r"users[\\/]+(someone|x)\b|76561198000000000", re.IGNORECASE)


def test_no_tracked_file_names_a_real_user():
    grep = subprocess.run(
        ["git", "grep", "-nIiE", PERSONAL],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert grep.returncode in (0, 1), grep.stderr  # 1 means no match
    found = [line[:120] for line in grep.stdout.splitlines() if not INVENTED.search(line)]
    assert not found, "use <Hauptbaum>, <ClaudeCode>, %TEMP%, <Konto-A>:\n" + "\n".join(found)
