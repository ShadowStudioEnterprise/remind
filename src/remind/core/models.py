from dataclasses import dataclass
from datetime import datetime

@dataclass
class MigraineEntry:
    timestamp: str          # ISO8601
    had_migraine: bool
    intensity: int          # 0-10
    notes: str = ""

    @staticmethod
    def now(had_migraine: bool, intensity: int, notes: str = "") -> "MigraineEntry":
        return MigraineEntry(
            timestamp=datetime.now().isoformat(timespec="seconds"),
            had_migraine=had_migraine,
            intensity=intensity,
            notes=notes.strip()
        )