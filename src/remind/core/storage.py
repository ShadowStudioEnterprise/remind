import json
from dataclasses import asdict
from typing import List
from remind.core.models import MigraineEntry
from remind.paths import history_path

def load_history() -> List[MigraineEntry]:
    path = history_path()
    if not path.exists():
        return []

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return [MigraineEntry(**item) for item in raw]
    except Exception:
        # Backup del archivo corrupto para no perderlo
        try:
            corrupt = path.with_suffix(".corrupt.json")
            corrupt.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
        except Exception:
            pass
        return []

def save_history(entries: List[MigraineEntry]) -> None:
    path = history_path()

    # Escritura atómica: escribimos a temp y reemplazamos
    tmp = path.with_suffix(".tmp")
    tmp.write_text(
        json.dumps([asdict(e) for e in entries], ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    tmp.replace(path)