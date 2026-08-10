"""Boolean matching for the effect filter.

Supported syntax, case-insensitive:
    vigor                 plain substring
    vigor AND attack      both must appear
    vigor OR mind         either may appear
    vigor & attack        same as AND
    vigor | mind          same as OR
    "two handed"          quote a phrase containing a space or an operator
    NOT curse             exclude
AND binds tighter than OR, so "a OR b AND c" means "a OR (b AND c)".
Bare spaces mean AND, which keeps simple typing behaving as before.
"""

from __future__ import annotations

import re

TOKEN = re.compile(r'"[^"]*"|\S+')
AND_WORDS = {"and", "&", "&&", "+"}
OR_WORDS = {"or", "|", "||"}
NOT_WORDS = {"not", "-", "!"}


def _tokenise(text: str) -> list[str]:
    out = []
    for raw in TOKEN.findall(text):
        if raw.startswith('"') and raw.endswith('"') and len(raw) >= 2:
            out.append(raw[1:-1].strip().lower())
        else:
            out.append(raw.lower())
    return [t for t in out if t]


def parse(text: str):
    """Return a predicate over a list of strings, or None for an empty query."""
    tokens = _tokenise(text or "")
    if not tokens:
        return None

    or_groups: list[list[tuple[bool, str]]] = [[]]
    negate_next = False
    quoted = {
        raw[1:-1].strip().lower()
        for raw in TOKEN.findall(text or "")
        if raw.startswith('"') and raw.endswith('"')
    }

    for token in tokens:
        # A quoted phrase is always a term, even if it reads like an operator.
        if token not in quoted:
            if token in OR_WORDS:
                or_groups.append([])
                negate_next = False
                continue
            if token in AND_WORDS:
                continue
            if token in NOT_WORDS:
                negate_next = True
                continue
            if token.startswith("-") and len(token) > 1:
                or_groups[-1].append((True, token[1:]))
                continue
        or_groups[-1].append((negate_next, token))
        negate_next = False

    or_groups = [g for g in or_groups if g]
    if not or_groups:
        return None

    def predicate(haystacks) -> bool:
        blob = " ".join(haystacks).lower()
        for group in or_groups:
            if all((term not in blob) if negated else (term in blob)
                   for negated, term in group):
                return True
        return False

    return predicate


def matches(text: str, haystacks) -> bool:
    predicate = parse(text)
    return True if predicate is None else predicate(haystacks)
