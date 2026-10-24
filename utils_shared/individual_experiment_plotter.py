# -*- coding: utf-8 -*-
"""Plot one experiment: oxygen, VO2 and configured haem panels, with averaging windows and events."""
# %% IMPORTS -----------------------------------------------------------------------------------------------------------------------------------------
import re
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator, ScalarFormatter

from utils_shared.helpers import simplify_name, save_figure_exact
from utils_shared.figure_layout import fit_figure_to_canvas
from utils_shared.schema import (HAEM_KEYS, VO2_KEYS, get_times, get_values,
                                 measurement_columns, resolve_source)
# %% HELPERS -----------------------------------------------------------------------------------------------------------------------------------------


def _first_series(df):
    """Return (time, values) for the first measurement column of a DataFrame."""
    column = measurement_columns(df)[0]
    return get_times(df), get_values(df, column)


def _legend(ax, config, text_only=False, location=None):
    """
    Legend with an optional thin box. ``text_only`` drops the coloured line beside each entry (used for the haem panels,
    where the colour already identifies the trace and the word names it).
    """
    options = {"loc": location or config["LEGEND_LOCATION"], "ncol": config["LEGEND_COLUMNS"],
               "frameon": config["LEGEND_FRAME"], "fontsize": config["LEGEND_FONT_SIZE"]}
    if text_only:
        options.update(handlelength=0, handletextpad=0)
    legend = ax.legend(**options)
    if config["LEGEND_FRAME"]:
        legend.get_frame().set_linewidth(config.get("LEGEND_FRAME_LINE_WIDTH", 0.4))
    return legend


def watermark_style(config):
    """Text keyword arguments for the faint run-name watermark (TITLE_STYLE = "watermark")."""
    return {"fontsize": config.get("WATERMARK_FONT_SIZE", config["TICK_FONT_SIZE"]),
            "color": config.get("WATERMARK_COLOUR", "0.35"), "alpha": config.get("WATERMARK_ALPHA", 0.5)}


def _set_min_ticks(axis, count):
    """Make sure an axis has at least ``count`` ticks (None = automatic). Positions stay 'nice' round values, so it can be one more."""
    if count is not None:
        axis.set_major_locator(MaxNLocator(nbins=count - 1, min_n_ticks=count))


class _HideTopTickLabels(ScalarFormatter):
    """
    A y-axis formatter that leaves out the tick label nearest the top edge when it would run into the panel above

    Stacked panels touch, so a label at the very top of one panel overlaps the bottom label of the panel above it. A label is
    dropped if its tick lies within 0.7 x ``font_pt`` points (the height of a digit) of the top of the axis, whatever the panel's height.
    """

    def __init__(self, font_pt):
        super().__init__()
        self._font_pt = font_pt

    def __call__(self, x, pos=None):
        axes = self.axis.axes
        height_pt = axes.get_window_extent().height * 72.0 / axes.figure.dpi
        low, high = self.axis.get_view_interval()
        if height_pt > 0 and x >= high - (high - low) * min(0.5, 0.7 * self._font_pt / height_pt):
            return ""
        return super().__call__(x, pos)


def _ylim_ignoring_start(times, series, ignore_minutes, margin=0.05, ignore_last_minutes=0.0):
    """(low, high) of the data after the first ``ignore_minutes`` and before the last ``ignore_last_minutes``, plus a margin; None if no finite data remain."""
    keep = (np.isfinite(times) & (times >= np.nanmin(times) + ignore_minutes)
            & (times <= np.nanmax(times) - ignore_last_minutes))
    values = np.concatenate([np.asarray(s, dtype=float)[keep] for s in series])
    values = values[np.isfinite(values)]
    if values.size == 0:
        return None
    low, high = values.min(), values.max()
    pad = (high - low) * margin or 1.0
    return low - pad, high + pad


