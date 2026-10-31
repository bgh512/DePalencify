"""
Processing and drawing of one experiment as a preview figure.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import copy
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Optional, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_shared.experiment_processing import experiment_data_processor
from utils_shared.individual_experiment_plotter import experiment_plotter
from utils_shared.paf_reader import experiment_paf_loader


# ---- CONSTANTS -----------------------------------------------------------------------
PREVIEW_DPI = 200
MAX_CACHED_FILES = 3
# Size of the preview while browsing, trimming and checking the analysis (the journal
# size is used once the journal has been chosen).
BROWSING_ANSWERS = {'journal': 'nature',
                    'columns': 2,
                    'height': 0.6,
                    'size_mode': 'custom',
                    }
TRIM_COLOUR = '0.45'
IGNORE_COLOUR = '#e8a317'


# ---- PreviewSpec ---------------------------------------------------------------------
@dataclass
class PreviewSpec:
    """
    ---- Summary ----
    The settings a preview is drawn with: the answers given so far. Every file is drawn
    with the same spec, so the files can be compared.
    Detailed structure can be found in DATA_FORMAT.md.
    """

    answers: dict
    limits: dict
    fit: Optional[dict]
    details: dict
    show_trim: bool = False
    show_ignored: bool = True


# ---- ViewerSession -------------------------------------------------------------------
@dataclass
class ViewerSession:
    """
    ---- Summary ----
    Everything the experiment browser keeps between steps: the files, the window and the
    recently read experiments.
    Detailed structure can be found in DATA_FORMAT.md.
    """

    summaries: List[dict]
    export_root: Path
    window: Any
    current: int = 0
    cache: OrderedDict = field(default_factory=OrderedDict)


# ---- PREVIEW HELPERS -----------------------------------------------------------------


# ---- _info_builder -------------------------------------------------------------------
def _info_builder(summary: dict, limits: dict, details: dict) -> dict:
    """
    ---- Summary ----
    Helper function to build the per-file information dictionary that
    experiment_data_processor needs, from the answers given so far.

    ---- Inputs ----
    summary : dict
        File summary (DATA_FORMAT.md).
    limits : dict
        {file name: {trim_start, trim_end, ignore_start, ignore_end}} in minutes; may
        lack the file.
    details : dict
        {file name: {OD, volume, dilution_factor, events}}; may lack the file.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        Per-file information (as built in everything_asker).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    name = summary['name']
    own = limits.get(name, {})
    info = {'path': summary['path'],
            'name': name,
            'duration': summary['duration_min'],
            'trim_start': own.get('trim_start'),
            'trim_end': own.get('trim_end'),
            'ignore_start': own.get('ignore_start') or 0.0,
            'ignore_end': own.get('ignore_end') or 0.0,
            }
    info.update(details.get(name, {}))
    return info


# ---- _loaded_experiment_getter -------------------------------------------------------
def _loaded_experiment_getter(session: ViewerSession,
                              summary: dict,
                              dataset: Optional[str],
                              ) -> dict:
    """
    ---- Summary ----
    Helper function to give a fresh copy of an experiment read from its file. The file
    is read once and kept for the next previews (the last few files only), and read
    again when the spectra of a dataset are needed that were not read before.

    ---- Inputs ----
    session : ViewerSession
        The browser session holding the cache.
    summary : dict
        File summary (DATA_FORMAT.md).
    dataset : Optional[str]
        Spectral dataset needed for the haem decomposition, or None for no spectra.

    ---- Globals read ----
    MAX_CACHED_FILES (module constant).

    ---- Outputs ----
    dict
        A deep copy of the experiment dictionary, safe to trim and process in place.

    ---- Globals mutated ----
    None. Updates the cache of the session (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    experiment_paf_loader
    """

    # ---- 1 Read the file if it is not cached -----------------------------------------
    name = summary['name']
    entry = session.cache.get(name)
    if entry is None or (dataset and dataset not in entry['experiment']['raw_spectra']):
        experiment = experiment_paf_loader(summary['path'],
                                           spectral_datasets=((dataset,)
                                                              if dataset
                                                              else ()
                                                              ),
                                           )
        entry = {'experiment': experiment}
        session.cache[name] = entry
    session.cache.move_to_end(name)
    while len(session.cache) > MAX_CACHED_FILES:
        session.cache.popitem(last=False)

    # ---- 2 Hand out a copy -----------------------------------------------------------
    return copy.deepcopy(entry['experiment'])


