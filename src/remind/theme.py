from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication


def apply_theme(app: QApplication, theme: str) -> None:
    """
    theme: 'dark' | 'light'
    """
    theme = (theme or "light").lower().strip()
    if theme == "dark":
        _apply_dark(app)
    else:
        _apply_light(app)


def _apply_light(app: QApplication) -> None:
    app.setPalette(QPalette())
    app.setStyleSheet("")


def _apply_dark(app: QApplication) -> None:
    palette = QPalette()

    # Base
    palette.setColor(QPalette.ColorRole.Window, QColor(24, 24, 27))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor(18, 18, 20))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(28, 28, 32))
    palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)

    # Text
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, QColor(32, 32, 36))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)

    # Links / highlights
    palette.setColor(QPalette.ColorRole.Link, QColor(120, 160, 255))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(80, 110, 200))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)

    # Disabled
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(160, 160, 160))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(160, 160, 160))

    app.setPalette(palette)

    # Extra: widgets “bonitos”
    app.setStyleSheet("""
        QToolTip { color: #ffffff; background-color: #2b2b2f; border: 1px solid #3a3a40; }
        QGroupBox { border: 1px solid rgba(255,255,255,40); border-radius: 8px; margin-top: 10px; }
        QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; color: rgba(255,255,255,210); }
        QLineEdit, QSpinBox {
            background: rgba(255,255,255,18);
            border: 1px solid rgba(255,255,255,35);
            border-radius: 8px;
            padding: 6px;
        }
        QPushButton {
            background: rgba(255,255,255,18);
            border: 1px solid rgba(255,255,255,35);
            border-radius: 10px;
            padding: 8px 12px;
        }
        QPushButton:hover { background: rgba(255,255,255,24); }
        QPushButton:pressed { background: rgba(255,255,255,14); }
        QMenu { background: #1f1f23; border: 1px solid rgba(255,255,255,25); }
        QMenu::item:selected { background: rgba(255,255,255,18); }
        QStatusBar { color: rgba(255,255,255,210); }
    """)