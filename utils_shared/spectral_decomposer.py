# -*- coding: utf-8 -*-
"""Spectral fit loading and haem decomposition routines."""
# %% IMPORTS -----------------------------------------------------------------------------------------------------------------------------------------
from pathlib import Path

import numpy as np
import pandas as pd

from utils_shared.schema import TIME_COLUMN, SPECTRUM_INDEX_COLUMN, get_times, get_values, measurement_columns
# %% IMPORT FIT --------------------------------------------------------------------------------------------------------------------------------------


def import_fit(filename: Path):
    """
    Import a haem spectral fit CSV

    The file holds (wavelength, response) column pairs, one pair per haem; the header of
    each wavelength column names the haem.
    """
    data = pd.read_csv(filename, delimiter=",")
    headers = data.columns
    haem_names = [str(headers[i]) for i in range(len(headers)) if i % 2 == 0]
    return {"haem_list": haem_names, "data": data}
# %% DECOMPOSITION HELPERS ---------------------------------------------------------------------------------------------------------------------------


def _wavelength_mask(wavelengths, fit_data: pd.DataFrame):
    """Boolean mask selecting wavelengths inside the range shared by all fits."""
    fit_wavelength = fit_data.iloc[:, ::2]
    wmax = min(np.nanmax(fit_wavelength, axis=0))
    wmin = max(np.nanmin(fit_wavelength, axis=0))
    return (wavelengths >= wmin) & (wavelengths <= wmax)


def filter_data(experimental_data: np.ndarray, fit_data: pd.DataFrame):
    """Filter experimental data (wavelength, value columns) to the wavelength range shared by all fits."""
    return experimental_data[_wavelength_mask(experimental_data[:, 0], fit_data)]


def s_array_generator(experimental_data: np.ndarray,
                      fit_data: pd.DataFrame,
                      degree_of_scatter: int = 1,
                      haemfactor: float = 1_000_000):
    """Generate haem and scatter basis components for one spectrum."""
    filtered = filter_data(experimental_data, fit_data)
    no_haems = int(len(fit_data.columns) / 2)
    s_array = np.zeros((len(filtered[:, 0]), no_haems + degree_of_scatter + 1))

    for i in range(no_haems):
        fit_x = fit_data.iloc[:, 2 * i]
        fit_y = fit_data.iloc[:, 2 * i + 1]
        s_array[:, i] = -np.interp(filtered[:, 0], fit_x, fit_y) * haemfactor

    s_array[:, no_haems] = 1.0
    for i in range(degree_of_scatter):
        scatter_function = 1 / filtered[:, 0] ** (i + 1)
        s_array[:, no_haems + i + 1] = (
            (scatter_function - np.amin(scatter_function))
            / np.amax(scatter_function - np.amin(scatter_function))
        )
    return s_array
# %% DECOMPOSITION FUNCTION --------------------------------------------------------------------------------------------------------------------------


def decomposition(experimental_data: np.ndarray,
                  fit_data: pd.DataFrame,
                  degree_of_scatter: int = 1,
                  haemfactor: float = 1_000_000):
    """
    Decompose one experimental spectrum into haem contributions and scatter

    Returns (c_array, filtered_data, scatter, background_subtracted, haems, haem_individual, residual).
    Useful for inspecting a single fit; decompose_experiment() uses an equivalent but faster route.
    """
    no_haems = int(len(fit_data.columns) / 2)
    filtered = filter_data(experimental_data, fit_data)
    wavelengths = filtered[:, 0]
    absorbances = filtered[:, 1]
    s_array = s_array_generator(experimental_data, fit_data, degree_of_scatter, haemfactor)

    c_array = np.matmul(
        np.matmul(np.linalg.inv(np.matmul(np.transpose(s_array), s_array)), np.transpose(s_array)),
        absorbances,
    )

    scatter = np.zeros_like(absorbances)
    for i in range(degree_of_scatter + 1):
        scatter += s_array[:, -(i + 1)] * c_array[-(i + 1)]

    haems = np.zeros_like(absorbances)
    haem_individual = []
    for i in range(no_haems):
        component = s_array[:, i] * c_array[i]
        haem_individual.append(np.column_stack((wavelengths, component)))
        haems += component

    residual = absorbances - (haems + scatter)
    background_subtracted = absorbances - scatter

    return (
        c_array,
        filtered,
        np.column_stack((wavelengths, scatter)),
        np.column_stack((wavelengths, background_subtracted)),
        np.column_stack((wavelengths, haems)),
        haem_individual,
        np.column_stack((wavelengths, residual)),
    )
# %% DECOMPOSE EXPERIMENT FUNCTION -------------------------------------------------------------------------------------------------------------------


