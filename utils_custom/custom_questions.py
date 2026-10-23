"""Terminal questions for the time response and haem and OCR response figures."""
from typing import Optional

from utils_custom.run_namer import group_assigner, hours_parser, run_name_lister
from utils_shared.questions import (ask_choice,
                                    ask_multi,
                                    ask_number,
                                    ask_text,
                                    ask_yes_no,
                                    )

HAEM_MODE_OPTIONS = [('delta', 'Delta A (change in absorbance from the start, mOD)'),
                     ('abs', 'Absorbance (mOD)'),
                     ('conc', 'Concentration'),
                     ]
METRIC_LABELS = {'delta': "Change from each run's baseline, in the units of the data",
                 'change': "Percentage of each run's baseline",
                 'value': 'The window average as it is',
                 }


# ---- CUSTOM CHOICE ASKER -------------------------------------------------------------

def custom_choice_asker(defaults: dict) -> tuple:
    """
    ---- Summary ----
    Main function to ask which of the special figures to make.

    ---- Inputs ----
    defaults : dict
        Default answers (config.DEFAULT_ANSWERS plus the remembered answers).

    ---- Globals read ----
    None.

    ---- Outputs ----
    tuple
        (plot_time_response, plot_haem_ocr) as booleans.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal (side effect).

    ---- Equations ----
    None.
    """
    plot_time_response = ask_yes_no('Plot a time response (difference spectra of '
                                    'control vs knockdown '
                                    'time points)?',
                                    defaults['plot_time_response'],
                                    )
    plot_haem_ocr = ask_yes_no('Plot a haem and OCR response (the large publication '
                               'figure and the '
                               'four-run exemplar figure)?',
                               defaults['plot_haem_ocr'],
                               )
    return plot_time_response, plot_haem_ocr


# ---- SIZE ASKER ----------------------------------------------------------------------

def _size_asker(title: str,
                spec: dict,
                defaults: dict,
                column_key: str,
                height_key: str,
                answers: dict,
                ) -> None:
    """
    ---- Summary ----
    Helper function to ask the width and height of one custom figure.

    ---- Inputs ----
    title : str
        Name of the figure, shown in the questions.
    spec : dict
        Journal specification (config.JOURNAL_SPECS entry).
    defaults : dict
        Default answers.
    column_key : str
        Key of the width answer.
    height_key : str
        Key of the height answer.
    answers : dict
        Answers dictionary the two values are stored in.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Stores the width and height in ``answers`` (side effect).

    ---- Equations ----
    None.
    """
    widths = spec['widths_mm']
    options = [(c, f'{c:g} column(s) wide ({mm} mm)') for c, mm in widths.items()]
    default = defaults[column_key] if defaults[column_key] in widths else options[-1][0]
    answers[column_key] = ask_choice(f'{title} width', options, default)
    page_mm = spec['page_height_mm']
    answers[height_key] = ask_number(f'{title} height as a fraction of the page height'
                                     f' '
                                     f'(1 = a full page = {page_mm:g} mm)',
                                     defaults[height_key],
                                     minimum=0,
                                     exclusive_minimum=True,
                                     maximum=1,
                                     )


# ---- TIME RESPONSE ASKER -------------------------------------------------------------

