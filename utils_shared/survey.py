"""Numbered terminal questions of the main program (sections 1 to 5)."""
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import re

import config as settings
from utils_custom.run_namer import run_name_lister
from utils_shared.individual_experiment_exporter import read_saved_settings
from utils_shared.paf_reader import PafError, read_experiment_summary
from utils_shared.questions import (ask_choice,
                                    ask_multi,
                                    ask_number,
                                    ask_numbers,
                                    ask_text,
                                    ask_yes_no,
                                    clean_path,
                                    info,
                                    italic,
                                    numbering_restarter,
                                    numbering_setter,
                                    progress_clearer,
                                    progress_printer,
                                    )
from utils_shared.spectral_decomposer import import_fit

JOURNAL_NAMES = {'nature': 'Nature',
                 'science': 'Science',
                 'cell': 'Cell',
                 'pnas': 'PNAS',
                 }
OCR_LABELS = {'raw': 'OCR (µM min⁻¹)',
              'od': 'OCR / OD (µM min⁻¹ OD⁻¹)',
              'percent': 'OCR (% of the range)',
              }
SUBSCRIPTS = {'0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄', '5': '₅',
              '6': '₆', '7': '₇', '8': '₈', '9': '₉', 'a': 'ₐ', 'e': 'ₑ',
              'h': 'ₕ', 'i': 'ᵢ', 'j': 'ⱼ', 'k': 'ₖ', 'l': 'ₗ', 'm': 'ₘ',
              'n': 'ₙ', 'o': 'ₒ', 'p': 'ₚ', 'r': 'ᵣ', 's': 'ₛ', 't': 'ₜ',
              'u': 'ᵤ', 'v': 'ᵥ', 'x': 'ₓ',
              }


# ---- HAEM NAME FORMATTER -------------------------------------------------------------

def haem_name_formatter(name: str) -> str:
    """
    ---- Summary ----
    Main function to write a haem name for the terminal: the $...$ maths markers are
    removed, subscripts become subscript characters where they exist, and the maths
    part is shown in italics, e.g. 'Cyt $b_H$' becomes 'Cyt bₕ'.

    ---- Inputs ----
    name : str
        Haem name as written in the fit file.

    ---- Globals read ----
    SUBSCRIPTS (module constant).

    ---- Outputs ----
    str
        Name for display only; the original name is still used everywhere else.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.
    """

    def _subscript_converter(match: 're.Match') -> str:
        text = match.group(1) if match.group(1) is not None else match.group(2)
        if all(c.lower() in SUBSCRIPTS for c in text):
            return ''.join(SUBSCRIPTS[c.lower()] for c in text)
        return '_' + text

    def _maths_converter(match: 're.Match') -> str:
        inner = re.sub(r'_\{([^}]*)\}|_(.)', _subscript_converter, match.group(1))
        return italic(inner.replace('\\', ''))

    return re.sub(r'\$([^$]*)\$', _maths_converter, str(name))


# ---- OPTION BUILDERS -----------------------------------------------------------------

def ocr_options(keys: List[str]) -> List[Tuple[str, str]]:
    """
    ---- Summary ----
    Helper function to build the (key, label) choices for the OCR questions, using
    the units of the plot axes.

    ---- Inputs ----
    keys : List[str]
        OCR kinds offered: 'raw', 'od' and/or 'percent'.

    ---- Globals read ----
    OCR_LABELS (module constant).

    ---- Outputs ----
    List[Tuple[str, str]]
        [(key, label), ...] in the order of ``keys``.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.
    """
    return [(key, OCR_LABELS[key]) for key in keys]


def haem_form_options(include_percent: bool) -> List[Tuple[str, str]]:
    """
    ---- Summary ----
    Helper function to build the (key, label) choices for the 'how to show the
    haems' questions. The delta A line explains itself in italics.

    ---- Inputs ----
    include_percent : bool
        True to offer the % oxidised choice.

    ---- Globals read ----
    None.

    ---- Outputs ----
    List[Tuple[str, str]]
        [(key, label), ...]: abs, delta, conc and optionally percent.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.
    """
    delta = f"ΔA (mOD), {italic('the change in absorbance from the start')}"
    options = [('abs', 'Absorbance (mOD)'),
               ('delta', delta),
               ('conc', 'Concentration'),
               ]
    if include_percent:
        options.append(('percent', '% oxidised (lowest to highest = 0 to 100 %)'))
    return options


# ---- COLUMNS TEXT --------------------------------------------------------------------

