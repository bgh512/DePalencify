# -*- coding: utf-8 -*-
"""
Journal-aware figure sizing and automatic layout

Everything here is derived from two things: the physical figure size (journal column
width x a fraction of the page
height) and one base font size. Margins are fitted to what is actually drawn, gaps and
paddings are multiples of the
font size, and panel letters sit at the top-left of each panel's real extent, so
changing the figure size or the font
size needs no other layout settings.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import math
from typing import Any, List, Optional, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.font_manager import FontProperties
from matplotlib.textpath import TextPath


# ---- CONSTANTS -----------------------------------------------------------------------
MM_PER_INCH = 25.4


# ---- FIGURE LAYOUT HELPERS -----------------------------------------------------------


# ---- _RENDERER GETTER ----------------------------------------------------------------
def _renderer_getter(fig: Figure) -> Any:
    """
    ---- Summary ----
    Helper function to get the renderer of a figure canvas.

    ---- Inputs ----
    fig : Figure
        Matplotlib figure.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Any
        Matplotlib renderer.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    try:
        return fig.canvas.get_renderer()
    except AttributeError:
        return fig._get_renderer()


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- FIGURE CANVAS FITTER ------------------------------------------------------------
def figure_canvas_fitter(fig: Figure,
                         pad_pt: float,
                         suptitle: Optional[Any] = None,
                         suptitle_gap_pt: float = 0.0,
                         iterations: int = 8,
                         tolerance_pt: float = 0.2,
                         ) -> None:
    """
    ---- Summary ----
    Main function to set the figure margins so that everything drawn sits a fixed
    padding inside the figure edge, whatever the figure size, font size or label
    lengths.

    ---- Inputs ----
    fig : Figure
        Matplotlib figure.
    pad_pt : float
        Whitespace between the content and the figure edge in points.
    suptitle : Optional[Any]
        Optional figure title (Text from fig.suptitle); it is placed pad_pt below the
        top edge.
    suptitle_gap_pt : float
        Gap between the title and the content in points.
    iterations : int
        Maximum number of fitting passes.
    tolerance_pt : float
        Stop when no margin moves by more than this many points.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing; the figure margins are changed in place. Raises ValueError when the
        contents leave no room for the axes.

    ---- Globals mutated ----
    None. Changes the subplot margins of ``fig`` and the layout flag and position of
    ``suptitle`` (side effect).

    ---- Equations ----
    Each margin = (pad + width of the decoration outside the axes) / figure size,
    repeated until the largest change is below tolerance_pt.

    ---- Helpers ----
    _renderer_getter
    """

    # ---- 1 Measure the figure --------------------------------------------------------
    width_pt, height_pt = (float(v) * 72.0 for v in fig.get_size_inches())
    renderer = _renderer_getter(fig)
    scale = 72.0 / fig.dpi
    top_limit = height_pt - pad_pt
    if suptitle is not None:
        suptitle.set_in_layout(False)
        suptitle.set_va('top')
        suptitle.set_y(1.0 - pad_pt / height_pt)
        title_height = suptitle.get_window_extent(renderer).height * scale
        top_limit = height_pt - pad_pt - title_height - suptitle_gap_pt

    # ---- 2 Fit the margins -----------------------------------------------------------
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
            raise ValueError('The figure is too small for its contents (labels, ticks '
                             'and gaps leave no room for the axes). '
                             'Use a larger figure, a smaller font size or less '
                             'spacing.',
                             )
        change = max(abs(left - params.left) * width_pt,
                     abs(right - params.right) * width_pt,
                     abs(bottom - params.bottom) * height_pt,
                     abs(top - params.top) * height_pt,
                     )
        fig.subplots_adjust(left=left, right=right, bottom=bottom, top=top)
        if change < tolerance_pt:
            break

    # ---- 3 Keep the title in the layout ----------------------------------------------
    if suptitle is not None:
        suptitle.set_in_layout(True)


# ---- FIGURE SIZE CALCULATOR ----------------------------------------------------------
def figure_size_calculator(spec: dict,
                           columns: float,
                           height: float,
                           ) -> Tuple[float, float]:
    """
    ---- Summary ----
    Main function to calculate the (width, height) of a figure in inches from a journal
    specification.

    ---- Inputs ----
    spec : dict
        Journal specification (config.JOURNAL_SPECS entry).
    columns : float
        Key of spec["widths_mm"]: 1, 1.5 or 2 columns wide.
    height : float
        Fraction of the journal page height (spec["page_height_mm"]), above 0 and at
        most 1; 0.5 is half a page.

    ---- Globals read ----
    MM_PER_INCH (module constant).

    ---- Outputs ----
    Tuple[float, float]
        (width, height) in inches. Raises ValueError for an unknown column count or a
        height outside (0, 1].

    ---- Globals mutated ----
    None.

    ---- Equations ----
    width_in = widths_mm[columns] / 25.4; height_in = page_height_mm x height / 25.4.

    ---- Helpers ----
    None.
    """

    widths = spec['widths_mm']
    if columns not in widths:
        raise ValueError(f'columns must be one of {sorted(widths)}; got {columns!r}.')
    if not 0 < height <= 1:
        raise ValueError(f'height is a fraction of the page height (0 < height <= 1); '
                         f'got {height!r}.',
                         )
    return widths[columns] / MM_PER_INCH, spec['page_height_mm'] * height / MM_PER_INCH


