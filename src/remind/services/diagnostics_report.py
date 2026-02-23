import json
import zipfile
from pathlib import Path
from datetime import datetime
from typing import Optional

from remind.services.logging_setup import get_log_dir, write_system_report
from remind.paths import settings_path, history_path  # asumo que existen
from remind.brand import DISPLAY_NAME, VERSION


def _safe_copy_json(src: Path, dst: Path, redact_notes: bool) -> None:
    """
    Copia JSON. Si redact_notes=True, elimina campo 'notes' si existe.
    """
    if not src.exists():
        return
    raw = json.loads(src.read_text(encoding="utf-8"))
    if redact_notes and isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict) and "notes" in item:
                item["notes"] = ""
    dst.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")


def build_diagnostics_zip(output_dir: Optional[str] = None, redact_notes: bool = True) -> Path:
    """
    Crea un ZIP de diagnóstico con logs + settings + history + system report.
    Devuelve ruta del zip.
    """
    out_dir = Path(output_dir) if output_dir else (Path(get_log_dir()).parent)
    out_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = out_dir / f"remind_diagnostics_{ts}.zip"

    tmp_dir = out_dir / f"_diag_tmp_{ts}"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    # 1) System report
    sys_report = tmp_dir / "system_report.txt"
    write_system_report(str(sys_report), DISPLAY_NAME, VERSION)

    # 2) Logs
    logs_dir = get_log_dir()
    for p in logs_dir.glob("app.log*"):
        try:
            (tmp_dir / p.name).write_bytes(p.read_bytes())
        except Exception:
            pass

    # 3) settings + history
    try:
        _safe_copy_json(Path(settings_path()), tmp_dir / "settings.json", redact_notes=False)
    except Exception:
        pass

    try:
        _safe_copy_json(Path(history_path()), tmp_dir / "migraine_history.json", redact_notes=redact_notes)
    except Exception:
        pass

    # 4) Zip
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for f in tmp_dir.iterdir():
            if f.is_file():
                z.write(f, arcname=f.name)

    # Limpieza tmp
    for f in tmp_dir.iterdir():
        try:
            f.unlink()
        except Exception:
            pass
    try:
        tmp_dir.rmdir()
    except Exception:
        pass

    return zip_path