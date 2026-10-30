"""
The steps of the experiment browser: ask, redraw the plot window, then accept or repeat.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import tempfile
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.questions import (choice_asker,
                                    heading_printer,
                                    info_printer,
                                    numbering_getter,
                                    numbering_setter,
                                    section_starter,
                                    )
from utils_shared.survey import (averaging_asker,
                                 decomposition_asker,
                                 event_asker,
                                 od_scaling_asker,
                                 plot_asker,
                                 saved_values_reader,
                                 trim_asker,
                                 )
from utils_viewer.viewer_preview import (BROWSING_ANSWERS,
                                         preview_drawer,
                                         ViewerSession,
                                         )
from utils_viewer.viewer_window import ViewerWindow


# ---- CONSTANTS -----------------------------------------------------------------------
PREVIEW_FILE = Path(tempfile.gettempdir()) / 'DePalencify_preview.png'
STAGE_TITLES = {'browser': 'Experiment browser',
                'trim': 'Trimming and ignoring',
                'analysis': 'Analysis',
                'plots': 'Individual experiment plots',
                }


# ---- STAGE HELPERS -------------------------------------------------------------------


# ---- _answers_previewer --------------------------------------------------------------
def _answers_previewer(answers: dict, fit: Optional[dict], kind: str) -> dict:
    """
    ---- Summary ----
    Helper function to build the answers used to draw a preview: the raw data while
    browsing and trimming, and the analysis chosen so far afterwards.

    ---- Inputs ----
    answers : dict
        Answers given so far.
    fit : Optional[dict]
        Fit dictionary, used to list the haems to show.
    kind : str
        'raw' (O2 and the raw OCR only), 'analysis' (also the haems and the OD scaling
        chosen so far, in a wide preview) or 'final' (exactly as the figure will be).

    ---- Globals read ----
    BROWSING_ANSWERS (module constant).

    ---- Outputs ----
    dict
        A copy of the answers with the preview settings; ``answers`` is not changed.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    result = dict(answers)
    if kind == 'final':
        return result
    result.update(BROWSING_ANSWERS)
    result.update({'plot_o2': True, 'plot_ocr': True, 'plot_haems': False})
    if kind == 'raw':
        result.update({'decompose': False,
                       'normalise_od': False,
                       'averaging': False,
                       'ocr_mode': 'raw',
                       })
        return result
    result['ocr_mode'] = 'od' if result['normalise_od'] else 'raw'
    if result['decompose'] and fit is not None:
        result.update({'plot_haems': True,
                       'haems': list(fit['haem_list']),
                       'haem_mode': 'delta',
                       'haem_per_od': bool(result['normalise_od']),
                       })
    return result


# ---- _file_chooser -------------------------------------------------------------------
def _file_chooser(session: ViewerSession) -> None:
    """
    ---- Summary ----
    Helper function to ask which file to look at and make it the current one.

    ---- Inputs ----
    session : ViewerSession
        The browser session; its current file is changed.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Sets session.current and reads from and prints to the terminal (side
    effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    choice_asker
    """

    options = [(str(number), summary['name'])
               for number, summary in enumerate(session.summaries)
               ]
    chosen = choice_asker('Which file would you like to look at?',
                          options,
                          str(session.current),
                          )
    session.current = int(chosen)


# ---- _limits_lister ------------------------------------------------------------------
def _limits_lister(summaries: List[dict], limits: Dict[str, dict]) -> None:
    """
    ---- Summary ----
    Helper function to print the trim and ignore limits of every file in one list.

    ---- Inputs ----
    summaries : List[dict]
        File summaries (DATA_FORMAT.md).
    limits : Dict[str, dict]
        {file name: {trim_start, trim_end, ignore_start, ignore_end}} in minutes.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Prints to the terminal (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    info_printer
    """

    info_printer('Limits (minutes):')
    for summary in summaries:
        v = limits[summary['name']]
        start = 'from 0' if not v['trim_start'] else f"from {v['trim_start']:g}"
        end = ('to the end'
               if v['trim_end'] is None
               else f"to {v['trim_end']:g}"
               )
        info_printer(f"  {summary['name']}: keep {start} {end}; ignore the first "
                     f"{v['ignore_start']:g} and the last {v['ignore_end']:g}",
                     )


