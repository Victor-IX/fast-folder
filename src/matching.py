from __future__ import annotations

import re
from collections.abc import Iterable
from difflib import SequenceMatcher

# Any match scoring below this is treated as "not a match at all".
MIN_SCORE = 0.40
# The runner-up has to be at least this far behind for the best match to win outright.
CLEAR_WINNER_MARGIN = 0.10
# Below this similarity, a typo-style match is too much of a stretch to consider.
FUZZY_MIN_RATIO = 0.60

# Splits on separators (-, _, ., space) and on camelCase boundaries.
_TOKEN_SPLIT = re.compile(r"[^a-zA-Z0-9]+|(?<=[a-z0-9])(?=[A-Z])")


def _tokens(name: str) -> list[str]:
    return [token for token in _TOKEN_SPLIT.split(name) if token]


def _initials(name: str) -> str:
    """Acronym built from the name's word starts: 'my-cool_project' -> 'mcp'."""
    return "".join(token[0] for token in _tokens(name)).lower()


def _subsequence_span(query: str, name: str) -> int | None:
    """Width of the window of NAME that contains QUERY's characters in order, or None."""
    start: int | None = None
    cursor = 0
    for char in query:
        found = name.find(char, cursor)
        if found == -1:
            return None
        if start is None:
            start = found
        cursor = found + 1
    if start is None:
        return None
    return cursor - start


def score(query: str, name: str) -> float:
    """Rate how well NAME answers QUERY, from 0.0 (no match) to 1.0 (exact).

    Tiers, strongest first: exact, prefix, substring, initials, in-order
    subsequence (handles dropped characters), then edit-distance similarity
    (handles typos and transpositions).
    """
    needle = query.lower()
    haystack = name.lower()
    if not needle or not haystack:
        return 0.0

    if needle == haystack:
        return 1.0

    # How much of the name the query actually accounts for; breaks ties inside a tier
    # so a short query prefers a short name.
    coverage = min(len(needle) / len(haystack), 1.0)

    if haystack.startswith(needle):
        return 0.85 + 0.10 * coverage

    if needle in haystack:
        return 0.70 + 0.10 * coverage

    initials = _initials(name)
    if initials and initials.startswith(needle):
        return 0.60 + 0.10 * (len(needle) / len(initials))

    span = _subsequence_span(needle, haystack)
    if span:
        return 0.45 + 0.15 * (len(needle) / span)

    ratio = SequenceMatcher(None, needle, haystack).ratio()
    if ratio >= FUZZY_MIN_RATIO:
        return 0.40 + 0.20 * (ratio - FUZZY_MIN_RATIO) / (1.0 - FUZZY_MIN_RATIO)

    return 0.0


def rank(query: str, names: Iterable[str]) -> list[tuple[str, float]]:
    """Names scoring at least MIN_SCORE for QUERY, best first, then alphabetical."""
    scored = ((name, score(query, name)) for name in names)
    matches = [(name, value) for name, value in scored if value >= MIN_SCORE]
    matches.sort(key=lambda match: (-match[1], match[0].lower()))
    return matches


def is_clear_winner(matches: list[tuple[str, float]]) -> bool:
    """True when the top match is unambiguous enough to act on without asking."""
    if not matches:
        return False
    best_score = matches[0][1]
    if best_score >= 1.0:
        return True
    if len(matches) == 1:
        return True
    return best_score - matches[1][1] >= CLEAR_WINNER_MARGIN


def ambiguous_matches(matches: list[tuple[str, float]], limit: int = 8) -> list[str]:
    """The top match plus every close-behind rival, for a disambiguation prompt."""
    if not matches:
        return []
    best_score = matches[0][1]
    close = [name for name, value in matches if best_score - value < CLEAR_WINNER_MARGIN]
    return close[:limit]
