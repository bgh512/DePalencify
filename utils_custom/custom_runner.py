"""Preparation of single experiments and drawing of the custom figures."""
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt

import config as settings
from config import Config
from utils_custom.custom_config import (OUTPUT_SUBFOLDER,
                                        exemplar_config_builder,
                                        individual_config_builder,
                                        publication_config_builder,
                                        source_selector,
                                        time_response_config_builder,
                                        )
from utils_custom.publication_plotter import (exemplar_figure_plotter,
                                              publication_figure_plotter,
                                              publication_figure_saver,
                                              )
from utils_custom.spectral_difference import (difference_spectrum_calculator,
                                              difference_spectrum_decomposer,
                                              spectral_averager,
                                              )
from utils_custom.time_response_exporter import time_response_exporter
from utils_custom.time_response_plotter import (time_response_figure_plotter,
                                                time_response_figure_saver,
                                                )
from utils_custom.triplicate_averager import triplicate_averager
from utils_custom.triplicate_exporter import triplicate_exporter
from utils_shared.averaging import calculate_experiment_averages


# ---- TIME RESPONSE PREPARER ----------------------------------------------------------

def _time_response_preparer(experiment: dict,
                            group: str,
                            answers: dict,
                            fit: dict,
                            ) -> dict:
    """
    ---- Summary ----
    Helper function to average the spectra in the event windows, subtract the last two
    windows and decompose the difference spectrum, on a copy of one experiment.

    ---- Inputs ----
    experiment : dict
        Processed experiment with attenuation spectra (DATA_FORMAT.md).
    group : str
        Group the experiment belongs to.
    answers : dict
        Terminal answers; uses decomposition_dataset and the tr_* windows.
    fit : dict
        Fit dictionary from import_fit.

    ---- Globals read ----
    config.DEGREE_OF_SCATTER, config.HAEM_FACTOR.

    ---- Outputs ----
    dict
        Shallow copy of the experiment with group, spectral_averages,
        difference_spectrum and difference_decomposition added.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None. See spectral_difference.py.
    """
    prepared = dict(experiment)
    prepared['group'] = group
    spectral_averager(prepared,
                      answers['decomposition_dataset'],
                      'attenuation',
                      answers['tr_window_minutes'],
                      answers['tr_gap_minutes'],
                      answers['tr_final_gap_minutes'],
                      None,
                      )
    difference_spectrum_calculator(prepared, 'penultimate', 'final')
    difference_spectrum_decomposer(prepared,
                                   fit,
                                   settings.DEGREE_OF_SCATTER,
                                   settings.HAEM_FACTOR,
                                   'signed',
                                   )
    return prepared


# ---- HAEM OCR PREPARER ---------------------------------------------------------------

def _haem_ocr_preparer(experiment: dict,
                       answers: dict,
                       od_available: bool,
                       ) -> Optional[dict]:
    """
    ---- Summary ----
    Helper function to calculate the event-window averages used by the haem and OCR
    response figures, on a copy of one experiment.

    ---- Inputs ----
    experiment : dict
        Processed experiment (DATA_FORMAT.md).
    answers : dict
        Terminal answers; uses the ho_* settings.
    od_available : bool
        True when OD, volume and dilution factor were available for this experiment.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[dict]
        Shallow copy with 'averages' added, or None when the experiment lacks the OD
        values the chosen sources need (it would not be comparable with the others).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.
    """
    needs_od = answers['ho_ocr_mode'] == 'od' or answers['ho_per_od']
    if needs_od and not od_available:
        print('  Left out of the haem and OCR response: OD, volume or dilution '
              'factor is missing, and the other runs are scaled by OD.',
              )
        return None
    vo2_source, haem_source = source_selector(answers, od_available)
    prepared = dict(experiment)
    calculate_experiment_averages(prepared,
                                  window_minutes=answers['ho_window_minutes'],
                                  gap_minutes=answers['ho_gap_minutes'],
                                  final_window_gap_minutes=(
                                      answers['ho_final_gap_minutes']),
                                  vo2_source=vo2_source,
                                  haem_source=haem_source,
                                  )
    return prepared


# ---- EXPERIMENT PREPARER -------------------------------------------------------------

def experiment_preparer(experiment: dict,
                        custom: dict,
                        answers: dict,
                        fit: Optional[dict],
                        od_available: bool,
                        ) -> dict:
    """
    ---- Summary ----
    Main function to prepare one processed experiment for the special figures. Each
    figure is prepared on its own, so a problem with one does not stop the other.

    ---- Inputs ----
    experiment : dict
        Processed experiment with its spectra still attached (DATA_FORMAT.md).
    custom : dict
        {'time_response_group': group or None, 'haem_ocr': bool} for this experiment.
    answers : dict
        Terminal answers.
    fit : Optional[dict]
        Fit dictionary from import_fit.
    od_available : bool
        True when OD, volume and dilution factor were available.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        {'time_response': prepared experiment or None, 'haem_ocr': prepared
        experiment or None}.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.
    """
    prepared = {'time_response': None, 'haem_ocr': None}
    if custom.get('time_response_group') and fit is not None:
        try:
            group = custom['time_response_group']
            prepared['time_response'] = _time_response_preparer(experiment,
                                                                group,
                                                                answers,
                                                                fit,
                                                                )
            print('  Time response: spectra averaged, difference spectrum decomposed')
        except (KeyError, ValueError, TypeError) as exc:
            print(f'  Time response skipped for this file: {exc}')
    if custom.get('haem_ocr'):
        try:
            prepared['haem_ocr'] = _haem_ocr_preparer(experiment,
                                                      answers,
                                                      od_available,
                                                      )
            if prepared['haem_ocr'] is not None:
                print('  Haem and OCR response: event averages calculated')
        except (KeyError, ValueError, TypeError) as exc:
            print(f'  Haem and OCR response skipped for this file: {exc}')
    return prepared


