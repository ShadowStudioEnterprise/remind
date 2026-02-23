import csv
from pathlib import Path
from typing import List
from datetime import datetime

from remind.core.models import MigraineEntry


def export_csv(entries: List[MigraineEntry], file_path: str) -> bool:
    """
    Exporta el histórico a CSV estructurado.
    Devuelve True si se exporta correctamente.
    """

    if not entries:
        return False

    path = Path(file_path)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Cabecera
        writer.writerow([
            "Fecha",
            "Hora",
            "Migraña",
            "Intensidad",
            "Duración (min)",
            "Medicación",
            "Notas"
        ])

        for e in entries:
            try:
                dt = datetime.fromisoformat(e.timestamp)
                date_str = dt.strftime("%Y-%m-%d")
                time_str = dt.strftime("%H:%M")
            except Exception:
                date_str = e.timestamp
                time_str = ""

            writer.writerow([
                date_str,
                time_str,
                "Sí" if e.had_migraine else "No",
                e.intensity if e.had_migraine else 0,
                getattr(e, "duration_min", ""),
                getattr(e, "medication", ""),
                getattr(e, "notes", ""),
            ])

    return True