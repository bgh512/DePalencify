# -*- coding: utf-8 -*-
"""
Journal-aware figure sizing and automatic layout

Everything here is derived from two things: the physical figure size (journal column width x a fraction of the page
height) and one base font size. Margins are fitted to what is actually drawn, gaps and paddings are multiples of the
font size, and panel letters sit at the top-left of each panel's real extent, so changing the figure size or the font
size needs no other layout settings.
"""
# %% IMPORTS -----------------------------------------------------------------------------------------------------------------------------------------
import math

from matplotlib.font_manager import FontProperties
from matplotlib.textpath import TextPath

MM_PER_INCH = 25.4
# %% SIZES AND STYLE ---------------------------------------------------------------------------------------------------------------------------------


def figure_size_inches(spec, columns, height):
    """
    (width, height) in inches for a journal spec

    columns : a key of ``spec["widths_mm"]`` (1, 1.5 or 2 columns)
    height  : fraction of the journal's page height (``spec["page_height_mm"]``); 0.5 = half a page, 1 = a full page
    """
    widths = spec["widths_mm"]
    if columns not in widths:
        raise ValueError(f"columns must be one of {sorted(widths)}; got {columns!r}.")
    if not 0 < height <= 1:
        raise ValueError(f"height is a fraction of the page height (0 < height <= 1); got {height!r}.")
    return widths[columns] / MM_PER_INCH, spec["page_height_mm"] * height / MM_PER_INCH


def make_style(spec, base_font_pt=6.0, spacing=1.0, line_width_pt=0.75):
    """
    Every font size, padding and line width of the figures, derived from the journal spec and three master settings

    base_font_pt  : axis-label size; tick labels are 1 pt smaller and titles 1 pt larger (panel letters follow the journal)
    spacing       : 1.0 = the default tightness of all paddings and gaps; 1.2 = 20 % looser, 0.8 = 20 % tighter
    line_width_pt : width of the data lines; axes, reference and event lines are scaled from it
    """
    unit = base_font_pt * spacing
    return {
        "fonts": {"tick": base_font_pt - 1.0, "label": base_font_pt, "title": base_font_pt + 1.0,
                  "panel_letter": spec["panel_letter_pt"]},
        "unit": unit,                          # the padding unit in points
        "tick_length": 0.5 * unit,
        "tick_pad": 0.5 * unit,
        "label_pad": 0.5 * unit,
        "title_pad": 0.8 * unit,
        "edge_pad": 0.5 * unit,                # whitespace between the content and the edge of the figure
        "title_gap": 1.0 * unit,               # figure title to content
        "event_label_offset": 0.8 * unit,
        "line_width": line_width_pt,
        "axes_line_width": round(0.65 * line_width_pt, 3),
        "thin_line_width": round(0.5 * line_width_pt, 3),
    }


def check_style(journal, spec, fonts, size_inches, label=""):
    """Warnings (a list of strings) for fonts outside the journal's range or a figure taller than it allows."""
    warnings = []
    low, high = spec["font_min_pt"], spec["font_max_pt"]
    outside = {name: value for name, value in fonts.items() if name != "panel_letter" and not low <= value <= high}
    if outside:
        warnings.append(f"{label}text sizes {outside} are outside {journal}'s {low:g}-{high:g} pt range.")
    height_mm = size_inches[1] * MM_PER_INCH
    if height_mm > spec["max_height_mm"] + 0.5:
        warnings.append(f"{label}height {height_mm:.0f} mm is more than the {spec['max_height_mm']} mm {journal} allows when the "
                        f"legend sits under the figure (a full page is {spec['page_height_mm']} mm).")
    return warnings
# %% TEXT AND GAPS -----------------------------------------------------------------------------------------------------------------------------------


def text_extent_pt(text, size_pt, rotation_deg=0.0):
    """(width, height) in points of the bounding box of ``text`` after rotating it (plain text, no mathtext)."""
    extents = TextPath((0, 0), text, size=size_pt, prop=FontProperties()).get_extents()
    width, height = extents.width, max(extents.height, 1.2 * size_pt)
    angle = math.radians(rotation_deg)
    return (abs(width * math.cos(angle)) + abs(height * math.sin(angle)),
            abs(width * math.sin(angle)) + abs(height * math.cos(angle)))


def gap_to_space(gap_pt, extent_pt, n):
    """
    The GridSpec ``wspace``/``hspace`` that leaves a gap of ``gap_pt`` points between ``n`` equal cells spread over ``extent_pt``

    (wspace and hspace are fractions of the average cell size, so they depend on the figure size.)
    """
    if n <= 1:
        return 0.0
    room = extent_pt - gap_pt * (n - 1)
    if room <= 0:
        raise ValueError("The figure is too small for the requested gaps; use a larger figure or a smaller font/spacing.")
    return gap_pt * n / room
