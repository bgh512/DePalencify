# -*- coding: utf-8 -*-
"""Export one processed experiment to an Excel workbook (optionally with spectral CSV files), and read the saved settings back."""
# %% IMPORTS -----------------------------------------------------------------------------------------------------------------------------------------
import json
from pathlib import Path

import numpy as np
import pandas as pd

from utils_shared.helpers import excel_sheet_name, safe_file_name
from utils_shared.schema import DELTA_HAEM_SOURCES

# Sheets written when the whole data set is exported (the short export holds only the first three).
BASIC_SHEETS = ("CcO2", "CsO2", "VoO2")
# Sheets are written in this order; any that are absent from the experiment are skipped.
# (experiment dictionary key, worksheet name)
DATA_SHEETS = (
    ("CcO2", "CcO2"),
    ("CsO2", "CsO2"),
    ("VoO2", "VoO2"),
    ("VoO2_OD", "VoO2_OD"),
    ("VoO2_percent", "VoO2_percent"),
    ("haem_conc", "haem_conc"),
    ("haem_abs", "haem_abs"),
    ("haem_delta_abs", "haem_delta_abs"),
    ("haem_OD", "haem_OD"),
    ("haem_abs_OD", "haem_abs_OD"),
    ("haem_delta_abs_OD", "haem_delta_abs_OD"),
    ("haem_percent", "haem_percent"),
)

# Spectral arrays exported to CSV (they are far too large for worksheets).
SPECTRAL_CSV_TYPES = (
    ("transmission", "transmiss"),
    ("intensity", "intensity"),
    ("attenuation", "attenuation"),
)
# %% SPECTRAL CSV FILES ------------------------------------------------------------------------------------------------------------------------------


def _export_spectral_csvs(experiment, folder):
    """Write one CSV per dataset/type (wavelengths down, one column per spectrum); returns a list of records."""
    name = experiment.get("experiment_name", "experiment")
    records = []

    for dataset_name, dataset in experiment.get("raw_spectra", {}).items():
        wavelengths = np.asarray(dataset["wavelengths"])
        times = np.asarray(dataset["time"], dtype=float)
        indices = np.asarray(dataset["spectrum_indices"])

        for data_key, file_suffix in SPECTRAL_CSV_TYPES:
            if dataset.get(data_key) is None:
                continue

            spectra = np.asarray(dataset[data_key], dtype=float)
            if spectra.ndim != 2:
                continue
            if spectra.shape[1] != len(wavelengths):
                raise ValueError(f"{name}/{dataset_name}: {data_key} does not match the number of wavelengths.")

            # Label each spectrum by its time; fall back to its index if times are unavailable.
            labels = [f"{t:g} min" if np.isfinite(t) else f"Spectrum {i}" for t, i in zip(times, indices)]
            frame = pd.DataFrame(spectra.T, columns=labels)
            frame.insert(0, "Wavelength (nm)", wavelengths)

            csv_name = f"{dataset_name}_{file_suffix}.csv"
            frame.to_csv(folder / csv_name, index=False)

            records.append({
                "Dataset": dataset_name,
                "Data type": data_key,
                "CSV file": csv_name,
                "Wavelengths": len(wavelengths),
                "Timepoints": spectra.shape[0],
            })
    return records
# %% AVERAGES TABLE ----------------------------------------------------------------------------------------------------------------------------------


def averages_table(averages):
    """
    Build the Averages worksheet table

    Columns: Average, Start time (min), End time (min), then for VoO2 and each haem:
    mean, SD and change from baseline (window mean as % of the average0 mean).
    """
    windows = averages["windows"]

    def names(kind):
        return list(dict.fromkeys(m for w in windows.values() for m in w[kind]))

    vo2_names, haem_names = names("vo2"), names("haem")
    groups = [("vo2", m, "VoO2" if len(vo2_names) == 1 else f"VoO2 ({m})") for m in vo2_names]
    groups += [("haem", m, str(m)) for m in haem_names]

    rows = []
    for window_name, window in windows.items():
        row = {"Average": window_name,
               "Start time (min)": window["start_time"],
               "End time (min)": window["end_time"]}
        for kind, measurement, label in groups:
            stats = window[kind].get(measurement, {})
            row[f"{label} mean"] = stats.get("mean", np.nan)
            row[f"{label} SD"] = stats.get("sd", np.nan)
            row[f"{label} change from baseline (%)"] = stats.get("change", np.nan)
        rows.append(row)
    return pd.DataFrame(rows)
# %% SAVED SETTINGS ---------------------------------------------------------------------------------------------------------------------------------
# What the user typed for an experiment (OD, volume, dilution factor, event labels and concentrations) is kept in the workbook, on the
# "Metadata" and "Events" sheets, and read back on the next run so it does not have to be typed again.
SETTINGS_KEYS = ("OD", "volume", "dilution_factor")


def workbook_path(output_dir, experiment_name):
    name = safe_file_name(experiment_name)
    return Path(output_dir) / name / f"{name}.xlsx"


def read_saved_settings(output_dir, experiment_name):
    """Return ``{"OD", "volume", "dilution_factor", "events": [{"datapoint", "label", "concentration_uM"}]}`` from an earlier export, or None."""
    path = workbook_path(output_dir, experiment_name)
    if not path.is_file():
        return None
    try:
        sheets = pd.read_excel(path, sheet_name=None)      # every sheet; older workbooks may lack "Events"
    except Exception:                    # a file open in Excel, a damaged file: just ask again
        return None
    if "Metadata" not in sheets:
        return None
    saved = {}
    metadata = sheets["Metadata"]
    for field, value in zip(metadata["Field"], metadata["Value"]):
        if field in SETTINGS_KEYS and pd.notna(value):
            try:
                saved[field] = float(value)
            except (TypeError, ValueError):
                pass
    events = []
    for _, row in sheets.get("Events", pd.DataFrame()).iterrows():
        concentration = row.get("concentration_uM")
        events.append({"datapoint": int(row["datapoint"]), "label": "" if pd.isna(row.get("label")) else str(row["label"]),
                       "concentration_uM": None if pd.isna(concentration) else float(concentration),
                       "ignored": bool(row.get("ignored", False)) if pd.notna(row.get("ignored", False)) else False})
    saved["events"] = events
    return saved if any(k in saved for k in SETTINGS_KEYS) or events else None