def _height_ratios(panels, config):
    """
    Relative panel heights from PANEL_HEIGHT_RATIOS ({"oxygen": a, "vo2": b, "haem": c})

    The "haem" value is the total for all haem panels, shared equally between them, so
    {"oxygen": 2, "vo2": 2, "haem": 5} gives the oxygen and VO2 panels 2/9 each and the haems 5/9 together.
    """
    weights = config["PANEL_HEIGHT_RATIOS"]
    n_haem = sum(panel["type"] == "haem" for panel in panels)
    ratios = []
    for panel in panels:
        weight = weights.get(panel["type"])
        if weight is None or weight <= 0:
            raise ValueError(f"PANEL_HEIGHT_RATIOS needs a positive value for {panel['type']!r}; got {weight!r}.")
        ratios.append(weight / n_haem if panel["type"] == "haem" else weight)
    return ratios


def _window_label(window_name, config):
    """Text for an averaging window from AVERAGING_WINDOW_LABEL_FORMAT ({n} = number, {name} = e.g. "average3"; "" = no label)."""
    match = re.search(r"(\d+)$", window_name)
    number = int(match.group(1)) if match else window_name
    return config["AVERAGING_WINDOW_LABEL_FORMAT"].format(n=number, name=window_name)


def _select_haem_data(experiment, config):
    """Return (haem DataFrame or None, source name)."""
    source = config["HAEM_PLOT_VALUES"]
    if not config["HAEM_PANELS"] or source is None:
        return None, source
    try:
        _, haem_data = resolve_source(experiment, source, HAEM_KEYS, "haem")
    except ValueError as exc:
        if source not in HAEM_KEYS:
            raise
        print(f"  Warning: {exc} Haem panels will be skipped.")
        return None, source
    return haem_data, source


def _build_panels(experiment, config, haem_data):
    """List the panels to draw: oxygen, VO2, then one per configured haem panel with matching data."""
    panels = []
    if config["PLOT_SET_AND_MEASURED_O2"]:
        panels.append({"type": "oxygen", "title": config["O2_PANEL_TITLE"]})
    if config["PLOT_VO2"]:
        panels.append({"type": "vo2", "title": config["VO2_PANEL_TITLE"]})

    if haem_data is not None:
        lookup = {simplify_name(column): column for column in measurement_columns(haem_data)}
        for spec in config["HAEM_PANELS"]:
            matched = [lookup[simplify_name(h)] for h in spec["haems"] if simplify_name(h) in lookup]
            missing = [h for h in spec["haems"] if simplify_name(h) not in lookup]
            if missing:
                print(f"  Warning: haem panel {spec['label']!r} could not find: {missing}")
            if matched:
                panels.append({"type": "haem", "title": spec["label"], "haems": matched})

    if not panels:
        raise ValueError("No panels selected. Enable an oxygen/VO2 panel or configure matching haem panels.")
    return panels


def _draw_windows(axes, experiment, config):
    """Draw the averaging windows behind the data on every axis."""
    averages = experiment.get("averages")
    if not (config["PLOT_AVERAGING_WINDOWS"] and averages):
        return

    for window_name, window in averages["windows"].items():
        start, end = window["start_time"], window["end_time"]
        if end <= start:
            continue
        for ax in axes:
            ax.axvspan(start, end, facecolor=config["AVERAGING_WINDOW_COLOUR"], alpha=config["AVERAGING_WINDOW_ALPHA"],
                       edgecolor=config["AVERAGING_WINDOW_EDGE_COLOUR"],
                       linewidth=config.get("AVERAGING_WINDOW_EDGE_LINE_WIDTH", 0.8), zorder=0)
        text = _window_label(window_name, config)
        if text:
            axes[0].text((start + end) / 2, 0.98, text, transform=axes[0].get_xaxis_transform(), ha="center", va="top",
                         fontsize=config["AVERAGING_WINDOW_LABEL_FONT_SIZE"], color=config["AVERAGING_WINDOW_EDGE_COLOUR"], zorder=2)
# %% DRAW AND PLOT --------------------------------------------------------------------------------------------------------------------------------


def experiment_title(experiment, config):
    """The figure/panel title for an experiment, from ``config["FIGURE_TITLE"]``."""
    return config["FIGURE_TITLE"].format(experiment_name=experiment["experiment_name"])


