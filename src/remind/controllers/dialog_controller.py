from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol

from PyQt6.QtWidgets import QMessageBox

from remind.ui.dialog.about_dialog import AboutDialog
from remind.ui.dialog.interval_dialog import IntervalDialog
from remind.i18n import t


class NotificationSettingsPort(Protocol):
    """
    Puerto mínimo para aplicar cambios de notificaciones (sin acoplar a implementación).
    """
    def apply_dialog_values(self, enabled: bool, hours: int) -> None: ...


@dataclass(frozen=True)
class DialogResult:
    ok: bool


class DialogController:
    """
    Controlador de diálogos:
      - AboutDialog
      - IntervalDialog (notificaciones)
    Usa i18n (JSON) y muestra feedback en statusbar a través de la View.
    """

    def __init__(self, window, settings, notification_port: NotificationSettingsPort):
        self.w = window
        self.settings = settings
        self.notification_port = notification_port

    # -------------------------
    # About
    # -------------------------

    def open_about(self) -> DialogResult:
        try:
            AboutDialog(self.settings, self.w).exec()
            return DialogResult(ok=True)
        except Exception as e:
            QMessageBox.critical(
                self.w,
                t(self.settings, "err_title"),
                t(self.settings, "err_generic", error=str(e))
            )
            return DialogResult(ok=False)

    # -------------------------
    # Notifications
    # -------------------------

    def open_notifications(self) -> DialogResult:
        """
        Abre el diálogo de notificaciones y aplica valores vía NotificationSettingsPort.
        """
        try:
            dlg = IntervalDialog(
                self.settings,
                current_enabled=self.settings.notifications_enabled,
                current_hours=self.settings.notification_hours,
                parent=self.w
            )

            if not dlg.exec():
                return DialogResult(ok=False)

            enabled = dlg.get_enabled()
            hours = dlg.get_hours()

            self.notification_port.apply_dialog_values(enabled=enabled, hours=hours)

            # Feedback UX (statusbar)
            self.w.show_status(
                t(self.settings, "status_notif_on", hours=self.settings.notification_hours)
                if self.settings.notifications_enabled else t(self.settings, "status_notif_off"),
                3000
            )
            return DialogResult(ok=True)

        except Exception as e:
            QMessageBox.critical(
                self.w,
                t(self.settings, "err_title"),
                t(self.settings, "err_generic", error=str(e))
            )
            return DialogResult(ok=False)