def _time_response_asker(names: list,
                         answers: dict,
                         defaults: dict,
                         spec: dict,
                         ) -> Optional[dict]:
    """
    ---- Summary ----
    Helper function to ask the settings of the time response figure.

    ---- Inputs ----
    names : list
        Experiment names (file names without the extension).
    answers : dict
        Answers dictionary the settings are stored in.
    defaults : dict
        Default answers.
    spec : dict
        Journal specification.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[dict]
        {experiment name: group} of the experiments that belong to the figure, or
        None when the figure cannot be made from these files.

    ---- Globals mutated ----
    None. Stores the settings in ``answers`` (side effect).

    ---- Equations ----
    None.
    """

    # ---- 1 Find the experiments of each group ---------------------------------
    print('\n  Time response: each file name needs a group word and the hours, for')
    print("  example 'control_7hours' or 'knockdown_24hours'.")
    text = ask_text('  The two group words, separated by a comma',
                    ','.join(defaults['tr_groups']),
                    )
    groups = [word.strip().lower() for word in text.split(',') if word.strip()]
    if len(groups) != 2:
        print('  Two group words are needed, so the time response is skipped.')
        return None
    found = group_assigner({name: {} for name in names}, groups)
    members = {name: experiment['group'] for name, experiment in found.items()}
    for group in groups:
        listed = [n for n, g in members.items() if g == group]
        print(f'    {group}: {", ".join(listed) if listed else "no files found"}')
    if any(group not in members.values() for group in groups):
        print('  Both groups need at least one file, so the time response is skipped.')
        return None
    unread = [n for n in members if hours_parser(n) is None]
    if unread:
        print(f'  No hours found in: {", ".join(unread)} (they are left out of the '
              f'examples).',
              )
    answers['tr_groups'] = groups

    # ---- 2 Averaging windows --------------------------------------------------
    answers['tr_window_minutes'] = ask_number('  Length of each spectral averaging '
                                              'window (minutes)',
                                              defaults['tr_window_minutes'],
                                              minimum=0,
                                              exclusive_minimum=True,
                                              )
    answers['tr_gap_minutes'] = ask_number('  How long before the next addition each '
                                           'window ends (minutes)',
                                           defaults['tr_gap_minutes'],
                                           minimum=0,
                                           )
    answers['tr_final_gap_minutes'] = ask_number('  How long before the end of the '
                                                 'recording the last window ends '
                                                 '(minutes)',
                                                 defaults['tr_final_gap_minutes'],
                                                 minimum=0,
                                                 )

    # ---- 3 The two example experiments ----------------------------------------
    timed = [n for n in members if hours_parser(n) is not None]
    options = [(n, f'{n} ({members[n]}, {hours_parser(n):g} hours)') for n in timed]
    if len(options) < 2:
        print('  Two experiments with hours are needed for the examples, so the time '
              'response is skipped.',
              )
        return None
    first_group = [n for n in timed if members[n] == groups[0]]
    left = ask_choice('  Example shown in the left panels', options, first_group[0])
    right = ask_choice('  Example shown in the right panels',
                       options,
                       first_group[-1] if first_group[-1] != left else options[-1][0],
                       )
    answers['tr_examples'] = [[members[left], hours_parser(left)],
                              [members[right], hours_parser(right)],
                              ]

    # ---- 4 Figure size --------------------------------------------------------
    _size_asker('  Time response figure',
                spec,
                defaults,
                'tr_columns',
                'tr_height',
                answers,
                )
    return members


# ---- HAEM OCR ASKER ------------------------------------------------------------------