def draw_experiment(fig, subplot_spec, experiment, config):
    """
    Draw one experiment's stacked panels into a cell of an existing figure

    This is the drawing code behind ``plot_experiment`` and is reused by the publication figure so
    the two always look identical. It does not add a title, adjust margins, save or show anything.
    Event labels hang below the lowest axis, so leave room underneath the cell.

    Returns ``(axes, panels)``: the list of axes (top to bottom) and the list of panel specs drawn.
    """
    haem_data, haem_source = _select_haem_data(experiment, config)
    panels = _build_panels(experiment, config, haem_data)

    vo2_df = vo2_label = None
    if config["PLOT_VO2"]:
        _, vo2_df = resolve_source(experiment, config["VO2_PLOT_VALUES"], VO2_KEYS, "VO2")
        vo2_label = config["VO2_AXIS_LABELS"][config["VO2_PLOT_VALUES"]]
    haem_label = config["HAEM_AXIS_LABELS"][haem_source] if haem_data is not None else None
    haem_colours = {simplify_name(k): v for k, v in config["HAEM_COLOURS"].items()}

    anchor = config["EVENT_LABEL_ANCHOR"]
    if anchor not in ("start", "center", "end"):
        raise ValueError(f'EVENT_LABEL_ANCHOR must be "start", "center" or "end"; got {anchor!r}.')

    grid = subplot_spec.subgridspec(len(panels), 1, hspace=config["SUBPLOT_HSPACE"],
                                    height_ratios=_height_ratios(panels, config))
    axes = [fig.add_subplot(grid[0, 0])]
    axes += [fig.add_subplot(grid[i, 0], sharex=axes[0]) for i in range(1, len(panels))]

    _draw_windows(axes, experiment, config)

    # Draw each panel.
    for ax, panel in zip(axes, panels):
        if panel["type"] == "oxygen":
            # Set and measured O2 differ in line style as well as colour (dashed / solid), so they stay distinguishable in grey scale
            # and for colour-blind readers.
            for key, label, colour, line_style in (
                    ("CsO2", config["SET_O2_LABEL"], config["SET_O2_COLOUR"], config.get("SET_O2_LINE_STYLE", "-")),
                    ("CcO2", config["MEASURED_O2_LABEL"], config["MEASURED_O2_COLOUR"], config.get("MEASURED_O2_LINE_STYLE", "-"))):
                if key not in experiment:
                    continue
                t, y = _first_series(experiment[key])
                ax.plot(t, y, label=label, zorder=3, linestyle=line_style, **({} if colour is None else {"color": colour}))
            ax.set_ylabel(config["O2_AXIS_LABEL"], labelpad=config["Y_LABEL_PAD"])
            _set_min_ticks(ax.yaxis, config["O2_Y_NUM_TICKS"])
            if config["O2_Y_MIN"] is not None or config["O2_Y_MAX"] is not None:
                ax.set_ylim(config["O2_Y_MIN"], config["O2_Y_MAX"])

        elif panel["type"] == "vo2":
            t, y = _first_series(vo2_df)
            ax.plot(t, y, label=config["VO2_LABEL"], zorder=3,
                    **({} if config["VO2_COLOUR"] is None else {"color": config["VO2_COLOUR"]}))
            ax.set_ylabel(vo2_label, labelpad=config["Y_LABEL_PAD"])
            _set_min_ticks(ax.yaxis, config["VO2_Y_NUM_TICKS"])
            y_max = config["VO2_Y_MAX"]
            if config["VO2_Y_PERCENTILE_MAX"] is not None and np.isfinite(y).any():
                keep = (np.isfinite(y) & (t >= np.nanmin(t) + config["Y_SCALE_IGNORE_FIRST_MINUTES"])
                        & (t <= np.nanmax(t) - config.get("Y_SCALE_IGNORE_LAST_MINUTES", 0.0)))
                if keep.any():
                    y_max = np.percentile(y[keep], config["VO2_Y_PERCENTILE_MAX"])
            ax.set_ylim(config["VO2_Y_MIN"], y_max)

        else:  # haem
            t = get_times(haem_data)
            for haem in panel["haems"]:
                ax.plot(t, get_values(haem_data, haem), label=haem, color=haem_colours.get(simplify_name(haem)),
                        linewidth=config["LINE_WIDTH"], zorder=3)
            ax.set_ylabel(panel["title"], labelpad=config["Y_LABEL_PAD"])
            _set_min_ticks(ax.yaxis, config["HAEM_Y_NUM_TICKS"])
            if config["HAEM_Y_MIN"] is not None or config["HAEM_Y_MAX"] is not None:
                ax.set_ylim(config["HAEM_Y_MIN"], config["HAEM_Y_MAX"])
            else:
                limits = _ylim_ignoring_start(t, [get_values(haem_data, h) for h in panel["haems"]],
                                              config["Y_SCALE_IGNORE_FIRST_MINUTES"],
                                              ignore_last_minutes=config.get("Y_SCALE_IGNORE_LAST_MINUTES", 0.0))
                if limits:
                    ax.set_ylim(*limits)

        if config["SHOW_LEGENDS"].get(panel["type"], True):
            # A haem panel's legend is just the word when it holds a single trace (HAEM_LEGEND_TEXT_ONLY).
            _legend(ax, config, text_only=(panel["type"] == "haem" and len(panel["haems"]) == 1
                                           and config.get("HAEM_LEGEND_TEXT_ONLY", False)),
                    location=config.get("LEGEND_LOCATIONS", {}).get(panel["type"]))

    # Format axes; x limits default to the span of the plotted data. Only the lowest axis shows x tick labels.
    for ax in axes:
        ax.tick_params(axis="both", labelsize=config["TICK_FONT_SIZE"], direction="in")
        ax.spines["top"].set_visible(config["AXES_TOP_SPINE"])
        ax.spines["right"].set_visible(config["AXES_RIGHT_SPINE"])

        x_data = np.concatenate([line.get_xdata() for line in ax.get_lines() if len(line.get_xdata())])
        left = config["X_MIN"] if config["X_MIN"] is not None else np.nanmin(x_data)
        right = config["X_MAX"] if config["X_MAX"] is not None else np.nanmax(x_data)
        ax.set_xlim(left=left, right=right)
    for ax in axes[:-1]:
        ax.tick_params(axis="x", labelbottom=False)
    if config.get("HIDE_TOUCHING_TICK_LABELS", False):
        for ax in axes[1:]:
            ax.yaxis.set_major_formatter(_HideTopTickLabels(config["TICK_FONT_SIZE"]))

    axes[-1].set_xlabel(config["TIME_AXIS_LABEL"], labelpad=config["TIME_AXIS_LABEL_PAD"])
    _set_min_ticks(axes[-1].xaxis, config["X_NUM_TICKS"])   # the time axis is shared by all the panels

    # Event lines (in front of data) and labels (below the lowest axis).
    events = experiment.get("metadata", {}).get("events", [])
    if config["PLOT_EVENTS"]:
        for event in events:
            for ax in axes:
                ax.axvline(event["time"], linestyle=config["EVENT_LINE_STYLE"], linewidth=config["EVENT_LINE_WIDTH"],
                           color=config["EVENT_LINE_COLOUR"], alpha=config["EVENT_LINE_ALPHA"], zorder=20)

        if config["EVENT_LABELS"]:
            # Every label sits EVENT_LABEL_OFFSET points below the lowest axis, whatever its height. With "start" or "end"
            # the text is anchored by that end at the dashed line and rotates about it (use a rotation that runs away from
            # the axis: 270-360 for "start", 0-90 for "end"); "center" keeps the old centred behaviour.
            horizontal = {"start": "left", "center": "center", "end": "right"}[anchor]
            on_top = config.get("EVENT_LABELS_ON_TOP", True)
            label_ax = axes[0] if on_top else axes[-1]
            y_edge, sign, vertical = (1, 1, "bottom") if on_top else (0, -1, "top")
            for event in events:
                conc = event.get("concentration_uM")
                text = f"{float(conc):g} µM {event.get('label', '')}".strip() if conc is not None else str(event.get("label", ""))
                label_ax.annotate(text,
                                  xy=(event["time"], y_edge), xycoords=label_ax.get_xaxis_transform(),
                                  xytext=(0, sign * config["EVENT_LABEL_OFFSET"]), textcoords="offset points",
                                  rotation=config["EVENT_LABEL_ROTATION"],
                                  rotation_mode="default" if anchor == "center" else "anchor",
                                  ha=horizontal, va=vertical, fontsize=config["EVENT_LABEL_FONTSIZE"],
                                  annotation_clip=False, zorder=21)

    # One shared y-label spanning all the haem axes (an invisible axes covering their rows keeps it aligned
    # under any later layout change); each haem axis carries only its own short label.
    haem_rows = [i for i, panel in enumerate(panels) if panel["type"] == "haem"]
    label_axes = list(axes)
    if haem_rows:
        span = fig.add_subplot(grid[haem_rows[0]:haem_rows[-1] + 1, 0], frameon=False)
        span.set_xticks([])
        span.set_yticks([])
        # The shared label sits beside the haem axes' own labels, so it needs one label's thickness more room when they exist.
        span_pad = config["HAEM_SPAN_LABEL_PAD"]
        if any(panels[i]["title"] for i in haem_rows):
            span_pad += 1.2 * config.get("LABEL_FONT_SIZE", config["TICK_FONT_SIZE"] + 1) + config["Y_LABEL_PAD"]
        span.set_ylabel(haem_label, labelpad=span_pad)
        label_axes.append(span)

    # Line every y-label up at the same distance (Y_LABEL_PAD) from the left-most tick labels.
    if config["ALIGN_Y_LABELS"]:
        fig.align_ylabels(label_axes)

    return axes, panels


