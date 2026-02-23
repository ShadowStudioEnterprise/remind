from datetime import datetime
from typing import List, Tuple
from remind.core.models import MigraineEntry

def _parse_ts(ts: str) -> datetime:
    try:
        return datetime.fromisoformat(ts)
    except ValueError:
        return datetime.min

def sort_entries(entries: List[MigraineEntry]) -> List[MigraineEntry]:
    return sorted(entries, key=lambda e: _parse_ts(e.timestamp))

def basic_stats(entries: List[MigraineEntry]) -> Tuple[int, int, float]:
    ordered = sort_entries(entries)
    total = len(ordered)
    migraine_count = sum(1 for e in ordered if e.had_migraine)
    avg_intensity = (
        sum(e.intensity for e in ordered if e.had_migraine) / migraine_count
        if migraine_count else 0.0
    )
    return total, migraine_count, avg_intensity