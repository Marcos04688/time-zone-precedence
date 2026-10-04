"""Time Zone Precedence.

Selects the most specific time zone from a set of candidate IANA tzdata
identifiers for a single location. Public entry point: :func:`select`.
"""

from .core import select, specificity, ZoneCandidate

__all__ = ["select", "specificity", "ZoneCandidate"]
