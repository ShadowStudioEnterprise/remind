from datetime import datetime, timedelta

from PyQt6.QtWidgets import QSystemTrayIcon

from plyer import notification as plyer_notification

from remind.services.notifications import Notifier
from remind.resources import resource_path
from remind.i18n import t


class NotificationController:
    """
    Controla notificaciones:
      - Notifier (timer)
      - smart reminder
      - envío por tray si existe, si no plyer
      - reacciona a cambios de settings
    """

    def __init__(self, window, settings, entries, tray_controller=None):
        self.w = window
        self.settings = settings
        self.entries = entries
        self.tray_controller = tray_controller  # puede ser None

        self.notifier = Notifier(
            interval_minutes=self.settings.notification_hours * 60,
            callback=self.notify_reminder,
            parent=self.w
        )

        # Reacciona a cambios
        if hasattr(self.settings, "notifications_enabled_changed"):
            self.settings.notifications_enabled_changed.connect(self._on_enabled_changed)
        if hasattr(self.settings, "notification_hours_changed"):
            self.settings.notification_hours_changed.connect(self._on_hours_changed)

        # Estado inicial
        if self.settings.notifications_enabled:
            self.notifier.start()

    # -------------------------
    # Reactividad
    # -------------------------

    def _on_enabled_changed(self, enabled: bool):
        if enabled:
            self.notifier.start()
        else:
            self.notifier.stop()

    def _on_hours_changed(self, hours: int):
        self.notifier.set_interval_minutes(hours * 60)

    # -------------------------
    # API pública (para UI)
    # -------------------------

    def apply_dialog_values(self, enabled: bool, hours: int):
        # Estas asignaciones disparan señales + autosave (si lo tienes)
        self.settings.notifications_enabled = bool(enabled)
        self.settings.notification_hours = int(hours)

    # -------------------------
    # Lógica principal
    # -------------------------

    def notify_reminder(self):
        if not self.settings.notifications_enabled:
            return

        # Smart reminder
        if getattr(self.settings, "smart_reminder", False):
            now = datetime.now()

            # ventana horaria
            try:
                if not (self.settings.reminder_start_hour <= now.hour <= self.settings.reminder_end_hour):
                    return
            except Exception:
                pass

            # evitar notificar si registró hace menos de X horas
            if self.entries:
                try:
                    last = max(self.entries, key=lambda e: e.timestamp)
                    last_dt = datetime.fromisoformat(last.timestamp)
                    if now - last_dt < timedelta(hours=self.settings.notification_hours):
                        return
                except Exception:
                    pass

        title = t(self.settings, "app_name")
        message = t(self.settings, "notif_message")

        # Preferencia: tray si existe y está visible
        if self.tray_controller is not None:
            self.tray_controller.show_message(title, message, ms=8000)
            return

        # Fallback plyer
        plyer_notification.notify(
            title=title,
            message=message,
            app_name=title,
            app_icon=resource_path("assets/app.ico"),
            timeout=10
        )