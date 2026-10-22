# -*- coding: utf-8 -*-
"""Convert transmission spectra to the attenuation spectra used for decomposition."""
import numpy as np


def transmission_to_attenuation(transmission, mode="fraction"):
    """
    Convert one transmission spectrum to attenuation

    mode: "fraction" (0-1), "percentage" (0-100) or "absorbance" (already converted).

    SIGN CONVENTION (intentional, known quirk): this returns log10(T), which is the
    NEGATIVE of the conventional attenuation -log10(T). The decomposition basis spectra
    in spectral_decomposer.py are also negated, and together these give haem
    concentrations the expected way round. Change both together or neither.
    """
    transmission = np.asarray(transmission, dtype=float)

    if mode == "absorbance":
        return transmission.copy()
    if mode == "fraction":
        transmittance = transmission
    elif mode == "percentage":
        transmittance = transmission / 100.0
    else:
        raise ValueError(f"Unknown transmission mode: {mode!r}")

    # Zero, negative or non-finite transmission has no logarithm. Those values become NaN (a gap in the decomposition for the
    # spectra that contain them) instead of stopping the whole experiment; the caller reports how many there were.
    bad = ~np.isfinite(transmittance) | (transmittance <= 0)
    with np.errstate(divide="ignore", invalid="ignore"):
        attenuation = np.log10(np.where(bad, np.nan, transmittance))
    return attenuation


def add_attenuation_to_experiment(experiment, mode="fraction", datasets=None):
    """Add an ``attenuation`` array (spectra x wavelengths) to the datasets in ``raw_spectra`` (all of them if ``datasets`` is None)."""
    for dataset_name, dataset in experiment.get("raw_spectra", {}).items():
        if datasets is not None and dataset_name not in datasets:
            continue
        transmission = np.asarray(dataset.get("transmission"), dtype=float)

        if transmission.ndim != 2:
            raise ValueError(
                f"{experiment.get('experiment_name', '<unknown>')}: {dataset_name}: "
                "transmission must be a 2D array before attenuation conversion."
            )

        dataset["attenuation"] = transmission_to_attenuation(transmission, mode=mode)
        n_bad = int(np.count_nonzero(np.isnan(dataset["attenuation"]) & ~np.isnan(transmission)) +
                    np.count_nonzero(np.isnan(transmission)))
        if n_bad:
            rows = int(np.count_nonzero(np.isnan(dataset["attenuation"]).any(axis=1)))
            print(f"  Warning: {dataset_name}: {n_bad} transmission values were zero, negative or missing "
                  f"({rows} spectra affected); they are left blank.")
    return experiment
