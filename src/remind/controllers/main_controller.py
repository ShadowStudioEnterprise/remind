import os
from PyQt6.QtWidgets import QFileDialog, QInputDialog

from remind.i18n import t


class MainController:
    """
    Controlador que conecta MainWindow (View) con AppController (use cases).
    """

    def __init__(self, window, settings, entries, app_controller):
        self.w = window
        self.settings = settings
        self.entries = entries
        self.app = app_controller

        # Bind callbacks (View -> Controller)
        self.w.on_reload = self.reload
        self.w.on_save_entry = self.save_entry
        self.w.on_open_notifications = self.open_notifications_dialog
        self.w.on_toggle_autostart = self.toggle_autostart
        self.w.on_set_language = self.set_language
        self.w.on_toggle_theme = self.toggle_theme
        self.w.on_export_pdf = self.export_pdf
        self.w.on_export_csv = self.export_csv
        self.w.on_export_diag = self.export_diag
        self.w.on_open_about = self.open_about

        # Inicial
        self.w.set_entries(self.entries)

    def reload(self):
        self.app.reload_history()

    def save_entry(self, had: bool, intensity: int, notes: str):
        ok = self.app.save_entry(had, intensity, notes)
        if ok:
            self.w.clear_notes()

    def open_notifications_dialog(self):
        # Esto lo puede gestionar NotificationController; aquí lo dejamos como “router”
        self.w.on_open_notifications_dialog_impl()

    def toggle_autostart(self, enabled: bool):
        self.app.set_autostart(enabled)

    def set_language(self, lang: str):
        self.settings.language = "en" if lang == "en" else "es"

    def toggle_theme(self, checked: bool):
        self.settings.theme = "dark" if checked else "light"

    def export_pdf(self):
        options = [
            t(self.settings, "period_all"),
            t(self.settings, "period_30"),
            t(self.settings, "period_90"),
        ]
        choice, ok = QInputDialog.getItem(
            self.w,
            t(self.settings, "export_pdf_title"),
            t(self.settings, "export_period_prompt"),
            options, 0, False
        )
        if not ok:
            return

        if choice == options[1]:
            period_days = 30
        elif choice == options[2]:
            period_days = 90
        else:
            period_days = None

        file_path, _ = QFileDialog.getSaveFileName(
            self.w,
            t(self.settings, "export_pdf_title"),
            "re_mind_report.pdf",
            "PDF Files (*.pdf)"
        )
        if not file_path:
            return

        ok = self.app.export_pdf(file_path, period_days)
        if ok:
            self.w.show_status(t(self.settings, "export_success"), 3000)
        else:
            self.w.show_warning(t(self.settings, "no_data_title"), t(self.settings, "no_data_msg"))

    def export_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self.w,
            t(self.settings, "export_csv_title"),
            "re_mind_history.csv",
            "CSV Files (*.csv)"
        )
        if not file_path:
            return

        ok = self.app.export_csv(file_path)
        if ok:
            self.w.show_status(t(self.settings, "export_success"), 3000)
        else:
            self.w.show_warning(t(self.settings, "no_data_title"), t(self.settings, "no_data_msg"))

    def export_diag(self):
        zip_path = self.app.export_diagnostics()
        if zip_path:
            self.w.show_status(t(self.settings, "diag_export_ok"), 4000)
            self.app.open_folder(os.path.dirname(zip_path))
        else:
            self.w.show_error(t(self.settings, "diag_export_err_title"), t(self.settings, "diag_export_err_msg"))

    def open_about(self):
        self.w.on_open_about_dialog_impl()