"""Publication figure (baseline OCR, OCR response, haem response), exemplars."""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from pathlib import Path
from typing import Any, Iterable, Optional

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.gridspec import SubplotSpec
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
from matplotlib.transforms import ScaledTranslation
import numpy as np
import pandas as pd
from scipy import stats as scipy_stats

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_custom.run_namer import condition_classifier, run_name_parser
from utils_shared.figure_layout import (figure_canvas_fitter,
                                        gap_space_calculator,
                                        panel_letter_adder,
                                        )
from utils_shared.helpers import (concentration_formatter,
                                  figure_saver,
                                  name_simplifier,
                                  )
from utils_shared.individual_experiment_plotter import (_HideTopTickLabels,
                                                        experiment_drawer,
                                                        experiment_title_builder,
                                                        watermark_style_builder,
                                                        )
from utils_shared.schema import (DELTA_HAEM_SOURCES,
                                 finite_float_converter,
                                 TIME_COLUMN,
                                 time_getter,
                                 )


# ---- CONSTANTS -----------------------------------------------------------------------
ORDER_TITLES = {'kcn_then_bd': 'KCN → BD', 'bd_then_kcn': 'BD → KCN'}
BLOCK_NAMES = ('baseline', 'ocr_response', 'haem_response')
RESPONSE_METRICS = ('delta', 'change', 'value')


# ---- PUBLICATION PLOTTER HELPERS -----------------------------------------------------


# ---- _AXES STYLER --------------------------------------------------------------------
def _axes_styler(ax: Axes,
                 config: dict,
                 tick_size: float,
                 pad: Optional[float] = None,
                 ) -> None:
    """
    ---- Summary ----
    Helper function to apply the tick, grid and spine style of the response and baseline
    panels.

    ---- Inputs ----
    ax : Axes
        Matplotlib axes to draw on.
    config : dict
        Figure settings dictionary built in custom_config.py.
    tick_size : float
        Tick label size in points.
    pad : Optional[float]
        Tick label pad in points, or None for the default.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Changes the style of ``ax`` (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    ax.tick_params(axis='both',
                   labelsize=tick_size,
                   direction='in',
                   **({} if pad is None else {'pad': pad}),
                   )
    ax.grid(False)
    ax.spines['top'].set_visible(config['AXES_TOP_SPINE'])
    ax.spines['right'].set_visible(config['AXES_RIGHT_SPINE'])


# ---- _BASELINE BAR PLOTTER -----------------------------------------------------------
def _baseline_bar_plotter(ax: Axes,
                          experiments: dict,
                          strains: tuple,
                          config: dict,
                          ) -> None:
    """
    ---- Summary ----
    Helper function to draw the baseline OCR (average0) bar chart per group, with every
    run overlaid and a Student t-test bracket between the two groups.

    ---- Inputs ----
    ax : Axes
        Matplotlib axes to draw on.
    experiments : dict
        Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.
    strains : tuple
        Group names (rows or bars), in drawing order.
    config : dict
        Figure settings dictionary built in custom_config.py.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Draws on ``ax`` (side effect).

    ---- Equations ----
    Bar height = mean of the run baselines; error bar = SEM = SD / sqrt(n). Student
    t-test with equal variances between the two groups.

    ---- Helpers ----
    _axes_styler
    _column_chooser
    _experiment_classifier
    _significance_bar_drawer
    _significance_formatter
    finite_float_converter
    """

    # ---- 1 Collect the baseline of each run ------------------------------------------
    values = {strain: [] for strain in strains}
    vo2_source = None
    for name, experiment in experiments.items():
        strain, _, _ = _experiment_classifier(name)
        averages = experiment.get('averages')
        if strain not in values or not averages:
            continue
        vo2_source = vo2_source or averages['settings']['vo2_source']
        baseline = averages['windows'].get('average0', {}).get('vo2', {})
        column = _column_chooser(baseline, config['OCR_VO2_COLUMN'])
        value = (finite_float_converter(baseline.get(column, {}).get('mean'))
                 if column
                 else np.nan
                 )
        if np.isfinite(value):
            values[strain].append(value)
        else:
            print(f'Warning: no baseline OCR for {name}; excluded from the baseline '
                  f'panel.',
                  )

    # ---- 2 Draw bars and points ------------------------------------------------------
    tick_size = config['RESPONSE_TICK_FONT_SIZE']
    x = np.arange(len(strains), dtype=float)
    means = [np.mean(values[s]) if values[s] else np.nan for s in strains]
    sems = [np.std(values[s], ddof=1) / np.sqrt(len(values[s]))
            if len(values[s]) >= 2
            else 0.0
            for s in strains
            ]
    width = config['BASELINE_BAR_WIDTH']
    ax.bar(x,
           means,
           width=width,
           color=[config['GROUP_STYLES'][s]['colour'] for s in strains],
           edgecolor='black',
           linewidth=config['THIN_LINE_WIDTH'],
           yerr=sems,
           capsize=config['RESPONSE_CAPSIZE'],
           error_kw={'elinewidth': config['RESPONSE_ERRORBAR_WIDTH'],
                     'capthick': config['RESPONSE_ERRORBAR_WIDTH'],
                     },
           zorder=2,
           )
    for xi, strain in zip(x, strains):
        if values[strain]:
            offsets = (np.linspace(-0.15, 0.15, len(values[strain])) * width / 0.62
                       if len(values[strain]) > 1
                       else np.array([0.0])
                       )
            ax.scatter(xi + offsets,
                       values[strain],
                       s=config['RESPONSE_POINT_SIZE'],
                       color='black',
                       edgecolor='white',
                       linewidth=0.5 * config['THIN_LINE_WIDTH'],
                       zorder=4,
                       )
        else:
            ax.text(xi,
                    0.5,
                    'No data',
                    transform=ax.get_xaxis_transform(),
                    ha='center',
                    va='center',
                    fontsize=tick_size,
                    )

    # ---- 3 Label the axes ------------------------------------------------------------
    ax.set_title('Baseline OCR (average0)')
    ax.set_ylabel(config['VO2_AXIS_LABELS'].get(vo2_source, 'VO2'),
                  fontsize=config['RESPONSE_YLABEL_FONT_SIZE'],
                  )
    ax.set_xticks(x)
    ax.set_xticklabels([s.capitalize() for s in strains])
    ax.set_xlim(-config['BASELINE_BAR_X_MARGIN'],
                len(strains) - 1 + config['BASELINE_BAR_X_MARGIN'],
                )
    if config['VO2_Y_MIN'] is not None:
        ax.set_ylim(bottom=config['VO2_Y_MIN'])
    tops = ([m + e for m, e in zip(means, sems) if np.isfinite(m)
             ] + [v for vs in values.values() for v in vs]
            )
    top = max(tops) if tops else 1.0

    # ---- 4 Significance bracket ------------------------------------------------------
    # Student's t-test (equal variances) between the two groups, shown as a bracket
    # above the data.
    test_text = None
    if config['BASELINE_TEST']:
        if len(strains) != 2:
            print(f'Warning: the baseline t-test needs exactly two groups in '
                  f'STRAIN_ROWS (got {len(strains)}); skipped.',
                  )
        elif min(len(values[s]) for s in strains) < 2:
            print('Warning: the baseline t-test needs at least two runs per group; '
                  'skipped.',
                  )
        else:
            result = scipy_stats.ttest_ind(values[strains[0]],
                                           values[strains[1]],
                                           equal_var=True,
                                           )
            test_text = _significance_formatter(result.pvalue,
                                                config['BASELINE_TEST_STYLE'],
                                                )
            n_text = ', '.join(f'{s} n={len(values[s])}' for s in strains)
            print(f"  Baseline OCR Student's t-test: t = {result.statistic:.3f}, df = "
                  f'{sum(len(values[s]) for s in strains) - 2}, '
                  f'p = {result.pvalue:.4g} ({n_text})',
                  )
    # Headroom for the bracket (the axis is finalised first so the bracket height is
    # relative to the final range).
    ax.set_ylim(top=top * (1.3 if test_text else 1.1))
    if test_text:
        _significance_bar_drawer(ax,
                                 x[0],
                                 x[1],
                                 top + 0.04 * ax.get_ylim()[1],
                                 test_text,
                                 tick_size,
                                 config,
                                 )
    _axes_styler(ax, config, tick_size)


# ---- _BLOCK GAP CALCULATOR -----------------------------------------------------------
def _block_gap_calculator(config: dict, n_blocks: int, n_columns: int) -> tuple:
    """
    ---- Summary ----
    Helper function to calculate the gap between the blocks and between the response
    columns of the publication figure.

    ---- Inputs ----
    config : dict
        Figure settings dictionary built in custom_config.py.
    n_blocks : int
        Number of blocks stacked vertically.
    n_columns : int
        Number of addition-order columns.

    ---- Globals read ----
    None.

    ---- Outputs ----
    tuple
        (hspace, wspace) as GridSpec fractions.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    block_gap = 2.4 xtick + 0.5 unit + 1.2 title + 0.8 unit + 1.0 unit; column_gap = 5 x
    0.55 tick + 0.5 unit + 1.5 unit (points). gap_to_space converts a gap in points to a
    GridSpec fraction.

    ---- Helpers ----
    gap_space_calculator
    """

    # ---- 1 Read the configuration ----------------------------------------------------
    unit = config['UNIT_PT']
    width_pt, height_pt = (v * 72.0 for v in config['FIGURE_SIZE'])
    tick, xtick, title = (config['RESPONSE_TICK_FONT_SIZE'],
                          config['RESPONSE_XTICK_FONT_SIZE'],
                          config['TITLE_FONT_SIZE'],
                          )

    # ---- 2 Calculate the gaps --------------------------------------------------------
    block_gap = 2.4 * xtick + 0.5 * unit + 1.2 * title + 0.8 * unit + 1.0 * unit
    column_gap = 5 * 0.55 * tick + 0.5 * unit + 1.5 * unit
    return (gap_space_calculator(block_gap, height_pt - 6 * unit, n_blocks),
            gap_space_calculator(column_gap, width_pt - 8 * unit, n_columns),
            )


# ---- _COLUMN CHOOSER -----------------------------------------------------------------
def _column_chooser(available: Iterable, preferred: Optional[str]) -> Optional[str]:
    """
    ---- Summary ----
    Helper function to choose the OCR column: the preferred one if set, else VoO2, else
    the first available.

    ---- Inputs ----
    available : Iterable
        Column names that are available.
    preferred : Optional[str]
        Column requested in the settings, or None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[str]
        Chosen column name, or None if none is available.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    available = list(available)
    if preferred is not None:
        return preferred if preferred in available else None
    if 'VoO2' in available:
        return 'VoO2'
    return available[0] if available else None


