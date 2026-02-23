import json
import os
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional

from PyQt6.QtCore import QObject, pyqtSignal

from remind.paths import settings_path  # tu helper AppData/settings.json


SETTINGS_VERSION = 1


@dataclass
class AppSettings:
    version: int = SETTINGS_VERSION

    # UI
    theme: str = "dark"        # "dark" | "light"
    language: str = "es"       # "es" | "en"

    # Notifications
    notifications_enabled: bool = True
    notification_hours: int = 8

    # Smart reminder (si lo tienes)
    smart_reminder: bool = True
    reminder_start_hour: int = 10
    reminder_end_hour: int = 22

    # Extras (si lo tienes)
    auto_start: bool = False


def _migrate(raw: Dict[str, Any]) -> Dict[str, Any]:
    v = int(raw.get("version", 0))

    if v < 1:
        raw["version"] = 1
        raw.setdefault("theme", "dark")
        raw.setdefault("language", "es")
        raw.setdefault("notifications_enabled", True)
        raw.setdefault("notification_hours", 8)
        raw.setdefault("smart_reminder", True)
        raw.setdefault("reminder_start_hour", 10)
        raw.setdefault("reminder_end_hour", 22)
        raw.setdefault("auto_start", False)

    # Normalizaciones defensivas
    theme = str(raw.get("theme", "dark")).lower()
    raw["theme"] = "light" if theme == "light" else "dark"

    lang = str(raw.get("language", "es")).lower()
    raw["language"] = "en" if lang == "en" else "es"

    try:
        h = int(raw.get("notification_hours", 8))
    except Exception:
        h = 8
    raw["notification_hours"] = max(1, min(24, h))

    try:
        raw["reminder_start_hour"] = max(0, min(23, int(raw.get("reminder_start_hour", 10))))
    except Exception:
        raw["reminder_start_hour"] = 10

    try:
        raw["reminder_end_hour"] = max(0, min(23, int(raw.get("reminder_end_hour", 22))))
    except Exception:
        raw["reminder_end_hour"] = 22

    raw["notifications_enabled"] = bool(raw.get("notifications_enabled", True))
    raw["smart_reminder"] = bool(raw.get("smart_reminder", True))
    raw["auto_start"] = bool(raw.get("auto_start", False))

    return raw


def _load_settings_data() -> AppSettings:
    path = settings_path()
    try:
        text = path.read_text(encoding="utf-8")
        raw = json.loads(text)
        raw = _migrate(raw if isinstance(raw, dict) else {})
        return AppSettings(**raw)
    except Exception:
        return AppSettings()

def _save_settings_data(data: AppSettings) -> None:
    path = settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(asdict(data), f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())

    tmp.replace(path)


