"""Export of the time response summary (difference spectra and haem percentages)."""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from pathlib import Path

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import pandas as pd

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_custom.time_response_plotter import time_label_builder
from utils_shared.helpers import file_name_sanitiser


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- TIME RESPONSE EXPORTER ----------------------------------------------------------
def time_response_exporter(experiments: dict,
                           output_dir: Path,
                           time_label_format: str = '{hours:g} hours',
                           ) -> list:
    """
    ---- Summary ----
    Main function to write the haem percentages and difference spectra of each group as
    CSV files.

    ---- Inputs ----
    experiments : dict
        Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.
    output_dir : Path
        Folder the CSV files are written to.
    time_label_format : str
        Format of the time point label, for example '{hours:g} hours'.

    ---- Globals read ----
    None.

    ---- Outputs ----
    list
        Paths of the files written.

    ---- Globals mutated ----
    None. Writes files (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    file_name_sanitiser
    time_label_builder
    """

    # ---- 1 Prepare the output folder -------------------------------------------------
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # ---- 2 Group the experiments -----------------------------------------------------
    by_group = {}
    for name, experiment in experiments.items():
        if 'difference_decomposition' in experiment:
            by_group.setdefault(experiment.get('group', 'all'),
                                [],
                                ).append((name, experiment))

    # ---- 3 Write a file for each group -----------------------------------------------
    paths = []
    for group, items in by_group.items():
        stem = file_name_sanitiser(group)
        rows = []
        for name, exp in items:
            decomposition = exp['difference_decomposition']
            row = {'Time point': time_label_builder(name, time_label_format)}
            row.update(zip(decomposition['haem_names'],
                           decomposition['haem_percentages'],
                           ),
                       )
            rows.append(row)
        percentages = pd.DataFrame(rows)
        path = output_dir / f'{stem}_haem_percentages.csv'
        percentages.to_csv(path, index=False)
        paths.append(path)
        pairs = []
        for name, exp in items:
            difference = exp['difference_spectrum']
            columns = {f'{name} wavelength (nm)': difference['wavelengths'],
                       f'{name} difference attenuation': difference['spectrum'],
                       }
            pairs.append(pd.DataFrame(columns))
        path = output_dir / f'{stem}_difference_spectra.csv'
        pd.concat(pairs, axis=1).to_csv(path, index=False)
        paths.append(path)

    # ---- 4 Report the export ---------------------------------------------------------
    print(f'  Exported {len(paths)} summary file(s) to: {output_dir.name}/')
    return paths
