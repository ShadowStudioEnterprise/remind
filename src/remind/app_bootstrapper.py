import logging
import os
from typing import Optional

from PyQt6.QtWidgets import QApplication

from remind.core.settings import load_settings
from remind.core.storage import load_history

from remind.ui.main_window import MainWindow, PdfExportRequest, CsvExportRequest, EntryFormData
from remind.ui.ui_translator import MainWindowTranslator

from remind.controllers.app_controller import AppController
from remind.controllers.theme_controller import ThemeController
from remind.controllers.tray_controller import TrayController
from remind.controllers.notification_controller import NotificationController
from remind.controllers.dialog_controller import DialogController
from remind.i18n import t


class AppBootstrapper:
    """
    Encapsula toda la composición (DI/wiring) para que app.py sea mínimo.
    """

    def __init__(self, app: QApplication, logger: Optional[logging.Logger] = None):
        self.app = app
        self.logger = logger or logging.getLogger("remind")

        self.settings = None
        self.entries = None

        self.window = None
        self.translator = None

        self.app_controller = None
        self.theme_controller = None
        self.tray_controller = None
        self.notification_controller = None

    def build(self) -> MainWindow:
        # ===============================
        # MODEL
        # ===============================
        self.settings = load_settings()
        self.entries = load_history()

        # ===============================
        # VIEW
        # ===============================
        self.window = MainWindow(settings=self.settings)

        # ===============================
        # TRANSLATOR
        # ===============================
        self.translator = MainWindowTranslator(self.window, self.settings)
        self.translator.apply()

        # ===============================
        # CONTROLLERS
        # ===============================
        self.app_controller = AppController(
            window=self.window,
            settings=self.settings,
            entries=self.entries
        )

        self.theme_controller = ThemeController(
            app=self.app,
            settings=self.settings,
            window=self.window
        )

        self.tray_controller = TrayController(
            window=self.window,
            settings=self.settings
        )

        self.notification_controller = NotificationController(
            window=self.window,
            settings=self.settings,
            entries=self.entries,
            tray_controller=self.tray_controller
        )
        self.dialog_controller = DialogController(
            window=self.window,
            settings=self.settings,
            notification_port=self.notification_controller
        )
        # ===============================
        # WIRING (View -> Controllers)
        # ===============================
        self._wire_callbacks()

        # Render inicial
        self.window.set_entries(self.entries)

        return self.window

    # -----------------------------------
    # Wiring
    # -----------------------------------

    def _wire_callbacks(self):
        w = self.window
        s = self.settings
        appc = self.app_controller
        tray = self.tray_controller

        # Reload
        w.on_reload = appc.reload_history

        # Save entry
        def handle_save(form: EntryFormData):
            ok = appc.save_entry(form.had_migraine, form.intensity, form.notes)
            if ok:
                w.clear_notes()

        w.on_save_entry = handle_save

        # Autostart
        w.on_toggle_autostart = appc.set_autostart

        # Language
        def handle_language(lang: str):
            s.language = "en" if lang == "en" else "es"

        w.on_set_language = handle_language

        # Theme toggle (checked => dark)
        def handle_theme(checked: bool):
            s.theme = "dark" if checked else "light"

        w.on_toggle_theme = handle_theme

        # Export PDF
        def handle_export_pdf(req: PdfExportRequest):
            ok = appc.export_pdf(req.file_path, req.period_days)
            if ok:
                w.show_status(t(s, "export_success"), 3000)
            else:
                w.show_warning(t(s, "no_data_title"), t(s, "no_data_msg"))

        w.on_export_pdf = handle_export_pdf

        # Export CSV
        def handle_export_csv(req: CsvExportRequest):
            ok = appc.export_csv(req.file_path)
            if ok:
                w.show_status(t(s, "export_success"), 3000)
            else:
                w.show_warning(t(s, "no_data_title"), t(s, "no_data_msg"))

        w.on_export_csv = handle_export_csv

        # Diagnostics ZIP
        def handle_diag():
            zip_path = appc.export_diagnostics()
            if zip_path:
                w.show_status(t(s, "diag_export_ok"), 4000)
                # abrir carpeta contenedora
                try:
                    appc.open_folder(os.path.dirname(zip_path))
                except Exception:
                    pass
            else:
                w.show_error(t(s, "diag_export_err_title"), t(s, "diag_export_err_msg"))

        w.on_export_diag = handle_diag

        # About / Notifications:
        # Como View-only, el controller decide (aquí puedes integrar AboutDialog/IntervalDialog en controllers)
        w.on_open_about = self.dialog_controller.open_about
        w.on_open_notifications = self.dialog_controller.open_notifications

        # Close to tray
        w.on_close_to_tray = tray.show_running_message