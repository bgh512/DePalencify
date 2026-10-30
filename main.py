"""
Main program: read .paf files, process them and export figures and workbooks.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import gc
import json
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import matplotlib
matplotlib.use('Agg')  # figures are saved to files; no window is needed
import matplotlib.pyplot as plt

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_custom.custom_questions import summary_figure_asker
from utils_custom.custom_runner import (exemplar_runner,
                                        experiment_preparer,
                                        ocr_and_haem_response_runner,
                                        time_response_runner,
                                        )
from utils_shared.comparison_plotter import comparison_figure_plotter
from utils_shared.experiment_processing import experiment_data_processor
from utils_shared.figure_layout import figure_size_calculator
from utils_shared.individual_experiment_exporter import experiment_workbook_exporter
from utils_shared.individual_experiment_plotter import experiment_plotter
from utils_shared.questions import section_starter, UserQuit, yes_no_asker
from utils_shared.run_logging import logging_starter, logging_stopper
from utils_shared.survey import (analysis_asker,
                                 files_asker,
                                 haem_name_formatter,
                                 JOURNAL_NAMES,
                                 multi_experiment_asker,
                                 plot_asker,
                                 trim_asker,
                                 )
from utils_viewer.viewer_stages import viewer_asker


# ---- CONSTANTS -----------------------------------------------------------------------
HERE = Path(__file__).resolve().parent
FITS_FOLDER = HERE / 'fits'
LAST_ANSWERS_FILE = HERE / 'last_answers.json'
VERSION = (HERE / 'VERSION').read_text().strip()


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- comparison_maker ----------------------------------------------------------------
def comparison_maker(comparison: dict,
                     kept: dict,
                     cfg: settings.Config,
                     export_root: Path,
                     ) -> None:
    """
    ---- Summary ----
    Main function to draw the side-by-side figure of two chosen experiments, or to say
    why it cannot be made.

    ---- Inputs ----
    comparison : dict
        Side-by-side settings: {runs: (left, right), columns, height}.
    kept : dict
        Results of experiment_processor keyed by experiment name.
    cfg : settings.Config
        Figure style and settings derived from the answers (config.py).
    export_root : Path
        Results folder.

    ---- Globals read ----
    settings.Config (the comparison journal is read from the answers).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Writes the comparison figure files and prints the outcome (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    comparison_figure_plotter
    figure_size_calculator
    plot_config_builder
    """

    # ---- 1 Set up the comparison -----------------------------------------------------
    cfg = settings.Config(dict(cfg.answers, journal=cfg.answers['comparison_journal']))
    # The side-by-side figure of the two chosen runs (skipped, with the reason, if
    # either one failed or they were plotted differently).
    names = comparison['runs']
    first, second = (kept.get(name) for name in names)
    print(f'\nComparison: {names[0]} (a) vs {names[1]} (b)')

    # ---- 2 Check both runs can be compared -------------------------------------------
    if not (first and second):
        print('  Not made: one of the two runs did not finish.')
        return
    if (first['vo2_source'], first['haem_source']) != (second['vo2_source'],
                                                       second['haem_source'],
                                                       ):
        print('  Not made: the two runs were plotted with different data (for example '
              'only one has an OD entered).',
              )
        return

    # ---- 3 Draw and save the figure --------------------------------------------------
    try:
        size = figure_size_calculator(cfg.SPEC,
                                      comparison['columns'],
                                      comparison['height'],
                                      )
        stem = comparison_figure_plotter(first['experiment'],
                                         second['experiment'],
                                         cfg.plot_config_builder(first['vo2_source'],
                                                                 first['haem_source'],
                                                                 ),
                                         export_root,
                                         size,
                                         cfg.SPEC,
                                         )
        print(f'  Saved {stem} ({size[0] * 25.4:.0f} x {size[1] * 25.4:.0f}'
              f' mm)',
              )
    except Exception as exc:
        print(f'  Not made: {type(exc).__name__}: {exc}')
        plt.close('all')


# ---- everything_asker ----------------------------------------------------------------
def everything_asker() -> Tuple[dict,
                                Path,
                                List[dict],
                                Optional[dict],
                                Optional[dict],
                                Optional[List[str]],
                                ]:
    """
    ---- Summary ----
    Main function to ask every question of the run in numbered sections (files, trimming
    and ignoring, analysis, plots, summary figures, export) and to build the per-file
    information.

    ---- Inputs ----
    None.

    ---- Globals read ----
    FITS_FOLDER, JOURNAL_NAMES (module constants); settings.DEFAULT_ANSWERS.

    ---- Outputs ----
    Tuple[dict, Path, List[dict], Optional[dict], Optional[dict], Optional[List[str]]]
        (answers, results folder, per-experiment info dictionaries, fit, side-by-side
        comparison settings or None, names of the 2x2 grid experiments or None). Raises
        UserQuit if the user declines to start.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal; writes last_answers.json through
    last_answers_saver (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    analysis_asker
    files_asker
    haem_name_formatter
    last_answers_loader
    last_answers_saver
    multi_experiment_asker
    plot_asker
    section_starter
    summary_figure_asker
    trim_asker
    viewer_asker
    yes_no_asker
    """

    # ---- 1 Load the remembered answers -----------------------------------------------
    last = last_answers_loader()
    defaults = dict(settings.DEFAULT_ANSWERS, **last.get('answers', {}))
    answers = dict(defaults)
    remembered = last.get('files', {})

    # ---- 2 Print the banner ----------------------------------------------------------
    print('=' * 70)
    print('  DePalencify  V2.0 beta')
    print('  Questions are in colour and numbered. Type your answer on the line below')
    print('  each question; Enter accepts the value shown in [brackets].')
    print('=' * 70)

    # ---- 3 Ask the questions ---------------------------------------------------------
    # ---- 3.1 Files -------------------------------------------------------------------
    section_starter('Your files')
    folder, summaries, export_root = files_asker(last)
    names = [s['name'] for s in summaries]

    # ---- 3.2 Trimming and ignoring, analysis and individual plots --------------------
    answers['use_viewer'] = yes_no_asker('Do you want to check each step in a plot '
                                         'window as you answer (the experiment '
                                         'browser)?',
                                         defaults['use_viewer'],
                                         )
    if answers['use_viewer']:
        limits, fit, details, plotted = viewer_asker(summaries,
                                                     answers,
                                                     defaults,
                                                     remembered,
                                                     FITS_FOLDER,
                                                     export_root,
                                                     )
    else:
        section_starter('Trimming and ignoring')
        limits = trim_asker(summaries, remembered)
        answers['ignore_first_minutes'] = max(v['ignore_start']
                                              for v in limits.values()
                                              )
        answers['ignore_last_minutes'] = max(v['ignore_end'] for v in limits.values())
        section_starter('Analysis')
        fit, details = analysis_asker(summaries,
                                      answers,
                                      defaults,
                                      FITS_FOLDER,
                                      export_root,
                                      )
        section_starter('Individual experiment plots')
        plotted = plot_asker(answers, defaults, fit)

    # ---- 3.5 Multi-experiment plots --------------------------------------------------
    section_starter('Multi-experiment plots')
    comparison, exemplar_names = multi_experiment_asker(summaries,
                                                        answers,
                                                        defaults,
                                                        plotted,
                                                        )

    # ---- 3.6 Experiment summaries ----------------------------------------------------
    section_starter('Experiment summaries')
    fit, custom = summary_figure_asker(names,
                                       answers,
                                       defaults,
                                       summaries,
                                       fit,
                                       FITS_FOLDER,
                                       )

    # ---- 3.7 Data export -------------------------------------------------------------
    section_starter('Data export')
    print('  Every experiment always gets a workbook with CcO2, CsO2, VoO2, the events'
          ' and your OD/volume/dilution entries.',
          )
    answers['export_full'] = yes_no_asker('Do you want to put every processed table in'
                                          ' the workbook (OD-scaled, haems, percent, '
                                          '...)?',
                                          defaults['export_full'],
                                          )
    answers['export_spectra'] = yes_no_asker('Do you want to export the spectra as csv'
                                             ' files (large, and it takes a while)?',
                                             defaults['export_spectra'],
                                             )

    # ---- 4 Read the experiments ------------------------------------------------------
    experiments = []
    for s in summaries:
        name = s['name']
        info = {'path': s['path'],
                'name': name,
                'duration': s['duration_min'],
                'trim_start': limits[name]['trim_start'],
                'trim_end': limits[name]['trim_end'],
                'ignore_start': limits[name]['ignore_start'],
                'ignore_end': limits[name]['ignore_end'],
                'custom': {'time_response_group': (custom['time_response'] or {}
                                                   ).get(name),
                           'haem_ocr': name in (custom['haem_ocr'] or []),
                           },
                'exemplar': name in (exemplar_names or []),
                }
        info['keep'] = ((bool(comparison) and name in comparison['runs']) or
                        info['exemplar'] or
                        bool(info['custom']['time_response_group']) or
                        info['custom']['haem_ocr']
                        )
        info.update(details[name])
        experiments.append(info)

    # ---- 5 Print the summary ---------------------------------------------------------
    section_starter('Summary')
    print(f'  Files:            {len(experiments)} from {folder}')
    print(f'  Results to:       {export_root}')
    spans = {}
    for name, v in limits.items():
        if v['trim_start'] or v['trim_end']:
            spans.setdefault((v['trim_start'] or 0, v['trim_end']), []).append(name)
    trimmed = [f"{('all files' if len(names) == len(limits) else ', '.join(names))}: "
               f"{'from %g ' % start if start else ''}{'to %g ' % end if end else ''}"
               f'min'
               for (start, end), names in spans.items()
               ]
    print(f"  Trimmed:          {', '.join(trimmed) or 'none'}")
    ignore_spans = {}
    for name, v in limits.items():
        ignore_spans.setdefault((v['ignore_start'] or 0, v['ignore_end'] or 0),
                                [],
                                ).append(name)
    ignored = [f"{('all files' if len(names) == len(limits) else ', '.join(names))}: "
               f'first {start:g} min, last {end:g} min'
               for (start, end), names in ignore_spans.items()
               ]
    print(f"  Ignored:          {'; '.join(ignored) or 'none'}")
    print(f'  Decomposition:    '
          f"{answers['fit_file'] if answers['decompose'] else 'no'}",
          )
    print(f"  OD scaling:       {'yes' if answers['normalise_od'] else 'no'}")
    averaging_text = 'no'
    if answers['averaging']:
        averaging_text = ('%g min window, ending %g min before the next addition'
                          % (answers['window_minutes'], answers['gap_minutes'])
                          )
    print(f'  Event averaging:  {averaging_text}')
    haem_names = [haem_name_formatter(name) for name in answers['haems']]
    shown = [name
             for name, on in (('O2', answers['plot_o2']),
                              (f"OCR ({answers['ocr_mode']})", answers['plot_ocr']),
                              (f"haems {', '.join(haem_names)} ("
                               f"{answers['haem_mode']})",
                               answers['plot_haems'],
                               ),
                              )
             if on
             ]
    print(f"  Plots:            {'; '.join(shown) or 'none'}")
    print(f"  Individual:       {JOURNAL_NAMES[answers['journal']]}, "
          f"{answers['columns']:g} column(s), height {answers['height']:g} of a page",
          )
    if comparison:
        print(f"  Side by side:     {comparison['runs'][0]} (a) vs "
              f"{comparison['runs'][1]} (b), "
              f"{JOURNAL_NAMES[answers['comparison_journal']]}, "
              f"{comparison['columns']:g} column(s), height {comparison['height']:g}",
              )
    if exemplar_names:
        print(f"  2x2 grid:         run {answers['ho_exemplar_run']}, "
              f"{JOURNAL_NAMES[answers['ex_journal']]}, {answers['ho_ex_columns']:g} "
              f"column(s), height {answers['ho_ex_height']:g}",
              )
    if answers['plot_time_response']:
        print(f"  Time response:    groups {', '.join(answers['tr_groups'])}, "
              f"{JOURNAL_NAMES[answers['tr_journal']]}, {answers['tr_columns']:g} "
              f"column(s), height {answers['tr_height']:g}",
              )
    if answers['plot_haem_ocr']:
        print(f"  Haem and OCR:     {len(custom['haem_ocr'])} file(s), "
              f"{JOURNAL_NAMES[answers['ho_journal']]}, {answers['ho_pub_columns']:g} "
              f"column(s), height {answers['ho_pub_height']:g}",
              )
    print(f'  Workbooks:        '
          f"{'all processed data' if answers['export_full'] else 'CcO2, CsO2, VoO2'}"
          f"{' + spectra csv' if answers['export_spectra'] else ''}",
          )

    # ---- 6 Confirm the start ---------------------------------------------------------
    if not yes_no_asker('Do you want to start?', True):
        raise UserQuit()

    # ---- 7 Remember the answers ------------------------------------------------------
    files = dict(remembered)
    files.update({name: dict(v) for name, v in limits.items()})
    last_answers_saver({'data_folder': str(folder),
                        'export_folder': str(export_root),
                        'files': files,
                        'answers': {k: v
                                    for k, v in answers.items()
                                    if k not in ('haems', 'ho_haems') or v
                                    },
                        },
                       )
    return answers, export_root, experiments, fit, comparison, exemplar_names


# ---- experiment_processor ------------------------------------------------------------
def experiment_processor(info: dict,
                         cfg: settings.Config,
                         fit: Optional[dict],
                         export_root: Path,
                         ) -> Optional[dict]:
    """
    ---- Summary ----
    Main function to read, process, plot and export one .paf file. Each step reports its
    own problem so the next step still runs.

    ---- Inputs ----
    info : dict
        Per-file information from everything_asker: path, name, trim and ignore times,
        OD values, events, custom and keep flags.
    cfg : settings.Config
        Figure style and settings derived from the answers (config.py).
    fit : Optional[dict]
        Fit dictionary from import_fit ({haem_list, data}), or None when the haems are
        not decomposed.
    export_root : Path
        Results folder.

    ---- Globals read ----
    plt (matplotlib.pyplot).

    ---- Outputs ----
    Optional[dict]
        {experiment, vo2_source, haem_source, prepared} when the experiment is needed
        again for the comparison or special figures (info["keep"]), otherwise None.

    ---- Globals mutated ----
    None. Writes the figure and the workbook files and prints progress (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    experiment_data_processor
    experiment_plotter
    experiment_preparer
    experiment_workbook_exporter
    plot_config_builder
    """

    # ---- 1 Set up the run ------------------------------------------------------------
    a = cfg.answers
    name = info['name']
    ignore_first, ignore_last = info['ignore_start'], info['ignore_end']
    print(f'\nProcessing: {name}')

    # ---- 2 Read and process the data -------------------------------------------------
    processed = experiment_data_processor(info, cfg, fit)
    experiment = processed['experiment']
    metadata = experiment['metadata']
    od_available = processed['od_available']
    vo2_source, haem_source = processed['vo2_source'], processed['haem_source']

    # ---- 6 Plot the experiment -------------------------------------------------------
    # Figure.
    haem_panels = a['plot_haems'] and 'haem_conc' in experiment
    if a['plot_o2'] or a['plot_ocr'] or haem_panels:
        try:
            print('  Plotting ...')
            experiment_plotter(experiment,
                               cfg.plot_config_builder(vo2_source,
                                                       haem_source
                                                       if haem_panels
                                                       else None,
                                                       ignore_first,
                                                       ignore_last,
                                                       ),
                               export_root,
                               )
        except Exception as exc:  # a figure problem must not lose the data export
            print(f'  Figure not made: {type(exc).__name__}: {exc}')
            plt.close('all')

    # ---- 7 Export the workbook -------------------------------------------------------
    # Workbook.
    metadata.update({'ignore_first_minutes': ignore_first,
                     'ignore_last_minutes': ignore_last,
                     'fit_file': a['fit_file'] if a['decompose'] else None,
                     'processed': datetime.now().strftime('%Y-%m-%d %H:%M'),
                     },
                    )
    print('  Exporting ...')
    experiment_workbook_exporter(experiment,
                                 export_root,
                                 full=a['export_full'],
                                 spectra=a['export_spectra'],
                                 )

    # ---- 8 Prepare the special figures -----------------------------------------------
    # the special figures
    prepared = experiment_preparer(experiment, info['custom'], a, fit, od_available)
    if info.get('keep'):  # needed again for the comparison and special figures
        experiment['raw_spectra'] = {}
        for item in prepared.values():
            if item is not None:
                item['raw_spectra'] = {}
        return {'experiment': experiment,
                'vo2_source': vo2_source,
                'haem_source': haem_source if haem_panels else None,
                'prepared': prepared,
                }
    return None


# ---- last_answers_loader -------------------------------------------------------------
def last_answers_loader() -> dict:
    """
    ---- Summary ----
    Main function to read the answers remembered from the last run.

    ---- Inputs ----
    None.

    ---- Globals read ----
    LAST_ANSWERS_FILE (module constant).

    ---- Outputs ----
    dict
        Contents of last_answers.json (data_folder, export_folder, answers, files); an
        empty dict when the file is missing or unreadable.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    try:
        return json.loads(LAST_ANSWERS_FILE.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {}


# ---- last_answers_saver --------------------------------------------------------------
def last_answers_saver(values: dict) -> None:
    """
    ---- Summary ----
    Main function to remember the answers of this run for the next one.

    ---- Inputs ----
    values : dict
        Content to write to last_answers.json: data_folder, export_folder, files and
        answers.

    ---- Globals read ----
    LAST_ANSWERS_FILE (module constant).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Writes last_answers.json (side effect); a read-only folder is ignored
    silently.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    try:
        LAST_ANSWERS_FILE.write_text(json.dumps(values, indent=2), encoding='utf-8')
    except OSError:
        pass  # a read-only folder just means the defaults are not remembered


# ---- main ----------------------------------------------------------------------------
def main() -> int:
    """
    ---- Summary ----
    Main function of the program: ask the questions, process every file, then draw the
    comparison and special figures, logging the output to a file.

    ---- Inputs ----
    None.

    ---- Globals read ----
    VERSION (written to the log).

    ---- Outputs ----
    int
        0 when every file finished, 1 when the run was cancelled or a file failed.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal, sets the matplotlib rcParams, writes
    results and a log file, and replaces sys.stdout and sys.stderr while logging (side
    effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    comparison_maker
    everything_asker
    experiment_processor
    logging_starter
    logging_stopper
    special_figures_maker
    """

    # ---- 1 Make the output safe for symbols ------------------------------------------
    for stream in (sys.stdout, sys.stderr):
        try:
            # symbols such as the delta never stop the program
            stream.reconfigure(errors='replace')
        except (AttributeError, ValueError):
            pass
    try:
        (answers,
         export_root,
         experiments,
         fit,
         comparison,
         exemplar_names,
         ) = everything_asker()
    except (UserQuit, KeyboardInterrupt):
        print('\nCancelled. Nothing was changed.')
        return 1

    # ---- 2 Set up the run ------------------------------------------------------------
    cfg = settings.Config(answers)
    plt.rcParams.update(cfg.RC_PARAMS)
    start = time.perf_counter()
    log_session = logging_starter(export_root, VERSION, answers)
    failed = []
    kept = {}

    # ---- 3 Process every file --------------------------------------------------------
    try:
        for warning in cfg.STYLE_WARNINGS:
            print(f'Figure style warning: {warning}')
        for info in experiments:
            try:
                result = experiment_processor(info, cfg, fit, export_root)
                if result:
                    kept[info['name']] = result
            except KeyboardInterrupt:
                raise
            except Exception as exc:
                print(f"  FAILED: {info['name']}: {type(exc).__name__}: {exc}")
                print(traceback.format_exc())
                failed.append(info['name'])
            finally:
                plt.close('all')
                gc.collect()
        if comparison:
            comparison_maker(comparison, kept, cfg, export_root)
        special_figures_maker(kept, cfg, fit, export_root, exemplar_names)
        minutes, seconds = divmod(time.perf_counter() - start, 60)
        print(f'\nFinished {len(experiments) - len(failed)} of {len(experiments)} '
              f'file(s) in {int(minutes)} min {seconds:.0f} s.',
              )
        if failed:
            print('Not completed: ' + ', '.join(failed) +
                  ' (details above and in the log file)',
                  )
        print(f'Results are in: {export_root}')
    except KeyboardInterrupt:
        print('\nStopped. Files finished so far are in: ' + str(export_root))
    finally:
        logging_stopper(log_session)
    return 1 if failed else 0


# ---- special_figures_maker -----------------------------------------------------------
def special_figures_maker(kept: dict,
                          cfg: settings.Config,
                          fit: Optional[dict],
                          export_root: Path,
                          exemplar_names: Optional[List[str]],
                          ) -> None:
    """
    ---- Summary ----
    Main function to draw the time response, haem and OCR response and 2x2 grid figures;
    each is skipped, with the reason, if it cannot be made.

    ---- Inputs ----
    kept : dict
        Results of experiment_processor keyed by experiment name.
    cfg : settings.Config
        Figure style and settings derived from the answers (config.py).
    fit : Optional[dict]
        Fit dictionary from import_fit ({haem_list, data}), or None when the haems are
        not decomposed.
    export_root : Path
        Results folder.
    exemplar_names : Optional[List[str]]
        Names of the four experiments of the 2x2 grid, or None.

    ---- Globals read ----
    settings.Config; time_response_runner, ocr_and_haem_response_runner and
    exemplar_runner (imported).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Writes the figure files and prints the outcome (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    exemplar_runner
    ocr_and_haem_response_runner
    time_response_runner
    """

    # ---- 1 Set up the figures --------------------------------------------------------
    a = cfg.answers
    journals = {'time_response': 'tr_journal', 'haem_ocr': 'ho_journal'}

    # ---- 2 Draw the summary figures --------------------------------------------------
    for key, enabled, title, runner in (('time_response',
                                         a['plot_time_response'],
                                         'Time response',
                                         time_response_runner,
                                         ),
                                        ('haem_ocr',
                                         a['plot_haem_ocr'],
                                         'Haem and OCR response',
                                         ocr_and_haem_response_runner,
                                         ),
                                        ):
        if not enabled:
            continue
        print(f'\n{title}')
        prepared = {name: item['prepared'][key]
                    for name, item in kept.items()
                    if item['prepared'].get(key) is not None
                    }
        if len(prepared) < 2:
            print(f'  Not made: only {len(prepared)} file(s) could be prepared (at '
                  f'least two are needed).',
                  )
            continue
        try:
            figure_cfg = settings.Config(dict(a, journal=a[journals[key]]))
            runner(prepared, figure_cfg, a, fit, export_root)
        except Exception as exc:  # one special figure must not stop the others
            print(f'  Not made: {type(exc).__name__}: {exc}')
            print(traceback.format_exc())
            plt.close('all')

    # ---- 3 Draw the exemplar figure --------------------------------------------------
    if a['plot_exemplar']:
        print('\n2x2 figure')
        chosen = {name: kept[name] for name in (exemplar_names or []) if name in kept}
        if len(chosen) < 4:
            print(f'  Not made: only {len(chosen)} of the four experiments finished.')
            return
        try:
            exemplar_runner(chosen,
                            settings.Config(dict(a, journal=a['ex_journal'])),
                            a,
                            fit,
                            export_root,
                            )
        except Exception as exc:
            print(f'  Not made: {type(exc).__name__}: {exc}')
            print(traceback.format_exc())
            plt.close('all')


if __name__ == '__main__':
    sys.exit(main())
