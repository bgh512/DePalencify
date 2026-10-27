"""Numbered terminal questions of section 6: the time response and the haem and OCR
response figures."""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from pathlib import Path
from typing import List, Optional

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_custom.run_namer import group_assigner, hours_parser, run_name_lister
from utils_shared.questions import (choice_asker,
                                    info_printer,
                                    multi_asker,
                                    text_asker,
                                    yes_no_asker,
                                    )
from utils_shared.survey import (averaging_asker,
                                 decomposition_asker,
                                 haem_form_option_builder,
                                 haem_name_formatter,
                                 haem_name_sorter,
                                 ocr_option_builder,
                                 size_asker,
                                 )


# ---- CUSTOM QUESTIONS HELPERS --------------------------------------------------------


# ---- _HAEM OCR ASKER -----------------------------------------------------------------
def _haem_ocr_asker(names: List[str],
                    answers: dict,
                    defaults: dict,
                    fit: dict,
                    ) -> Optional[List[str]]:
    """
    ---- Summary ----
    Helper function to ask the settings of the haem and OCR response figure (6.2.x).

    ---- Inputs ----
    names : List[str]
        Experiment names (file names without the extension).
    answers : dict
        Answers dictionary the settings are stored in.
    defaults : dict
        Default answers.
    fit : dict
        Fit dictionary (haem_list) used to list the haems.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[List[str]]
        Names of the experiments that belong to the figure, or None when it cannot be
        made from these files.

    ---- Globals mutated ----
    None. Stores the settings in ``answers`` (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    choice_asker
    haem_form_option_builder
    haem_name_formatter
    haem_name_sorter
    info_printer
    multi_asker
    ocr_option_builder
    run_name_lister
    size_asker
    yes_no_asker
    """

    # ---- 1 Show how the file names are read ------------------------------------------
    info_printer('File names need the strain, the addition order and the run number, '
                 'e.g. '
                 "'knockdown_kcn_then_bd_run1'.",
                 depth=2,
                 )
    rows = run_name_lister(names)
    usable = [r
              for r in rows
              if all(r[key] is not None for key in ('strain', 'order', 'run'))
              ]
    left_out = [r['name'] for r in rows if r not in usable]
    if not usable:
        info_printer('None of the file names fit, so the haem and OCR response is '
                     'skipped.',
                     depth=2,
                     )
        return None
    sets = {}
    for row in usable:
        sets.setdefault((row['strain'], row['order']), []).append(row['run'])
    info_printer(f'{len(usable)} file(s) found in {len(sets)} set(s):', depth=2)
    for (strain, order), runs in sets.items():
        runs_text = ', '.join(str(r) for r in sorted(runs))
        info_printer(f'  {len(runs)} replicate(s) of strain: {strain}, additions: '
                     f'{order} '
                     f'(run {runs_text})',
                     depth=2,
                     )
    if left_out:
        left_text = ', '.join(left_out)
        info_printer(f'Left out (name not recognised): {left_text}', depth=2)

    # ---- 2 What is shown -------------------------------------------------------------
    ocr_keys = ['raw'] + (['od'] if answers['normalise_od'] else []) + ['percent']
    answers['ho_ocr_mode'] = choice_asker('Which OCR would you like to use?',
                                          ocr_option_builder(ocr_keys),
                                          defaults['ho_ocr_mode']
                                          if defaults['ho_ocr_mode'] in ocr_keys
                                          else ocr_keys[0],
                                          depth=2,
                                          )
    answers['ho_haem_mode'] = choice_asker('How would you like to show the haems?',
                                           haem_form_option_builder(True),
                                           defaults['ho_haem_mode'],
                                           depth=2,
                                           )
    answers['ho_per_od'] = False
    if answers['normalise_od'] and answers['ho_haem_mode'] != 'percent':
        answers['ho_per_od'] = yes_no_asker('Do you want to scale the haems by OD as '
                                            'well?',
                                            defaults['ho_per_od'],
                                            depth=2,
                                            )
    answers['ho_metric'] = 'delta'
    answers['ho_haems'] = multi_asker('Which haems should get a row, and in which '
                                      'order?',
                                      haem_name_sorter(fit['haem_list']),
                                      default_all=True,
                                      keep_order=True,
                                      depth=2,
                                      default_values=(defaults['ho_haems']
                                                      or list(fit['haem_list'])
                                                      ),
                                      label_formatter=haem_name_formatter,
                                      )

    # ---- 3 Figure size ---------------------------------------------------------------
    size_asker(answers,
               defaults,
               {'journal': 'ho_journal',
                'columns': 'ho_pub_columns',
                'height': 'ho_pub_height',
                'mode': 'ho_size_mode',
                },
               (2, 0.75),
               depth=2,
               )
    return [r['name'] for r in usable]


