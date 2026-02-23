from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from remind.i18n import t
from remind.brand import DISPLAY_NAME, VERSION


class AboutDialog(QDialog):
    """
    Dialogo informativo simple.
    No contiene lógica.
    """

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings

        self.setModal(True)
        self.setMinimumWidth(320)

        layout = QVBoxLayout(self)

        self.lbl_title = QLabel()
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))

        self.lbl_version = QLabel()
        self.lbl_version.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_desc = QLabel()
        self.lbl_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_desc.setWordWrap(True)

        self.btn_close = QPushButton()
        self.btn_close.clicked.connect(self.accept)

        layout.addWidget(self.lbl_title)
        layout.addWidget(self.lbl_version)
        layout.addWidget(self.lbl_desc)
        layout.addSpacing(10)
        layout.addWidget(self.btn_close)

        self.apply_i18n()

    def apply_i18n(self):
        self.setWindowTitle(t(self.settings, "about_title"))
        self.lbl_title.setText(DISPLAY_NAME)
        self.lbl_version.setText(f"{t(self.settings, 'about_version')}: {VERSION}")
        self.lbl_desc.setText(t(self.settings, "about_description"))
        self.btn_close.setText(t(self.settings, "btn_close"))