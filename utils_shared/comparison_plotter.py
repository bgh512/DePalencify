"""
Two experiments side by side in one figure.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from pathlib import Path
from typing import Any, List, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.figure_layout import (figure_canvas_fitter,
                                        gap_space_calculator,
                                        panel_letter_adder,
                                        )
from utils_shared.helpers import figure_saver, file_name_sanitiser
from utils_shared.individual_experiment_plotter import (experiment_drawer,
                                                        watermark_style_builder,
                                                        )


# ---- CONSTANTS -----------------------------------------------------------------------
# white space between the two plots, beyond what their labels need (in multiples of the
# layout pad)
GAP_EXTRA_PT_PER_PAD = 8


# ---- COMPARISON PLOTTER HELPERS ------------------------------------------------------


# ---- _overhang_calculator ------------------------------------------------------------
def _overhang_calculator(fig: Figure,
                         members: List[Axes],
                         main: Axes,
                         ) -> Tuple[float, float]:
    """
    ---- Summary ----
    Helper function to measure how far the labels of a plot stick out to the left and
    right of its main axes.

    ---- Inputs ----
    fig : Figure
        Matplotlib figure.
    members : List[Axes]
        All axes of the plot.
    main : Axes
        Main axes the overhang is measured from.

    ---- Globals read ----
    Needs a figure that has been drawn or can be rendered.

    ---- Outputs ----
    Tuple[float, float]
        (points to the left, points to the right).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _renderer_getter
    """

    renderer = _renderer_getter(fig)
    scale = 72.0 / fig.dpi
    boxes = [b for b in (ax.get_tightbbox(renderer) for ax in members) if b is not None]
    box = main.get_window_extent(renderer)
    return (box.x0 - min(b.x0 for b in boxes)
            ) * scale, (max(b.x1 for b in boxes) - box.x1) * scale


# ---- _renderer_getter ----------------------------------------------------------------
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


# ---- comparison_figure_plotter -------------------------------------------------------
def comparison_figure_plotter(first: dict,
                              second: dict,
                              config: dict,
                              export_root: Path,
                              figure_size: Tuple[float, float],
                              spec: dict,
                              share_time_axis: bool = True,
                              ) -> str:
    """
    ---- Summary ----
    Main function to draw two experiments side by side with their own y axes, panel
    letters a and b and a gap sized to their labels, and save it as svg and png.

    ---- Inputs ----
    first : dict
        Experiment drawn on the left (panel a).
    second : dict
        Experiment drawn on the right (panel b).
    config : dict
        Individual-experiment plot settings (config.py); uses LAYOUT_PAD_PT, FIGURE_DPI,
        TITLE_GAP_PT and TIGHT_BBOX.
    export_root : Path
        Results folder.
    figure_size : Tuple[float, float]
        (width, height) of the whole figure in inches.
    spec : dict
        Journal specification (config.JOURNAL_SPECS entry).
    share_time_axis : bool
        True gives both plots the same time range.

    ---- Globals read ----
    GAP_EXTRA_PT_PER_PAD (module constant).

    ---- Outputs ----
    str
        File stem of the saved figure.

    ---- Globals mutated ----
    None. Writes <export_root>/<stem>.svg and .png (side effect); the figure
    is closed before returning.

    ---- Equations ----
    None.

    ---- Helpers ----
    _overhang_calculator
    experiment_drawer
    figure_canvas_fitter
    figure_saver
    file_name_sanitiser
    gap_space_calculator
    panel_letter_adder
    watermark_style_builder
    """

    # ---- 1 Set up the figure ---------------------------------------------------------
    width_pt = figure_size[0] * 72.0
    pad = config['LAYOUT_PAD_PT']
    fig = plt.figure(figsize=figure_size, dpi=config['FIGURE_DPI'])

    # ---- 2 Draw the panels -----------------------------------------------------------
    try:
        grid = fig.add_gridspec(1, 2, wspace=0.2)
        axes_a, panels_a = experiment_drawer(fig, grid[0, 0], first, config)
        count_before = len(fig.axes)
        axes_b, panels_b = experiment_drawer(fig, grid[0, 1], second, config)
        members_a = [ax for ax in fig.axes[:count_before]]
        members_b = [ax for ax in fig.axes[count_before:]]
        if share_time_axis:
            left = min(axes_a[-1].get_xlim()[0], axes_b[-1].get_xlim()[0])
            right = max(axes_a[-1].get_xlim()[1], axes_b[-1].get_xlim()[1])
            for ax in list(axes_a) + list(axes_b):
                ax.set_xlim(left, right)
        # Margins, then a gap wide enough for the right plot's y labels and the left
        # plot's event labels plus clear white space.
        for _ in range(3):
            figure_canvas_fitter(fig, pad, None, config['TITLE_GAP_PT'])
            _, a_right = _overhang_calculator(fig, members_a, axes_a[0])
            b_left, _ = _overhang_calculator(fig, members_b, axes_b[0])
            params = fig.subplotpars
            extent_pt = (params.right - params.left) * width_pt
            gap_pt = a_right + b_left + GAP_EXTRA_PT_PER_PAD * pad
            grid.update(wspace=gap_space_calculator(gap_pt, extent_pt, 2))
        figure_canvas_fitter(fig, pad, None, config['TITLE_GAP_PT'])
        letter_case = spec.get('panel_letter_case', 'upper')
        note = (None, watermark_style_builder(config))
        panel_letter_adder(fig,
                           [('a',
                             axes_a[0],
                             members_a,
                             (first['experiment_name'], note[1]),
                             ),
                            ('b',
                             axes_b[0],
                             members_b,
                             (second['experiment_name'], note[1]),
                             ),
                            ],
                           spec['panel_letter_pt'],
                           case=letter_case,
                           )
        figure_canvas_fitter(fig, pad, None, config['TITLE_GAP_PT'])
        stem = file_name_sanitiser(f"{first['experiment_name']}_vs_"
                                   f"{second['experiment_name']}",
                                   )
        figure_saver(fig,
                     Path(export_root),
                     stem,
                     ('svg', 'png'),
                     figure_size,
                     config['FIGURE_DPI'],
                     tight=config['TIGHT_BBOX'],
                     )
        return stem
    finally:
        plt.close(fig)
