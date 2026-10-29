"""
Figure of four exemplar experiments in a 2x2 grid.
"""

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.gridspec import SubplotSpec

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_custom.run_namer import experiment_classifier, ORDER_TITLES
from utils_shared.figure_layout import (figure_finisher,
                                        gap_space_calculator,
                                        stack_legend_drawer,
                                        )
from utils_shared.individual_experiment_plotter import (experiment_drawer,
                                                        experiment_title_builder,
                                                        watermark_style_builder,
                                                        )
from utils_shared.schema import TIME_COLUMN, time_getter


# ---- EXEMPLAR HELPERS ----------------------------------------------------------------


# ---- _crop_start_finder --------------------------------------------------------------
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


# ---- _exemplar_gap_calculator --------------------------------------------------------
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
    x 1.2 label + y label pad + 5 x 0.55 tick + 0.5 unit + 1.5 unit (points) for one
    column, 1.5 unit when there are several (the later columns have no y labels).

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
    if n_columns > 1:
        # the columns after the first have no y labels or tick labels
        column_gap = 1.5 * unit
    return (gap_space_calculator(row_gap, height_pt - 6 * unit, n_rows),
            gap_space_calculator(column_gap, width_pt - 8 * unit, n_columns),
            )


# ---- _exemplar_plotter ---------------------------------------------------------------
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


# ---- _exemplar_selector --------------------------------------------------------------
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
    experiment_classifier
    """

    # ---- 1 Prepare the lookup --------------------------------------------------------
    lookup = {}

    # ---- 2 Index the experiments -----------------------------------------------------
    for name, experiment in experiments.items():
        strain, order, experiment_run = experiment_classifier(name)
        if strain and order and experiment_run == run:
            if (strain, order) in lookup:
                raise ValueError(f'More than one run{run} experiment matches '
                                 f'{(strain, order)}: '
                                 f"{lookup[(strain, order)]['experiment_name']!r} and "
                                 f'{name!r}',
                                 )
            lookup[(strain, order)] = experiment
    return lookup


# ---- _experiment_cropper -------------------------------------------------------------
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


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- exemplar_figure_plotter ---------------------------------------------------------
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
    experiment_title_builder
    figure_finisher
    stack_legend_drawer
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
    row_axes = {}
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
            # One legend per row, drawn after the layout is final (section 6).
            quadrant_config = {**quadrant_config,
                               'SHOW_LEGENDS': {'oxygen': False,
                                                'vo2': False,
                                                'haem': False,
                                                },
                               }
            if c > 0:
                quadrant_config['SHOW_Y_LABELS'] = False
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
            if c == len(orders) - 1:
                row_axes[r] = list(axes)

    # ---- 5 Give each haem the same y axis in every quadrant --------------------------
    by_haem = {}
    for quadrant_axes in axes_by_cell.values():
        for ax in quadrant_axes:
            names = getattr(ax, 'haem_names', None)
            if names:
                by_haem.setdefault(tuple(names), []).append(ax)
    for group in by_haem.values():
        lows, highs = zip(*(sorted(ax.get_ylim()) for ax in group))
        for ax in group:
            ax.set_ylim(min(lows), max(highs))

    # ---- 6 Fit margins and add panel letters -----------------------------------------
    suptitle = None
    if config['FIGURE_TITLE']:
        suptitle = fig.suptitle(config['FIGURE_TITLE'],
                                fontsize=config['SUPTITLE_FONT_SIZE'],
                                fontweight='bold',
                                )
    # One legend for the whole figure, centred between the top and bottom rows.
    rows_down = [row_axes[r] for r in sorted(row_axes)]
    if rows_down:
        stack_legend_drawer(rows_down[0],
                            individual_config,
                            bottom=rows_down[-1][-1],
                            )
    figure_finisher(fig, config, panels, suptitle)
    print('  Exemplar panels: ' + ', '.join(f'{letter} = {name}'
                                            for letter, name in letter_names.items()
                                            ),
          )
    return fig, {**axes_by_cell, 'letters': letter_names}