# ---- _TIME RESPONSE ASKER ------------------------------------------------------------
def _time_response_asker(names: List[str],
                         answers: dict,
                         defaults: dict,
                         ) -> Optional[dict]:
    """
    ---- Summary ----
    Helper function to ask the settings of the time response figure (6.1.x).

    ---- Inputs ----
    names : List[str]
        Experiment names (file names without the extension).
    answers : dict
        Answers dictionary the settings are stored in.
    defaults : dict
        Default answers.

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

    ---- Helpers ----
    choice_asker
    group_assigner
    hours_parser
    info_printer
    size_asker
    text_asker
    """

    # ---- 1 Find the experiments of each group ----------------------------------------
    info_printer("File names need a group word and the hours, e.g. 'control_7hours'.",
                 depth=2,
                 )
    text = text_asker('What are the two group words, separated by a comma?',
                      ','.join(defaults['tr_groups']),
                      depth=2,
                      )
    groups = [word.strip().lower() for word in text.split(',') if word.strip()]
    if len(groups) != 2:
        info_printer('Two group words are needed, so the time response is skipped.',
                     depth=2,
                     )
        return None
    found = group_assigner({name: {} for name in names}, groups)
    members = {name: experiment['group'] for name, experiment in found.items()}
    for group in groups:
        listed = [n for n, g in members.items() if g == group]
        listed_text = ', '.join(listed) if listed else 'no files found'
        info_printer(f'{group}: {listed_text}', depth=2)
    if any(group not in members.values() for group in groups):
        info_printer('Both groups need at least one file, so the time response is '
                     'skipped.',
                     depth=2,
                     )
        return None
    answers['tr_groups'] = groups

    # ---- 2 The two example experiments -----------------------------------------------
    timed = [n for n in members if hours_parser(n) is not None]
    options = [(n, f'{n} ({members[n]}, {hours_parser(n):g} hours)') for n in timed]
    if len(options) < 2:
        info_printer('Two experiments with hours in their name are needed for the '
                     'examples, '
                     'so the time response is skipped.',
                     depth=2,
                     )
        return None
    first_group = [n for n in timed if members[n] == groups[0]]
    saved = [n for group, hours in (defaults.get('tr_examples') or [])
             for n in timed
             if members[n] == group and hours_parser(n) == hours
             ][:2]
    top_default = saved[0] if saved else first_group[0]
    left = choice_asker('Which experiment should the top example show?',
                        options,
                        top_default,
                        depth=2,
                        )
    if len(saved) > 1:
        bottom_default = saved[1]
    elif first_group[-1] != left:
        bottom_default = first_group[-1]
    else:
        bottom_default = options[-1][0]
    right = choice_asker('Which experiment should the bottom example show?',
                         options,
                         bottom_default,
                         depth=2,
                         )
    answers['tr_examples'] = [[members[left], hours_parser(left)],
                              [members[right], hours_parser(right)],
                              ]

    # ---- 3 Figure size ---------------------------------------------------------------
    size_asker(answers,
               defaults,
               {'journal': 'tr_journal',
                'columns': 'tr_columns',
                'height': 'tr_height',
                'mode': 'tr_size_mode',
                },
               (2, 0.75),
               depth=2,
               )
    return members


