"""
Trimming of the start and end of an experiment.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from typing import Optional

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.schema import TIME_COLUMN


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- experiment_trimmer --------------------------------------------------------------
def experiment_trimmer(experiment: dict,
                       start_time: Optional[float] = None,
                       end_time: Optional[float] = None,
                       ) -> dict:
    """
    ---- Summary ----
    Main function to keep only the part of an experiment between a start and an end
    time. After a start trim the time axis is re-zeroed so the chosen start becomes 0,
    and events keep their original datapoint numbers.

    ---- Inputs ----
    experiment : dict
        Experiment dictionary, as defined in DATA_FORMAT.md.
    start_time : Optional[float]
        Start of the part kept, in minutes on the original recording; None keeps the
        start.
    end_time : Optional[float]
        End of the part kept, in minutes on the original recording; None keeps the end.

    ---- Globals read ----
    TIME_COLUMN (module constant).

    ---- Outputs ----
    dict
        The same experiment dictionary, trimmed in place. Raises ValueError for an
        invalid time range, events outside the range, no data left, or missing spectrum
        times.

    ---- Globals mutated ----
    None. Trims CcO2, CsO2, VoO2 and the raw spectra, shifts the event times and sets
    metadata trimmed_before_minutes / trimmed_after_minutes in place (side effects).

    ---- Equations ----
    t_new = t - start_time; rows kept where start_time <= t <= end_time.

    ---- Helpers ----
    None.
    """

    # ---- 1 Validate the time range ---------------------------------------------------
    name = experiment['experiment_name']
    start = 0.0 if start_time is None else float(start_time)
    end = np.inf if end_time is None else float(end_time)
    if start < 0:
        raise ValueError(f'{name}: the start time cannot be negative.')
    if end <= start:
        raise ValueError(f'{name}: the end time ({end:g} min) must be after the start '
                         f'time ({start:g} min).',
                         )

    # ---- 2 Check the events ----------------------------------------------------------
    events = experiment['metadata'].get('events', [])
    early = [e for e in events if e['time'] < start]
    late = [e for e in events if e['time'] > end]
    if early:
        raise ValueError(f'{name}: cannot trim the start at {start:g} min because '
                         f'{len(early)} event(s) occur earlier.',
                         )
    if late:
        raise ValueError(f'{name}: cannot trim the end at {end:g} min because '
                         f'{len(late)} event(s) occur later.',
                         )

    # ---- 3 Trim the data tables ------------------------------------------------------
    for key in ('CcO2', 'CsO2', 'VoO2'):
        frame = experiment.get(key)
        if frame is None:
            continue
        times = frame[TIME_COLUMN].to_numpy(dtype=float)
        trimmed = frame.loc[(times >= start) & (times <= end)].reset_index(drop=True)
        if trimmed.empty:
            raise ValueError(f'{name}: trimming {key} to {start:g}-{end:g} min leaves '
                             f'no data.',
                             )
        trimmed[TIME_COLUMN] = trimmed[TIME_COLUMN].to_numpy(dtype=float) - start
        experiment[key] = trimmed

    # ---- 4 Trim the raw spectra ------------------------------------------------------
    for dataset_name, dataset in experiment['raw_spectra'].items():
        if not np.all(np.isfinite(dataset['time'])):
            raise ValueError(f'{name}/{dataset_name}: cannot trim because spectrum '
                             f'times are unavailable.',
                             )
        keep = (dataset['time'] >= start) & (dataset['time'] <= end)
        for field in ('spectrum_indices',
                      'time',
                      'transmission',
                      'intensity',
                      'attenuation',
                      ):
            if field in dataset:
                dataset[field] = dataset[field][keep]
        dataset['time'] = dataset['time'] - start

    # ---- 5 Shift the events and record the trim --------------------------------------
    for event in events:
        event['time'] = float(event['time']) - start
        event.pop('row_index', None)  # no longer a row of the trimmed data
    if start_time is not None:
        experiment['metadata']['trimmed_before_minutes'] = start
    if end_time is not None:
        experiment['metadata']['trimmed_after_minutes'] = end
    return experiment
