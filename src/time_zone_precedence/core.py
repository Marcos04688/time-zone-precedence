"""Core selection logic for time-zone precedence.

The problem: a location can be matched by several IANA time-zone identifiers.
``select`` returns the single most specific one.

Specificity is measured purely by the number of path segments in the IANA
identifier, counting the forward-slash separator. This is a deliberate
choice: no timezone-boundary geometry ships in the Python standard library
(nor here), so geographic area is unavailable. Segment count is a useful,
deterministic proxy — ``Europe/London`` describes one country, while
``America/North_Dakota/New_Salem`` describes one city within one state.
Ties are broken by input order: the first candidate at the highest
specificity wins. This is stable and predictable; callers that want a
particular tie-break can pre-sort their input.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ZoneCandidate:
    """A single candidate time zone for a location.

    Attributes
    ----------
    zone_id:
        IANA time-zone identifier (e.g. ``"America/North_Dakota/New_Salem"``).
    """

    zone_id: str


def specificity(zone_id: str) -> int:
    """Return the specificity score of an IANA time-zone identifier.

    The score is the number of segments produced when splitting on ``'/'``.
    ``"America/Chicago"`` → 2; ``"America/North_Dakota/New_Salem"`` → 3.
    A bare identifier without a slash (``"UTC"``, ``"GMT"``) scores 1.

    Raises
    ------
    TypeError
        If *zone_id* is not a :class:`str`.
    ValueError
        If *zone_id* is empty or consists only of slashes (no usable
        segment after splitting).
    """
    if not isinstance(zone_id, str):
        raise TypeError(
            f"zone_id must be a str, got {type(zone_id).__name__}"
        )
    if not zone_id:
        raise ValueError("zone_id must be a non-empty string")

    # ``split`` on "/" gives the segment count directly. Leading/trailing
    # slashes would yield empty segments, which we reject as malformed
    # because an IANA identifier never begins or ends with a separator.
    parts = zone_id.split("/")
    if any(part == "" for part in parts):
        raise ValueError(
            f"zone_id contains an empty segment: {zone_id!r}"
        )
    return len(parts)


def select(candidates) -> ZoneCandidate:
    """Return the most specific time-zone candidate for a location.

    *candidates* is an iterable of :class:`ZoneCandidate`. The candidate with
    the highest :func:`specificity` score wins. Ties are broken by the order
    in which candidates appear in *candidates* — the earliest one wins.

    Parameters
    ----------
    candidates:
        Iterable of :class:`ZoneCandidate`.

    Returns
    -------
    ZoneCandidate
        The selected candidate.

    Raises
    ------
    TypeError
        If *candidates* is not iterable, or yields a non-:class:`ZoneCandidate`.
    ValueError
        If *candidates* is empty, or any candidate's ``zone_id`` is empty.
    """
    try:
        iterator = iter(candidates)
    except TypeError as exc:
        raise TypeError(
            "candidates must be an iterable of ZoneCandidate"
        ) from exc

    best = None
    best_score = -1
    for cand in iterator:
        if not isinstance(cand, ZoneCandidate):
            raise TypeError(
                "each candidate must be a ZoneCandidate, got "
                f"{type(cand).__name__}"
            )
        score = specificity(cand.zone_id)
        if score > best_score:
            best = cand
            best_score = score

    if best is None:
        raise ValueError("candidates must contain at least one ZoneCandidate")
    return best