# ---- _WINDOW ENSURER -----------------------------------------------------------------
def _window_ensurer(answers: dict, defaults: dict) -> None:
    """
    ---- Summary ----
    Helper function to make sure the event-window settings exist for the special
    figures: they reuse the section 3 settings, which are asked here if event
    averaging was switched off there.

    ---- Inputs ----
    answers : dict
        Answers dictionary; uses averaging, window_minutes and gap_minutes.
    defaults : dict
        Default answers.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Stores the tr_* and ho_* window answers in ``answers`` (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    averaging_asker
    info_printer
    """

    if not answers['averaging'] and not answers.get('window_asked'):
        info_printer('This figure averages around the events, like section 3.3.',
                     depth=2,
                     )
        averaging_asker(answers, defaults, forced=True, depth=2)
    for prefix in ('tr', 'ho'):
        answers[f'{prefix}_window_minutes'] = answers['window_minutes']
        answers[f'{prefix}_gap_minutes'] = answers['gap_minutes']
        answers[f'{prefix}_final_gap_minutes'] = answers['final_gap_minutes']


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- SUMMARY FIGURE ASKER ------------------------------------------------------------
def summary_figure_asker(names: List[str],
                         answers: dict,
                         defaults: dict,
                         summaries: List[dict],
                         fit: Optional[dict],
                         fits_folder: Path,
                         ) -> tuple:
    """
    ---- Summary ----
    Main function to ask section 6: whether to plot a time response and a haem and
    OCR response, and the settings of each one chosen. Both need the haem fit, which
    is asked for here if it was not chosen in section 3.

    ---- Inputs ----
    names : List[str]
        Experiment names (file names without the extension).
    answers : dict
        Answers dictionary the settings are stored in.
    defaults : dict
        Default answers.
    summaries : List[dict]
        File summaries (DATA_FORMAT.md), used if the fit has to be asked for.
    fit : Optional[dict]
        Fit dictionary chosen in section 3, or None.
    fits_folder : Path
        Folder holding the fit .csv files.

    ---- Globals read ----
    None.

    ---- Outputs ----
    tuple
        (fit, result). result is {'time_response': {name: group} or None,
        'haem_ocr': [names] or None}; None means that figure will not be made.

    ---- Globals mutated ----
    None. Stores the settings in ``answers`` (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _haem_ocr_asker
    _time_response_asker
    _window_ensurer
    decomposition_asker
    info_printer
    yes_no_asker
    """

    result = {'time_response': None, 'haem_ocr': None}
    answers['plot_time_response'] = False
    answers['plot_haem_ocr'] = False
    for key, question, asker in (('time_response',
                                  'Do you want to plot a time response?',
                                  None,
                                  ),
                                 ('haem_ocr',
                                  'Do you want to plot a haem and OCR response?',
                                  None,
                                  ),
                                 ):
        if not yes_no_asker(question, defaults[f'plot_{key}']):
            continue

        # ---- 1 Make sure the haems are decomposed ------------------------------------
        if fit is None:
            info_printer('This figure needs the haems, so they are decomposed.',
                         depth=2,
                         )
            (answers['decompose'],
             answers['fit_file'],
             fit,
             answers['decomposition_dataset'],
             ) = decomposition_asker(summaries,
                                     defaults,
                                     fits_folder,
                                     forced=True,
                                     depth=2,
                                     )
            if fit is None:
                info_printer('No haem fit is available, so this figure is skipped.',
                             depth=2,
                             )
                continue

        # ---- 2 Ask the settings of the figure ----------------------------------------
        _window_ensurer(answers, defaults)
        if key == 'time_response':
            result[key] = _time_response_asker(names, answers, defaults)
        else:
            result[key] = _haem_ocr_asker(names, answers, defaults, fit)
        answers[f'plot_{key}'] = result[key] is not None
    return fit, result
