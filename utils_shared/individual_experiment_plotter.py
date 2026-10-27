# -*- coding: utf-8 -*-
"""
Plot one experiment: oxygen, VO2 and configured haem panels, with averaging windows and
events.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from pathlib import Path
import re
from typing import Any, List, Optional, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.gridspec import SubplotSpec
from matplotlib.legend import Legend
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator, ScalarFormatter
import numpy as np
import pandas as pd

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.figure_layout import figure_canvas_fitter
from utils_shared.helpers import (concentration_formatter,
                                  figure_saver,
                                  name_simplifier,
                                  )
from utils_shared.schema import (HAEM_KEYS,
                                 measurement_column_finder,
                                 source_resolver,
                                 time_getter,
                                 value_getter,
                                 VO2_KEYS,
                                 )


# ---- _HIDE TOP TICK LABELS -----------------------------------------------------------
class _HideTopTickLabels(ScalarFormatter):
    """
    A y-axis formatter that leaves out the tick label nearest the top edge when it would
    run into the panel above

    Stacked panels touch, so a label at the very top of one panel overlaps the bottom
    label of the panel above it. A label is
    dropped if its tick lies within 0.7 x ``font_pt`` points (the height of a digit) of
    the top of the axis, whatever the panel's height.
    """

    # ---- __INIT__ --------------------------------------------------------------------
    def __init__(self, font_pt: float) -> None:
        """
        ---- Summary ----
        Helper method to create the formatter.

        ---- Inputs ----
        font_pt : float
            Font size of the tick labels in points.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        super().__init__()
        self._font_pt = font_pt

    # ---- __CALL__ --------------------------------------------------------------------
    def __call__(self, x: float, pos: Optional[int] = None) -> str:
        """
        ---- Summary ----
        Helper method to format one tick label, returning an empty string for the label
        nearest the top edge when it would run into the panel above.

        ---- Inputs ----
        x : float
            Tick value.
        pos : Optional[int]
            Tick position, as passed by matplotlib.

        ---- Globals read ----
        None.

        ---- Outputs ----
        str
            Tick label text, or an empty string for a label within 0.7 x font_pt points
            of the top of the axis.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        A label is dropped when x >= high - (high - low) x min(0.5, 0.7 x font_pt /
        axes_height_pt), where low and high are the view limits.

        ---- Helpers ----
        None.
        """

        axes = self.axis.axes
        height_pt = axes.get_window_extent().height * 72.0 / axes.figure.dpi
        low, high = self.axis.get_view_interval()
        if (height_pt > 0 and
            x >= high - (high - low) * min(0.5, 0.7 * self._font_pt / height_pt)
            ):
            return ''
        return super().__call__(x, pos)


# ---- INDIVIDUAL EXPERIMENT PLOTTER HELPERS -------------------------------------------


