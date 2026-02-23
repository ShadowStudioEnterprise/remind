from __future__ import annotations

from remind.i18n import t


class MainWindowTranslator:
    """
    Responsable exclusivo de aplicar textos i18n a MainWindow (View-only).
    """

    def __init__(self, window, settings):
        self.w = window
        self.settings = settings

        # Reaplicar automáticamente al cambiar idioma (si Settings expone señal)
        if hasattr(self.settings, "language_changed"):
            self.settings.language_changed.connect(lambda _lang: self.apply())

        # Opcional: refrescar textos dependientes del checkbox
        if hasattr(self.w, "chk_had"):
            try:
                self.w.chk_had.stateChanged.connect(lambda _v: self._form())
            except Exception:
                pass

    def apply(self):
        self._window()
        self._menus()
        self._actions()
        self._form()
        self._chart()
        self._export_dialog_strings()

    def _window(self):
        # Si ya tienes "app_name" como DISPLAY_NAME, perfecto.
        self.w.setWindowTitle(t(self.settings, "app_name"))

    def _menus(self):
        self.w.file_menu.setTitle(t(self.settings, "menu_file"))
        self.w.settings_menu.setTitle(t(self.settings, "menu_settings"))
        self.w.view_menu.setTitle(t(self.settings, "menu_view"))
        self.w.help_menu.setTitle(t(self.settings, "menu_help"))
        self.w.lang_menu.setTitle(t(self.settings, "menu_language"))

    def _actions(self):
        # Reload
        self.w.act_reload.setText(t(self.settings, "act_reload"))
        if hasattr(self.w.act_reload, "setStatusTip"):
            self.w.act_reload.setStatusTip(t(self.settings, "act_reload_tip"))

        # Notifications
        self.w.act_notifications.setText(t(self.settings, "act_notifications"))
        if hasattr(self.w.act_notifications, "setStatusTip"):
            self.w.act_notifications.setStatusTip(t(self.settings, "act_notifications_tip"))

        # Export
        self.w.act_export_pdf.setText(t(self.settings, "act_export_pdf"))
        # Normaliza la key: usa "act_export_csv" (más consistente)
        self.w.act_export_csv.setText(t(self.settings, "act_export_csv"))
        self.w.act_clear_notes.setText(t(self.settings, "act_clear_notes"))

        # Settings toggles
        self.w.act_about.setText(t(self.settings, "act_about"))
        self.w.act_autostart.setText(t(self.settings, "act_autostart"))
        self.w.act_dark_mode.setText(t(self.settings, "act_dark_mode"))

        # Diagnostics
        self.w.act_diag.setText(t(self.settings, "diag_export"))
        if hasattr(self.w.act_diag, "setStatusTip"):
            self.w.act_diag.setStatusTip(t(self.settings, "diag_export_tip"))

        # ✅ NEW: Updater
        if hasattr(self.w, "act_check_updates"):
            self.w.act_check_updates.setText(t(self.settings, "act_check_updates"))
            if hasattr(self.w.act_check_updates, "setStatusTip"):
                self.w.act_check_updates.setStatusTip(t(self.settings, "act_check_updates_tip"))

        # Language actions
        self.w.act_lang_es.setText(t(self.settings, "lang_es"))
        self.w.act_lang_en.setText(t(self.settings, "lang_en"))

        self._sync_language_checks()

    def _form(self):
        self.w.form_box.setTitle(t(self.settings, "group_record"))
        self.w.chk_had.setText(t(self.settings, "chk_had"))
        self.w.lbl_intensity.setText(t(self.settings, "lbl_intensity"))
        self.w.btn_save.setText(t(self.settings, "btn_save"))

        # Notas/estado dependiente de checkbox
        try:
            had = self.w.chk_had.isChecked()
        except Exception:
            had = True

        if had:
            self.w.lbl_notes.setText(t(self.settings, "lbl_notes"))
            self.w.txt_notes.setPlaceholderText(t(self.settings, "ph_notes_migraine"))
        else:
            # Si quieres “estado” cuando NO hay migraña, está bien
            self.w.lbl_notes.setText(t(self.settings, "lbl_state"))
            self.w.txt_notes.setPlaceholderText(t(self.settings, "ph_notes_nomigraine"))

    def _chart(self):
        if not hasattr(self.w, "chart"):
            return

        # Mantén compatibilidad con ambas firmas: apply_i18n() o apply_i18n(settings)
        try:
            self.w.chart.apply_i18n(self.settings)
        except TypeError:
            try:
                self.w.chart.apply_i18n()
            except Exception:
                pass

    def _export_dialog_strings(self):
        """
        Strings que la View-only usa para mostrar diálogos sin conocer t().
        """
        # PDF
        self.w._pdf_period_title = t(self.settings, "export_pdf_title")
        self.w._pdf_period_prompt = t(self.settings, "export_period_prompt")
        self.w._pdf_period_options = [
            t(self.settings, "period_all"),
            t(self.settings, "period_30"),
            t(self.settings, "period_90"),
        ]
        self.w._pdf_save_title = t(self.settings, "export_pdf_title")

        # CSV
        self.w._csv_save_title = t(self.settings, "export_csv_title")

    def _sync_language_checks(self):
        lang = getattr(self.settings, "language", "es")
        is_es = (lang == "es")
        self.w.act_lang_es.setChecked(is_es)
        self.w.act_lang_en.setChecked(not is_es)