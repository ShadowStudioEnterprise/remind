import os
from typing import Optional, List

from PyQt6.QtWidgets import QMessageBox

from remind.core.models import MigraineEntry
from remind.core.storage import load_history, save_history
from remind.services.export_csv import export_csv
from remind.services.export_pdf_report import export_pdf_report
from remind.services.diagnostics_report import build_diagnostics_zip
from remind.services.autostart import enable_autostart, disable_autostart
from remind.i18n import t
from remind.services.updater import (
    fetch_latest_json,
    is_update_available,
    download_and_verify_installer,
    run_installer,
)

class AppController:
    """
    Casos de uso (use-cases) de la app.
    No crea UI; recibe una referencia a la ventana para:
      - mostrar mensajes de error
      - usar statusBar()
    """

    def __init__(self, window, settings, entries: List[MigraineEntry]):
        self.w = window
        self.settings = settings
        self.entries = entries  # lista compartida con MainWindow

    # -------------------------
    # History
    # -------------------------

    def reload_history(self) -> None:
        self.entries[:] = load_history()
        self.w.refresh()
        self.w.statusBar().showMessage(t(self.settings, "status_history_reloaded"), 2000)

    def save_entry(self, had: bool, intensity: int, notes: str) -> bool:
        entry = MigraineEntry.now(had_migraine=had, intensity=intensity, notes=notes)
        self.entries.append(entry)

        try:
            save_history(self.entries)
        except Exception as e:
            QMessageBox.critical(
                self.w,
                t(self.settings, "err_title"),
                t(self.settings, "err_save_failed", error=str(e)),
            )
            return False

        self.w.refresh()
        self.w.statusBar().showMessage(t(self.settings, "status_saved"), 2000)
        return True

    # -------------------------
    # Exports
    # -------------------------

    def export_pdf(self, file_path: str, period_days: Optional[int]) -> bool:
        return export_pdf_report(
            entries=self.entries,
            path=file_path,
            settings=self.settings,
            period_days=period_days,
        )

    def export_csv(self, file_path: str) -> bool:
        return export_csv(self.entries, file_path)

    def export_diagnostics(self) -> Optional[str]:
        """
        Devuelve path del ZIP o None.
        """
        try:
            zip_path = build_diagnostics_zip(redact_notes=True)
            return str(zip_path)
        except Exception:
            return None

    # -------------------------
    # Autostart
    # -------------------------

    def set_autostart(self, enabled: bool) -> None:
        self.settings.auto_start = enabled
        if enabled:
            enable_autostart()
        else:
            disable_autostart()

    # -------------------------
    # Helpers UI
    # -------------------------

    def open_folder(self, folder_path: str) -> None:
        try:
            os.startfile(folder_path)  # Windows
        except Exception:
            pass
    
    def check_for_updates(self):
        try:
            latest = fetch_latest_json()
        except Exception as e:
            QMessageBox.warning(
                self.window,
                "Actualizaciones",
                f"No se pudo comprobar actualizaciones:\n{e}",
            )
            return

        if not is_update_available(latest.version):
            QMessageBox.information(
                self.window,
                "Actualizaciones",
                "Estás usando la última versión.",
            )
            return

        reply = QMessageBox.question(
            self.window,
            "Actualización disponible",
            f"Nueva versión disponible: {latest.version}\n\n"
            "¿Descargar e instalar ahora?",
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            installer_path = download_and_verify_installer(latest)
        except Exception as e:
            QMessageBox.critical(
                self.window,
                "Actualizaciones",
                f"Error descargando/verificando:\n{e}",
            )
            return

        run_installer(installer_path)
        self.window.close()