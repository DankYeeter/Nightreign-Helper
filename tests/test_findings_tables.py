"""qa/findings.md and security/findings.md broke silently, five times in one
day (NH-003, T-209/T-211): four rows found and fixed by the director
(QA-211, QA-225, QA-226, QA-227), and a fifth one (QA-240) that the fix
commit for the other four created itself -- an unescaped pipe inside a shell
command in a description cell split that row into an extra column. Nobody
noticed until the retrospective read the raw text.

`tests/` held no `.md` path literal at all before this file (T-202 checked
with two independent search masks, zero hits). This is the first guard.

Both tables are read as plain markdown, not rendered: a row is one text line
that starts with an unescaped ``|``. The header row is read to get the
expected column count and to find the "Status" and "Letzte Pruefung"
columns by name -- the two tables do not have the same shape (8 columns for
qa/findings.md, 5 for security/findings.md), and hardcoding either number
here would make this test guard its own assumption instead of the files.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import NamedTuple

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

FINDINGS_FILES = (
    REPO_ROOT / "qa" / "findings.md",
    REPO_ROOT / "security" / "findings.md",
)

DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


class Row(NamedTuple):
    line_number: int  # 1-based, matches what an editor shows
    cells: list[str]
    ends_with_pipe: bool


def split_table_row(line: str) -> tuple[list[str], bool]:
    """Split one markdown table line into its cells.

    Honours ``\\|`` as an escaped, literal pipe (that is how QA-240's own
    shell command is written today: ``git show HEAD~1:<datei> \\| sed -n``).
    A well-formed row ``| a | b |`` produces the two cells ``[" a ", " b "]``;
    the phantom empty strings before the leading pipe and after the trailing
    one are dropped. If the line does not end in an unescaped pipe, nothing
    is dropped off the end, so the last cell carries whatever came after the
    missing pipe -- that is how a missing closing pipe is detected below.
    """
    text = line.rstrip("\n").rstrip("\r")
    cells: list[str] = []
    current: list[str] = []
    i = 0
    length = len(text)
    while i < length:
        char = text[i]
        if char == "\\" and i + 1 < length and text[i + 1] == "|":
            current.append("|")
            i += 2
            continue
        if char == "|":
            cells.append("".join(current))
            current = []
            i += 1
            continue
        current.append(char)
        i += 1
    cells.append("".join(current))

    ends_with_pipe = bool(cells) and cells[-1] == "" and text.endswith("|")
    if cells and cells[0] == "":
        cells = cells[1:]
    if ends_with_pipe and cells and cells[-1] == "":
        cells = cells[:-1]
    return cells, ends_with_pipe


def parse_findings_table(text: str) -> tuple[list[str], list[Row]]:
    """Parse the one findings table a file holds.

    The header is the first line starting with ``| ID |``; the line right
    after it is the ``|---|---|`` separator and is skipped. Every other line
    that starts with ``|`` is a data row -- blank lines between rows (both
    files have at least one) are skipped, not treated as the end of the
    table.
    """
    lines = text.splitlines()
    header_index = next(
        index for index, line in enumerate(lines) if line.startswith("| ID |")
    )
    header_cells, _ = split_table_row(lines[header_index])

    rows: list[Row] = []
    for line_number, line in enumerate(lines[header_index + 2 :], start=header_index + 3):
        if not line.strip() or not line.startswith("|"):
            continue
        cells, ends_with_pipe = split_table_row(line)
        rows.append(Row(line_number, cells, ends_with_pipe))
    return header_cells, rows


def _column_index(header_cells: list[str], name: str) -> int:
    normalized = [cell.strip() for cell in header_cells]
    return normalized.index(name)


def _finding_id(cells: list[str]) -> str:
    return cells[0].strip() if cells else "<row has no cells>"


def find_wrong_column_count(header_cells: list[str], rows: list[Row]) -> list[str]:
    expected = len(header_cells)
    return [
        f"line {row.line_number} ({_finding_id(row.cells)}): "
        f"{len(row.cells)} columns, header has {expected}"
        for row in rows
        if len(row.cells) != expected
    ]


def find_missing_closing_pipe(rows: list[Row]) -> list[str]:
    return [
        f"line {row.line_number} ({_finding_id(row.cells)}): no closing pipe"
        for row in rows
        if not row.ends_with_pipe
    ]


def find_status_that_is_a_date(header_cells: list[str], rows: list[Row]) -> list[str]:
    # QA-211: the Status cell was silently overwritten by a "Letzte
    # Pruefung"-shaped date and stopped saying whether the finding was open.
    status_index = _column_index(header_cells, "Status")
    violations = []
    for row in rows:
        if len(row.cells) <= status_index:
            continue  # wrong arity is find_wrong_column_count's job
        status_text = row.cells[status_index].strip().strip("*").strip()
        if DATE_RE.fullmatch(status_text):
            violations.append(
                f"line {row.line_number} ({_finding_id(row.cells)}): "
                f"Status column reads a bare date ({status_text!r})"
            )
    return violations


def find_last_checked_that_is_not_a_date(
    header_cells: list[str], rows: list[Row]
) -> list[str]:
    date_index = _column_index(header_cells, "Letzte Pruefung")
    violations = []
    for row in rows:
        if len(row.cells) <= date_index:
            continue  # wrong arity is find_wrong_column_count's job
        date_text = row.cells[date_index].strip()
        if not DATE_RE.fullmatch(date_text):
            violations.append(
                f"line {row.line_number} ({_finding_id(row.cells)}): "
                f"Letzte Pruefung column is not a plain YYYY-MM-DD date "
                f"({date_text!r})"
            )
    return violations


@pytest.mark.parametrize("path", FINDINGS_FILES, ids=lambda p: p.relative_to(REPO_ROOT).as_posix())
def test_every_row_has_the_header_column_count(path: Path) -> None:
    header_cells, rows = parse_findings_table(path.read_text(encoding="utf-8"))
    violations = find_wrong_column_count(header_cells, rows)
    assert not violations, f"{path}:\n" + "\n".join(violations)


@pytest.mark.parametrize("path", FINDINGS_FILES, ids=lambda p: p.relative_to(REPO_ROOT).as_posix())
def test_every_row_closes_with_a_pipe(path: Path) -> None:
    _, rows = parse_findings_table(path.read_text(encoding="utf-8"))
    violations = find_missing_closing_pipe(rows)
    assert not violations, f"{path}:\n" + "\n".join(violations)


@pytest.mark.parametrize("path", FINDINGS_FILES, ids=lambda p: p.relative_to(REPO_ROOT).as_posix())
def test_status_column_is_never_a_bare_date(path: Path) -> None:
    header_cells, rows = parse_findings_table(path.read_text(encoding="utf-8"))
    violations = find_status_that_is_a_date(header_cells, rows)
    assert not violations, f"{path}:\n" + "\n".join(violations)


@pytest.mark.parametrize("path", FINDINGS_FILES, ids=lambda p: p.relative_to(REPO_ROOT).as_posix())
def test_last_checked_column_is_always_a_date(path: Path) -> None:
    header_cells, rows = parse_findings_table(path.read_text(encoding="utf-8"))
    violations = find_last_checked_that_is_not_a_date(header_cells, rows)
    assert not violations, f"{path}:\n" + "\n".join(violations)
