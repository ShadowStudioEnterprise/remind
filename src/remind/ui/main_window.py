from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, Sequence

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QGroupBox, QFormLayout,
    QCheckBox, QSpinBox, QLineEdit, QPushButton, QMessageBox,
    QToolBar, QStatusBar, QLabel, QMenu, QFileDialog, QInputDialog
)
from PyQt6.QtGui import QAction, QIcon

from remind.ui.chart_widget import ChartWidget
from remind.resources import resource_path


# ==========================
# DTOs (View <-> Controller)
# ==========================

@dataclass(frozen=True)
class EntryFormData:
    had_migraine: bool
    intensity: int
    notes: str


@dataclass(frozen=True)
class PdfExportRequest:
    period_days: Optional[int]          # None | 30 | 90
    file_path: str


@dataclass(frozen=True)
class CsvExportRequest:
    file_path: str


# ==========================
# View-only MainWindow
# ==========================

class MainWindow(QMainWindow):
    """
    VIEW-ONLY:
      - Construye widgets
      - Expone eventos (callbacks) de usuario
      - Expone métodos de UI (set_entries, dialogs, mensajes)
      - NO contiene: lógica negocio, i18n, theme, storage, notificaciones, tray
    """

    # --------- Event callbacks (Controller wires these) ---------
    on_reload: Optional[Callable[[], None]] = None
    on_save_entry: Optional[Callable[[EntryFormData], None]] = None
    on_open_notifications: Optional[Callable[[], None]] = None
    on_toggle_autostart: Optional[Callable[[bool], None]] = None
    on_set_language: Optional[Callable[[str], None]] = None          # "es"|"en"
    on_toggle_theme: Optional[Callable[[bool], None]] = None         # checked => dark
    on_export_pdf: Optional[Callable[[PdfExportRequest], None]] = None
    on_export_csv: Optional[Callable[[CsvExportRequest], None]] = None
    on_export_diag: Optional[Callable[[], None]] = None
    on_open_about: Optional[Callable[[], None]] = None
    on_check_updates: Optional[Callable[[], None]] = None            # NEW: updater flow
    on_close_to_tray: Optional[Callable[[], None]] = None            # optional: tray controller handles

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings

        # Branding/icon
        self.setWindowIcon(QIcon(resource_path("assets/app.ico")))

        # UI
        self._build_toolbar()
        self.setStatusBar(QStatusBar(self))
        self._build_ui()

        # Defaults synced from settings (no theme apply here)
        self.act_autostart.setChecked(bool(getattr(self.settings, "auto_start", False)))
        self.act_dark_mode.setChecked(getattr(self.settings, "theme", "dark") == "dark")
        self._sync_language_checks(getattr(self.settings, "language", "es"))

        # ---- i18n-injected dialog strings (Translator sets these) ----
        # PDF dialogs
        self._pdf_period_title = "Export"
        self._pdf_period_prompt = "Select period"
        self._pdf_period_options = ["All", "30 days", "90 days"]
        self._pdf_save_title = "Export PDF"
        # CSV dialogs
        self._csv_save_title = "Export CSV"

    # ==========================================================
    # i18n application hook (Translator calls this)
    # ==========================================================

    def apply_texts(
        self,
        *,
        window_title: str,
        # Menus
        menu_file: str,
        menu_settings: str,
        menu_view: str,
        menu_help: str,
        # Language menu
        menu_language: str,
        lang_es: str,
        lang_en: str,
        # Actions
        act_reload: str,
        act_notifications: str,
        act_autostart: str,
        act_dark_mode: str,
        act_export_pdf: str,
        act_export_csv: str,
        act_clear_notes: str,
        act_about: str,
        act_diag: str,
        act_check_updates: str,
        # Form
        form_group_title: str,
        chk_had_text: str,
        lbl_intensity: str,
        lbl_notes: str,
        txt_notes_ph: str,
        btn_save: str,
        # Dialog text packs
        pdf_period_title: str,
        pdf_period_prompt: str,
        pdf_period_options: Sequence[str],
        pdf_save_title: str,
        csv_save_title: str,
    ) -> None:
        """
        Translator debería llamar a esto para aplicar i18n de golpe.
        Aquí NO se usa t(), solo se aplican strings ya traducidas.
        """
        self.setWindowTitle(window_title)

        # Menus
        self.file_menu.setTitle(menu_file)
        self.settings_menu.setTitle(menu_settings)
        self.view_menu.setTitle(menu_view)
        self.help_menu.setTitle(menu_help)

        # Language menu
        self.lang_menu.setTitle(menu_language)
        self.act_lang_es.setText(lang_es)
        self.act_lang_en.setText(lang_en)

        # Actions
        self.act_reload.setText(act_reload)
        self.act_notifications.setText(act_notifications)
        self.act_autostart.setText(act_autostart)
        self.act_dark_mode.setText(act_dark_mode)
        self.act_export_pdf.setText(act_export_pdf)
        self.act_export_csv.setText(act_export_csv)
        self.act_clear_notes.setText(act_clear_notes)
        self.act_about.setText(act_about)
        self.act_diag.setText(act_diag)
        self.act_check_updates.setText(act_check_updates)

        # Form
        self.form_box.setTitle(form_group_title)
        self.chk_had.setText(chk_had_text)
        self.lbl_intensity.setText(lbl_intensity)
        self.lbl_notes.setText(lbl_notes)
        self.txt_notes.setPlaceholderText(txt_notes_ph)
        self.btn_save.setText(btn_save)

        # Dialog strings (used by view helpers)
        self._pdf_period_title = pdf_period_title
        self._pdf_period_prompt = pdf_period_prompt
        self._pdf_period_options = list(pdf_period_options)
        self._pdf_save_title = pdf_save_title
        self._csv_save_title = csv_save_title

    # ==========================================================
    # BUILD
    # ==========================================================

    def _build_toolbar(self):
        self.toolbar = QToolBar("Main")
        self.addToolBar(self.toolbar)

        # Actions (stored as attributes so Translator can set text)
        self.act_reload = QAction(QIcon(resource_path("assets/bug.png")), "", self)
        self.act_reload.triggered.connect(self._emit_reload)
        self.toolbar.addAction(self.act_reload)

        self.toolbar.addSeparator()

        self.act_notifications = QAction("", self)
        self.act_notifications.triggered.connect(self._emit_open_notifications)
        self.toolbar.addAction(self.act_notifications)

        self.toolbar.addSeparator()

        self.act_export_pdf = QAction("", self)
        self.act_export_pdf.triggered.connect(self._emit_export_pdf)
        self.toolbar.addAction(self.act_export_pdf)

        self.toolbar.addSeparator()

        self.act_export_csv = QAction("", self)
        self.act_export_csv.triggered.connect(self._emit_export_csv)
        self.toolbar.addAction(self.act_export_csv)

        self.toolbar.addSeparator()

        self.act_clear_notes = QAction("", self)
        self.act_clear_notes.triggered.connect(self.clear_notes)
        self.toolbar.addAction(self.act_clear_notes)

        # Menús
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("")
        self.settings_menu = self.menu.addMenu("")
        self.view_menu = self.menu.addMenu("")
        self.help_menu = self.menu.addMenu("")

        # File
        self.file_menu.addAction(self.act_reload)
        self.file_menu.addAction(self.act_export_pdf)
        self.file_menu.addAction(self.act_export_csv)

        # Settings
        self.settings_menu.addAction(self.act_notifications)

        self.act_autostart = QAction("", self)
        self.act_autostart.setCheckable(True)
        self.act_autostart.triggered.connect(self._emit_toggle_autostart)
        self.settings_menu.addAction(self.act_autostart)

        # View: theme
        self.act_dark_mode = QAction("", self)
        self.act_dark_mode.setCheckable(True)
        self.act_dark_mode.triggered.connect(self._emit_toggle_theme)
        self.view_menu.addAction(self.act_dark_mode)

        # View: language submenu
        self.lang_menu = QMenu("", self)
        self.view_menu.addMenu(self.lang_menu)

        self.act_lang_es = QAction("", self)
        self.act_lang_es.setCheckable(True)
        self.act_lang_es.triggered.connect(lambda: self._emit_set_language("es"))

        self.act_lang_en = QAction("", self)
        self.act_lang_en.setCheckable(True)
        self.act_lang_en.triggered.connect(lambda: self._emit_set_language("en"))

        self.lang_menu.addAction(self.act_lang_es)
        self.lang_menu.addAction(self.act_lang_en)

        # Help: Check updates (NEW)
        self.act_check_updates = QAction("", self)
        self.act_check_updates.triggered.connect(self._emit_check_updates)
        self.help_menu.addAction(self.act_check_updates)

        # Help: About / Diagnostics
        self.act_about = QAction("", self)
        self.act_about.triggered.connect(self._emit_open_about)
        self.help_menu.addAction(self.act_about)

        self.act_diag = QAction("", self)
        self.act_diag.triggered.connect(self._emit_export_diag)
        self.help_menu.addAction(self.act_diag)

    def _build_ui(self):
        central = QWidget()
        root = QHBoxLayout(central)

        # Form
        self.form_box = QGroupBox("")
        form_layout = QFormLayout(self.form_box)

        self.chk_had = QCheckBox("")
        self.chk_had.setChecked(True)
        self.chk_had.stateChanged.connect(self._toggle_intensity)

        self.lbl_intensity = QLabel("")
        self.spn_intensity = QSpinBox()
        self.spn_intensity.setRange(1, 10)
        self.spn_intensity.setValue(5)

        self.lbl_notes = QLabel("")
        self.txt_notes = QLineEdit()

        self.btn_save = QPushButton("")
        self.btn_save.clicked.connect(self._emit_save_entry)

        form_layout.addRow(self.chk_had)
        form_layout.addRow(self.lbl_intensity, self.spn_intensity)
        form_layout.addRow(self.lbl_notes, self.txt_notes)
        form_layout.addRow(self.btn_save)

        # Chart
        self.chart = ChartWidget(settings=self.settings)
        form_layout.addWidget(self.chart)

        root.addWidget(self.form_box, 1)
        self.setCentralWidget(central)

        self._toggle_intensity()

    # ==========================================================
    # Public View API (Controller calls)
    # ==========================================================

    def set_entries(self, entries) -> None:
        self.chart.set_entries(entries)

    def clear_notes(self) -> None:
        self.txt_notes.clear()

    def set_dark_checked(self, dark: bool) -> None:
        self.act_dark_mode.setChecked(bool(dark))

    def set_autostart_checked(self, enabled: bool) -> None:
        self.act_autostart.setChecked(bool(enabled))

    def set_language_checked(self, lang: str) -> None:
        self._sync_language_checks(lang)

    def show_status(self, text: str, ms: int = 2000) -> None:
        self.statusBar().showMessage(text, ms)

    def show_error(self, title: str, msg: str) -> None:
        QMessageBox.critical(self, title, msg)

    def show_warning(self, title: str, msg: str) -> None:
        QMessageBox.warning(self, title, msg)

    def show_info(self, title: str, msg: str) -> None:
        QMessageBox.information(self, title, msg)

    # ---- Dialog helpers (View decides how to ask the user) ----

    def ask_period(self, title: str, prompt: str, options: Sequence[str]) -> Optional[int]:
        """
        Devuelve index de opción o None si cancelado.
        """
        choice, ok = QInputDialog.getItem(self, title, prompt, list(options), 0, False)
        if not ok:
            return None
        try:
            return list(options).index(choice)
        except ValueError:
            return 0

    def ask_save_file(self, title: str, default_name: str, filter_str: str) -> Optional[str]:
        file_path, _ = QFileDialog.getSaveFileName(self, title, default_name, filter_str)
        return file_path or None

    # ==========================================================
    # Form logic (View-only UX)
    # ==========================================================

    def _toggle_intensity(self):
        had = self.chk_had.isChecked()
        self.lbl_intensity.setVisible(had)
        self.spn_intensity.setVisible(had)
        self.spn_intensity.setEnabled(had)
        if had and self.spn_intensity.value() < 1:
            self.spn_intensity.setValue(5)

    def read_form(self) -> EntryFormData:
        had = self.chk_had.isChecked()
        intensity = int(self.spn_intensity.value()) if had else 0
        notes = self.txt_notes.text()
        return EntryFormData(had_migraine=had, intensity=intensity, notes=notes)

    # ==========================================================
    # Emit events to Controller
    # ==========================================================

    def _emit_reload(self):
        if self.on_reload:
            self.on_reload()

    def _emit_save_entry(self):
        if self.on_save_entry:
            self.on_save_entry(self.read_form())

    def _emit_open_notifications(self):
        if self.on_open_notifications:
            self.on_open_notifications()

    def _emit_toggle_autostart(self, checked: bool):
        if self.on_toggle_autostart:
            self.on_toggle_autostart(bool(checked))

    def _emit_set_language(self, lang: str):
        self._sync_language_checks(lang)
        if self.on_set_language:
            self.on_set_language(lang)

    def _emit_toggle_theme(self, checked: bool):
        if self.on_toggle_theme:
            self.on_toggle_theme(bool(checked))

    def _emit_check_updates(self):
        if self.on_check_updates:
            self.on_check_updates()

    def _emit_export_pdf(self):
        """
        View solicita input (periodo + path) y emite un request DTO.
        Los textos (title/prompt/options) ya están i18n-inyectados por Translator.
        """
        if not self.on_export_pdf:
            return

        idx = self.ask_period(
            self._pdf_period_title,
            self._pdf_period_prompt,
            self._pdf_period_options,
        )
        if idx is None:
            return

        # mapping index->days
        period_days = None
        if idx == 1:
            period_days = 30
        elif idx == 2:
            period_days = 90

        file_path = self.ask_save_file(
            self._pdf_save_title,
            "re_mind_report.pdf",
            "PDF Files (*.pdf)"
        )
        if not file_path:
            return

        self.on_export_pdf(PdfExportRequest(period_days=period_days, file_path=file_path))

    def _emit_export_csv(self):
        if not self.on_export_csv:
            return

        file_path = self.ask_save_file(
            self._csv_save_title,
            "re_mind_history.csv",
            "CSV Files (*.csv)"
        )
        if not file_path:
            return

        self.on_export_csv(CsvExportRequest(file_path=file_path))

    def _emit_export_diag(self):
        if self.on_export_diag:
            self.on_export_diag()

    def _emit_open_about(self):
        if self.on_open_about:
            self.on_open_about()

    # ==========================================================
    # Language checks (View-only)
    # ==========================================================

    def _sync_language_checks(self, lang: str):
        is_es = (lang == "es")
        self.act_lang_es.setChecked(is_es)
        self.act_lang_en.setChecked(not is_es)

    # ==========================================================
    # Close behavior (delegable)
    # ==========================================================

    def closeEvent(self, event):
        """
        View-only: delega al controller si quiere "close to tray".
        """
        if self.on_close_to_tray:
            event.ignore()
            self.hide()
            self.on_close_to_tray()
            return
        super().closeEvent(event)