# ---- _AXES LEGEND DRAWER -------------------------------------------------------------
def _axes_legend_drawer(ax: Axes,
                        config: dict,
                        text_only: bool = False,
                        location: Optional[str] = None,
                        ) -> Legend:
    """
    ---- Summary ----
    Helper function to draw a legend with an optional thin box.

    ---- Inputs ----
    ax : Axes
        Matplotlib axes.
    config : dict
        Individual-experiment plot settings, as built by Config.plot_config in
        config.py.
    text_only : bool
        True drops the coloured line beside each entry (used for haem panels, where the
        colour already identifies the trace).
    location : Optional[str]
        Legend location; None uses config["LEGEND_LOCATION"].

    ---- Globals read ----
    config keys LEGEND_LOCATION, LEGEND_COLUMNS, LEGEND_FRAME, LEGEND_FONT_SIZE,
    LEGEND_FRAME_LINE_WIDTH and LEGENDS_OUTSIDE (legend in the white space right of
    the axes).

    ---- Outputs ----
    Legend
        The legend that was drawn.

    ---- Globals mutated ----
    None. Adds a legend to ``ax`` (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 Build the legend options --------------------------------------------------
    options = {'loc': location or config['LEGEND_LOCATION'],
               'ncol': config['LEGEND_COLUMNS'],
               'frameon': config['LEGEND_FRAME'],
               'fontsize': config['LEGEND_FONT_SIZE'],
               }

    # ---- 2 Draw the legend -----------------------------------------------------------
    if text_only:
        options.update(handlelength=0, handletextpad=0)
    if config.get('LEGENDS_OUTSIDE', False):
        options.update(loc='center left', bbox_to_anchor=(1.02, 0.5), borderaxespad=0)
    legend = ax.legend(**options)
    if config['LEGEND_FRAME']:
        legend.get_frame().set_linewidth(config.get('LEGEND_FRAME_LINE_WIDTH', 0.4))
    return legend


# ---- _FIRST SERIES GETTER ------------------------------------------------------------
def _first_series_getter(df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
    """
    ---- Summary ----
    Helper function to get the time and values of the first measurement column of a
    DataFrame.

    ---- Inputs ----
    df : pd.DataFrame
        Time-resolved data frame (DATA_FORMAT.md).

    ---- Globals read ----
    None.

    ---- Outputs ----
    Tuple[np.ndarray, np.ndarray]
        (times, values) of the first measurement column.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    measurement_column_finder
    time_getter
    value_getter
    """

    column = measurement_column_finder(df)[0]
    return time_getter(df), value_getter(df, column)


# ---- _HAEM DATA SELECTOR -------------------------------------------------------------
def _haem_data_selector(experiment: dict,
                        config: dict,
                        ) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    ---- Summary ----
    Helper function to pick the haem data frame the haem panels plot.

    ---- Inputs ----
    experiment : dict
        Experiment dictionary, as defined in DATA_FORMAT.md.
    config : dict
        Individual-experiment plot settings, as built by Config.plot_config in
        config.py.

    ---- Globals read ----
    config keys HAEM_PANELS and HAEM_PLOT_VALUES; schema.HAEM_KEYS.

    ---- Outputs ----
    Tuple[Optional[pd.DataFrame], Optional[str]]
        (haem data frame or None, source name). None when haem panels are off or the
        source is missing from the experiment (a warning is printed).

    ---- Globals mutated ----
    None. Prints a warning when the source is missing (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    source_resolver
    """

    # ---- 1 Read the settings ---------------------------------------------------------
    source = config['HAEM_PLOT_VALUES']
    if not config['HAEM_PANELS'] or source is None:
        return None, source

    # ---- 2 Select the data -----------------------------------------------------------
    try:
        _, haem_data = source_resolver(experiment, source, HAEM_KEYS, 'haem')
    except ValueError as exc:
        if source not in HAEM_KEYS:
            raise
        print(f'  Warning: {exc} Haem panels will be skipped.')
        return None, source
    return haem_data, source


# ---- _HEIGHT RATIO CALCULATOR --------------------------------------------------------
def _height_ratio_calculator(panels: List[dict], config: dict) -> List[float]:
    """
    ---- Summary ----
    Helper function to calculate the relative panel heights from PANEL_HEIGHT_RATIOS.

    ---- Inputs ----
    panels : List[dict]
        Panel specifications; each has a "type" of oxygen, vo2 or haem.
    config : dict
        Individual-experiment plot settings, as built by Config.plot_config in
        config.py.

    ---- Globals read ----
    config keys PANEL_HEIGHT_RATIOS and EQUAL_PANEL_HEIGHTS.

    ---- Outputs ----
    List[float]
        Relative height of each panel. The haem weight is shared equally between the
        haem panels. Raises ValueError for a missing or non-positive weight.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    ratio = weight for oxygen and vo2 panels; weight / n_haem for each haem panel; 1 for
    every panel when EQUAL_PANEL_HEIGHTS is set.

    ---- Helpers ----
    None.
    """

    # ---- 1 Read the weights ----------------------------------------------------------
    if config.get('EQUAL_PANEL_HEIGHTS'):
        return [1.0] * len(panels)
    weights = config['PANEL_HEIGHT_RATIOS']
    n_haem = sum(panel['type'] == 'haem' for panel in panels)

    # ---- 2 Calculate the ratios ------------------------------------------------------
    ratios = []
    for panel in panels:
        weight = weights.get(panel['type'])
        if weight is None or weight <= 0:
            raise ValueError(f'PANEL_HEIGHT_RATIOS needs a positive value for '
                             f"{panel['type']!r}; got {weight!r}.",
                             )
        ratios.append(weight / n_haem if panel['type'] == 'haem' else weight)
    return ratios


