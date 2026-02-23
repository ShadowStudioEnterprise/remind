import sys
import traceback
from datetime import datetime
from pathlib import Path

from remind.paths import data_dir  # o donde guardes appdata


def install_crash_hook(logger):
    def excepthook(exc_type, exc, tb):
        try:
            text = "".join(traceback.format_exception(exc_type, exc, tb))
            logger.critical("Unhandled exception:\n%s", text)

            # Guardar crash report
            crash_dir = Path(data_dir()) / "crash"
            crash_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            (crash_dir / f"crash_{ts}.log").write_text(text, encoding="utf-8")
        except Exception:
            pass
        # Deja el comportamiento por defecto (terminar)
        sys.__excepthook__(exc_type, exc, tb)

    sys.excepthook = excepthook