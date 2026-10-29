# DePalencify - Data Format

## 1. Structures

### 1.1 Dictionaries

#### `experiment`

One experiment (one `.paf` file) as passed between the processing functions. Created by `experiment_paf_loader` and extended by the processing steps. Keys marked optional exist only when the matching analysis was switched on.

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'experiment_name'` | str | | | File stem of the `.paf` file |
| `'metadata'` | dict | | | `'OD'`, `'volume'`, `'dilution_factor'`, `'events'`, `'ignored_events'` and acquisition details |
| `'CcO2'` | pd.DataFrame | (n_points, 2) | uM | Measured O2: `Time (min)` and the measurement column |
| `'CsO2'` | pd.DataFrame | (n_points, 2) | uM | Set O2 |
| `'VoO2'` | pd.DataFrame | (n_points, 2) | uM/min | Oxygen consumption rate (OCR) |
| `'VoO2_OD'` | pd.DataFrame | (n_points, 2) | | Optional. OCR divided by dilution factor x OD x volume |
| `'VoO2_percent'` | pd.DataFrame | (n_points, 2) | % | Optional. OCR scaled to 0-100 % of its range |
| `'haem_conc'` | pd.DataFrame | (n_spectra, 2 + n_haems) | | Optional. Fitted haem concentrations; columns `Time (min)`, `spectrum_index` and one per haem |
| `'haem_abs'` | pd.DataFrame | (n_spectra, 2 + n_haems) | mOD | Optional. Haem concentration x peak of the fit spectrum |
| `'haem_delta_abs'` | pd.DataFrame | (n_spectra, 2 + n_haems) | mOD | Optional. `haem_abs` shifted so the mean of the baseline window is 0 |
| `'haem_OD'`, `'haem_abs_OD'`, `'haem_delta_abs_OD'` | pd.DataFrame | (n_spectra, 2 + n_haems) | | Optional. The matching tables divided by dilution factor x OD x volume |
| `'haem_percent'` | pd.DataFrame | (n_spectra, 2 + n_haems) | % | Optional. `haem_conc` scaled to 0-100 % |
| `'raw_spectra'` | dict | | | `{dataset: {'wavelengths', 'spectrum_indices', 'time', 'transmission', 'intensity', 'attenuation'}}`; dropped after the special figures are prepared |
| `'averages'` | dict | | | Event-window statistics (see `averages`) |

Example:

```python
experiment = {'experiment_name': 'control_7hours',
              'metadata': metadata,
              'VoO2': vo2_table,
              'averages': averages,
              }
```

#### `experiment_summary`

Quick description of one `.paf` file, read before the questions are asked. Created by `experiment_summary_reader`.

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'name'` | str | | | File stem |
| `'duration_min'` | float | | min | Length of the recording |
| `'frames'` | int | | | Number of time points |
| `'datasets'` | List[str] | | | Spectral datasets in the file |
| `'events'` | List[dict] | | | Events, each with `'time'` in minutes |
| `'traces'` | List[str] | | | Names of the recorded traces |

#### `averages`

Event-window statistics of one experiment. Created by `experiment_averages_calculator`, stored as `experiment['averages']`.

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'settings'` | dict | | | `window_minutes`, `gap_minutes`, `final_window_gap_minutes`, `vo2_source`, `vo2_key`, `haem_source`, `haem_key` |
| `'windows'` | dict | | | `{window name: window record}`; `average0` is the baseline window, then `average1` ... one per event |

Window record:

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'start_time'` | float | | min | Start of the window |
| `'end_time'` | float | | min | End of the window |
| `'vo2'` | dict | | | `{measurement: statistics}` for the OCR |
| `'haem'` | dict | | | `{haem name: statistics}` |

