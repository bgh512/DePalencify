"""
Cell formats and cell writers shared by the workbook exporters.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from typing import Any

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.schema import finite_float_converter


# ---- CONSTANTS -----------------------------------------------------------------------
GROUP_COLOUR = '#D9EAD3'
HEADER_COLOUR = '#EAF2F8'


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- formula_writer ------------------------------------------------------------------
def formula_writer(sheet: Any,
                   row: int,
                   col: int,
                   formula: str,
                   value: Any,
                   cell_format: Any,
                   ) -> None:
    """
    ---- Summary ----
    Main function to write a formula with the value that the program calculated, so
    that the cell shows the right number even before Excel recalculates it.

    ---- Inputs ----
    sheet : Any
        xlsxwriter worksheet.
    row : int
        Row index (0-based).
    col : int
        Column index (0-based).
    formula : str
        Excel formula starting with '='.
    value : Any
        Calculated result; NaN is stored as an empty string.
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

    cached = value
    if isinstance(value, (int, float, np.integer, np.floating)):
        number = finite_float_converter(value)
        cached = number if np.isfinite(number) else ''
    sheet.write_formula(row, col, formula, cell_format, cached)


# ---- number_writer -------------------------------------------------------------------
def number_writer(sheet: Any,
                  row: int,
                  col: int,
                  value: Any,
                  cell_format: Any,
                  ) -> None:
    """
    ---- Summary ----
    Main function to write a number, or leave the cell empty when it is not finite.

    ---- Inputs ----
    sheet : Any
        xlsxwriter worksheet.
    row : int
        Row index (0-based).
    col : int
        Column index (0-based).
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

    number = finite_float_converter(value)
    if np.isfinite(number):
        sheet.write_number(row, col, number, cell_format)
    else:
        sheet.write_blank(row, col, None, cell_format)


# ---- workbook_formats_builder --------------------------------------------------------
def workbook_formats_builder(workbook: Any) -> dict:
    """
    ---- Summary ----
    Main function to define the cell formats of the workbook.

    ---- Inputs ----
    workbook : Any
        xlsxwriter workbook.

    ---- Globals read ----
    GROUP_COLOUR, HEADER_COLOUR : str
        Fill colours of the header cells.

    ---- Outputs ----
    dict
        {name: xlsxwriter format} with the keys title, group, header, text, number,
        percent, p_value and integer.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    centred = {'bold': True, 'border': 1, 'align': 'center', 'valign': 'vcenter',
               'text_wrap': True,
               }
    return {'title': workbook.add_format({'bold': True, 'font_size': 13}),
            'group': workbook.add_format({**centred, 'bg_color': GROUP_COLOUR}),
            'header': workbook.add_format({**centred, 'bg_color': HEADER_COLOUR}),
            'text': workbook.add_format({'text_wrap': False}),
            'number': workbook.add_format({'num_format': '0.0000'}),
            'percent': workbook.add_format({'num_format': '0.00'}),
            'p_value': workbook.add_format({'num_format': '0.000000'}),
            'integer': workbook.add_format({'num_format': '0'}),
            }
