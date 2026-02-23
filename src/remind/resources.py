import sys
from pathlib import Path


def resource_path(relative_path: str) -> str:
    """
    Devuelve la ruta absoluta correcta tanto en desarrollo
    como cuando está empaquetado con PyInstaller (--onefile).
    """
    if hasattr(sys, "_MEIPASS"):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent

    return str(base_path / relative_path)