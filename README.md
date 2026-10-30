# DePalencify (V1.0)

Reads Espana Scientific Software `.paf` files, plots every experiment and the combined figures, and exports Excel workbooks that can be checked by hand.

## 1. Installation

### 1.1 Using GitHub (recommended)

Git and Python 3.9 or newer must be installed first. If they are not, follow the requirements in section 1.2, then return here.

#### Windows

1. Open a terminal: press the Windows key, type `PowerShell` and press Enter.
2. Go to the folder where the project should be installed:

    ```powershell
    cd C:\Users\<username>\Documents
    ```

3. Download the project and enter its folder:

    ```powershell
    git clone https://github.com/bgh512/DePalencify.git
    cd DePalencify
    ```

4. Create and activate a Python environment, then install the dependencies:

    ```powershell
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt
    ```

    If PowerShell refuses to run the activation script, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once and try again. The launcher `run.bat` does this step itself, so it can be skipped if only the launcher is used.

#### macOS

1. Open Terminal: press Cmd + Space, type `Terminal` and press Enter. If git is missing, run `xcode-select --install` first.
2. Go to the folder where the project should be installed:

    ```bash
    cd ~/Documents
    ```

3. Download the project and enter its folder:

    ```bash
    git clone https://github.com/bgh512/DePalencify.git
    cd DePalencify
    ```

4. Create and activate a Python environment, then install the dependencies:

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install -r requirements.txt
    ```

    The launchers `run.command` and `run.sh` do this step themselves, so it can be skipped if only a launcher is used.

#### Linux

1. Open a terminal (Ctrl + Alt + T on most distributions). On Debian or Ubuntu, install the requirements first:

    ```bash
    sudo apt install git python3 python3-venv python3-pip
    ```

2. Go to the folder where the project should be installed:

    ```bash
    cd ~/Documents
    ```

3. Download the project and enter its folder:

    ```bash
    git clone https://github.com/bgh512/DePalencify.git
    cd DePalencify
    ```

4. Create and activate a Python environment, then install the dependencies:

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install -r requirements.txt
    ```

### 1.2 Manual install

No git is needed.

#### Requirements

- Python 3.9 or newer: <https://www.python.org/downloads/> (on Windows, tick "Add python.exe to PATH" in the installer).

#### Install from the .zip

1. On the project's GitHub page, click **Code**, then **Download ZIP**.
2. Extract the .zip to the desired location.
3. Open a terminal in the extracted folder:
    - Windows: right-click inside the folder and choose **Open in Terminal**.
    - macOS: right-click the folder and choose **New Terminal at Folder**.
    - Linux: right-click inside the folder and choose **Open in Terminal**.
