from __future__ import annotations

from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QProgressBar, QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect
)
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve

from remind.resources import resource_path
from remind.i18n import t


class SplashWidget(QWidget):
    """
    Splash premium con fade + progreso + status.
    i18n:
      - recibe settings (fuente única de idioma)
      - usa t(settings, key)
      - permite refrescar textos con apply_i18n()
    """

    def __init__(self, settings, version: str, parent=None):
        super().__init__(parent)

        self.settings = settings
        self._status_key: Optional[str] = "loading"  # clave por defecto

        # Ventana sin bordes, siempre arriba
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        # Imagen splash
        self.pixmap = QPixmap(resource_path("assets/splash.png"))
        if self.pixmap.isNull():
            raise FileNotFoundError("No se pudo cargar assets/splash.png")

        self.image = QLabel(self)
        self.image.setPixmap(self.pixmap)
        self.image.setFixedSize(self.pixmap.size())
        self.image.setAlignment(Qt.AlignmentFlag.AlignCenter)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(self.image)

        # Status
        self.status = QLabel(self.image)
        self.status.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
        self.status.setFont(QFont("Segoe UI", 11))
        self.status.setStyleSheet("color: rgba(255,255,255,230);")
        self.status.setWordWrap(True)
        self.status.setFixedWidth(self.pixmap.width() - 40)
        self.status.move(20, self.pixmap.height() - 95)

        status_shadow = QGraphicsDropShadowEffect(self.status)
        status_shadow.setBlurRadius(18)
        status_shadow.setOffset(0, 2)
        status_shadow.setColor(Qt.GlobalColor.black)
        self.status.setGraphicsEffect(status_shadow)

        # Versión
        self.version = QLabel(self.image)
        self.version.setText(version)
        self.version.setFont(QFont("Segoe UI", 9))
        self.version.setStyleSheet("color: rgba(255,255,255,160);")
        self.version.adjustSize()
        self.version.move(self.pixmap.width() - self.version.width() - 14, self.pixmap.height() - 28)

        version_shadow = QGraphicsDropShadowEffect(self.version)
        version_shadow.setBlurRadius(12)
        version_shadow.setOffset(0, 2)
        version_shadow.setColor(Qt.GlobalColor.black)
        self.version.setGraphicsEffect(version_shadow)

        # Progreso
        self.progress = QProgressBar(self.image)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedWidth(self.pixmap.width() - 40)
        self.progress.setFixedHeight(10)
        self.progress.move(20, self.pixmap.height() - 55)

        self.progress.setStyleSheet("""
            QProgressBar {
                border: 0px;
                border-radius: 5px;
                background: rgba(255,255,255,40);
            }
            QProgressBar::chunk {
                border-radius: 5px;
                background: rgba(255,255,255,180);
            }
        """)

        # Fade
        self.opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity)
        self.opacity.setOpacity(0.0)

        self.fade_in_anim = QPropertyAnimation(self.opacity, b"opacity")
        self.fade_in_anim.setDuration(280)
        self.fade_in_anim.setStartValue(0.0)
        self.fade_in_anim.setEndValue(1.0)
        self.fade_in_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.fade_out_anim = QPropertyAnimation(self.opacity, b"opacity")
        self.fade_out_anim.setDuration(220)
        self.fade_out_anim.setStartValue(1.0)
        self.fade_out_anim.setEndValue(0.0)
        self.fade_out_anim.setEasingCurve(QEasingCurve.Type.InCubic)

        self.resize(self.pixmap.size())

        # Si cambia idioma durante splash, refresca status por key
        if hasattr(self.settings, "language_changed"):
            self.settings.language_changed.connect(lambda _lang: self.apply_i18n())

        self.apply_i18n()

    def apply_i18n(self) -> None:
        if self._status_key:
            self.status.setText(t(self.settings, self._status_key))

    def center_on_screen(self, app):
        screen = app.primaryScreen().availableGeometry()
        x = screen.center().x() - self.width() // 2
        y = screen.center().y() - self.height() // 2
        self.move(x, y)

    def show_with_fade_in(self, app):
        self.center_on_screen(app)
        self.show()
        self.fade_in_anim.start()

    def close_with_fade_out(self, on_finished=None):
        if on_finished:
            self.fade_out_anim.finished.connect(on_finished)
        self.fade_out_anim.start()

    def set_status(self, text: str) -> None:
        self._status_key = None
        self.status.setText(text)

    def set_status_key(self, key: str) -> None:
        self._status_key = key
        self.status.setText(t(self.settings, key))

    def set_progress(self, value: int):
        self.progress.setValue(max(0, min(100, int(value))))