# ---- TIME RESPONSE RUNNER ------------------------------------------------------------

def time_response_runner(experiments: dict,
                         cfg: Config,
                         answers: dict,
                         fit: dict,
                         export_root: Path,
                         ) -> None:
    """
    ---- Summary ----
    Main function to export and draw the time response figure from the prepared
    experiments.

    ---- Inputs ----
    experiments : dict
        Prepared experiments keyed by name, each with group and
        difference_decomposition (DATA_FORMAT.md).
    cfg : Config
        Figure style derived from the answers.
    answers : dict
        Terminal answers.
    fit : dict
        Fit dictionary from import_fit.
    export_root : Path
        Results folder.

    ---- Globals read ----
    custom_config.OUTPUT_SUBFOLDER.

    ---- Outputs ----
    None
        Nothing; files are written.

    ---- Globals mutated ----
    None. Writes the CSV summaries and the figure files (side effect).

    ---- Equations ----
    None.
    """

    # ---- 1 Choose the data plotted in the examples ----------------------------
    haem_names = list(fit['haem_list'])
    with_od = all('VoO2_OD' in e and 'haem_delta_abs_OD' in e
                  for e in experiments.values()
                  )
    vo2_source = 'od' if with_od else 'raw'
    haem_source = 'delta_abs_od' if with_od else 'delta_abs'
    individual = individual_config_builder(answers, vo2_source, haem_source, haem_names)
    config = time_response_config_builder(cfg, answers, haem_names)

    # ---- 2 Export the summary tables -------------------------------------------
    folder = Path(export_root) / config['OUTPUT_SUBFOLDER']
    time_response_exporter(experiments, folder, config['TIME_LABEL_FORMAT'])

    # ---- 3 Draw and save the figure --------------------------------------------
    fig, _ = time_response_figure_plotter(experiments, config, individual)
    time_response_figure_saver(fig, export_root, config)
    plt.close(fig)


# ---- HAEM OCR RUNNER -----------------------------------------------------------------

def haem_ocr_runner(experiments: dict,
                    cfg: Config,
                    answers: dict,
                    fit: dict,
                    export_root: Path,
                    ) -> None:
    """
    ---- Summary ----
    Main function to combine the runs of each condition and draw the haem and OCR
    response: the publication figure and the four-run exemplar figure. The two
    figures are drawn independently, so a problem with one does not stop the other.

    ---- Inputs ----
    experiments : dict
        Prepared experiments keyed by name, each with averages (DATA_FORMAT.md).
    cfg : Config
        Figure style derived from the answers.
    answers : dict
        Terminal answers.
    fit : dict
        Fit dictionary from import_fit.
    export_root : Path
        Results folder.

    ---- Globals read ----
    custom_config.OUTPUT_SUBFOLDER.

    ---- Outputs ----
    None
        Nothing; files are written.

    ---- Globals mutated ----
    None. Writes the workbook and the figure files (side effect).

    ---- Equations ----
    None.
    """

    # ---- 1 Combine the runs of each condition ----------------------------------
    triplicates = triplicate_averager(experiments)
    if not triplicates:
        print('  Not made: every condition needs at least two runs with averages.')
        return
    workbook = Path(export_root) / OUTPUT_SUBFOLDER / 'triplicate_summary.xlsx'
    triplicate_exporter(triplicates, workbook)

    # ---- 2 Publication figure --------------------------------------------------
    haem_names = list(fit['haem_list'])
    try:
        config = publication_config_builder(cfg, answers, haem_names)
        fig, _ = publication_figure_plotter(experiments, triplicates, config)
        publication_figure_saver(fig, export_root, config)
        plt.close(fig)
    except Exception as exc:  # keep the exemplar figure going
        print(f'  Publication figure not made: {type(exc).__name__}: {exc}')
        plt.close('all')

    # ---- 3 Exemplar figure -----------------------------------------------------
    try:
        settings_used = next(iter(triplicates.values()))['settings']
        shown = [h for h in haem_names if h in answers['ho_haems']]
        individual = individual_config_builder(answers,
                                               settings_used['vo2_source'],
                                               settings_used['haem_source'],
                                               shown,
                                               )
        config = exemplar_config_builder(cfg, answers)
        fig, _ = exemplar_figure_plotter(experiments, config, individual)
        publication_figure_saver(fig, export_root, config)
        plt.close(fig)
    except Exception as exc:
        print(f'  Exemplar figure not made: {type(exc).__name__}: {exc}')
        plt.close('all')