4. Create and activate a Python environment, then install the dependencies:

    Windows (PowerShell):

    ```powershell
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt
    ```

    macOS and Linux:

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install -r requirements.txt
    ```

### 1.3 Following the dev branch (optional)

The steps above install `main`, the stable version. `dev` has newer changes that are not yet fully tested.

- Installed with git: from inside the project folder run `git checkout dev`, then `git pull`. To go back to the stable version run `git checkout main`.
- Manual install: on the project's GitHub page choose `dev` in the branch drop-down, click **Code**, then **Download ZIP**, and install as in section 1.2.

## 2. Running

### 2.1 From the terminal

Activate the environment first (see section 1), then run:

```bash
python main.py
```

The program has no command-line options. It asks numbered questions in the terminal (Enter accepts the default in square brackets); the answers are remembered for the next run in `last_answers.json`.

### 2.2 Using the launcher

- Windows: double-click `run.bat`.
- macOS: double-click `run.command`.
- Linux: run `./run.sh`.

The launchers create their own environment on the first run, install what is missing, check GitHub for updates when the folder is a git clone, and start `main.py`.

### 2.3 The questions

1. **Your files:** the `.paf` folder, the results folder, and whether to use the experiment browser (see section 2.4).
2. **Experiment browser** (only with the browser on): look through the files in the plot window.
3. **Trimming and ignoring:** TRIM (data that is not imported, plotted or used) and IGNORE (data that is plotted but not used for calculations), each for the start and the end. Ignore times count from the new 0 after trimming.
4. **Analysis:** decompose the haems (which fit), scale by OD, average around the events (window, gap), change event labels. Write `ignore` as an event's label to ignore an event that was not an addition.
5. **Individual experiment plots:** oxygen, OCR, haems, event-label angle, journal and size.
6. **Multi-experiment plots:** two experiments side by side, four experiments in a 2x2 grid.
7. **Experiment summaries:** time response, OCR and haem response.
8. **Data export**, then a summary and the start question.

The numbers above are those with the experiment browser on; with it off, section 2 is left out and the later sections move up by one.

Every figure asks for its own journal. Answering `None` uses Nature with the default size.

### 2.4 The experiment browser

With the browser on (the default, question 1.3), the plot window shows the experiment you are asking about and is redrawn after each answer. The terminal is still the only place you type: the plot window is for looking, and it cannot be clicked to change anything. It does not respond to zooming or dragging while a question is waiting for an answer.

- **Experiment browser:** step through the files (next, previous, go to a file) and look at the set and measured O2, the OCR and the events.
- **Trimming and ignoring:** after the four questions, the whole recording is drawn with the TRIMMED part grey and hatched and the IGNORED part amber. Answer *Yes, accept*, *No, enter the limits again* (your answers are offered as the defaults) or *Look at another file in the plot window first*.
- **Analysis:** the decomposition, OD scaling, averaging windows and event labels are each drawn for the current file and accepted or asked again in the same way.
- **Individual experiment plots:** the figure is drawn at the journal size you chose, and can be accepted or changed.
- **Going back:** after the individual plots you can go back to any earlier step. Its questions are asked again with your answers as the defaults, and your answers to the later steps are kept.

The previews use the same processing as the final run, so what is shown is what is saved. Only one file is previewed at a time (use *Look at another file* to check others), and the multi-experiment figures (sections 6 and 7) are made after the questions, as before.

If no plot window can be opened (for example no display, or no GUI library such as tkinter or Qt), each preview is saved as a picture (`DePalencify_preview.png` in the temporary folder) and opened in the default picture viewer; the path is printed. Answer `n` to question 1.3 to use the questions without the browser.

### 2.5 Outputs

Everything goes into the results folder you chose:

| Output | Description |
|---|---|
| `<experiment>/<experiment>.xlsx` and figure files | One workbook and one figure per experiment |
| `2x2_comparison.*` | Four experiments in a 2x2 grid |
| `ocr_and_haem_response.*` | Baseline OCR bars, OCR response and haem response (`.png`, `.svg`) |
| `ocr_and_haem_response.xlsx` | Run values, averages, SEM and every significance test, written so the maths can be checked by hand |
| `time_response.*` | The 3 x 3 time response figure (`.png`, `.svg`) |
| `time_response.xlsx` | Difference spectra, haem percentages and the waterfall baseline, written so the maths can be checked by hand |
| `logs/YYYY_MM_DD-HH_MM_SS.log` | Everything printed during the run, with the version, seed and settings |

Both summary figures need a haem fit in `fits/`. File names must carry the information the figure needs: `knockdown_kcn_then_bd_run1` (strain, addition order, run) for the OCR and haem response, and `control_7hours` (group, hours) for the time response. Files whose names do not fit are listed and left out of that figure only.

## 3. Project structure

```
DePalencify/
    make_zip.bat            zips the project for sharing (Windows)
    main.py                 entry point
    config.py               defaults, journal sizes and colours
    run.bat, run.command, run.sh   launchers
    launchers/              desktop shortcut scripts
    assets/                 icons
    fits/                   haem fit CSVs (your own fit goes here)
    utils_shared/           reading, processing, plotting and export of single experiments
        __init__.py
        paf_reader.py       direct .paf reader
        experiment_processing.py   the processing steps shared by the run and the previews
        ...
    utils_viewer/           the experiment browser (plot window previews of each step)
        __init__.py
        viewer_window.py    the plot window (or the preview picture when there is no window)
        viewer_preview.py   processes and draws one file as a preview
        viewer_stages.py    the browser, trim, analysis and plot steps and going back
    utils_custom/           the multi-experiment figures and their workbooks
        __init__.py
        ocr_and_haem_response_plotter.py
        time_response_plotter.py
        ...
    requirements.txt        Python dependencies
    VERSION                 current version
    README.md
    FUNCTION_LIST.md
    DATA_FORMAT.md
    CLAUDE.md               imports the style guide for Claude
    style/                  shared style guide (git submodule, contains CODING_STYLE.md)
```

## 4. Links to other .md files

- [FUNCTION_LIST.md](FUNCTION_LIST.md): every function and class, with its docstring.
- [DATA_FORMAT.md](DATA_FORMAT.md): custom data structures, units and formats.
- [style/CODING_STYLE.md](style/CODING_STYLE.md): the coding and formatting standards used in this project.

## 5. License

No licence file has been added yet.