# %% AUTOMATIC MARGINS -------------------------------------------------------------------------------------------------------------------------------


def _renderer(fig):
    try:
        return fig.canvas.get_renderer()
    except AttributeError:
        return fig._get_renderer()


def fit_figure_to_canvas(fig, pad_pt, suptitle=None, suptitle_gap_pt=0.0, iterations=8, tolerance_pt=0.2):
    """
    Set the figure margins so everything drawn (axes, tick and axis labels, event labels, legends, panel letters) sits
    ``pad_pt`` inside the edge of the figure, whatever the figure size, font size or label lengths

    suptitle : an optional figure title (``fig.suptitle(...)``); it is placed ``pad_pt`` below the top edge and the content
               is kept ``suptitle_gap_pt`` below it.
    """
    width_pt, height_pt = (float(v) * 72.0 for v in fig.get_size_inches())
    renderer = _renderer(fig)
    scale = 72.0 / fig.dpi

    top_limit = height_pt - pad_pt
    if suptitle is not None:
        suptitle.set_in_layout(False)
        suptitle.set_va("top")
        suptitle.set_y(1.0 - pad_pt / height_pt)
        title_height = suptitle.get_window_extent(renderer).height * scale
        top_limit = height_pt - pad_pt - title_height - suptitle_gap_pt

    for _ in range(iterations):
        box = fig.get_tightbbox(renderer)
        params = fig.subplotpars
        left_deco = params.left * width_pt - box.x0 * 72.0
        right_deco = box.x1 * 72.0 - params.right * width_pt
        bottom_deco = params.bottom * height_pt - box.y0 * 72.0
        top_deco = box.y1 * 72.0 - params.top * height_pt

        left = (pad_pt + left_deco) / width_pt
        right = (width_pt - pad_pt - right_deco) / width_pt
        bottom = (pad_pt + bottom_deco) / height_pt
        top = (top_limit - top_deco) / height_pt
        if not (0 <= left < right <= 1 and 0 <= bottom < top <= 1):
            raise ValueError("The figure is too small for its contents (labels, ticks and gaps leave no room for the axes). "
                             "Use a larger figure, a smaller font size or less spacing.")

        change = max(abs(left - params.left) * width_pt, abs(right - params.right) * width_pt,
                     abs(bottom - params.bottom) * height_pt, abs(top - params.top) * height_pt)
        fig.subplots_adjust(left=left, right=right, bottom=bottom, top=top)
        if change < tolerance_pt:
            break

    if suptitle is not None:
        suptitle.set_in_layout(True)
# %% PANEL LETTERS -----------------------------------------------------------------------------------------------------------------------------------


def add_panel_letters(fig, panels, font_pt, case="upper", weight="bold", gap_pt=0.0):
    """
    Write each panel's letter at the top-left corner of everything that panel draws (labels, ticks, titles)

    panels : ``[(letter, main_axes, [axes that make up the panel]), ...]``. The letter is attached to ``main_axes`` so it
             moves with it, and letters whose panels share a left edge are lined up. A panel may carry a fourth item,
             ``(text, text keyword arguments)``: a small note written on the same line, just after the letter (used for
             faint run-name watermarks, so it takes no extra height). Call fit_figure_to_canvas again afterwards so the
             letters are inside the margins.
    """
    if case not in ("upper", "lower"):
        raise ValueError('The panel letter case must be "upper" or "lower".')
    renderer = _renderer(fig)
    scale = 72.0 / fig.dpi

    rows = []
    for letter, main, members, *extra in panels:
        boxes = [b for b in (ax.get_tightbbox(renderer) for ax in members) if b is not None]
        main_box = main.get_window_extent(renderer)
        left = min(b.x0 for b in boxes)
        top = max(b.y1 for b in boxes)
        rows.append((letter, main, (main_box.x0 - left) * scale, (top - main_box.y1) * scale, round(main_box.x0 / 2.0),
                     extra[0] if extra else None))

    column_offset = {}
    for _, _, dx, _, key, _ in rows:
        column_offset[key] = max(column_offset.get(key, 0.0), dx)

    artists = []
    for letter, main, _, dy, key, note in rows:
        text = letter.lower() if case == "lower" else letter.upper()
        artists.append(main.annotate(text, xy=(0, 1), xycoords="axes fraction",
                                     xytext=(-column_offset[key], dy + gap_pt), textcoords="offset points",
                                     ha="left", va="bottom", fontsize=font_pt, fontweight=weight, annotation_clip=False))
        if note:
            note_text, note_kwargs = note
            artists.append(main.annotate(note_text, xy=(0, 1), xycoords="axes fraction",
                                         xytext=(-column_offset[key] + 1.3 * font_pt, dy + gap_pt),
                                         textcoords="offset points", ha="left", va="bottom", annotation_clip=False,
                                         **note_kwargs))
    return artists
