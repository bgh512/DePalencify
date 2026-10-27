# DePalencify

One-click processing of Espana Scientific Software (Palencia / Tarragona / Gerona)
`.paf` files. Double-click `run.bat` (Windows) or `run.command` / `run.sh`
(Mac / Linux). The program reads every `.paf` in a folder directly, asks its
questions in the terminal, plots each experiment, and exports an Excel workbook
per experiment.

## What it asks, in order

Questions are numbered, shown in colour, and the answer is typed on the line below
(Enter accepts the [default]). Follow-up questions are indented and numbered one level
deeper (3.1 then 3.1.1).

1. **Your files**: the .paf folder, the results folder
2. **Trimming and ignoring**: TRIM (data that is not imported, plotted or used) and
   IGNORE (data that is plotted but not used for calculations), each for the start and
   the end. Ignore times count from the new 0 after trimming. The values are
   remembered per file for the next run.
3. **Analysis**: decompose the haems (which fit), scale by OD (OD, volume and dilution
   factor per file), average around the events (window, gap), change event labels.
   Write `ignore` as an event's label to ignore an event that was not an addition.
4. **Individual experiment plots**: oxygen, OCR, haems, event-label angle, journal and size
5. **Multi-experiment plots**: two experiments side by side, four experiments in a 2x2 grid
6. **Experiment summaries**: time response, haem and OCR response
7. **Data export**, then a summary and the start question

Every figure asks for its own journal. Answering `None` uses Nature with the default
size: individual 1 column x 0.5 page, side by side and 2x2 1.5 columns x 0.7 page, time
response and haem and OCR response 2 columns x 0.75 page.

## Special figures

Both run from the `.paf` files through the same reader as everything else; no
exported binary or text files are needed. Both need a haem fit in `fits/`, so
choosing either one switches the decomposition on.

### Time response
File names need a group word and the hours: `control_7hours`,
`knockdown_24hours`. Spectra are averaged in the event windows, the last two
windows are subtracted (penultimate minus final), and that difference spectrum is
decomposed into haems. Output: `time_response_figure.*` in the results folder and
`<group>_difference_spectra.csv`, `<group>_haem_percentages.csv` in `triplicate_data/`.

### Haem and OCR response
File names need strain, addition order and run: `knockdown_kcn_then_bd_run1`,
`control_bd_then_kcn_run2`. Runs of one condition are combined (mean, SEM,
Student t-tests with Holm correction). Output: `publication_figure.*` (baseline OCR
bars, OCR response, haem response) in the results folder, and
`triplicate_summary.xlsx` and the t-test table in `triplicate_data/`. The averaging windows are those of section 3.

### Four experiments in a 2x2 grid (section 5)
One run of each strain and addition order, drawn like the individual figures:
`2x2_comparison.*` in the results folder.

Files whose names do not fit are listed and left out of that figure only.

## Files

- `DePalencify.py` main program; `config.py` defaults and colours
- `utils_shared/` reading, processing, plotting and export of single experiments
- `utils_custom/` the special figures
- `fits/` haem fit CSVs (your own fit goes here)
- `FUNCTION_LIST.md`, `DATA_FORMAT.md`, `CODING_STYLE.md` project documentation

## Installation

Download the program from GitHub (needs [git](https://git-scm.com/) and Python 3.9 or newer):

```
git clone https://github.com/bgh512/DePalencify.git
cd DePalencify
git checkout dev
```

Without git, use the green **Code > Download ZIP** button on
https://github.com/bgh512/DePalencify and unzip it. To update later, run
`git pull` inside the folder (the launchers also check for updates).

## Requirements

Python 3.9 or newer with numpy, pandas, scipy, matplotlib and openpyxl. The
launchers install what is missing; to install by hand run
`pip install numpy pandas scipy matplotlib openpyxl`.

## Running

- Windows: double-click `run.bat`
- Mac: double-click `run.command`
- Linux / Mac terminal: `./run.sh`

Or directly: `python DePalencify.py`. Answer the numbered questions; Enter accepts
the [default].

## Outputs

In the results folder you chose, one sub-folder per run holds, for every `.paf` file:

- one figure per experiment (`.svg` and `.png`, sized for the chosen journal)
- one Excel workbook per experiment (CcO2, CsO2, VoO2, events and metadata sheets;
  optionally everything and the spectra)
- the comparison, time-response and haem/OCR figures if you asked for them
- a log file of the run

The OD, volume, dilution factor and event labels you type are saved in each
workbook and offered again next time.
