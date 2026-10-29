"""
Across-run (triplicate) statistics of the event-window averages.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from typing import Iterable

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_custom.run_namer import condition_grouper


# ---- TRIPLICATE AVERAGER HELPERS -----------------------------------------------------


# ---- _run_summariser -----------------------------------------------------------------
def _run_summariser(values: Iterable) -> tuple:
    """
    ---- Summary ----
    Helper function to summarise the finite values of one window across runs.

    ---- Inputs ----
    values : Iterable
        Values to summarise (one per run).

    ---- Globals read ----
    None.

    ---- Outputs ----
    tuple
        (mean, sample SD, SEM, N). SD and SEM are NaN for N < 2; all NaN with N = 0 when
        no value is finite.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    SD = sqrt(sum((x - mean)^2) / (N - 1)); SEM = SD / sqrt(N).

    ---- Helpers ----
    None.
    """

    numbers = np.asarray(list(values), dtype=float)
    numbers = numbers[np.isfinite(numbers)]
    n = len(numbers)
    if n == 0:
        return np.nan, np.nan, np.nan, 0
    mean = float(np.mean(numbers))
    if n < 2:
        return mean, np.nan, np.nan, n
    sd = float(np.std(numbers, ddof=1))
    return mean, sd, sd / np.sqrt(n), n


# ---- _run_value_getter ---------------------------------------------------------------
def _run_value_getter(windows_by_run: dict,
                      window_name: str,
                      kind: str,
                      measurement: str,
                      field: str,
                      ) -> dict:
    """
    ---- Summary ----
    Helper function to read one statistic of one window and measurement for every run.

    ---- Inputs ----
    windows_by_run : dict
        {run number: {window name: window record}} from the runs' averages.
    window_name : str
        Window name such as 'average3'.
    kind : str
        'vo2' or 'haem'.
    measurement : str
        Measurement (column) name.
    field : str
        Statistic name: 'mean', 'sd', 'change' or 'delta'.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        {run number: value}, NaN where a run lacks the window.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return {run: windows[window_name][kind].get(measurement, {}).get(field, np.nan)
            if window_name in windows
            else np.nan
            for run, windows in windows_by_run.items()
            }


# ---- _window_sorter ------------------------------------------------------------------
def _window_sorter(window_name: str) -> int:
    """
    ---- Summary ----
    Helper function to sort averaging window names numerically.

    ---- Inputs ----
    window_name : str
        Window name such as 'average3'.

    ---- Globals read ----
    None.

    ---- Outputs ----
    int
        Window number.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return int(window_name[len('average'):])


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- triplicate_averager -------------------------------------------------------------
def triplicate_averager(experiments: dict, min_runs: int = 2) -> dict:
    """
    ---- Summary ----
    Main function to combine the per-experiment event averages across the runs of each
    condition.

    ---- Inputs ----
    experiments : dict
        Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.
    min_runs : int
        Conditions with fewer runs that have averages are skipped.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        {condition: result}; result holds runs, run_numbers, windows, window_times,
        settings and, for vo2 and haem, per-window statistics (DATA_FORMAT.md).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _run_summariser
    _run_value_getter
    _window_sorter
    condition_grouper
    """

    # ---- 1 Prepare the results -------------------------------------------------------
    results = {}

    # ---- 2 Average each condition ----------------------------------------------------
    for condition, runs in sorted(condition_grouper(experiments).items()):
        # ---- 2.1 Select the usable runs ----------------------------------------------
        usable = {run: exp for run, exp in sorted(runs.items()) if exp.get('averages')}
        if len(usable) < min_runs:
            print(f'  Skipping {condition}: fewer than {min_runs} runs with averages.')
            continue

        # ---- 2.2 Collect the window times --------------------------------------------
        windows_by_run = {run: exp['averages']['windows'] for run, exp in usable.items()
                          }
        window_names = sorted({w for windows in windows_by_run.values() for w in windows
                               },
                              key=_window_sorter,
                              )
        window_times = {}
        for window_name in window_names:
            for windows in windows_by_run.values():
                if window_name in windows:
                    window_times[window_name] = (windows[window_name]['start_time'],
                                                 windows[window_name]['end_time'],
                                                 )
                    break

        # ---- 2.3 Start the result ----------------------------------------------------
        result = {'runs': {run: exp['experiment_name'] for run, exp in usable.items()},
                  'run_numbers': list(usable),
                  'windows': window_names,
                  'window_times': window_times,
                  'settings': next(iter(usable.values()))['averages']['settings'],
                  }

        # ---- 2.4 Average each measurement kind ---------------------------------------
        for kind in ('vo2', 'haem'):
            measurements = list(dict.fromkeys(m
                                              for windows in windows_by_run.values()
                                              for w in windows.values()
                                              for m in w[kind]
                                              ),
                                )
            result[kind] = {}
            for measurement in measurements:
                result[kind][measurement] = {}
                for window_name in window_names:
                    values = {field: _run_value_getter(windows_by_run,
                                                       window_name,
                                                       kind,
                                                       measurement,
                                                       field,
                                                       )
                              for field in ('mean', 'sd', 'change', 'delta')
                              }
                    run_means, run_sds = values['mean'], values['sd']
                    run_changes, run_deltas = values['change'], values['delta']
                    mean, sd, sem, n = _run_summariser(run_means.values())
                    c_mean, c_sd, c_sem, c_n = _run_summariser(run_changes.values())
                    d_mean, d_sd, d_sem, d_n = _run_summariser(run_deltas.values())
                    statistics = {'run_means': run_means,
                                  'run_sds': run_sds,
                                  'run_changes': run_changes,
                                  'run_deltas': run_deltas,
                                  'mean': mean,
                                  'sd': sd,
                                  'sem': sem,
                                  'n': n,
                                  'change_mean': c_mean,
                                  'change_sd': c_sd,
                                  'change_sem': c_sem,
                                  'change_n': c_n,
                                  'delta_mean': d_mean,
                                  'delta_sd': d_sd,
                                  'delta_sem': d_sem,
                                  'delta_n': d_n,
                                  }
                    result[kind][measurement][window_name] = statistics

        # ---- 2.5 Store the result ----------------------------------------------------
        results[condition] = result
    return results
