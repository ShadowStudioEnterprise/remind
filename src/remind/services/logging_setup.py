import logging
import platform
import sys
import traceback
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime

from remind.paths import get_app_dir  # asumo que ya lo tienes (AppData)


LOGGER_NAME = "remind"


def get_log_dir() -> Path:
    d = Path(get_app_dir()) / "logs"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_log_path() -> Path:
    return get_log_dir() / "app.log"


def init_logging(level: int = logging.INFO) -> logging.Logger:
    """
    Inicializa logging a fichero rotativo + consola (opcional).
    Llamar una sola vez al arrancar.
    """
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level)

    # Evitar handlers duplicados si reinicias en dev
    if logger.handlers:
        return logger

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File handler rotativo (5 x 512KB)
    fh = RotatingFileHandler(
        filename=str(get_log_path()),
        maxBytes=512 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    fh.setFormatter(fmt)
    fh.setLevel(level)
    logger.addHandler(fh)

    # Consola: útil en dev (si no usas --noconsole, se verá)
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    sh.setLevel(level)
    logger.addHandler(sh)

    logger.info("Logger inicializado")
    return logger


def write_system_report(path: str, app_name: str, app_version: str) -> None:
    """
    Escribe un txt con info de entorno (para el ZIP de diagnóstico).
    """
    p = Path(path)
    lines = [
        f"{app_name} {app_version}",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        f"Python: {sys.version}",
        f"Executable: {sys.executable}",
        f"Platform: {platform.platform()}",
        f"Machine: {platform.machine()}",
        f"Processor: {platform.processor()}",
    ]
    p.write_text("\n".join(lines), encoding="utf-8")


def log_exception(logger: logging.Logger, exc: BaseException, context: str = "") -> None:
    """
    Loggea una excepción con traceback.
    """
    msg = f"Exception: {context}".strip()
    tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    logger.error("%s\n%s", msg, tb)