# ---- _MIN TICKS SETTER ---------------------------------------------------------------
def _min_ticks_setter(axis: Any, count: Optional[int]) -> None:
    """
    ---- Summary ----
    Helper function to make sure an axis has at least a given number of ticks, still at
    round values.

    ---- Inputs ----
    axis : Any
        Matplotlib axis object (ax.xaxis or ax.yaxis).
    count : Optional[int]
        Minimum number of ticks; None leaves the ticks automatic.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing; the major locator of the axis is replaced.

    ---- Globals mutated ----
    None. Sets the major locator of ``axis`` (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if count is not None:
        axis.set_major_locator(MaxNLocator(nbins=count - 1, min_n_ticks=count))


# ---- _PANEL BUILDER ------------------------------------------------------------------
def _panel_builder(experiment: dict,
                   config: dict,
                   haem_data: Optional[pd.DataFrame],
                   ) -> List[dict]:
    """
    ---- Summary ----
    Helper function to list the panels to draw: oxygen, VO2, then one for each
    configured haem panel with matching data.

    ---- Inputs ----
    experiment : dict
        Experiment dictionary, as defined in DATA_FORMAT.md.
    config : dict
        Individual-experiment plot settings, as built by Config.plot_config in
        config.py.
    haem_data : Optional[pd.DataFrame]
        Haem data frame, or None.

    ---- Globals read ----
    config keys PLOT_SET_AND_MEASURED_O2, PLOT_VO2, O2_PANEL_TITLE, VO2_PANEL_TITLE and
    HAEM_PANELS.

    ---- Outputs ----
    List[dict]
        Panel specifications {type, title, haems}. Raises ValueError when no panel is
        selected.

    ---- Globals mutated ----
    None. Prints a warning for haems missing from the data (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    measurement_column_finder
    name_simplifier
    """

    # ---- 1 Add the panels ------------------------------------------------------------
    panels = []
    if config['PLOT_SET_AND_MEASURED_O2']:
        panels.append({'type': 'oxygen', 'title': config['O2_PANEL_TITLE']})
    if config['PLOT_VO2']:
        panels.append({'type': 'vo2', 'title': config['VO2_PANEL_TITLE']})
    if haem_data is not None:
        lookup = {name_simplifier(column): column
                  for column in measurement_column_finder(haem_data)
                  }
        for spec in config['HAEM_PANELS']:
            matched = [lookup[name_simplifier(h)]
                       for h in spec['haems']
                       if name_simplifier(h) in lookup
                       ]
            missing = [h for h in spec['haems'] if name_simplifier(h) not in lookup]
            if missing:
                print(f"  Warning: haem panel {spec['label']!r} could not find: "
                      f'{missing}',
                      )
            if matched:
                panels.append({'type': 'haem',
                               'title': spec['label'],
                               'haems': matched,
                               },
                              )

    # ---- 2 Check there is something to plot ------------------------------------------
    if not panels:
        raise ValueError('No panels selected. Enable an oxygen/VO2 panel or configure '
                         'matching haem panels.',
                         )
    return panels


# ---- _VO2 YMAX CALCULATOR ------------------------------------------------------------
def _vo2_ymax_calculator(y: np.ndarray,
                         window_fraction: float,
                         headroom: float,
                         ) -> float:
    """
    ---- Summary ----
    Helper function to choose the top of the OCR axis so that the whole run is shown
    (including the start) while a narrow spike, such as the one when dithionite is
    added, does not stretch the axis.

    ---- Inputs ----
    y : np.ndarray
        OCR values of the whole run (NaN allowed).
    window_fraction : float
        Width of the rolling median as a fraction of the number of points; spikes
        narrower than half of it are removed from the envelope.
    headroom : float
        Fraction of the envelope height added above the highest smoothed value.

    ---- Globals read ----
    None.

    ---- Outputs ----
    float
        Top of the axis; NaN when there are no finite values.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    smooth = rolling median of y (window = window_fraction x n points, at least 5);
    noise = 95th percentile of |y - smooth|;
    top = max(smooth) + noise + headroom x max(smooth).

    ---- Helpers ----
    None.
    """

    # ---- 1 Smooth away the spikes ----------------------------------------------------
    values = pd.Series(np.asarray(y, dtype=float))
    if not np.isfinite(values).any():
        return float('nan')
    window = max(5, int(round(window_fraction * len(values))))
    smooth = values.rolling(window, center=True, min_periods=1).median()

    # ---- 2 Add the noise and the headroom --------------------------------------------
    noise = float(np.nanpercentile(np.abs(values - smooth), 95))
    top = float(np.nanmax(smooth))
    return top + noise + headroom * max(top, 0.0)


# ---- _WINDOW DRAWER ------------------------------------------------------------------
def _window_drawer(axes: List[Axes], experiment: dict, config: dict) -> None:
    """
    ---- Summary ----
    Helper function to draw the averaging windows behind the data on every axis.

    ---- Inputs ----
    axes : List[Axes]
        Axes of the experiment, top to bottom.
    experiment : dict
        Experiment dictionary, as defined in DATA_FORMAT.md.
    config : dict
        Individual-experiment plot settings, as built by Config.plot_config in
        config.py.

    ---- Globals read ----
    config keys PLOT_AVERAGING_WINDOWS and the AVERAGING_WINDOW_* appearance settings.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Adds shaded spans and labels to the axes (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _window_label_builder
    """

    # ---- 1 Check there are windows to draw -------------------------------------------
    averages = experiment.get('averages')
    if not (config['PLOT_AVERAGING_WINDOWS'] and averages):
        return

    # ---- 2 Draw each window ----------------------------------------------------------
    for window_name, window in averages['windows'].items():
        start, end = window['start_time'], window['end_time']
        if end <= start:
            continue
        for ax in axes:
            ax.axvspan(start,
                       end,
                       facecolor=config['AVERAGING_WINDOW_COLOUR'],
                       alpha=config['AVERAGING_WINDOW_ALPHA'],
                       edgecolor=config['AVERAGING_WINDOW_EDGE_COLOUR'],
                       linewidth=config.get('AVERAGING_WINDOW_EDGE_LINE_WIDTH', 0.8),
                       zorder=0,
                       )
        text = _window_label_builder(window_name, config)
        if text:
            axes[0].text((start + end) / 2,
                         0.98,
                         text,
                         transform=axes[0].get_xaxis_transform(),
                         ha='center',
                         va='top',
                         fontsize=config['AVERAGING_WINDOW_LABEL_FONT_SIZE'],
                         color=config['AVERAGING_WINDOW_EDGE_COLOUR'],
                         zorder=2,
                         )


# ---- _WINDOW LABEL BUILDER -----------------------------------------------------------
def _window_label_builder(window_name: str, config: dict) -> str:
    """
    ---- Summary ----
    Helper function to build the text of an averaging window from
    AVERAGING_WINDOW_LABEL_FORMAT.

    ---- Inputs ----
    window_name : str
        Window name, for example 'average3'.
    config : dict
        Individual-experiment plot settings, as built by Config.plot_config in
        config.py.

    ---- Globals read ----
    config key AVERAGING_WINDOW_LABEL_FORMAT ({n} is the number, {name} the window
    name).

    ---- Outputs ----
    str
        Label text; empty when the format is empty.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    match = re.search(r'(\d+)$', window_name)
    number = int(match.group(1)) if match else window_name
    return config['AVERAGING_WINDOW_LABEL_FORMAT'].format(n=number, name=window_name)


# ---- _YLIM CALCULATOR ----------------------------------------------------------------
def _ylim_calculator(times: np.ndarray,
                     series: List[np.ndarray],
                     ignore_minutes: float,
                     margin: float = 0.05,
                     ignore_last_minutes: float = 0.0,
                     ) -> Optional[Tuple[float, float]]:
    """
    ---- Summary ----
    Helper function to calculate y limits from the data after the ignored start and
    before the ignored end, plus a margin.

    ---- Inputs ----
    times : np.ndarray
        Times in minutes.
    series : List[np.ndarray]
        Value arrays on the same time axis.
    ignore_minutes : float
        Minutes at the start left out of the limits.
    margin : float
        Fraction of the data range added on both sides.
    ignore_last_minutes : float
        Minutes at the end left out of the limits.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[Tuple[float, float]]
        (low, high), or None when no finite data remain.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    pad = (max - min) x margin (1 if the range is 0); limits = (min - pad, max + pad).

    ---- Helpers ----
    None.
    """

    keep = (np.isfinite(times) & (times >= np.nanmin(times) + ignore_minutes
                                  ) & (times <= np.nanmax(times) - ignore_last_minutes)
            )
    values = np.concatenate([np.asarray(s, dtype=float)[keep] for s in series])
    values = values[np.isfinite(values)]
    if values.size == 0:
        return None
    low, high = values.min(), values.max()
    pad = (high - low) * margin or 1.0
    return low - pad, high + pad


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- EXPERIMENT DRAWER ---------------------------------------------------------------
def experiment_drawer(fig: Figure,
                      subplot_spec: SubplotSpec,
                      experiment: dict,
                      config: dict,
                      ) -> Tuple[List[Axes], List[dict]]:
    """
    ---- Summary ----
    Main function to draw one experiment's stacked panels into a cell of an existing
    figure. It adds no title, adjusts no margins and saves nothing; event labels hang
    below the lowest axis, so room is needed underneath the cell.

    ---- Inputs ----
    fig : Figure
        Matplotlib figure.
    subplot_spec : SubplotSpec
        Grid cell the experiment is drawn in.
    experiment : dict
        Experiment dictionary, as defined in DATA_FORMAT.md.
    config : dict
        Individual-experiment plot settings, as built by Config.plot_config in
        config.py.

    ---- Globals read ----
    Many config keys (panels, axes labels, colours, events, windows; see
    Config.plot_config in config.py) and schema.VO2_KEYS.

    ---- Outputs ----
    Tuple[List[Axes], List[dict]]
        (axes from top to bottom, panel specifications drawn).

    ---- Globals mutated ----
    None. Adds axes and artists to ``fig`` (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _axes_legend_drawer
    _first_series_getter
    _haem_data_selector
    _height_ratio_calculator
    _min_ticks_setter
    _panel_builder
    _window_drawer
    _ylim_calculator
    name_simplifier
    source_resolver
    time_getter
    value_getter
    """

    # ---- 1 Select the data and panels ------------------------------------------------
    haem_data, haem_source = _haem_data_selector(experiment, config)
    panels = _panel_builder(experiment, config, haem_data)

    # ---- 2 Prepare the labels and colours --------------------------------------------
    vo2_df = vo2_label = None
    if config['PLOT_VO2']:
        _, vo2_df = source_resolver(experiment,
                                    config['VO2_PLOT_VALUES'],
                                    VO2_KEYS,
                                    'VO2',
                                    )
        vo2_label = config['VO2_AXIS_LABELS'][config['VO2_PLOT_VALUES']]
    haem_label = (config['HAEM_AXIS_LABELS'][haem_source]
                  if haem_data is not None
                  else None
                  )
    haem_colours = {name_simplifier(k): v for k, v in config['HAEM_COLOURS'].items()}
    anchor = config['EVENT_LABEL_ANCHOR']
    if anchor not in ('start', 'center', 'end'):
        raise ValueError(f'EVENT_LABEL_ANCHOR must be "start", "center" or "end"; got '
                         f'{anchor!r}.',
                         )

    # ---- 3 Build the axes grid -------------------------------------------------------
    height_ratios = _height_ratio_calculator(panels, config)
    grid = (subplot_spec.subgridspec(len(panels),
                                     1,
                                     hspace=config['SUBPLOT_HSPACE'],
                                     height_ratios=height_ratios,
                                     )
            )
    axes = [fig.add_subplot(grid[0, 0])]
    axes += [fig.add_subplot(grid[i, 0], sharex=axes[0]) for i in range(1, len(panels))]
    _window_drawer(axes, experiment, config)

    # ---- 4 Draw each panel -----------------------------------------------------------
    # Draw each panel.
    for ax, panel in zip(axes, panels):
        if panel['type'] == 'oxygen':
            # Set and measured O2 differ in line style as well as colour (dashed /
            # solid), so they stay distinguishable in grey scale
            # and for colour-blind readers.
            for key, label, colour, line_style in (('CsO2',
                                                    config['SET_O2_LABEL'],
                                                    config['SET_O2_COLOUR'],
                                                    config.get('SET_O2_LINE_STYLE',
                                                               '-',
                                                               ),
                                                    ),
                                                   ('CcO2',
                                                    config['MEASURED_O2_LABEL'],
                                                    config['MEASURED_O2_COLOUR'],
                                                    config.get('MEASURED_O2_LINE_STYLE',
                                                               '-',
                                                               ),
                                                    ),
                                                   ):
                if key not in experiment:
                    continue
                t, y = _first_series_getter(experiment[key])
                ax.plot(t,
                        y,
                        label=label,
                        zorder=3,
                        linestyle=line_style,
                        **({} if colour is None else {'color': colour}),
                        )
            ax.set_ylabel(config['O2_AXIS_LABEL'], labelpad=config['Y_LABEL_PAD'])
            _min_ticks_setter(ax.yaxis, config['O2_Y_NUM_TICKS'])
            if config['O2_Y_MIN'] is not None or config['O2_Y_MAX'] is not None:
                ax.set_ylim(config['O2_Y_MIN'], config['O2_Y_MAX'])
        elif panel['type'] == 'vo2':
            t, y = _first_series_getter(vo2_df)
            ax.plot(t,
                    y,
                    label=config['VO2_LABEL'],
                    zorder=3,
                    **({}
                       if config['VO2_COLOUR'] is None
                       else {'color': config['VO2_COLOUR']}
                       ),
                    )
            ax.set_ylabel(vo2_label, labelpad=config['Y_LABEL_PAD'])
            _min_ticks_setter(ax.yaxis, config['VO2_Y_NUM_TICKS'])
            y_max = config['VO2_Y_MAX']
            if y_max is None and np.isfinite(y).any():
                y_max = _vo2_ymax_calculator(y,
                                             config['VO2_Y_SPIKE_WINDOW_FRACTION'],
                                             config['VO2_Y_HEADROOM'],
                                             )
            ax.set_ylim(config['VO2_Y_MIN'], y_max)
        else:  # haem
            t = time_getter(haem_data)
            for haem in panel['haems']:
                ax.plot(t,
                        value_getter(haem_data, haem),
                        label=haem,
                        color=haem_colours.get(name_simplifier(haem)),
                        linewidth=config['LINE_WIDTH'],
                        zorder=3,
                        )
            ax.set_ylabel(panel['title'], labelpad=config['Y_LABEL_PAD'])
            ax.haem_names = [name_simplifier(haem) for haem in panel['haems']]
            _min_ticks_setter(ax.yaxis, config['HAEM_Y_NUM_TICKS'])
            if config['HAEM_Y_MIN'] is not None or config['HAEM_Y_MAX'] is not None:
                ax.set_ylim(config['HAEM_Y_MIN'], config['HAEM_Y_MAX'])
            else:
                limits = (_ylim_calculator(t,
                                           [value_getter(haem_data, h)
                                            for h in panel['haems']
                                            ],
                                           config['Y_SCALE_IGNORE_FIRST_MINUTES'],
                                           ignore_last_minutes=config.get(
                                               'Y_SCALE_IGNORE_LAST_MINUTES',
                                               0.0,
                                           ),
                                           )
                          )
                if limits:
                    ax.set_ylim(*limits)
        if config['SHOW_LEGENDS'].get(panel['type'], True):
            # A haem panel's legend is just the word when it holds a single trace
            # (HAEM_LEGEND_TEXT_ONLY).
            _axes_legend_drawer(ax,
                                config,
                                text_only=(panel['type'] == 'haem' and
                                           len(panel['haems']) == 1 and
                                           config.get('HAEM_LEGEND_TEXT_ONLY', False)
                                           ),
                                location=config.get('LEGEND_LOCATIONS',
                                                    {},
                                                    ).get(panel['type']),
                                )

    # ---- 5 Format the axes -----------------------------------------------------------
    # Format axes; x limits default to the span of the plotted data. Only the lowest
    # axis shows x tick labels.
    for ax in axes:
        ax.tick_params(axis='both', labelsize=config['TICK_FONT_SIZE'], direction='in')
        ax.spines['top'].set_visible(config['AXES_TOP_SPINE'])
        ax.spines['right'].set_visible(config['AXES_RIGHT_SPINE'])
        x_data = np.concatenate([line.get_xdata()
                                 for line in ax.get_lines()
                                 if len(line.get_xdata())
                                 ],
                                )
        left = config['X_MIN'] if config['X_MIN'] is not None else np.nanmin(x_data)
        right = config['X_MAX'] if config['X_MAX'] is not None else np.nanmax(x_data)
        ax.set_xlim(left=left, right=right)
    for ax in axes[:-1]:
        ax.tick_params(axis='x', labelbottom=False)
    max_ticks = config.get('HAEM_Y_MAX_TICKS')
    for ax, panel in zip(axes, panels):
        if max_ticks and panel['type'] == 'haem':
            low, high = sorted(ax.get_ylim())
            ticks = [tick for tick in ax.get_yticks() if low <= tick <= high]
            if len(ticks) > max_ticks:
                ax.set_yticks([ticks[0], ticks[-1]])
    if not config.get('SHOW_Y_LABELS', True):
        for ax in axes:
            ax.set_ylabel('')
            ax.tick_params(axis='y', labelleft=False)
    if config.get('HIDE_TOUCHING_TICK_LABELS', False):
        for ax in axes[1:]:
            ax.yaxis.set_major_formatter(_HideTopTickLabels(config['TICK_FONT_SIZE']))
    axes[-1].set_xlabel(config['TIME_AXIS_LABEL'],
                        labelpad=config['TIME_AXIS_LABEL_PAD'],
                        )
    # the time axis is shared by all the panels
    _min_ticks_setter(axes[-1].xaxis, config['X_NUM_TICKS'])

    # ---- 6 Draw the events -----------------------------------------------------------
    # Event lines (in front of data) and labels (below the lowest axis).
    events = experiment.get('metadata', {}).get('events', [])
    if config['PLOT_EVENTS']:
        for event in events:
            for ax in axes:
                ax.axvline(event['time'],
                           linestyle=config['EVENT_LINE_STYLE'],
                           linewidth=config['EVENT_LINE_WIDTH'],
                           color=config['EVENT_LINE_COLOUR'],
                           alpha=config['EVENT_LINE_ALPHA'],
                           zorder=20,
                           )
        if config['EVENT_LABELS']:
            # Every label sits EVENT_LABEL_OFFSET points below the lowest axis, whatever
            # its height. With "start" or "end"
            # the text is anchored by that end at the dashed line and rotates about it
            # (use a rotation that runs away from
            # the axis: 270-360 for "start", 0-90 for "end"); "center" keeps the old
            # centred behaviour.
            horizontal = {'start': 'left', 'center': 'center', 'end': 'right'}[anchor]
            on_top = config.get('EVENT_LABELS_ON_TOP', True)
            label_ax = axes[0] if on_top else axes[-1]
            y_edge, sign, vertical = (1, 1, 'bottom') if on_top else (0, -1, 'top')
            for event in events:
                conc = event.get('concentration_uM')
                text = (f"{concentration_formatter(conc)} "
                        f"{event.get('label', '')}".strip()
                        if conc is not None
                        else str(event.get('label', ''))
                        )
                label_ax.annotate(text,
                                  xy=(event['time'], y_edge),
                                  xycoords=label_ax.get_xaxis_transform(),
                                  xytext=(0, sign * config['EVENT_LABEL_OFFSET']),
                                  textcoords='offset points',
                                  rotation=config['EVENT_LABEL_ROTATION'],
                                  rotation_mode=('default'
                                                 if anchor == 'center'
                                                 else 'anchor'
                                                 ),
                                  ha=horizontal,
                                  va=vertical,
                                  fontsize=config['EVENT_LABEL_FONTSIZE'],
                                  annotation_clip=False,
                                  zorder=21,
                                  )

    # ---- 7 Add the shared haem label -------------------------------------------------
    # One shared y-label spanning all the haem axes (an invisible axes covering their
    # rows keeps it aligned
    # under any later layout change); each haem axis carries only its own short label.
    haem_rows = [i for i, panel in enumerate(panels) if panel['type'] == 'haem']
    label_axes = list(axes)
    if haem_rows and config.get('SHOW_Y_LABELS', True):
        span = fig.add_subplot(grid[haem_rows[0]:haem_rows[-1] + 1, 0], frameon=False)
        span.set_xticks([])
        span.set_yticks([])
        # The shared label sits beside the haem axes' own labels, so it needs one
        # label's thickness more room when they exist.
        span_pad = config['HAEM_SPAN_LABEL_PAD']
        if any(panels[i]['title'] for i in haem_rows):
            span_pad += (1.2 * config.get('LABEL_FONT_SIZE',
                                          config['TICK_FONT_SIZE'] + 1,
                                          ) + config['Y_LABEL_PAD']
                         )
        span.set_ylabel(haem_label,
                        labelpad=span_pad + 0.5 * config['TICK_FONT_SIZE'],
                        )
        label_axes.append(span)

    # ---- 8 Align the y labels --------------------------------------------------------
    # Line every y-label up at the same distance (Y_LABEL_PAD) from the left-most tick
    # labels.
    if config['ALIGN_Y_LABELS']:
        fig.align_ylabels(label_axes)
    return axes, panels


# ---- EXPERIMENT PLOTTER --------------------------------------------------------------
def experiment_plotter(experiment: dict,
                       config: dict,
                       export_root: Path,
                       ) -> Tuple[Figure, List[Axes]]:
    """
    ---- Summary ----
    Main function to plot one experiment in its own figure, optionally save it as svg
    and png, then show or close it.

    ---- Inputs ----
    experiment : dict
        Experiment dictionary, as defined in DATA_FORMAT.md.
    config : dict
        Individual-experiment plot settings, as built by Config.plot_config in
        config.py.
    export_root : Path
        Results folder.

    ---- Globals read ----
    config keys FIGURE_SIZE, FIGURE_DPI, TITLE_STYLE, LAYOUT_PAD_PT, FIT_MARGINS,
    TITLE_GAP_PT, SAVE_FIGURES, TIGHT_BBOX, SHOW_INDIVIDUAL_FIGURES and the title
    settings.

    ---- Outputs ----
    Tuple[Figure, List[Axes]]
        The figure (already closed unless SHOW_INDIVIDUAL_FIGURES is set) and its axes.

    ---- Globals mutated ----
    None. Writes <export_root>/<name>/<name>.svg and .png and prints a message (side
    effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    experiment_drawer
    experiment_title_builder
    figure_canvas_fitter
    figure_saver
    watermark_style_builder
    """

    # ---- 1 Draw the figure -----------------------------------------------------------
    name = experiment['experiment_name']
    export_root = Path(export_root)
    fig = plt.figure(figsize=config['FIGURE_SIZE'], dpi=config['FIGURE_DPI'])
    axes, panels = experiment_drawer(fig,
                                     fig.add_gridspec(1, 1)[0, 0],
                                     experiment,
                                     config,
                                     )
    if any(panel['type'] == 'haem' for panel in panels):
        print(f"    Haem data selected: {config['HAEM_PLOT_VALUES']}")

    # ---- 2 Add the title -------------------------------------------------------------
    suptitle = None
    if config.get('TITLE_STYLE', 'heading') == 'watermark':
        # Faint run name in the top-left corner, outside the layout, so it takes none of
        # the figure's height.
        width_pt, height_pt = (v * 72.0 for v in config['FIGURE_SIZE'])
        pad = config.get('LAYOUT_PAD_PT', 3.0)
        mark = fig.text(pad / width_pt,
                        1.0 - pad / height_pt,
                        experiment_title_builder(experiment, config),
                        ha='left',
                        va='top',
                        **watermark_style_builder(config),
                        )
        mark.set_in_layout(False)
    else:
        suptitle = fig.suptitle(experiment_title_builder(experiment, config),
                                fontsize=config['TITLE_FONT_SIZE'],
                                fontweight='bold',
                                )

    # ---- 3 Fit the margins -----------------------------------------------------------
    if config.get('FIT_MARGINS', False):
        # Margins fitted to the drawn labels, so nothing is cut off or overlaps at any
        # figure or font size.
        figure_canvas_fitter(fig,
                             config['LAYOUT_PAD_PT'],
                             suptitle,
                             config['TITLE_GAP_PT'],
                             )
    else:
        fig.subplots_adjust(bottom=config['FIGURE_BOTTOM_MARGIN'])

    # ---- 4 Save the figure -----------------------------------------------------------
    if config['SAVE_FIGURES']:
        width, height = config['FIGURE_SIZE']
        figure_saver(fig,
                     export_root / name,
                     name,
                     ('svg', 'png'),
                     config['FIGURE_SIZE'],
                     config['FIGURE_DPI'],
                     tight=config['TIGHT_BBOX'],
                     )
        print(f"    Figure saved at {width:g} x {height:g} in, {config['FIGURE_DPI']} "
              f'dpi '
              f"({round(width * config['FIGURE_DPI'])} x "
              f"{round(height * config['FIGURE_DPI'])} px): {export_root.name}/{name}/",
              )

    # ---- 5 Show the figure -----------------------------------------------------------
    if config['SHOW_INDIVIDUAL_FIGURES']:
        plt.show()
    else:
        plt.close(fig)
    return fig, axes


# ---- EXPERIMENT TITLE BUILDER --------------------------------------------------------
def experiment_title_builder(experiment: dict, config: dict) -> str:
    """
    ---- Summary ----
    Main function to build the title of an experiment from the FIGURE_TITLE format.

    ---- Inputs ----
    experiment : dict
        Experiment dictionary, as defined in DATA_FORMAT.md.
    config : dict
        Individual-experiment plot settings, as built by Config.plot_config in
        config.py.

    ---- Globals read ----
    config key FIGURE_TITLE ({experiment_name} is replaced).

    ---- Outputs ----
    str
        Title text.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return config['FIGURE_TITLE'].format(experiment_name=experiment['experiment_name'])


# ---- WATERMARK STYLE BUILDER ---------------------------------------------------------
def watermark_style_builder(config: dict) -> dict:
    """
    ---- Summary ----
    Main function to build the text keyword arguments of the faint run-name watermark.

    ---- Inputs ----
    config : dict
        Individual-experiment plot settings, as built by Config.plot_config in
        config.py.

    ---- Globals read ----
    config keys WATERMARK_FONT_SIZE, TICK_FONT_SIZE, WATERMARK_COLOUR and
    WATERMARK_ALPHA.

    ---- Outputs ----
    dict
        Keyword arguments fontsize, color and alpha for matplotlib text.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return {'fontsize': config.get('WATERMARK_FONT_SIZE', config['TICK_FONT_SIZE']),
            'color': config.get('WATERMARK_COLOUR', '0.35'),
            'alpha': config.get('WATERMARK_ALPHA', 0.5),
            }
