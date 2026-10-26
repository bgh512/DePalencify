# -*- coding: utf-8 -*-
"""
Small, generic utilities shared by several modules (names, file names, Excel sheet
names).
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from pathlib import Path
import re
from typing import Any, List, Sequence, Tuple

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
from matplotlib.figure import Figure


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- CONCENTRATION FORMATTER ---------------------------------------------------------
def concentration_formatter(concentration_um: Any) -> str:
    """
    ---- Summary ----
    Main function to write a concentration given in micromolar with the most readable
    unit: M from 1 000 000 uM, mM from 1000 uM and uM below that.

    ---- Inputs ----
    concentration_um : Any
        Concentration in micromolar (uM); anything float() accepts.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        For example '2 uM', '2 mM' (from 2000 uM) or '1.5 mM'; the unit is written
        with the micro sign. Raises ValueError or TypeError if the value is not a
        number.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    mM = uM / 1000; M = uM / 1 000 000.

    ---- Helpers ----
    None.
    """

    # ---- 1 Choose the unit -----------------------------------------------------------
    value = float(concentration_um)
    if abs(value) >= 1_000_000:
        return f'{value / 1_000_000:g} M'
    if abs(value) >= 1000:
        return f'{value / 1000:g} mM'
    return f'{value:g} µM'


# ---- EXCEL SHEET NAMER ---------------------------------------------------------------
def excel_sheet_namer(name: Any, used: set) -> str:
    """
    ---- Summary ----
    Main function to make a valid, unique Excel sheet name (at most 31 characters, no
    special characters).

    ---- Inputs ----
    name : Any
        Proposed sheet name (converted with str).
    used : set
        Lower-cased sheet names already taken; the new name is added to it.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        Sheet name, with a numeric suffix when the name is already taken.

    ---- Globals mutated ----
    None. Adds the lower-cased result to ``used`` (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    base = re.sub(r'[\[\]:*?/\\]', '_', str(name)).strip("'") or 'Data'
    base = base[:31]
    candidate, counter = base, 2
    while candidate.lower() in used:
        suffix = f'_{counter}'
        candidate = base[:31 - len(suffix)] + suffix
        counter += 1
    used.add(candidate.lower())
    return candidate


# ---- FIGURE SAVER --------------------------------------------------------------------
def figure_saver(fig: Figure,
                 folder: Path,
                 stem: str,
                 formats: Sequence[str],
                 size: Tuple[float, float],
                 dpi: int,
                 tight: bool = False,
                 ) -> List[Path]:
    """
    ---- Summary ----
    Main function to save a figure in each requested format at exactly the requested
    size. The size is pinned again just before saving because interactive backends
    resize figures, and tight cropping is off unless requested.

    ---- Inputs ----
    fig : Figure
        Matplotlib figure to save.
    folder : Path
        Output folder; created if missing.
    stem : str
        File name without the extension.
    formats : Sequence[str]
        File extensions, for example ("svg", "png").
    size : Tuple[float, float]
        Width and height in inches.
    dpi : int
        Resolution in dots per inch; the saved pixel size is size x dpi.
    tight : bool
        True to crop the canvas around the artists (bbox_inches="tight").

    ---- Globals read ----
    None.

    ---- Outputs ----
    List[Path]
        Paths of the saved files, in the order of ``formats``.

    ---- Globals mutated ----
    None. Resizes the figure to ``size`` and writes the files (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    # ---- 1 Prepare the folder and size -----------------------------------------------
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    fig.set_size_inches(*size, forward=False)

    # ---- 2 Save every format ---------------------------------------------------------
    paths = []
    for extension in formats:
        path = folder / f'{stem}.{extension}'
        fig.savefig(path,
                    format=extension,
                    dpi=dpi,
                    **({'bbox_inches': 'tight'} if tight else {}),
                    )
        paths.append(path)
    return paths


# ---- FILE NAME SANITISER -------------------------------------------------------------
def file_name_sanitiser(name: Any, default: str = 'experiment') -> str:
    """
    ---- Summary ----
    Main function to replace the characters that are illegal in file names.

    ---- Inputs ----
    name : Any
        Proposed name (converted with str).
    default : str
        Name used when nothing is left after cleaning.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        File name with the characters < > : " / backslash | ? * replaced by underscores.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    cleaned = re.sub(r'[<>:"/\\|?*]', '_', str(name)).strip()
    return cleaned or default


# ---- NAME SIMPLIFIER -----------------------------------------------------------------
def name_simplifier(value: Any) -> str:
    """
    ---- Summary ----
    Main function to simplify a name for matching by lower-casing it and removing
    everything except letters and digits, so "Cyt $c_1$" equals "cyt c1".

    ---- Inputs ----
    value : Any
        Name (converted with str).

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        Lower-case letters and digits only.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return re.sub(r'[^a-z0-9]', '', str(value).lower())
