"""Time response figure: waterfalls, example time courses and decompositions."""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from pathlib import Path
from typing import Any, Optional

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt
import numpy as np

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_custom.run_namer import hours_parser
from utils_shared.figure_layout import (figure_canvas_fitter,
                                        gap_space_calculator,
                                        panel_letter_adder,
                                        text_extent_calculator,
                                        )
from utils_shared.helpers import (concentration_formatter,
                                  figure_saver,
                                  name_simplifier,
                                  )
from utils_shared.individual_experiment_plotter import experiment_drawer


# ---- TIME RESPONSE PLOTTER HELPERS ---------------------------------------------------


# ---- _EVENT LABEL HEIGHT CALCULATOR --------------------------------------------------
def _event_label_height_calculator(experiments: list, individual_config: dict) -> float:
    """
    ---- Summary ----
    Helper function to calculate the height the rotated event labels above the example
    time courses need.

    ---- Inputs ----
    experiments : list
        Example experiments.
    individual_config : dict
        Individual-experiment plot settings, as returned by Config.plot_config in
        config.py.

    ---- Globals read ----
    None.

    ---- Outputs ----
    float
        Height in points; 0 when the labels are not drawn on top.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    text_extent_calculator
    """

    # ---- 1 Check whether events are plotted ------------------------------------------
    c = individual_config
    if not (c['PLOT_EVENTS'] and
            c['EVENT_LABELS'] and
            c.get('EVENT_LABELS_ON_TOP', True)
            ):
        return 0.0

    # ---- 2 Measure the labels --------------------------------------------------------
    heights = []
    for experiment in experiments:
        for event in experiment.get('metadata', {}).get('events', []):
            conc = event.get('concentration_uM')
            text = (f"{'? µM' if conc is None else concentration_formatter(conc)} "
                    f"{event.get('label', '')}".strip()
                    )
            heights.append(text_extent_calculator(text,
                                                  c['EVENT_LABEL_FONTSIZE'],
                                                  c['EVENT_LABEL_ROTATION'],
                                                  )[1],
                           )
    return (max(heights) if heights else 0.0) + c['EVENT_LABEL_OFFSET']


# ---- _EXAMPLE FINDER -----------------------------------------------------------------
def _example_finder(groups: dict, group: str, hours: float) -> tuple:
    """
    ---- Summary ----
    Helper function to find the experiment of one group at a given number of hours.

    ---- Inputs ----
    groups : dict
        {group: [(time label, experiment), ...]}.
    group : str
        Group name.
    hours : float
        Hours in the experiment name.

    ---- Globals read ----
    None.

    ---- Outputs ----
    tuple
        (time label, experiment). Raises ValueError if there is none.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    hours_parser
    """

    if group not in groups:
        raise ValueError(f'Example group {group!r} must be one of {list(groups)}.')
    for label, experiment in groups[group]:
        if hours_parser(experiment['experiment_name']) == float(hours):
            return label, experiment
    raise ValueError(f'No {group} experiment at {hours} hours; available: '
                     f'{[label for label, _ in groups[group]]}.',
                     )