# ---- FIGURE STYLE BUILDER ------------------------------------------------------------
def figure_style_builder(spec: dict,
                         base_font_pt: float = 6.0,
                         spacing: float = 1.0,
                         line_width_pt: float = 0.75,
                         ) -> dict:
    """
    ---- Summary ----
    Main function to derive every font size, padding and line width of the figures from
    the journal specification and three master settings.

    ---- Inputs ----
    spec : dict
        Journal specification (config.JOURNAL_SPECS entry).
    base_font_pt : float
        Axis-label size in points; tick labels are 1 pt smaller and titles 1 pt larger.
    spacing : float
        Tightness of all paddings and gaps: 1.0 is the default, 1.2 is 20 % looser, 0.8
        is 20 % tighter.
    line_width_pt : float
        Width of the data lines in points; axes, reference and event lines are scaled
        from it.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        Style dictionary with 'fonts' {tick, label, title, panel_letter} and the points
        values unit, tick_length, tick_pad, label_pad, title_pad, edge_pad, title_gap,
        event_label_offset, line_width, axes_line_width and thin_line_width.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    unit = base_font_pt x spacing; every padding is a multiple of unit (for example
    title_pad = 0.8 x unit); axes_line_width = 0.65 x line_width_pt; thin_line_width =
    0.5 x line_width_pt.

    ---- Helpers ----
    None.
    """

    # ---- 1 Calculate the base unit ---------------------------------------------------
    unit = base_font_pt * spacing

    # ---- 2 Build the style -----------------------------------------------------------
    return {
        'fonts': {'tick': base_font_pt - 1.0,
                  'label': base_font_pt,
                  'title': base_font_pt + 1.0,
                  'panel_letter': spec['panel_letter_pt'],
                  },
        'unit': unit,                          # the padding unit in points
        'tick_length': 0.5 * unit,
        'tick_pad': 0.5 * unit,
        'label_pad': 0.5 * unit,
        'title_pad': 0.8 * unit,
        # whitespace between the content and the edge of the figure
        'edge_pad': 0.5 * unit,
        'title_gap': 1.0 * unit,               # figure title to content
        'event_label_offset': 0.8 * unit,
        'line_width': line_width_pt,
        'axes_line_width': round(0.65 * line_width_pt, 3),
        'thin_line_width': round(0.5 * line_width_pt, 3),
    }


