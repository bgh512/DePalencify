"""
Figure of the baseline OCR, the OCR response and the haem response.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from typing import Any, Iterable, Optional

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.gridspec import SubplotSpec
from matplotlib.lines import Line2D
from matplotlib.transforms import ScaledTranslation
from scipy import stats as scipy_stats

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_custom.run_namer import (condition_classifier,
                                    experiment_classifier,
                                    ORDER_TITLES,
                                    )
from utils_shared.figure_layout import figure_finisher, gap_space_calculator
from utils_shared.helpers import concentration_formatter, name_simplifier
from utils_shared.individual_experiment_plotter import _HideTopTickLabels
from utils_shared.schema import DELTA_HAEM_SOURCES, finite_float_converter


# ---- CONSTANTS -----------------------------------------------------------------------
BLOCK_NAMES = ('baseline', 'ocr_response', 'haem_response')
RESPONSE_METRICS = ('delta', 'change', 'value')


# ---- OCR AND HAEM RESPONSE HELPERS ---------------------------------------------------


# ---- _axes_styler --------------------------------------------------------------------
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


# ---- _baseline_bar_plotter -----------------------------------------------------------
def _baseline_bar_plotter(ax: Axes,
                          experiments: dict,
                          strains: tuple,
                          config: dict,
                          tests: list,
                          ) -> dict:
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
    tests : list
        List collecting one dictionary per t-test comparison.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        Baseline summary for the workbook: 'strains', 'vo2_source' and 'runs' ({group:
        {experiment name: baseline OCR}}).

    ---- Globals mutated ----
    None. Draws on ``ax`` and appends the baseline t-test to ``tests`` (side effects).

    ---- Equations ----
    Bar height = mean of the run baselines; error bar = SEM = SD / sqrt(n). Student
    t-test with equal variances between the two groups.

    ---- Helpers ----
    _axes_styler
    _column_chooser
    _significance_bar_drawer
    _significance_formatter
    experiment_classifier
    finite_float_converter
    """

    # ---- 1 Collect the baseline of each run ------------------------------------------
    runs = {strain: {} for strain in strains}
    vo2_source = None
    for name, experiment in experiments.items():
        strain, _, _ = experiment_classifier(name)
        averages = experiment.get('averages')
        if strain not in runs or not averages:
            continue
        vo2_source = vo2_source or averages['settings']['vo2_source']
        baseline = averages['windows'].get('average0', {}).get('vo2', {})
        column = _column_chooser(baseline, config['OCR_VO2_COLUMN'])
        value = (finite_float_converter(baseline.get(column, {}).get('mean'))
                 if column
                 else np.nan
                 )
        if np.isfinite(value):
            runs[strain][name] = value
        else:
            print(f'Warning: no baseline OCR for {name}; excluded from the baseline '
                  f'panel.',
                  )

    # ---- 2 Draw bars and points ------------------------------------------------------
    values = {strain: list(runs[strain].values()) for strain in strains}
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
    ax.set_title('Baseline OCR')
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
    alpha = config['RESPONSE_TEST_ALPHA']
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
            tests.append({'panel': 'Baseline OCR',
                          'measurement': 'average0',
                          'metric': 'value',
                          'window': 'average0',
                          'group_a': strains[0],
                          'group_b': strains[1],
                          'values_a': dict(runs[strains[0]]),
                          'values_b': dict(runs[strains[1]]),
                          't': float(result.statistic),
                          'p': float(result.pvalue),
                          'p_adjusted': float(result.pvalue),
                          'correction': 'none',
                          'alpha': alpha,
                          'significant': bool(result.pvalue < alpha),
                          'mark': test_text,
                          },
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
    return {'strains': tuple(strains), 'vo2_source': vo2_source, 'runs': runs}


# ---- _block_gap_calculator -----------------------------------------------------------
def _block_gap_calculator(config: dict, blocks: list, n_columns: int) -> tuple:
    """
    ---- Summary ----
    Helper function to calculate the gap below each block of the OCR and haem response
    figure (each gap is sized for what it holds) and the gap between the response
    columns.

    ---- Inputs ----
    config : dict
        Figure settings dictionary built in custom_config.py.
    blocks : list
        Block names from top to bottom ('baseline', 'ocr_response', 'haem_response').
    n_columns : int
        Number of addition-order columns.

    ---- Globals read ----
    None.

    ---- Outputs ----
    tuple
        (gaps in points, one per block but the last; wspace as a GridSpec fraction).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    A gap above the first response block = x tick labels + 0.5 unit + title and legend
    row + 1.0 unit. The gap between the OCR and haem responses = two-line tick labels +
    0.5 unit + the significance bars' headroom + 0.5 unit. column_gap = 5 x 0.55 tick +
    0.5 unit + 1.5 unit (points).

    ---- Helpers ----
    gap_space_calculator
    """

    # ---- 1 Read the configuration ----------------------------------------------------
    unit = config['UNIT_PT']
    width_pt = config['FIGURE_SIZE'][0] * 72.0
    tick, xtick, title = (config['RESPONSE_TICK_FONT_SIZE'],
                          config['RESPONSE_XTICK_FONT_SIZE'],
                          config['TITLE_FONT_SIZE'],
                          )
    legend_row = 1.2 * max(title, 1.8 * config['RESPONSE_LEGEND_FONT_SIZE'])

    # ---- 2 Calculate the gaps --------------------------------------------------------
    gaps = []
    for upper, lower in zip(blocks, blocks[1:]):
        if upper == 'ocr_response':
            headroom = config['RESPONSE_TEST_HEADROOM_PT']
            gaps.append(2.4 * xtick + 0.5 * unit + headroom + 0.5 * unit)
        else:
            gaps.append(1.2 * xtick + 0.5 * unit + legend_row + 1.0 * unit)
    column_gap = 5 * 0.55 * tick + 0.5 * unit + 1.5 * unit
    return gaps, gap_space_calculator(column_gap, width_pt - 8 * unit, n_columns)


# ---- _column_chooser -----------------------------------------------------------------
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


# ---- _condition_indexer --------------------------------------------------------------
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


# ---- _finite_run_filter --------------------------------------------------------------
def _finite_run_filter(runs: dict) -> dict:
    """
    ---- Summary ----
    Helper function to keep the runs that have a finite value.

    ---- Inputs ----
    runs : dict
        {run number or experiment name: value}; values may be NaN.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        The same mapping without the runs whose value is NaN or infinite; values are
        floats.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return {run: float(value)
            for run, value in runs.items()
            if np.isfinite(value)
            }


# ---- _haem_block_plotter -------------------------------------------------------------
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
                        bars_above: bool = False,
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
    bars_above : bool
        True draws the top row's significance bars in the white space above the block
        (between it and the block above) instead of inside the axes.

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
    _mean_ylim_setter
    _measurement_finder
    _outside_bar_drawer
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
                                        outside=bars_above and r == 0,
                                        measurement=column,
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
        if bars_above and r == 0:
            for ax in grid_axes[0]:
                _outside_bar_drawer(ax, config)
        if r > 0:
            for ax in grid_axes[r]:
                hider = _HideTopTickLabels(config['RESPONSE_TICK_FONT_SIZE'])
                ax.yaxis.set_major_formatter(hider)
    return grid_axes, span


# ---- _haem_label_finder --------------------------------------------------------------
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


# ---- _haem_label_pad_calculator ------------------------------------------------------
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


# ---- _haem_row_selector --------------------------------------------------------------
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


# ---- _haem_source_finder -------------------------------------------------------------
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


# ---- _layout_validator ---------------------------------------------------------------
def _layout_validator(config: dict) -> tuple:
    """
    ---- Summary ----
    Helper function to check that the layout options of the OCR and haem response
    figure are recognised and to return the group and order lists.

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


# ---- _legend_handle_builder ----------------------------------------------------------
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


# ---- _mean_ylim_setter ---------------------------------------------------------------
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
    range is max(means) - min(means) (at least 1 % of the largest absolute mean). When
    all means are on one side of the baseline, the baseline side gets a 3 % margin.

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
    # When every mean lies on one side of the baseline, the baseline sits right at the
    # edge of the axis (a small margin only) and the data fill the rest, so the axis
    # does not waste half its height on the empty side.
    low, high = float(values.min()), float(values.max())
    span = max(high - low, 0.01 * max(abs(low), abs(high), 1e-12))
    edge = 0.03
    if baseline_level is not None and span > 0:
        if high <= baseline_level + 0.02 * span:
            ax.set_ylim(low - margin * span, baseline_level + edge * span)
            return
        if low >= baseline_level - 0.02 * span:
            ax.set_ylim(baseline_level - edge * span, high + margin * span)
            return
    ax.set_ylim(low - margin * span, high + margin * span)


# ---- _measurement_finder -------------------------------------------------------------
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


# ---- _metric_field_selector ----------------------------------------------------------
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


# ---- _ocr_block_plotter --------------------------------------------------------------
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
        ax.set_ylim(-3, 103)
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
                                    measurement=column,
                                    )

    # ---- 3 Share the axis limits -----------------------------------------------------
    if config['SHARE_Y_BETWEEN_ORDERS'] and len(axes) > 1:
        _row_ylim_sharer(axes)
    # The axis line itself covers only 0 to 100 % (the margins and the headroom for the
    # significance bars sit outside it).
    for ax in axes:
        ax.spines['left'].set_bounds(0, 100)

    # ---- 4 Return the axes -----------------------------------------------------------
    return axes


