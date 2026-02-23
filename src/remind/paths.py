from pathlib import Path
from platformdirs import user_data_dir
from remind.brand import INTERNAL_NAME

APP_NAME = INTERNAL_NAME
APP_AUTHOR = INTERNAL_NAME

def get_app_dir() -> Path:
    """
    Carpeta de datos de usuario por sistema operativo.
    Crea la carpeta si no existe.
    """
    base = Path(user_data_dir(appname=APP_NAME, appauthor=APP_AUTHOR))
    base.mkdir(parents=True, exist_ok=True)
    return base

def settings_path() -> Path:
    return get_app_dir() / "settings.json"

def history_path() -> Path:
    return get_app_dir() / "migraine_history.json"

def logs_path() -> Path:
    return get_app_dir() / "app.log"