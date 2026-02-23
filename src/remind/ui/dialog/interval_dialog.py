from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QSpinBox, QSlider, QPushButton, QCheckBox
)
from PyQt6.QtCore import Qt

from remind.i18n import t


class IntervalDialog(QDialog):
    """
    Diálogo para configurar notificaciones:
      - Toggle ON/OFF
      - Intervalo en horas (1-24)
      - Presets rápidos
      - Slider y SpinBox sincronizados
    """
    def __init__(self, settings, current_enabled: bool, current_hours: int, parent=None):
        super().__init__(parent)
        self.settings = settings

        self.setModal(True)
        self.setMinimumWidth(360)

        # Normaliza entrada
        current_hours = max(1, min(24, int(current_hours)))

        layout = QVBoxLayout(self)

        # Title + desc
        self.lbl_title = QLabel()
        self.lbl_title.setStyleSheet("font-weight: 600; font-size: 14px;")
        layout.addWidget(self.lbl_title)

        self.lbl_desc = QLabel()
        self.lbl_desc.setWordWrap(True)
        layout.addWidget(self.lbl_desc)

        # Toggle
        self.chk_enabled = QCheckBox()
        self.chk_enabled.setChecked(bool(current_enabled))
        self.chk_enabled.stateChanged.connect(self._on_enabled_changed)
        layout.addWidget(self.chk_enabled)

        # Controles de intervalo
        grid = QGridLayout()
        layout.addLayout(grid)

        self.lbl_interval = QLabel()

        self.spn_hours = QSpinBox()
        self.spn_hours.setRange(1, 24)
        self.spn_hours.setValue(current_hours)

        self.sld_hours = QSlider(Qt.Orientation.Horizontal)
        self.sld_hours.setRange(1, 24)
        self.sld_hours.setValue(current_hours)
        self.sld_hours.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.sld_hours.setTickInterval(1)

        # Sync bidireccional (sin bucles)
        self.spn_hours.valueChanged.connect(self._sync_from_spin)
        self.sld_hours.valueChanged.connect(self._sync_from_slider)

        grid.addWidget(self.lbl_interval, 0, 0)
        grid.addWidget(self.spn_hours, 0, 1)
        grid.addWidget(self.sld_hours, 1, 0, 1, 2)

        # Presets rápidos
        presets_row = QHBoxLayout()
        layout.addLayout(presets_row)

        self.lbl_presets = QLabel()
        presets_row.addWidget(self.lbl_presets)

        self.preset_buttons = []
        for h in (6, 8, 12, 24):
            btn = QPushButton()
            btn.setMinimumWidth(60)
            btn.clicked.connect(lambda _, hh=h: self._apply_preset(hh))
            self.preset_buttons.append((h, btn))
            presets_row.addWidget(btn)

        presets_row.addStretch()

        # Botones OK/Cancel
        btn_row = QHBoxLayout()
        layout.addLayout(btn_row)

        self.btn_cancel = QPushButton()
        self.btn_ok = QPushButton()
        self.btn_ok.setDefault(True)

        self.btn_cancel.clicked.connect(self.reject)
        self.btn_ok.clicked.connect(self.accept)

        btn_row.addStretch()
        btn_row.addWidget(self.btn_cancel)
        btn_row.addWidget(self.btn_ok)

        # Aplicar i18n y estado inicial
        self.apply_i18n()
        self._on_enabled_changed()

    def apply_i18n(self):
        # Ventana
        self.setWindowTitle(t(self.settings, "dlg_notif_title"))

        # Textos
        self.lbl_title.setText(t(self.settings, "dlg_notif_subtitle"))
        self.lbl_desc.setText(t(self.settings, "dlg_notif_desc"))
        self.chk_enabled.setText(t(self.settings, "dlg_notif_toggle"))
        self.lbl_interval.setText(t(self.settings, "dlg_notif_interval"))
        self.lbl_presets.setText(t(self.settings, "dlg_presets"))

        # Sufijo horas: ES " h", EN " h" (puedes cambiar a " hr" si quieres)
        self.spn_hours.setSuffix(" h")

        # Presets: mantener "6h" en ambos idiomas (universal)
        for h, btn in self.preset_buttons:
            btn.setText(f"{h}h")

        # Botones
        self.btn_cancel.setText(t(self.settings, "btn_cancel"))
        self.btn_ok.setText(t(self.settings, "btn_save_cfg"))

    def _sync_from_spin(self, value: int):
        if self.sld_hours.value() != value:
            self.sld_hours.blockSignals(True)
            self.sld_hours.setValue(value)
            self.sld_hours.blockSignals(False)

    def _sync_from_slider(self, value: int):
        if self.spn_hours.value() != value:
            self.spn_hours.blockSignals(True)
            self.spn_hours.setValue(value)
            self.spn_hours.blockSignals(False)

    def _apply_preset(self, hours: int):
        self.spn_hours.setValue(hours)  # ya sincroniza el slider

    def _on_enabled_changed(self):
        enabled = self.chk_enabled.isChecked()
        self.spn_hours.setEnabled(enabled)
        self.sld_hours.setEnabled(enabled)

    def get_enabled(self) -> bool:
        return self.chk_enabled.isChecked()

    def get_hours(self) -> int:
        return self.spn_hours.value()