# ---- _offset_transformer -------------------------------------------------------------
def _offset_transformer(ax: Axes, points: float) -> Any:
    """
    ---- Summary ----
    Helper function to build a transform that shifts data coordinates upward by a
    number of points.

    ---- Inputs ----
    ax : Axes
        Matplotlib axes whose data coordinates are shifted.
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

    shift = ScaledTranslation(0, points / 72.0, ax.figure.dpi_scale_trans)
    return ax.transData + shift


# ---- _outside_bar_drawer -------------------------------------------------------------
def _outside_bar_drawer(ax: Axes, config: dict) -> None:
    """
    ---- Summary ----
    Helper function to draw the significance bars stored by _response_window_tester in
    the white space just above an axes, so the plot keeps its full height.

    ---- Inputs ----
    ax : Axes
        Response panel whose y range is final.
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
    _test_bar_drawer
    """

    half = config['RESPONSE_GROUP_DODGE'] / 2.0
    top = ax.get_ylim()[1]
    for centre, text in getattr(ax, 'outside_marks', []):
        _test_bar_drawer(ax, centre - half, centre + half, top, text, config)


# ---- _p_value_adjuster ---------------------------------------------------------------
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


# ---- _panel_labeller -----------------------------------------------------------------
def _panel_labeller(state: dict, main_ax: Axes, members: list, name: str) -> None:
    """
    ---- Summary ----
    Helper function to give the next letter to a panel.

    ---- Inputs ----
    state : dict
        Lettering state with keys 'letters' (iterator of letters), 'names' ({letter:
        panel name}) and 'panels' (list of (letter, main axes, member axes)).
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
    None. Advances ``state['letters']`` and appends to ``state['names']`` and
    ``state['panels']`` (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    letter = next(state['letters'])
    state['names'][letter] = name
    state['panels'].append((letter, main_ax, members))


# ---- _reference_level_finder ---------------------------------------------------------
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


# ---- _reference_selector -------------------------------------------------------------
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


# ---- _response_axes_preparer ---------------------------------------------------------
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


# ---- _response_metric_checker --------------------------------------------------------
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


# ---- _response_series_drawer ---------------------------------------------------------
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


# ---- _response_window_tester ---------------------------------------------------------
def _response_window_tester(ax: Axes,
                            x: np.ndarray,
                            windows: list,
                            series_by_strain: dict,
                            strains: tuple,
                            metric: str,
                            config: dict,
                            panel_name: str,
                            tests: list,
                            outside: bool = False,
                            measurement: str = '',
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
    outside : bool
        True keeps the axis range as it is and stores the marks on ``ax`` for
        _outside_bar_drawer, which draws them in the space above the axes.
    measurement : str
        Name of the measurement tested (OCR or haem column), written to the test table.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Appends one dictionary per comparison to ``tests`` (the keys are listed in
    DATA_FORMAT.md) and draws on ``ax`` (side effects); with ``outside`` it sets
    ``ax.outside_marks`` instead of drawing.

    ---- Equations ----
    Equal-variance Student t-test per window; p values adjusted across the windows of
    the panel (RESPONSE_TEST_CORRECTION); significant if p_adj < RESPONSE_TEST_ALPHA.

    ---- Helpers ----
    _finite_run_filter
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
        values_a = _finite_run_filter(stats_a[runs_key])
        values_b = _finite_run_filter(stats_b[runs_key])
        a = np.array(list(values_a.values()), dtype=float)
        b = np.array(list(values_b.values()), dtype=float)
        if a.size < 2 or b.size < 2 or (np.ptp(a) == 0 and np.ptp(b) == 0):
            continue
        result = scipy_stats.ttest_ind(a, b, equal_var=True)
        if not np.isfinite(result.pvalue):
            continue
        # The bar sits above the means plus their SEM, with the SEM capped at a tenth of
        # the axis so that one noisy window or outlier run does not stretch the axis
        sem_cap = 0.1 * (ax.get_ylim()[1] - ax.get_ylim()[0])
        sems = [min(s[sem_key], sem_cap) if np.isfinite(s[sem_key]) else 0.0
                for s in (stats_a, stats_b)
                ]
        top = max(s[mean_key] + sem for s, sem in zip((stats_a, stats_b), sems))
        results.append({'index': i,
                        'window': window,
                        't': float(result.statistic),
                        'p': float(result.pvalue),
                        'top': float(top),
                        'values_a': _finite_run_filter(stats_a[runs_key]),
                        'values_b': _finite_run_filter(stats_b[runs_key]),
                        },
                       )

    # ---- 3 Adjust the p values -------------------------------------------------------
    adjusted = _p_value_adjuster([r['p'] for r in results],
                                 config['RESPONSE_TEST_CORRECTION'],
                                 )
    marks = []
    for result, p_adjusted in zip(results, adjusted):
        significant = bool(p_adjusted < config['RESPONSE_TEST_ALPHA'])
        text = ''
        if significant:
            text = '***' if p_adjusted < 0.001 else '**' if p_adjusted < 0.01 else '*'
        tests.append({'panel': panel_name,
                      'measurement': measurement,
                      'metric': metric,
                      'window': result['window'],
                      'group_a': strains[0],
                      'group_b': strains[1],
                      'values_a': result['values_a'],
                      'values_b': result['values_b'],
                      't': result['t'],
                      'p': result['p'],
                      'p_adjusted': float(p_adjusted),
                      'correction': config['RESPONSE_TEST_CORRECTION'],
                      'alpha': config['RESPONSE_TEST_ALPHA'],
                      'significant': significant,
                      'mark': text,
                      },
                     )
        if significant:
            marks.append((result, text))
    if not marks:
        return
    if outside:
        ax.outside_marks = [(x[result['index']], text) for result, text in marks]
        return
    # Headroom so the bars and stars sit inside the axes: they need a fixed number of
    # points, so work out what fraction of the
    # axis that is from its current height, and extend the y range by it.
    axes_height_pt = ax.get_position().height * ax.figure.get_size_inches()[1] * 72.0
    # ---- 4 Draw the significance bars ------------------------------------------------
    # Only as much as the bars need above the highest marked point: a panel whose
    # data end well below the top of the axis already has the room.
    fraction = min(0.4, config['RESPONSE_TEST_HEADROOM_PT'] / axes_height_pt)
    low, high = ax.get_ylim()
    needed = max(result['top'] for result, _ in marks)
    ax.set_ylim(low, max(high, low + (needed - low) / (1.0 - fraction)))
    high = max(high, needed)
    # Only label ticks that lie within the data, not in the headroom above it.
    ax.set_yticks([tick for tick in ax.get_yticks() if low <= tick <= high])
    half = config['RESPONSE_GROUP_DODGE'] / 2.0
    for result, text in marks:
        centre = x[result['index']]
        _test_bar_drawer(ax, centre - half, centre + half, result['top'], text, config)


# ---- _row_ylim_sharer ----------------------------------------------------------------
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


# ---- _significance_bar_drawer --------------------------------------------------------
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


# ---- _significance_formatter ---------------------------------------------------------
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


# ---- _test_bar_drawer ----------------------------------------------------------------
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

    # ---- 3 Draw the horizontal bar ---------------------------------------------------
    ax.plot([x_left, x_right],
            [y, y],
            color='black',
            linewidth=width,
            solid_capstyle='butt',
            transform=_offset_transformer(ax, gap + tick),
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
            transform=_offset_transformer(ax, gap + tick / 2),
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


# ---- _tick_label_builder -------------------------------------------------------------
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
    concentration_formatter
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


# ---- _window_orderer -----------------------------------------------------------------
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


# ---- ocr_and_haem_response_figure_plotter --------------------------------------------
def ocr_and_haem_response_figure_plotter(experiments: dict,
                                         triplicates: dict,
                                         config: dict,
                                         ) -> tuple:
    """
    ---- Summary ----
    Main function to build the OCR and haem response figure: baseline OCR, OCR response
    and haem response blocks.

    ---- Inputs ----
    experiments : dict
        Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.
    triplicates : dict
        Across-run statistics from triplicate_averager.
    config : dict
        Figure settings from custom_config.ocr_and_haem_response_config_builder.

    ---- Globals read ----
    None.

    ---- Outputs ----
    tuple
        (fig, axes); axes holds 'baseline', 'ocr_response', 'haem_response' and
        'letters' ({letter: panel name}).

    ---- Globals mutated ----
    None. Stores the t-test records on the returned figure as ``fig.response_tests`` and
    the baseline summary as ``fig.response_baseline`` (None without a baseline block).

    ---- Equations ----
    None.

    ---- Helpers ----
    _baseline_bar_plotter
    _block_gap_calculator
    _condition_indexer
    _haem_block_plotter
    _haem_row_selector
    _haem_source_finder
    _layout_validator
    _legend_handle_builder
    _ocr_block_plotter
    _panel_labeller
    _reference_selector
    _response_metric_checker
    experiment_classifier
    figure_finisher
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
    unclassified = [n for n in experiments if None in experiment_classifier(n)[:2]]
    if unclassified:
        print('Note: not used in the OCR and haem response figure (strain/order/run '
              f'not identified): {unclassified}',
              )
    blocks = list(config['BLOCK_ORDER'])
    haem_source = None
    if 'haem_response' in blocks:
        haem_source = _haem_source_finder(triplicates)
        _response_metric_checker(config['HAEM_RESPONSE_METRIC'], haem_source)
    # ---- 2 Create the figure grid ----------------------------------------------------
    fig = plt.figure(figsize=config['FIGURE_SIZE'], dpi=config['FIGURE_DPI'])
    block_gaps, column_wspace = _block_gap_calculator(config, blocks, len(orders))
    content_pt = (config['FIGURE_SIZE'][1] * 72.0 - 6 * config['UNIT_PT']
                  - sum(block_gaps)
                  )
    weights = [config['HEIGHT_RATIOS'][name] for name in blocks]
    ratios = []
    for index, weight in enumerate(weights):
        ratios.append(content_pt * weight / sum(weights))
        if index < len(block_gaps):
            ratios.append(block_gaps[index])  # an empty spacer row of that height
    outer = fig.add_gridspec(nrows=len(ratios),
                             ncols=1,
                             hspace=0.0,
                             height_ratios=ratios,
                             )
    cells = dict(zip(blocks, (outer[2 * i] for i in range(len(blocks)))))
    letter_names, panels, tests = {}, [], []
    state = {'letters': iter('ABCDEFGHIJKLMNOPQRSTUVWXYZ'),
             'names': letter_names,
             'panels': panels,
             }
    axes_baseline, axes_ocr, axes_haem, baseline = None, [], [], None

    # ---- 3 Draw the blocks -----------------------------------------------------------
    # Blocks are drawn (and lettered) top to bottom.
    for block in blocks:
        if block == 'baseline':
            # Top-left cell of a grid with one cell per order column, so it lines up
            # with the panels beneath it.
            grid = cells[block].subgridspec(1, len(orders), wspace=column_wspace)
            axes_baseline = fig.add_subplot(grid[0, 0])
            baseline = _baseline_bar_plotter(axes_baseline,
                                             experiments,
                                             strains,
                                             config,
                                             tests,
                                             )
            _panel_labeller(state, axes_baseline, [axes_baseline], 'baseline OCR')
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
                _panel_labeller(state, ax, [ax], f'OCR response {ORDER_TITLES[order]}')
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
                                                       bars_above='ocr_response'
                                                       in blocks[:blocks.index(block)],
                                                       )
            for column, order in enumerate(orders):  # one letter per addition order
                members = [row[column] for row in axes_haem]
                if column == 0:
                    # the shared y label sits left of the first column
                    members.append(haem_span)
                _panel_labeller(state,
                                axes_haem[0][column],
                                members,
                                f'haem response {ORDER_TITLES[order]}',
                                )

    # ---- 4 Add one title and one legend per column -----------------------------------
    # The addition order heads each column, once, above its top response panel; the
    # group legend, in a box, shares that row at the right. Both sit as close to the
    # axes as they can.
    heads = axes_ocr or (list(axes_haem[0]) if axes_haem else [])
    for order, ax in zip(orders, heads):
        ax.set_title(ORDER_TITLES[order], pad=2)
        ax.legend(handles=_legend_handle_builder(strains, config),
                  loc='lower right',
                  bbox_to_anchor=(1.0, 1.0),
                  ncol=len(strains),
                  fontsize=config['RESPONSE_LEGEND_FONT_SIZE'],
                  frameon=True,
                  edgecolor='black',
                  fancybox=False,
                  borderaxespad=0.0,
                  borderpad=0.3,
                  columnspacing=1.0,
                  ).get_frame().set_linewidth(config['THIN_LINE_WIDTH'])

    # ---- 5 Fit margins and add panel letters -----------------------------------------
    suptitle = None
    if config['FIGURE_TITLE']:
        suptitle = fig.suptitle(config['FIGURE_TITLE'],
                                fontsize=config['SUPTITLE_FONT_SIZE'],
                                fontweight='bold',
                                )
    figure_finisher(fig, config, panels, suptitle)

    # ---- 6 Report --------------------------------------------------------------------
    fig.response_tests = tests
    fig.response_baseline = baseline
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
