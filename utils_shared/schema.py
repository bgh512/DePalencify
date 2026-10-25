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
haem_abs             haem absorbance contribution in mOD (concentration x peak of the
fit spectrum; optional)
haem_delta_abs       haem_abs shifted additively so the mean of its first window (after
an excluded start) is 0 (optional)
haem_OD              OD-normalised haem_conc      (optional)
haem_abs_OD          OD-normalised haem_abs       (optional)
haem_delta_abs_OD    OD-normalised haem_delta_abs (optional)
haem_percent         haem_conc scaled to 0-100 %  (optional)
averages             event-window statistics      (optional)
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from typing import Any, Dict, List, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pandas as pd


# ---- CONSTANTS -----------------------------------------------------------------------
TIME_COLUMN = 'Time (min)'
SPECTRUM_INDEX_COLUMN = 'spectrum_index'
# Source names used in the config -> experiment dictionary keys.
VO2_KEYS = {'raw': 'VoO2', 'od': 'VoO2_OD', 'percent': 'VoO2_percent'}
HAEM_KEYS = {'raw': 'haem_conc',
             'od': 'haem_OD',
             'percent': 'haem_percent',
             'abs': 'haem_abs',
             'abs_od': 'haem_abs_OD',
             'delta_abs': 'haem_delta_abs',
             'delta_abs_od': 'haem_delta_abs_OD',
             }
# Haem sources that are already a change from a reference point (they start at 0), so a
# "% of baseline" is meaningless for them.
DELTA_HAEM_SOURCES = ('delta_abs', 'delta_abs_od')


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- FINITE FLOAT CONVERTER ----------------------------------------------------------
def finite_float_converter(value: Any) -> float:
    """
    ---- Summary ----
    Main function to convert a value to a finite float, or NaN when that is not
    possible.

    ---- Inputs ----
    value : Any
        Value to convert.

    ---- Globals read ----
    None.

    ---- Outputs ----
    float
        The value as a float, or NaN when it is not a number or not finite.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    try:
        value = float(value)
    except (TypeError, ValueError):
        return np.nan
    return value if np.isfinite(value) else np.nan


# ---- MEASUREMENT COLUMN FINDER -------------------------------------------------------
def measurement_column_finder(df: pd.DataFrame) -> List[str]:
    """
    ---- Summary ----
    Main function to list the measurement columns of an experiment DataFrame.

    ---- Inputs ----
    df : pd.DataFrame
        Time-resolved DataFrame with TIME_COLUMN.

    ---- Globals read ----
    TIME_COLUMN, SPECTRUM_INDEX_COLUMN (module constants).

    ---- Outputs ----
    List[str]
        Every column except TIME_COLUMN and SPECTRUM_INDEX_COLUMN.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return [c for c in df.columns if c not in (TIME_COLUMN, SPECTRUM_INDEX_COLUMN)]


# ---- SOURCE RESOLVER -----------------------------------------------------------------
def source_resolver(experiment: dict,
                    source: str,
                    keys: Dict[str, str],
                    what: str,
                    ) -> Tuple[str, pd.DataFrame]:
    """
    ---- Summary ----
    Main function to look up a dataset of an experiment by its source name from the
    settings.

    ---- Inputs ----
    experiment : dict
        Experiment dictionary, as defined in DATA_FORMAT.md.
    source : str
        Source name, one of the keys of ``keys`` (for example "raw", "od", "percent").
    keys : Dict[str, str]
        VO2_KEYS or HAEM_KEYS: {source name: experiment dictionary key}.
    what : str
        Label used in error messages, for example "VO2" or "haem".

    ---- Globals read ----
    None.

    ---- Outputs ----
    Tuple[str, pd.DataFrame]
        (experiment dictionary key, the DataFrame). Raises ValueError when the source
        name is invalid or the dataset has not been calculated.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 Validate the source -------------------------------------------------------
    if source not in keys:
        raise ValueError(f'{what} source must be one of {list(keys)}; received '
                         f'{source!r}.',
                         )

    # ---- 2 Fetch the table -----------------------------------------------------------
    key = keys[source]
    df = experiment.get(key)
    if not isinstance(df, pd.DataFrame) or df.empty:
        raise ValueError(f"{experiment.get('experiment_name', '<unknown>')}: {key} is "
                         f'unavailable.',
                         )
    return key, df


# ---- TIME GETTER ---------------------------------------------------------------------
def time_getter(df: pd.DataFrame) -> np.ndarray:
    """
    ---- Summary ----
    Main function to read the time column of an experiment DataFrame.

    ---- Inputs ----
    df : pd.DataFrame
        Time-resolved DataFrame; must hold TIME_COLUMN.

    ---- Globals read ----
    TIME_COLUMN (module constant).

    ---- Outputs ----
    np.ndarray
        Times in minutes as a float array, shape (n_points,); unreadable values are NaN.
        Raises KeyError when the column is missing.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    if TIME_COLUMN not in df.columns:
        raise KeyError(f'DataFrame has no {TIME_COLUMN!r} column; columns: '
                       f'{list(df.columns)}',
                       )
    return pd.to_numeric(df[TIME_COLUMN], errors='coerce').to_numpy(dtype=float)


# ---- VALUE GETTER --------------------------------------------------------------------
def value_getter(df: pd.DataFrame, column: str) -> np.ndarray:
    """
    ---- Summary ----
    Main function to read one measurement column as a float array.

    ---- Inputs ----
    df : pd.DataFrame
        Time-resolved DataFrame.
    column : str
        Name of the measurement column.

    ---- Globals read ----
    None.

    ---- Outputs ----
    np.ndarray
        Values as a float array, shape (n_points,); unreadable values are NaN.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return pd.to_numeric(df[column], errors='coerce').to_numpy(dtype=float)
