"""
Export of the time response to a workbook that can be checked by hand.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from pathlib import Path

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import xlsxwriter
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_custom.run_namer import hours_parser
from utils_custom.time_response_plotter import (group_collector,
                                                shared_baseline_subtracter,
                                                )
from utils_custom.workbook_helpers import (formula_writer,
                                           number_writer,
                                           workbook_formats_builder,
                                           )


# ---- CONSTANTS -----------------------------------------------------------------------
NOTE_LINES = ('Time response: workbook for checking the maths by hand',
              '',
              'Each time point is one experiment. Percentages, differences and '
              'baselines are live Excel formulas on the numbers beside them.',
              '',
              'Difference spectra sheet',
              '  For every experiment: the mean attenuation spectrum of the '
              'penultimate window (minuend) and of the final window '
              '(subtrahend), and difference = minuend - subtrahend. The windows '
              'are the event averaging windows of the run; their start and end '
              'times (minutes) are in the header of each block.',
              '',
              'Haem percentages sheet',
              '  The difference spectrum of each experiment is decomposed into '
              'the haem spectra of the fit plus scatter terms by least squares. '
              'The fitted coefficient of each haem is listed. Percentage = 100 '
              'x coefficient / sum of the coefficients ("signed" basis) or / '
              'sum of the absolute coefficients ("absolute" basis); the basis '
              'used is written in the sheet. The percentages add up to 100 on '
              'the signed basis.',
              '',
              'Waterfall sheet (only when the shared baseline is on)',
              '  Mean = average of the difference spectra of the group; baseline '
              '= straight line fitted to the mean between the two wavelengths '
              'given in the header (SLOPE and INTERCEPT); corrected = '
              'difference - baseline. The waterfall figure then aligns and '
              'offsets the corrected spectra for display only.',
              )


# ---- HELPERS -------------------------------------------------------------------------


# ---- _difference_sheet_writer --------------------------------------------------------
def _difference_sheet_writer(workbook: object,
                             groups: dict,
                             formats: dict,
                             ) -> dict:
    """
    ---- Summary ----
    Helper function to write the two window means and their difference for every
    experiment.

    ---- Inputs ----
    workbook : object
        xlsxwriter workbook.
    groups : dict
        {group: [(time label, experiment), ...]} from group_collector.
    formats : dict
        Cell formats from workbook_formats_builder.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        {experiment name: (first column, first data row, number of rows)} so other
        sheets can refer to the difference column.

    ---- Globals mutated ----
    None. Adds a worksheet to the workbook (side effect).

    ---- Equations ----
    difference = mean spectrum of the minuend window - mean spectrum of the subtrahend
    window.

    ---- Helpers ----
    formula_writer
    number_writer
    """

    sheet = workbook.add_worksheet('Difference spectra')
    sheet.write(0, 0, 'Difference spectra (attenuation)', formats['title'])
    sheet.set_column(0, 400, 12)
    locations = {}
    col = 0
    for group, items in groups.items():
        for label, experiment in items:
            name = experiment['experiment_name']
            averages = experiment['spectral_averages']
            difference = experiment['difference_spectrum']
            minuend = averages['windows'][difference['minuend']]
            subtrahend = averages['windows'][difference['subtrahend']]
            sheet.merge_range(2, col, 2, col + 3, f'{group}, {label}', formats['group'])
            sheet.merge_range(3, col, 3, col + 3, name, formats['header'])
            sheet.merge_range(4, col, 4, col + 3,
                              f"Minuend {difference['minuend']}: "
                              f"{minuend['start_time']:.2f}-"
                              f"{minuend['end_time']:.2f} min",
                              formats['header'],
                              )
            sheet.merge_range(5, col, 5, col + 3,
                              f"Subtrahend {difference['subtrahend']}: "
                              f"{subtrahend['start_time']:.2f}-"
                              f"{subtrahend['end_time']:.2f} min",
                              formats['header'],
                              )
            heads = ['Wavelength (nm)', 'Minuend mean', 'Subtrahend mean', 'Difference']
            for offset, text in enumerate(heads):
                sheet.write(6, col + offset, text, formats['header'])
            wavelengths = averages['wavelengths']
            for number, wavelength in enumerate(wavelengths):
                row = 7 + number
                number_writer(sheet, row, col, wavelength, formats['number'])
                number_writer(sheet, row, col + 1, minuend['mean'][number],
                              formats['number'],
                              )
                number_writer(sheet, row, col + 2, subtrahend['mean'][number],
                              formats['number'],
                              )
                formula_writer(sheet,
                               row,
                               col + 3,
                               f'={xl_rowcol_to_cell(row, col + 1)}-'
                               f'{xl_rowcol_to_cell(row, col + 2)}',
                               difference['spectrum'][number],
                               formats['number'],
                               )
            locations[name] = (col, 7, len(wavelengths))
            col += 5
    sheet.freeze_panes(7, 0)
    return locations


# ---- _haem_sheet_writer --------------------------------------------------------------
def _haem_sheet_writer(workbook: object, groups: dict, formats: dict) -> None:
    """
    ---- Summary ----
    Helper function to write the haem coefficients of every experiment and the
    percentages calculated from them.

    ---- Inputs ----
    workbook : object
        xlsxwriter workbook.
    groups : dict
        {group: [(time label, experiment), ...]} from group_collector.
    formats : dict
        Cell formats from workbook_formats_builder.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Adds a worksheet to the workbook (side effect).

    ---- Equations ----
    percentage = 100 c / sum(c) (signed) or 100 c / sum(|c|) (absolute), with c the
    fitted haem coefficient.

    ---- Helpers ----
    formula_writer
    number_writer
    """

    sheet = workbook.add_worksheet('Haem percentages')
    sheet.write(0, 0, 'Haem coefficients and percentages', formats['title'])
    sheet.set_column(0, 0, 14)
    sheet.set_column(1, 1, 30)
    sheet.set_column(2, 60, 13)
    row = 2
    for group, items in groups.items():
        names = items[0][1]['difference_decomposition']['haem_names']
        count = len(names)
        sheet.merge_range(row, 0, row, 2 * count + 3, group, formats['group'])
        headers = ['Time point', 'Experiment']
        headers += [f'Coefficient {name}' for name in names]
        headers += ['Denominator']
        headers += [f'% {name}' for name in names]
        headers += ['Sum of %']
        for col, text in enumerate(headers):
            sheet.write(row + 1, col, text, formats['header'])
        sheet.set_row(row + 1, 32)
        for number, (label, experiment) in enumerate(items):
            decomposition = experiment['difference_decomposition']
            line = row + 2 + number
            coefficients = decomposition['coefficients']
            basis = decomposition['percent_basis']
            sheet.write(line, 0, label)
            sheet.write(line, 1, experiment['experiment_name'])
            for offset, value in enumerate(coefficients):
                number_writer(sheet, line, 2 + offset, value, formats['number'])
            span = xl_range(line, 2, line, 1 + count)
            denominator_cell = xl_rowcol_to_cell(line, 2 + count)
            absolute = np.abs(np.asarray(coefficients, dtype=float))
            formula_writer(sheet,
                           line,
                           2 + count,
                           f'=SUM({span})'
                           if basis == 'signed'
                           else f'=SUMPRODUCT(ABS({span}))',
                           float(np.sum(coefficients))
                           if basis == 'signed'
                           else float(absolute.sum()),
                           formats['number'],
                           )
            for offset in range(count):
                formula_writer(sheet,
                               line,
                               3 + count + offset,
                               f'=100*{xl_rowcol_to_cell(line, 2 + offset)}/'
                               f'{denominator_cell}',
                               decomposition['haem_percentages'][offset],
                               formats['percent'],
                               )
            formula_writer(sheet,
                           line,
                           3 + 2 * count,
                           f'=SUM({xl_range(line, 3 + count, line, 2 + 2 * count)})',
                           float(np.nansum(decomposition['haem_percentages'])),
                           formats['percent'],
                           )
        basis = items[0][1]['difference_decomposition']['percent_basis']
        sheet.write(row + 2 + len(items), 0, f'Percentage basis: {basis}')
        row += len(items) + 5


# ---- _picks_sheet_writer -------------------------------------------------------------
def _picks_sheet_writer(workbook: object,
                        picks: dict,
                        formats: dict,
                        ) -> None:
    """
    ---- Summary ----
    Helper function to list which experiments the panels of the figure show and which
    time points were left out of the waterfalls.

    ---- Inputs ----
    workbook : object
        xlsxwriter workbook.
    picks : dict
        Picks of the figure ('kinetic', 'decomposition' as lists of (group, time label,
        experiment name) and 'skipped_hours').
    formats : dict
        Cell formats from workbook_formats_builder.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Adds a worksheet to the workbook (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    sheet = workbook.add_worksheet('Figure panels')
    sheet.write(0, 0, 'Experiments shown in the figure', formats['title'])
    sheet.set_column(0, 3, 22)
    for col, text in enumerate(['Panel', 'Group', 'Time point', 'Experiment']):
        sheet.write(2, col, text, formats['header'])
    rows = [(f'Kinetic trace {n}', *pick)
            for n, pick in enumerate(picks['kinetic'], start=1)
            ]
    rows += [(f'Decomposition plot {n}', *pick)
             for n, pick in enumerate(picks['decomposition'], start=1)
             ]
    for number, values in enumerate(rows):
        for col, value in enumerate(values):
            sheet.write(3 + number, col, value)
    skipped = ', '.join(f'{hours:g}' for hours in picks['skipped_hours']) or 'none'
    sheet.write(4 + len(rows), 0, f'Hours left out of the waterfalls: {skipped}')


# ---- _waterfall_sheet_writer ---------------------------------------------------------
def _waterfall_sheet_writer(workbook: object,
                            groups: dict,
                            locations: dict,
                            config: dict,
                            formats: dict,
                            ) -> None:
    """
    ---- Summary ----
    Helper function to write the shared-baseline correction of the waterfalls.

    ---- Inputs ----
    workbook : object
        xlsxwriter workbook.
    groups : dict
        {group: [(time label, experiment), ...]} of the time points in the waterfalls.
    locations : dict
        Difference spectra locations from _difference_sheet_writer.
    config : dict
        Time response settings (WATERFALL_BASELINE_* and TIME_LABEL_FORMAT).
    formats : dict
        Cell formats from workbook_formats_builder.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Adds a worksheet to the workbook (side effect).

    ---- Equations ----
    baseline(w) = intercept + slope w, fitted to the mean difference spectrum between
    WATERFALL_BASELINE_X_MIN and WATERFALL_BASELINE_X_MAX; corrected = difference -
    baseline. Degrees above 1 are written as calculated values.

    ---- Helpers ----
    formula_writer
    number_writer
    shared_baseline_subtracter
    """

    sheet = workbook.add_worksheet('Waterfall')
    sheet.write(0, 0, 'Shared baseline correction of the waterfalls', formats['title'])
    sheet.set_column(0, 400, 13)
    col = 0
    for group, items in groups.items():
        wavelengths = np.column_stack([e['difference_spectrum']['wavelengths']
                                       for _, e in items
                                       ])
        spectra = np.column_stack([e['difference_spectrum']['spectrum']
                                   for _, e in items
                                   ])
        x_min = config['WATERFALL_BASELINE_X_MIN']
        x_max = config['WATERFALL_BASELINE_X_MAX']
        degree = config['WATERFALL_BASELINE_DEGREE']
        corrected, baseline = shared_baseline_subtracter(wavelengths,
                                                         spectra,
                                                         x_min,
                                                         x_max,
                                                         degree,
                                                         )
        count = len(items)
        n = spectra.shape[0]
        sheet.merge_range(2, col, 2, col + count + 2 + count, group, formats['group'])
        sheet.write(3, col, f'Baseline fit {x_min}-{x_max} nm, degree {degree}')
        heads = ['Wavelength (nm)']
        heads += [f'Difference {label}' for label, _ in items]
        heads += ['Mean', 'Baseline']
        heads += [f'Corrected {label}' for label, _ in items]
        for offset, text in enumerate(heads):
            sheet.write(4, col + offset, text, formats['header'])
        sheet.set_row(4, 32)
        low = config['WATERFALL_BASELINE_X_MIN']
        high = config['WATERFALL_BASELINE_X_MAX']
        mean_wl = wavelengths.mean(axis=1)
        inside = np.where((mean_wl >= low) & (mean_wl <= high))[0]
        mean_col, base_col = col + 1 + count, col + 2 + count
        if len(inside):
            fit_wl = xl_range(7 + inside[0], col, 7 + inside[-1], col)
            fit_mean = xl_range(7 + inside[0], mean_col, 7 + inside[-1], mean_col)
        for number in range(n):
            row = 7 + number
            number_writer(sheet, row, col, mean_wl[number], formats['number'])
            for k, (label, experiment) in enumerate(items):
                source, first, _ = locations[experiment['experiment_name']]
                formula_writer(sheet,
                               row,
                               col + 1 + k,
                               f"='Difference spectra'!"
                               f'{xl_rowcol_to_cell(first + number, source + 3)}',
                               spectra[number, k],
                               formats['number'],
                               )
            formula_writer(sheet,
                           row,
                           mean_col,
                           f'=AVERAGE({xl_range(row, col + 1, row, col + count)})',
                           float(spectra[number].mean()),
                           formats['number'],
                           )
            if config['WATERFALL_BASELINE_DEGREE'] == 1 and len(inside):
                wl_cell = xl_rowcol_to_cell(row, col)
                formula_writer(sheet,
                               row,
                               base_col,
                               f'=INTERCEPT({fit_mean},{fit_wl})+SLOPE({fit_mean},'
                               f'{fit_wl})*{wl_cell}',
                               baseline[number, 0],
                               formats['number'],
                               )
            else:
                number_writer(sheet, row, base_col, baseline[number, 0],
                              formats['number'],
                              )
            for k in range(count):
                formula_writer(sheet,
                               row,
                               col + 3 + count + k,
                               f'={xl_rowcol_to_cell(row, col + 1 + k)}-'
                               f'{xl_rowcol_to_cell(row, base_col)}',
                               corrected[number, k],
                               formats['number'],
                               )
        col += 2 * count + 5


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- time_response_exporter ----------------------------------------------------------
def time_response_exporter(experiments: dict,
                           config: dict,
                           picks: dict,
                           output_path: Path,
                           ) -> Path:
    """
    ---- Summary ----
    Main function to write the workbook behind the time response figure: the window
    means and difference spectra, the haem coefficients and percentages, and the
    waterfall baseline correction, as formulas so a reader can check the maths.

    ---- Inputs ----
    experiments : dict
        Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.
    config : dict
        Time response settings from custom_config.time_response_config_builder.
    picks : dict
        Experiments shown in the panels (``fig.time_response_picks``).
    output_path : Path
        Workbook (.xlsx) to write.

    ---- Globals read ----
    NOTE_LINES : tuple
        Text of the Notes sheet.

    ---- Outputs ----
    Path
        The workbook path.

    ---- Globals mutated ----
    None. Writes the workbook (side effect).

    ---- Equations ----
    None. See the Notes sheet of the workbook.

    ---- Helpers ----
    _difference_sheet_writer
    _haem_sheet_writer
    _picks_sheet_writer
    _waterfall_sheet_writer
    group_collector
    hours_parser
    workbook_formats_builder
    """

    # ---- 1 Collect the experiments ---------------------------------------------------
    groups = group_collector(experiments, config)
    skipped = {float(hours) for hours in config['SKIP_HOURS']}

    # ---- 2 Prepare the workbook ------------------------------------------------------
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    workbook = xlsxwriter.Workbook(str(output_path))
    formats = workbook_formats_builder(workbook)
    notes = workbook.add_worksheet('Notes')
    notes.set_column(0, 0, 130, workbook.add_format({'text_wrap': True}))
    for row, line in enumerate(NOTE_LINES):
        notes.write(row, 0, line, formats['title'] if row == 0 else None)

    # ---- 3 Write the sheets ----------------------------------------------------------
    _picks_sheet_writer(workbook, picks, formats)
    _haem_sheet_writer(workbook, groups, formats)
    locations = _difference_sheet_writer(workbook, groups, formats)
    if config['WATERFALL_SHARED_BASELINE']:
        shown = {group: [item for item in items
                         if hours_parser(item[1]['experiment_name']) not in skipped
                         ]
                 for group, items in groups.items()
                 }
        _waterfall_sheet_writer(workbook, shown, locations, config, formats)

    # ---- 4 Save and report -----------------------------------------------------------
    workbook.close()
    print(f'  {output_path.name} saved')
    return output_path
