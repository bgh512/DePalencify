"""
Saving of the custom figures into the results folder.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from pathlib import Path

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
from matplotlib.figure import Figure

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.helpers import figure_saver


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- custom_figure_saver -------------------------------------------------------------
def custom_figure_saver(fig: Figure, export_root: Path, config: dict) -> list:
    """
    ---- Summary ----
    Main function to save one of the custom figures (2x2, OCR and haem response, time
    response) at its exact size in the results folder.

    ---- Inputs ----
    fig : Figure
        Figure returned by one of the custom figure plotters.
    export_root : Path
        Results folder; the files are written straight into it.
    config : dict
        Figure settings dictionary built in custom_config.py.

    ---- Globals read ----
    None.

    ---- Outputs ----
    list
        Paths of the files written.

    ---- Globals mutated ----
    None. Writes the figure files (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    figure_saver
    """

    # ---- 1 Save the figure -----------------------------------------------------------
    export_root = Path(export_root)
    width, height = config['FIGURE_SIZE']
    paths = figure_saver(fig,
                         export_root,
                         config['FILE_NAME'],
                         config['SAVE_FORMATS'],
                         config['FIGURE_SIZE'],
                         config['FIGURE_DPI'],
                         tight=config['TIGHT_BBOX'],
                         )

    # ---- 2 Report the export ---------------------------------------------------------
    print(f"  {config['FILE_NAME']} saved at {width:g} x {height:g} in, "
          f"{config['FIGURE_DPI']} dpi "
          f"({round(width * config['FIGURE_DPI'])} x "
          f"{round(height * config['FIGURE_DPI'])} px)",
          )
    return paths
