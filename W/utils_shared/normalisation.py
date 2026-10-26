# -*- coding: utf-8 -*-
"""Normalisation of VoO2 and haem data: OD normalisation (of VoO2, haem concentration,
haem abs and haem delta abs) and relative (0-100 %) scaling (of VoO2 and haem
concentration only)."""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from typing import Any, Union

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pandas as pd

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.schema import measurement_column_finder, time_getter


# ---- NORMALISATION HELPERS -----------------------------------------------------------


# ---- _FRAME NORMALISER ---------------------------------------------------------------
def _frame_normaliser(df: pd.DataFrame, **kwargs: Any) -> pd.DataFrame:
    """
    ---- Summary ----
    Helper function to OD-normalise the measurement columns of a data frame, leaving the
    time and index columns untouched.

    ---- Inputs ----
    df : pd.DataFrame
        Data frame with a time column and measurement columns.
    **kwargs : Any
        optical_density, volume and dilution_factor, passed to data_normaliser.

    ---- Globals read ----
    None.

    ---- Outputs ----
    pd.DataFrame
        Scaled copy of the data frame.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    data_normaliser
    measurement_column_finder
    """

    result = df.copy()
    columns = measurement_column_finder(df)
    if columns:
        result[columns] = data_normaliser(df[columns], **kwargs)
    return result


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- DATA NORMALISER -----------------------------------------------------------------
def data_normaliser(data: Union[pd.DataFrame, pd.Series, np.ndarray],
                    optical_density: float,
                    volume: float,
                    dilution_factor: float,
                    ) -> Union[pd.DataFrame, pd.Series, np.ndarray]:
    """
    ---- Summary ----
    Main function to divide numeric data by dilution factor x optical density x volume.

    ---- Inputs ----
    data : Union[pd.DataFrame, pd.Series, np.ndarray]
        Numeric data to scale.
    optical_density : float
        OD of the sample (> 0).
    volume : float
        Volume of the sample (> 0).
    dilution_factor : float
        Dilution factor (> 0).

    ---- Globals read ----
    None.

    ---- Outputs ----
    Union[pd.DataFrame, pd.Series, np.ndarray]
        Scaled data of the same kind as the input. Raises ValueError if the denominator
        is not positive and finite.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    scaled = data / (dilution_factor x optical_density x volume).

    ---- Helpers ----
    None.
    """

    denominator = float(dilution_factor) * float(optical_density) * float(volume)
    if not np.isfinite(denominator) or denominator <= 0:
        raise ValueError('Dilution factor x OD x volume must be positive and finite.')
    if isinstance(data, pd.DataFrame):
        return data.apply(lambda column: pd.to_numeric(column, errors='raise'),
                          ) / denominator
    if isinstance(data, pd.Series):
        return pd.to_numeric(data, errors='raise') / denominator
    return np.asarray(data, dtype=float) / denominator


# ---- EXPERIMENT NORMALISER -----------------------------------------------------------
def experiment_normaliser(experiment: dict) -> dict:
    """
    ---- Summary ----
    Main function to OD-normalise VoO2 and, when present, the haem data of an
    experiment.

    ---- Inputs ----
    experiment : dict
        Experiment dictionary, as defined in DATA_FORMAT.md.

    ---- Globals read ----
    None. Calls schema.measurement_columns.

    ---- Outputs ----
    dict
        The same experiment dictionary. Raises KeyError if dilution_factor, OD or volume
        is missing from the metadata, and ValueError if VoO2 has no measurement columns.

    ---- Globals mutated ----
    experiment: adds VoO2_OD and, for each of haem_conc, haem_abs and haem_delta_abs
    that exists, haem_OD, haem_abs_OD and haem_delta_abs_OD.

    ---- Equations ----
    x_OD = x / (dilution_factor x OD x volume). Dividing by a constant commutes with the
    shift behind delta abs, so haem_delta_abs_OD equals the shifted haem_abs_OD.

    ---- Helpers ----
    _frame_normaliser
    measurement_column_finder
    """

    # ---- 1 Check the required settings -----------------------------------------------
    metadata = experiment['metadata']
    missing = [key for key in ('dilution_factor', 'OD', 'volume') if key not in metadata
               ]
    if missing:
        raise KeyError(f"{experiment['experiment_name']}: missing OD-normalisation "
                       f'metadata {missing}',
                       )

    # ---- 2 Normalise the data --------------------------------------------------------
    kwargs = {'optical_density': metadata['OD'],
              'volume': metadata['volume'],
              'dilution_factor': metadata['dilution_factor'],
              }
    if not measurement_column_finder(experiment['VoO2']):
        raise ValueError(f"{experiment['experiment_name']}: no VoO2 measurement "
                         f'columns found',
                         )
    experiment['VoO2_OD'] = _frame_normaliser(experiment['VoO2'], **kwargs)
    for source_key, target_key in (('haem_conc', 'haem_OD'),
                                   ('haem_abs', 'haem_abs_OD'),
                                   ('haem_delta_abs', 'haem_delta_abs_OD'),
                                   ):
        if isinstance(experiment.get(source_key), pd.DataFrame):
            experiment[target_key] = _frame_normaliser(experiment[source_key], **kwargs)
    return experiment


