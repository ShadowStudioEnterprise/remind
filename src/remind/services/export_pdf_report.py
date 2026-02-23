import io
from dataclasses import asdict
from datetime import datetime, timedelta, date
from typing import List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")  # importante para export en background
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Table, TableStyle

from remind.core.models import MigraineEntry
from remind.resources import resource_path
from remind.i18n import t
from remind.brand import DISPLAY_NAME, VERSION


# ---------------------------
# Config “márgenes médicos”
# ---------------------------
PAGE_W, PAGE_H = A4
MARGIN_X = 18 * mm
MARGIN_TOP = 18 * mm
MARGIN_BOTTOM = 18 * mm

HEADER_H = 18 * mm
FOOTER_H = 12 * mm


def _parse_dt(ts: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(ts)
    except Exception:
        return None


def _filter_entries(entries: List[MigraineEntry], period_days: Optional[int]) -> List[MigraineEntry]:
    """
    Filtra por periodo: últimos N días (30/90), si period_days != None.
    Mantiene todos si period_days is None.
    """
    parsed = [(e, _parse_dt(e.timestamp)) for e in entries]
    parsed = [(e, dt) for e, dt in parsed if dt is not None]

    if not parsed:
        return []

    parsed.sort(key=lambda x: x[1])  # asc

    if period_days is None:
        return [e for e, _ in parsed]

    cutoff = datetime.now() - timedelta(days=int(period_days))
    return [e for e, dt in parsed if dt >= cutoff]


def _date_range(entries: List[MigraineEntry]) -> Optional[Tuple[datetime, datetime]]:
    dts = []
    for e in entries:
        dt = _parse_dt(e.timestamp)
        if dt:
            dts.append(dt)
    if not dts:
        return None
    return min(dts), max(dts)


def _build_plot_png(entries: List[MigraineEntry], theme: str) -> Optional[bytes]:
    """
    Crea una gráfica (matplotlib) como PNG en memoria para insertarla en el PDF.
    Incluye puntos + línea y (opcional) media móvil simple.
    """
    data = []
    for e in entries:
        if getattr(e, "had_migraine", False):
            dt = _parse_dt(e.timestamp)
            if dt:
                data.append((dt, int(getattr(e, "intensity", 0))))

    if not data:
        return None

    data.sort(key=lambda x: x[0])
    xs = [d for d, _ in data]
    ys = [v for _, v in data]

    # Tema (coherente con app)
    theme = (theme or "dark").lower()
    dark = theme == "dark"

    fig, ax = plt.subplots(figsize=(7.4, 3.4), dpi=160)

    if dark:
        fig.patch.set_facecolor("#121214")
        ax.set_facecolor("#121214")
        ax.tick_params(colors="white")
        for spine in ax.spines.values():
            spine.set_color("white")
        ax.yaxis.label.set_color("white")
        ax.xaxis.label.set_color("white")
        ax.title.set_color("white")
        grid_alpha = 0.25
    else:
        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")
        grid_alpha = 0.25

    ax.plot(xs, ys, marker="o", linewidth=1.8)

    # Media móvil 7 días (simple, por ventana temporal)
    # (solo si hay suficientes puntos)
    if len(xs) >= 3:
        ma_x = []
        ma_y = []
        for i, cur in enumerate(xs):
            win_start = cur - timedelta(days=7)
            vals = [v for d, v in zip(xs, ys) if win_start <= d <= cur]
            if vals:
                ma_x.append(cur)
                ma_y.append(sum(vals) / len(vals))
        if len(ma_y) > 2:
            ax.plot(ma_x, ma_y, linestyle="--", linewidth=2)

    ax.set_ylim(0, 10)
    ax.grid(True, alpha=grid_alpha)
    fig.autofmt_xdate()
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", transparent=False)
    plt.close(fig)
    return buf.getvalue()


def _draw_header_footer(
    c: Canvas,
    settings,
    title: str,
    period_label: str,
    start_dt: Optional[datetime],
    end_dt: Optional[datetime],
    page_num: int,
    total_pages: int,
    theme: str,
):
    theme = (theme or "dark").lower()
    dark = theme == "dark"

    # Colores
    if dark:
        bg = colors.HexColor("#121214")
        fg = colors.white
        sub = colors.Color(1, 1, 1, alpha=0.75)
        line = colors.Color(1, 1, 1, alpha=0.18)
    else:
        bg = colors.white
        fg = colors.HexColor("#111111")
        sub = colors.Color(0, 0, 0, alpha=0.65)
        line = colors.Color(0, 0, 0, alpha=0.12)

    # Fondo página (solo si dark)
    if dark:
        c.saveState()
        c.setFillColor(bg)
        c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        c.restoreState()

    # Header line
    c.setStrokeColor(line)
    c.setLineWidth(1)
    c.line(MARGIN_X, PAGE_H - MARGIN_TOP - HEADER_H, PAGE_W - MARGIN_X, PAGE_H - MARGIN_TOP - HEADER_H)

    # Logo + marca
    logo_path = None
    try:
        logo_path = resource_path("assets/logo.png")
    except Exception:
        logo_path = None

    y_top = PAGE_H - MARGIN_TOP

    if logo_path:
        try:
            # Tamaño visual ~14mm alto
            logo_h = 12 * mm
            logo_w = 32 * mm
            c.drawImage(logo_path, MARGIN_X, y_top - logo_h, width=logo_w, height=logo_h, mask="auto")
            brand_x = MARGIN_X + logo_w + 6 * mm
        except Exception:
            brand_x = MARGIN_X
    else:
        brand_x = MARGIN_X

    c.setFillColor(fg)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(brand_x, y_top - 10 * mm, DISPLAY_NAME)

    c.setFillColor(sub)
    c.setFont("Helvetica", 9)
    c.drawString(brand_x, y_top - 15 * mm, f"{VERSION} • {period_label}")

    # Título documento
    c.setFillColor(fg)
    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(PAGE_W - MARGIN_X, y_top - 10 * mm, title)

    # Rango fechas
    if start_dt and end_dt:
        c.setFillColor(sub)
        c.setFont("Helvetica", 9)
        c.drawRightString(
            PAGE_W - MARGIN_X,
            y_top - 15 * mm,
            f"{t(settings, 'date_range')}: {start_dt.date().isoformat()} → {end_dt.date().isoformat()}",
        )

    # Footer
    c.setStrokeColor(line)
    c.line(MARGIN_X, MARGIN_BOTTOM + FOOTER_H, PAGE_W - MARGIN_X, MARGIN_BOTTOM + FOOTER_H)

    c.setFillColor(sub)
    c.setFont("Helvetica", 9)
    c.drawString(MARGIN_X, MARGIN_BOTTOM + 4 * mm, t(settings, "generated_on").format(dt=datetime.now().strftime("%Y-%m-%d %H:%M")))
    c.drawRightString(PAGE_W - MARGIN_X, MARGIN_BOTTOM + 4 * mm, f"{page_num}/{total_pages}")


def export_pdf_report(
    entries: List[MigraineEntry],
    path: str,
    settings,
    period_days: Optional[int] = None,   # None = todo, 30, 90
) -> bool:
    """
    Export PDF multipágina A4, márgenes médicos, coherente con tema e i18n.
    Devuelve False si no hay datos.
    """
    filtered = _filter_entries(entries, period_days)

    if not filtered:
        return False

    # Para rango global (con todo, no solo migrañas)
    dr = _date_range(filtered)
    start_dt, end_dt = dr if dr else (None, None)

    # Label periodo (i18n)
    if period_days is None:
        period_label = t(settings, "period_all")
    else:
        period_label = t(settings, "period_last_days").format(days=int(period_days))

    theme = getattr(settings, "theme", "dark")

    # Precalcular plot (puede ser None si no hay episodios)
    plot_png = _build_plot_png(filtered, theme=theme)

    # Contenido para tabla: orden desc por fecha (más útil clínicamente)
    rows = []
    parsed = [(e, _parse_dt(e.timestamp)) for e in filtered]
    parsed = [(e, dt) for e, dt in parsed if dt is not None]
    parsed.sort(key=lambda x: x[1], reverse=True)

    for e, dt in parsed:
        had = "1" if getattr(e, "had_migraine", False) else "0"
        intensity = str(getattr(e, "intensity", 0) if getattr(e, "had_migraine", False) else 0)
        duration = str(getattr(e, "duration_min", "") or "")
        medication = str(getattr(e, "medication", "") or "")
        notes = str(getattr(e, "notes", "") or "")

        rows.append([
            dt.strftime("%Y-%m-%d"),
            dt.strftime("%H:%M"),
            had,
            intensity,
            duration,
            medication,
            notes[:120],  # cap para que no reviente layout
        ])

    # Estimación de páginas:
    # - Página 1: portada + plot + stats
    # - Páginas siguientes: tabla (n filas por página aprox)
    table_rows_per_page = 22
    table_pages = (len(rows) + (table_rows_per_page - 1)) // table_rows_per_page
    total_pages = 1 + max(1, table_pages)

    c = Canvas(path, pagesize=A4)

    # ----------------
    # Página 1: Resumen
    # ----------------
    _draw_header_footer(
        c=c,
        settings=settings,
        title=t(settings, "report_title"),
        period_label=period_label,
        start_dt=start_dt,
        end_dt=end_dt,
        page_num=1,
        total_pages=total_pages,
        theme=theme,
    )

    content_top = PAGE_H - MARGIN_TOP - HEADER_H - 8 * mm
    x0 = MARGIN_X
    x1 = PAGE_W - MARGIN_X

    # Stats básicas (solo episodios)
    migraine_intensities = []
    migraine_count = 0
    for e in filtered:
        if getattr(e, "had_migraine", False):
            migraine_count += 1
            migraine_intensities.append(int(getattr(e, "intensity", 0)))

    if migraine_intensities:
        avg_int = sum(migraine_intensities) / len(migraine_intensities)
        max_int = max(migraine_intensities)
    else:
        avg_int = 0.0
        max_int = 0

    theme_l = (theme or "dark").lower()
    dark = theme_l == "dark"
    fg = colors.white if dark else colors.HexColor("#111111")
    sub = colors.Color(1, 1, 1, alpha=0.78) if dark else colors.Color(0, 0, 0, alpha=0.65)

    c.setFillColor(fg)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x0, content_top, t(settings, "summary"))

    c.setFillColor(sub)
    c.setFont("Helvetica", 10)
    c.drawString(x0, content_top - 6 * mm, f"{t(settings, 'episodes_total')}: {len(filtered)}")
    c.drawString(x0, content_top - 12 * mm, f"{t(settings, 'migraine_episodes')}: {migraine_count}")
    c.drawString(x0, content_top - 18 * mm, f"{t(settings, 'avg_intensity')}: {avg_int:.2f}")
    c.drawString(x0, content_top - 24 * mm, f"{t(settings, 'max_intensity')}: {max_int}")

    # Plot
    plot_y = content_top - 36 * mm
    if plot_png:
        img = ImageReader(io.BytesIO(plot_png))
        # Caja plot
        plot_w = (x1 - x0)
        plot_h = 78 * mm
        c.drawImage(img, x0, plot_y - plot_h, width=plot_w, height=plot_h, mask="auto")
    else:
        c.setFillColor(sub)
        c.setFont("Helvetica", 10)
        c.drawString(x0, plot_y - 10 * mm, t(settings, "no_migraine_data_for_plot"))

    # Nota clínica
    note_y = MARGIN_BOTTOM + FOOTER_H + 10 * mm
    c.setFillColor(sub)
    c.setFont("Helvetica", 9)
    c.drawString(x0, note_y, t(settings, "clinical_note"))

    c.showPage()

    # ----------------
    # Páginas tabla
    # ----------------
    headers = [
        t(settings, "col_date"),
        t(settings, "col_time"),
        t(settings, "col_had"),
        t(settings, "col_intensity"),
        t(settings, "col_duration"),
        t(settings, "col_medication"),
        t(settings, "col_notes"),
    ]

    # Theme table colors
    if dark:
        table_bg = colors.HexColor("#1a1a1d")
        header_bg = colors.HexColor("#242428")
        grid = colors.Color(1, 1, 1, alpha=0.18)
        text = colors.white
        header_text = colors.white
    else:
        table_bg = colors.white
        header_bg = colors.HexColor("#f2f2f2")
        grid = colors.Color(0, 0, 0, alpha=0.12)
        text = colors.HexColor("#111111")
        header_text = colors.HexColor("#111111")

    page_num = 2
    for page_i in range(max(1, table_pages)):
        _draw_header_footer(
            c=c,
            settings=settings,
            title=t(settings, "report_title"),
            period_label=period_label,
            start_dt=start_dt,
            end_dt=end_dt,
            page_num=page_num,
            total_pages=total_pages,
            theme=theme,
        )

        chunk = rows[page_i * table_rows_per_page:(page_i + 1) * table_rows_per_page]

        data = [headers] + chunk

        # Tabla dentro de caja usable
        table_x = MARGIN_X
        table_y_top = PAGE_H - MARGIN_TOP - HEADER_H - 10 * mm
        table_w = PAGE_W - 2 * MARGIN_X
        table_h = PAGE_H - (MARGIN_TOP + HEADER_H + 20 * mm) - (MARGIN_BOTTOM + FOOTER_H + 10 * mm)

        # Anchos (ajusta si lo necesitas)
        col_widths = [
            22 * mm,  # date
            16 * mm,  # time
            10 * mm,  # had
            16 * mm,  # intensity
            22 * mm,  # duration
            30 * mm,  # medication
            table_w - (22+16+10+16+22+30) * mm,  # notes (resto)
        ]

        tbl = Table(data, colWidths=col_widths)

        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), header_bg),
            ("TEXTCOLOR", (0, 0), (-1, 0), header_text),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),

            ("BACKGROUND", (0, 1), (-1, -1), table_bg),
            ("TEXTCOLOR", (0, 1), (-1, -1), text),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 8),

            ("GRID", (0, 0), (-1, -1), 0.5, grid),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [table_bg, table_bg]),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))

        # Dibujar tabla: ReportLab usa bottom-left
        w, h = tbl.wrapOn(c, table_w, table_h)
        tbl.drawOn(c, table_x, table_y_top - h)

        c.showPage()
        page_num += 1

    c.save()
    return True