def _columns_text(columns: float) -> str:
    """
    ---- Summary ----
    Helper function to write a figure width in columns, e.g. '1 column' or
    '1.5 columns'.

    ---- Inputs ----
    columns : float
        Number of journal columns.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        Text such as '2 columns'.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.
    """
    return f"{columns:g} column{'' if columns == 1 else 's'}"


# ---- PAF FINDER ----------------------------------------------------------------------

def paf_finder(folder: Path) -> List[Path]:
    """
    ---- Summary ----
    Helper function to list the .paf files directly inside a folder, by name.

    ---- Inputs ----
    folder : Path
        Existing folder.

    ---- Globals read ----
    None.

    ---- Outputs ----
    List[Path]
        The .paf files, sorted case-insensitively by name.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.
    """
    files = [p for p in Path(folder).iterdir()
             if p.is_file() and p.suffix.lower() == '.paf'
             ]
    return sorted(files, key=lambda p: _natural_sorter(p.name))


# ---- NATURAL SORTER ------------------------------------------------------------------

def _natural_sorter(name: str) -> list:
    """
    ---- Summary ----
    Helper function to build a sort key that puts numbers in numerical order, so
    'control_7hours' comes before 'control_24hours'.

    ---- Inputs ----
    name : str
        File or experiment name.

    ---- Globals read ----
    None.

    ---- Outputs ----
    list
        Key of alternating lower-case text and integer parts (text first).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.
    """
    parts = re.split(r'(\d+)', name.lower())
    return [int(part) if part.isdigit() else part for part in parts]


# ---- FILES ASKER ---------------------------------------------------------------------

def files_asker(last: dict) -> Tuple[Path, List[dict], Path]:
    """
    ---- Summary ----
    Main function to ask for the folder of .paf files (1.1) and the results folder
    (1.2), and to read a summary of every file.

    ---- Inputs ----
    last : dict
        Remembered answers (last_answers.json); uses data_folder and export_folder.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Tuple[Path, List[dict], Path]
        (data folder, summary of each readable file, results folder). Each summary
        has name, path, duration_min, events and datasets (DATA_FORMAT.md).

    ---- Globals mutated ----
    None. Reads from and prints to the terminal (side effect).

    ---- Equations ----
    None.
    """

    # ---- 1 Ask for the .paf folder -------------------------------------------
    while True:
        text = ask_text('What is the directory with the .paf files?',
                        last.get('data_folder'),
                        )
        if not text:
            info('Please type or drag in a folder.')
            continue
        folder = Path(clean_path(text)).expanduser()
        if not folder.is_dir():
            info('That folder does not exist.')
            continue
        files = paf_finder(folder)
        if not files:
            info('There are no .paf files directly inside that folder.')
            continue
        break

    # ---- 2 Read every file ----------------------------------------------------
    summaries = []
    for number, path in enumerate(files, start=1):
        progress_printer(f'Reading file {number} of {len(files)}: {path.name} ...')
        try:
            summary = read_experiment_summary(path)
        except PafError as exc:
            progress_clearer()
            info(f'Skipping {path.name}: {exc}')
            continue
        summary['path'] = path
        summaries.append(summary)
    progress_clearer()
    if not summaries:
        raise SystemExit('None of the .paf files could be read.')
    info(f'\nFound {len(summaries)} readable file(s):')
    for summary in summaries:
        info(f"  {summary['name']}: {summary['duration_min']:.1f} min, "
             f"{len(summary['events'])} event(s)",
             )

    # ---- 3 Ask for the results folder ----------------------------------------
    same_folder = last.get('data_folder') == str(folder)
    default = last.get('export_folder') if same_folder else str(folder / 'export')
    text = ask_text('To which directory would you like the results to be saved?',
                    default,
                    )
    return folder, summaries, Path(clean_path(text)).expanduser()


# ---- LIMITS ASKER --------------------------------------------------------------------

