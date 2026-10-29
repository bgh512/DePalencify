"""
Event-window averaging of OCR and haem data for one experiment.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from typing import Dict, Optional

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pandas as pd

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.schema import (DELTA_HAEM_SOURCES,
                                 HAEM_KEYS,
                                 measurement_column_finder,
                                 source_resolver,
                                 time_getter,
                                 value_getter,
                                 VO2_KEYS,
                                 )


# ---- AVERAGING HELPERS ---------------------------------------------------------------


# ---- _baseline_change_adder ----------------------------------------------------------
def _baseline_change_adder(window_stats: Dict[str, Dict[str, float]],
                           baseline_stats: Dict[str, Dict[str, float]],
                           percent_of_baseline: bool = True,
                           ) -> None:
    """
    ---- Summary ----
    Helper function to add the change from the baseline window to the statistics of a
    window.

    ---- Inputs ----
    window_stats : Dict[str, Dict[str, float]]
        Statistics of one window, from window_statistics_calculator; modified in place.
    baseline_stats : Dict[str, Dict[str, float]]
        Statistics of the baseline window (average0).
    percent_of_baseline : bool
        False for sources that already are a change from a reference (baseline near 0),
        where a percentage is meaningless.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    window_stats: adds "delta" and "change" to every column.

    ---- Equations ----
    delta = mean - baseline_mean; change = mean / baseline_mean x 100 (NaN if
    percent_of_baseline is False, the baseline is 0 or a value is not finite).

    ---- Helpers ----
    None.
    """

    # ---- 1 Add the change from the baseline ------------------------------------------
    for column, stats in window_stats.items():
        baseline = baseline_stats.get(column, {}).get('mean', np.nan)
        stats['delta'] = (stats['mean'] - baseline if np.isfinite(baseline) and
                          np.isfinite(stats['mean']) else np.nan
                          )
        usable = (np.isfinite(baseline)
                  and not np.isclose(baseline, 0.0)
                  and np.isfinite(stats['mean'])
                  )
        if not percent_of_baseline:
            stats['change'] = np.nan
        elif usable:
            stats['change'] = stats['mean'] / baseline * 100.0
        else:
            stats['change'] = np.nan


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- experiment_averages_calculator --------------------------------------------------
def experiment_averages_calculator(experiment: dict,
                                   window_minutes: float,
                                   gap_minutes: float,
                                   final_window_gap_minutes: float = 0.5,
                                   vo2_source: Optional[str] = 'od',
                                   haem_source: Optional[str] = 'abs',
                                   ) -> dict:
    """
    ---- Summary ----
    Main function to calculate event-window statistics for VoO2 and haem data and store
    them in the experiment.

    ---- Inputs ----
    experiment : dict
        Experiment dictionary, as defined in DATA_FORMAT.md.
    window_minutes : float
        Length of each averaging window, in minutes (> 0).
    gap_minutes : float
        How long before the next addition each window ends, in minutes (>= 0).
    final_window_gap_minutes : float
        How long before the end of the recording the last window ends, in minutes (>=
        0).
    vo2_source : Optional[str]
        VoO2 source key (e.g. 'od', 'raw', 'percent'); None leaves VoO2 out.
    haem_source : Optional[str]
        Haem source key (e.g. 'abs', 'delta_abs_od'); None leaves the haems out.

    ---- Globals read ----
    schema.VO2_KEYS, HAEM_KEYS and DELTA_HAEM_SOURCES; schema.resolve_source, get_times.

    ---- Outputs ----
    dict
        The same experiment dictionary. Raises ValueError for invalid settings, no
        source, no events, invalid times or windows that do not fit between the
        additions.

    ---- Globals mutated ----
    experiment: adds experiment["averages"] = {"settings", "windows"} (layout in
    DATA_FORMAT.md).

    ---- Equations ----
    average0 ends gap_minutes before the first event; averageN ends gap_minutes before
    event N+1 (final_window_gap_minutes before the end of the recording for the last
    event); each window starts window_minutes before its end. change = mean /
    mean(average0) x 100 (NaN for delta abs sources); delta = mean - mean(average0).

    ---- Helpers ----
    _baseline_change_adder
    source_resolver
    time_getter
    window_statistics_calculator
    """

    # ---- 1 Validate the inputs -------------------------------------------------------
    name = experiment['experiment_name']
    if window_minutes <= 0:
        raise ValueError('window_minutes must be positive.')
    if gap_minutes < 0 or final_window_gap_minutes < 0:
        raise ValueError('Averaging gaps cannot be negative.')
    if vo2_source is None and haem_source is None:
        raise ValueError(f'{name}: nothing to average (no VO2 and no haem source).')

    # ---- 2 Resolve the data sources --------------------------------------------------
    vo2_key, vo2_df = (source_resolver(experiment, vo2_source, VO2_KEYS, 'VO2')
                       if vo2_source
                       else (None, None)
                       )
    haem_key, haem_df = (source_resolver(experiment, haem_source, HAEM_KEYS, 'haem')
                         if haem_source
                         else (None, None)
                         )

    # ---- 3 Define the windows --------------------------------------------------------
    events = sorted(experiment['metadata'].get('events', []),
                    key=lambda event: event['time'],
                    )
    if not events:
        raise ValueError(f'{name}: no timed events found for averaging.')
    reference_df = vo2_df if vo2_df is not None else haem_df
    reference_times = time_getter(reference_df)
    if not np.any(np.isfinite(reference_times)):
        raise ValueError(f'{name}: no valid times.')
    recording_end = float(np.nanmax(reference_times))
    # Define the averaging windows.
    first_event = float(events[0]['time'])
    boundaries = [('average0',
                   first_event - gap_minutes - window_minutes,
                   first_event - gap_minutes,
                   ),
                  ]
    for i, event in enumerate(events):
        event_time = float(event['time'])
        if i + 1 < len(events):
            end = float(events[i + 1]['time']) - gap_minutes
            problem = f'insufficient time between additions {i + 1} and {i + 2}.'
        else:
            end = recording_end - final_window_gap_minutes
            problem = 'insufficient recording time after the final addition.'
        start = end - window_minutes
        if start < event_time:
            raise ValueError(f'{name}: {problem}')
        boundaries.append((f'average{i + 1}', start, end))

    # ---- 4 Calculate the window statistics -------------------------------------------
    windows = {}
    for window_name, start, end in boundaries:
        windows[window_name] = {'start_time': start,
                                'end_time': end,
                                'vo2': window_statistics_calculator(vo2_df, start, end)
                                if vo2_df is not None
                                else {},
                                'haem': window_statistics_calculator(haem_df,
                                                                     start,
                                                                     end,
                                                                     )
                                if haem_df is not None
                                else {},
                                }

    # ---- 5 Store the results ---------------------------------------------------------
    baseline = windows['average0']
    haem_is_absolute = haem_source not in DELTA_HAEM_SOURCES
    for window in windows.values():
        _baseline_change_adder(window['vo2'], baseline['vo2'])
        _baseline_change_adder(window['haem'],
                               baseline['haem'],
                               percent_of_baseline=haem_is_absolute,
                               )
    final_gap = final_window_gap_minutes
    experiment['averages'] = {'settings': {'window_minutes': window_minutes,
                                           'gap_minutes': gap_minutes,
                                           'final_window_gap_minutes': final_gap,
                                           'vo2_source': vo2_source,
                                           'vo2_key': vo2_key,
                                           'haem_source': haem_source,
                                           'haem_key': haem_key,
                                           },
                              'windows': windows,
                              }
    return experiment


# ---- window_statistics_calculator ----------------------------------------------------
def window_statistics_calculator(df: pd.DataFrame,
                                 start_time: float,
                                 end_time: float,
                                 ) -> Dict[str, Dict[str, float]]:
    """
    ---- Summary ----
    Main function to calculate the mean and sample SD of every measurement column inside
    a time window.

    ---- Inputs ----
    df : pd.DataFrame
        Data frame with a time column and measurement columns (DATA_FORMAT.md).
    start_time : float
        Window start, in minutes.
    end_time : float
        Window end, in minutes.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Dict[str, Dict[str, float]]
        {column: {"mean", "sd"}}. Values are NaN when no finite point falls in the
        window (SD: fewer than two).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    mean = sum(x) / n; SD = sqrt(sum((x - mean)^2) / (n - 1)) over the finite points
    with start_time <= t <= end_time.

    ---- Helpers ----
    measurement_column_finder
    time_getter
    value_getter
    """

    # ---- 1 Select the window ---------------------------------------------------------
    times = time_getter(df)
    in_window = np.isfinite(times) & (times >= start_time) & (times <= end_time)

    # ---- 2 Calculate the statistics --------------------------------------------------
    stats = {}
    for column in measurement_column_finder(df):
        values = value_getter(df, column)
        selected = values[in_window & np.isfinite(values)]
        stats[str(column)] = {'mean': float(np.mean(selected))
                              if selected.size
                              else np.nan,
                              'sd': float(np.std(selected, ddof=1))
                              if selected.size >= 2
                              else np.nan,
                              }
    return stats
