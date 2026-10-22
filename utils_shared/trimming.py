# -*- coding: utf-8 -*-
"""Cut the start and/or end off an experiment. All times are minutes on the original recording's clock."""
import numpy as np

from utils_shared.schema import TIME_COLUMN


def trim_experiment(experiment, start_time=None, end_time=None):
    """
    Keep only ``start_time <= t <= end_time`` (either may be None)

    After a start trim the time axis is re-zeroed so the chosen start becomes 0 (CcO2/CsO2/VoO2, spectra and event times all shift).
    Events keep their original ``datapoint`` number, which is what ties saved labels and concentrations to them.
    """
    name = experiment["experiment_name"]
    start = 0.0 if start_time is None else float(start_time)
    end = np.inf if end_time is None else float(end_time)
    if start < 0:
        raise ValueError(f"{name}: the start time cannot be negative.")
    if end <= start:
        raise ValueError(f"{name}: the end time ({end:g} min) must be after the start time ({start:g} min).")

    events = experiment["metadata"].get("events", [])
    early = [e for e in events if e["time"] < start]
    late = [e for e in events if e["time"] > end]
    if early:
        raise ValueError(f"{name}: cannot trim the start at {start:g} min because {len(early)} event(s) occur earlier.")
    if late:
        raise ValueError(f"{name}: cannot trim the end at {end:g} min because {len(late)} event(s) occur later.")

    for key in ("CcO2", "CsO2", "VoO2"):
        frame = experiment.get(key)
        if frame is None:
            continue
        times = frame[TIME_COLUMN].to_numpy(dtype=float)
        trimmed = frame.loc[(times >= start) & (times <= end)].reset_index(drop=True)
        if trimmed.empty:
            raise ValueError(f"{name}: trimming {key} to {start:g}-{end:g} min leaves no data.")
        trimmed[TIME_COLUMN] = trimmed[TIME_COLUMN].to_numpy(dtype=float) - start
        experiment[key] = trimmed

    for dataset_name, dataset in experiment["raw_spectra"].items():
        if not np.all(np.isfinite(dataset["time"])):
            raise ValueError(f"{name}/{dataset_name}: cannot trim because spectrum times are unavailable.")
        keep = (dataset["time"] >= start) & (dataset["time"] <= end)
        for field in ("spectrum_indices", "time", "transmission", "intensity", "attenuation"):
            if field in dataset:
                dataset[field] = dataset[field][keep]
        dataset["time"] = dataset["time"] - start

    for event in events:
        event["time"] = float(event["time"]) - start
        event.pop("row_index", None)                       # no longer a row of the trimmed data
    if start_time is not None:
        experiment["metadata"]["trimmed_before_minutes"] = start
    if end_time is not None:
        experiment["metadata"]["trimmed_after_minutes"] = end
    return experiment