# ---- _CONDITION INDEXER --------------------------------------------------------------
def _condition_indexer(triplicates: dict) -> dict:
    """
    ---- Summary ----
    Helper function to map each (strain, order) pair to its condition name in the
    triplicate results.

    ---- Inputs ----
    triplicates : dict
        Across-run statistics per condition, from triplicate_averager (DATA_FORMAT.md).

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        {(strain, order): condition name}. Raises ValueError if two conditions match one
        pair.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    condition_classifier
    """

    lookup = {}
    for condition in triplicates:
        strain, order = condition_classifier(condition)
        if strain and order:
            if (strain, order) in lookup:
                raise ValueError(f'More than one condition matches {(strain, order)}: '
                                 f'{lookup[(strain, order)]!r} and {condition!r}',
                                 )
            lookup[(strain, order)] = condition
    return lookup


# ---- _CROP START FINDER --------------------------------------------------------------
def _crop_start_finder(experiment: dict,
                       mode: str,
                       before_minutes: float,
                       margin_minutes: float,
                       ) -> float:
    """
    ---- Summary ----
    Helper function to find the time at which an exemplar crop begins.

    ---- Inputs ----
    experiment : dict
        Experiment dictionary, as defined in DATA_FORMAT.md.
    mode : str
        'baseline' (start of the average0 window) or 'first_addition'.
    before_minutes : float
        Minutes kept before the first addition.
    margin_minutes : float
        Extra minutes kept before the baseline window.

    ---- Globals read ----
    None.

    ---- Outputs ----
    float
        Crop start time in minutes.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 Find the start from the baseline ------------------------------------------
    if mode == 'baseline':
        baseline = experiment.get('averages', {}).get('windows', {}).get('average0')
        if not baseline:
            raise ValueError(f"{experiment['experiment_name']}: no baseline averaging "
                             f'window (average0), so the exemplar cannot '
                             'start at the baseline. Calculate the averages first, or '
                             'set CROP_START to "first_addition".',
                             )
        return baseline['start_time'] - margin_minutes

    # ---- 2 Find the start from the first addition ------------------------------------
    if mode == 'first_addition':
        events = experiment.get('metadata', {}).get('events', [])
        if not events:
            raise ValueError(f"{experiment['experiment_name']}: no events, so the data"
                             f' cannot be cropped to the first addition.',
                             )
        return min(event['time'] for event in events) - before_minutes

    # ---- 3 Reject unknown modes ------------------------------------------------------
    raise ValueError(f'CROP_START must be "baseline", "first_addition" or None; '
                     f'received {mode!r}.',
                     )


# ---- _EXEMPLAR GAP CALCULATOR --------------------------------------------------------
def _exemplar_gap_calculator(config: dict,
                             individual_config: dict,
                             n_rows: int,
                             n_columns: int,
                             ) -> tuple:
    """
    ---- Summary ----
    Helper function to calculate the gap between rows and between columns of the
    exemplar quadrants.

    ---- Inputs ----
    config : dict
        Figure settings dictionary built in custom_config.py.
    individual_config : dict
        Individual-experiment plot settings, as returned by Config.plot_config in
        config.py.
    n_rows : int
        Number of group rows.
    n_columns : int
        Number of addition-order columns.

    ---- Globals read ----
    None.

    ---- Outputs ----
    tuple
        (hspace, wspace) as GridSpec fractions.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    row_gap = 1.2 tick + 0.5 unit + label pad + 1.2 label + 1.0 unit; column_gap = lines
    x 1.2 label + y label pad + 5 x 0.55 tick + 0.5 unit + 1.5 unit (points).

    ---- Helpers ----
    gap_space_calculator
    """

    # ---- 1 Read the configuration ----------------------------------------------------
    c, unit = individual_config, config['UNIT_PT']
    width_pt, height_pt = (v * 72.0 for v in config['FIGURE_SIZE'])
    tick, label = c['TICK_FONT_SIZE'], c.get('LABEL_FONT_SIZE', c['TICK_FONT_SIZE'] + 1)

    # ---- 2 Measure the axis labels ---------------------------------------------------
    labels = [c['O2_AXIS_LABEL'],
              c['VO2_AXIS_LABELS'][c['VO2_PLOT_VALUES']],
              c['HAEM_AXIS_LABELS'].get(c['HAEM_PLOT_VALUES'], ''),
              ]
    lines = max(str(text).count('\n') + 1 for text in labels)

    # ---- 3 Calculate the gaps --------------------------------------------------------
    # tick labels, time-axis label, clearance
    row_gap = (1.2 * tick +
               0.5 * unit +
               c['TIME_AXIS_LABEL_PAD'] +
               1.2 * label +
               1.0 * unit
               )
    column_gap = (lines * 1.2 * label +
                  c['Y_LABEL_PAD'] +
                  5 * 0.55 * tick +
                  0.5 * unit +
                  1.5 * unit
                  )
    return (gap_space_calculator(row_gap, height_pt - 6 * unit, n_rows),
            gap_space_calculator(column_gap, width_pt - 8 * unit, n_columns),
            )


# ---- _EXEMPLAR PLOTTER ---------------------------------------------------------------
def _exemplar_plotter(fig: Figure,
                      subplot_spec: SubplotSpec,
                      experiment: dict,
                      individual_config: dict,
                      ) -> list:
    """
    ---- Summary ----
    Helper function to draw one experiment exactly as the individual plotter does.

    ---- Inputs ----
    fig : Figure
        Matplotlib figure.
    subplot_spec : SubplotSpec
        Grid cell the experiment is drawn in.
    experiment : dict
        Experiment dictionary, as defined in DATA_FORMAT.md.
    individual_config : dict
        Individual-experiment plot settings, as returned by Config.plot_config in
        config.py.

    ---- Globals read ----
    None.

    ---- Outputs ----
    list
        Axes of the stacked panels.

    ---- Globals mutated ----
    None. Adds axes to ``fig`` (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    experiment_drawer
    """

    axes, _ = experiment_drawer(fig, subplot_spec, experiment, individual_config)
    return axes


# ---- _EXEMPLAR SELECTOR --------------------------------------------------------------
def _exemplar_selector(experiments: dict, run: int) -> dict:
    """
    ---- Summary ----
    Helper function to pick the experiment of one run number for every (strain, order)
    cell.

    ---- Inputs ----
    experiments : dict
        Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.
    run : int
        Run number shown for each condition.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        {(strain, order): experiment}. Raises ValueError if two experiments match one
        cell.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _experiment_classifier
    """

    # ---- 1 Prepare the lookup --------------------------------------------------------
    lookup = {}

    # ---- 2 Index the experiments -----------------------------------------------------
    for name, experiment in experiments.items():
        strain, order, experiment_run = _experiment_classifier(name)
        if strain and order and experiment_run == run:
            if (strain, order) in lookup:
                raise ValueError(f'More than one run{run} experiment matches '
                                 f'{(strain, order)}: '
                                 f"{lookup[(strain, order)]['experiment_name']!r} and "
                                 f'{name!r}',
                                 )
            lookup[(strain, order)] = experiment
    return lookup


# ---- _EXPERIMENT CLASSIFIER ----------------------------------------------------------
def _experiment_classifier(name: str) -> tuple:
    """
    ---- Summary ----
    Helper function to identify the strain, addition order and run number from an
    experiment name.

    ---- Inputs ----
    name : str
        Experiment name such as 'control_kcn_then_bd_run1'.

    ---- Globals read ----
    None.

    ---- Outputs ----
    tuple
        (strain, order, run); entries are None where they cannot be identified.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    condition_classifier
    run_name_parser
    """

    parsed = run_name_parser(name)
    if parsed is None:
        return None, None, None
    condition, run = parsed
    strain, order = condition_classifier(condition)
    return strain, order, run


# ---- _EXPERIMENT CROPPER -------------------------------------------------------------
def _experiment_cropper(experiment: dict, start: float) -> tuple:
    """
    ---- Summary ----
    Helper function to copy an experiment cropped to begin at a chosen time, with time
    measured from there.

    ---- Inputs ----
    experiment : dict
        Experiment dictionary, as defined in DATA_FORMAT.md.
    start : float
        Time in minutes at which the crop begins.

    ---- Globals read ----
    None.

    ---- Outputs ----
    tuple
        (cropped experiment copy, last time in minutes).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    t_new = t - start; rows with t_new < 0 are dropped.

    ---- Helpers ----
    time_getter
    """

    # ---- 1 Read the experiment -------------------------------------------------------
    events = experiment.get('metadata', {}).get('events', [])
    origin = start
    cropped = dict(experiment)
    last_time = -np.inf

    # ---- 2 Shift and crop each series ------------------------------------------------
    for key, value in experiment.items():
        if isinstance(value, pd.DataFrame) and TIME_COLUMN in value.columns:
            shifted = time_getter(value) - origin
            keep = shifted >= -1e-9
            frame = value.loc[keep].copy()
            frame[TIME_COLUMN] = shifted[keep]
            cropped[key] = frame
            if keep.any():
                last_time = max(last_time, float(np.nanmax(shifted[keep])))

    # ---- 3 Update the metadata -------------------------------------------------------
    cropped['metadata'] = {**experiment['metadata'],
                           'events': [{**event, 'time': event['time'] - origin}
                                      for event in events
                                      ],
                           }

    # ---- 4 Update the averages -------------------------------------------------------
    if experiment.get('averages'):
        windows = {name: {**window,
                          'start_time': window['start_time'] - origin,
                          'end_time': window['end_time'] - origin,
                          }
                   for name, window in experiment['averages']['windows'].items()
                   }
        cropped['averages'] = {**experiment['averages'], 'windows': windows}
    return cropped, last_time


# ---- _FIGURE FINISHER ----------------------------------------------------------------
def _figure_finisher(fig: Figure,
                     config: dict,
                     panels: list,
                     suptitle: Any,
                     fit_to_corner: bool = False,
                     ) -> None:
    """
    ---- Summary ----
    Helper function to fit the margins to the drawn content, add the panel letters at
    the top-left of each panel and fit again.

    ---- Inputs ----
    fig : Figure
        Matplotlib figure.
    config : dict
        Figure settings dictionary built in custom_config.py.
    panels : list
        List of (letter, main axes, [axes of the panel]) tuples.
    suptitle : Any
        Figure title text object, or None.
    fit_to_corner : bool
        False puts each letter above everything its panel draws; True puts it just above
        whatever lies in its own corner.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Resizes the layout of ``fig`` and adds text to it (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    figure_canvas_fitter
    panel_letter_adder
    """

    pad, gap = config['EDGE_PAD_PT'], config['TITLE_GAP_PT']
    figure_canvas_fitter(fig, pad, suptitle, gap)
    if config['PANEL_LETTERS'] and panels:
        panel_letter_adder(fig,
                           panels,
                           config['PANEL_LETTER_FONT_SIZE'],
                           config['PANEL_LETTER_CASE'],
                           fit_to_corner=fit_to_corner,
                           )
        figure_canvas_fitter(fig, pad, suptitle, gap)


# ---- _HAEM BLOCK PLOTTER -------------------------------------------------------------
def _haem_block_plotter(fig: Figure,
                        spec: SubplotSpec,
                        orders: tuple,
                        strains: tuple,
                        triplicates: dict,
                        conditions: dict,
                        references: dict,
                        config: dict,
                        rows: list,
                        haem_source: str,
                        tests: Optional[list] = None,
                        ) -> tuple:
    """
    ---- Summary ----
    Helper function to draw the haem response: one row per haem, one column per addition
    order, a line per group.

    ---- Inputs ----
    fig : Figure
        Matplotlib figure.
    spec : SubplotSpec
        Grid cell the block is drawn in.
    orders : tuple
        Addition-order names (columns), in drawing order.
    strains : tuple
        Group names (rows or bars), in drawing order.
    triplicates : dict
        Across-run statistics per condition, from triplicate_averager (DATA_FORMAT.md).
    conditions : dict
        Lookup {(strain, order): condition name}.
    references : dict
        Lookup {order: experiment or None} used for the event tick labels.
    config : dict
        Figure settings dictionary built in custom_config.py.
    rows : list
        Haem row dictionaries {haem, label}.
    haem_source : str
        Haem source key, for example 'delta_abs_od'.
    tests : Optional[list]
        List collecting t-test comparisons, or None to skip the tests.

    ---- Globals read ----
    None.

    ---- Outputs ----
    tuple
        (grid of axes [row][column], invisible axes carrying the shared y label).

    ---- Globals mutated ----
    None. Adds axes to ``fig`` and appends to ``tests`` (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _haem_label_finder
    _haem_label_pad_calculator
    _legend_handle_builder
    _measurement_finder
    _reference_level_finder
    _response_axes_preparer
    _response_series_drawer
    _response_window_tester
    _row_ylim_sharer
    _tick_label_builder
    _window_orderer
    """

    # ---- 1 Create the axes -----------------------------------------------------------
    metric = config['HAEM_RESPONSE_METRIC']
    baseline_level = _reference_level_finder(metric, haem_source)
    grid_axes = [[fig.add_subplot(spec[r, c]) for c in range(len(orders))]
                 for r in range(len(rows))
                 ]

    # ---- 2 Shared y label ------------------------------------------------------------
    # One shared y-label spanning every row (an invisible axes covering them keeps it
    # aligned under layout changes).
    span = fig.add_subplot(spec[:, 0], frameon=False)
    span.set_xticks([])
    span.set_yticks([])
    span.set_ylabel(_haem_label_finder(config, metric, haem_source),
                    fontsize=config['RESPONSE_YLABEL_FONT_SIZE'],
                    labelpad=_haem_label_pad_calculator(config),
                    )

    # ---- 3 Draw every row ------------------------------------------------------------
    for r, row in enumerate(rows):
        last_row = r == len(rows) - 1
        for c, order in enumerate(orders):
            ax = grid_axes[r][c]
            windows = _window_orderer(order, strains, triplicates, conditions)
            if r == 0:
                ax.set_title(f'Haem response: {ORDER_TITLES[order]}')
            if not windows:
                ax.text(0.5,
                        0.5,
                        'No averaging data available',
                        transform=ax.transAxes,
                        ha='center',
                        va='center',
                        )
                continue
            x = _response_axes_preparer(ax,
                                        windows,
                                        _tick_label_builder(references[order], windows),
                                        last_row,
                                        config,
                                        baseline_level,
                                        )
            if c == 0:
                ax.set_ylabel(row['label'],
                              fontsize=config['RESPONSE_YLABEL_FONT_SIZE'],
                              )
            drawn = False
            series = {}
            for k, strain in enumerate(strains):
                condition = conditions.get((strain, order))
                if condition is None:
                    continue
                measurements = triplicates[condition]['haem']
                column = _measurement_finder(measurements, row['haem'])
                if column is None:
                    continue
                series[strain] = [measurements[column].get(w) for w in windows]
                dodge = (k - (len(strains) - 1) / 2) * config['RESPONSE_GROUP_DODGE']
                drawn |= _response_series_drawer(ax,
                                                 x,
                                                 series[strain],
                                                 config['GROUP_STYLES'][strain],
                                                 config,
                                                 metric=metric,
                                                 offset=dodge,
                                                 )
            _mean_ylim_setter(ax, list(series.values()), metric, baseline_level)
            if tests is not None:
                _response_window_tester(ax,
                                        x,
                                        windows,
                                        series,
                                        strains,
                                        metric,
                                        config,
                                        f"Haem response {row['label']}: "
                                        f'{ORDER_TITLES[order]}',
                                        tests,
                                        )
            if not drawn:
                print(f"Warning: no data for haem {row['haem']!r} ("
                      f'{ORDER_TITLES[order]}).',
                      )
                ax.text(0.5,
                        0.5,
                        f"No {row['haem']} data",
                        transform=ax.transAxes,
                        ha='center',
                        va='center',
                        )
        if config['SHARE_Y_BETWEEN_ORDERS'] and len(orders) > 1:
            _row_ylim_sharer(grid_axes[r])
        if r > 0:
            for ax in grid_axes[r]:
                hider = _HideTopTickLabels(config['RESPONSE_TICK_FONT_SIZE'])
                ax.yaxis.set_major_formatter(hider)
    grid_axes[0][0].legend(handles=_legend_handle_builder(strains, config),
                           loc=config['RESPONSE_LEGEND_LOCATION'],
                           fontsize=config['RESPONSE_LEGEND_FONT_SIZE'],
                           frameon=False,
                           )
    return grid_axes, span


# ---- _HAEM LABEL FINDER --------------------------------------------------------------
def _haem_label_finder(config: dict, metric: str, haem_source: str) -> str:
    """
    ---- Summary ----
    Helper function to find the shared y label of the haem response rows.

    ---- Inputs ----
    config : dict
        Figure settings dictionary built in custom_config.py.
    metric : str
        Response metric: 'delta', 'change' or 'value'.
    haem_source : str
        Haem source key, for example 'delta_abs_od'.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        Label text from HAEM_RESPONSE_AXIS_LABELS for the metric and source.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    labels = config['HAEM_RESPONSE_AXIS_LABELS'][metric]
    if isinstance(labels, dict):
        label = labels.get(haem_source, labels.get('default'))
        if label is None:
            raise ValueError(f'HAEM_RESPONSE_AXIS_LABELS["{metric}"] has no entry for '
                             f'the haem source "{haem_source}" '
                             f'(or a "default" entry).',
                             )
        return label
    return labels


# ---- _HAEM LABEL PAD CALCULATOR ------------------------------------------------------
def _haem_label_pad_calculator(config: dict) -> float:
    """
    ---- Summary ----
    Helper function to calculate the points between the shared haem label and the haem
    axes.

    ---- Inputs ----
    config : dict
        Figure settings dictionary built in custom_config.py.

    ---- Globals read ----
    None.

    ---- Outputs ----
    float
        Label pad in points.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    pad = 1.2 label font + 0.5 unit + 5 x 0.55 tick font + 0.5 unit (points).

    ---- Helpers ----
    None.
    """

    unit = config['UNIT_PT']
    return (1.2 * config['RESPONSE_YLABEL_FONT_SIZE'] +
            0.5 * unit +
            5 * 0.55 * config['RESPONSE_TICK_FONT_SIZE'] +
            0.5 * unit
            )


# ---- _HAEM ROW SELECTOR --------------------------------------------------------------
def _haem_row_selector(config: dict) -> list:
    """
    ---- Summary ----
    Helper function to select the haem response rows to draw, in the order listed in
    HAEM_RESPONSE_SHOW.

    ---- Inputs ----
    config : dict
        Figure settings dictionary built in custom_config.py.

    ---- Globals read ----
    None.

    ---- Outputs ----
    list
        Row dictionaries {haem, label}. Every row is returned when HAEM_RESPONSE_SHOW is
        empty. Entries are matched to a row label or haem name ignoring case and
        punctuation.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    name_simplifier
    """

    # ---- 1 Read the configured rows --------------------------------------------------
    rows = list(config['HAEM_RESPONSE_ROWS'])
    wanted = config['HAEM_RESPONSE_SHOW']
    if not wanted:
        return rows

    # ---- 2 Select the requested rows -------------------------------------------------
    selected = []
    for entry in wanted:
        key = name_simplifier(entry)
        match = next((r
                      for r in rows
                      if key in (name_simplifier(r['label']),
                                 name_simplifier(r['haem']),
                                 )
                      ),
                     None,
                     )
        if match is None:
            options = ', '.join(f"{r['label']!r}" for r in rows)
            raise ValueError(f'HAEM_RESPONSE_SHOW entry {entry!r} matches no '
                             f'HAEM_RESPONSE_ROWS entry (labels: {options}).',
                             )
        if match not in selected:
            selected.append(match)
    return selected


# ---- _HAEM SOURCE FINDER -------------------------------------------------------------
def _haem_source_finder(triplicates: dict) -> str:
    """
    ---- Summary ----
    Helper function to find the haem source that every condition's averages were
    calculated from.

    ---- Inputs ----
    triplicates : dict
        Across-run statistics per condition, from triplicate_averager (DATA_FORMAT.md).

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        Haem source key, for example 'delta_abs_od'. Raises ValueError if the conditions
        differ.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    sources = {result['settings'].get('haem_source') for result in triplicates.values()}
    sources.discard(None)
    if len(sources) != 1:
        raise ValueError(f'The haem response needs every condition averaged from one '
                         f'haem source; found {sorted(sources)}.',
                         )
    return sources.pop()


# ---- _LAYOUT VALIDATOR ---------------------------------------------------------------
def _layout_validator(config: dict) -> tuple:
    """
    ---- Summary ----
    Helper function to check that the layout options of the publication figure are
    recognised and to return the group and order lists.

    ---- Inputs ----
    config : dict
        Figure settings dictionary built in custom_config.py.

    ---- Globals read ----
    ORDER_TITLES, BLOCK_NAMES, RESPONSE_METRICS (module constants).

    ---- Outputs ----
    tuple
        (orders, strains): addition orders (columns) and groups (rows), as tuples.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 Check the orders and strains ----------------------------------------------
    orders, strains = tuple(config['ORDER_COLUMNS']), tuple(config['STRAIN_ROWS'])
    unknown_orders = [o for o in orders if o not in ORDER_TITLES]
    unknown_strains = [s for s in strains if s not in config['GROUP_STYLES']]
    if unknown_orders:
        raise ValueError(f'ORDER_COLUMNS has unknown entries {unknown_orders}; use '
                         f'{list(ORDER_TITLES)}.',
                         )
    if unknown_strains:
        raise ValueError(f'STRAIN_ROWS has entries with no GROUP_STYLES: '
                         f'{unknown_strains}.',
                         )
    if not orders or not strains:
        raise ValueError('ORDER_COLUMNS and STRAIN_ROWS must each contain at least one'
                         ' entry.',
                         )

    # ---- 2 Check the response settings -----------------------------------------------
    if not config['HAEM_RESPONSE_ROWS']:
        raise ValueError('HAEM_RESPONSE_ROWS must contain at least one haem.')
    if config['HAEM_RESPONSE_METRIC'] not in RESPONSE_METRICS:
        raise ValueError(f'HAEM_RESPONSE_METRIC must be one of '
                         f'{list(RESPONSE_METRICS)}; got '
                         f"{config['HAEM_RESPONSE_METRIC']!r}.",
                         )
    if config['PANEL_LETTER_CASE'] not in ('upper', 'lower'):
        raise ValueError('PANEL_LETTER_CASE must be "upper" or "lower".')

    # ---- 3 Check the blocks ----------------------------------------------------------
    blocks = list(config['BLOCK_ORDER'])
    unknown_blocks = [b for b in blocks if b not in BLOCK_NAMES]
    if unknown_blocks or len(set(blocks)) != len(blocks) or not blocks:
        raise ValueError(f'BLOCK_ORDER must list each of {list(BLOCK_NAMES)} at most '
                         f'once (and not be empty); got {blocks}.',
                         )
    missing = [b for b in blocks if b not in config['HEIGHT_RATIOS']]
    if missing:
        raise ValueError(f'HEIGHT_RATIOS is missing {missing}.')
    return orders, strains


# ---- _LEGEND HANDLE BUILDER ----------------------------------------------------------
def _legend_handle_builder(strains: tuple, config: dict) -> list:
    """
    ---- Summary ----
    Helper function to build legend entries showing each group's colour, line style and
    marker.

    ---- Inputs ----
    strains : tuple
        Group names (rows or bars), in drawing order.
    config : dict
        Figure settings dictionary built in custom_config.py.

    ---- Globals read ----
    None.

    ---- Outputs ----
    list
        Line2D handles, one per group.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return [Line2D([0],
                   [0],
                   color=config['GROUP_STYLES'][s]['colour'],
                   linestyle=config['GROUP_STYLES'][s]['linestyle'],
                   marker=config['GROUP_STYLES'][s]['marker'],
                   markersize=config['RESPONSE_MARKER_SIZE'],
                   linewidth=config['RESPONSE_LINE_WIDTH'],
                   label=s.capitalize(),
                   )
            for s in strains
            ]


# ---- _MEAN YLIM SETTER ---------------------------------------------------------------
def _mean_ylim_setter(ax: Axes,
                      series_list: list,
                      metric: str,
                      baseline_level: Optional[float] = None,
                      margin: float = 0.12,
                      ) -> None:
    """
    ---- Summary ----
    Helper function to set the y range of a response panel from the group means (and
    the baseline level) only, so that a single outlier run or a very large error bar
    does not stretch the axis. Points and error bars beyond the range are clipped.

    ---- Inputs ----
    ax : Axes
        Response panel, with the series already drawn.
    series_list : list
        One list of window statistics per strain, as drawn by _response_series_drawer.
    metric : str
        Response metric, which decides the field holding the mean.
    baseline_level : Optional[float]
        Reference level that must stay in view (for example 100 for % of baseline).
    margin : float
        Fraction of the mean range added above and below.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None.

    ---- Globals mutated ----
    None. Sets the y limits of ``ax`` (side effect); does nothing when no mean is
    finite.

    ---- Equations ----
    low = min(means) - margin x range; high = max(means) + margin x range, where the
    range is max(means) - min(means) (at least 1 % of the largest absolute mean).

    ---- Helpers ----
    _metric_field_selector
    """

    # ---- 1 Collect the means ---------------------------------------------------------
    mean_key = _metric_field_selector(metric)[0]
    values = [s[mean_key] for series in series_list for s in series if s]
    if baseline_level is not None:
        values.append(baseline_level)
    values = np.array(values, dtype=float)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return

    # ---- 2 Set the limits ------------------------------------------------------------
    low, high = float(values.min()), float(values.max())
    span = max(high - low, 0.01 * max(abs(low), abs(high), 1e-12))
    ax.set_ylim(low - margin * span, high + margin * span)


# ---- _MEASUREMENT FINDER -------------------------------------------------------------
def _measurement_finder(available: Iterable, wanted: str) -> Optional[str]:
    """
    ---- Summary ----
    Helper function to find the column matching a wanted name, ignoring case and
    punctuation.

    ---- Inputs ----
    available : Iterable
        Column names that are available.
    wanted : str
        Name to look for.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[str]
        Matching column name, or None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    name_simplifier
    """

    target = name_simplifier(wanted)
    for column in available:
        if name_simplifier(column) == target:
            return column
    return None


# ---- _METRIC FIELD SELECTOR ----------------------------------------------------------
def _metric_field_selector(metric: str) -> tuple:
    """
    ---- Summary ----
    Helper function to name the keys of the triplicate statistics used by a response
    metric.

    ---- Inputs ----
    metric : str
        Response metric: 'delta', 'change' or 'value'.

    ---- Globals read ----
    None.

    ---- Outputs ----
    tuple
        (mean key, sem key, n key, per-run values key).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if metric == 'value':
        return 'mean', 'sem', 'n', 'run_means'
    return f'{metric}_mean', f'{metric}_sem', f'{metric}_n', f'run_{metric}s'


# ---- _OCR BLOCK PLOTTER --------------------------------------------------------------
def _ocr_block_plotter(fig: Figure,
                       spec: SubplotSpec,
                       orders: tuple,
                       strains: tuple,
                       triplicates: dict,
                       conditions: dict,
                       references: dict,
                       config: dict,
                       tests: Optional[list] = None,
                       ) -> list:
    """
    ---- Summary ----
    Helper function to draw the OCR response (percent of each run's baseline, mean and
    SEM across runs), one axes per addition order.

    ---- Inputs ----
    fig : Figure
        Matplotlib figure.
    spec : SubplotSpec
        Grid cell the block is drawn in.
    orders : tuple
        Addition-order names (columns), in drawing order.
    strains : tuple
        Group names (rows or bars), in drawing order.
    triplicates : dict
        Across-run statistics per condition, from triplicate_averager (DATA_FORMAT.md).
    conditions : dict
        Lookup {(strain, order): condition name}.
    references : dict
        Lookup {order: experiment or None} used for the event tick labels.
    config : dict
        Figure settings dictionary built in custom_config.py.
    tests : Optional[list]
        List collecting t-test comparisons, or None to skip the tests.

    ---- Globals read ----
    None.

    ---- Outputs ----
    list
        The axes, one per addition order.

    ---- Globals mutated ----
    None. Adds axes to ``fig`` and appends to ``tests`` (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _column_chooser
    _legend_handle_builder
    _response_axes_preparer
    _response_series_drawer
    _response_window_tester
    _row_ylim_sharer
    _tick_label_builder
    _window_orderer
    """

    # ---- 1 Create the axes -----------------------------------------------------------
    axes = [fig.add_subplot(spec[0, col]) for col in range(len(orders))]

    # ---- 2 Plot each order -----------------------------------------------------------
    for col, (ax, order) in enumerate(zip(axes, orders)):
        ax.set_title(f'OCR response: {ORDER_TITLES[order]}')

        # ---- 2.1 Order the windows ---------------------------------------------------
        windows = _window_orderer(order, strains, triplicates, conditions)
        if not windows:
            ax.text(0.5,
                    0.5,
                    'No averaging data available',
                    transform=ax.transAxes,
                    ha='center',
                    va='center',
                    )
            continue

        # ---- 2.2 Prepare the axes ----------------------------------------------------
        x = _response_axes_preparer(ax,
                                    windows,
                                    _tick_label_builder(references[order], windows),
                                    True,
                                    config,
                                    )
        if col == 0:
            ax.set_ylabel(config['OCR_RESPONSE_AXIS_LABEL'],
                          fontsize=config['RESPONSE_YLABEL_FONT_SIZE'],
                          )

        # ---- 2.3 Draw each strain ----------------------------------------------------
        series = {}
        for k, strain in enumerate(strains):
            condition = conditions.get((strain, order))
            if condition is None:
                continue
            measurements = triplicates[condition]['vo2']
            column = _column_chooser(measurements, config['OCR_VO2_COLUMN'])
            if column is None:
                print(f'Warning: OCR column unavailable for {condition}; not plotted.')
                continue
            series[strain] = [measurements[column].get(w) for w in windows]
            dodge = (k - (len(strains) - 1) / 2) * config['RESPONSE_GROUP_DODGE']
            _response_series_drawer(ax,
                                    x,
                                    series[strain],
                                    config['GROUP_STYLES'][strain],
                                    config,
                                    offset=dodge,
                                    )

        # ---- 2.4 Add the significance tests ------------------------------------------
        _mean_ylim_setter(ax, list(series.values()), 'change', 100)
        if tests is not None:
            _response_window_tester(ax,
                                    x,
                                    windows,
                                    series,
                                    strains,
                                    'change',
                                    config,
                                    f'OCR response: {ORDER_TITLES[order]}',
                                    tests,
                                    )

    # ---- 3 Share the axis limits -----------------------------------------------------
    if config['SHARE_Y_BETWEEN_ORDERS'] and len(axes) > 1:
        _row_ylim_sharer(axes)

    # ---- 4 Add the legend ------------------------------------------------------------
    axes[0].legend(handles=_legend_handle_builder(strains, config),
                   loc=config['RESPONSE_LEGEND_LOCATION'],
                   fontsize=config['RESPONSE_LEGEND_FONT_SIZE'],
                   frameon=False,
                   )
    return axes


# ---- _P VALUE ADJUSTER ---------------------------------------------------------------
def _p_value_adjuster(p_values: Iterable, method: str) -> np.ndarray:
    """
    ---- Summary ----
    Helper function to adjust a list of p values for multiple comparisons.

    ---- Inputs ----
    p_values : Iterable
        Raw p values.
    method : str
        'none', 'bonferroni' or 'holm'.

    ---- Globals read ----
    None.

    ---- Outputs ----
    np.ndarray
        Adjusted p values, same order as the input.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Bonferroni: p_adj = min(n p, 1). Holm: sort ascending, p_adj(i) = min(max over j <=
    i of (n - j) p(j), 1) with j counted from 0.

    ---- Helpers ----
    None.
    """

    # ---- 1 Read the p values ---------------------------------------------------------
    p = np.asarray(p_values, dtype=float)
    n = p.size

    # ---- 2 Apply the correction ------------------------------------------------------
    if method == 'none' or n == 0:
        return p.copy()
    if method == 'bonferroni':
        return np.minimum(p * n, 1.0)
    if method == 'holm':
        adjusted, running = np.empty(n), 0.0
        for rank, index in enumerate(np.argsort(p)):
            running = max(running, (n - rank) * p[index])
            adjusted[index] = min(running, 1.0)
        return adjusted
    raise ValueError(f'RESPONSE_TEST_CORRECTION must be "none", "holm" or '
                     f'"bonferroni"; received {method!r}.',
                     )


# ---- _REFERENCE LEVEL FINDER ---------------------------------------------------------
def _reference_level_finder(metric: str, haem_source: str) -> Optional[float]:
    """
    ---- Summary ----
    Helper function to find the height of the dashed reference line of the haem
    response.

    ---- Inputs ----
    metric : str
        Response metric: 'delta', 'change' or 'value'.
    haem_source : str
        Haem source key, for example 'delta_abs_od'.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[float]
        0 for a change, 100 for percent of baseline, 0 for a delta abs value, otherwise
        None.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if metric == 'delta':
        return 0
    if metric == 'change':
        return 100
    return 0 if haem_source in DELTA_HAEM_SOURCES else None


# ---- _REFERENCE SELECTOR -------------------------------------------------------------
def _reference_selector(experiments: dict,
                        triplicates: dict,
                        conditions: dict,
                        orders: tuple,
                        strains: tuple,
                        ) -> dict:
    """
    ---- Summary ----
    Helper function to pick, for each addition order, the first run of the first
    available group (used for the event tick labels).

    ---- Inputs ----
    experiments : dict
        Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.
    triplicates : dict
        Across-run statistics per condition, from triplicate_averager (DATA_FORMAT.md).
    conditions : dict
        Lookup {(strain, order): condition name}.
    orders : tuple
        Addition-order names (columns), in drawing order.
    strains : tuple
        Group names (rows or bars), in drawing order.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        {order: experiment or None}.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 Prepare the references ----------------------------------------------------
    references = {}

    # ---- 2 Select a reference for each order -----------------------------------------
    for order in orders:
        references[order] = None
        for strain in strains:
            condition = conditions.get((strain, order))
            if condition:
                first_run = triplicates[condition]['run_numbers'][0]
                run_name = triplicates[condition]['runs'][first_run]
                references[order] = experiments[run_name]
                break
    return references


# ---- _RESPONSE AXES PREPARER ---------------------------------------------------------
def _response_axes_preparer(ax: Axes,
                            window_names: list,
                            tick_labels: list,
                            show_xlabels: bool,
                            config: dict,
                            baseline_level: Optional[float] = 100,
                            ) -> np.ndarray:
    """
    ---- Summary ----
    Helper function to draw the baseline reference line and set the window ticks of a
    response panel.

    ---- Inputs ----
    ax : Axes
        Matplotlib axes to draw on.
    window_names : list
        Averaging window names, for example ['average0', 'average1'].
    tick_labels : list
        Tick label of every window.
    show_xlabels : bool
        True to write the tick labels.
    config : dict
        Figure settings dictionary built in custom_config.py.
    baseline_level : Optional[float]
        Height of the reference line, or None for no line.

    ---- Globals read ----
    None.

    ---- Outputs ----
    np.ndarray
        x positions of the windows.

    ---- Globals mutated ----
    None. Changes the style of ``ax`` (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _axes_styler
    """

    # ---- 1 Draw the baseline ---------------------------------------------------------
    if baseline_level is not None:
        ax.axhline(baseline_level,
                   color='0.55',
                   linestyle='--',
                   linewidth=config['THIN_LINE_WIDTH'],
                   zorder=1,
                   )

    # ---- 2 Set the x axis ------------------------------------------------------------
    x = np.arange(len(window_names), dtype=float)
    ax.set_xticks(x)
    if show_xlabels:
        ax.set_xticklabels(tick_labels, fontsize=config['RESPONSE_XTICK_FONT_SIZE'])
    else:
        ax.set_xticklabels([])

    # ---- 3 Style the axes ------------------------------------------------------------
    _axes_styler(ax, config, config['RESPONSE_TICK_FONT_SIZE'])
    if not show_xlabels:
        ax.tick_params(axis='x', labelbottom=False)
    return x


# ---- _RESPONSE METRIC CHECKER --------------------------------------------------------
def _response_metric_checker(metric: str, haem_source: str) -> None:
    """
    ---- Summary ----
    Helper function to reject a percent-of-baseline response for the delta abs sources,
    which start at 0.

    ---- Inputs ----
    metric : str
        Response metric: 'delta', 'change' or 'value'.
    haem_source : str
        Haem source key, for example 'delta_abs_od'.

    ---- Globals read ----
    DELTA_HAEM_SOURCES (schema constant).

    ---- Outputs ----
    None
        Nothing. Raises ValueError for the combination that is not allowed.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if metric == 'change' and haem_source in DELTA_HAEM_SOURCES:
        raise ValueError(f'HAEM_RESPONSE_METRIC "change" (% of baseline) cannot be '
                         f'used with AVERAGE_HAEM_SOURCE = '
                         f'"{haem_source}", which starts at 0 and is not scaled. Use '
                         f'"value" (change from the start-of-run '
                         f'reference) or "delta" (change from the baseline window), or'
                         f' average "abs" / "abs_od" instead.',
                         )


# ---- _RESPONSE SERIES DRAWER ---------------------------------------------------------
def _response_series_drawer(ax: Axes,
                            x: Iterable,
                            stats_list: list,
                            style: dict,
                            config: dict,
                            label: Optional[str] = None,
                            metric: str = 'change',
                            offset: float = 0.0,
                            ) -> bool:
    """
    ---- Summary ----
    Helper function to plot every run as a point, the mean as a line and SEM error bars
    for one group.

    ---- Inputs ----
    ax : Axes
        Matplotlib axes to draw on.
    x : Iterable
        x positions of the windows.
    stats_list : list
        Statistics dictionary (or None) for each window.
    style : dict
        Group style: colour, linestyle, marker.
    config : dict
        Figure settings dictionary built in custom_config.py.
    label : Optional[str]
        Unused legend text.
    metric : str
        Response metric: 'delta', 'change' or 'value'.
    offset : float
        Horizontal shift in x units so groups sit side by side.

    ---- Globals read ----
    None.

    ---- Outputs ----
    bool
        True if anything was drawn.

    ---- Globals mutated ----
    None. Draws on ``ax`` (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _metric_field_selector
    """

    # ---- 1 Read the statistics -------------------------------------------------------
    mean_key, sem_key, n_key, runs_key = _metric_field_selector(metric)
    means = np.array([s[mean_key] if s else np.nan for s in stats_list], dtype=float)
    if not np.isfinite(means).any():
        return False

    # ---- 2 Draw the mean line --------------------------------------------------------
    xs = np.asarray(x, dtype=float) + offset
    ax.plot(xs,
            means,
            color=style['colour'],
            linestyle=style['linestyle'],
            linewidth=config['RESPONSE_LINE_WIDTH'],
            label='_nolegend_',
            zorder=3,
            )

    # ---- 3 Draw the points and error bars --------------------------------------------
    for xi, stats in zip(xs, stats_list):
        if not stats:
            continue
        runs = np.array(list(stats[runs_key].values()), dtype=float)
        runs = runs[np.isfinite(runs)]
        ax.scatter(np.full(runs.size, xi),
                   runs,
                   s=config['RESPONSE_POINT_SIZE'],
                   marker=style['marker'],
                   color=style['colour'],
                   edgecolor='white',
                   linewidth=0.5 * config['THIN_LINE_WIDTH'],
                   zorder=4,
                   )
        if (stats[n_key] >= 2 and
            np.isfinite(stats[mean_key]) and
            np.isfinite(stats[sem_key])
            ):
            ax.errorbar(xi,
                        stats[mean_key],
                        yerr=stats[sem_key],
                        fmt='none',
                        ecolor=style['colour'],
                        elinewidth=config['RESPONSE_ERRORBAR_WIDTH'],
                        capsize=config['RESPONSE_CAPSIZE'],
                        zorder=2,
                        )
    return True


# ---- _RESPONSE WINDOW TESTER ---------------------------------------------------------
def _response_window_tester(ax: Axes,
                            x: np.ndarray,
                            windows: list,
                            series_by_strain: dict,
                            strains: tuple,
                            metric: str,
                            config: dict,
                            panel_name: str,
                            tests: list,
                            ) -> None:
    """
    ---- Summary ----
    Helper function to run a Student t-test between the two groups at every window of a
    response panel and mark the significant windows.

    ---- Inputs ----
    ax : Axes
        Matplotlib axes to draw on.
    x : np.ndarray
        x positions of the windows.
    windows : list
        Window names.
    series_by_strain : dict
        {strain: [statistics per window]}.
    strains : tuple
        Group names (rows or bars), in drawing order.
    metric : str
        Response metric: 'delta', 'change' or 'value'.
    config : dict
        Figure settings dictionary built in custom_config.py.
    panel_name : str
        Panel name written to the test table.
    tests : list
        List collecting one dictionary per t-test comparison.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Appends one dictionary per comparison to ``tests`` and draws on ``ax`` (side
    effects).

    ---- Equations ----
    Equal-variance Student t-test per window; p values adjusted across the windows of
    the panel (RESPONSE_TEST_CORRECTION); significant if p_adj < RESPONSE_TEST_ALPHA.

    ---- Helpers ----
    _metric_field_selector
    _p_value_adjuster
    _test_bar_drawer
    """

    if not config['RESPONSE_TESTS'] or len(strains) != 2:
        return
    # ---- 1 Select the series ---------------------------------------------------------
    first, second = (series_by_strain.get(strain) for strain in strains)
    if not first or not second:
        return
    mean_key, sem_key, _, runs_key = _metric_field_selector(metric)

    # ---- 2 Test every window ---------------------------------------------------------
    results = []
    for i, window in enumerate(windows):
        stats_a, stats_b = first[i], second[i]
        if not stats_a or not stats_b:
            continue
        a = np.array(list(stats_a[runs_key].values()), dtype=float)
        b = np.array(list(stats_b[runs_key].values()), dtype=float)
        a, b = a[np.isfinite(a)], b[np.isfinite(b)]
        if a.size < 2 or b.size < 2 or (np.ptp(a) == 0 and np.ptp(b) == 0):
            continue
        result = scipy_stats.ttest_ind(a, b, equal_var=True)
        if not np.isfinite(result.pvalue):
            continue
        top = max(a.max(),
                  b.max(),
                  *(s[mean_key] + (s[sem_key] if np.isfinite(s[sem_key]) else 0.0)
                    for s in (stats_a, stats_b)
                    ),
                  )
        results.append({'index': i,
                        'window': window,
                        't': float(result.statistic),
                        'p': float(result.pvalue),
                        'top': float(top),
                        'n_a': int(a.size),
                        'n_b': int(b.size),
                        'mean_a': float(a.mean()),
                        'mean_b': float(b.mean()),
                        },
                       )

    # ---- 3 Adjust the p values -------------------------------------------------------
    adjusted = _p_value_adjuster([r['p'] for r in results],
                                 config['RESPONSE_TEST_CORRECTION'],
                                 )
    marks = []
    for result, p_adjusted in zip(results, adjusted):
        significant = bool(p_adjusted < config['RESPONSE_TEST_ALPHA'])
        tests.append({'panel': panel_name,
                      'window': result['window'],
                      f'{strains[0]} n': result['n_a'],
                      f'{strains[1]} n': result['n_b'],
                      f'{strains[0]} mean': result['mean_a'],
                      f'{strains[1]} mean': result['mean_b'],
                      't': result['t'],
                      'p': result['p'],
                      'p adjusted': float(p_adjusted),
                      'correction': config['RESPONSE_TEST_CORRECTION'],
                      'significant': significant,
                      },
                     )
        if significant:
            marks.append((result,
                          '***'
                          if p_adjusted < 0.001
                          else '**'
                          if p_adjusted < 0.01
                          else '*',
                          ),
                         )
    if not marks:
        return
    # Headroom so the bars and stars sit inside the axes: they need a fixed number of
    # points, so work out what fraction of the
    # axis that is from its current height, and extend the y range by it.
    axes_height_pt = ax.get_position().height * ax.figure.get_size_inches()[1] * 72.0
    # ---- 4 Draw the significance bars ------------------------------------------------
    fraction = min(0.4, config['RESPONSE_TEST_HEADROOM_PT'] / axes_height_pt)
    low, high = ax.get_ylim()
    high = max(high, max(result['top'] for result, _ in marks))
    ax.set_ylim(low, low + (high - low) / (1.0 - fraction))
    half = config['RESPONSE_GROUP_DODGE'] / 2.0
    for result, text in marks:
        centre = x[result['index']]
        _test_bar_drawer(ax, centre - half, centre + half, result['top'], text, config)


# ---- _ROW YLIM SHARER ----------------------------------------------------------------
def _row_ylim_sharer(axes_row: list) -> None:
    """
    ---- Summary ----
    Helper function to give every axes in a row the union of their y ranges.

    ---- Inputs ----
    axes_row : list
        Axes of one row.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Sets the y limits of the axes (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    lows, highs = zip(*(ax.get_ylim() for ax in axes_row))
    for ax in axes_row:
        ax.set_ylim(min(lows), max(highs))


# ---- _SIGNIFICANCE BAR DRAWER --------------------------------------------------------
def _significance_bar_drawer(ax: Axes,
                             x_left: float,
                             x_right: float,
                             y: float,
                             text: str,
                             tick_size: float,
                             config: dict,
                             ) -> None:
    """
    ---- Summary ----
    Helper function to draw a bracket between two x positions with text centred above
    it.

    ---- Inputs ----
    ax : Axes
        Matplotlib axes to draw on.
    x_left : float
        Left end of the bracket (data units).
    x_right : float
        Right end of the bracket (data units).
    y : float
        Height of the bracket (data units).
    text : str
        Text written above the bracket.
    tick_size : float
        Tick label size in points.
    config : dict
        Figure settings dictionary built in custom_config.py.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Draws on ``ax`` (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 Calculate the bracket height ----------------------------------------------
    height = config['BASELINE_TEST_BRACKET_HEIGHT'] * (ax.get_ylim()[1] -
                                                       ax.get_ylim()[0]
                                                       )

    # ---- 2 Draw the bracket ----------------------------------------------------------
    ax.plot([x_left, x_left, x_right, x_right],
            [y, y + height, y + height, y],
            color='black',
            linewidth=config['RESPONSE_ERRORBAR_WIDTH'],
            solid_capstyle='butt',
            clip_on=False,
            zorder=5,
            )

    # ---- 3 Add the label -------------------------------------------------------------
    ax.text((x_left + x_right) / 2,
            y + height,
            text,
            ha='center',
            va='bottom',
            fontsize=config['BASELINE_TEST_FONT_SIZE'],
            zorder=5,
            )


# ---- _SIGNIFICANCE FORMATTER ---------------------------------------------------------
def _significance_formatter(p_value: float, style: str) -> str:
    """
    ---- Summary ----
    Helper function to format a p value as stars or as text.

    ---- Inputs ----
    p_value : float
        p value.
    style : str
        'stars' or 'p'.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        '***', '**', '*' or 'ns' (stars style) or the p value text.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if style == 'p':
        return 'p < 0.001' if p_value < 0.001 else f'p = {p_value:.3f}'
    return ('***'
            if p_value < 0.001
            else '**'
            if p_value < 0.01
            else '*'
            if p_value < 0.05
            else 'ns'
            )


# ---- _TEST BAR DRAWER ----------------------------------------------------------------
def _test_bar_drawer(ax: Axes,
                     x_left: float,
                     x_right: float,
                     y: float,
                     text: str,
                     config: dict,
                     ) -> None:
    """
    ---- Summary ----
    Helper function to draw a small bracket joining the two groups' points at one window
    with text above it.

    ---- Inputs ----
    ax : Axes
        Matplotlib axes to draw on.
    x_left : float
        Left end (data units).
    x_right : float
        Right end (data units).
    y : float
        Data height the clearances are measured from.
    text : str
        Stars written above the bracket.
    config : dict
        Figure settings dictionary built in custom_config.py.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Draws on ``ax`` (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _offset_transformer
    """

    # ---- 1 Read the sizes ------------------------------------------------------------
    gap = 0.5 * config['RESPONSE_MARKER_SIZE'] + 1.0
    tick = config['RESPONSE_TEST_BAR_TICK']
    width = config['RESPONSE_ERRORBAR_WIDTH']

    # ---- 2 Define the offset helper --------------------------------------------------
    def _offset_transformer(points: float) -> Any:
        """
        ---- Summary ----
        Helper function to build a transform that shifts data coordinates upward by a
        number of points.

        ---- Inputs ----
        points : float
            Upward shift in points.

        ---- Globals read ----
        None.

        ---- Outputs ----
        Any
            Matplotlib transform.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        return (ax.transData + ScaledTranslation(0,
                                                 points / 72.0,
                                                 ax.figure.dpi_scale_trans,
                                                 )
                )

    # ---- 3 Draw the horizontal bar ---------------------------------------------------
    ax.plot([x_left, x_right],
            [y, y],
            color='black',
            linewidth=width,
            solid_capstyle='butt',
            transform=_offset_transformer(gap + tick),
            clip_on=False,
            zorder=6,
            scalex=False,
            scaley=False,
            )

    # ---- 4 Draw the end ticks --------------------------------------------------------
    ax.plot([x_left, x_right],
            [y, y],
            linestyle='none',
            marker='|',
            markersize=tick,
            markeredgewidth=width,
            color='black',
            transform=_offset_transformer(gap + tick / 2),
            clip_on=False,
            zorder=6,
            scalex=False,
            scaley=False,
            )

    # ---- 5 Add the label -------------------------------------------------------------
    ax.annotate(text,
                xy=((x_left + x_right) / 2, y),
                xytext=(0, gap + tick + 0.5),
                textcoords='offset points',
                ha='center',
                va='bottom',
                fontsize=config['RESPONSE_TEST_FONT_SIZE'],
                annotation_clip=False,
                zorder=6,
                )


# ---- _TICK LABEL BUILDER -------------------------------------------------------------
def _tick_label_builder(experiment: Optional[dict], window_names: list) -> list:
    """
    ---- Summary ----
    Helper function to build the x tick labels of the averaging windows: Baseline, then
    the addition that precedes each window.

    ---- Inputs ----
    experiment : Optional[dict]
        Reference experiment whose events label the windows, or None.
    window_names : list
        Averaging window names, for example ['average0', 'average1'].

    ---- Globals read ----
    None.

    ---- Outputs ----
    list
        One label per window; additions are written as label and concentration.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    finite_float_converter
    """

    # ---- 1 Read the events -----------------------------------------------------------
    events = []
    if experiment is not None:
        events = sorted(experiment.get('metadata', {}).get('events', []),
                        key=lambda e: finite_float_converter(e.get('time', 0)),
                        )

    # ---- 2 Build a label for each window ---------------------------------------------
    labels = []
    for window_name in window_names:
        number = int(window_name[len('average'):])
        if number == 0:
            labels.append('Baseline')
        elif number - 1 >= len(events):
            labels.append(f'After addition {number}')
        else:
            event = events[number - 1]
            label = event.get('label') or event.get('name') or f'Addition {number}'
            conc = event.get('concentration_uM')
            try:
                labels.append(f'{label}\n{concentration_formatter(conc)}'
                              if conc is not None
                              else str(label),
                              )
            except (TypeError, ValueError):
                labels.append(str(label))
    return labels


# ---- _WINDOW ORDERER -----------------------------------------------------------------
def _window_orderer(order: str,
                    strains: tuple,
                    triplicates: dict,
                    conditions: dict,
                    ) -> list:
    """
    ---- Summary ----
    Helper function to list the averaging windows present in any condition of one
    addition order.

    ---- Inputs ----
    order : str
        Addition order name.
    strains : tuple
        Group names (rows or bars), in drawing order.
    triplicates : dict
        Across-run statistics per condition, from triplicate_averager (DATA_FORMAT.md).
    conditions : dict
        Lookup {(strain, order): condition name}.

    ---- Globals read ----
    None.

    ---- Outputs ----
    list
        Window names in numerical order.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    names = set()
    for strain in strains:
        condition = conditions.get((strain, order))
        if condition:
            names.update(triplicates[condition]['windows'])
    return sorted(names, key=lambda n: int(n[len('average'):]))


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- EXEMPLAR FIGURE PLOTTER ---------------------------------------------------------
def exemplar_figure_plotter(experiments: dict,
                            config: dict,
                            individual_config: dict,
                            ) -> tuple:
    """
    ---- Summary ----
    Main function to build the exemplar figure: one run per condition, each drawn by the
    individual plotter in its own quadrant.

    ---- Inputs ----
    experiments : dict
        Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.
    config : dict
        Exemplar figure settings from custom_config.exemplar_config_builder.
    individual_config : dict
        Individual-experiment plot settings, as returned by Config.plot_config in
        config.py.

    ---- Globals read ----
    None.

    ---- Outputs ----
    tuple
        (fig, axes); axes maps (strain, order) to its list of axes and 'letters' to
        {letter: experiment name}.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _crop_start_finder
    _exemplar_gap_calculator
    _exemplar_plotter
    _exemplar_selector
    _experiment_cropper
    _figure_finisher
    experiment_title_builder
    watermark_style_builder
    """

    # ---- 1 Validate and select the runs ----------------------------------------------
    orders, strains = tuple(config['ORDER_COLUMNS']), tuple(config['STRAIN_ROWS'])
    unknown = [o for o in orders if o not in ORDER_TITLES]
    if unknown or not orders or not strains:
        raise ValueError(f'ORDER_COLUMNS must be a non-empty subset of '
                         f'{list(ORDER_TITLES)} and STRAIN_ROWS non-empty.',
                         )
    if config['PANEL_LETTER_CASE'] not in ('upper', 'lower'):
        raise ValueError('PANEL_LETTER_CASE must be "upper" or "lower".')
    individual_config = {**individual_config, **config.get('INDIVIDUAL_OVERRIDES', {})}
    exemplars = _exemplar_selector(experiments, config['EXEMPLAR_RUN'])
    # Optionally crop every run to start a little before its first addition, with time
    # measured from that addition, so the
    # additions line up across all four quadrants and the event labels need only be
    # written once per column.
    # ---- 2 Crop the runs -------------------------------------------------------------
    mode = config.get('CROP_START')
    if mode is not None:
        last_times = []
        for key, experiment in exemplars.items():
            start = _crop_start_finder(experiment,
                                       mode,
                                       config['CROP_BEFORE_FIRST_ADDITION_MINUTES'],
                                       config['CROP_MARGIN_MINUTES'],
                                       )
            exemplars[key], last = _experiment_cropper(experiment, start)
            last_times.append(last)
        individual_config = {**individual_config,
                             'X_MIN': 0.0,
                             'X_MAX': max(last_times),
                             'Y_SCALE_IGNORE_FIRST_MINUTES': 0.0,
                             'TIME_AXIS_LABEL': config['TIME_AXIS_LABEL'],
                             }

    # ---- 3 Check the additions line up -----------------------------------------------
    # The event labels are written above the top row only, so the rows of a column must
    # have their additions at the same times.
    for order in orders:
        times = [[round(e['time'], 2)
                  for e in exemplars[(strain, order)]['metadata']['events']
                  ]
                 for strain in strains
                 if (strain, order) in exemplars
                 ]
        if (len(times) > 1 and
            (len({len(t) for t in times}) > 1 or
             any(abs(a - b) > 0.3 for t in times[1:] for a, b in zip(times[0], t))
             )
            ):
            print(f'Warning: the additions in the {ORDER_TITLES[order]} column are not'
                  f' at the same times in both rows ({times}); '
                  f'the event labels above the column are those of {strains[0]}.',
                  )

    # ---- 4 Draw the quadrants --------------------------------------------------------
    fig = plt.figure(figsize=config['FIGURE_SIZE'], dpi=config['FIGURE_DPI'])
    row_hspace, column_wspace = _exemplar_gap_calculator(config,
                                                         individual_config,
                                                         len(strains),
                                                         len(orders),
                                                         )
    grid = fig.add_gridspec(nrows=len(strains),
                            ncols=len(orders),
                            hspace=row_hspace,
                            wspace=column_wspace,
                            )
    letters, letter_names, axes_by_cell, panels = iter('ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                                                       ), {}, {}, []
    for r, strain in enumerate(strains):
        for c, order in enumerate(orders):
            experiment = exemplars.get((strain, order))
            if experiment is None:
                print(f"Warning: no run{config['EXEMPLAR_RUN']} experiment found for "
                      f'{strain}, '
                      f'{ORDER_TITLES[order]}; that quadrant is empty.',
                      )
                continue
            quadrant_config = (individual_config
                               if r == 0
                               else {**individual_config, 'EVENT_LABELS': False}
                               )
            axes = _exemplar_plotter(fig, grid[r, c], experiment, quadrant_config)
            axes_by_cell[(strain, order)] = axes
            letter = next(letters)
            letter_names[letter] = experiment['experiment_name']
            if config.get('RUN_NAME_WATERMARK', True):
                # Faint run name inside the top panel's empty bottom-left corner, so it
                # takes no space at all.
                axes[0].text(0.012,
                             0.06,
                             experiment_title_builder(experiment, individual_config),
                             transform=axes[0].transAxes,
                             ha='left',
                             va='bottom',
                             zorder=1,
                             **watermark_style_builder(individual_config),
                             )
            panels.append((letter, axes[0], list(axes)))

    # ---- 5 Fit margins and add panel letters -----------------------------------------
    suptitle = None
    if config['FIGURE_TITLE']:
        suptitle = fig.suptitle(config['FIGURE_TITLE'],
                                fontsize=config['SUPTITLE_FONT_SIZE'],
                                fontweight='bold',
                                )
    _figure_finisher(fig, config, panels, suptitle, fit_to_corner=True)
    print('  Exemplar panels: ' + ', '.join(f'{letter} = {name}'
                                            for letter, name in letter_names.items()
                                            ),
          )
    return fig, {**axes_by_cell, 'letters': letter_names}


# ---- PUBLICATION FIGURE PLOTTER ------------------------------------------------------
def publication_figure_plotter(experiments: dict,
                               triplicates: dict,
                               config: dict,
                               ) -> tuple:
    """
    ---- Summary ----
    Main function to build the publication figure: baseline OCR, OCR response and haem
    response blocks.

    ---- Inputs ----
    experiments : dict
        Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.
    triplicates : dict
        Across-run statistics from triplicate_averager.
    config : dict
        Publication figure settings from custom_config.publication_config_builder.

    ---- Globals read ----
    None.

    ---- Outputs ----
    tuple
        (fig, axes); axes holds 'baseline', 'ocr_response', 'haem_response' and
        'letters' ({letter: panel name}).

    ---- Globals mutated ----
    None. Stores the t-test table on the returned figure as ``fig.response_tests``.

    ---- Equations ----
    None.

    ---- Helpers ----
    _baseline_bar_plotter
    _block_gap_calculator
    _condition_indexer
    _experiment_classifier
    _figure_finisher
    _haem_block_plotter
    _haem_row_selector
    _haem_source_finder
    _layout_validator
    _ocr_block_plotter
    _panel_labeller
    _reference_selector
    _response_metric_checker
    """

    # ---- 1 Validate and select -------------------------------------------------------
    orders, strains = _layout_validator(config)
    haem_rows = _haem_row_selector(config)
    conditions = _condition_indexer(triplicates)
    references = _reference_selector(experiments,
                                     triplicates,
                                     conditions,
                                     orders,
                                     strains,
                                     )
    unclassified = [n for n in experiments if None in _experiment_classifier(n)[:2]]
    if unclassified:
        print(f'Note: not used in the publication figure (strain/order/run not '
              f'identified): {unclassified}',
              )
    blocks = list(config['BLOCK_ORDER'])
    haem_source = None
    if 'haem_response' in blocks:
        haem_source = _haem_source_finder(triplicates)
        _response_metric_checker(config['HAEM_RESPONSE_METRIC'], haem_source)
    # ---- 2 Create the figure grid ----------------------------------------------------
    fig = plt.figure(figsize=config['FIGURE_SIZE'], dpi=config['FIGURE_DPI'])
    block_hspace, column_wspace = _block_gap_calculator(config,
                                                        len(blocks),
                                                        len(orders),
                                                        )
    outer = fig.add_gridspec(nrows=len(blocks),
                             ncols=1,
                             hspace=block_hspace,
                             height_ratios=[config['HEIGHT_RATIOS'][name]
                                            for name in blocks
                                            ],
                             )
    cells = dict(zip(blocks, (outer[i] for i in range(len(blocks)))))
    letters, letter_names, panels, tests = iter('ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                                                ), {}, [], []
    def _panel_labeller(main_ax: Axes, members: list, name: str) -> None:
        """
        ---- Summary ----
        Helper function to give the next letter to a panel.

        ---- Inputs ----
        main_ax : Axes
            Main axes of the panel.
        members : list
            All axes that belong to the panel.
        name : str
            Panel name used in the printed panel list.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Appends to the enclosing ``panels`` and ``letter_names`` (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        letter = next(letters)
        letter_names[letter] = name
        panels.append((letter, main_ax, members))
    axes_baseline, axes_ocr, axes_haem = None, [], []

    # ---- 3 Draw the blocks -----------------------------------------------------------
    # Blocks are drawn (and lettered) top to bottom.
    for block in blocks:
        if block == 'baseline':
            # Top-left cell of a grid with one cell per order column, so it lines up
            # with the panels beneath it.
            grid = cells[block].subgridspec(1, len(orders), wspace=column_wspace)
            axes_baseline = fig.add_subplot(grid[0, 0])
            _baseline_bar_plotter(axes_baseline, experiments, strains, config)
            _panel_labeller(axes_baseline, [axes_baseline], 'baseline OCR')
        elif block == 'ocr_response':
            grid = cells[block].subgridspec(1, len(orders), wspace=column_wspace)
            axes_ocr = _ocr_block_plotter(fig,
                                          grid,
                                          orders,
                                          strains,
                                          triplicates,
                                          conditions,
                                          references,
                                          config,
                                          tests,
                                          )
            for order, ax in zip(orders, axes_ocr):  # one letter per addition order
                _panel_labeller(ax, [ax], f'OCR response {ORDER_TITLES[order]}')
        else:  # haem_response
            grid = cells[block].subgridspec(len(haem_rows),
                                            len(orders),
                                            hspace=config.get('HAEM_ROWS_HSPACE', 0.0),
                                            wspace=column_wspace,
                                            )
            axes_haem, haem_span = _haem_block_plotter(fig,
                                                       grid,
                                                       orders,
                                                       strains,
                                                       triplicates,
                                                       conditions,
                                                       references,
                                                       config,
                                                       haem_rows,
                                                       haem_source,
                                                       tests,
                                                       )
            for column, order in enumerate(orders):  # one letter per addition order
                members = [row[column] for row in axes_haem]
                if column == 0:
                    # the shared y label sits left of the first column
                    members.append(haem_span)
                _panel_labeller(axes_haem[0][column],
                                members,
                                f'haem response {ORDER_TITLES[order]}',
                                )

    # ---- 4 Fit margins and add panel letters -----------------------------------------
    suptitle = None
    if config['FIGURE_TITLE']:
        suptitle = fig.suptitle(config['FIGURE_TITLE'],
                                fontsize=config['SUPTITLE_FONT_SIZE'],
                                fontweight='bold',
                                )
    _figure_finisher(fig, config, panels, suptitle)

    # ---- 5 Report --------------------------------------------------------------------
    fig.response_tests = tests
    if config['RESPONSE_TESTS']:
        significant = sum(row['significant'] for row in tests)
        print(f"  Response t-tests (Student, {config['RESPONSE_TEST_CORRECTION']} "
              f'correction across the windows of each panel): '
              f'{significant} of {len(tests)} comparisons below p = '
              f"{config['RESPONSE_TEST_ALPHA']:g}",
              )
    print('  Panels: ' + ', '.join(f'{letter} = {name}'
                                   for letter, name in letter_names.items()
                                   ),
          )
    return fig, {'baseline': axes_baseline,
                 'ocr_response': axes_ocr,
                 'haem_response': axes_haem,
                 'letters': letter_names,
                 }


# ---- PUBLICATION FIGURE SAVER --------------------------------------------------------
def publication_figure_saver(fig: Figure, export_root: Path, config: dict) -> list:
    """
    ---- Summary ----
    Main function to save a publication or exemplar figure at its exact size, plus the
    t-test table when there is one.

    ---- Inputs ----
    fig : Figure
        Figure returned by publication_figure_plotter or exemplar_figure_plotter.
    export_root : Path
        Results folder.
    config : dict
        Figure settings dictionary built in custom_config.py.

    ---- Globals read ----
    None.

    ---- Outputs ----
    list
        Paths of the files written.

    ---- Globals mutated ----
    None. Writes files under <export_root>/<OUTPUT_SUBFOLDER> (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    figure_saver
    """

    # ---- 1 Save the figure -----------------------------------------------------------
    folder = Path(export_root) / config['OUTPUT_SUBFOLDER']
    width, height = config['FIGURE_SIZE']
    paths = figure_saver(fig,
                         folder,
                         config['FILE_NAME'],
                         config['SAVE_FORMATS'],
                         config['FIGURE_SIZE'],
                         config['FIGURE_DPI'],
                         tight=config['TIGHT_BBOX'],
                         )

    # ---- 2 Save the test results -----------------------------------------------------
    tests = getattr(fig, 'response_tests', None)
    if tests:
        table_path = folder / f"{config['FILE_NAME']}_response_tests.csv"
        pd.DataFrame(tests).to_csv(table_path, index=False)
        paths = list(paths) + [table_path]

    # ---- 3 Report the export ---------------------------------------------------------
    print(f"  {config['FILE_NAME']} saved at {width:g} x {height:g} in, "
          f"{config['FIGURE_DPI']} dpi "
          f"({round(width * config['FIGURE_DPI'])} x "
          f"{round(height * config['FIGURE_DPI'])} px): "
          f'{folder.relative_to(Path(export_root))}',
          )
    return paths
