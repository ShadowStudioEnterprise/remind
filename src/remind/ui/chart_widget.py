from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QToolTip

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from remind.core.models import MigraineEntry
from remind.i18n import t


class ChartWidget(QWidget):
    """
    Matplotlib en PyQt6:
      - Toolbar (zoom/pan)
      - Tooltips i18n al hover
      - Tema dark/light coherente
    """

    def __init__(self, settings, parent=None):
        super().__init__(parent)

        self.settings = settings

        self.figure = Figure(figsize=(5, 3), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        self.entries: List[MigraineEntry] = []
        self.theme = "dark"

        self._points: List[Tuple[datetime, int]] = []
        self._last_tip_index: Optional[int] = None

        self.canvas.mpl_connect("motion_notify_event", self._on_motion)

        QToolTip.setFont(self.font())

    # -------------------------
    # API pública
    # -------------------------

    def set_entries(self, entries: List[MigraineEntry]):
        self.entries = entries or []
        self._draw()

    def apply_theme(self, theme: str):
        self.theme = (theme or "dark").lower()
        self._apply_toolbar_theme()
        self._draw()

    def apply_i18n(self):
        """
        Si cambias idioma en runtime, llama a esto para que los tooltips
        futuros salgan ya traducidos (no hace falta redibujar).
        """
        pass

    # -------------------------
    # Interno
    # -------------------------

    def _apply_toolbar_theme(self):
        dark = self.theme == "dark"
        if dark:
            self.toolbar.setStyleSheet("""
                QToolBar { background: #121214; border: 0px; }
                QToolButton { color: white; }
            """)
        else:
            self.toolbar.setStyleSheet("")

    def _moving_average(self, dates, values, window_days=7):
        ma_x = []
        ma_y = []
        for cur in dates:
            win_start = cur - timedelta(days=window_days)
            vals = [v for d, v in zip(dates, values) if win_start <= d <= cur]
            if vals:
                ma_x.append(cur)
                ma_y.append(sum(vals) / len(vals))
        return ma_x, ma_y

    def _extract_points(self) -> List[Tuple[datetime, int]]:
        pts = []
        for e in self.entries:
            if getattr(e, "had_migraine", False):
                try:
                    dt = datetime.fromisoformat(e.timestamp)
                    pts.append((dt, int(getattr(e, "intensity", 0))))
                except Exception:
                    continue
        pts.sort(key=lambda x: x[0])
        return pts

    def _draw(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        dark = self.theme == "dark"
        if dark:
            bg = "#121214"
            fg = "white"
            grid_alpha = 0.25
        else:
            bg = "white"
            fg = "#111111"
            grid_alpha = 0.25

        self.figure.patch.set_facecolor(bg)
        ax.set_facecolor(bg)

        ax.tick_params(colors=fg)
        for spine in ax.spines.values():
            spine.set_color(fg)
        ax.yaxis.label.set_color(fg)
        ax.xaxis.label.set_color(fg)
        ax.title.set_color(fg)

        self._points = self._extract_points()
        if not self._points:
            self.canvas.draw()
            return

        xs = [d for d, _ in self._points]
        ys = [v for _, v in self._points]

        ax.plot(xs, ys, linewidth=1.6, alpha=0.9)
        self._scatter = ax.scatter(xs, ys, s=22)

        if len(xs) >= 3:
            ma_x, ma_y = self._moving_average(xs, ys, 7)
            if len(ma_y) > 2:
                ax.plot(ma_x, ma_y, linestyle="--", linewidth=2, alpha=0.85)

        ax.set_ylim(0, 10)
        ax.grid(True, alpha=grid_alpha)

        self.figure.autofmt_xdate()
        self.figure.tight_layout()

        self._last_tip_index = None
        QToolTip.hideText()

        self.canvas.draw()

    def _on_motion(self, event):
        if not event.inaxes or not self._points:
            if self._last_tip_index is not None:
                self._last_tip_index = None
                QToolTip.hideText()
            return

        # Si está en modo zoom/pan, no mostramos tooltip
        mode = getattr(self.toolbar, "mode", "")
        if mode:
            if self._last_tip_index is not None:
                self._last_tip_index = None
                QToolTip.hideText()
            return

        ax = event.inaxes
        threshold_px = 12

        best_i = None
        best_d2 = None

        for i, (dt, intensity) in enumerate(self._points):
            xpix, ypix = ax.transData.transform((dt, intensity))
            dx = xpix - event.x
            dy = ypix - event.y
            d2 = dx * dx + dy * dy
            if best_d2 is None or d2 < best_d2:
                best_d2 = d2
                best_i = i

        if best_i is None or best_d2 is None or best_d2 > (threshold_px * threshold_px):
            if self._last_tip_index is not None:
                self._last_tip_index = None
                QToolTip.hideText()
            return

        if self._last_tip_index == best_i:
            return

        self._last_tip_index = best_i
        dt, intensity = self._points[best_i]

        dt_str = dt.strftime("%Y-%m-%d %H:%M")

        tip = (
            f"{t(self.settings, 'tooltip_datetime').format(dt=dt_str)}\n"
            f"{t(self.settings, 'tooltip_intensity').format(val=intensity)}"
        )

        if hasattr(event, "guiEvent") and event.guiEvent is not None:
            pos = event.guiEvent.globalPosition().toPoint()
            QToolTip.showText(pos, tip, self.canvas)
        else:
            QToolTip.showText(self.mapToGlobal(self.canvas.pos()), tip, self.canvas)