def _limits_asker(summaries: List[dict],
                  remembered: dict,
                  key: str,
                  question: str,
                  per_file: str,
                  fallback: Optional[float],
                  all_text: str,
                  bounds_builder: Callable[[dict, dict], dict],
                  note_builder: Callable[[dict], str],
                  collected: dict,
                  ) -> Dict[str, Optional[float]]:
    """
    ---- Summary ----
    Helper function to ask one yes/no question and then one number per file (trim or
    ignore, start or end), offering the values remembered from the last run.

    ---- Inputs ----
    summaries : List[dict]
        File summaries (DATA_FORMAT.md).
    remembered : dict
        {file name: {key: value}} from the last run.
    key : str
        Name of the limit, for example 'trim_start'.
    question : str
        The yes/no question.
    per_file : str
        Question for each file; {name} is replaced by the file name.
    fallback : Optional[float]
        Default for a file with no remembered value; None means 'none' and one
        value is asked per file. A number means one value is asked for all files,
        then optionally one per file.
    all_text : str
        The question for the value that applies to all files (ignore only).
    bounds_builder : Callable[[dict, dict], dict]
        Function (summary, limits collected so far for that file) giving the
        minimum and maximum accepted for the file.
    note_builder : Callable[[dict], str]
        Function (summary) giving the information line shown before the question.
    collected : dict
        {file name: {key: value}} of the limits asked so far.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, Optional[float]]
        {file name: minutes or None}.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal (side effect).

    ---- Equations ----
    None.
    """
    remembered_values = [remembered.get(s['name'], {}).get(key) for s in summaries]
    any_remembered = any(value for value in remembered_values)
    nothing_remembered = not any(v is not None for v in remembered_values)
    default_yes = any_remembered or (fallback is not None and fallback > 0
                                     and nothing_remembered)
    limits = {s['name']: None for s in summaries}
    if not ask_yes_no(question, default_yes):
        if fallback is not None:
            limits = {s['name']: 0.0 for s in summaries}
        return limits

    # ---- 1 One value for every file (ignore only) --------------------------------
    common = None
    if fallback is not None:
        known = [v for v in remembered_values if v is not None]
        common_default = max(set(known), key=known.count) if known else fallback
        common = ask_number(all_text,
                            common_default,
                            minimum=0,
                            depth=2,
                            )
        differs = any(v is not None and v != common for v in known)
        if not ask_yes_no('Do you want a different value for any file?',
                          differs,
                          depth=2,
                          ):
            return {s['name']: common for s in summaries}

    # ---- 2 One value per file ------------------------------------------------------
    for summary in summaries:
        name = summary['name']
        old = remembered.get(name, {}).get(key)
        default = old if old is not None else common
        note = note_builder(summary)
        if note:
            info(f'{name}: {note}', depth=2)
        bounds = bounds_builder(summary, collected.get(name, {}))
        limits[name] = ask_number(per_file.format(name=name),
                                  default,
                                  allow_blank=fallback is None,
                                  depth=2,
                                  **bounds,
                                  )
    return limits


# ---- TRIM ASKER ----------------------------------------------------------------------

def trim_asker(summaries: List[dict], remembered: dict) -> Dict[str, dict]:
    """
    ---- Summary ----
    Main function to ask section 2: which data is trimmed away (start, end) and which
    is ignored in the calculations (start, end), per file.

    ---- Inputs ----
    summaries : List[dict]
        File summaries (DATA_FORMAT.md).
    remembered : dict
        {file name: {trim_start, trim_end, ignore_start, ignore_end}} from the last
        run; offered as the defaults.

    ---- Globals read ----
    config.DEFAULT_ANSWERS (default ignore time at the start).

    ---- Outputs ----
    Dict[str, dict]
        {file name: {'trim_start', 'trim_end' (minutes on the original recording, or
        None), 'ignore_start', 'ignore_end' (minutes, counted from the new 0 time)}}.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal (side effect).

    ---- Equations ----
    None.
    """

    # ---- 1 Explain the two words ----------------------------------------------
    info('TRIM: data that will not be imported, plotted or used.')
    info('IGNORE: data that will be imported and plotted, but not used for '
         'calculations (baselines, % ranges, axis limits).',
         )
    collected = {s['name']: {} for s in summaries}

    # ---- 2 Ask the four questions ----------------------------------------------
    def _first_event(summary: dict) -> float:
        return min((e['time'] for e in summary['events']),
                   default=summary['duration_min'],
                   )

    def _last_event(summary: dict) -> float:
        return max((e['time'] for e in summary['events']), default=0.0)

    plan = (('trim_start',
             'Do you want to TRIM the START of any of the data?',
             'At what time (minutes) should {name} start?',
             None,
             '',
             lambda s, c: {'minimum': 0, 'maximum': _first_event(s)},
             lambda s: f'first event at {_first_event(s):.1f} min, recording '
                       f"{s['duration_min']:.1f} min",
             ),
            ('trim_end',
             'Do you want to TRIM the END of any of the data?',
             'At what time (minutes) should {name} end?',
             None,
             '',
             lambda s, c: {'minimum': max(_last_event(s), c.get('trim_start') or 0.0)},
             lambda s: f'last event at {_last_event(s):.1f} min, recording '
                       f"{s['duration_min']:.1f} min",
             ),
            ('ignore_start',
             'Do you want to IGNORE the START of any of the data?',
             'How many minutes at the start of {name} should be ignored?',
             settings.DEFAULT_ANSWERS['ignore_first_minutes'],
             'How many minutes at the start of the data should be ignored?',
             lambda s, c: {'minimum': 0},
             lambda s: '',
             ),
            ('ignore_end',
             'Do you want to IGNORE the END of any of the data?',
             'How many minutes at the end of {name} should be ignored?',
             0.0,
             'How many minutes at the end of the data should be ignored?',
             lambda s, c: {'minimum': 0},
             lambda s: '',
             ),
            )
    for key, question, per_file, fallback, all_text, bounds, note in plan:
        limits = _limits_asker(summaries,
                               remembered,
                               key,
                               question,
                               per_file,
                               fallback,
                               all_text,
                               bounds,
                               note,
                               collected,
                               )
        for name, value in limits.items():
            collected[name][key] = value

    # ---- 3 Tidy the values ------------------------------------------------------
    by_name = {s['name']: s for s in summaries}
    for name, values in collected.items():
        if not values['trim_start']:
            values['trim_start'] = None
        end = values['trim_end']
        if end is not None and end >= by_name[name]['duration_min']:
            values['trim_end'] = None
        values['ignore_start'] = values['ignore_start'] or 0.0
        values['ignore_end'] = values['ignore_end'] or 0.0
    return collected