def _haem_ocr_asker(names: list,
                    answers: dict,
                    defaults: dict,
                    spec: dict,
                    fit: dict,
                    ) -> Optional[list]:
    """
    ---- Summary ----
    Helper function to ask the settings of the haem and OCR response figures.

    ---- Inputs ----
    names : list
        Experiment names (file names without the extension).
    answers : dict
        Answers dictionary the settings are stored in.
    defaults : dict
        Default answers.
    spec : dict
        Journal specification.
    fit : dict
        Fit dictionary (haem_list and data) used to list the haems.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[list]
        Names of the experiments that belong to the figures, or None when the figures
        cannot be made from these files.

    ---- Globals mutated ----
    None. Stores the settings in ``answers`` (side effect).

    ---- Equations ----
    None.
    """

    # ---- 1 Show how the file names are read ------------------------------------
    print('\n  Haem and OCR response: each file name needs the strain (control or')
    print('  knockdown), the addition order (e.g. kcn_then_bd or bd_then_kcn) and')
    print("  the run number, for example 'knockdown_kcn_then_bd_run1'.")
    rows = run_name_lister(names)
    usable = []
    for row in rows:
        known = all(row[key] is not None for key in ('strain', 'order', 'run'))
        if known:
            usable.append(row)
            description = f"{row['strain']}, {row['order']}, run {row['run']}"
        else:
            description = 'not recognised, left out'
        print(f"    {row['name']}: {description}")
    if not usable:
        print('  None of the files can be used, so the haem and OCR response is '
              'skipped.',
              )
        return None
    conditions = {(r['strain'], r['order']) for r in usable}
    print(f'  {len(usable)} file(s) in {len(conditions)} condition(s) will be used.')

    # ---- 2 Haems, metric and OCR -----------------------------------------------
    mode = ask_choice('  Show the haems as',
                      HAEM_MODE_OPTIONS,
                      defaults['ho_haem_mode'],
                      )
    answers['ho_haem_mode'] = mode
    answers['ho_per_od'] = (ask_yes_no('  Divide the haem values by OD as well?',
                                       defaults['ho_per_od'],
                                       )
                            if answers['normalise_od']
                            else False
                            )
    metrics = ['delta', 'value'] if mode == 'delta' else ['delta', 'change', 'value']
    if mode == 'delta':
        print('  (A percentage of baseline is not available for delta A, which '
              'starts at 0.)',
              )
    answers['ho_metric'] = ask_choice('  What the haem response shows',
                                      [(m, METRIC_LABELS[m]) for m in metrics],
                                      defaults['ho_metric']
                                      if defaults['ho_metric'] in metrics
                                      else 'delta',
                                      )
    names_in_fit = list(fit['haem_list'])
    answers['ho_haems'] = ask_multi('  Which haems get a row in the haem response?',
                                    names_in_fit,
                                    default_all=True,
                                    )
    if answers['normalise_od']:
        answers['ho_ocr_mode'] = ask_choice('  Which OCR',
                                            [('od', 'OCR per OD'), ('raw', 'Raw OCR')],
                                            defaults['ho_ocr_mode'],
                                            )
    else:
        answers['ho_ocr_mode'] = 'raw'

    # ---- 3 Averaging windows ---------------------------------------------------
    answers['ho_window_minutes'] = ask_number('  Length of each averaging window '
                                              '(minutes)',
                                              defaults['ho_window_minutes'],
                                              minimum=0,
                                              exclusive_minimum=True,
                                              )
    answers['ho_gap_minutes'] = ask_number('  How long before the next addition each '
                                           'window ends (minutes)',
                                           defaults['ho_gap_minutes'],
                                           minimum=0,
                                           )
    answers['ho_final_gap_minutes'] = ask_number('  How long before the end of the '
                                                 'recording the last window ends '
                                                 '(minutes)',
                                                 defaults['ho_final_gap_minutes'],
                                                 minimum=0,
                                                 )
    runs = sorted({r['run'] for r in usable})
    run_default = runs[0]
    if defaults['ho_exemplar_run'] in runs:
        run_default = defaults['ho_exemplar_run']
    run_options = [(r, f'run {r}') for r in runs]
    answers['ho_exemplar_run'] = int(ask_choice('  Run shown in the four-run exemplar '
                                                'figure',
                                                run_options,
                                                run_default,
                                                ),
                                     )

    # ---- 4 Figure sizes --------------------------------------------------------
    _size_asker('  Publication figure',
                spec,
                defaults,
                'ho_pub_columns',
                'ho_pub_height',
                answers,
                )
    _size_asker('  Exemplar figure',
                spec,
                defaults,
                'ho_ex_columns',
                'ho_ex_height',
                answers,
                )
    return [r['name'] for r in usable]


# ---- CUSTOM DETAIL ASKER -------------------------------------------------------------

def custom_detail_asker(names: list,
                        answers: dict,
                        defaults: dict,
                        fit: Optional[dict],
                        wants_time_response: bool,
                        wants_haem_ocr: bool,
                        ) -> dict:
    """
    ---- Summary ----
    Main function to ask the settings of the special figures that were chosen, after
    the journal is known.

    ---- Inputs ----
    names : list
        Experiment names (file names without the extension).
    answers : dict
        Answers dictionary the settings are stored in; must hold 'journal' and
        'normalise_od'.
    defaults : dict
        Default answers.
    fit : Optional[dict]
        Fit dictionary used to list the haems; required for both figures.
    wants_time_response : bool
        True when the time response was chosen.
    wants_haem_ocr : bool
        True when the haem and OCR response was chosen.

    ---- Globals read ----
    config.JOURNAL_SPECS (through the answers' journal key).

    ---- Outputs ----
    dict
        {'time_response': {experiment name: group} or None, 'haem_ocr': [experiment
        names] or None}. None means the figure will not be made.

    ---- Globals mutated ----
    None. Stores the settings in ``answers`` (side effect).

    ---- Equations ----
    None.
    """
    from config import JOURNAL_SPECS

    spec = JOURNAL_SPECS[answers['journal']]
    result = {'time_response': None, 'haem_ocr': None}
    if fit is None:
        print('  The special figures need the haem fit, so they are skipped.')
        answers['plot_time_response'] = answers['plot_haem_ocr'] = False
        return result
    if wants_time_response:
        result['time_response'] = _time_response_asker(names, answers, defaults, spec)
    if wants_haem_ocr:
        result['haem_ocr'] = _haem_ocr_asker(names, answers, defaults, spec, fit)
    answers['plot_time_response'] = result['time_response'] is not None
    answers['plot_haem_ocr'] = result['haem_ocr'] is not None
    return result
