# -*- coding: utf-8 -*-
"""Event-window averaging of VoO2 and haem data for one experiment (either may be left out)."""
# %% IMPORTS -----------------------------------------------------------------------------------------------------------------------------------------
import numpy as np

from utils_shared.schema import (VO2_KEYS, HAEM_KEYS, DELTA_HAEM_SOURCES, get_times, get_values,
                                 measurement_columns, resolve_source)
# %% WINDOW STATISTICS -------------------------------------------------------------------------------------------------------------------------------


def window_statistics(df, start_time, end_time):
    """
    Mean and sample SD of every measurement column within [start_time, end_time]

    Returns ``{column: {"mean": float, "sd": float}}``; values are NaN when no (or, for the
    SD, fewer than two) finite points fall inside the window.
    """
    times = get_times(df)
    in_window = np.isfinite(times) & (times >= start_time) & (times <= end_time)

    stats = {}
    for column in measurement_columns(df):
        values = get_values(df, column)
        selected = values[in_window & np.isfinite(values)]
        stats[str(column)] = {
            "mean": float(np.mean(selected)) if selected.size else np.nan,
            "sd": float(np.std(selected, ddof=1)) if selected.size >= 2 else np.nan,
        }
    return stats


def _add_change_from_baseline(window_stats, baseline_stats, percent_of_baseline=True):
    """
    Add ``change`` (window mean as % of the baseline mean) and ``delta`` (window mean minus baseline mean)

    ``change`` is NaN when ``percent_of_baseline`` is False (a source that is already a change from a reference, such as
    delta abs, has a baseline near 0, so a percentage of it is meaningless).
    """
    for column, stats in window_stats.items():
        baseline = baseline_stats.get(column, {}).get("mean", np.nan)
        stats["delta"] = stats["mean"] - baseline if np.isfinite(baseline) and np.isfinite(stats["mean"]) else np.nan
        if not percent_of_baseline:
            stats["change"] = np.nan
        elif np.isfinite(baseline) and not np.isclose(baseline, 0.0) and np.isfinite(stats["mean"]):
            stats["change"] = stats["mean"] / baseline * 100.0
        else:
            stats["change"] = np.nan
# %% EXPERIMENT AVERAGES -----------------------------------------------------------------------------------------------------------------------------


def calculate_experiment_averages(experiment,
                                  window_minutes,
                                  gap_minutes,
                                  final_window_gap_minutes=0.5,
                                  vo2_source="od",
                                  haem_source="abs"):   # either source may be None to leave that measurement out
    """
    Calculate event-window statistics and store them in ``experiment["averages"]``

    Windows:
        average0 = baseline window ending ``gap_minutes`` before the first event
        averageN = window ending ``gap_minutes`` before event N+1 (or
                   ``final_window_gap_minutes`` before the end of the recording for the last event)

    Result layout::

        experiment["averages"] = {
            "settings": {...},
            "windows": {"average0": {"start_time", "end_time",
                                     "vo2":  {column: {"mean", "sd", "change", "delta"}},
                                     "haem": {column: {"mean", "sd", "change", "delta"}}},
                        "average1": {...}, ...},
        }

    ``change`` is the window mean as a percentage of the average0 mean (average0 = 100 %); it is NaN for the delta abs
    haem sources ("delta_abs", "delta_abs_od"), which start at 0 and are never scaled to a percentage.
    ``delta`` is the window mean minus the average0 mean, in the units of the source (mOD for the "abs" haem source).
    The window ``mean`` is the source's own value (for the delta abs sources, the change from the start-of-run reference).
    """
    name = experiment["experiment_name"]

    if window_minutes <= 0:
        raise ValueError("window_minutes must be positive.")
    if gap_minutes < 0 or final_window_gap_minutes < 0:
        raise ValueError("Averaging gaps cannot be negative.")

    if vo2_source is None and haem_source is None:
        raise ValueError(f"{name}: nothing to average (no VO2 and no haem source).")
    vo2_key, vo2_df = resolve_source(experiment, vo2_source, VO2_KEYS, "VO2") if vo2_source else (None, None)
    haem_key, haem_df = resolve_source(experiment, haem_source, HAEM_KEYS, "haem") if haem_source else (None, None)

    events = sorted(experiment["metadata"].get("events", []), key=lambda event: event["time"])
    if not events:
        raise ValueError(f"{name}: no timed events found for averaging.")

    reference_df = vo2_df if vo2_df is not None else haem_df
    reference_times = get_times(reference_df)
    if not np.any(np.isfinite(reference_times)):
        raise ValueError(f"{name}: no valid times.")
    recording_end = float(np.nanmax(reference_times))

    # Define the averaging windows.
    first_event = float(events[0]["time"])
    boundaries = [("average0", first_event - gap_minutes - window_minutes, first_event - gap_minutes)]

    for i, event in enumerate(events):
        event_time = float(event["time"])
        if i + 1 < len(events):
            end = float(events[i + 1]["time"]) - gap_minutes
            problem = f"insufficient time between additions {i + 1} and {i + 2}."
        else:
            end = recording_end - final_window_gap_minutes
            problem = "insufficient recording time after the final addition."
        start = end - window_minutes
        if start < event_time:
            raise ValueError(f"{name}: {problem}")
        boundaries.append((f"average{i + 1}", start, end))

    windows = {}
    for window_name, start, end in boundaries:
        windows[window_name] = {
            "start_time": start,
            "end_time": end,
            "vo2": window_statistics(vo2_df, start, end) if vo2_df is not None else {},
            "haem": window_statistics(haem_df, start, end) if haem_df is not None else {},
        }

    baseline = windows["average0"]
    for window in windows.values():
        _add_change_from_baseline(window["vo2"], baseline["vo2"])
        _add_change_from_baseline(window["haem"], baseline["haem"],
                                  percent_of_baseline=haem_source not in DELTA_HAEM_SOURCES)

    experiment["averages"] = {
        "settings": {
            "window_minutes": window_minutes,
            "gap_minutes": gap_minutes,
            "final_window_gap_minutes": final_window_gap_minutes,
            "vo2_source": vo2_source,
            "vo2_key": vo2_key,
            "haem_source": haem_source,
            "haem_key": haem_key,
        },
        "windows": windows,
    }
    return experiment
