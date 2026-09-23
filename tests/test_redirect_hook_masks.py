"""The data-redirect hook refuses program starts, not commands that name run.py.

NH-011. `.claude/hooks/enforce-data-redirect.ps1` once matched "python"
anywhere followed by "run.py" anywhere and refused seven commands on 22.09.
that started nothing. These literals come from those refusals and from the
start forms the team really uses; none sets the three redirect variables, so
every recognised start must come back as `deny`.
"""

from __future__ import annotations

import json
import pathlib
import subprocess

import pytest

from nrplanner import shortcut

HOOK = (pathlib.Path(__file__).resolve().parents[1]
        / ".claude" / "hooks" / "enforce-data-redirect.ps1")

NOT_A_START = [
    'python - <<\'EOF\'\nimport pathlib\n'
    'p = pathlib.Path("nrplanner/advisor/run.py")\nEOF',
    "cd x && python -m pyflakes nrplanner/ run.py && echo flakes-clean",
    'grep -rl "LOCALAPPDATA\\|python.*run.py" scratchpad/',
    "ls; python - <<'EOF'\n"
    "roots=['nrplanner','nrdata','scripts','tests','run.py']\nEOF",
    "sed -n 1,5p nrplanner/advisor/run.py; pytest tests/test_advisor.py -q",
    "python scratchpad/show.py . scripts/measure_advisor_block.py:wait",
    # T-330a Nebenfund (T-332b): "|" in einem Anfuehrungszeichen-Text zaehlte
    # als Befehlsgrenze und liess $istExeKommando faelschlich anschlagen.
    'grep -E "foo|NightreignHelper.exe" datei',
    "Select-String -Pattern 'a|NightreignHelper\\.exe'",
]

A_START = [
    "python run.py",
    ".venv/Scripts/python.exe -X utf8 run.py",
    "A=1 B=2 nohup python run.py > log 2>&1 &",
    "cd x && python -u run.py",
    "Start-Process -FilePath python -ArgumentList 'run.py'",
    '& "C:\\Py\\python.exe" run.py',
    "python scripts/measure_advisor_block.py",
    # $istExeKommando muss trotz der Quotes-Maske oben weiterhin greifen.
    '& "C:\\x\\NightreignHelper.exe"',
    'Start-Process -FilePath ".\\dist\\NightreignHelper.exe"',
    "dist\\NightreignHelper.exe",
    "cmd; NightreignHelper.exe",
]


def _decision(command: str) -> str | None:
    powershell = shortcut.powershell_path()
    if powershell is None:
        pytest.skip("Windows PowerShell not found")
    call = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
    done = subprocess.run(
        [str(powershell), "-NoProfile", "-ExecutionPolicy", "Bypass",
         "-File", str(HOOK)],
        input=call, capture_output=True, text=True, timeout=60, check=True)
    if not done.stdout.strip():
        return None
    return json.loads(done.stdout)["hookSpecificOutput"]["permissionDecision"]


@pytest.mark.parametrize("command", NOT_A_START)
def test_a_command_that_only_names_the_script_passes(command):
    assert _decision(command) is None


@pytest.mark.parametrize("command", A_START)
def test_a_start_without_the_redirect_is_refused(command):
    assert _decision(command) == "deny"