# ---- FIGURE STYLE CHECKER ------------------------------------------------------------
def figure_style_checker(journal: str,
                         spec: dict,
                         fonts: dict,
                         size_inches: Tuple[float, float],
                         label: str = '',
                         ) -> List[str]:
    """
    ---- Summary ----
    Main function to list warnings for fonts outside the journal range or a figure
    taller than the journal allows.

    ---- Inputs ----
    journal : str
        Journal name, used in the warning text.
    spec : dict
        Journal specification (config.JOURNAL_SPECS entry).
    fonts : dict
        Font sizes in points keyed by role, as in make_style()['fonts'].
    size_inches : Tuple[float, float]
        (width, height) of the figure in inches.
    label : str
        Text put in front of each warning.

    ---- Globals read ----
    MM_PER_INCH (module constant).

    ---- Outputs ----
    List[str]
        Warning messages; empty when the style fits the journal.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 Check the font sizes ------------------------------------------------------
    warnings = []
    low, high = spec['font_min_pt'], spec['font_max_pt']
    outside = {name: value
               for name, value in fonts.items()
               if name != 'panel_letter' and not low <= value <= high
               }
    if outside:
        warnings.append(f"{label}text sizes {outside} are outside {journal}'s {low:g}-"
                        f'{high:g} pt range.',
                        )

    # ---- 2 Check the figure height ---------------------------------------------------
    height_mm = size_inches[1] * MM_PER_INCH
    if height_mm > spec['max_height_mm'] + 0.5:
        warnings.append(f'{label}height {height_mm:.0f} mm is more than the '
                        f"{spec['max_height_mm']} mm {journal} allows when the "
                        f'legend sits under the figure (a full page is '
                        f"{spec['page_height_mm']} mm).",
                        )
    return warnings


# ---- GAP SPACE CALCULATOR ------------------------------------------------------------
def gap_space_calculator(gap_pt: float, extent_pt: float, n: int) -> float:
    """
    ---- Summary ----
    Main function to calculate the GridSpec wspace or hspace that leaves a given gap
    between equal cells.

    ---- Inputs ----
    gap_pt : float
        Wanted gap between neighbouring cells in points.
    extent_pt : float
        Total width or height covered by the cells and gaps in points.
    n : int
        Number of equal cells.

    ---- Globals read ----
    None.

    ---- Outputs ----
    float
        GridSpec spacing as a fraction of the average cell size; 0 for a single cell.
        Raises ValueError when the gaps do not fit in extent_pt.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    room = extent_pt - gap_pt x (n - 1); space = gap_pt x n / room.

    ---- Helpers ----
    None.
    """

    if n <= 1:
        return 0.0
    room = extent_pt - gap_pt * (n - 1)
    if room <= 0:
        raise ValueError('The figure is too small for the requested gaps; use a larger'
                         ' figure or a smaller font/spacing.',
                         )
    return gap_pt * n / room


# ---- PANEL LETTER ADDER --------------------------------------------------------------
def panel_letter_adder(fig: Figure,
                       panels: list,
                       font_pt: float,
                       case: str = 'upper',
                       weight: str = 'bold',
                       gap_pt: float = 0.0,
                       ) -> list:
    """
    ---- Summary ----
    Main function to write each panel letter just above the top edge of its panel's
    main axes, to the left of everything the panel draws on that side.

    ---- Inputs ----
    fig : Figure
        Matplotlib figure.
    panels : list
        [(letter, main axes, [axes of the panel]), ...]; a fourth item (text, text
        keyword arguments) adds a small note after the letter.
    font_pt : float
        Letter size in points.
    case : str
        'upper' or 'lower'.
    weight : str
        Matplotlib font weight of the letters.
    gap_pt : float
        Extra gap above the panel in points.

    ---- Globals read ----
    None.

    ---- Outputs ----
    list
        The annotation artists created. Raises ValueError for an unknown case.

    ---- Globals mutated ----
    None. Adds annotations to the main axes of each panel (side effect); call
    figure_canvas_fitter afterwards so the letters are inside the margins.

    ---- Equations ----
    None.

    ---- Helpers ----
    _renderer_getter
    """

    # ---- 1 Validate the inputs -------------------------------------------------------
    if case not in ('upper', 'lower'):
        raise ValueError('The panel letter case must be "upper" or "lower".')

    # ---- 2 Measure the panels --------------------------------------------------------
    renderer = _renderer_getter(fig)
    scale = 72.0 / fig.dpi
    rows = []
    for letter, main, members, *extra in panels:
        boxes = [b
                 for b in (ax.get_tightbbox(renderer) for ax in members)
                 if b is not None
                 ]
        main_box = main.get_window_extent(renderer)
        left = min(b.x0 for b in boxes)
        # Never closer to the axes than one letter width, so a panel with nothing to
        # its left still keeps its letter clear of the axes and the labels above them.
        reach = max((main_box.x0 - left) * scale, 1.3 * font_pt)
        rows.append((letter,
                     main,
                     reach,
                     0.0,
                     round(main_box.x0 / 2.0),
                     extra[0] if extra else None,
                     ),
                    )

    # ---- 3 Align the letters ---------------------------------------------------------
    column_offset = {}
    for _, _, dx, _, key, _ in rows:
        column_offset[key] = max(column_offset.get(key, 0.0), dx)

    # ---- 4 Draw the letters ----------------------------------------------------------
    artists = []
    for letter, main, _, dy, key, note in rows:
        text = letter.lower() if case == 'lower' else letter.upper()
        artists.append(main.annotate(text,
                                     xy=(0, 1),
                                     xycoords='axes fraction',
                                     xytext=(-column_offset[key], dy + gap_pt),
                                     textcoords='offset points',
                                     ha='left',
                                     va='bottom',
                                     fontsize=font_pt,
                                     fontweight=weight,
                                     annotation_clip=False,
                                     ),
                       )
        if note:
            note_text, note_kwargs = note
            artists.append(main.annotate(note_text,
                                         xy=(0, 1),
                                         xycoords='axes fraction',
                                         xytext=(-column_offset[key] + 1.3 * font_pt,
                                                 dy + gap_pt,
                                                 ),
                                         textcoords='offset points',
                                         ha='left',
                                         va='bottom',
                                         annotation_clip=False,
                                         **note_kwargs,
                                         ),
                           )
    return artists


# ---- TEXT EXTENT CALCULATOR ----------------------------------------------------------
def text_extent_calculator(text: str,
                           size_pt: float,
                           rotation_deg: float = 0.0,
                           ) -> Tuple[float, float]:
    """
    ---- Summary ----
    Main function to calculate the width and height of the bounding box of a piece of
    text after rotating it.

    ---- Inputs ----
    text : str
        Plain text without mathtext.
    size_pt : float
        Font size in points.
    rotation_deg : float
        Rotation of the text in degrees.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Tuple[float, float]
        (width, height) in points of the rotated bounding box; the unrotated height is
        at least 1.2 x size_pt.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    w = |W cos(a)| + |H sin(a)|; h = |W sin(a)| + |H cos(a)|, where W and H are the
    unrotated text width and height and a is the rotation angle.

    ---- Helpers ----
    None.
    """

    extents = TextPath((0, 0), text, size=size_pt, prop=FontProperties()).get_extents()
    width, height = extents.width, max(extents.height, 1.2 * size_pt)
    angle = math.radians(rotation_deg)
    return (abs(width * math.cos(angle)) + abs(height * math.sin(angle)),
            abs(width * math.sin(angle)) + abs(height * math.cos(angle)),
            )