# ---- PERCENT CONVERTER ---------------------------------------------------------------
def percent_converter(experiment: dict,
                      source_key: str,
                      target_key: str,
                      **scaling_kwargs: Any,
                      ) -> dict:
    """
    ---- Summary ----
    Main function to scale one table of an experiment to 0-100 % and store it under a
    new key.

    ---- Inputs ----
    experiment : dict
        Experiment dictionary, as defined in DATA_FORMAT.md.
    source_key : str
        Key of the table to scale, e.g. 'haem_conc' or 'VoO2'.
    target_key : str
        Key the scaled table is stored under, e.g. 'haem_percent'.
    **scaling_kwargs : Any
        exclude_first_minutes, exclude_last_minutes and window_seconds, passed to
        percent_scaler.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        The same experiment dictionary. Raises ValueError if the source table is
        unavailable.

    ---- Globals mutated ----
    experiment: adds experiment[target_key].

    ---- Equations ----
    None.

    ---- Helpers ----
    percent_scaler
    """

    # ---- 1 Check the source ----------------------------------------------------------
    source = experiment.get(source_key)
    if not isinstance(source, pd.DataFrame):
        raise ValueError(f"{experiment['experiment_name']}: {source_key} is "
                         f'unavailable, cannot scale to percent.',
                         )

    # ---- 2 Convert to percentages ----------------------------------------------------
    experiment[target_key] = percent_scaler(source,
                                            label=f"{experiment['experiment_name']}/"
                                            f'{source_key}',
                                            **scaling_kwargs,
                                            )
    return experiment


# ---- PERCENT SCALER ------------------------------------------------------------------
def percent_scaler(df: pd.DataFrame,
                   label: str = 'data',
                   exclude_first_minutes: float = 0.0,
                   exclude_last_minutes: float = 0.0,
                   window_seconds: float = 30.0,
                   ) -> pd.DataFrame:
    """
    ---- Summary ----
    Main function to scale each measurement column of a data frame to a relative 0-100 %
    range.

    ---- Inputs ----
    df : pd.DataFrame
        Data frame with a time column (minutes) and measurement columns.
    label : str
        Name used in error messages.
    exclude_first_minutes : float
        Windows must start at least this long after the first measurement.
    exclude_last_minutes : float
        Windows must finish at least this long before the last measurement.
    window_seconds : float
        Length of each averaging window, in seconds (> 0).

    ---- Globals read ----
    schema.get_times, measurement_columns.

    ---- Outputs ----
    pd.DataFrame
        Scaled copy; the windows used are stored in result.attrs["percent_scaling"]. A
        constant column becomes NaN. Raises ValueError for invalid settings or when no
        complete window remains.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    percent = (value - low) / (high - low) x 100, where low and high are the lowest and
    highest window means (windows must contain data spanning at least 80 % of their
    length). Values outside the range are kept.

    ---- Helpers ----
    measurement_column_finder
    time_getter
    """

    # ---- 1 Validate the inputs -------------------------------------------------------
    if window_seconds <= 0:
        raise ValueError('window_seconds must be positive.')
    if exclude_first_minutes < 0 or exclude_last_minutes < 0:
        raise ValueError('Excluded periods cannot be negative.')

    # ---- 2 Find the allowed windows --------------------------------------------------
    columns = measurement_column_finder(df)
    if not columns:
        raise ValueError(f'{label}: no measurement columns were found.')
    times = time_getter(df)
    finite_times = times[np.isfinite(times)]
    if finite_times.size == 0:
        raise ValueError(f'{label}: no finite measurement times are available.')
    window_minutes = window_seconds / 60.0
    first_allowed = finite_times.min() + exclude_first_minutes
    last_allowed = finite_times.max() - exclude_last_minutes
    # Candidate windows must start after the excluded period and fit before the end.
    allowed = (np.isfinite(times) &
               (times >= first_allowed) &
               (times + window_minutes <= last_allowed + 1e-12))
    candidate_starts = (np.unique(times[allowed],
                                  )
                        )
    if candidate_starts.size == 0:
        raise ValueError(f'{label}: no complete {window_seconds:g}-second windows '
                         f'remain after excluding the '
                         'initial/final periods. Reduce the exclusion or window '
                         'duration.',
                         )

    # ---- 3 Scale each column ---------------------------------------------------------
    result = df.copy()
    scaling_info = {}
    for column in columns:
        values = pd.to_numeric(df[column], errors='coerce').to_numpy(dtype=float)
        lowest = highest = None
        for start in candidate_starts:
            mask = (np.isfinite(times) & np.isfinite(values) & (times >= start) &
                    (times <= start + window_minutes))
            window_times, window_values = times[mask], values[mask]
            # Require measurements to span at least 80 % of the window.
            if (window_times.size < 2 or
                window_times.max() - window_times.min() < window_minutes * 0.8
                ):
                continue
            info = {'mean': float(np.mean(window_values)),
                    'start_time': float(window_times.min()),
                    'end_time': float(window_times.max()),
                    'n_points': int(window_values.size),
                    }
            if lowest is None or info['mean'] < lowest['mean']:
                lowest = info
            if highest is None or info['mean'] > highest['mean']:
                highest = info
        if lowest is None or highest is None:
            raise ValueError(f'{label}: insufficient data to find valid '
                             f'{window_seconds:g}-second windows for {column!r}.',
                             )
        low, span = lowest['mean'], highest['mean'] - lowest['mean']
        # A constant signal has no measurable relative range.
        result[column] = (np.nan
                          if np.isclose(span, 0.0)
                          else (values - low) / span * 100.0
                          )
        scaling_info[column] = {'zero_percent_window': lowest,
                                'hundred_percent_window': highest,
                                'minimum_mean': low,
                                'maximum_mean': highest['mean'],
                                }
    result.attrs['percent_scaling'] = scaling_info
    return result
