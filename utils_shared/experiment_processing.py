"""
Reading and processing of one experiment (everything before the figure and the export).
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from typing import List, Optional

# ---- LOCAL IMPORTS -------------------------------------------------------------------
import config as settings
from utils_shared.attenuation import experiment_attenuation_adder
from utils_shared.averaging import experiment_averages_calculator
from utils_shared.normalisation import experiment_normaliser, percent_converter
from utils_shared.paf_reader import experiment_paf_loader, PafError
from utils_shared.spectral_decomposer import experiment_decomposer
from utils_shared.trimming import experiment_trimmer


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- event_settings_merger -----------------------------------------------------------
def event_settings_merger(experiment: dict, events: List[dict]) -> None:
    """
    ---- Summary ----
    Main function to copy the label, concentration and ignored flag entered for each
    event onto the experiment, and to move ignored events out of the working event list.

    ---- Inputs ----
    experiment : dict
        Experiment dictionary, as defined in DATA_FORMAT.md.
    events : List[dict]
        Entered events: {datapoint, label, concentration_uM, ignored}.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Updates experiment["metadata"]["events"] in place and adds
    experiment["metadata"]["ignored_events"] (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 Apply the entered settings to the events ----------------------------------
    entered = {e['datapoint']: e for e in events}
    for event in experiment['metadata'].get('events', []):
        item = entered.get(event['datapoint'])
        if item:
            event['label'] = item['label'] or event['text']
            event['concentration_uM'] = item['concentration_uM']
            event['ignored'] = bool(item.get('ignored', False))

    # ---- 2 Separate the ignored events -----------------------------------------------
    # Ignored events leave the working list (so nothing plots or averages them) but are
    # kept in metadata["ignored_events"] so the workbook still records them.
    metadata = experiment['metadata']
    events = metadata.get('events', [])
    metadata['ignored_events'] = [e for e in events if e.get('ignored')]
    metadata['events'] = [e for e in events if not e.get('ignored')]


# ---- experiment_data_processor -------------------------------------------------------
def experiment_data_processor(info: dict,
                              cfg: settings.Config,
                              fit: Optional[dict],
                              experiment: Optional[dict] = None,
                              ) -> dict:
    """
    ---- Summary ----
    Main function to read (or take) one experiment and process its data: trim, decompose
    into haems, scale by OD, convert to percentages, choose the plotted sources and
    average around the events. It draws and saves nothing.

    ---- Inputs ----
    info : dict
        Per-file information from everything_asker: path, name, trim and ignore times,
        OD values and events.
    cfg : settings.Config
        Figure style and settings derived from the answers (config.py).
    fit : Optional[dict]
        Fit dictionary from import_fit ({haem_list, data}), or None when the haems are
        not decomposed.
    experiment : Optional[dict]
        An experiment already read from the file (the experiment browser keeps a copy
        so the file is not read again). It is processed in place. None reads the file.

    ---- Globals read ----
    settings.TRANSMISSION_MODE, settings.DEGREE_OF_SCATTER, settings.HAEM_FACTOR,
    settings.DELTA_ABS_WINDOW_SECONDS, settings.PERCENT_AVERAGE_WINDOW_SECONDS.

    ---- Outputs ----
    dict
        {experiment, od_available, vo2_source, haem_source}. Prints progress and the
        reason when a step is skipped (side effect).

    ---- Globals mutated ----
    None. Processes the experiment dictionary in place (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    event_settings_merger
    experiment_attenuation_adder
    experiment_averages_calculator
    experiment_decomposer
    experiment_normaliser
    experiment_paf_loader
    experiment_trimmer
    percent_converter
    percent_need_checker
    source_chooser
    """

    # ---- 1 Set up the run ------------------------------------------------------------
    a = cfg.answers
    ignore_first, ignore_last = info['ignore_start'], info['ignore_end']

    # ---- 2 Read the file -------------------------------------------------------------
    if experiment is None:
        datasets = (None
                    if a['export_spectra']
                    else ((a['decomposition_dataset'],) if a['decompose'] else ())
                    )
        experiment = experiment_paf_loader(info['path'],
                                           spectral_datasets=datasets,
                                           with_intensity=a['export_spectra'],
                                           )
    metadata = experiment['metadata']
    for key in ('OD', 'volume', 'dilution_factor'):
        if info.get(key) is not None:
            metadata[key] = info[key]
    event_settings_merger(experiment, info.get('events', []))
    skipped = len(metadata.get('ignored_events', []))
    print(f"  Read {len(experiment['CcO2'])} points, "
          f"{len(metadata['events'])} event(s)" +
          (f' ({skipped} ignored)' if skipped else ''),
          )

    # ---- 3 Trim the experiment -------------------------------------------------------
    if info.get('trim_start') is not None or info.get('trim_end') is not None:
        experiment_trimmer(experiment,
                           start_time=info.get('trim_start'),
                           end_time=info.get('trim_end'),
                           )
        if info.get('trim_start') is not None:
            print(f"  Trimmed: data before {info['trim_start']:g} min discarded (that "
                  f'point is now time 0)',
                  )
        if info.get('trim_end') is not None:
            print(f"  Trimmed: data after {info['trim_end']:g} min discarded")

    # ---- 4 Prepare the data ----------------------------------------------------------
    # ---- 4.1 Check OD scaling is possible --------------------------------------------
    od_available = False
    if a['normalise_od']:
        od_available = all(metadata.get(k) for k in ('OD', 'volume', 'dilution_factor'))
        if not od_available:
            print('  Warning: OD, volume or dilution factor is missing, so this file '
                  'is not scaled by OD (raw values are used instead).',
                  )

    # ---- 4.2 Decompose into haems ----------------------------------------------------
    # Attenuation and decomposition into haems.
    if a['decompose']:
        try:
            attenuation_datasets = (None
                                    if a['export_spectra']
                                    else (a['decomposition_dataset'],)
                                    )
            experiment_attenuation_adder(experiment,
                                         mode=settings.TRANSMISSION_MODE,
                                         datasets=attenuation_datasets,
                                         )
            print('  Decomposing ...')
            delta_window_seconds = settings.DELTA_ABS_WINDOW_SECONDS
            experiment_decomposer(experiment,
                                  fit,
                                  dataset_name=a['decomposition_dataset'],
                                  spectrum_type='attenuation',
                                  degree_of_scatter=settings.DEGREE_OF_SCATTER,
                                  haemfactor=settings.HAEM_FACTOR,
                                  delta_exclude_first_minutes=ignore_first,
                                  delta_window_seconds=delta_window_seconds,
                                  )
            reference = experiment['haem_delta_abs'].attrs['delta_abs_baseline']
            print(f"  Decomposed with {a['fit_file']}; delta A reference: "
                  f"{reference['start_time']:.2f}-{reference['end_time']:.2f} min",
                  )
        except (KeyError, ValueError, PafError) as exc:
            print(f'  Decomposition skipped: {exc}')
    elif a['export_spectra']:
        experiment_attenuation_adder(experiment, mode=settings.TRANSMISSION_MODE)

    # ---- 4.3 Normalise by OD ---------------------------------------------------------
    # OD scaling and relative (%) scaling.
    if od_available:
        try:
            experiment_normaliser(experiment)
            print(f"  OD scaling: OD {metadata['OD']:g}, volume {metadata['volume']:g}"
                  f", dilution factor {metadata['dilution_factor']:g}",
                  )
        except (KeyError, ValueError) as exc:
            od_available = False
            print(f'  OD scaling skipped: {exc}')

    # ---- 4.4 Convert to percentages --------------------------------------------------
    percent_vo2, percent_haem = cfg.percent_need_checker()
    percent_window_seconds = settings.PERCENT_AVERAGE_WINDOW_SECONDS
    for needed, source_key, target_key in ((percent_haem, 'haem_conc', 'haem_percent'),
                                           (percent_vo2, 'VoO2', 'VoO2_percent'),
                                           ):
        if needed and source_key in experiment:
            try:
                percent_converter(experiment,
                                  source_key,
                                  target_key,
                                  exclude_first_minutes=ignore_first,
                                  exclude_last_minutes=ignore_last,
                                  window_seconds=percent_window_seconds,
                                  )
            except (KeyError, ValueError, TypeError) as exc:
                print(f'  {target_key} skipped: {exc}')

    # ---- 5 Choose the sources and average --------------------------------------------
    vo2_source, haem_source = cfg.source_chooser(od_available)
    if haem_source is not None and not (a['plot_haems'] or a['averaging']):
        haem_source = None
    # Event-window averages.
    if a['averaging']:
        if not metadata['events']:
            print('  Averaging skipped: this file has no events.')
        else:
            try:
                average_haem_source = (haem_source
                                       if 'haem_conc' in experiment
                                       else None
                                       )
                final_gap = a['final_gap_minutes']
                experiment_averages_calculator(experiment,
                                               window_minutes=a['window_minutes'],
                                               gap_minutes=a['gap_minutes'],
                                               final_window_gap_minutes=final_gap,
                                               vo2_source=vo2_source,
                                               haem_source=average_haem_source,
                                               )
                print(f"  Calculated {len(experiment['averages']['windows'])} event "
                      f'averages',
                      )
            except (KeyError, ValueError, TypeError) as exc:
                print(f'  Averaging skipped: {exc}')

    # ---- 6 Return the processed experiment -------------------------------------------
    return {'experiment': experiment,
            'od_available': od_available,
            'vo2_source': vo2_source,
            'haem_source': haem_source,
            }
