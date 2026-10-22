# -*- coding: utf-8 -*-
"""Two experiments side by side in one figure, each with its own y axes, panel letters (a, b) and white space between them."""
from pathlib import Path

import matplotlib.pyplot as plt

from utils_shared.figure_layout import add_panel_letters, fit_figure_to_canvas, gap_to_space
from utils_shared.helpers import safe_file_name, save_figure_exact
from utils_shared.individual_experiment_plotter import draw_experiment, watermark_style

GAP_EXTRA_PT_PER_PAD = 8          # white space between the two plots, beyond what their labels need (in multiples of the layout pad)


def _renderer(fig):
    try:
        return fig.canvas.get_renderer()
    except AttributeError:
        return fig._get_renderer()


def _overhang_pt(fig, members, main):
    """(points the labels of ``members`` stick out to the left of ``main``, to the right of it)"""
    renderer = _renderer(fig)
    scale = 72.0 / fig.dpi
    boxes = [b for b in (ax.get_tightbbox(renderer) for ax in members) if b is not None]
    box = main.get_window_extent(renderer)
    return (box.x0 - min(b.x0 for b in boxes)) * scale, (max(b.x1 for b in boxes) - box.x1) * scale


def plot_comparison(first, second, config, export_root, figure_size, spec, share_time_axis=False):
    """
    Draw ``first`` (left, panel a) and ``second`` (right, panel b) with the individual-experiment settings in ``config``

    figure_size     : (width, height) in inches of the whole figure
    spec            : the journal spec (panel letter size and case)
    share_time_axis : both plots use the same time range (each keeps its own y axes)
    Saved as svg + png in ``<export_root>/comparison/``. Returns the file stem.
    """
    width_pt = figure_size[0] * 72.0
    pad = config["LAYOUT_PAD_PT"]
    fig = plt.figure(figsize=figure_size, dpi=config["FIGURE_DPI"])
    try:
        grid = fig.add_gridspec(1, 2, wspace=0.2)
        axes_a, panels_a = draw_experiment(fig, grid[0, 0], first, config)
        count_before = len(fig.axes)
        axes_b, panels_b = draw_experiment(fig, grid[0, 1], second, config)
        members_a = [ax for ax in fig.axes[:count_before]]
        members_b = [ax for ax in fig.axes[count_before:]]

        if share_time_axis:
            left = min(axes_a[-1].get_xlim()[0], axes_b[-1].get_xlim()[0])
            right = max(axes_a[-1].get_xlim()[1], axes_b[-1].get_xlim()[1])
            for ax in list(axes_a) + list(axes_b):
                ax.set_xlim(left, right)

        # Margins, then a gap wide enough for the right plot's y labels and the left plot's event labels plus clear white space.
        for _ in range(3):
            fit_figure_to_canvas(fig, pad, None, config["TITLE_GAP_PT"])
            _, a_right = _overhang_pt(fig, members_a, axes_a[0])
            b_left, _ = _overhang_pt(fig, members_b, axes_b[0])
            params = fig.subplotpars
            extent_pt = (params.right - params.left) * width_pt
            gap_pt = a_right + b_left + GAP_EXTRA_PT_PER_PAD * pad
            grid.update(wspace=gap_to_space(gap_pt, extent_pt, 2))
        fit_figure_to_canvas(fig, pad, None, config["TITLE_GAP_PT"])

        letter_case = spec.get("panel_letter_case", "upper")
        note = (None, watermark_style(config))
        add_panel_letters(fig, [("a", axes_a[0], members_a, (first["experiment_name"], note[1])),
                                ("b", axes_b[0], members_b, (second["experiment_name"], note[1]))],
                          spec["panel_letter_pt"], case=letter_case)
        fit_figure_to_canvas(fig, pad, None, config["TITLE_GAP_PT"])

        stem = safe_file_name(f"{first['experiment_name']}_vs_{second['experiment_name']}")
        save_figure_exact(fig, Path(export_root) / "comparison", stem, ("svg", "png"), figure_size, config["FIGURE_DPI"],
                          tight=config["TIGHT_BBOX"])
        return stem
    finally:
        plt.close(fig)