# ---- DECOMPOSITION ASKER -------------------------------------------------------------

def decomposition_asker(summaries: List[dict],
                        defaults: dict,
                        fits_folder: Path,
                        forced: bool = False,
                        depth: int = 1,
                        ) -> tuple:
    """
    ---- Summary ----
    Main function to ask whether to decompose the spectra into haems and which fit to
    use.

    ---- Inputs ----
    summaries : List[dict]
        File summaries (DATA_FORMAT.md); the spectrometers in common are used.
    defaults : dict
        Default answers (decompose, fit_file, decomposition_dataset).
    fits_folder : Path
        Folder holding the fit .csv files.
    forced : bool
        True to skip the yes/no question (a figure that needs the haems was chosen).
    depth : int
        Numbering depth of the questions (1 = 3.1, 2 = 3.1.1).

    ---- Globals read ----
    None.

    ---- Outputs ----
    tuple
        (decompose, fit_file, fit, dataset). fit is the dictionary from import_fit,
        or None when no decomposition will be done.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal (side effect).

    ---- Equations ----
    None.
    """
    none_chosen = (False, None, None, defaults['decomposition_dataset'])
    fits = sorted(fits_folder.glob('*.csv'), key=lambda p: p.name.lower())
    if not fits:
        info(f'No fit files (.csv) were found in {fits_folder}, so haems cannot be '
             'decomposed this time. Put a fit .csv in that folder and run again.',
             )
        return none_chosen
    if not forced and not ask_yes_no('Do you want to decompose the haems?',
                                     defaults['decompose'],
                                     depth=depth,
                                     ):
        return none_chosen
    names = [p.name for p in fits]
    default_fit = defaults.get('fit_file')
    fit_file = ask_choice('Which fit would you like to use?',
                          [(n, n) for n in names],
                          default_fit if default_fit in names else names[0],
                          depth=depth + (0 if forced else 1),
                          )
    try:
        fit = import_fit(fits_folder / fit_file)
    except Exception as exc:
        info(f'The fit file could not be read ({exc}); haems will not be decomposed.')
        return none_chosen
    common = set(summaries[0]['datasets'])
    for summary in summaries[1:]:
        common &= set(summary['datasets'])
    if not common:
        info('The files have no spectrometer in common, so haems cannot be '
             'decomposed.',
             )
        return none_chosen
    dataset = defaults['decomposition_dataset']
    if dataset not in common:
        options = sorted(common)
        dataset = options[0]
        if len(options) > 1:
            dataset = ask_choice('Which spectrometer holds the haem spectra?',
                                 [(o, o) for o in options],
                                 options[0],
                                 depth=depth + 1,
                                 )
    return True, fit_file, fit, dataset


# ---- AVERAGING ASKER -----------------------------------------------------------------

