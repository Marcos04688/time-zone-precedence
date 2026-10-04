# Time Zone Precedence

Selects the most specific IANA time-zone identifier for a location from a set of candidates.

```python
from time_zone_precedence import ZoneCandidate, select, specificity

result = select([
    ZoneCandidate("America/Chicago"),
    ZoneCandidate("America/North_Dakota/New_Salem"),
])
print(result.zone_id)  # America/North_Dakota/New_Salem
```

## Why

A single location may legitimately be matched by multiple IANA time-zone identifiers — for instance, a point in North Dakota could be described by both `America/Chicago` and `America/North_Dakota/New_Salem`. When the downstream consumer (a scheduler, a formatter, a log writer) only accepts one zone, you have to pick.

This library picks by specificity, measured as the number of `/`-separated segments in the identifier. `America/Chicago` has 2; `America/North_Dakota/New_Salem` has 3. The deeper path names a smaller geographic area, which is what you usually want when several zones overlap.

The trade-off: this is a textual heuristic, not a geometric one. No timezone-boundary data ships in the Python standard library, and this library deliberately depends only on the standard library. If two candidates have the same segment count, the first one in the input wins — stable, predictable, and under the caller's control via input ordering.

## Edge cases

- Bare identifiers (`UTC`, `GMT`) score 1 and lose to any slashed identifier.
- Empty strings, leading/trailing slashes, and double slashes are rejected with `ValueError` — they are not valid IANA identifiers.
- `select` raises `ValueError` on an empty candidate list and `TypeError` if any element is not a `ZoneCandidate`.
