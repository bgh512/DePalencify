"""
Preparation of single experiments and drawing of the custom figures.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from pathlib import Path
from typing import Optional

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import matplotlib.pyplot as plt

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from config import Config
from utils_custom.custom_config import (exemplar_config_builder,
                                        individual_config_builder,
                                        ocr_and_haem_response_config_builder,
                                        source_selector,
                                        time_response_config_builder,
                                        )
from utils_custom.custom_figure_saver import custom_figure_saver
from utils_custom.exemplar_plotter import exemplar_figure_plotter
from utils_custom.ocr_and_haem_response_exporter import ocr_and_haem_response_exporter
from utils_custom.ocr_and_haem_response_plotter import (
    ocr_and_haem_response_figure_plotter,
)
from utils_custom.spectral_difference import (difference_spectrum_calculator,
                                              difference_spectrum_decomposer,
                                              spectral_averager,
                                              )
from utils_custom.time_response_exporter import time_response_exporter
from utils_custom.time_response_plotter import time_response_figure_plotter
from utils_custom.triplicate_averager import triplicate_averager
from utils_shared.averaging import experiment_averages_calculator


# ---- CUSTOM RUNNER HELPERS -----------------------------------------------------------


# ---- _ocr_and_haem_response_preparer -------------------------------------------------
def _ocr_and_haem_response_preparer(experiment: dict,
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

    ---- Helpers ----
    experiment_averages_calculator
    source_selector
    """

    # ---- 1 Check the inputs ----------------------------------------------------------
    needs_od = answers['ho_ocr_mode'] == 'od' or answers['ho_per_od']
    if needs_od and not od_available:
        print('  Left out of the haem and OCR response: OD, volume or dilution '
              'factor is missing, and the other runs are scaled by OD.',
              )
        return None

    # ---- 2 Select the data sources ---------------------------------------------------
    vo2_source, haem_source = source_selector(answers, od_available)

    # ---- 3 Average the experiment ----------------------------------------------------
    prepared = dict(experiment)
    final_gap = answers['ho_final_gap_minutes']
    experiment_averages_calculator(prepared,
                                   window_minutes=answers['ho_window_minutes'],
                                   gap_minutes=answers['ho_gap_minutes'],
                                   final_window_gap_minutes=final_gap,
                                   vo2_source=vo2_source,
                                   haem_source=haem_source,
                                   )
    return prepared