# ---- _review_asker -------------------------------------------------------------------
def _review_asker(session: ViewerSession,
                  question: str,
                  change_label: str,
                  redraw: Callable[[], bool],
                  ) -> bool:
    """
    ---- Summary ----
    Helper function to ask whether the user accepts what the plot window shows. The user
    can also look at another file, which redraws the window, before deciding.

    ---- Inputs ----
    session : ViewerSession
        The browser session; its current file may be changed.
    question : str
        The accept question, for example 'Do you accept these limits?'.
    change_label : str
        Label of the answer that asks the questions of the step again.
    redraw : Callable[[], bool]
        Function that draws the preview of the current file.

    ---- Globals read ----
    None.

    ---- Outputs ----
    bool
        True when accepted, False when the user wants to answer the step again.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal and redraws the window (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _file_chooser
    choice_asker
    """

    options = [('yes', 'Yes, accept'),
               ('no', change_label),
               ]
    if len(session.summaries) > 1:
        options.append(('file', 'Look at another file in the plot window first'))
    while True:
        choice = choice_asker(question, options, 'yes')
        if choice == 'yes':
            return True
        if choice == 'no':
            return False
        _file_chooser(session)
        redraw()


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- analysis_stage_runner -----------------------------------------------------------
def analysis_stage_runner(session: ViewerSession,
                          answers: dict,
                          defaults: dict,
                          limits: Dict[str, dict],
                          fits_folder: Path,
                          details_before: Optional[Dict[str, dict]] = None,
                          ) -> Tuple[Optional[dict], Dict[str, dict]]:
    """
    ---- Summary ----
    Main function to ask the analysis questions (haem decomposition, OD scaling, event
    averaging and event labels) one at a time, redrawing the plot window after each so
    the result can be accepted or asked again.

    ---- Inputs ----
    session : ViewerSession
        The browser session.
    answers : dict
        Answers dictionary the values are stored in.
    defaults : dict
        Default answers offered by the questions.
    limits : Dict[str, dict]
        Trim and ignore limits of every file (trim_asker).
    fits_folder : Path
        Folder holding the fit .csv files.
    details_before : Optional[Dict[str, dict]]
        OD values and events from an earlier pass, offered as defaults when the step is
        asked again.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Tuple[Optional[dict], Dict[str, dict]]
        (fit, details) exactly as analysis_asker returns them.

    ---- Globals mutated ----
    None. Stores the answers in ``answers`` (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _answers_previewer
    _review_asker
    averaging_asker
    decomposition_asker
    event_asker
    od_scaling_asker
    preview_drawer
    saved_values_reader
    """

    summaries = session.summaries
    details: Dict[str, dict] = {s['name']: {} for s in summaries}
    fit: Optional[dict] = None
    saved = saved_values_reader(summaries, session.export_root)
    for name, values in (details_before or {}).items():
        saved[name] = dict(saved.get(name) or {}, **values)
    answers.update({'decompose': False, 'normalise_od': False, 'averaging': False})

    def redraw() -> bool:
        return preview_drawer(session,
                              _answers_previewer(answers, fit, 'analysis'),
                              limits,
                              fit,
                              details,
                              )

    # ---- 1 Decomposition -------------------------------------------------------------
    while True:
        (answers['decompose'],
         answers['fit_file'],
         fit,
         answers['decomposition_dataset'],
         ) = decomposition_asker(summaries, defaults, fits_folder)
        if not answers['decompose']:
            break
        redraw()
        if _review_asker(session,
                         'Do you accept this decomposition?',
                         'No, choose the fit again',
                         redraw,
                         ):
            break
        defaults = dict(defaults, decompose=True, fit_file=answers['fit_file'])

    # ---- 2 OD scaling ----------------------------------------------------------------
    while True:
        details = od_scaling_asker(summaries, answers, defaults, saved)
        if not answers['normalise_od']:
            break
        redraw()
        if _review_asker(session,
                         'Do you accept this OD scaling?',
                         'No, enter the OD values again',
                         redraw,
                         ):
            break
        defaults = dict(defaults, normalise_od=True)
        for name, values in details.items():
            saved[name] = dict(saved.get(name) or {}, **values)

    # ---- 3 Averaging -----------------------------------------------------------------
    while True:
        averaging_asker(answers, defaults)
        if not answers['averaging']:
            break
        redraw()
        if _review_asker(session,
                         'Do you accept these averaging windows?',
                         'No, change the window and gap',
                         redraw,
                         ):
            break
        defaults = dict(defaults, averaging=True)
        defaults.update({k: answers[k] for k in ('window_minutes', 'gap_minutes')})

    # ---- 4 Event labels --------------------------------------------------------------
    while True:
        for name, events in event_asker(summaries, saved).items():
            details[name]['events'] = events
            saved[name] = dict(saved.get(name) or {}, events=events)
        redraw()
        if _review_asker(session,
                         'Do you accept these event labels?',
                         'No, change the labels again',
                         redraw,
                         ):
            break
    return fit, details


