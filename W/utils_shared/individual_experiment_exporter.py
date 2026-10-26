# -*- coding: utf-8 -*-
"""
Export one processed experiment to an Excel workbook (optionally with spectral CSV
files), and read the saved settings back.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import json
from pathlib import Path
from typing import Any, List, Optional

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pandas as pd

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.helpers import excel_sheet_namer, file_name_sanitiser
from utils_shared.schema import DELTA_HAEM_SOURCES


# ---- CONSTANTS -----------------------------------------------------------------------
# Sheets written when the whole data set is exported (the short export holds only the
# first three).
BASIC_SHEETS = ('CcO2', 'CsO2', 'VoO2')
# Sheets are written in this order; any that are absent from the experiment are skipped.
# (experiment dictionary key, worksheet name)
DATA_SHEETS = (('CcO2', 'CcO2'),
               ('CsO2', 'CsO2'),
               ('VoO2', 'VoO2'),
               ('VoO2_OD', 'VoO2_OD'),
               ('VoO2_percent', 'VoO2_percent'),
               ('haem_conc', 'haem_conc'),
               ('haem_abs', 'haem_abs'),
               ('haem_delta_abs', 'haem_delta_abs'),
               ('haem_OD', 'haem_OD'),
               ('haem_abs_OD', 'haem_abs_OD'),
               ('haem_delta_abs_OD', 'haem_delta_abs_OD'),
               ('haem_percent', 'haem_percent'),
               )
# Spectral arrays exported to CSV (they are far too large for worksheets).
SPECTRAL_CSV_TYPES = (('transmission', 'transmiss'),
                      ('intensity', 'intensity'),
                      ('attenuation', 'attenuation'),
                      )

# What the user typed for an experiment (OD, volume, dilution factor, event labels and
# concentrations) is kept in the workbook, on the
# "Metadata" and "Events" sheets, and read back on the next run so it does not have to
# be typed again.
SETTINGS_KEYS = ('OD', 'volume', 'dilution_factor')


# ---- INDIVIDUAL EXPERIMENT EXPORTER HELPERS ------------------------------------------


# ---- _SPECTRAL CSV EXPORTER ----------------------------------------------------------
def _spectral_csv_exporter(experiment: dict, folder: Path) -> List[dict]:
    """
    ---- Summary ----
    Helper function to write one CSV per spectral dataset and data type, with
    wavelengths down and one column per spectrum.

    ---- Inputs ----
    experiment : dict
        Experiment dictionary, as defined in DATA_FORMAT.md.
    folder : Path
        Existing folder the CSV files are written to.

    ---- Globals read ----
    SPECTRAL_CSV_TYPES (module constant).

    ---- Outputs ----
    List[dict]
        One record per CSV file: Dataset, Data type, CSV file, Wavelengths, Timepoints.
        Raises ValueError when a spectrum length does not match the wavelengths.

    ---- Globals mutated ----
    None. Writes CSV files into ``folder`` (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 Set up --------------------------------------------------------------------
    name = experiment.get('experiment_name', 'experiment')
    records = []

    # ---- 2 Write every dataset -------------------------------------------------------
    for dataset_name, dataset in experiment.get('raw_spectra', {}).items():
        wavelengths = np.asarray(dataset['wavelengths'])
        times = np.asarray(dataset['time'], dtype=float)
        indices = np.asarray(dataset['spectrum_indices'])
        for data_key, file_suffix in SPECTRAL_CSV_TYPES:
            if dataset.get(data_key) is None:
                continue
            spectra = np.asarray(dataset[data_key], dtype=float)
            if spectra.ndim != 2:
                continue
            if spectra.shape[1] != len(wavelengths):
                raise ValueError(f'{name}/{dataset_name}: {data_key} does not match '
                                 f'the number of wavelengths.',
                                 )
            # Label each spectrum by its time; fall back to its index if times are
            # unavailable.
            labels = [f'{t:g} min' if np.isfinite(t) else f'Spectrum {i}'
                      for t, i in zip(times, indices)
                      ]
            frame = pd.DataFrame(spectra.T, columns=labels)
            frame.insert(0, 'Wavelength (nm)', wavelengths)
            csv_name = f'{dataset_name}_{file_suffix}.csv'
            frame.to_csv(folder / csv_name, index=False)
            records.append({'Dataset': dataset_name,
                            'Data type': data_key,
                            'CSV file': csv_name,
                            'Wavelengths': len(wavelengths),
                            'Timepoints': spectra.shape[0],
                            },
                           )
    return records


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- AVERAGES TABLE BUILDER ----------------------------------------------------------
def averages_table_builder(averages: dict) -> pd.DataFrame:
    """
    ---- Summary ----
    Main function to build the Averages worksheet table: one row per window with the
    mean, SD and change from baseline of VoO2 and of each haem.

    ---- Inputs ----
    averages : dict
        Event-window averages, as added to the experiment by
        calculate_experiment_averages (DATA_FORMAT.md); uses averages['windows'].

    ---- Globals read ----
    None.

    ---- Outputs ----
    pd.DataFrame
        Columns Average, Start time (min), End time (min), then mean, SD and change from
        baseline (%) for VoO2 and each haem.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Change from baseline = window mean as a percentage of the average0 mean (calculated
    in the averaging step).

    ---- Helpers ----
    _name_lister
    """

    # ---- 1 Get the measurement names -------------------------------------------------
    windows = averages['windows']
    def _name_lister(kind: str) -> List[str]:
        """
        ---- Summary ----
        Helper function to list the measurement names of one kind (vo2 or haem) over all
        windows, in first-seen order.

        ---- Inputs ----
        kind : str
            'vo2' or 'haem'.

        ---- Globals read ----
        None.

        ---- Outputs ----
        List[str]
            Unique measurement names.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        return list(dict.fromkeys(m for w in windows.values() for m in w[kind]))
    vo2_names, haem_names = _name_lister('vo2'), _name_lister('haem')

    # ---- 2 Define the column groups --------------------------------------------------
    groups = [('vo2', m, 'VoO2' if len(vo2_names) == 1 else f'VoO2 ({m})')
              for m in vo2_names
              ]
    groups += [('haem', m, str(m)) for m in haem_names]

    # ---- 3 Build the rows ------------------------------------------------------------
    rows = []
    for window_name, window in windows.items():
        row = {'Average': window_name,
               'Start time (min)': window['start_time'],
               'End time (min)': window['end_time'],
               }
        for kind, measurement, label in groups:
            stats = window[kind].get(measurement, {})
            row[f'{label} mean'] = stats.get('mean', np.nan)
            row[f'{label} SD'] = stats.get('sd', np.nan)
            row[f'{label} change from baseline (%)'] = stats.get('change', np.nan)
        rows.append(row)
    return pd.DataFrame(rows)


# ---- EXPERIMENT WORKBOOK EXPORTER ----------------------------------------------------
def experiment_workbook_exporter(experiment: dict,
                                 output_dir: Path,
                                 full: bool = False,
                                 spectra: bool = False,
                                 ) -> Path:
    """
    ---- Summary ----
    Main function to export one experiment to <output_dir>/<name>/<name>.xlsx, with the
    CcO2, CsO2 and VoO2 sheets, Averages, Events and Metadata, and optionally every
    processed table and the spectral CSV files.

    ---- Inputs ----
    experiment : dict
        Experiment dictionary, as defined in DATA_FORMAT.md.
    output_dir : Path
        Results folder.
    full : bool
        True adds every processed table in the order of DATA_SHEETS.
    spectra : bool
        True also writes the spectral CSV files next to the workbook (large and slow)
        and an index sheet linking to them.

    ---- Globals read ----
    BASIC_SHEETS, DATA_SHEETS and schema.DELTA_HAEM_SOURCES.

    ---- Outputs ----
    Path
        Path of the workbook.

    ---- Globals mutated ----
    None. Creates the folder, the workbook and optional CSV files (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _frame_writer
    _spectral_csv_exporter
    averages_table_builder
    excel_sheet_namer
    file_name_sanitiser
    """

    # ---- 1 Set up the output paths ---------------------------------------------------
    name = file_name_sanitiser(experiment.get('experiment_name', 'experiment'))
    folder = Path(output_dir) / name
    folder.mkdir(parents=True, exist_ok=True)
    output_path = folder / f'{name}.xlsx'
    spectral_records = _spectral_csv_exporter(experiment, folder) if spectra else []

    # ---- 2 Write the workbook --------------------------------------------------------
    used_sheets = set()
    sheet_keys = DATA_SHEETS if full else tuple((k, k) for k in BASIC_SHEETS)
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        workbook = writer.book
        header_format = workbook.add_format({'bold': True,
                                             'bg_color': '#D9EAD3',
                                             'border': 1,
                                             'text_wrap': True,
                                             },
                                            )
        link_format = workbook.add_format({'font_color': 'blue', 'underline': 1})
        def _frame_writer(frame: pd.DataFrame,
                          sheet_title: str,
                          first_col_width: float = 18,
                          ) -> Any:
            """
            ---- Summary ----
            Helper function to write a DataFrame as a formatted worksheet.

            ---- Inputs ----
            frame : pd.DataFrame
                Data to write.
            sheet_title : str
                Wanted sheet name; made unique and valid for Excel.
            first_col_width : float
                Width of the first column.

            ---- Globals read ----
            None.

            ---- Outputs ----
            Any
                The xlsxwriter worksheet.

            ---- Globals mutated ----
            None. Adds a sheet to the open workbook and records its name (side effect).

            ---- Equations ----
            None.

            ---- Helpers ----
            excel_sheet_namer
            """

            sheet = excel_sheet_namer(sheet_title, used_sheets)
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
            worksheet = _frame_writer(pd.DataFrame(spectral_records),
                                      'Spectral data',
                                      first_col_width=14,
                                      )
            for row, record in enumerate(spectral_records, start=1):
                worksheet.write_url(row,
                                    2,
                                    f"external:{record['CSV file']}",
                                    link_format,
                                    string=record['CSV file'],
                                    )
            worksheet.set_column(2, 2, 28)
        # 2. Time-resolved datasets.
        for key, sheet_title in sheet_keys:
            frame = experiment.get(key)
            if isinstance(frame, pd.DataFrame) and not frame.empty:
                _frame_writer(frame, sheet_title)
        # 3. Event-window averages.
        averages = experiment.get('averages')
        if averages and averages.get('windows'):
            table = averages_table_builder(averages)
            worksheet = _frame_writer(table, 'Averages', first_col_width=14)
            settings = averages['settings']
            used = [f'{label} source: {key}'
                    for label, key in (('VoO2', settings.get('vo2_key')),
                                       ('haem', settings.get('haem_key')),
                                       )
                    if key
                    ]
            notes = ['; '.join(used) + '.',
                     f"Windows are {settings['window_minutes']:g} min long, ending "
                     f"{settings['gap_minutes']:g} min "
                     f'before each addition and '
                     f"{settings['final_window_gap_minutes']:g} min before the end of "
                     f'the recording.',
                     'Change from baseline = window mean as a percentage of the '
                     'average0 mean (average0 = 100 %).',
                     ]
            if settings.get('haem_source') in DELTA_HAEM_SOURCES:
                notes.append('Haem change from baseline (%) is not calculated for '
                             'delta abs sources (they start at 0).',
                             )
            for offset, note in enumerate(notes, start=2):
                worksheet.write(len(table) + offset, 0, note)
        metadata = (experiment.get('metadata')
                    if isinstance(experiment.get('metadata'), dict)
                    else {}
                    )
        # 4. Events, with the label and concentration the user entered.
        all_events = (list(metadata.get('events', [])) +
                      list(metadata.get('ignored_events', [])))
        events = (sorted(all_events,
                         key=lambda e: e.get('time',
                                             ) if e.get('time') is not None else 0,
                         )
                  )
        if True:  # always written, so the sheet exists even for a file with no events
            _frame_writer(pd.DataFrame({'event': [f'Event {i}'
                                                  for i in range(1, len(events) + 1)
                                                  ],
                                        'datapoint': [e.get('datapoint') for e in events
                                                      ],
                                        'time_min': [e.get('time') for e in events],
                                        'paf_text': [e.get('text', '') for e in events],
                                        'label': [e.get('label', '') for e in events],
                                        'concentration_uM': [e.get('concentration_uM')
                                                             for e in events
                                                             ],
                                        'ignored': [bool(e.get('ignored', False))
                                                    for e in events
                                                    ],
                                        },
                                       ),
                          'Events',
                          first_col_width=12,
                          )
        # 5. Metadata (OD, volume, dilution factor, settings used, notes, acquisition
        # details).
        fields = [(k, v)
                  for k, v in metadata.items()
                  if k not in ('events', 'ignored_events', 'binary_metadata')
                  ]
        frame = pd.DataFrame({'Field': [k for k, _ in fields],
                              'Value': [json.dumps(v, default=str)
                                        if isinstance(v, (dict, list, tuple))
                                        else v
                                        for _, v in fields
                                        ],
                              },
                             )
        worksheet = _frame_writer(frame, 'Metadata', first_col_width=24)
        worksheet.set_column(1, 1, 90)

    # ---- 3 Report the export ---------------------------------------------------------
    print(f'  Exported experiment data to: {Path(output_dir).name}/{name}/{name}.xlsx')
    return output_path


# ---- SAVED SETTINGS READER -----------------------------------------------------------
def saved_settings_reader(output_dir: Path, experiment_name: str) -> Optional[dict]:
    """
    ---- Summary ----
    Main function to read the OD, volume, dilution factor and events saved in the
    workbook of an earlier export.

    ---- Inputs ----
    output_dir : Path
        Results folder.
    experiment_name : str
        Experiment name (file name without the extension).

    ---- Globals read ----
    SETTINGS_KEYS (module constant).

    ---- Outputs ----
    Optional[dict]
        {'OD', 'volume', 'dilution_factor', 'events': [{'datapoint', 'label',
        'concentration_uM', 'ignored'}]}, or None when there is no readable workbook or
        nothing was saved.

    ---- Globals mutated ----
    None. Reads the workbook from disk.

    ---- Equations ----
    None.

    ---- Helpers ----
    workbook_path_builder
    """

    # ---- 1 Find the workbook ---------------------------------------------------------
    path = workbook_path_builder(output_dir, experiment_name)
    if not path.is_file():
        return None

    # ---- 2 Read the sheets -----------------------------------------------------------
    try:
        # every sheet; older workbooks may lack "Events"
        sheets = pd.read_excel(path, sheet_name=None)
    except Exception:  # a file open in Excel, a damaged file: just ask again
        return None
    if 'Metadata' not in sheets:
        return None

    # ---- 3 Read the metadata ---------------------------------------------------------
    saved = {}
    metadata = sheets['Metadata']
    for field, value in zip(metadata['Field'], metadata['Value']):
        if field in SETTINGS_KEYS and pd.notna(value):
            try:
                saved[field] = float(value)
            except (TypeError, ValueError):
                pass

    # ---- 4 Read the events -----------------------------------------------------------
    events = []
    for _, row in sheets.get('Events', pd.DataFrame()).iterrows():
        concentration = row.get('concentration_uM')
        events.append({'datapoint': int(row['datapoint']),
                       'label': '' if pd.isna(row.get('label')) else str(row['label']),
                       'concentration_uM': None
                       if pd.isna(concentration)
                       else float(concentration),
                       'ignored': bool(row.get('ignored', False))
                       if pd.notna(row.get('ignored', False))
                       else False,
                       },
                      )
    saved['events'] = events
    return saved if any(k in saved for k in SETTINGS_KEYS) or events else None


# ---- WORKBOOK PATH BUILDER -----------------------------------------------------------
def workbook_path_builder(output_dir: Path, experiment_name: str) -> Path:
    """
    ---- Summary ----
    Main function to build the path of the workbook of an experiment.

    ---- Inputs ----
    output_dir : Path
        Results folder.
    experiment_name : str
        Experiment name; made safe for file names.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Path
        <output_dir>/<name>/<name>.xlsx.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    file_name_sanitiser
    """

    name = file_name_sanitiser(experiment_name)
    return Path(output_dir) / name / f'{name}.xlsx'