def plot_experiment(experiment, config, export_root):
    """Plot one experiment in its own figure, optionally save SVG/PNG to ``<export_root>/<name>/``, then show or close it."""
    name = experiment["experiment_name"]
    export_root = Path(export_root)

    fig = plt.figure(figsize=config["FIGURE_SIZE"], dpi=config["FIGURE_DPI"])
    axes, panels = draw_experiment(fig, fig.add_gridspec(1, 1)[0, 0], experiment, config)

    if any(panel["type"] == "haem" for panel in panels):
        print(f"    Haem data selected: {config['HAEM_PLOT_VALUES']}")

    suptitle = None
    if config.get("TITLE_STYLE", "heading") == "watermark":
        # Faint run name in the top-left corner, outside the layout, so it takes none of the figure's height.
        width_pt, height_pt = (v * 72.0 for v in config["FIGURE_SIZE"])
        pad = config.get("LAYOUT_PAD_PT", 3.0)
        mark = fig.text(pad / width_pt, 1.0 - pad / height_pt, experiment_title(experiment, config), ha="left", va="top",
                        **watermark_style(config))
        mark.set_in_layout(False)
    else:
        suptitle = fig.suptitle(experiment_title(experiment, config), fontsize=config["TITLE_FONT_SIZE"], fontweight="bold")
    if config.get("FIT_MARGINS", False):
        # Margins fitted to the drawn labels, so nothing is cut off or overlaps at any figure or font size.
        fit_figure_to_canvas(fig, config["LAYOUT_PAD_PT"], suptitle, config["TITLE_GAP_PT"])
    else:
        fig.subplots_adjust(bottom=config["FIGURE_BOTTOM_MARGIN"])

    if config["SAVE_FIGURES"]:
        width, height = config["FIGURE_SIZE"]
        save_figure_exact(fig, export_root / name, name, ("svg", "png"), config["FIGURE_SIZE"], config["FIGURE_DPI"],
                          tight=config["TIGHT_BBOX"])
        print(f"    Figure saved at {width:g} x {height:g} in, {config['FIGURE_DPI']} dpi "
              f"({round(width * config['FIGURE_DPI'])} x {round(height * config['FIGURE_DPI'])} px): {export_root.name}/{name}/")

    if config["SHOW_INDIVIDUAL_FIGURES"]:
        plt.show()
    else:
        plt.close(fig)

    return fig, axes