# ---- _EXAMPLE VIEWER -----------------------------------------------------------------
def _example_viewer(experiment: dict) -> dict:
    """
    ---- Summary ----
    Helper function to copy an experiment so that its individual figure shows only the
    two windows its difference spectrum came from.

    ---- Inputs ----
    experiment : dict
        Experiment dictionary, as defined in DATA_FORMAT.md.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        Copy with averages holding the penultimate and final spectral windows.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    averages = experiment['spectral_averages']
    chosen = [averages['roles']['penultimate'], averages['roles']['final']]
    return {**experiment,
            'averages': {'windows': {name: averages['windows'][name] for name in chosen
                                     },
                         },
            }


# ---- _HAEM WINDOW DRAWER -------------------------------------------------------------
def _haem_window_drawer(ax: Axes, decomposition: dict, config: dict) -> None:
    """
    ---- Summary ----
    Helper function to shade, behind the spectra, a window around the peak of every
    haem in the haem's own colour, to show where each haem should appear.

    ---- Inputs ----
    ax : Axes
        Matplotlib axes with wavelength on the x axis.
    decomposition : dict
        difference_decomposition of an experiment (DATA_FORMAT.md).
    config : dict
        Figure settings dictionary built in custom_config.py.

    ---- Globals read ----
    config keys HAEM_COLOURS, HAEM_WINDOW_HALF_WIDTH_NM and HAEM_WINDOW_ALPHA.

    ---- Outputs ----
    None

    ---- Globals mutated ----
    None. Draws on ``ax`` and leaves its x limits as they were (side effect).

    ---- Equations ----
    window = peak +- HAEM_WINDOW_HALF_WIDTH_NM, where the peak is the wavelength of the
    largest absolute value of the haem's fitted component.

    ---- Helpers ----
    name_simplifier
    """

    # ---- 1 Draw one window per haem --------------------------------------------------
    colours = {name_simplifier(k): v for k, v in config['HAEM_COLOURS'].items()}
    half = config['HAEM_WINDOW_HALF_WIDTH_NM']
    x_limits = ax.get_xlim()
    for name, component in zip(decomposition['haem_names'],
                               decomposition['haem_individual'],
                               ):
        values = np.abs(component[:, 1])
        if not np.isfinite(values).any() or np.nanmax(values) == 0:
            continue
        centre = float(component[int(np.nanargmax(values)), 0])
        ax.axvspan(centre - half,
                   centre + half,
                   color=colours.get(name_simplifier(name)),
                   alpha=config['HAEM_WINDOW_ALPHA'],
                   linewidth=0,
                   zorder=0,
                   )
    ax.set_xlim(x_limits)


# ---- _LEGEND DRAWER ------------------------------------------------------------------
def _legend_drawer(ax: Axes,
                   config: dict,
                   location: str,
                   columns: Optional[int] = None,
                   outside: bool = False,
                   anchor: Optional[tuple] = None,
                   ) -> Any:
    """
    ---- Summary ----
    Helper function to draw a legend in the journal style: small text and an optional
    thin box.

    ---- Inputs ----
    ax : Axes
        Matplotlib axes to draw on.
    config : dict
        Figure settings dictionary built in custom_config.py.
    location : str
        Matplotlib legend location.
    columns : Optional[int]
        Number of legend columns, or None for the setting.
    outside : bool
        True puts the legend in the white space to the right of the axes.
    anchor : Optional[tuple]
        Axes-coordinate anchor of the legend's ``location`` point, which overrides
        ``outside``.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Any
        The legend.

    ---- Globals mutated ----
    None. Adds a legend to ``ax`` (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    options = {}
    if outside:
        options = {'loc': 'upper left',
                   'bbox_to_anchor': (1.03, 1.0),
                   'borderaxespad': 0,
                   }
    if anchor is not None:
        options = {'bbox_to_anchor': anchor, 'borderaxespad': 0}
    legend = ax.legend(**{'loc': location, **options},
                       frameon=config['LEGEND_FRAME'],
                       fontsize=config['LEGEND_FONT_SIZE'],
                       ncol=columns or config['LEGEND_COLUMNS'],
                       )
    if config['LEGEND_FRAME']:
        legend.get_frame().set_linewidth(config['THIN_LINE_WIDTH'])
    return legend


# ---- _TIME AXES STYLER ---------------------------------------------------------------
def _time_axes_styler(ax: Axes, config: dict) -> None:
    """
    ---- Summary ----
    Helper function to apply the tick direction, label size and spine style.

    ---- Inputs ----
    ax : Axes
        Matplotlib axes to draw on.
    config : dict
        Figure settings dictionary built in custom_config.py.

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
                   which='both',
                   labelsize=config['TICK_FONT_SIZE'],
                   direction=config['TICK_DIRECTION'],
                   )
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


# ---- _TIME GAP CALCULATOR ------------------------------------------------------------
def _time_gap_calculator(config: dict,
                         individual_config: dict,
                         label_height_pt: float,
                         ) -> tuple:
    """
    ---- Summary ----
    Helper function to calculate the row and column gaps of the time response figure
    from the font sizes and the figure size.

    ---- Inputs ----
    config : dict
        Figure settings dictionary built in custom_config.py.
    individual_config : dict
        Individual-experiment plot settings, as returned by Config.plot_config in
        config.py.
    label_height_pt : float
        Height of the event labels in points.

    ---- Globals read ----
    None.

    ---- Outputs ----
    tuple
        (hspace, wspace, row gap in points); the first two are GridSpec fractions.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    row_gap = 1.2 tick + 0.5 unit + label pad + 1.2 label + event label height + 1.0
    unit; column_gap = 1.2 label + 0.5 unit + 5 x 0.55 tick + 0.5 unit + 1.5 unit
    (points).

    ---- Helpers ----
    gap_space_calculator
    """

    # ---- 1 Read the configuration ----------------------------------------------------
    unit = config['UNIT_PT']
    width_pt, height_pt = (v * 72.0 for v in config['FIGURE_SIZE'])
    tick, label = config['TICK_FONT_SIZE'], config['AXIS_LABEL_FONT_SIZE']

    # ---- 2 Calculate the gaps --------------------------------------------------------
    row_gap = (1.2 * tick +
               0.5 * unit +
               individual_config['TIME_AXIS_LABEL_PAD'] +
               1.2 * label +
               label_height_pt +
               1.0 * unit
               )
    column_gap = 1.2 * label + 0.5 * unit + 5 * 0.55 * tick + 0.5 * unit + 1.5 * unit
    return (gap_space_calculator(row_gap, height_pt - 6 * unit, 3),
            gap_space_calculator(column_gap, width_pt - 8 * unit, 2),
            row_gap,
            )


# ---- _TITLE STYLER -------------------------------------------------------------------
def _title_styler(ax: Axes, text: str, config: dict) -> None:
    """
    ---- Summary ----
    Helper function to set a panel title in the figure style.

    ---- Inputs ----
    ax : Axes
        Matplotlib axes to draw on.
    text : str
        Title text.
    config : dict
        Figure settings dictionary built in custom_config.py.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Sets the title of ``ax`` (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    ax.set_title(text,
                 fontsize=config['TITLE_FONT_SIZE'],
                 loc=config['TITLE_ALIGNMENT'],
                 fontweight=config['TITLE_WEIGHT'],
                 )


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- DECOMPOSITION PLOTTER -----------------------------------------------------------
def decomposition_plotter(ax: Axes, decomposition: dict, config: dict) -> None:
    """
    ---- Summary ----
    Main function to draw a difference spectrum with its scatter-free fit, residual and
    each haem contribution.

    ---- Inputs ----
    ax : Axes
        Matplotlib axes to draw on.
    decomposition : dict
        difference_decomposition of an experiment (DATA_FORMAT.md).
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
    _haem_window_drawer
    _legend_drawer
    _time_axes_styler
    name_simplifier
    """

    # ---- 1 Read the decomposition ----------------------------------------------------
    measured = decomposition['no_scatter']
    residual = decomposition['residual']
    colours = {name_simplifier(k): v for k, v in config['HAEM_COLOURS'].items()}
    width = config['LINE_WIDTH']

    # ---- 2 Draw the spectra ----------------------------------------------------------
    ax.plot(measured[:, 0],
            measured[:, 1],
            color='black',
            label='Spectrum',
            linewidth=width,
            )
    ax.plot(residual[:, 0],
            residual[:, 1],
            color='grey',
            label='Residual',
            linewidth=width,
            )

    # ---- 3 Draw the haem components --------------------------------------------------
    for name, component in zip(decomposition['haem_names'],
                               decomposition['haem_individual'],
                               ):
        ax.plot(component[:, 0],
                component[:, 1],
                color=colours.get(name_simplifier(name)),
                label=name,
                linewidth=width,
                )

    # ---- 4 Style the axes ------------------------------------------------------------
    ax.set_xlim(left=np.min(measured[:, 0]), right=np.max(measured[:, 0]))
    _haem_window_drawer(ax, decomposition, config)
    ax.set_xlabel('Wavelength (nm)', fontsize=config['AXIS_LABEL_FONT_SIZE'])
    ax.set_ylabel(config['DECOMPOSITION_Y_LABEL'],
                  fontsize=config['AXIS_LABEL_FONT_SIZE'],
                  )
    _time_axes_styler(ax, config)
    _legend_drawer(ax, config, config['DECOMPOSITION_LEGEND_LOCATION'])
    ax.set_xlim(left=np.min(measured[:, 0]), right=np.max(measured[:, 0]))


# ---- GROUP COLLECTOR -----------------------------------------------------------------
def group_collector(experiments: dict, config: dict) -> dict:
    """
    ---- Summary ----
    Main function to collect the decomposed experiments of each group, with their time
    labels.

    ---- Inputs ----
    experiments : dict
        Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.
    config : dict
        Figure settings dictionary built in custom_config.py.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        {group: [(time label, experiment), ...]}. Experiments without a difference
        decomposition are reported and left out; ValueError if a group is empty.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    time_label_builder
    """

    # ---- 1 Prepare the groups --------------------------------------------------------
    groups = {group: [] for group in config['GROUP_ORDER']}

    # ---- 2 Collect the experiments ---------------------------------------------------
    for name, experiment in experiments.items():
        group = experiment.get('group')
        if group not in groups:
            continue
        if 'difference_decomposition' not in experiment:
            print(f'  Skipping {name} in the time response figure: no difference '
                  f'decomposition.',
                  )
            continue
        groups[group].append((time_label_builder(name, config['TIME_LABEL_FORMAT']),
                              experiment,
                              ),
                             )

    # ---- 3 Check for empty groups ----------------------------------------------------
    empty = [group for group, items in groups.items() if not items]
    if empty:
        raise ValueError(f"No decomposed experiments for group(s): {', '.join(empty)}.")
    return groups


# ---- SHARED BASELINE SUBTRACTER ------------------------------------------------------
def shared_baseline_subtracter(wavelengths: np.ndarray,
                               spectra: np.ndarray,
                               x_min: Optional[float] = None,
                               x_max: Optional[float] = None,
                               degree: int = 1,
                               ) -> tuple:
    """
    ---- Summary ----
    Main function to subtract one shared polynomial baseline, fitted to the mean
    spectrum, from every spectrum.

    ---- Inputs ----
    wavelengths : np.ndarray
        Wavelengths, shape (n_wavelengths, n_spectra), nm.
    spectra : np.ndarray
        Spectra, shape (n_wavelengths, n_spectra).
    x_min : Optional[float]
        Lower wavelength of the fit range, or None.
    x_max : Optional[float]
        Upper wavelength of the fit range, or None.
    degree : int
        Polynomial degree, at least 1.

    ---- Globals read ----
    None.

    ---- Outputs ----
    tuple
        (corrected spectra, shared baseline), both shaped like ``spectra``.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    baseline(w) = polynomial fitted to mean over spectra of S(w) within [x_min, x_max];
    corrected = S - baseline.

    ---- Helpers ----
    None.
    """

    # ---- 1 Check the inputs ----------------------------------------------------------
    if not isinstance(degree, (int, np.integer)) or degree < 1:
        raise ValueError('Baseline degree must be an integer of at least 1.')

    # ---- 2 Average the spectra -------------------------------------------------------
    mean_wavelengths = np.mean(wavelengths, axis=1)
    mean_spectrum = np.mean(spectra, axis=1)

    # ---- 3 Select the fit range ------------------------------------------------------
    mask = np.ones(mean_wavelengths.shape, dtype=bool)
    if x_min is not None:
        mask &= mean_wavelengths >= x_min
    if x_max is not None:
        mask &= mean_wavelengths <= x_max
    if len(np.unique(mean_wavelengths[mask])) <= degree:
        raise ValueError(f'Polynomial degree {degree} needs more than {degree} unique '
                         f'wavelengths in the baseline range.',
                         )

    # ---- 4 Fit and subtract the baseline ---------------------------------------------
    coefficients = np.polyfit(mean_wavelengths[mask], mean_spectrum[mask], deg=degree)
    shared_baseline = np.polyval(coefficients, wavelengths)
    return spectra - shared_baseline, shared_baseline


# ---- TIME LABEL BUILDER --------------------------------------------------------------
def time_label_builder(experiment_name: str,
                       label_format: str = '{hours:g} hours',
                       ) -> str:
    """
    ---- Summary ----
    Main function to build the label of a time point from the experiment name.

    ---- Inputs ----
    experiment_name : str
        Experiment name such as 'control_7hours'.
    label_format : str
        Format string with an {hours} field.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        For example '7 hours'; the experiment name when it contains no hours.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    hours_parser
    """

    hours = hours_parser(experiment_name)
    return (label_format.format(hours=hours)
            if hours is not None
            else str(experiment_name)
            )


# ---- TIME RESPONSE FIGURE PLOTTER ----------------------------------------------------
def time_response_figure_plotter(experiments: dict,
                                 config: dict,
                                 individual_config: dict,
                                 ) -> tuple:
    """
    ---- Summary ----
    Main function to build the time response figure: waterfalls, then two examples (time
    course and decomposition).

    ---- Inputs ----
    experiments : dict
        Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.
    config : dict
        Time response settings from custom_config.time_response_config_builder.
    individual_config : dict
        Individual-experiment plot settings, as returned by Config.plot_config in
        config.py.

    ---- Globals read ----
    None.

    ---- Outputs ----
    tuple
        (fig, axes); axes maps the panel letters 'A'-'F' to axes (the time-course
        examples give their list of axes).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _event_label_height_calculator
    _example_finder
    _example_viewer
    _time_gap_calculator
    _title_styler
    decomposition_plotter
    experiment_drawer
    figure_canvas_fitter
    gap_space_calculator
    group_collector
    panel_letter_adder
    waterfall_plotter
    """

    # ---- 1 Validate and select the examples ------------------------------------------
    group_order = tuple(config['GROUP_ORDER'])
    if len(group_order) != 2:
        raise ValueError('GROUP_ORDER must list exactly two groups (one column each).')
    if config['WATERFALL_LEGEND_ON'] not in ('all', 'first', 'none'):
        raise ValueError('WATERFALL_LEGEND_ON must be "all", "first" or "none".')
    if len(config['EXAMPLES']) != 2:
        raise ValueError('EXAMPLES must list exactly two (group, hours) examples.')
    if config['PANEL_LETTER_CASE'] not in ('upper', 'lower'):
        raise ValueError('PANEL_LETTER_CASE must be "upper" or "lower".')
    groups = group_collector(experiments, config)
    example_picks = [(group,) + _example_finder(groups, group, hours)
                     for group, hours in config['EXAMPLES']
                     ]
    example_config = {**individual_config,
                      **config.get('EXAMPLE_PLOT_OVERRIDES', {}),
                      'PLOT_AVERAGING_WINDOWS': True,
                      'AVERAGING_WINDOWS_KEY': 'averages',
                      }
    # The short example panels cannot hold a one-line haem label, so it takes two lines
    # (name, then units).
    example_config['HAEM_AXIS_LABELS'] = {key: label.replace(' (', '\n(', 1)
                                          for key, label
                                          in example_config['HAEM_AXIS_LABELS'].items()
                                          }
    label_height = _event_label_height_calculator([experiment
                                                   for _, _, experiment in example_picks
                                                   ],
                                                  example_config,
                                                  )

    # ---- 2 Create the figure grid ----------------------------------------------------
    fig = plt.figure(figsize=config['FIGURE_SIZE'], dpi=config['FIGURE_DPI'])
    row_hspace, column_wspace, row_gap = _time_gap_calculator(config,
                                                              example_config,
                                                              label_height,
                                                              )
    grid = GridSpec(3,
                    2,
                    figure=fig,
                    height_ratios=config['HEIGHT_RATIOS'],
                    width_ratios=config['WIDTH_RATIOS'],
                    hspace=row_hspace,
                    wspace=column_wspace,
                    )
    # The two waterfalls are stacked in the centre of the bottom row, in a quarter of
    # the figure width. The gap between them holds the title of the lower one (and the
    # wavelength axis is written once, under the lower, when they share it).
    # ---- 3 Draw the waterfalls -------------------------------------------------------
    unit = config['UNIT_PT']
    ratios = config['HEIGHT_RATIOS']
    waterfall_row_pt = (config['FIGURE_SIZE'][1] * 72.0 - 6 * unit - 2 * row_gap
                        ) * ratios[2] / sum(ratios)
    stack_gap = 1.2 * config['TITLE_FONT_SIZE'] + 0.8 * unit + 1.0 * unit
    if config['WATERFALL_SHARE_X_AXIS']:
        stack_gap += 0.5 * unit  # the upper panel keeps its tick marks
    else:
        stack_gap += (1.2 * config['TICK_FONT_SIZE'] +
                      1.0 * unit +
                      1.2 * config['AXIS_LABEL_FONT_SIZE']
                      )
    fraction = config['WATERFALL_WIDTH_FRACTION']
    centred = grid[2, :].subgridspec(1,
                                     3,
                                     width_ratios=[(1 - fraction) / 2,
                                                   fraction,
                                                   (1 - fraction) / 2,
                                                   ],
                                     wspace=0,
                                     )
    stacked = centred[0, 1].subgridspec(2,
                                        1,
                                        hspace=gap_space_calculator(stack_gap,
                                                                    waterfall_row_pt,
                                                                    2,
                                                                    ),
                                        )
    axes, panels = {}, []
    for index, group in enumerate(group_order):
        shared = config['WATERFALL_SHARE_X_AXIS'] and index == 1
        ax = fig.add_subplot(stacked[index, 0], sharex=axes['E'] if shared else None)
        _title_styler(ax, config['GROUP_TITLES'].get(group, group), config)
        waterfall_plotter(ax,
                          groups[group],
                          config,
                          show_legend=config['WATERFALL_LEGEND_ON'] == 'all',
                          )
        if config['WATERFALL_SHARE_X_AXIS'] and index == 0:
            ax.set_xlabel('')
            ax.tick_params(axis='x', labelbottom=False)
        axes['EF'[index]] = ax

    # ---- 4 Draw the examples ---------------------------------------------------------
    for row, (group, label, experiment) in enumerate(example_picks):
        known = {id(ax) for ax in fig.axes}
        stack, _ = experiment_drawer(fig,
                                     grid[row, 0],
                                     _example_viewer(experiment),
                                     example_config,
                                     )
        # the panels and the invisible axes that carries the shared label
        members = [ax for ax in fig.axes if id(ax) not in known]
        decomposition_ax = fig.add_subplot(grid[row, 1])
        group_title = config['GROUP_TITLES'].get(group, group)
        title = config['EXAMPLE_TITLE_FORMAT'].format(group=group_title, time=label)
        _title_styler(decomposition_ax, title, config)
        decomposition_plotter(decomposition_ax,
                              experiment['difference_decomposition'],
                              config,
                              )
        left_letter, right_letter = ('AB', 'CD')[row]
        axes[left_letter], axes[right_letter] = stack, decomposition_ax
        panels += [(left_letter, stack[0], members),
                   (right_letter, decomposition_ax, [decomposition_ax]),
                   ]

    # ---- 5 Fit margins and add panel letters -----------------------------------------
    panels = panels + [(letter, axes[letter], [axes[letter]]) for letter in 'EF']
    suptitle = (fig.suptitle(config['FIGURE_TITLE'],
                             fontsize=config['SUPTITLE_FONT_SIZE'],
                             fontweight='bold',
                             )
                if config['FIGURE_TITLE']
                else None
                )
    pad, gap = config['EDGE_PAD_PT'], config['TITLE_GAP_PT']
    figure_canvas_fitter(fig, pad, suptitle, gap)
    if config['WATERFALL_LEGEND_ON'] == 'first':
        # One legend in the white space right of the waterfalls, centred vertically
        # on the gap between them (in the upper axes' coordinates).
        upper, lower = axes['E'].get_position(), axes['F'].get_position()
        centre = (upper.y0 + lower.y1) / 2
        _legend_drawer(axes['E'],
                       config,
                       'center left',
                       config['WATERFALL_LEGEND_COLUMNS'],
                       anchor=(1.03, (centre - upper.y0) / upper.height),
                       )
    if config['PANEL_LETTERS']:
        panel_letter_adder(fig,
                           panels,
                           config['PANEL_LETTER_FONT_SIZE'],
                           config['PANEL_LETTER_CASE'],
                           )
    figure_canvas_fitter(fig, pad, suptitle, gap)
    return fig, axes


# ---- TIME RESPONSE FIGURE SAVER ------------------------------------------------------
def time_response_figure_saver(fig: Figure, export_root: Path, config: dict) -> list:
    """
    ---- Summary ----
    Main function to save the time response figure at its exact size.

    ---- Inputs ----
    fig : Figure
        Figure returned by time_response_figure_plotter.
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
    None. Writes files (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    figure_saver
    """

    # ---- 1 Save the figure -----------------------------------------------------------
    folder = Path(export_root) / config['OUTPUT_SUBFOLDER']
    paths = figure_saver(fig,
                         folder,
                         config['FILE_NAME'],
                         config['SAVE_FORMATS'],
                         config['FIGURE_SIZE'],
                         config['FIGURE_DPI'],
                         tight=config['TIGHT_BBOX'],
                         )

    # ---- 2 Report the export ---------------------------------------------------------
    print(f"  {config['FILE_NAME']} saved: {folder.relative_to(Path(export_root))}")
    return paths


# ---- WATERFALL PLOTTER ---------------------------------------------------------------
def waterfall_plotter(ax: Axes,
                      items: list,
                      config: dict,
                      show_legend: bool = True,
                      ) -> None:
    """
    ---- Summary ----
    Main function to draw the offset difference spectra of one group, first time point
    at the top, with additive peak alignment.

    ---- Inputs ----
    ax : Axes
        Matplotlib axes to draw on.
    items : list
        [(time label, experiment), ...] of one group.
    config : dict
        Figure settings dictionary built in custom_config.py.
    show_legend : bool
        True to draw the legend.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Draws on ``ax`` (side effect).

    ---- Equations ----
    aligned = S + (1 - max of S within [ALIGN_MIN, ALIGN_MAX]); shifted_i = aligned_i -
    min(aligned_i) + (n - 1 - i) x offset; offset defaults to 0.75 x the largest span.

    ---- Helpers ----
    _haem_window_drawer
    _legend_drawer
    _time_axes_styler
    shared_baseline_subtracter
    """

    # ---- 1 Collect the spectra -------------------------------------------------------
    wavelengths = [item[1]['difference_spectrum']['wavelengths'] for item in items]
    spectra = [item[1]['difference_spectrum']['spectrum'] for item in items]
    labels = [item[0] for item in items]
    n_points = len(spectra)

    # ---- 2 Align the peaks -----------------------------------------------------------
    align_min, align_max = config['ALIGN_MIN'], config['ALIGN_MAX']
    if align_min is not None and align_max is not None and align_min >= align_max:
        raise ValueError('ALIGN_MIN must be smaller than ALIGN_MAX.')
    if config['WATERFALL_SHARED_BASELINE']:
        if len({len(w) for w in wavelengths}) != 1:
            raise ValueError('WATERFALL_SHARED_BASELINE needs every spectrum on the '
                             'same wavelength grid.',
                             )
        corrected, _ = shared_baseline_subtracter(np.column_stack(wavelengths),
                                                  np.column_stack(spectra),
                                                  config['WATERFALL_BASELINE_X_MIN'],
                                                  config['WATERFALL_BASELINE_X_MAX'],
                                                  config['WATERFALL_BASELINE_DEGREE'],
                                                  )
        spectra = [corrected[:, i] for i in range(n_points)]
    # Additive alignment: the maximum within the alignment window is shifted to 1; shape
    # and scale are preserved.
    in_range, aligned = [], []
    for w, s in zip(wavelengths, spectra):
        mask = np.ones(w.shape, dtype=bool)
        if align_min is not None:
            mask &= w >= align_min
        if align_max is not None:
            mask &= w <= align_max
        if not mask.any():
            raise ValueError('The alignment range contains no data for at least one '
                             'spectrum.',
                             )
        in_range.append(mask)
        aligned.append(s + (1.0 - np.max(s[mask])))
    minima = np.array([np.min(a[m]) for a, m in zip(aligned, in_range)])
    maxima = np.array([np.max(a[m]) for a, m in zip(aligned, in_range)])
    maximum_span = np.max(maxima - minima)

    # ---- 3 Offset and draw -----------------------------------------------------------
    offset = config['WATERFALL_OFFSET']
    if offset is None:
        offset = maximum_span * 0.75 if maximum_span > 0 else 1.0
    if offset <= 0:
        raise ValueError('WATERFALL_OFFSET must be positive.')
    x_min, x_max = config['X_MIN'], config['X_MAX']
    displayed = []
    for i in range(n_points):
        shifted = aligned[i] - minima[i] + (n_points - 1 - i) * offset
        ax.plot(wavelengths[i],
                shifted,
                label=labels[i],
                linewidth=config['LINE_WIDTH'],
                )
        keep = np.ones(len(shifted), dtype=bool)
        if x_min is not None:
            keep &= wavelengths[i] >= x_min
        if x_max is not None:
            keep &= wavelengths[i] <= x_max
        displayed.extend(shifted[keep])
    if x_min is not None or x_max is not None:
        ax.set_xlim(left=x_min, right=x_max)
    # ---- 4 Style the axes ------------------------------------------------------------
    ax.set_xlabel('Wavelength (nm)', fontsize=config['AXIS_LABEL_FONT_SIZE'])
    ax.set_ylabel(config['WATERFALL_Y_LABEL'], fontsize=config['AXIS_LABEL_FONT_SIZE'])
    _time_axes_styler(ax, config)
    ax.set_yticks([])
    _haem_window_drawer(ax, items[0][1]['difference_decomposition'], config)
    if show_legend:
        _legend_drawer(ax,
                       config,
                       config['WATERFALL_LEGEND_LOCATION'],
                       config['WATERFALL_LEGEND_COLUMNS'],
                       outside=config['WATERFALL_LEGEND_OUTSIDE'],
                       )
    if displayed:
        low, high = np.min(displayed), np.max(displayed)
        padding = (high - low) * 0.01 if high > low else 0.05
        ax.set_ylim(low - padding, high + padding)
