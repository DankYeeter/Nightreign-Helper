"""Boolean matching for the effect filter.

Supported syntax:
    vigor                 plain substring, case-insensitive
    vigor AND attack      both must appear (AND must be upper case)
    vigor OR mind         either may appear (OR must be upper case)
    vigor & attack        same as AND
    vigor | mind          same as OR
    "two handed"          quote a phrase containing a space or an operator
    NOT curse             exclude (NOT must be upper case)
    -curse, !curse        same as NOT curse
Lower- or mixed-case "and"/"or"/"not" are searched as plain text, so typing
an effect description that happens to contain one of those words still
works (QA-263). AND binds tighter than OR, so "a OR b AND c" means
"a OR (b AND c)". Bare spaces mean AND, which keeps simple typing behaving
as before.
"""

from __future__ import annotations

import re

TOKEN = re.compile(r'"[^"]*"|\S+')
AND_SYMBOLS = {"&", "&&", "+"}
OR_SYMBOLS = {"|", "||"}
NOT_SYMBOLS = {"-", "!"}


def _tokenise(text: str) -> list[tuple[str, bool]]:
    """Split into (token, was_quoted) pairs, case preserved."""
    out = []
    for raw in TOKEN.findall(text):
        if raw.startswith('"') and raw.endswith('"') and len(raw) >= 2:
            inner = raw[1:-1].strip()
            if inner:
                out.append((inner, True))
        else:
            out.append((raw, False))
    return out


def parse(text: str):
    """Return a predicate over a list of strings, or None for an empty query."""
    tokens = _tokenise(text or "")
    if not tokens:
        return None

    or_groups: list[list[tuple[bool, str]]] = [[]]
    negate_next = False

    for token, was_quoted in tokens:
        # A quoted phrase is always a term, even if it reads like an operator.
        if not was_quoted:
            if token == "OR" or token in OR_SYMBOLS:
                or_groups.append([])
                negate_next = False
                continue
            if token == "AND" or token in AND_SYMBOLS:
                continue
            if token == "NOT" or token in NOT_SYMBOLS:
                negate_next = True
                continue
            if token[0] in NOT_SYMBOLS and len(token) > 1:
                or_groups[-1].append((True, token[1:].lower()))
                continue
        or_groups[-1].append((negate_next, token.lower()))
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
