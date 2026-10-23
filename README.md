# DePalencify

One-click processing of Espana Scientific Software (Palencia / Tarragona / Gerona)
`.paf` files. Double-click `run.bat` (Windows) or `run.command` / `run.sh`
(Mac / Linux). The program reads every `.paf` in a folder directly, asks its
questions in the terminal, plots each experiment, and exports an Excel workbook
per experiment.

## What it asks, in order

1. Files, results folder
2. Settling time to ignore, trimming at start and end
3. Analysis: haem decomposition (fit), OD scaling, event averaging
4. What to plot, event-label angle, optional side-by-side comparison of two runs
5. **Special figures** (new): time response, then haem and OCR response
6. Figure size (journal, width, height)
7. Settings of the special figures (only if you chose them)
8. Data export, then OD / volume / dilution and event labels for each file

## Special figures

Both run from the `.paf` files through the same reader as everything else; no
exported binary or text files are needed. Both need a haem fit in `fits/`, so
choosing either one switches the decomposition on.

### Time response
File names need a group word and the hours: `control_7hours`,
`knockdown_24hours`. Spectra are averaged in the event windows, the last two
windows are subtracted (penultimate minus final), and that difference spectrum is
decomposed into haems. Output: `publication_figure/time_response_figure.*`,
`<group>_difference_spectra.csv`, `<group>_haem_percentages.csv`.

### Haem and OCR response
File names need strain, addition order and run: `knockdown_kcn_then_bd_run1`,
`control_bd_then_kcn_run2`. Runs of one condition are combined (mean, SEM,
Student t-tests with Holm correction). Output in `publication_figure/`:
`publication_figure.*` (baseline OCR bars, OCR response, haem response),
`exemplar_figure.*` (one run of each of the four conditions) and
`triplicate_summary.xlsx`.

Files whose names do not fit are listed and left out of that figure only.

## Files

- `DePalencify.py` main program; `config.py` defaults and colours
- `utils_shared/` reading, processing, plotting and export of single experiments
- `utils_custom/` the special figures
- `fits/` haem fit CSVs (your own fit goes here)
- `FUNCTION_LIST.md`, `DATA_FORMAT.md`, `CODING_STYLE.md` project documentation

## Requirements

Python 3.9 or newer with numpy, pandas, scipy, matplotlib and openpyxl. The
launchers install what is missing.