# ---- _time_response_preparer ---------------------------------------------------------
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

    ---- Helpers ----
    difference_spectrum_calculator
    difference_spectrum_decomposer
    spectral_averager
    """

    # ---- 1 Copy and label the experiment ---------------------------------------------
    prepared = dict(experiment)
    prepared['group'] = group

    # ---- 2 Average the spectra -------------------------------------------------------
    spectral_averager(prepared,
                      answers['decomposition_dataset'],
                      'attenuation',
                      answers['tr_window_minutes'],
                      answers['tr_gap_minutes'],
                      answers['tr_final_gap_minutes'],
                      None,
                      )

    # ---- 3 Calculate and decompose the difference spectrum ---------------------------
    difference_spectrum_calculator(prepared, 'penultimate', 'final')
    difference_spectrum_decomposer(prepared,
                                   fit,
                                   settings.DEGREE_OF_SCATTER,
                                   settings.HAEM_FACTOR,
                                   'signed',
                                   )
    return prepared


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- exemplar_runner -----------------------------------------------------------------
def exemplar_runner(chosen: dict,
                    cfg: Config,
                    answers: dict,
                    fit: Optional[dict],
                    export_root: Path,
                    ) -> None:
    """
    ---- Summary ----
    Main function to draw the 2x2 figure: one experiment for each strain and addition
    order, plotted like the individual experiment figures.

    ---- Inputs ----
    chosen : dict
        {experiment name: kept result of process_experiment} with the keys
        experiment, vo2_source and haem_source (DATA_FORMAT.md).
    cfg : Config
        Figure style of this figure (its own journal).
    answers : dict
        Terminal answers; uses haems, plot_haems and the ho_ex_* and ho_exemplar_run
        settings.
    fit : Optional[dict]
        Fit dictionary, or None when the haems were not decomposed.
    export_root : Path
        Results folder.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing; the figure files are written.

    ---- Globals mutated ----
    None. Writes the figure files (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    custom_figure_saver
    exemplar_config_builder
    exemplar_figure_plotter
    individual_config_builder
    """

    # ---- 1 Choose the data plotted ---------------------------------------------------
    experiments = {name: item['experiment'] for name, item in chosen.items()}
    first = next(iter(chosen.values()))
    shown = []
    if fit is not None and answers['plot_haems']:
        shown = [h for h in answers['haems'] if h in fit['haem_list']]
    haem_source = first['haem_source'] if shown else None
    figure_answers = dict(answers, journal=cfg.answers['journal'])
    individual = individual_config_builder(figure_answers,
                                           first['vo2_source'],
                                           haem_source,
                                           shown,
                                           )

    # ---- 2 Draw and save the figure --------------------------------------------------
    config = exemplar_config_builder(cfg, answers)
    fig, _ = exemplar_figure_plotter(experiments, config, individual)
    custom_figure_saver(fig, export_root, config)
    plt.close(fig)


# ---- experiment_preparer -------------------------------------------------------------
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

    ---- Helpers ----
    _ocr_and_haem_response_preparer
    _time_response_preparer
    """

    # ---- 1 Set up the result ---------------------------------------------------------
    prepared = {'time_response': None, 'haem_ocr': None}

    # ---- 2 Prepare the time response -------------------------------------------------
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

    # ---- 3 Prepare the haem and OCR response -----------------------------------------
    if custom.get('haem_ocr'):
        try:
            prepared['haem_ocr'] = _ocr_and_haem_response_preparer(experiment,
                                                                   answers,
                                                                   od_available,
                                                                   )
            if prepared['haem_ocr'] is not None:
                print('  Haem and OCR response: event averages calculated')
        except (KeyError, ValueError, TypeError) as exc:
            print(f'  Haem and OCR response skipped for this file: {exc}')
    return prepared


# ---- ocr_and_haem_response_runner ----------------------------------------------------
def ocr_and_haem_response_runner(experiments: dict,
                                 cfg: Config,
                                 answers: dict,
                                 fit: dict,
                                 export_root: Path,
                                 ) -> None:
    """
    ---- Summary ----
    Main function to combine the runs of each condition, draw the OCR and haem response
    figure and write the workbook behind it. A problem with the figure does not stop
    the workbook, and neither stops the 2x2 figure, which is drawn separately.

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
    None.

    ---- Outputs ----
    None
        Nothing; files are written.

    ---- Globals mutated ----
    None. Writes ocr_and_haem_response.xlsx and the figure files to ``export_root``
    (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    custom_figure_saver
    ocr_and_haem_response_config_builder
    ocr_and_haem_response_exporter
    ocr_and_haem_response_figure_plotter
    triplicate_averager
    """

    # ---- 1 Combine the runs of each condition ----------------------------------------
    triplicates = triplicate_averager(experiments)
    if not triplicates:
        print('  Not made: every condition needs at least two runs with averages.')
        return

    # ---- 2 Draw and save the figure --------------------------------------------------
    haem_names = list(fit['haem_list'])
    config = ocr_and_haem_response_config_builder(cfg, answers, haem_names)
    tests, baseline = [], None
    try:
        fig, _ = ocr_and_haem_response_figure_plotter(experiments, triplicates, config)
        tests, baseline = fig.response_tests, fig.response_baseline
        custom_figure_saver(fig, export_root, config)
        plt.close(fig)
    except Exception as exc:  # keep the workbook and the 2x2 figure going
        print(f'  OCR and haem response figure not made: {type(exc).__name__}: {exc}')
        plt.close('all')

    # ---- 3 Write the workbook --------------------------------------------------------
    ocr_and_haem_response_exporter(triplicates,
                                   tests,
                                   baseline,
                                   Path(export_root) / f"{config['FILE_NAME']}.xlsx",
                                   )


# ---- time_response_runner ------------------------------------------------------------
def time_response_runner(experiments: dict,
                         cfg: Config,
                         answers: dict,
                         fit: dict,
                         export_root: Path,
                         ) -> None:
    """
    ---- Summary ----
    Main function to draw the time response figure from the prepared experiments and
    write the workbook behind it.

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
    None.

    ---- Outputs ----
    None
        Nothing; files are written.

    ---- Globals mutated ----
    None. Writes time_response.xlsx and the figure files to ``export_root`` (side
    effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    custom_figure_saver
    individual_config_builder
    time_response_config_builder
    time_response_exporter
    time_response_figure_plotter
    """

    # ---- 1 Choose the data plotted in the examples -----------------------------------
    haem_names = list(fit['haem_list'])
    with_od = all('VoO2_OD' in e and 'haem_delta_abs_OD' in e
                  for e in experiments.values()
                  )
    vo2_source = 'od' if with_od else 'raw'
    haem_source = 'delta_abs_od' if with_od else 'delta_abs'
    individual = individual_config_builder(answers, vo2_source, haem_source, haem_names)
    config = time_response_config_builder(cfg, answers, haem_names)

    # ---- 2 Draw and save the figure --------------------------------------------------
    fig, _ = time_response_figure_plotter(experiments, config, individual)
    picks = fig.time_response_picks
    custom_figure_saver(fig, export_root, config)
    plt.close(fig)

    # ---- 3 Write the workbook --------------------------------------------------------
    time_response_exporter(experiments,
                           config,
                           picks,
                           Path(export_root) / f"{config['FILE_NAME']}.xlsx",
                           )
