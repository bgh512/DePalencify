# -*- coding: utf-8 -*-
"""Convert transmission spectra to the attenuation spectra used for decomposition."""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from typing import Optional, Sequence, Union

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- ATTENUATION CONVERTER -----------------------------------------------------------
def attenuation_converter(transmission: Union[Sequence[float], np.ndarray],
                          mode: str = 'fraction',
                          ) -> np.ndarray:
    """
    ---- Summary ----
    Main function to convert transmission spectra to attenuation (log10 of the
    transmittance).

    ---- Inputs ----
    transmission : Union[Sequence[float], np.ndarray]
        Transmission values, any shape.
    mode : str
        Meaning of the input: 'fraction' (0-1), 'percentage' (0-100) or 'absorbance'
        (already converted, returned as is).

    ---- Globals read ----
    None.

    ---- Outputs ----
    np.ndarray
        Attenuation with the shape of the input. Zero, negative or non-finite
        transmission becomes NaN. Raises ValueError for an unknown mode.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    attenuation = log10(T), where T is the transmittance (fraction). This is the
    NEGATIVE of the conventional -log10(T); the decomposition basis spectra are negated
    too, so the two signs cancel (change both together or neither).

    ---- Helpers ----
    None.
    """

    # ---- 1 Convert the input to transmittance ----------------------------------------
    transmission = np.asarray(transmission, dtype=float)
    if mode == 'absorbance':
        return transmission.copy()
    if mode == 'fraction':
        transmittance = transmission
    elif mode == 'percentage':
        transmittance = transmission / 100.0
    else:
        raise ValueError(f'Unknown transmission mode: {mode!r}')

    # ---- 2 Calculate the attenuation -------------------------------------------------
    # Zero, negative or non-finite transmission has no logarithm. Those values become
    # NaN (a gap in the decomposition for the
    # spectra that contain them) instead of stopping the whole experiment; the caller
    # reports how many there were.
    bad = ~np.isfinite(transmittance) | (transmittance <= 0)
    with np.errstate(divide='ignore', invalid='ignore'):
        attenuation = np.log10(np.where(bad, np.nan, transmittance))
    return attenuation


# ---- EXPERIMENT ATTENUATION ADDER ----------------------------------------------------
def experiment_attenuation_adder(experiment: dict,
                                 mode: str = 'fraction',
                                 datasets: Optional[Sequence[str]] = None,
                                 ) -> dict:
    """
    ---- Summary ----
    Main function to add an attenuation array to the spectral datasets of an experiment.

    ---- Inputs ----
    experiment : dict
        Experiment dictionary, as defined in DATA_FORMAT.md.
    mode : str
        Transmission mode passed to attenuation_converter ('fraction', 'percentage' or
        'absorbance').
    datasets : Optional[Sequence[str]]
        Dataset names to convert; None converts all of them.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        The same experiment dictionary. Raises ValueError if a transmission array is not
        2D.

    ---- Globals mutated ----
    experiment: adds raw_spectra[dataset]["attenuation"] (n_spectra x n_wavelengths) for
    each converted dataset; prints a warning with the number of blank values (side
    effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    attenuation_converter
    """

    # ---- 1 Add the attenuation to each raw spectrum ----------------------------------
    for dataset_name, dataset in experiment.get('raw_spectra', {}).items():
        if datasets is not None and dataset_name not in datasets:
            continue
        transmission = np.asarray(dataset.get('transmission'), dtype=float)
        if transmission.ndim != 2:
            raise ValueError(f"{experiment.get('experiment_name', '<unknown>')}: "
                             f'{dataset_name}: '
                             'transmission must be a 2D array before attenuation '
                             'conversion.',
                             )
        dataset['attenuation'] = attenuation_converter(transmission, mode=mode)
        n_bad = int(np.count_nonzero(np.isnan(dataset['attenuation'],
                                              ) & ~np.isnan(transmission),
                                     ) + np.count_nonzero(np.isnan(transmission)),
                    )
        if n_bad:
            rows = int(np.count_nonzero(np.isnan(dataset['attenuation']).any(axis=1)))
            print(f'  Warning: {dataset_name}: {n_bad} transmission values were zero, '
                  f'negative or missing '
                  f'({rows} spectra affected); they are left blank.',
                  )
    return experiment