def averaging_asker(answers: dict,
                    defaults: dict,
                    forced: bool = False,
                    depth: int = 1,
                    ) -> None:
    """
    ---- Summary ----
    Main function to ask whether to average around the events, and the window
    settings.

    ---- Inputs ----
    answers : dict
        Answers dictionary the values are stored in.
    defaults : dict
        Default answers (averaging, window_minutes, gap_minutes).
    forced : bool
        True to skip the yes/no question and only ask the window settings (a figure
        that needs the averages was chosen). The averaging answer is not changed.
    depth : int
        Numbering depth of the first question.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Stores window_minutes and gap_minutes (and averaging) in ``answers``.

    ---- Equations ----
    None.
    """
    if not forced:
        answers['averaging'] = ask_yes_no('Do you want to average around the events?',
                                          defaults['averaging'],
                                          depth=depth,
                                          )
        if not answers['averaging']:
            return
    sub = depth if forced else depth + 1
    answers['window_minutes'] = ask_number('How long a window (minutes) should the '
                                           'average be taken over?',
                                           defaults['window_minutes'],
                                           minimum=0,
                                           exclusive_minimum=True,
                                           depth=sub,
                                           )
    answers['gap_minutes'] = ask_number('How long before the next addition should '
                                        'the averaging window end (minutes)?',
                                        defaults['gap_minutes'],
                                        minimum=0,
                                        depth=sub,
                                        )
    answers['window_asked'] = True


# ---- OD ASKER ------------------------------------------------------------------------

def od_asker(summaries: List[dict], saved: dict) -> Dict[str, dict]:
    """
    ---- Summary ----
    Main function to ask the OD, volume and dilution factor of every file, offering the
    values saved in each experiment's workbook.

    ---- Inputs ----
    summaries : List[dict]
        File summaries (DATA_FORMAT.md).
    saved : dict
        {file name: values read from its workbook} (read_saved_settings).

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, dict]
        {file name: {'OD', 'volume', 'dilution_factor'}}.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal (side effect).

    ---- Equations ----
    None.
    """
    values = {}
    for summary in summaries:
        name = summary['name']
        old = saved.get(name) or {}
        info(f'\n{name}:', depth=2, tight=True)
        numbering_restarter(2)
        values[name] = {'OD': ask_number('What was the OD of the cells added?',
                                         old.get('OD'),
                                         minimum=0,
                                         exclusive_minimum=True,
                                         depth=2,
                                         ),
                        'volume': ask_number('What volume of cells (mL) were spun down '
                                             'and resuspended in 5 mL?',
                                             old.get('volume'),
                                             minimum=0,
                                             exclusive_minimum=True,
                                             depth=2,
                                             ),
                        'dilution_factor': ask_number('What is the dilution factor, if '
                                                      'the cells were diluted mid run?',
                                                      old.get('dilution_factor', 1.0),
                                                      minimum=0,
                                                      exclusive_minimum=True,
                                                      depth=2,
                                                      ),
                        }
    return values


# ---- EVENT ASKER ---------------------------------------------------------------------

def event_asker(summaries: List[dict], saved: dict) -> Dict[str, List[dict]]:
    """
    ---- Summary ----
    Main function to ask whether to change the event labels, concentrations and which
    events to ignore, file by file.

    ---- Inputs ----
    summaries : List[dict]
        File summaries (DATA_FORMAT.md).
    saved : dict
        {file name: values read from its workbook} (read_saved_settings).

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, List[dict]]
        {file name: [{'datapoint', 'label', 'concentration_uM', 'ignored'}, ...]}.
        A label of 'ignore' marks an event that was not an addition.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal (side effect).

    ---- Equations ----
    None.
    """

    # ---- 1 Start from the saved or file values ---------------------------------
    result = {}
    for summary in summaries:
        old = {e['datapoint']: e for e in (saved.get(summary['name']) or {})
               .get('events', [])}
        events = []
        for event in summary['events']:
            before = old.get(event['datapoint'], {})
            ignored = bool(before.get('ignored', False))
            events.append({'datapoint': event['datapoint'],
                           'label': 'ignore' if ignored
                           else (before.get('label') or event['text']),
                           'concentration_uM': before.get('concentration_uM'),
                           'ignored': ignored,
                           })
        result[summary['name']] = events
    with_events = [s for s in summaries if s['events']]
    if not with_events:
        return result

    # ---- 2 Show the current events and ask which runs to change ------------------
    info('Current runs and event labels are:')
    for number, summary in enumerate(with_events, start=1):
        info(f"{number}) {summary['name']}:")
        for event, entry in zip(summary['events'], result[summary['name']]):
            info(_event_line_builder(event, entry), depth=2)
    if not ask_yes_no('Do you want to change any event labels?', False):
        return result
    chosen = ask_numbers('Which run(s) do you want to change?',
                         len(with_events),
                         depth=2,
                         )

    # ---- 3 Ask about the events of each chosen run -------------------------------
    for number in chosen:
        summary = with_events[number - 1]
        name = summary['name']
        events = result[name]
        info(f'\n{name}:', depth=2)
        for event, entry in zip(summary['events'], events):
            info(_event_line_builder(event, entry), depth=2)
        numbering_setter(2, number)
        for event, entry in zip(summary['events'], events):
            label = ask_text(f"What was added at {event['time']:.2f} min? "
                             "Write 'ignore' to ignore this event.",
                             entry['label'],
                             depth=3,
                             )
            entry['label'] = label or entry['label']
            entry['ignored'] = entry['label'].strip().lower() == 'ignore'
            if entry['ignored']:
                continue
            entry['concentration_uM'] = ask_number('What was the final concentration '
                                                   'in uM?',
                                                   entry['concentration_uM'],
                                                   minimum=0,
                                                   allow_blank=True,
                                                   depth=3,
                                                   blank_label='unknown',
                                                   )
    return result


