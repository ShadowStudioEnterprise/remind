from PyQt6.QtCore import QObject, QTimer

class Notifier(QObject):
    def __init__(self, interval_minutes: int, callback, parent=None):
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.setInterval(interval_minutes * 60 * 1000)
        self._timer.timeout.connect(callback)

    def start(self):
        self._timer.start()

    def stop(self):
        self._timer.stop()

    def is_active(self) -> bool:
        return self._timer.isActive()

    def set_interval_minutes(self, minutes: int):
        self._timer.setInterval(minutes * 60 * 1000)