# %% EXPORT ------------------------------------------------------------------------------------------------------------------------------------------


def export_individual_experiment(experiment, output_dir, full=False, spectra=False):
    """
    Export one experiment to ``<output_dir>/<experiment name>/<experiment name>.xlsx``

    Always: the CcO2, CsO2 and VoO2 sheets, the Averages sheet (if averages were calculated), Events and Metadata.
    full=True   adds every processed table (VoO2_OD, haem_conc, haem_abs, haem_delta_abs, ... in the order of DATA_SHEETS).
    spectra=True also writes the spectral CSV files next to the workbook (large and slow) and an index sheet linking to them.
    Returns the workbook path.
    """
    name = safe_file_name(experiment.get("experiment_name", "experiment"))
    folder = Path(output_dir) / name
    folder.mkdir(parents=True, exist_ok=True)
    output_path = folder / f"{name}.xlsx"

    spectral_records = _export_spectral_csvs(experiment, folder) if spectra else []
    used_sheets = set()
    sheet_keys = DATA_SHEETS if full else tuple((k, k) for k in BASIC_SHEETS)

    with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
        workbook = writer.book
        header_format = workbook.add_format({"bold": True, "bg_color": "#D9EAD3", "border": 1, "text_wrap": True})
        link_format = workbook.add_format({"font_color": "blue", "underline": 1})

        def write_frame(frame, sheet_title, first_col_width=18):
            """Write a DataFrame as a formatted worksheet and return the worksheet."""
            sheet = excel_sheet_name(sheet_title, used_sheets)
            frame.to_excel(writer, sheet_name=sheet, index=False)
            worksheet = writer.sheets[sheet]
            for col, column_name in enumerate(frame.columns):
                worksheet.write(0, col, str(column_name), header_format)
            worksheet.set_row(0, 32)
            worksheet.set_column(0, 0, first_col_width)
            worksheet.set_column(1, max(len(frame.columns), 2), 16)
            worksheet.freeze_panes(1, 0)
            return worksheet

        # 1. Spectral data index (links to the CSVs).
        if spectral_records:
            worksheet = write_frame(pd.DataFrame(spectral_records), "Spectral data", first_col_width=14)
            for row, record in enumerate(spectral_records, start=1):
                worksheet.write_url(row, 2, f"external:{record['CSV file']}", link_format, string=record["CSV file"])
            worksheet.set_column(2, 2, 28)

        # 2. Time-resolved datasets.
        for key, sheet_title in sheet_keys:
            frame = experiment.get(key)
            if isinstance(frame, pd.DataFrame) and not frame.empty:
                write_frame(frame, sheet_title)

        # 3. Event-window averages.
        averages = experiment.get("averages")
        if averages and averages.get("windows"):
            table = averages_table(averages)
            worksheet = write_frame(table, "Averages", first_col_width=14)
            settings = averages["settings"]
            used = [f"{label} source: {key}" for label, key in (("VoO2", settings.get("vo2_key")), ("haem", settings.get("haem_key"))) if key]
            notes = [
                "; ".join(used) + ".",
                f"Windows are {settings['window_minutes']:g} min long, ending {settings['gap_minutes']:g} min "
                f"before each addition and {settings['final_window_gap_minutes']:g} min before the end of the recording.",
                "Change from baseline = window mean as a percentage of the average0 mean (average0 = 100 %).",
            ]
            if settings.get("haem_source") in DELTA_HAEM_SOURCES:
                notes.append("Haem change from baseline (%) is not calculated for delta abs sources (they start at 0).")
            for offset, note in enumerate(notes, start=2):
                worksheet.write(len(table) + offset, 0, note)

        metadata = experiment.get("metadata") if isinstance(experiment.get("metadata"), dict) else {}

        # 4. Events, with the label and concentration the user entered.
        events = sorted(list(metadata.get("events", [])) + list(metadata.get("ignored_events", [])),
                        key=lambda e: e.get("time") if e.get("time") is not None else 0)
        if True:                                   # always written, so the sheet exists even for a file with no events
            write_frame(pd.DataFrame({
                "event": [f"Event {i}" for i in range(1, len(events) + 1)],
                "datapoint": [e.get("datapoint") for e in events],
                "time_min": [e.get("time") for e in events],
                "paf_text": [e.get("text", "") for e in events],
                "label": [e.get("label", "") for e in events],
                "concentration_uM": [e.get("concentration_uM") for e in events],
                "ignored": [bool(e.get("ignored", False)) for e in events]}), "Events", first_col_width=12)

        # 5. Metadata (OD, volume, dilution factor, settings used, notes, acquisition details).
        fields = [(k, v) for k, v in metadata.items() if k not in ("events", "ignored_events", "binary_metadata")]
        frame = pd.DataFrame({
            "Field": [k for k, _ in fields],
            "Value": [json.dumps(v, default=str) if isinstance(v, (dict, list, tuple)) else v for _, v in fields],
        })
        worksheet = write_frame(frame, "Metadata", first_col_width=24)
        worksheet.set_column(1, 1, 90)

    print(f"  Exported experiment data to: {Path(output_dir).name}/{name}/{name}.xlsx")
    return output_path