# ---- EVENT LINE BUILDER --------------------------------------------------------------

def _event_line_builder(event: dict, entry: dict) -> str:
    """
    ---- Summary ----
    Helper function to write one event as 'label, time' for the event listings.

    ---- Inputs ----
    event : dict
        Event from the file summary (time in minutes).
    entry : dict
        Current label, concentration_uM and ignored flag of that event.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        For example '  nd-011992, 15.01 min' or with the concentration and
        '[IGNORED]' when they apply.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.
    """
    conc = ('' if entry['concentration_uM'] is None
            else f", {entry['concentration_uM']:g} uM")
    note = '  [IGNORED]' if entry['ignored'] else ''
    return f"  {entry['label']}, {event['time']:.2f} min{conc}{note}"


# ---- ANALYSIS ASKER ------------------------------------------------------------------

def analysis_asker(summaries: List[dict],
                   answers: dict,
                   defaults: dict,
                   fits_folder: Path,
                   export_root: Path,
                   ) -> tuple:
    """
    ---- Summary ----
    Main function to ask section 3: haem decomposition, OD scaling, event averaging
    and the event labels.

    ---- Inputs ----
    summaries : List[dict]
        File summaries (DATA_FORMAT.md).
    answers : dict
        Answers dictionary the values are stored in.
    defaults : dict
        Default answers.
    fits_folder : Path
        Folder holding the fit .csv files.
    export_root : Path
        Results folder, where the saved OD and event values are looked for.

    ---- Globals read ----
    None.

    ---- Outputs ----
    tuple
        (fit, details). details is {file name: {'OD', 'volume', 'dilution_factor',
        'events'}}; the OD entries are only present when scaling by OD.

    ---- Globals mutated ----
    None. Stores the answers in ``answers`` (side effect).

    ---- Equations ----
    None.
    """

    # ---- 1 Decomposition ---------------------------------------------------------
    (answers['decompose'],
     answers['fit_file'],
     fit,
     answers['decomposition_dataset'],
     ) = decomposition_asker(summaries, defaults, fits_folder)

    # ---- 2 OD scaling ------------------------------------------------------------
    saved = {}
    for number, summary in enumerate(summaries, start=1):
        progress_printer(f'Looking for earlier values, file {number} of '
                         f'{len(summaries)} ...',
                         )
        saved[summary['name']] = read_saved_settings(export_root, summary['name'])
    progress_clearer()
    if any(saved.values()):
        info("\nEarlier OD and event values found in the experiments' workbooks are "
             'offered as defaults.',
             )
    answers['normalise_od'] = ask_yes_no('Do you want to scale by OD (divide by '
                                         'dilution factor x OD x volume)?',
                                         defaults['normalise_od'],
                                         )
    details = {s['name']: {} for s in summaries}
    if answers['normalise_od']:
        for name, values in od_asker(summaries, saved).items():
            details[name].update(values)

    # ---- 3 Averaging ---------------------------------------------------------------
    averaging_asker(answers, defaults)

    # ---- 4 Event labels --------------------------------------------------------------
    for name, events in event_asker(summaries, saved).items():
        details[name]['events'] = events
    return fit, details


# ---- SIZE ASKER ----------------------------------------------------------------------

