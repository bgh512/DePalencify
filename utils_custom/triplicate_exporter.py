"""Export of the across-run (triplicate) statistics to an Excel workbook."""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from pathlib import Path
from typing import Any

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import pandas as pd

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.helpers import excel_sheet_namer
from utils_shared.schema import finite_float_converter


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- TRIPLICATE EXPORTER -------------------------------------------------------------
def triplicate_exporter(triplicates: dict, output_path: Path) -> Path:
    """
    ---- Summary ----
    Main function to write one worksheet per condition of the across-run statistics to
    an Excel workbook.

    ---- Inputs ----
    triplicates : dict
        Across-run statistics per condition, from triplicate_averager (DATA_FORMAT.md).
    output_path : Path
        Workbook (.xlsx) to write.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Path
        The workbook path.

    ---- Globals mutated ----
    None. Writes the workbook (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    _number_writer
    excel_sheet_namer
    finite_float_converter
    """

    # ---- 1 Check the inputs ----------------------------------------------------------
    if not triplicates:
        raise ValueError('No triplicate results to export.')

    # ---- 2 Prepare the workbook ------------------------------------------------------
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        # ---- 2.1 Define the cell formats ---------------------------------------------
        workbook = writer.book
        group_format = workbook.add_format({'bold': True,
                                            'bg_color': '#D9EAD3',
                                            'border': 1,
                                            'align': 'center',
                                            'valign': 'vcenter',
                                            'text_wrap': True,
                                            },
                                           )
        sub_format = workbook.add_format({'bold': True,
                                          'bg_color': '#EAF2F8',
                                          'border': 1,
                                          'align': 'center',
                                          'valign': 'vcenter',
                                          'text_wrap': True,
                                          },
                                         )
        number_format = workbook.add_format({'num_format': '0.0000'})
        # 90 displays as 90.0%
        percent_format = workbook.add_format({'num_format': '0.0"%"'})

        # ---- 2.2 Define the number writer --------------------------------------------
        def _number_writer(sheet: Any,
                           row: int,
                           col: int,
                           value: Any,
                           cell_format: Any,
                           ) -> None:
            """
            ---- Summary ----
            Helper function to write a number, or leave the cell blank when it is not
            finite.

            ---- Inputs ----
            sheet : Any
                xlsxwriter worksheet.
            row : int
                Row index.
            col : int
                Column index.
            value : Any
                Value to write.
            cell_format : Any
                xlsxwriter cell format.

            ---- Globals read ----
            None.

            ---- Outputs ----
            None
                Nothing.

            ---- Globals mutated ----
            None. Writes to the worksheet (side effect).

            ---- Equations ----
            None.

            ---- Helpers ----
            finite_float_converter
            """

            value = finite_float_converter(value)
            if np.isfinite(value):
                sheet.write_number(row, col, value, cell_format)
            else:
                sheet.write_blank(row, col, None, cell_format)

        # ---- 2.3 Write a sheet for each condition ------------------------------------
        used_sheets = set()
        for condition, result in sorted(triplicates.items()):
            runs = result['run_numbers']
            print(f'\n  Triplicate condition: {condition}')
            print(f"    Runs found: {', '.join(f'run{r}' for r in runs)}")
            # Measurement groups: VoO2 first, then each haem.
            vo2_names = list(result['vo2'])
            groups = [('vo2', m, 'VoO2' if len(vo2_names) == 1 else f'VoO2 - {m}')
                      for m in vo2_names
                      ]
            groups += [('haem', m, str(m)) for m in result['haem']]
            subheaders = [h for r in runs for h in (f'Run {r} Mean', f'Run {r} SD')]
            subheaders += ['Replicate Mean',
                           'Replicate SD',
                           'Replicate SEM',
                           'Mean % of baseline',
                           'SD of % baseline',
                           'SEM of % baseline',
                           'Mean change from baseline',
                           'SD of change',
                           'SEM of change',
                           ]
            n_per_group = len(subheaders)
            n_run_cols = 2 * len(runs)
            sheet_name = excel_sheet_namer(condition, used_sheets)
            worksheet = workbook.add_worksheet(sheet_name)
            writer.sheets[sheet_name] = worksheet
            # Header: fixed columns first, then one block per measurement.
            fixed_headers = ['Average',
                             'Start time (min, first run)',
                             'End time (min, first run)',
                             ]
            for col, text in enumerate(fixed_headers):
                worksheet.merge_range(0, col, 1, col, text, group_format)
                worksheet.set_column(col, col, 14)
            first_col = len(fixed_headers)
            for _, _, label in groups:
                worksheet.merge_range(0,
                                      first_col,
                                      0,
                                      first_col + n_per_group - 1,
                                      label,
                                      group_format,
                                      )
                for offset, text in enumerate(subheaders):
                    worksheet.write(1, first_col + offset, text, sub_format)
                    worksheet.set_column(first_col + offset,
                                         first_col + offset,
                                         19 if offset >= n_run_cols + 3 else 15,
                                         )
                first_col += n_per_group
            worksheet.set_row(0, 32)
            worksheet.set_row(1, 44)
            worksheet.freeze_panes(2, 1)
            # Data rows.
            for row, window_name in enumerate(result['windows'], start=2):
                start, end = result['window_times'][window_name]
                worksheet.write(row, 0, window_name)
                _number_writer(worksheet, row, 1, start, number_format)
                _number_writer(worksheet, row, 2, end, number_format)
                col = len(fixed_headers)
                for kind, measurement, _ in groups:
                    stats = result[kind][measurement].get(window_name)
                    if stats is None:
                        col += n_per_group
                        continue
                    for run in runs:
                        _number_writer(worksheet,
                                       row,
                                       col,
                                       stats['run_means'].get(run),
                                       number_format,
                                       )
                        _number_writer(worksheet,
                                       row,
                                       col + 1,
                                       stats['run_sds'].get(run),
                                       number_format,
                                       )
                        col += 2
                    for key in ('mean', 'sd', 'sem'):
                        _number_writer(worksheet, row, col, stats[key], number_format)
                        col += 1
                    for key in ('change_mean', 'change_sd', 'change_sem'):
                        _number_writer(worksheet, row, col, stats[key], percent_format)
                        col += 1
                    for key in ('delta_mean', 'delta_sd', 'delta_sem'):
                        _number_writer(worksheet, row, col, stats[key], number_format)
                        col += 1
            print(f"    Worksheet '{sheet_name}': {len(result['windows'])} averaging "
                  f'windows',
                  )

    # ---- 3 Report the export ---------------------------------------------------------
    print(f'\n  Triplicate summary exported to: {output_path.parent.parent.name}/'
          f'{output_path.parent.name}/{output_path.name}',
          )
    return output_path
