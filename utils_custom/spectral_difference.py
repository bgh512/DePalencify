"""
Event-window spectral averages, their difference spectrum and its decomposition.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from typing import Iterable, Optional

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.spectral_decomposer import spectrum_decomposer


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- difference_spectrum_calculator --------------------------------------------------
def difference_spectrum_calculator(experiment: dict,
                                   minuend: str = 'penultimate',
                                   subtrahend: str = 'final',
                                   ) -> dict:
    """
    ---- Summary ----
    Main function to subtract one averaged spectrum from another.

    ---- Inputs ----
    experiment : dict
        Experiment dictionary, as defined in DATA_FORMAT.md.
    minuend : str
        Window name or role ('penultimate', 'final') to subtract from.
    subtrahend : str
        Window name or role to subtract.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        The experiment, with difference_spectrum added (DATA_FORMAT.md).

    ---- Globals mutated ----
    None. Adds ``difference_spectrum`` to the experiment (side effect).

    ---- Equations ----
    difference = mean spectrum of the minuend window - mean spectrum of the subtrahend
    window.

    ---- Helpers ----
    None.
    """

    # ---- 1 Read the spectral averages ------------------------------------------------
    name = experiment['experiment_name']
    averages = experiment.get('spectral_averages')
    if not averages:
        raise ValueError(f'{name}: spectral averages must be calculated first.')
    windows = averages['windows']

    # ---- 2 Resolve the windows -------------------------------------------------------
    resolved = []
    for choice in (minuend, subtrahend):
        window_name = averages['roles'].get(choice, choice)
        if window_name not in windows:
            raise ValueError(f'{name}: {choice!r} is not an available averaging window'
                             f' '
                             f"(available: {', '.join(windows)}; roles: "
                             f"{averages['roles']}).",
                             )
        resolved.append(window_name)

    # ---- 3 Store the difference spectrum ---------------------------------------------
    experiment['difference_spectrum'] = {'wavelengths': averages['wavelengths'],
                                         'spectrum': windows[resolved[0]]['mean'] -
                                         windows[resolved[1]]['mean'],
                                         'minuend': resolved[0],
                                         'subtrahend': resolved[1],
                                         }
    return experiment


# ---- difference_spectrum_decomposer --------------------------------------------------
def difference_spectrum_decomposer(experiment: dict,
                                   fit: dict,
                                   degree_of_scatter: int = 1,
                                   haemfactor: float = 1000000,
                                   percent_basis: str = 'signed',
                                   ) -> dict:
    """
    ---- Summary ----
    Main function to decompose the difference spectrum into haem contributions using the
    shared decomposition.

    ---- Inputs ----
    experiment : dict
        Experiment dictionary, as defined in DATA_FORMAT.md.
    fit : dict
        Fit dictionary from import_fit: {haem_list, data}.
    degree_of_scatter : int
        Number of scatter terms in the decomposition.
    haemfactor : float
        Scale factor applied to the fit spectra.
    percent_basis : str
        'signed' (coefficient / sum of coefficients) or 'absolute' (coefficient / sum of
        absolute coefficients).

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        The experiment, with difference_decomposition added (DATA_FORMAT.md).

    ---- Globals mutated ----
    None. Adds ``difference_decomposition`` to the experiment (side effect).

    ---- Equations ----
    percent_i = 100 c_i / sum(c) ('signed') or 100 c_i / sum(|c|) ('absolute'); NaN when
    the denominator is about 0.

    ---- Helpers ----
    spectrum_decomposer
    """

    # ---- 1 Check the inputs ----------------------------------------------------------
    name = experiment['experiment_name']
    difference = experiment.get('difference_spectrum')
    if not difference:
        raise ValueError(f'{name}: the difference spectrum must be calculated first.')
    if percent_basis not in ('signed', 'absolute'):
        raise ValueError(f'percent_basis must be "signed" or "absolute"; received '
                         f'{percent_basis!r}.',
                         )

    # ---- 2 Decompose the difference spectrum -----------------------------------------
    experimental = np.column_stack((difference['wavelengths'], difference['spectrum']))
    (coefficients,
     filtered,
     scatter,
     no_scatter,
     haem_total,
     haem_individual,
     residual,
     ) = spectrum_decomposer(experimental, fit['data'], degree_of_scatter, haemfactor)

    # ---- 3 Calculate the haem percentages --------------------------------------------
    haem_names = [str(h) for h in fit['haem_list']]
    n_haems = len(haem_names)
    haem_coefficients = np.asarray(coefficients[:n_haems], dtype=float).reshape(-1)
    denominator = (haem_coefficients.sum()
                   if percent_basis == 'signed'
                   else np.abs(haem_coefficients).sum()
                   )
    if np.isfinite(denominator) and not np.isclose(denominator, 0.0):
        percentages = haem_coefficients / denominator * 100.0
    else:
        percentages = np.full(n_haems, np.nan)

    # ---- 4 Store the decomposition ---------------------------------------------------
    order = sorted(range(n_haems), key=lambda i: haem_names[i].casefold())
    experiment['difference_decomposition'] = {'haem_names': [haem_names[i]
                                                             for i in order
                                                             ],
                                              'coefficients': haem_coefficients[order],
                                              'haem_percentages': percentages[order],
                                              'percent_basis': percent_basis,
                                              'filtered_data': filtered,
                                              'scatter': scatter,
                                              'no_scatter': no_scatter,
                                              'haem_total': haem_total,
                                              'haem_individual': [haem_individual[i]
                                                                  for i in order
                                                                  ],
                                              'residual': residual,
                                              }
    return experiment


# ---- spectral_averager ---------------------------------------------------------------
def spectral_averager(experiment: dict,
                      dataset_name: str,
                      spectrum_type: str,
                      window_minutes: float,
                      gap_minutes: float,
                      final_window_gap_minutes: float = 0.5,
                      expected_events: Optional[int] = None,
                      ) -> dict:
    """
    ---- Summary ----
    Main function to average the chosen spectra in each event window.

    ---- Inputs ----
    experiment : dict
        Experiment dictionary, as defined in DATA_FORMAT.md.
    dataset_name : str
        Spectrometer dataset, for example 'Cyt'.
    spectrum_type : str
        Spectrum field, for example 'attenuation'.
    window_minutes : float
        Length of each window in minutes.
    gap_minutes : float
        Gap between a window and the next addition in minutes.
    final_window_gap_minutes : float
        Gap between the last window and the end of the data in minutes.
    expected_events : Optional[int]
        Raise if the run has a different number of events; None skips the check.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        The experiment, with spectral_averages added (DATA_FORMAT.md).

    ---- Globals mutated ----
    None. Adds ``spectral_averages`` to the experiment (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    window_definer
    """

    # ---- 1 Validate the inputs -------------------------------------------------------
    name = experiment['experiment_name']
    dataset = experiment.get('raw_spectra', {}).get(dataset_name)
    if dataset is None:
        raise ValueError(f'{name}: unknown spectral dataset {dataset_name!r}.')
    if spectrum_type not in dataset:
        raise ValueError(f'{name}/{dataset_name}: {spectrum_type!r} not found (run '
                         f'attenuation first?). '
                         f"Available fields: {', '.join(dataset)}",
                         )
    spectra = np.asarray(dataset[spectrum_type], dtype=float)
    times = np.asarray(dataset['time'], dtype=float)
    if not np.all(np.isfinite(times)):
        raise ValueError(f'{name}/{dataset_name}: spectrum times are unavailable '
                         f'(spectra/CsO2 length mismatch).',
                         )
    events = experiment['metadata'].get('events', [])
    if not events:
        raise ValueError(f'{name}: no timed events found for averaging.')
    if expected_events is not None and len(events) != expected_events:
        raise ValueError(f'{name}: expected {expected_events} events but found '
                         f'{len(events)}.',
                         )

    # ---- 2 Define the windows --------------------------------------------------------
    boundaries = window_definer([event['time'] for event in events],
                                float(np.max(times)),
                                window_minutes,
                                gap_minutes,
                                final_window_gap_minutes,
                                )

    # ---- 3 Average the spectra in each window ----------------------------------------
    windows, skipped = {}, {}
    for window_name, start, end, previous in boundaries:
        if previous is not None and start < previous:
            skipped[window_name] = (f'it would start {previous - start:.2f} min before '
                                    f'the previous addition'
                                    )
            continue
        selected = spectra[(times >= start) & (times <= end)]
        if selected.shape[0] == 0:
            skipped[window_name] = f'no spectra between {start:.2f} and {end:.2f} min'
            continue
        windows[window_name] = {'start_time': start,
                                'end_time': end,
                                'n_spectra': int(selected.shape[0]),
                                'mean': selected.mean(axis=0),
                                'sd': selected.std(axis=0, ddof=1)
                                if selected.shape[0] >= 2
                                else np.full(selected.shape[1], np.nan),
                                }
    for window_name, reason in skipped.items():
        print(f'  Averaging window {window_name} skipped: {reason}.')

    # ---- 4 Store the result ----------------------------------------------------------
    final_name, penultimate_name = boundaries[-1][0], boundaries[-2][0]
    for role, window_name in (('final', final_name), ('penultimate', penultimate_name)):
        if window_name not in windows:
            raise ValueError(f'{name}: the {role} averaging window ({window_name}) is '
                             f'not available: '
                             f"{skipped.get(window_name, 'unknown reason')}.",
                             )
    settings = {'dataset': dataset_name,
                'spectrum_type': spectrum_type,
                'window_minutes': window_minutes,
                'gap_minutes': gap_minutes,
                'final_window_gap_minutes': final_window_gap_minutes,
                }
    roles = {'penultimate': penultimate_name, 'final': final_name}
    wavelengths = np.asarray(dataset['wavelengths'], dtype=float)
    experiment['spectral_averages'] = {'settings': settings,
                                       'wavelengths': wavelengths,
                                       'windows': windows,
                                       'skipped': skipped,
                                       'roles': roles,
                                       }
    return experiment


# ---- window_definer ------------------------------------------------------------------
def window_definer(event_times: Iterable,
                   recording_end: float,
                   window_minutes: float,
                   gap_minutes: float,
                   final_window_gap_minutes: float,
                   ) -> list:
    """
    ---- Summary ----
    Helper function to lay out the averaging windows of one run.

    ---- Inputs ----
    event_times : Iterable
        Event times in minutes.
    recording_end : float
        Last time of the recording in minutes.
    window_minutes : float
        Length of each window.
    gap_minutes : float
        Gap between the end of a window and the next addition.
    final_window_gap_minutes : float
        Gap between the last window and the end of the data.

    ---- Globals read ----
    None.

    ---- Outputs ----
    list
        [(name, start, end, previous event time or None), ...].

    ---- Globals mutated ----
    None.

    ---- Equations ----
    average0 ends gap_minutes before the first addition; averageN ends gap_minutes
    before addition N + 1; the last window ends final_window_gap_minutes before the end.
    start = end - window_minutes.

    ---- Helpers ----
    None.
    """

    # ---- 1 Check the inputs ----------------------------------------------------------
    if window_minutes <= 0:
        raise ValueError('window_minutes must be positive.')
    if gap_minutes < 0 or final_window_gap_minutes < 0:
        raise ValueError('Averaging gaps cannot be negative.')

    # ---- 2 Calculate the window ends -------------------------------------------------
    event_times = sorted(float(t) for t in event_times)
    ends = ([t - gap_minutes for t in event_times] + [recording_end -
                                                      final_window_gap_minutes,
                                                      ]
            )

    # ---- 3 Build the windows ---------------------------------------------------------
    previous = [None] + event_times
    return [(f'average{i}', end - window_minutes, end, previous[i])
            for i, end in enumerate(ends)
            ]
