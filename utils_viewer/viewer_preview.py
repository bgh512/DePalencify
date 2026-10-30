"""
Processing and drawing of one experiment as a preview in the plot window.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import contextlib
import copy
import io
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import matplotlib.pyplot as plt

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_shared.experiment_processing import experiment_data_processor
from utils_shared.individual_experiment_plotter import experiment_plotter
from utils_shared.paf_reader import experiment_paf_loader
from utils_viewer.viewer_window import PREVIEW_DPI, ViewerWindow


# ---- CONSTANTS -----------------------------------------------------------------------
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


# ---- ViewerSession -------------------------------------------------------------------
@dataclass
class ViewerSession:
    """
    ---- Summary ----
    Everything the experiment browser keeps between steps: the files, the plot window
    and the recently read experiments.
    Detailed structure can be found in DATA_FORMAT.md.
    """

    summaries: List[dict]
    export_root: Path
    window: ViewerWindow
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


# ---- _overlay_drawer -----------------------------------------------------------------
def _overlay_drawer(fig: object,
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
    Main function to process one file with the answers given so far and draw it in the
    plot window. Problems are reported, never raised, so the questions carry on.

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
        File to draw; None draws the current file of the session.

    ---- Globals read ----
    settings.Config; PREVIEW_DPI (module constant).

    ---- Outputs ----
    bool
        True when the preview was drawn, False when it could not be.

    ---- Globals mutated ----
    None. Draws in the plot window and prints warnings (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _info_builder
    _loaded_experiment_getter
    _overlay_drawer
    """

    # ---- 1 Set up the file and the settings ------------------------------------------
    summary = (session.summaries[session.current]
               if name is None
               else next(s for s in session.summaries if s['name'] == name)
               )
    own = limits.get(summary['name'], {})
    shown_limits = {summary['name']: {} if show_trim else own}
    info = _info_builder(summary, shown_limits, details)
    preview_answers = dict(settings.DEFAULT_ANSWERS,
                           **dict(answers, export_spectra=False),
                           )
    cfg = settings.Config(preview_answers)
    plt.rcParams.update(cfg.RC_PARAMS)

    # ---- 2 Process the data ----------------------------------------------------------
    needs_dataset = preview_answers['decompose'] and fit is not None
    buffer = io.StringIO()
    try:
        experiment = _loaded_experiment_getter(session,
                                               summary,
                                               preview_answers['decomposition_dataset']
                                               if needs_dataset
                                               else None,
                                               )
        with contextlib.redirect_stdout(buffer):
            processed = experiment_data_processor(info, cfg, fit, experiment)
    except Exception as exc:  # a preview problem must never stop the questions
        print(f"  Preview not drawn for {summary['name']}: {type(exc).__name__}: {exc}")
        return False
    for line in buffer.getvalue().splitlines():
        if any(word in line for word in ('Warning', 'skipped', 'Not ')):
            print(line)

    # ---- 3 Draw the figure -----------------------------------------------------------
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
    try:
        fig = session.window.figure_getter()
        with contextlib.redirect_stdout(io.StringIO()):
            _, axes = experiment_plotter(experiment,
                                         plot_config,
                                         session.export_root,
                                         fig=fig,
                                         )
    except Exception as exc:
        print(f"  Preview not drawn for {summary['name']}: {type(exc).__name__}: {exc}")
        return False

    # ---- 4 Shade the trimmed and ignored parts ---------------------------------------
    regions = []
    duration = float(experiment['CcO2'].iloc[-1, 0])
    start = (own.get('trim_start') or 0.0) if show_trim else 0.0
    end = ((own.get('trim_end') or summary['duration_min'])
           if show_trim
           else duration
           )
    if show_trim:
        regions += [(0.0, start, 'trim'), (end, summary['duration_min'], 'trim')]
    if show_ignored:
        regions += [(start, start + (own.get('ignore_start') or 0.0), 'ignore'),
                    (end - (own.get('ignore_end') or 0.0), end, 'ignore'),
                    ]
    note = ''
    if show_trim:
        note = 'grey hatched = trimmed away, amber = ignored in calculations'
    elif show_ignored and any(r[2] == 'ignore' and r[1] > r[0] for r in regions):
        note = 'amber = ignored in calculations'
    _overlay_drawer(fig, axes, regions, note)

    # ---- 5 Show it -------------------------------------------------------------------
    session.window.window_refresher()
    return True
