# -*- coding: utf-8 -*-
"""Names and conventions that define the experiment data model.

Every time-resolved DataFrame stored in an experiment dictionary carries its own
``TIME_COLUMN`` (minutes), so downstream code reads ``df[TIME_COLUMN]`` directly
and never has to search for a time column.

Experiment dictionary keys
--------------------------
experiment_name      str
metadata             dict (OD, volume, dilution_factor, events, ...)
CcO2, CsO2, VoO2     DataFrames: TIME_COLUMN + measurement column(s)
raw_spectra          {dataset: {wavelengths, spectrum_indices, time,
                                transmission, intensity, attenuation}}
VoO2_OD              OD-normalised VoO2           (optional)
VoO2_percent         VoO2 scaled to 0-100 %       (optional)
haem_conc            DataFrame: TIME_COLUMN, SPECTRUM_INDEX_COLUMN, haems (optional)
haem_abs             haem absorbance contribution in mOD (concentration x peak of the fit spectrum; optional)
haem_delta_abs       haem_abs shifted additively so the mean of its first window (after an excluded start) is 0 (optional)
haem_OD              OD-normalised haem_conc      (optional)
haem_abs_OD          OD-normalised haem_abs       (optional)
haem_delta_abs_OD    OD-normalised haem_delta_abs (optional)
haem_percent         haem_conc scaled to 0-100 %  (optional)
averages             event-window statistics      (optional)
"""
import numpy as np
import pandas as pd

TIME_COLUMN = "Time (min)"
SPECTRUM_INDEX_COLUMN = "spectrum_index"

# Source names used in the config -> experiment dictionary keys.
VO2_KEYS = {"raw": "VoO2", "od": "VoO2_OD", "percent": "VoO2_percent"}
HAEM_KEYS = {"raw": "haem_conc", "od": "haem_OD", "percent": "haem_percent", "abs": "haem_abs",
             "abs_od": "haem_abs_OD", "delta_abs": "haem_delta_abs", "delta_abs_od": "haem_delta_abs_OD"}
# Haem sources that are already a change from a reference point (they start at 0), so a "% of baseline" is meaningless for them.
DELTA_HAEM_SOURCES = ("delta_abs", "delta_abs_od")


def measurement_columns(df):
    """Return the measurement columns of a DataFrame (everything except time/index)."""
    return [c for c in df.columns if c not in (TIME_COLUMN, SPECTRUM_INDEX_COLUMN)]


def get_times(df):
    """Return the TIME_COLUMN of a DataFrame as a float array (minutes)."""
    if TIME_COLUMN not in df.columns:
        raise KeyError(f"DataFrame has no {TIME_COLUMN!r} column; columns: {list(df.columns)}")
    return pd.to_numeric(df[TIME_COLUMN], errors="coerce").to_numpy(dtype=float)


def get_values(df, column):
    """Return one measurement column as a float array."""
    return pd.to_numeric(df[column], errors="coerce").to_numpy(dtype=float)


def resolve_source(experiment, source, keys, what):
    """
    Look up a dataset by its config source name

    Parameters
    ----------
    source : one of the keys of ``keys`` (e.g. "raw", "od", "percent")
    keys   : VO2_KEYS or HAEM_KEYS
    what   : label used in error messages (e.g. "VO2", "haem")

    Returns (experiment_key, DataFrame); raises ValueError if the source name is
    invalid or the dataset has not been calculated for this experiment.
    """
    if source not in keys:
        raise ValueError(f"{what} source must be one of {list(keys)}; received {source!r}.")
    key = keys[source]
    df = experiment.get(key)
    if not isinstance(df, pd.DataFrame) or df.empty:
        raise ValueError(f"{experiment.get('experiment_name', '<unknown>')}: {key} is unavailable.")
    return key, df


def finite_or_nan(value):
    """Convert to a finite float, or NaN."""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return np.nan
    return value if np.isfinite(value) else np.nan