Statistics of one measurement in one window:

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'mean'` | float | | as the source | Mean over the window |
| `'sd'` | float | | as the source | Sample standard deviation (n - 1) over the window |
| `'delta'` | float | | as the source | Mean minus the mean of `average0` |
| `'change'` | float | | % | Mean as a percentage of the mean of `average0` (NaN for delta sources or a zero baseline) |

#### `triplicate`

One condition (strain and addition order, e.g. `knockdown_kcn_then_bd`) with its runs combined. Created by `triplicate_averager`, returned as `{condition: triplicate}`.

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'runs'` | dict | | | `{run number: experiment name}` |
| `'run_numbers'` | List[int] | (n_runs,) | | Run numbers in order |
| `'windows'` | List[str] | | | Window names in order |
| `'window_times'` | dict | | min | `{window name: (start, end)}` taken from the first run holding the window |
| `'settings'` | dict | | | Copy of the `settings` of the runs' `averages` |
| `'vo2'` | dict | | | `{measurement: {window name: run statistics}}` |
| `'haem'` | dict | | | `{haem name: {window name: run statistics}}` |

Run statistics of one measurement in one window. The `run_*` values are the per-run window values; the rest are calculated over the runs.

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'run_means'` | dict | | as the source | `{run number: window mean}` |
| `'run_sds'` | dict | | as the source | `{run number: window SD}` |
| `'run_changes'` | dict | | % | `{run number: change from baseline}` |
| `'run_deltas'` | dict | | as the source | `{run number: delta from baseline}` |
| `'mean'`, `'sd'`, `'sem'`, `'n'` | float, float, float, int | | as the source | Mean, sample SD, SEM (SD / sqrt(n)) and count of the run means |
| `'change_mean'`, `'change_sd'`, `'change_sem'`, `'change_n'` | float, float, float, int | | % | The same for the run changes |
| `'delta_mean'`, `'delta_sd'`, `'delta_sem'`, `'delta_n'` | float, float, float, int | | as the source | The same for the run deltas |

#### `test_record`

One significance test drawn on the OCR and haem response figure. Appended to a list by the plotter and written to `ocr_and_haem_response.xlsx`.

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'panel'` | str | | | Panel name, e.g. `haem response bd then kcn` |
| `'measurement'` | str | | | OCR or haem name |
| `'metric'` | str | | | Compared statistic (`mean`, `change` or `delta`) |
| `'window'` | str | | | Window name |
| `'group_a'`, `'group_b'` | str | | | The two groups compared |
| `'values_a'`, `'values_b'` | dict | | as the metric | `{run number: value}` of each group (finite values only) |
| `'t'` | float | | | Student t statistic (equal variances) |
| `'p'` | float | | | Two-sided p value |
| `'p_adjusted'` | float | | | p value after the correction across the windows of the panel |
| `'correction'` | str | | | `holm` or `none` |
| `'alpha'` | float | | | Significance level |
| `'significant'` | bool | | | `p_adjusted < alpha` |
| `'mark'` | str | | | `*`, `**`, `***` or empty |

#### `difference_spectrum` and `difference_decomposition`