def calculate_delta_abs(haem_abs: pd.DataFrame,
                        exclude_first_minutes: float = 5.0,
                        window_seconds: float = 30.0,
                        label: str = "haem_abs") -> pd.DataFrame:
    """
    Shift every haem's absorbance additively so that its reference level is 0, giving a change in absorbance (mOD)

    The reference level of each haem is its mean in the first ``window_seconds`` that start ``exclude_first_minutes``
    after the first measurement (the first minutes are ignored while the sample settles). Nothing is scaled: only a
    constant is subtracted from each haem, so differences between points are unchanged and the shape of the trace is
    kept. The reference window is stored in ``result.attrs["delta_abs_baseline"]``.
    """
    if window_seconds <= 0:
        raise ValueError("window_seconds must be positive.")
    if exclude_first_minutes < 0:
        raise ValueError("exclude_first_minutes cannot be negative.")

    columns = measurement_columns(haem_abs)
    times = get_times(haem_abs)
    finite_times = times[np.isfinite(times)]
    if not columns or finite_times.size == 0:
        raise ValueError(f"{label}: no haem columns or finite times available for the delta absorbance.")

    start = float(finite_times.min()) + exclude_first_minutes
    end = start + window_seconds / 60.0
    in_window = np.isfinite(times) & (times >= start) & (times <= end)
    if not in_window.any():
        raise ValueError(f"{label}: no spectra between {start:.2f} and {end:.2f} min for the delta absorbance reference. "
                         "Reduce the excluded start period or increase the window length.")

    result = haem_abs.copy()
    reference = {}
    for column in columns:
        values = get_values(haem_abs, column)
        selected = values[in_window & np.isfinite(values)]
        if selected.size == 0:
            raise ValueError(f"{label}: no finite {column!r} values in the delta absorbance reference window.")
        reference[str(column)] = float(np.mean(selected))
        result[column] = values - reference[str(column)]

    result.attrs["delta_abs_baseline"] = {
        "mean_by_haem": reference,
        "start_time": float(times[in_window].min()),
        "end_time": float(times[in_window].max()),
        "n_spectra": int(in_window.sum()),
    }
    return result


def decompose_experiment(experiment: dict,
                         fit: dict,
                         dataset_name: str = "Cyt",
                         spectrum_type: str = "attenuation",
                         degree_of_scatter: int = 1,
                         haemfactor: float = 1_000_000,
                         delta_exclude_first_minutes: float = 5.0,
                         delta_window_seconds: float = 30.0):
    """
    Decompose every spectrum of one dataset and store ``experiment["haem_conc"]``, ``experiment["haem_abs"]`` and
    ``experiment["haem_delta_abs"]``

    haem_conc columns: TIME_COLUMN, SPECTRUM_INDEX_COLUMN, one column per haem in the fit.
    haem_abs  same layout, in mOD: the absorbance each haem contributes at the peak of its fit spectrum, i.e. the
              fitted coefficient multiplied by the fit's peak amplitude (the wavelength where |fit| is largest). This is
              the signal *before* any extinction coefficient is applied, so it does not depend on the isolated-enzyme
              coefficients. It is proportional to haem_conc, with the same sign, and does not depend on haemfactor.
    haem_delta_abs  haem_abs minus each haem's mean over the first ``delta_window_seconds`` that start
              ``delta_exclude_first_minutes`` after the first spectrum (see calculate_delta_abs), so it starts at 0 and
              shows the change in absorbance (mOD) from that point.
    The basis spectra depend only on the wavelengths, so the least-squares projector is
    built once and applied to all spectra (same maths as decomposition()).
    """
    name = experiment.get("experiment_name", "<unknown>")

    if fit is None or "data" not in fit or "haem_list" not in fit:
        raise ValueError("A valid fit returned by import_fit() is required.")

    raw_spectra = experiment.get("raw_spectra", {})
    if dataset_name not in raw_spectra:
        raise ValueError(
            f"{name}: unknown spectral dataset {dataset_name!r}. "
            f"Available datasets: {', '.join(raw_spectra) or '<none>'}"
        )

    dataset = raw_spectra[dataset_name]
    if spectrum_type not in dataset:
        raise ValueError(
            f"{name}/{dataset_name}: spectral data type {spectrum_type!r} not found. "
            f"Available fields: {', '.join(dataset)}"
        )

    wavelengths = np.asarray(dataset["wavelengths"], dtype=float)
    spectra = np.asarray(dataset[spectrum_type], dtype=float)
    spectrum_indices = np.asarray(dataset["spectrum_indices"])
    times = np.asarray(dataset["time"], dtype=float)

    if wavelengths.ndim != 1:
        raise ValueError(f"{name}/{dataset_name}: wavelengths must be a 1D array.")
    if spectra.ndim != 2 or spectra.shape[1] != len(wavelengths):
        raise ValueError(f"{name}/{dataset_name}: {spectrum_type!r} must be a (spectra x wavelengths) array.")
    if len(spectrum_indices) != len(spectra) or len(times) != len(spectra):
        raise ValueError(f"{name}/{dataset_name}: spectrum index/time count does not match spectra.")
    if not np.all(np.isfinite(times)):
        raise ValueError(f"{name}/{dataset_name}: spectrum times are unavailable (spectra/CsO2 length mismatch).")

    fit_data = fit["data"]
    haem_names = list(fit["haem_list"])

    mask = _wavelength_mask(wavelengths, fit_data)
    s_array = s_array_generator(np.column_stack((wavelengths, spectra[0])),
                                fit_data, degree_of_scatter, haemfactor)
    projector = np.linalg.inv(s_array.T @ s_array) @ s_array.T
    coefficients = spectra[:, mask] @ projector.T          # (n_spectra, n_components)

    haem_conc = pd.DataFrame(coefficients[:, :len(haem_names)], columns=haem_names)
    haem_conc.insert(0, SPECTRUM_INDEX_COLUMN, spectrum_indices)
    haem_conc.insert(0, TIME_COLUMN, times)
    experiment["haem_conc"] = haem_conc

    # Peak amplitude (OD per unit coefficient) of each haem's basis spectrum; x1000 converts OD to mOD.
    peak_amplitude = np.max(np.abs(s_array[:, :len(haem_names)]), axis=0)
    haem_abs = haem_conc.copy()
    haem_abs[haem_names] = coefficients[:, :len(haem_names)] * peak_amplitude * 1000.0
    haem_abs.attrs["peak_amplitude_OD"] = dict(zip(haem_names, peak_amplitude.tolist()))
    experiment["haem_abs"] = haem_abs
    experiment["haem_delta_abs"] = calculate_delta_abs(haem_abs, delta_exclude_first_minutes, delta_window_seconds,
                                                       label=f"{name}/haem_abs")
    return experiment