def size_asker(answers: dict,
               defaults: dict,
               keys: dict,
               fallback: Tuple[float, float],
               depth: int = 1,
               ) -> None:
    """
    ---- Summary ----
    Main function to ask the journal, width and height of one figure. Answering None
    to the journal question uses Nature with the fallback width and height.

    ---- Inputs ----
    answers : dict
        Answers dictionary the values are stored in.
    defaults : dict
        Default answers.
    keys : dict
        Names of the answers: {'journal', 'columns', 'height', 'mode'}.
    fallback : Tuple[float, float]
        (columns, height) used when the journal is None.
    depth : int
        Numbering depth of the journal question.

    ---- Globals read ----
    config.JOURNAL_SPECS.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Stores the four answers in ``answers`` (side effect).

    ---- Equations ----
    None.
    """
    columns_default, height_default = fallback
    options = [('none',
                'None (use the default: Nature, '
                f'{_columns_text(columns_default)} wide, '
                f'{height_default:g} of a page tall)',
                )]
    options += [(key, name) for key, name in JOURNAL_NAMES.items()]
    remembered = defaults[keys['journal']] if defaults[keys['mode']] == 'custom' \
        else 'none'
    journal = ask_choice('Which journal format would you like?',
                         options,
                         remembered if remembered in dict(options) else 'none',
                         depth=depth,
                         )
    if journal == 'none':
        answers[keys['mode']] = 'default'
        answers[keys['journal']] = 'nature'
        answers[keys['columns']] = columns_default
        answers[keys['height']] = height_default
        return
    answers[keys['mode']] = 'custom'
    answers[keys['journal']] = journal
    spec = settings.JOURNAL_SPECS[journal]
    widths = [(c, f'{_columns_text(c)} wide ({mm} mm)')
              for c, mm in spec['widths_mm'].items()
              ]
    old = defaults[keys['columns']]
    answers[keys['columns']] = ask_choice('How wide should the figure be?',
                                          widths,
                                          old if old in spec['widths_mm']
                                          else widths[0][0],
                                          depth=depth + 1,
                                          )
    page = spec['page_height_mm']
    answers[keys['height']] = ask_number('How tall should the figure be, as a '
                                         f'fraction of the page height (1 = a full '
                                         f'page = {page:g} mm)?',
                                         defaults[keys['height']],
                                         minimum=0,
                                         exclusive_minimum=True,
                                         maximum=1,
                                         depth=depth + 1,
                                         )


# ---- PLOT ASKER ----------------------------------------------------------------------

def plot_asker(answers: dict, defaults: dict, fit: Optional[dict]) -> bool:
    """
    ---- Summary ----
    Main function to ask section 4: what the individual experiment figures show and
    how they are sized.

    ---- Inputs ----
    answers : dict
        Answers dictionary the values are stored in; must hold normalise_od and
        decompose.
    defaults : dict
        Default answers.
    fit : Optional[dict]
        Fit dictionary (haem_list) used to list the haems, or None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    bool
        True when at least one panel is plotted.

    ---- Globals mutated ----
    None. Stores the answers in ``answers`` (side effect).

    ---- Equations ----
    None.
    """

    # ---- 1 Oxygen and OCR ------------------------------------------------------
    answers['plot_o2'] = ask_yes_no('Do you want to plot the set and measured [O2] '
                                    '(CsO2 and CcO2)?',
                                    defaults['plot_o2'],
                                    )
    answers['plot_ocr'] = ask_yes_no('Do you want to plot the OCR?',
                                     defaults['plot_ocr'],
                                     )
    if answers['plot_ocr']:
        keys = ['raw'] + (['od'] if answers['normalise_od'] else []) + ['percent']
        answers['ocr_mode'] = ask_choice('Which OCR would you like to plot?',
                                         ocr_options(keys),
                                         defaults['ocr_mode'] if defaults['ocr_mode']
                                         in keys else keys[0],
                                         depth=2,
                                         )

    # ---- 2 Haems -----------------------------------------------------------------
    answers['plot_haems'] = False
    if answers['decompose']:
        answers['plot_haems'] = ask_yes_no('Do you want to plot the haems?',
                                           defaults['plot_haems'],
                                           )
    if answers['plot_haems']:
        answers['haems'] = ask_multi('Which haems would you like to plot, and in '
                                     'which order?',
                                     list(fit['haem_list']),
                                     default_all=True,
                                     keep_order=True,
                                     depth=2,
                                     default_values=defaults['haems'],
                                     label_formatter=haem_name_formatter,
                                     )
        answers['haem_mode'] = ask_choice('How would you like to plot the haems?',
                                          haem_form_options(True),
                                          defaults['haem_mode'],
                                          depth=2,
                                          )
        if answers['normalise_od'] and answers['haem_mode'] != 'percent':
            answers['haem_per_od'] = ask_yes_no('Do you want to scale the haems by '
                                                'OD as well?',
                                                defaults['haem_per_od'],
                                                depth=2,
                                                )

    # ---- 3 Labels and size --------------------------------------------------------
    plotted = answers['plot_o2'] or answers['plot_ocr'] or answers['plot_haems']
    if not plotted:
        info('Nothing is set to be plotted, so no individual figures will be made.')
    else:
        answers['event_label_angle'] = ask_number('At what angle should the event '
                                                  'labels be plotted (0 = '
                                                  'horizontal, 90 = vertical)?',
                                                  defaults['event_label_angle'],
                                                  minimum=0,
                                                  maximum=90,
                                                  )
    size_asker(answers,
               defaults,
               {'journal': 'journal',
                'columns': 'columns',
                'height': 'height',
                'mode': 'size_mode',
                },
               (1, 0.5),
               )
    return plotted