Added to each experiment of the time response figure by `utils_custom`.

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'group'` | str | | | Group word of the file name, e.g. `knockdown` |
| `'spectral_averages'` | dict | | | `{window name: {'time_range', 'wavelengths', 'attenuation'}}` |
| `'difference_spectrum'` | dict | | | `'wavelengths'` (n_wavelengths,), `'spectrum'` (n_wavelengths,), `'minuend'`, `'subtrahend'` (window names; the spectrum is minuend minus subtrahend) |
| `'difference_decomposition'` | dict | | | `'haem_names'` (n_haems), `'coefficients'` (n_haems), `'haem_percentages'` (n_haems, %), `'percent_basis'` (signed or absolute), `'filtered_data'`, `'scatter'`, `'no_scatter'`, `'haem_total'` (each n_wavelengths) and `'haem_individual'` (n_haems arrays of n_wavelengths) |

#### `last_answers`

Saved to `last_answers.json` next to `main.py` and offered as the defaults on the next run.

| Key | Type | Shape | Units | Description |
|---|---|---|---|---|
| `'data_folder'` | str | | | Folder of the `.paf` files |
| `'export_folder'` | str | | | Results folder |
| `'answers'` | dict | | | Terminal answers |
| `'files'` | dict | | min | `{file name: {'trim_start', 'trim_end', 'ignore_start', 'ignore_end'}}`; trim times are on the original recording, ignore times count from the new 0 after trimming |

### 1.2 Dataclasses

#### `Spectra`

Defined in `utils_shared/paf_reader.py`. Created by `spectra_parser`, used by `record_scanner` and `PafFile`.

| Field | Type | Shape | Units | Default | Description |
|---|---|---|---|---|---|
| `offset` | int | | bytes | `0` | Position of the record in the file |
| `name` | str | | | `''` | Spectrometer name |
| `nframes` | int | | | `0` | Number of spectra |
| `npix` | int | | | `0` | Number of pixels (wavelengths) |
| `wl_off` | Optional[int] | | bytes | `None` | Position of the wavelength axis |
| `wavelengths` | Optional[np.ndarray] | (npix,) | nm | `None` | Wavelength of each pixel |
| `data_off` | int | | bytes | `0` | Position of the spectra block |
| `data_end` | int | | bytes | `0` | End of the spectra block |
| `log` | Optional[np.ndarray] | (nframes + 2, npix) | | `None` | Raw rows: dark row, reference row, then one row per spectrum |
| `rec_end` | int | | bytes | `0` | End of the record |
| `ref` | Optional[np.ndarray] | (npix,) | | `None` | Reference spectrum |
| `params` | dict | | | `{}` | Acquisition parameters found in the record |
| `trailer` | list | | | `[]` | Text tokens after the data block |
| `checks` | dict | | | `{}` | Warnings raised while parsing |

### 1.3 Arrays

#### `spectra`

Attenuation (or transmission, or intensity) of one spectral dataset.

| Axis | Name | Length | Description |
|---|---|---|---|
| 0 | spectrum | `n_spectra` | One row per spectrum, in time order |
| 1 | wavelength | `n_wavelengths` | One column per wavelength |

- **dtype:** float64
- **Units of the values:** OD for attenuation, fraction for transmission, counts for intensity

### 1.4 Files

#### `individual experiment workbook`

| Property | Value |
|---|---|
| File type | xlsx |
| Sheets | `CcO2`, `CsO2`, `VoO2` and, for the full export, `VoO2_OD`, `VoO2_percent`, `haem_conc`, `haem_abs`, `haem_delta_abs`, `haem_OD`, `haem_abs_OD`, `haem_delta_abs_OD`, `haem_percent`; plus `Averages`, `Events` and `Metadata` when available |
| Location and name | `<results>/<run folder>/<experiment>/<experiment>.xlsx` |

| Column (data sheets) | Type | Units | Description |
|---|---|---|---|
| `Time (min)` | float | min | Time of the point |
| `spectrum_index` | int | | Spectrum number (haem sheets only) |
| measurement columns | float | see `experiment` | One per trace or haem |

The `Averages` sheet has one row per window: `Average`, `Start time (min)`, `End time (min)` and, per measurement, `<name> mean`, `<name> SD` and `<name> change from baseline (%)`.

#### `spectral csv`

| Property | Value |
|---|---|
| File type | CSV |
| Delimiter | comma |
| Encoding | UTF-8 |
| Location and name | `<results>/<run folder>/<experiment>/<dataset>_<type>.csv`, type `transmiss`, `intensity` or `attenuation` |

| Column | Type | Units | Description |
|---|---|---|---|
| `Wavelength (nm)` | float | nm | Wavelength |
| `<time> min` | float | see the type | One column per spectrum |

#### `ocr_and_haem_response.xlsx`

| Property | Value |
|---|---|
| File type | xlsx (live formulas with stored values) |
| Sheets | `Notes`, `Baseline OCR`, one sheet per condition, `Tests` |
| Location and name | `<results>/ocr_and_haem_response.xlsx` |

- **Notes:** how to read the workbook and the formulas used.
- **Baseline OCR:** the baseline OCR of every run (`Run`, `Experiment`, `Baseline OCR`), then `N`, `Mean`, `SD`, `SEM` per group and the baseline t-test.
- **One sheet per condition:** for each measurement, a table with one row per window and one column per run (the run means), then `N`, `Mean`, `SD`, `SEM`; the same for the change from baseline. The window times are not repeated per run.
- **Tests:** one row per test record: group A and B run values, means, variances, pooled variance, `t`, degrees of freedom, `p`, Holm rank, multiplier and adjusted `p`, `alpha` and the mark, so each result can be checked independently.

| Column (Tests) | Type | Units | Description |
|---|---|---|---|
| panel, measurement, metric, window | str | | Which comparison the row is |
| group A / B values, n, mean, variance | float | as the metric | Inputs of the test |
| `t`, `df`, `p` | float | | Student t-test, equal variances, two-sided |
| rank, multiplier, `p adjusted` | float | | Holm correction across the windows of the panel |
| `alpha`, `significant`, mark | | | Result |

#### `time_response.xlsx`

| Property | Value |
|---|---|
| File type | xlsx (live formulas with stored values) |
| Sheets | `Notes`, `Figure panels`, `Difference spectra`, `Haem percentages`, `Waterfall` (when a shared baseline is used) |
| Location and name | `<results>/time_response.xlsx` |

- **Figure panels:** `Panel`, `Group`, `Time point`, `Experiment` for every experiment drawn.
- **Difference spectra:** per experiment, the minuend and subtrahend window averages by wavelength and their difference.
- **Haem percentages:** per experiment, the fitted haem coefficients and the percentages calculated from them.
- **Waterfall:** the difference spectra with the shared baseline fit (`INTERCEPT` and `SLOPE` formulas) and the corrected spectra.

#### `last_answers.json`

| Property | Value |
|---|---|
| File type | JSON |
| Encoding | UTF-8 |
| Location and name | `last_answers.json` next to `main.py` (not committed) |

Structure: see `last_answers` in section 1.1.

#### `log file`

| Property | Value |
|---|---|
| File type | text |
| Encoding | UTF-8 |
| Location and name | `<results>/logs/YYYY_MM_DD-HH_MM_SS.log` |

The first lines are the project version, the random seed (none: the program uses no random numbers) and the settings of the run, then everything printed during the run.

#### Figure files

| Property | Value |
|---|---|
| File type | `.png` and `.svg` |
| Location and name | `<results>/<experiment>.*` per experiment, `<results>/2x2_comparison.*`, `<results>/ocr_and_haem_response.*`, `<results>/time_response.*` |

## 2. Conventions

Project-wide choices, written once. The tables above use these units and symbols.

### 2.1 Units

| Quantity | Unit | Name suffix |
|---|---|---|
| Time | min | `(min)` in column names, `_min` in keys |
| Wavelength | nm | none |
| Oxygen concentration | uM | none |
| Oxygen consumption rate | uM/min | none |
| Haem absorbance | mOD | none |
| Fractions of a range or baseline | % | none |

Terminal questions that ask for hours or minutes say which.

### 2.2 Dtypes

float64 for all arrays unless stated otherwise in the tables above. The wavelength axis is stored in the file as float32.

### 2.3 Axis order and shape symbols

| Data | Axis order |
|---|---|
| Time-resolved tables | One row per time point, `Time (min)` first |
| Spectral arrays | `(n_spectra, n_wavelengths)`: time first, then the spectral axis |

| Symbol | Meaning |
|---|---|
| `n_points` | Number of time points of a trace |
| `n_spectra` | Number of spectra (frames) |
| `n_wavelengths` | Number of wavelengths (pixels) |
| `n_haems` | Number of haems in the fit |
| `n_runs` | Number of runs of a condition |
