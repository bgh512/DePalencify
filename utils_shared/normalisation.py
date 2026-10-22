# -*- coding: utf-8 -*-
"""Normalisation of VoO2 and haem data: OD normalisation (of VoO2, haem concentration, haem abs and haem delta abs)
and relative (0-100 %) scaling (of VoO2 and haem concentration only)."""
# %% IMPORTS -----------------------------------------------------------------------------------------------------------------------------------------
import numpy as np
import pandas as pd

from utils_shared.schema import get_times, measurement_columns
# %% NORMALISE BY OD ---------------------------------------------------------------------------------------------------------------------------------


def normalise_data(data, optical_density, volume, dilution_factor):
    """Divide numeric data by dilution factor x optical density x volume."""
    denominator = float(dilution_factor) * float(optical_density) * float(volume)

    if not np.isfinite(denominator) or denominator <= 0:
        raise ValueError("Dilution factor x OD x volume must be positive and finite.")

    if isinstance(data, pd.DataFrame):
        return data.apply(lambda column: pd.to_numeric(column, errors="raise")) / denominator
    if isinstance(data, pd.Series):
        return pd.to_numeric(data, errors="raise") / denominator
    return np.asarray(data, dtype=float) / denominator


def _normalise_frame(df, **kwargs):
    """OD-normalise the measurement columns of a DataFrame, leaving time/index columns untouched."""
    result = df.copy()
    columns = measurement_columns(df)
    if columns:
        result[columns] = normalise_data(df[columns], **kwargs)
    return result


def normalise_experiment(experiment):
    """
    OD-normalise VoO2 and (if present) the haem data

    Adds ``VoO2_OD`` and, for each of ``haem_conc``, ``haem_abs`` and ``haem_delta_abs`` that exists, ``haem_OD``,
    ``haem_abs_OD`` and ``haem_delta_abs_OD``. (Dividing by a constant commutes with the additive shift behind delta abs, so
    haem_delta_abs_OD is the same as shifting haem_abs_OD.) Requires the metadata keys ``dilution_factor``, ``OD`` and
    ``volume``. Only VoO2 and haem concentration are ever scaled to percent (see convert_to_percent); the absorbance forms
    are not.
    """
    metadata = experiment["metadata"]
    missing = [key for key in ("dilution_factor", "OD", "volume") if key not in metadata]
    if missing:
        raise KeyError(f"{experiment['experiment_name']}: missing OD-normalisation metadata {missing}")

    kwargs = {
        "optical_density": metadata["OD"],
        "volume": metadata["volume"],
        "dilution_factor": metadata["dilution_factor"],
    }

    if not measurement_columns(experiment["VoO2"]):
        raise ValueError(f"{experiment['experiment_name']}: no VoO2 measurement columns found")
    experiment["VoO2_OD"] = _normalise_frame(experiment["VoO2"], **kwargs)

    for source_key, target_key in (("haem_conc", "haem_OD"),
                                   ("haem_abs", "haem_abs_OD"),
                                   ("haem_delta_abs", "haem_delta_abs_OD")):
        if isinstance(experiment.get(source_key), pd.DataFrame):
            experiment[target_key] = _normalise_frame(experiment[source_key], **kwargs)

    return experiment
# %% RELATIVE (PERCENT) SCALING ----------------------------------------------------------------------------------------------------------------------


def scale_to_percent(df,
                     label="data",
                     exclude_first_minutes=0.0,
                     exclude_last_minutes=0.0,
                     window_seconds=30.0):
    """
    Scale each measurement column to a relative 0-100 % range

    For every column, the mean is calculated in all complete ``window_seconds`` windows
    (using the DataFrame's own TIME_COLUMN). The window with the lowest mean defines 0 %
    and the window with the highest mean defines 100 %. Windows must start after
    ``exclude_first_minutes``, finish before ``exclude_last_minutes`` from the end, and
    contain data spanning at least 80 % of the window. Values outside the range (below
    0 % / above 100 %) are kept.

    The windows used are stored in ``result.attrs["percent_scaling"]``.
    """
    if window_seconds <= 0:
        raise ValueError("window_seconds must be positive.")
    if exclude_first_minutes < 0 or exclude_last_minutes < 0:
        raise ValueError("Excluded periods cannot be negative.")

    columns = measurement_columns(df)
    if not columns:
        raise ValueError(f"{label}: no measurement columns were found.")

    times = get_times(df)
    finite_times = times[np.isfinite(times)]
    if finite_times.size == 0:
        raise ValueError(f"{label}: no finite measurement times are available.")

    window_minutes = window_seconds / 60.0
    first_allowed = finite_times.min() + exclude_first_minutes
    last_allowed = finite_times.max() - exclude_last_minutes

    # Candidate windows must start after the excluded period and fit before the end.
    candidate_starts = np.unique(
        times[np.isfinite(times) & (times >= first_allowed) & (times + window_minutes <= last_allowed + 1e-12)]
    )
    if candidate_starts.size == 0:
        raise ValueError(
            f"{label}: no complete {window_seconds:g}-second windows remain after excluding the "
            "initial/final periods. Reduce the exclusion or window duration."
        )

    result = df.copy()
    scaling_info = {}

    for column in columns:
        values = pd.to_numeric(df[column], errors="coerce").to_numpy(dtype=float)
        lowest = highest = None

        for start in candidate_starts:
            mask = np.isfinite(times) & np.isfinite(values) & (times >= start) & (times <= start + window_minutes)
            window_times, window_values = times[mask], values[mask]

            # Require measurements to span at least 80 % of the window.
            if window_times.size < 2 or window_times.max() - window_times.min() < window_minutes * 0.8:
                continue

            info = {
                "mean": float(np.mean(window_values)),
                "start_time": float(window_times.min()),
                "end_time": float(window_times.max()),
                "n_points": int(window_values.size),
            }
            if lowest is None or info["mean"] < lowest["mean"]:
                lowest = info
            if highest is None or info["mean"] > highest["mean"]:
                highest = info

        if lowest is None or highest is None:
            raise ValueError(f"{label}: insufficient data to find valid {window_seconds:g}-second windows for {column!r}.")

        low, span = lowest["mean"], highest["mean"] - lowest["mean"]
        # A constant signal has no measurable relative range.
        result[column] = np.nan if np.isclose(span, 0.0) else (values - low) / span * 100.0

        scaling_info[column] = {
            "zero_percent_window": lowest,
            "hundred_percent_window": highest,
            "minimum_mean": low,
            "maximum_mean": highest["mean"],
        }

    result.attrs["percent_scaling"] = scaling_info
    return result


def convert_to_percent(experiment, source_key, target_key, **scaling_kwargs):
    """
    Scale ``experiment[source_key]`` to 0-100 % and store it as ``experiment[target_key]``

    Typical use: ("haem_conc", "haem_percent") and ("VoO2", "VoO2_percent").
    """
    source = experiment.get(source_key)
    if not isinstance(source, pd.DataFrame):
        raise ValueError(f"{experiment['experiment_name']}: {source_key} is unavailable, cannot scale to percent.")

    experiment[target_key] = scale_to_percent(
        source, label=f"{experiment['experiment_name']}/{source_key}", **scaling_kwargs
    )
    return experiment