# ---- browser_stage_runner ------------------------------------------------------------
def browser_stage_runner(session: ViewerSession, answers: dict) -> None:
    """
    ---- Summary ----
    Main function to let the user look through the files in the plot window (the set and
    measured O2 and the OCR, with the events) before answering any questions about
    them.

    ---- Inputs ----
    session : ViewerSession
        The browser session; its current file is changed.
    answers : dict
        Answers so far, used for the figure style of the preview.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal and draws the plot window (side
    effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _answers_previewer
    _file_chooser
    choice_asker
    info_printer
    preview_drawer
    """

    options = [('next', 'Next file'),
               ('previous', 'Previous file'),
               ('goto', 'Go to a specific file'),
               ('continue', 'Continue to trimming and ignoring'),
               ]
    total = len(session.summaries)
    while True:
        summary = session.summaries[session.current]
        preview_drawer(session,
                       _answers_previewer(answers, None, 'raw'),
                       {},
                       None,
                       {},
                       show_ignored=False,
                       )
        info_printer(f"\nCurrent file: {session.current + 1} of {total}")
        info_printer(f"Filename: {summary['name']} ({summary['duration_min']:.1f} "
                     f"min, {len(summary['events'])} event(s))",
                     )
        choice = choice_asker('What would you like to do?', options, 'continue')
        if choice == 'continue':
            return
        if choice == 'goto':
            _file_chooser(session)
        elif choice == 'next' and session.current + 1 < total:
            session.current += 1
        elif choice == 'previous' and session.current > 0:
            session.current -= 1
        else:
            info_printer('There is no file in that direction.')


# ---- plots_stage_runner --------------------------------------------------------------
def plots_stage_runner(session: ViewerSession,
                       answers: dict,
                       defaults: dict,
                       limits: Dict[str, dict],
                       fit: Optional[dict],
                       details: Dict[str, dict],
                       ) -> bool:
    """
    ---- Summary ----
    Main function to ask what the individual figures show and how they are sized, then
    draw the figure as it will be saved and ask whether to accept it.

    ---- Inputs ----
    session : ViewerSession
        The browser session.
    answers : dict
        Answers dictionary the values are stored in.
    defaults : dict
        Default answers offered by the questions.
    limits : Dict[str, dict]
        Trim and ignore limits of every file.
    fit : Optional[dict]
        Fit dictionary, or None.
    details : Dict[str, dict]
        OD values and events of every file.

    ---- Globals read ----
    None.

    ---- Outputs ----
    bool
        True when at least one panel is plotted (as plot_asker returns it).

    ---- Globals mutated ----
    None. Stores the answers in ``answers`` (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _answers_previewer
    _review_asker
    plot_asker
    preview_drawer
    """

    def redraw() -> bool:
        return preview_drawer(session,
                              _answers_previewer(answers, fit, 'final'),
                              limits,
                              fit,
                              details,
                              show_ignored=False,
                              )

    while True:
        plotted = plot_asker(answers, defaults, fit)
        if not plotted:
            return False
        redraw()
        if _review_asker(session,
                         'Do you accept this figure?',
                         'No, change what is plotted or its size',
                         redraw,
                         ):
            return plotted
        defaults = dict(answers)


# ---- trim_stage_runner ---------------------------------------------------------------
def trim_stage_runner(session: ViewerSession,
                      answers: dict,
                      remembered: Dict[str, dict],
                      ) -> Dict[str, dict]:
    """
    ---- Summary ----
    Main function to ask the trim and ignore questions, shade the trimmed and ignored
    parts in the plot window, and ask whether to accept them.

    ---- Inputs ----
    session : ViewerSession
        The browser session.
    answers : dict
        Answers so far, used for the figure style of the preview.
    remembered : Dict[str, dict]
        {file name: {trim_start, trim_end, ignore_start, ignore_end}} offered as the
        defaults (from the last run, or from the previous attempt).

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, dict]
        The limits of every file, exactly as trim_asker returns them.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal and draws the plot window (side
    effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _answers_previewer
    _limits_lister
    _review_asker
    preview_drawer
    trim_asker
    """

    while True:
        limits = trim_asker(session.summaries, remembered)
        _limits_lister(session.summaries, limits)

        def redraw() -> bool:
            return preview_drawer(session,
                                  _answers_previewer(answers, None, 'raw'),
                                  limits,
                                  None,
                                  {},
                                  show_trim=True,
                                  )

        redraw()
        if _review_asker(session,
                         'Do you accept these limits?',
                         'No, enter the limits again',
                         redraw,
                         ):
            return limits
        remembered = dict(remembered, **limits)


