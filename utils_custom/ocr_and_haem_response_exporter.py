"""
Export of the OCR and haem response to a workbook that can be checked by hand.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import re
from pathlib import Path
from typing import Any, Optional

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import numpy as np
import xlsxwriter
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_custom.workbook_helpers import (formula_writer,
                                           number_writer,
                                           workbook_formats_builder,
                                           )
from utils_shared.helpers import excel_sheet_namer
from utils_shared.schema import finite_float_converter


# ---- CONSTANTS -----------------------------------------------------------------------
BASELINE_WINDOW = 'average0'
FAMILIES = (('value', 'Window mean', 'run_means'),
            ('change', '% of baseline', 'run_changes'),
            ('delta', 'Change from baseline', 'run_deltas'),
            )
NOTE_LINES = ('OCR and haem response: workbook for checking the maths by hand',
              '',
              'Every sheet is built so that each number can be recalculated '
              'from the numbers beside it. Mean, SD, SEM, the t-tests and the '
              'corrections are live Excel formulas, so clicking a cell shows '
              'how it is calculated.',
              '',
              'Condition sheets (one per strain and addition order)',
              '  Each row is an averaging window (average0 is the baseline window '
              'before the first addition). Each run column holds the mean of '
              'that run in the window, taken from the own workbook of the run '
              '("Averages" sheet). The run to file name list is at the top of '
              'the sheet.',
              '  Window mean: the values read from the runs.',
              '  % of baseline = window mean / baseline window mean x 100 (same '
              'run).',
              '  Change from baseline = window mean - baseline window mean (same '
              'run).',
              '  N = number of runs with a value; Mean = AVERAGE of the runs; SD '
              '= sample standard deviation, sqrt(sum((x - mean)^2) / (N - 1)), '
              'written STDEV in Excel; SEM = SD / sqrt(N). These are the means '
              'and error bars drawn in the figure.',
              '',
              'Baseline OCR sheet',
              '  The baseline OCR (average0) of every run, with the mean, SD and '
              'SEM of each group, as in the bar chart.',
              '',
              'Tests sheet',
              '  One row per window and panel: the run values of both groups, '
              'then N, mean, SD, SEM, and the Student t-test with equal '
              'variances (two-sided).',
              '  pooled variance = ((nA - 1) SDA^2 + (nB - 1) SDB^2) / (nA + nB - '
              '2); t = (meanA - meanB) / sqrt(pooled variance x (1/nA + 1/nB)); '
              'df = nA + nB - 2; p = TDIST(|t|, df, 2).',
              '  "p (TTEST check)" repeats the p value with the Excel function '
              'TTEST on the run values; it has to agree with p.',
              '  Correction across the windows of a panel: the rows of a panel '
              'are listed smallest p first (rank 1, 2, ...). Holm: multiplier = '
              'm - rank + 1 where m is the number of windows tested in the '
              'panel; the adjusted p is the running maximum of multiplier x p, '
              'capped at 1. Bonferroni: multiplier = m. None: multiplier = 1.',
              '  Significant when the adjusted p is below alpha. Marks drawn in '
              'the figure: * p < alpha, ** p < 0.01, *** p < 0.001 (adjusted '
              'p).',
              )


# ---- HELPERS -------------------------------------------------------------------------


# ---- _baseline_sheet_writer ----------------------------------------------------------
def _baseline_sheet_writer(workbook: Any, baseline: dict, formats: dict) -> None:
    """
    ---- Summary ----
    Helper function to write the baseline OCR of every run with the mean, SD and SEM
    of each group.

    ---- Inputs ----
    workbook : Any
        xlsxwriter workbook.
    baseline : dict
        Baseline summary from the response plotter: 'strains' and 'runs' ({group:
        {experiment name: baseline OCR}}).
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
    Mean = AVERAGE of the runs; SD = STDEV (n - 1); SEM = SD / sqrt(N).

    ---- Helpers ----
    _statistics_writer
    number_writer
    """

    sheet = workbook.add_worksheet('Baseline OCR')
    sheet.write(0, 0,
                f'Baseline OCR (window {BASELINE_WINDOW}), one value per run',
                formats['title'],
                )
    sheet.write(1, 0, f'Source of the OCR: {baseline["vo2_source"]}')
    sheet.set_column(0, 0, 14)
    sheet.set_column(1, 1, 44)
    sheet.set_column(2, 8, 11)
    row = 3
    for strain in baseline['strains']:
        runs = baseline['runs'][strain]
        sheet.merge_range(row, 0, row, 6, strain, formats['group'])
        for col, text in enumerate(['Run', 'Experiment', 'Baseline OCR']):
            sheet.write(row + 1, col, text, formats['header'])
        for number, (experiment, value) in enumerate(runs.items()):
            sheet.write(row + 2 + number, 0, number + 1)
            sheet.write(row + 2 + number, 1, experiment)
            number_writer(sheet, row + 2 + number, 2, value, formats['number'])
        end = row + 2 + max(len(runs), 1)
        for col, text in enumerate(['N', 'Mean', 'SD', 'SEM']):
            sheet.write(row + 1, 3 + col, text, formats['header'])
        sheet.write(row + 2, 3, 'of the values in column C', formats['text'])
        values = list(runs.values())
        _statistics_writer(sheet,
                           row + 3,
                           2,
                           len(values),
                           values,
                           formats,
                           formats['number'],
                           )
        row = end + 3


# ---- _condition_sheet_writer ---------------------------------------------------------
def _condition_sheet_writer(workbook: Any,
                            name: str,
                            condition: str,
                            result: dict,
                            formats: dict,
                            ) -> None:
    """
    ---- Summary ----
    Helper function to write the sheet of one condition: the run-by-run window means
    with their mean, SD and SEM for the OCR and each haem.

    ---- Inputs ----
    workbook : Any
        xlsxwriter workbook.
    name : str
        Sheet name.
    condition : str
        Condition name, e.g. 'knockdown_kcn_then_bd'.
    result : dict
        Across-run statistics of the condition from triplicate_averager.
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
    _measurement_table_writer
    """

    # ---- 1 Write the heading ---------------------------------------------------------
    sheet = workbook.add_worksheet(name)
    runs = list(result['run_numbers'])
    sheet.write(0, 0, f'Condition: {condition}', formats['title'])
    listing = '; '.join(f'Run {run} = {result["runs"][run]}' for run in runs)
    sheet.write(1, 0, f'Runs: {listing}')
    settings = ', '.join(f'{key} = {value}'
                         for key, value in result['settings'].items()
                         if isinstance(value, (str, int, float, bool))
                         )
    sheet.write(2, 0, f'Settings: {settings}')
    sheet.write(3, 0, 'Mean, SD and SEM are formulas on the run values: mean = '
                'AVERAGE, SD = STDEV (n - 1), SEM = SD / sqrt(N).',
                )
    sheet.set_column(0, 0, 14)
    sheet.set_column(1, 80, 11)
    sheet.freeze_panes(5, 1)

    # ---- 2 Write the OCR and haem tables ---------------------------------------------
    row = 5
    groups = [('vo2', m, 'OCR' if len(result['vo2']) == 1 else f'OCR - {m}')
              for m in result['vo2']
              ]
    groups += [('haem', m, f'Haem {m}') for m in result['haem']]
    for kind, measurement, label in groups:
        row = _measurement_table_writer(sheet,
                                        row,
                                        label,
                                        result['windows'],
                                        result[kind][measurement],
                                        runs,
                                        formats,
                                        )


# ---- _measurement_table_writer -------------------------------------------------------
def _measurement_table_writer(sheet: Any,
                              top_row: int,
                              label: str,
                              windows: list,
                              stats_by_window: dict,
                              runs: list,
                              formats: dict,
                              ) -> int:
    """
    ---- Summary ----
    Helper function to write the tables of one measurement (OCR or one haem): window
    means, % of baseline and change from baseline side by side, one row per window.

    ---- Inputs ----
    sheet : Any
        xlsxwriter worksheet.
    top_row : int
        Row index (0-based) of the first row written.
    label : str
        Measurement name.
    windows : list
        Window names, in order; the first is the baseline window.
    stats_by_window : dict
        {window: statistics} of this measurement, from triplicate_averager.
    runs : list
        Run numbers, in column order.
    formats : dict
        Cell formats from workbook_formats_builder.

    ---- Globals read ----
    BASELINE_WINDOW : str
        Name of the baseline window, the reference of the change tables.
    FAMILIES : tuple
        (key, title, statistics key) of the three tables.

    ---- Outputs ----
    int
        Index of the first free row below the tables.

    ---- Globals mutated ----
    None. Writes to the worksheet (side effect).

    ---- Equations ----
    % of baseline = window mean / baseline mean x 100; change from baseline = window
    mean - baseline mean; both per run, as formulas on the window mean table.

    ---- Helpers ----
    _statistics_writer
    finite_float_converter
    formula_writer
    number_writer
    """

    # ---- 1 Decide which tables to write ----------------------------------------------
    n_runs = len(runs)
    width = n_runs + 4
    has_baseline = BASELINE_WINDOW in windows
    shown = []
    for key, title, stats_key in FAMILIES:
        finite = [finite_float_converter(value)
                  for stats in stats_by_window.values()
                  for value in stats[stats_key].values()
                  ]
        if key == 'value' or (has_baseline and np.isfinite(finite).any()):
            shown.append((key, title, stats_key))
    sheet.merge_range(top_row,
                      0,
                      top_row,
                      len(shown) * (width + 1) - 1,
                      label,
                      formats['group'],
                      )
    sheet.write(top_row + 2, 0, 'Window', formats['header'])
    data_row = top_row + 3
    baseline_row = data_row + windows.index(BASELINE_WINDOW) if has_baseline else None

    # ---- 2 Write each table ----------------------------------------------------------
    for index, (key, title, stats_key) in enumerate(shown):
        first_col = 1 + index * (width + 1)
        sheet.merge_range(top_row + 1, first_col, top_row + 1, first_col + width - 1,
                          title,
                          formats['header'],
                          )
        run_labels = [f'Run {run}' for run in runs]
        for offset, text in enumerate(run_labels + ['N', 'Mean', 'SD', 'SEM']):
            sheet.write(top_row + 2, first_col + offset, text, formats['header'])
        cell_format = formats['percent'] if key == 'change' else formats['number']
        for number, window in enumerate(windows):
            row = data_row + number
            stats = stats_by_window.get(window)
            if index == 0:
                sheet.write(row, 0, window)
            if stats is None:
                continue
            cached = [stats[stats_key].get(run, np.nan) for run in runs]
            for offset, run in enumerate(runs):
                col = first_col + offset
                if key == 'value':
                    number_writer(sheet, row, col, cached[offset], cell_format)
                    continue
                value_cell = xl_rowcol_to_cell(row, 1 + offset)
                base_cell = xl_rowcol_to_cell(baseline_row, 1 + offset, row_abs=True)
                if key == 'change':
                    formula = (f'=IF(AND(ISNUMBER({value_cell}),ISNUMBER({base_cell}),'
                               f'{base_cell}<>0),{value_cell}/{base_cell}*100,"")'
                               )
                else:
                    formula = (f'=IF(AND(ISNUMBER({value_cell}),ISNUMBER({base_cell})),'
                               f'{value_cell}-{base_cell},"")'
                               )
                formula_writer(sheet, row, col, formula, cached[offset], cell_format)
            _statistics_writer(sheet,
                               row,
                               first_col,
                               n_runs,
                               cached,
                               formats,
                               cell_format,
                               )
    return data_row + len(windows) + 1


# ---- _statistics_writer --------------------------------------------------------------
def _statistics_writer(sheet: Any,
                       row: int,
                       first_col: int,
                       n_runs: int,
                       values: list,
                       formats: dict,
                       cell_format: Any,
                       ) -> None:
    """
    ---- Summary ----
    Helper function to write N, mean, SD and SEM formulas to the right of the run cells
    of one row.

    ---- Inputs ----
    sheet : Any
        xlsxwriter worksheet.
    row : int
        Row index (0-based).
    first_col : int
        Column of the first run cell; the statistics follow the last run cell.
    n_runs : int
        Number of run columns.
    values : list
        The run values of the row (NaN where a run has none), for the cached results.
    formats : dict
        Cell formats from workbook_formats_builder.
    cell_format : Any
        Format of the mean, SD and SEM cells.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Writes to the worksheet (side effect).

    ---- Equations ----
    N = count of the finite values; mean = sum / N; SD = sqrt(sum((x - mean)^2) /
    (N - 1)); SEM = SD / sqrt(N). Mean, SD and SEM are empty when N is too small.

    ---- Helpers ----
    finite_float_converter
    formula_writer
    """

    # ---- 1 Calculate the cached results ----------------------------------------------
    numbers = np.array([finite_float_converter(v) for v in values], dtype=float)
    numbers = numbers[np.isfinite(numbers)]
    n = len(numbers)
    mean = float(np.mean(numbers)) if n else np.nan
    sd = float(np.std(numbers, ddof=1)) if n > 1 else np.nan
    sem = sd / np.sqrt(n) if n > 1 else np.nan

    # ---- 2 Write the formulas --------------------------------------------------------
    runs = xl_range(row, first_col, row, first_col + n_runs - 1)
    n_cell = xl_rowcol_to_cell(row, first_col + n_runs)
    sd_cell = xl_rowcol_to_cell(row, first_col + n_runs + 2)
    formula_writer(sheet, row, first_col + n_runs, f'=COUNT({runs})', n,
                   formats['integer'],
                   )
    formula_writer(sheet,
                   row,
                   first_col + n_runs + 1,
                   f'=IF({n_cell}>0,AVERAGE({runs}),"")',
                   mean,
                   cell_format,
                   )
    formula_writer(sheet,
                   row,
                   first_col + n_runs + 2,
                   f'=IF({n_cell}>1,STDEV({runs}),"")',
                   sd,
                   cell_format,
                   )
    formula_writer(sheet,
                   row,
                   first_col + n_runs + 3,
                   f'=IF({n_cell}>1,{sd_cell}/SQRT({n_cell}),"")',
                   sem,
                   cell_format,
                   )


# ---- _test_row_writer ----------------------------------------------------------------
def _test_row_writer(sheet: Any,
                     row: int,
                     record: dict,
                     columns: dict,
                     panel_first_row: int,
                     rank: int,
                     panel_size: int,
                     running: float,
                     formats: dict,
                     ) -> None:
    """
    ---- Summary ----
    Helper function to write one t-test comparison: the run values, the statistics,
    the t-test and the multiple comparison correction, as formulas.

    ---- Inputs ----
    sheet : Any
        xlsxwriter worksheet.
    row : int
        Row index (0-based) of this comparison.
    record : dict
        One t-test record from the response plotter (DATA_FORMAT.md).
    columns : dict
        Column indices by name, from _tests_sheet_writer.
    panel_first_row : int
        Row index of the first comparison of this panel.
    rank : int
        Rank of the comparison in its panel by raw p value, from 1.
    panel_size : int
        Number of comparisons in the panel.
    running : float
        Running maximum of multiplier x p up to this rank, for the cached result.
    formats : dict
        Cell formats from workbook_formats_builder.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Writes to the worksheet (side effect).

    ---- Equations ----
    pooled = ((nA - 1) SDA^2 + (nB - 1) SDB^2) / (nA + nB - 2); t = (meanA - meanB) /
    sqrt(pooled (1/nA + 1/nB)); df = nA + nB - 2; p = TDIST(|t|, df, 2). Holm: adjusted
    p = min(1, max over ranks <= r of (m - rank + 1) p); Bonferroni: min(1, m p).

    ---- Helpers ----
    formula_writer
    number_writer
    """

    # ---- 1 Write the labels and the run values ---------------------------------------
    cell = {name: xl_rowcol_to_cell(row, col) for name, col in columns.items()}
    values = {'a': list(record['values_a'].values()),
              'b': list(record['values_b'].values()),
              }
    for name in ('panel', 'measurement', 'window', 'group_a', 'group_b'):
        sheet.write(row, columns[name], re.sub(r'[$\\{}]', '', record[name]))
    sheet.write(row, columns['runs_a'], ', '.join(str(r) for r in record['values_a']))
    sheet.write(row, columns['runs_b'], ', '.join(str(r) for r in record['values_b']))
    ranges = {}
    for side in ('a', 'b'):
        first = columns[f'{side}_first']
        for offset, value in enumerate(values[side]):
            number_writer(sheet, row, first + offset, value, formats['number'])
        ranges[side] = xl_range(row, first, row, first + max(len(values[side]), 1) - 1)

    # ---- 2 Write the group statistics ------------------------------------------------
    stats = {}
    for side in ('a', 'b'):
        numbers = np.array(values[side], dtype=float)
        n = len(numbers)
        mean = float(numbers.mean())
        sd = float(numbers.std(ddof=1)) if n > 1 else np.nan
        stats[side] = (n, mean, sd)
        formula_writer(sheet, row, columns[f'{side}_n'],
                       f'=COUNT({ranges[side]})',
                       n,
                       formats['integer'],
                       )
        formula_writer(sheet, row, columns[f'{side}_mean'],
                       f'=AVERAGE({ranges[side]})',
                       mean,
                       formats['number'],
                       )
        formula_writer(sheet, row, columns[f'{side}_sd'],
                       f'=STDEV({ranges[side]})',
                       sd,
                       formats['number'],
                       )
        formula_writer(sheet, row, columns[f'{side}_sem'],
                       f'={cell[f"{side}_sd"]}/SQRT({cell[f"{side}_n"]})',
                       sd / np.sqrt(n),
                       formats['number'],
                       )

    # ---- 3 Write the t-test ----------------------------------------------------------
    (n_a, _, sd_a), (n_b, _, sd_b) = stats['a'], stats['b']
    df = n_a + n_b - 2
    pooled = ((n_a - 1) * sd_a ** 2 + (n_b - 1) * sd_b ** 2) / df
    formula_writer(sheet, row, columns['df'],
                   f'={cell["a_n"]}+{cell["b_n"]}-2',
                   df,
                   formats['integer'],
                   )
    formula_writer(sheet, row, columns['pooled'],
                   f'=(({cell["a_n"]}-1)*{cell["a_sd"]}^2+({cell["b_n"]}-1)*'
                   f'{cell["b_sd"]}^2)/{cell["df"]}',
                   pooled,
                   formats['number'],
                   )
    formula_writer(sheet, row, columns['t'],
                   f'=({cell["a_mean"]}-{cell["b_mean"]})/SQRT({cell["pooled"]}*'
                   f'(1/{cell["a_n"]}+1/{cell["b_n"]}))',
                   record['t'],
                   formats['number'],
                   )
    formula_writer(sheet, row, columns['p'],
                   f'=TDIST(ABS({cell["t"]}),{cell["df"]},2)',
                   record['p'],
                   formats['p_value'],
                   )
    formula_writer(sheet, row, columns['p_check'],
                   f'=TTEST({ranges["a"]},{ranges["b"]},2,2)',
                   record['p'],
                   formats['p_value'],
                   )

    # ---- 4 Write the correction ------------------------------------------------------
    correction = record['correction']
    multiplier = {'holm': panel_size - rank + 1,
                  'bonferroni': panel_size,
                  'none': 1,
                  }[correction]
    sheet.write_number(row, columns['rank'], rank, formats['integer'])
    sheet.write_number(row, columns['panel_size'], panel_size, formats['integer'])
    formula = {'holm': f'={cell["panel_size"]}-{cell["rank"]}+1',
               'bonferroni': f'={cell["panel_size"]}',
               'none': '=1',
               }[correction]
    formula_writer(sheet, row, columns['multiplier'], formula, multiplier,
                   formats['integer'],
                   )
    candidate = multiplier * record['p']
    formula_writer(sheet, row, columns['candidate'],
                   f'={cell["multiplier"]}*{cell["p"]}',
                   candidate,
                   formats['p_value'],
                   )
    running_cell = xl_rowcol_to_cell(row, columns['running'])
    if correction == 'holm':
        first_candidate = xl_rowcol_to_cell(panel_first_row,
                                            columns['candidate'],
                                            row_abs=True,
                                            )
        formula_writer(sheet, row, columns['running'],
                       f'=MAX({first_candidate}:{cell["candidate"]})',
                       running,
                       formats['p_value'],
                       )
    else:
        formula_writer(sheet, row, columns['running'],
                       f'={cell["candidate"]}',
                       candidate,
                       formats['p_value'],
                       )
    formula_writer(sheet, row, columns['adjusted'],
                   f'=MIN(1,{running_cell})',
                   record['p_adjusted'],
                   formats['p_value'],
                   )
    sheet.write_number(row, columns['alpha'], record['alpha'], formats['p_value'])
    formula_writer(sheet, row, columns['significant'],
                   f'=IF({cell["adjusted"]}<{cell["alpha"]},"yes","no")',
                   'yes' if record['significant'] else 'no',
                   formats['text'],
                   )
    if record['panel'] == 'Baseline OCR':
        sheet.write(row, columns['mark'], record['mark'])
    else:
        formula_writer(sheet, row, columns['mark'],
                       f'=IF({cell["adjusted"]}<{cell["alpha"]},IF({cell["adjusted"]}'
                       f'<0.001,"***",IF({cell["adjusted"]}<0.01,"**","*")),"")',
                       record['mark'],
                       formats['text'],
                       )


# ---- _tests_sheet_writer -------------------------------------------------------------
def _tests_sheet_writer(workbook: Any, tests: list, formats: dict) -> None:
    """
    ---- Summary ----
    Helper function to write the t-tests of the figure, one row per comparison, with
    everything needed to repeat them.

    ---- Inputs ----
    workbook : Any
        xlsxwriter workbook.
    tests : list
        t-test records from the response plotter (DATA_FORMAT.md).
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
    See _test_row_writer.

    ---- Helpers ----
    _test_row_writer
    """

    # ---- 1 Lay out the columns -------------------------------------------------------
    sheet = workbook.add_worksheet('Tests')
    n_a = max(max(len(r['values_a']) for r in tests), 1)
    n_b = max(max(len(r['values_b']) for r in tests), 1)
    names = ['panel', 'measurement', 'window', 'group_a', 'group_b', 'runs_a',
             'runs_b',
             ]
    headers = ['Panel', 'Measurement', 'Window', 'Group A', 'Group B', 'Runs A',
               'Runs B',
               ]
    columns = {name: index for index, name in enumerate(names)}
    columns['a_first'] = len(names)
    columns['b_first'] = len(names) + n_a
    headers += [f'A value {i + 1}' for i in range(n_a)]
    headers += [f'B value {i + 1}' for i in range(n_b)]
    later = [('a_n', 'N A'), ('a_mean', 'Mean A'), ('a_sd', 'SD A'),
             ('a_sem', 'SEM A'), ('b_n', 'N B'), ('b_mean', 'Mean B'),
             ('b_sd', 'SD B'), ('b_sem', 'SEM B'), ('df', 'df'),
             ('pooled', 'Pooled variance'), ('t', 't'), ('p', 'p (two-sided)'),
             ('p_check', 'p (TTEST check)'), ('rank', 'Rank in panel'),
             ('panel_size', 'm (windows in panel)'), ('multiplier', 'Multiplier'),
             ('candidate', 'Multiplier x p'), ('running', 'Running maximum'),
             ('adjusted', 'Adjusted p'), ('alpha', 'Alpha'),
             ('significant', 'Significant'), ('mark', 'Mark in figure'),
             ]
    for name, header in later:
        columns[name] = len(headers)
        headers.append(header)
    sheet.write(0, 0, 'Student t-tests (equal variances, two-sided) between the two '
                'groups, window by window',
                formats['title'],
                )
    sheet.write(1, 0, 'Group A and B values are the run values of each group in the '
                'window; see the Notes sheet for the formulas.',
                )
    for col, header in enumerate(headers):
        sheet.write(3, col, header, formats['header'])
    sheet.set_row(3, 32)
    sheet.set_column(0, 0, 34)
    sheet.set_column(1, len(headers), 12)
    sheet.freeze_panes(4, 3)

    # ---- 2 Write the comparisons panel by panel --------------------------------------
    row = 4
    for panel in dict.fromkeys(record['panel'] for record in tests):
        records = sorted((r for r in tests if r['panel'] == panel),
                         key=lambda r: r['p'],
                         )
        candidates = [{'holm': len(records) - rank + 1,
                       'bonferroni': len(records),
                       'none': 1,
                       }[record['correction']] * record['p']
                      for rank, record in enumerate(records, start=1)
                      ]
        running = np.maximum.accumulate(candidates)
        for rank, record in enumerate(records, start=1):
            _test_row_writer(sheet,
                             row,
                             record,
                             columns,
                             row - rank + 1,
                             rank,
                             len(records),
                             (float(running[rank - 1])
                              if record['correction'] == 'holm'
                              else candidates[rank - 1]
                              ),
                             formats,
                             )
            row += 1


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- ocr_and_haem_response_exporter --------------------------------------------------
def ocr_and_haem_response_exporter(triplicates: dict,
                                   tests: list,
                                   baseline: Optional[dict],
                                   output_path: Path,
                                   ) -> Path:
    """
    ---- Summary ----
    Main function to write the workbook behind the OCR and haem response figure: the
    run-by-run values with their mean, SD and SEM, the baseline OCR and the t-tests,
    all as formulas so a reader can check the maths.

    ---- Inputs ----
    triplicates : dict
        Across-run statistics per condition, from triplicate_averager (DATA_FORMAT.md).
    tests : list
        t-test records of the figure (``fig.response_tests``); may be empty.
    baseline : Optional[dict]
        Baseline summary of the figure (``fig.response_baseline``), or None.
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
    _baseline_sheet_writer
    _condition_sheet_writer
    _tests_sheet_writer
    excel_sheet_namer
    workbook_formats_builder
    """

    # ---- 1 Check the inputs ----------------------------------------------------------
    if not triplicates:
        raise ValueError('No triplicate results to export.')

    # ---- 2 Prepare the workbook ------------------------------------------------------
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    workbook = xlsxwriter.Workbook(str(output_path))
    formats = workbook_formats_builder(workbook)

    # ---- 3 Write the sheets ----------------------------------------------------------
    notes = workbook.add_worksheet('Notes')
    notes.set_column(0, 0, 130, workbook.add_format({'text_wrap': True}))
    for row, line in enumerate(NOTE_LINES):
        notes.write(row, 0, line, formats['title'] if row == 0 else None)
    used = {'Notes', 'Baseline OCR', 'Tests'}
    if baseline is not None:
        _baseline_sheet_writer(workbook, baseline, formats)
    if tests:
        _tests_sheet_writer(workbook, tests, formats)
    for condition, result in sorted(triplicates.items()):
        sheet_name = excel_sheet_namer(condition, used)
        _condition_sheet_writer(workbook, sheet_name, condition, result, formats)
        print(f'  Sheet {sheet_name!r}: {len(result["windows"])} averaging windows, '
              f'{len(result["run_numbers"])} runs',
              )

    # ---- 4 Save and report -----------------------------------------------------------
    workbook.close()
    print(f'  {output_path.name} saved')
    return output_path
