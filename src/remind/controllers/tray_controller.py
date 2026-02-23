from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon

from remind.resources import resource_path
from remind.i18n import t


class TrayController:
    """
    Controla el System Tray:
      - icono + menú + textos i18n
      - abrir ventana / registro rápido / salir
      - mensaje "app sigue en segundo plano"
      - click en notificación -> quick register
    """

    def __init__(self, window, settings):
        self.w = window
        self.settings = settings

        self.tray = QSystemTrayIcon(self.w)
        self.tray.setIcon(QIcon(resource_path("assets/app.ico")))
        self.tray.setToolTip(t(self.settings, "app_name"))

        self.menu = QMenu()

        self.act_open = self.menu.addAction("")
        self.act_register = self.menu.addAction("")
        self.menu.addSeparator()
        self.act_exit = self.menu.addAction("")

        self.act_open.triggered.connect(self.show_from_tray)
        self.act_register.triggered.connect(self.quick_register)
        self.act_exit.triggered.connect(self.exit_app)

        self.tray.setContextMenu(self.menu)
        self.tray.activated.connect(self._tray_activated)

        # click en notificación (si backend lo soporta)
        try:
            self.tray.messageClicked.connect(self._notification_clicked)
        except Exception:
            pass

        self.tray.show()
        self.apply_i18n()

        # Reaccionar a cambios de idioma
        if hasattr(self.settings, "language_changed"):
            self.settings.language_changed.connect(lambda _lang: self.apply_i18n())

    # -------------------------
    # i18n
    # -------------------------

    def apply_i18n(self):
        self.act_open.setText(t(self.settings, "tray_open"))
        self.act_register.setText(t(self.settings, "tray_register"))
        self.act_exit.setText(t(self.settings, "tray_exit"))
        self.tray.setToolTip(t(self.settings, "app_name"))

    # -------------------------
    # API pública
    # -------------------------

    def show_from_tray(self):
        self.w.show()
        self.w.raise_()
        self.w.activateWindow()

    def quick_register(self):
        self.show_from_tray()
        # UX: activar modo registro rápido en el formulario
        if hasattr(self.w, "chk_had"):
            self.w.chk_had.setChecked(True)
        if hasattr(self.w, "spn_intensity") and self.w.spn_intensity.isVisible():
            self.w.spn_intensity.setFocus()
        elif hasattr(self.w, "txt_notes"):
            self.w.txt_notes.setFocus()

    def exit_app(self):
        self.tray.hide()
        QApplication.instance().quit()

    def show_running_message(self):
        if self.tray.isVisible():
            self.tray.showMessage(
                t(self.settings, "app_name"),
                t(self.settings, "tray_running"),
                QSystemTrayIcon.MessageIcon.Information,
                3000
            )

    def show_message(self, title: str, message: str, ms: int = 8000):
        if self.tray.isVisible():
            self.tray.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, ms)

    # -------------------------
    # Interno
    # -------------------------

    def _notification_clicked(self):
        self.quick_register()

    def _tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_from_tray()