# ---- _overlay_drawer -----------------------------------------------------------------
def _overlay_drawer(fig: Figure,
                    axes: list,
                    regions: list,
                    note: str,
                    ) -> None:
    """
    ---- Summary ----
    Helper function to shade regions of the time axis on every panel of the preview.

    ---- Inputs ----
    fig : Figure
        The preview figure.
    axes : list
        Panels of the preview, top to bottom.
    regions : list
        [(start_min, end_min, kind)] with kind 'trim' (grey hatched) or 'ignore'
        (amber).
    note : str
        Short explanation of the shading, written in the corner of the figure; may be
        empty.

    ---- Globals read ----
    IGNORE_COLOUR, TRIM_COLOUR (module constants).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Adds shaded regions and the note to the figure (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    for start, end, kind in regions:
        if end <= start:
            continue
        for ax in axes:
            if kind == 'trim':
                ax.axvspan(start, end, facecolor=TRIM_COLOUR, alpha=0.25, hatch='///',
                           edgecolor=TRIM_COLOUR, linewidth=0, zorder=1)
            else:
                ax.axvspan(start, end, facecolor=IGNORE_COLOUR, alpha=0.22,
                           linewidth=0, zorder=1)
    if note:
        mark = fig.text(0.995, 0.005, note, ha='right', va='bottom', fontsize=6,
                        color='0.35', alpha=0.9)
        mark.set_in_layout(False)


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- preview_drawer ------------------------------------------------------------------
def preview_drawer(session: ViewerSession,
                   answers: dict,
                   limits: dict,
                   fit: Optional[dict],
                   details: dict,
                   show_trim: bool = False,
                   show_ignored: bool = True,
                   name: Optional[str] = None,
                   ) -> bool:
    """
    ---- Summary ----
    Main function to show the answers given so far in the window. A window with its own
    controls (the experiment browser window) is given the settings and draws every file
    the user looks at with them; otherwise the current file is drawn and saved as a
    picture. Problems are reported, never raised, so the questions carry on.

    ---- Inputs ----
    session : ViewerSession
        The browser session (files, window, cache, current file).
    answers : dict
        Answers so far; missing keys come from config.DEFAULT_ANSWERS.
    limits : dict
        {file name: {trim_start, trim_end, ignore_start, ignore_end}} in minutes.
    fit : Optional[dict]
        Fit dictionary from fit_importer, or None.
    details : dict
        {file name: {OD, volume, dilution_factor, events}}.
    show_trim : bool
        True to draw the whole recording and shade the part that would be trimmed, so
        the trim limits can be judged. False draws the trimmed data.
    show_ignored : bool
        True to shade the ignored start and end in amber.
    name : Optional[str]
        File to show; None keeps the file being looked at.

    ---- Globals read ----
    None.

    ---- Outputs ----
    bool
        True when the preview was drawn (or handed to the window), False when it could
        not be.

    ---- Globals mutated ----
    None. Draws in the window or writes the preview picture (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    preview_figure_builder
    """

    # ---- 1 Collect the settings ------------------------------------------------------
    spec = PreviewSpec(answers=dict(answers),
                       limits=copy.deepcopy(limits),
                       fit=fit,
                       details=copy.deepcopy(details),
                       show_trim=show_trim,
                       show_ignored=show_ignored,
                       )

    # ---- 2 Hand them to the window or draw one picture -------------------------------
    if session.window.is_interactive:
        session.window.spec_publisher(spec, name)
        return True
    figure, notes = preview_figure_builder(
        session,
        spec,
        name or session.summaries[session.current]['name'],
    )
    if notes:
        print('\n'.join(f'  {line}' for line in notes.splitlines()))
    if figure is None:
        return False
    session.window.figure_shower(figure)
    return True


# ---- preview_figure_builder ----------------------------------------------------------
def preview_figure_builder(session: ViewerSession,
                           spec: PreviewSpec,
                           name: str,
                           ) -> Tuple[Optional[Figure], str]:
    """
    ---- Summary ----
    Main function to process one file with the answers of a spec and draw it in a new
    figure. Problems are reported, never raised.

    ---- Inputs ----
    session : ViewerSession
        The browser session (files, window, cache).
    spec : PreviewSpec
        The settings to draw with.
    name : str
        Name of the file to draw.

    ---- Globals read ----
    settings.Config; PREVIEW_DPI (module constant).

    ---- Outputs ----
    Tuple[Optional[Figure], str]
        (figure, notes). The figure is None when the preview could not be drawn, and
        the notes then say why. Otherwise the notes are the warnings of the processing
        (a skipped step, a missing OD), one per line, and may be empty.

    ---- Globals mutated ----
    None. Sets the matplotlib rcParams of the figure style (side effect). Nothing is
    printed; the caller decides where the notes go.

    ---- Equations ----
    None.

    ---- Helpers ----
    _info_builder
    _loaded_experiment_getter
    _overlay_drawer
    """

    # ---- 1 Set up the file and the settings ------------------------------------------
    summary = next(s for s in session.summaries if s['name'] == name)
    own = spec.limits.get(name, {})
    info = _info_builder(summary, {name: {} if spec.show_trim else own}, spec.details)
    preview_answers = dict(settings.DEFAULT_ANSWERS,
                           **dict(spec.answers, export_spectra=False),
                           )
    cfg = settings.Config(preview_answers)
    plt.rcParams.update(cfg.RC_PARAMS)

    # ---- 2 Process the data and draw the figure --------------------------------------
    needs_dataset = preview_answers['decompose'] and spec.fit is not None
    fig = Figure(dpi=PREVIEW_DPI)
    try:
        with session.window.output_capturer() as buffer:
            experiment = _loaded_experiment_getter(session,
                                                   summary,
                                                   preview_answers[
                                                       'decomposition_dataset']
                                                   if needs_dataset
                                                   else None,
                                                   )
            processed = experiment_data_processor(info, cfg, spec.fit, experiment)
            experiment = processed['experiment']
            haem_panels = preview_answers['plot_haems'] and 'haem_conc' in experiment
            plot_config = cfg.plot_config_builder(processed['vo2_source'],
                                                  processed['haem_source']
                                                  if haem_panels
                                                  else None,
                                                  info['ignore_start'],
                                                  info['ignore_end'],
                                                  )
            plot_config.update({'SAVE_FIGURES': False,
                                'SHOW_INDIVIDUAL_FIGURES': False,
                                'FIGURE_DPI': PREVIEW_DPI,
                                })
            _, axes = experiment_plotter(experiment,
                                         plot_config,
                                         session.export_root,
                                         fig=fig,
                                         )
    except Exception as exc:  # a preview problem must never stop the questions
        return None, f'Preview not drawn for {name}: {type(exc).__name__}: {exc}'
    notes = '\n'.join(line.strip()
                      for line in buffer.getvalue().splitlines()
                      if any(word in line for word in ('Warning', 'skipped', 'Not '))
                      )

    # ---- 3 Shade the trimmed and ignored parts ---------------------------------------
    regions = []
    duration = float(experiment['CcO2'].iloc[-1, 0])
    start = (own.get('trim_start') or 0.0) if spec.show_trim else 0.0
    end = ((own.get('trim_end') or summary['duration_min'])
           if spec.show_trim
           else duration
           )
    if spec.show_trim:
        regions += [(0.0, start, 'trim'), (end, summary['duration_min'], 'trim')]
    if spec.show_ignored:
        regions += [(start, start + (own.get('ignore_start') or 0.0), 'ignore'),
                    (end - (own.get('ignore_end') or 0.0), end, 'ignore'),
                    ]
    note = ''
    if spec.show_trim:
        note = 'grey hatched = trimmed away, amber = ignored in calculations'
    elif spec.show_ignored and any(r[2] == 'ignore' and r[1] > r[0] for r in regions):
        note = 'amber = ignored in calculations'
    _overlay_drawer(fig, axes, regions, note)
    return fig, notes