# ---- MULTI EXPERIMENT ASKER ----------------------------------------------------------

def multi_experiment_asker(summaries: List[dict],
                           answers: dict,
                           defaults: dict,
                           plotted: bool,
                           ) -> tuple:
    """
    ---- Summary ----
    Main function to ask section 5: the side-by-side figure of two experiments and
    the 2x2 figure of four experiments.

    ---- Inputs ----
    summaries : List[dict]
        File summaries (DATA_FORMAT.md).
    answers : dict
        Answers dictionary the values are stored in.
    defaults : dict
        Default answers.
    plotted : bool
        True when section 4 plots at least one panel (both figures reuse its choices).

    ---- Globals read ----
    None.

    ---- Outputs ----
    tuple
        (comparison, exemplar_names). comparison is {'runs': (left, right),
        'columns', 'height'} or None; exemplar_names is the list of the four
        experiments of the 2x2 figure, or None.

    ---- Globals mutated ----
    None. Stores the answers in ``answers`` (side effect).

    ---- Equations ----
    None.
    """
    comparison = None
    exemplar_names = None
    answers['plot_comparison'] = False
    answers['plot_exemplar'] = False
    if not plotted:
        info('The figures below reuse the panels chosen in section 4, and nothing '
             'is plotted there, so they are skipped.',
             )
        return comparison, exemplar_names

    # ---- 1 Two experiments side by side -----------------------------------------
    if len(summaries) >= 2 and ask_yes_no('Do you want to plot two experiments side '
                                          'by side?',
                                          defaults['plot_comparison'],
                                          ):
        names = [(s['name'], s['name']) for s in summaries]
        first = ask_choice('Which experiment goes on the left?', names, depth=2)
        second = ask_choice('Which experiment goes on the right?',
                            [n for n in names if n[0] != first],
                            depth=2,
                            )
        size_asker(answers,
                   defaults,
                   {'journal': 'comparison_journal',
                    'columns': 'comparison_columns',
                    'height': 'comparison_height',
                    'mode': 'comparison_size_mode',
                    },
                   (1.5, 0.7),
                   depth=2,
                   )
        comparison = {'runs': (first, second),
                      'columns': answers['comparison_columns'],
                      'height': answers['comparison_height'],
                      }
        answers['plot_comparison'] = True

    # ---- 2 Four experiments in a 2x2 grid ----------------------------------------
    if len(summaries) >= 4 and ask_yes_no('Do you want to plot four experiments in a '
                                          '2x2 grid (knockdown and control, two '
                                          'addition orders)?',
                                          defaults['plot_exemplar'],
                                          ):
        info("Names are read as <strain>_<order>_run<N>, e.g. "
             "'knockdown_kcn_then_bd_run1'.",
             depth=2,
             )
        rows = [r for r in run_name_lister([s['name'] for s in summaries])
                if all(r[k] is not None for k in ('strain', 'order', 'run'))]
        runs = sorted({r['run'] for r in rows})
        if not runs:
            info('No file name fits, so this figure is skipped.', depth=2)
        else:
            old = defaults['ho_exemplar_run']
            run = ask_choice('Which run number should be shown?',
                             [(r, f'run {r}') for r in runs],
                             old if old in runs else runs[0],
                             depth=2,
                             )
            answers['ho_exemplar_run'] = int(run)
            if not answers['averaging']:
                info('This figure starts at the baseline averaging window, so the '
                     'events are averaged as in section 3.3.',
                     depth=2,
                     )
                averaging_asker(answers, defaults, forced=True, depth=2)
                answers['averaging'] = True
            exemplar_names = [r['name'] for r in rows if r['run'] == int(run)]
            info(f"Using: {', '.join(exemplar_names)}", depth=2)
            size_asker(answers,
                       defaults,
                       {'journal': 'ex_journal',
                        'columns': 'ho_ex_columns',
                        'height': 'ho_ex_height',
                        'mode': 'ex_size_mode',
                        },
                       (1.5, 0.7),
                       depth=2,
                       )
            answers['plot_exemplar'] = True
    return comparison, exemplar_names