# ---- viewer_asker --------------------------------------------------------------------
def viewer_asker(summaries: List[dict],
                 answers: dict,
                 defaults: dict,
                 remembered: Dict[str, dict],
                 fits_folder: Path,
                 export_root: Path,
                 ) -> Tuple[Dict[str, dict], Optional[dict], Dict[str, dict], bool]:
    """
    ---- Summary ----
    Main function to ask the questions of the experiment browser: the file browser,
    trimming and ignoring, the analysis and the individual figures. The plot window is
    redrawn after each answer, and at the end any step can be gone back to.

    ---- Inputs ----
    summaries : List[dict]
        File summaries (DATA_FORMAT.md).
    answers : dict
        Answers dictionary the values are stored in.
    defaults : dict
        Default answers offered by the questions.
    remembered : Dict[str, dict]
        {file name: limits} from the last run.
    fits_folder : Path
        Folder holding the fit .csv files.
    export_root : Path
        Results folder.

    ---- Globals read ----
    PREVIEW_FILE, STAGE_TITLES (module constants).

    ---- Outputs ----
    Tuple[Dict[str, dict], Optional[dict], Dict[str, dict], bool]
        (limits, fit, details, plotted) as the same questions return them when they are
        asked without the browser.

    ---- Globals mutated ----
    None. Stores the answers in ``answers``, reads from and prints to the terminal,
    draws and closes the plot window (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    analysis_stage_runner
    browser_stage_runner
    choice_asker
    heading_printer
    numbering_getter
    numbering_setter
    plots_stage_runner
    section_starter
    trim_stage_runner
    """

    session = ViewerSession(summaries, export_root, ViewerWindow(PREVIEW_FILE))
    state: dict = {}

    # ---- run_browser -----------------------------------------------------------------
    def run_browser() -> None:
        browser_stage_runner(session, answers)

    def run_trim() -> None:
        old = state.get('limits') or remembered
        state['limits'] = trim_stage_runner(session, answers, old)
        answers['ignore_first_minutes'] = max(v['ignore_start']
                                              for v in state['limits'].values()
                                              )
        answers['ignore_last_minutes'] = max(v['ignore_end']
                                             for v in state['limits'].values()
                                             )

    def run_analysis() -> None:
        old_defaults = dict(answers) if state.get('fit_asked') else defaults
        state['fit'], state['details'] = analysis_stage_runner(session,
                                                               answers,
                                                               old_defaults,
                                                               state['limits'],
                                                               fits_folder,
                                                               state.get('details'),
                                                               )
        state['fit_asked'] = True

    def run_plots() -> None:
        old_defaults = dict(answers) if state.get('plots_asked') else defaults
        state['plotted'] = plots_stage_runner(session,
                                              answers,
                                              old_defaults,
                                              state['limits'],
                                              state['fit'],
                                              state['details'],
                                              )
        state['plots_asked'] = True

    steps = [('browser', run_browser),
             ('trim', run_trim),
             ('analysis', run_analysis),
             ('plots', run_plots),
             ]

    # ---- 2 Ask every step once -------------------------------------------------------
    try:
        for key, runner in steps:
            section_starter(STAGE_TITLES[key])
            runner()
        last_section, last_question = numbering_getter(0), numbering_getter(1)

        # ---- 3 Go back to any step ---------------------------------------------------
        options = [('done', 'No, continue')]
        options += [(key, STAGE_TITLES[key]) for key, _ in steps]
        while True:
            numbering_setter(0, last_section)
            numbering_setter(1, last_question)
            chosen = choice_asker('Do you want to go back to any of these steps?',
                                  options,
                                  'done',
                                  )
            if chosen == 'done':
                break
            index = [key for key, _ in steps].index(chosen)
            number = index + 2
            numbering_setter(0, number)
            heading_printer(f'{number}. {STAGE_TITLES[chosen]} (again)')
            steps[index][1]()
            if index < len(steps) - 1:
                later = ', '.join(STAGE_TITLES[k] for k, _ in steps[index + 1:])
                info_printer(f'Your answers to the later steps ({later}) were kept. '
                             f'Go back to them if this change affects them.',
                             )
    finally:
        session.window.window_closer()

    # ---- 4 Return the answers --------------------------------------------------------
    return state['limits'], state['fit'], state['details'], state['plotted']
