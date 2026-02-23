from PyQt6.QtWidgets import QApplication

from remind.theme import apply_theme


class ThemeController:
    """
    Aplica tema global a la app y notifica/ajusta vistas que lo requieran.
    """

    def __init__(self, app: QApplication, settings, window=None):
        self.app = app
        self.settings = settings
        self.window = window  # View (opcional)

        # Estado inicial
        self.apply(self.settings.theme)

        # Reactivo
        if hasattr(self.settings, "theme_changed"):
            self.settings.theme_changed.connect(self.apply)

    def apply(self, theme: str):
        # 1) App palette / styles
        apply_theme(self.app, theme)

        # 2) Views que necesiten redibujar (matplotlib, etc.)
        if self.window is not None:
            if hasattr(self.window, "chart"):
                self.window.chart.apply_theme(theme)

            # Sincroniza check del menú si existe
            if hasattr(self.window, "act_dark_mode"):
                self.window.act_dark_mode.setChecked(theme == "dark")