class SettingsStore(QObject):
    """
    Wrapper observable sobre AppSettings:
      - properties con señales
      - save() centralizado
    """

    theme_changed = pyqtSignal(str)
    language_changed = pyqtSignal(str)

    notifications_enabled_changed = pyqtSignal(bool)
    notification_hours_changed = pyqtSignal(int)

    smart_reminder_changed = pyqtSignal(bool)
    reminder_window_changed = pyqtSignal(int, int)  # start, end

    auto_start_changed = pyqtSignal(bool)

    # si quieres “cualquier cambio”
    changed = pyqtSignal()

    def __init__(self, data: AppSettings):
        super().__init__()
        self._data = data

    # ---- helpers ----

    def to_dataclass(self) -> AppSettings:
        return self._data

    def save(self) -> None:
        _save_settings_data(self._data)

    def _emit_changed(self):
        self.changed.emit()

    # ---- properties ----

    @property
    def theme(self) -> str:
        return self._data.theme

    @theme.setter
    def theme(self, value: str):
        v = "light" if str(value).lower() == "light" else "dark"
        if v != self._data.theme:
            self._data.theme = v
            self.theme_changed.emit(v)
            self._emit_changed()

    @property
    def language(self) -> str:
        return self._data.language

    @language.setter
    def language(self, value: str):
        v = "en" if str(value).lower() == "en" else "es"
        if v != self._data.language:
            self._data.language = v
            self.language_changed.emit(v)
            self._emit_changed()

    @property
    def notifications_enabled(self) -> bool:
        return self._data.notifications_enabled

    @notifications_enabled.setter
    def notifications_enabled(self, value: bool):
        v = bool(value)
        if v != self._data.notifications_enabled:
            self._data.notifications_enabled = v
            self.notifications_enabled_changed.emit(v)
            self._emit_changed()

    @property
    def notification_hours(self) -> int:
        return self._data.notification_hours

    @notification_hours.setter
    def notification_hours(self, value: int):
        try:
            v = max(1, min(24, int(value)))
        except Exception:
            v = 8
        if v != self._data.notification_hours:
            self._data.notification_hours = v
            self.notification_hours_changed.emit(v)
            self._emit_changed()

    @property
    def smart_reminder(self) -> bool:
        return self._data.smart_reminder

    @smart_reminder.setter
    def smart_reminder(self, value: bool):
        v = bool(value)
        if v != self._data.smart_reminder:
            self._data.smart_reminder = v
            self.smart_reminder_changed.emit(v)
            self._emit_changed()

    @property
    def reminder_start_hour(self) -> int:
        return self._data.reminder_start_hour

    @property
    def reminder_end_hour(self) -> int:
        return self._data.reminder_end_hour

    def set_reminder_window(self, start_hour: int, end_hour: int):
        s = max(0, min(23, int(start_hour)))
        e = max(0, min(23, int(end_hour)))
        if s != self._data.reminder_start_hour or e != self._data.reminder_end_hour:
            self._data.reminder_start_hour = s
            self._data.reminder_end_hour = e
            self.reminder_window_changed.emit(s, e)
            self._emit_changed()

    @property
    def auto_start(self) -> bool:
        return self._data.auto_start

    @auto_start.setter
    def auto_start(self, value: bool):
        v = bool(value)
        if v != self._data.auto_start:
            self._data.auto_start = v
            self.auto_start_changed.emit(v)
            self._emit_changed()
    
    def reset_to_defaults(self) -> None:
        """
        Restaura valores por defecto y emite señales necesarias.
        """
        defaults = AppSettings()

        # Hacemos setters para que emitan signals
        self.theme = defaults.theme
        self.language = defaults.language
        self.notifications_enabled = defaults.notifications_enabled
        self.notification_hours = defaults.notification_hours
        self.smart_reminder = defaults.smart_reminder
        self.set_reminder_window(defaults.reminder_start_hour, defaults.reminder_end_hour)
        self.auto_start = defaults.auto_start

    def update(
        self,
        *,
        theme: Optional[str] = None,
        language: Optional[str] = None,
        notifications_enabled: Optional[bool] = None,
        notification_hours: Optional[int] = None,
        smart_reminder: Optional[bool] = None,
        reminder_start_hour: Optional[int] = None,
        reminder_end_hour: Optional[int] = None,
        auto_start: Optional[bool] = None,
    ):
        if theme is not None:
            self.theme = theme
        if language is not None:
            self.language = language
        if notifications_enabled is not None:
            self.notifications_enabled = notifications_enabled
        if notification_hours is not None:
            self.notification_hours = notification_hours
        if smart_reminder is not None:
            self.smart_reminder = smart_reminder
        if reminder_start_hour is not None or reminder_end_hour is not None:
            self.set_reminder_window(
                reminder_start_hour if reminder_start_hour is not None else self.reminder_start_hour,
                reminder_end_hour if reminder_end_hour is not None else self.reminder_end_hour,
            )
        if auto_start is not None:
            self.auto_start = auto_start

def load_settings() -> SettingsStore:
    """
    Nuevo contrato: devuelve SettingsStore (QObject observable).
    """
    return SettingsStore(_load_settings_data())