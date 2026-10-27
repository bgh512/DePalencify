"""Settings dictionaries of the custom figures, built from the terminal answers."""

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from config import Config, haem_colour_mapper
from utils_shared.figure_layout import figure_size_calculator
from utils_shared.helpers import name_simplifier


# ---- CONSTANTS -----------------------------------------------------------------------
HAEM_LABELS = {'cyta605': '$a_{605}$',
               'cytcc': '$cc$',
               'cytc1': '$c_1$',
               'cytbh': '$b_H$',
               'cytbl': '$b_L$',
               'cytb557': '$b_{557}$',
               }
ORDER_COLUMNS = ('kcn_then_bd', 'bd_then_kcn')
STRAIN_ROWS = ('knockdown', 'control')
GROUP_STYLES = {'knockdown': {'colour': '#0072B2', 'linestyle': '-', 'marker': 's'},
                'control': {'colour': '#D55E00', 'linestyle': '--', 'marker': '^'},
                }
HAEM_AXIS_LABELS = {'raw': 'Haem concentration',
                    'od': 'Haem concentration (/OD)',
                    'percent': 'Oxidised haem (% of range)',
                    'abs': 'Haem absorbance (mOD)',
                    'abs_od': 'Absorbance (mOD OD$^{-1}$)',
                    'delta_abs': 'ΔA (mOD)',
                    'delta_abs_od': 'ΔA (mOD OD$^{-1}$)',
                    }
SAVE_FORMATS = ('svg', 'png')
OUTPUT_SUBFOLDER = ''
DATA_SUBFOLDER = 'triplicate_data'
DELTA_A_OD_LABEL = '$\\Delta$A (mOD OD$^{-1}$)'
HAEM_ABS_OD_LABEL = 'Haem absorbance (mOD OD$^{-1}$)'


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- EXEMPLAR CONFIG BUILDER ---------------------------------------------------------
def exemplar_config_builder(cfg: Config, answers: dict) -> dict:
    """
    ---- Summary ----
    Main function to build the settings of the four-run exemplar figure.

    ---- Inputs ----
    cfg : Config
        Figure style derived from the answers (config.py).
    answers : dict
        Terminal answers; uses ho_exemplar_run, ho_ex_columns and ho_ex_height.

    ---- Globals read ----
    ORDER_COLUMNS, STRAIN_ROWS, SAVE_FORMATS, OUTPUT_SUBFOLDER, DATA_SUBFOLDER.

    ---- Outputs ----
    dict
        Settings for exemplar_figure_plotter and publication_figure_saver.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    figure_size_calculator
    """

    # ---- 1 Read the style and size ---------------------------------------------------
    style, fonts, unit, spec = cfg.STYLE, cfg.FONTS, cfg.UNIT, cfg.SPEC
    size = figure_size_calculator(spec,
                                  answers['ho_ex_columns'],
                                  answers['ho_ex_height'],
                                  )

    # ---- 2 Build the configuration ---------------------------------------------------
    return {'SAVE_FIGURE': True,
            'SAVE_FORMATS': SAVE_FORMATS,
            'OUTPUT_SUBFOLDER': OUTPUT_SUBFOLDER,
            'DATA_SUBFOLDER': DATA_SUBFOLDER,
            'FILE_NAME': '2x2_comparison',
            'ORDER_COLUMNS': ORDER_COLUMNS,
            'STRAIN_ROWS': STRAIN_ROWS,
            'EXEMPLAR_RUN': answers['ho_exemplar_run'],
            'CROP_START': 'baseline',
            'CROP_MARGIN_MINUTES': 0.0,
            'CROP_BEFORE_FIRST_ADDITION_MINUTES': 0.5,
            'TIME_AXIS_LABEL': 'Time from baseline (min)',
            'RUN_NAME_WATERMARK': answers.get('ex_watermark', True),
            'INDIVIDUAL_OVERRIDES': {'PANEL_HEIGHT_RATIOS': {'oxygen': 3,
                                                             'vo2': 4,
                                                             'haem': 5,
                                                             },
                                     'EQUAL_PANEL_HEIGHTS': True,
                                     'EVENT_LABEL_ROTATION': 30,
                                     'LEGEND_LOCATIONS': {'oxygen': 'center right'},
                                     },
            'FIGURE_SIZE': size,
            'FIGURE_DPI': cfg.FIGURE_DPI,
            'TIGHT_BBOX': False,
            'FIGURE_TITLE': None,
            'SUPTITLE_FONT_SIZE': fonts['title'],
            'UNIT_PT': unit,
            'EDGE_PAD_PT': style['edge_pad'],
            'TITLE_GAP_PT': style['title_gap'],
            'PANEL_LETTERS': True,
            'PANEL_LETTER_CASE': spec['panel_letter_case'],
            'PANEL_LETTER_FONT_SIZE': fonts['panel_letter'],
            }


# ---- HAEM LABELLER -------------------------------------------------------------------
def haem_labeller(haem_name: str) -> str:
    """
    ---- Summary ----
    Main function to give a haem its short y-axis label, for example '$b_H$'.

    ---- Inputs ----
    haem_name : str
        Haem name as written in the fit file, for example 'Cyt bH'.

    ---- Globals read ----
    HAEM_LABELS (module constant).

    ---- Outputs ----
    str
        Short label; the haem name itself when it is not a known haem.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    name_simplifier
    """

    return HAEM_LABELS.get(name_simplifier(haem_name), haem_name)


# ---- INDIVIDUAL CONFIG BUILDER -------------------------------------------------------
def individual_config_builder(answers: dict,
                              vo2_source: str,
                              haem_source: str,
                              haem_names: list,
                              ) -> dict:
    """
    ---- Summary ----
    Main function to build the individual-experiment plot settings used inside the
    custom figures: oxygen, OCR and one panel per chosen haem.

    ---- Inputs ----
    answers : dict
        Terminal answers (journal, size and label angle are taken from them).
    vo2_source : str
        OCR source plotted: 'raw' or 'od'.
    haem_source : str
        Haem source plotted, for example 'delta_abs_od'.
    haem_names : list
        Haem names, in panel order, matching the decomposition columns.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        Plot settings in the format of Config.plot_config.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    plot_config_builder
    """

    # ---- 1 Merge the answers ---------------------------------------------------------
    merged = dict(answers,
                  plot_o2=True,
                  plot_ocr=True,
                  plot_haems=True,
                  decompose=True,
                  averaging=True,
                  haems=list(haem_names),
                  ocr_mode=vo2_source,
                  )

    # ---- 2 Build the individual configuration ----------------------------------------
    individual = Config(merged).plot_config_builder(vo2_source, haem_source)

    # ---- 3 Set the haem axis labels --------------------------------------------------
    individual['HAEM_AXIS_LABELS'] = dict(individual['HAEM_AXIS_LABELS'],
                                          **HAEM_AXIS_LABELS,
                                          )
    return individual


# ---- PUBLICATION CONFIG BUILDER ------------------------------------------------------
def publication_config_builder(cfg: Config, answers: dict, haem_names: list) -> dict:
    """
    ---- Summary ----
    Main function to build the settings of the haem and OCR publication figure.

    ---- Inputs ----
    cfg : Config
        Figure style derived from the answers (config.py).
    answers : dict
        Terminal answers; uses ho_haems, ho_metric, ho_pub_columns and ho_pub_height.
    haem_names : list
        Haem names of the fit, in fit order.

    ---- Globals read ----
    ORDER_COLUMNS, STRAIN_ROWS, GROUP_STYLES, SAVE_FORMATS, OUTPUT_SUBFOLDER,
    DATA_SUBFOLDER.

    ---- Outputs ----
    dict
        Settings for publication_figure_plotter and publication_figure_saver.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    figure_size_calculator
    haem_labeller
    """

    # ---- 1 Gather the style values ---------------------------------------------------
    style, fonts, unit, spec = cfg.STYLE, cfg.FONTS, cfg.UNIT, cfg.SPEC
    size = figure_size_calculator(spec,
                                  answers['ho_pub_columns'],
                                  answers['ho_pub_height'],
                                  )

    # ---- 2 Build the settings --------------------------------------------------------
    rows = [{'haem': name, 'label': haem_labeller(name)} for name in haem_names]
    return ({'SAVE_FIGURE': True,
             'SAVE_FORMATS': SAVE_FORMATS,
             'OUTPUT_SUBFOLDER': OUTPUT_SUBFOLDER,
             'DATA_SUBFOLDER': DATA_SUBFOLDER,
             'FILE_NAME': 'publication_figure',
             'ORDER_COLUMNS': ORDER_COLUMNS,
             'STRAIN_ROWS': STRAIN_ROWS,
             'BLOCK_ORDER': ('baseline', 'ocr_response', 'haem_response'),
             'HAEM_RESPONSE_ROWS': rows,
             'HAEM_RESPONSE_SHOW': list(answers['ho_haems']),
             'HAEM_RESPONSE_METRIC': answers['ho_metric'],
             'OCR_VO2_COLUMN': None,
             'GROUP_STYLES': GROUP_STYLES,
             'FIGURE_SIZE': size,
             'FIGURE_DPI': cfg.FIGURE_DPI,
             'TIGHT_BBOX': False,
             'FIGURE_TITLE': None,
             'SUPTITLE_FONT_SIZE': fonts['title'],
             'TITLE_FONT_SIZE': fonts['title'],
             'UNIT_PT': unit,
             'EDGE_PAD_PT': style['edge_pad'],
             'TITLE_GAP_PT': style['title_gap'],
             'THIN_LINE_WIDTH': style['thin_line_width'],
             'HEIGHT_RATIOS': {'baseline': 7, 'ocr_response': 7, 'haem_response': 18},
             'BASELINE_BAR_WIDTH': 0.4,
             'BASELINE_BAR_X_MARGIN': 0.8,
             'SHARE_Y_BETWEEN_ORDERS': True,
             'AXES_TOP_SPINE': False,
             'AXES_RIGHT_SPINE': False,
             'BASELINE_TEST': True,
             'BASELINE_TEST_STYLE': 'stars',
             'BASELINE_TEST_FONT_SIZE': fonts['label'],
             'BASELINE_TEST_BRACKET_HEIGHT': 0.03,
             'PANEL_LETTERS': True,
             'PANEL_LETTER_CASE': spec['panel_letter_case'],
             'PANEL_LETTER_FONT_SIZE': fonts['panel_letter'],
             'VO2_AXIS_LABELS': {'raw': 'Baseline OCR\n($\\mu$M min$^{-1}$)',
                                 'od': 'OCR (µM\nmin$^{-1}$\nOD$^{-1}$)',
                                 'percent': 'OCR (% of range)',
                                 },
             'VO2_Y_MIN': 0,
             'OCR_RESPONSE_AXIS_LABEL': '% of baseline OCR',
             'HAEM_RESPONSE_AXIS_LABELS': {'delta': {'abs': '$\\Delta$A (mOD)',
                                                     'abs_od': DELTA_A_OD_LABEL,
                                                     'delta_abs': '$\\Delta$A (mOD)',
                                                     'delta_abs_od': DELTA_A_OD_LABEL,
                                                     'percent': 'Change in oxidised '
                                                                'haem (%)',
                                                     'default': 'Change from baseline',
                                                     },
                                           'change': 'Change from baseline (%)',
                                           'value': {'abs': 'Haem absorbance (mOD)',
                                                     'abs_od': HAEM_ABS_OD_LABEL,
                                                     'delta_abs': '$\\Delta$A (mOD)',
                                                     'delta_abs_od': DELTA_A_OD_LABEL,
                                                     'default': 'Haem signal',
                                                     },
                                           },
             'RESPONSE_LINE_WIDTH': style['line_width'],
             'RESPONSE_POINT_SIZE': round((4.0 * style['line_width']) ** 2, 1),
             'RESPONSE_GROUP_DODGE': 0.12,
             'RESPONSE_MARKER_SIZE': round(4.0 * style['line_width'], 2),
             'RESPONSE_ERRORBAR_WIDTH': style['axes_line_width'],
             'RESPONSE_CAPSIZE': round(0.35 * unit, 2),
             'RESPONSE_TICK_FONT_SIZE': fonts['tick'],
             'RESPONSE_XTICK_FONT_SIZE': fonts['tick'],
             'RESPONSE_YLABEL_FONT_SIZE': fonts['label'],
             'RESPONSE_LEGEND_FONT_SIZE': fonts['tick'],
             'RESPONSE_LEGEND_LOCATION': 'best',
             'RESPONSE_TESTS': True,
             'RESPONSE_TEST_CORRECTION': 'holm',
             'RESPONSE_TEST_ALPHA': 0.05,
             'RESPONSE_TEST_FONT_SIZE': fonts['label'],
             'RESPONSE_TEST_BAR_TICK': round(0.4 * unit, 2),
             'RESPONSE_TEST_HEADROOM_PT': round(2.8 * unit, 1),
             }
            )


# ---- SOURCE SELECTOR -----------------------------------------------------------------
def source_selector(answers: dict, od_available: bool) -> tuple:
    """
    ---- Summary ----
    Main function to choose the OCR and haem data sources of the haem and OCR response
    figures from the answers.

    ---- Inputs ----
    answers : dict
        Terminal answers; uses ho_ocr_mode ('raw', 'od' or 'percent'), ho_haem_mode
        ('delta', 'abs', 'conc' or 'percent') and ho_per_od.
    od_available : bool
        True when the experiment has OD, volume and dilution factor.

    ---- Globals read ----
    None.

    ---- Outputs ----
    tuple
        (vo2_source, haem_source) as used by the averaging and plotting code, for
        example ('od', 'delta_abs_od'). OD sources are only chosen when od_available.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    pairs = {'conc': ('raw', 'od'),
             'abs': ('abs', 'abs_od'),
             'delta': ('delta_abs', 'delta_abs_od'),
             'percent': ('percent', 'percent'),
             }
    raw_haem, od_haem = pairs[answers['ho_haem_mode']]
    use_od = od_available and answers['ho_per_od']
    vo2_source = answers['ho_ocr_mode']
    if vo2_source == 'od' and not od_available:
        vo2_source = 'raw'
    return vo2_source, (od_haem if use_od else raw_haem)


# ---- TIME RESPONSE CONFIG BUILDER ----------------------------------------------------
def time_response_config_builder(cfg: Config, answers: dict, haem_names: list,) -> dict:
    """
    ---- Summary ----
    Main function to build the settings of the time response figure.

    ---- Inputs ----
    cfg : Config
        Figure style derived from the answers (config.py).
    answers : dict
        Terminal answers; uses tr_groups, tr_examples, tr_columns and tr_height.
    haem_names : list
        Haem names of the fit, used to colour the decomposition panels.

    ---- Globals read ----
    SAVE_FORMATS, OUTPUT_SUBFOLDER, DATA_SUBFOLDER.

    ---- Outputs ----
    dict
        Settings for time_response_figure_plotter, time_response_figure_saver and
        time_response_exporter.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    figure_size_calculator
    haem_colour_mapper
    """

    # ---- 1 Read the style and size ---------------------------------------------------
    style, fonts, unit, spec = cfg.STYLE, cfg.FONTS, cfg.UNIT, cfg.SPEC
    size = figure_size_calculator(spec, answers['tr_columns'], answers['tr_height'],)
    groups = tuple(answers['tr_groups'])

    # ---- 2 Build the configuration ---------------------------------------------------
    return {'SAVE_FIGURE': True,
            'SAVE_FORMATS': SAVE_FORMATS,
            'OUTPUT_SUBFOLDER': OUTPUT_SUBFOLDER,
            'DATA_SUBFOLDER': DATA_SUBFOLDER,
            'FILE_NAME': 'time_response_figure',
            'GROUP_ORDER': groups,
            'GROUP_TITLES': {group: group.capitalize() for group in groups},
            'TIME_LABEL_FORMAT': '{hours:g} hours',
            'EXAMPLES': tuple((group, hours) for group, hours in answers['tr_examples']
                              ),
            'EXAMPLE_TITLE_FORMAT': '{group}, {time}',
            'EXAMPLE_PLOT_OVERRIDES': {'EVENT_LABEL_ROTATION': 30,
                                       'PLOT_VO2': False,
                                       'HAEM_Y_MAX_TICKS': 2,
                                       'PANEL_HEIGHT_RATIOS': {'oxygen': 2,
                                                               'vo2': 3,
                                                               'haem': 5,
                                                               },
                                       },
            'FIGURE_SIZE': size,
            'FIGURE_DPI': cfg.FIGURE_DPI,
            'TIGHT_BBOX': False,
            'FIGURE_TITLE': None,
            'SUPTITLE_FONT_SIZE': fonts['title'],
            'UNIT_PT': unit,
            'EDGE_PAD_PT': style['edge_pad'],
            'TITLE_GAP_PT': style['title_gap'],
            'THIN_LINE_WIDTH': style['thin_line_width'],
            'HEIGHT_RATIOS': (1.5, 1.5, 2.6),
            'WIDTH_RATIOS': (1, 1),
            'PANEL_LETTERS': True,
            'PANEL_LETTER_CASE': spec['panel_letter_case'],
            'PANEL_LETTER_FONT_SIZE': fonts['panel_letter'],
            'WATERFALL_OFFSET': None,
            'X_MIN': None,
            'X_MAX': None,
            'ALIGN_MIN': 540,
            'ALIGN_MAX': 575,
            'WATERFALL_SHARED_BASELINE': False,
            'WATERFALL_BASELINE_X_MIN': 415,
            'WATERFALL_BASELINE_X_MAX': 670,
            'WATERFALL_BASELINE_DEGREE': 1,
            'WATERFALL_Y_LABEL': 'Offset Δ\nattenuation',
            'WATERFALL_WIDTH_FRACTION': 0.25,
            'HAEM_WINDOW_HALF_WIDTH_NM': 2.5,
            'HAEM_WINDOW_ALPHA': 0.15,
            'WATERFALL_LEGEND_LOCATION': 'lower right',
            'WATERFALL_LEGEND_COLUMNS': 1,
            'WATERFALL_LEGEND_OUTSIDE': True,
            'WATERFALL_LEGEND_ON': 'first',
            'WATERFALL_SHARE_X_AXIS': True,
            'DECOMPOSITION_Y_LABEL': 'Δ attenuation',
            'DECOMPOSITION_LEGEND_LOCATION': 'upper right',
            'HAEM_COLOURS': haem_colour_mapper(haem_names),
            'TICK_FONT_SIZE': fonts['tick'],
            'AXIS_LABEL_FONT_SIZE': fonts['label'],
            'TITLE_FONT_SIZE': fonts['title'],
            'TITLE_WEIGHT': 'bold',
            'TITLE_ALIGNMENT': 'left',
            'LINE_WIDTH': style['line_width'],
            'TICK_DIRECTION': 'in',
            'LEGEND_FONT_SIZE': fonts['tick'],
            'LEGEND_COLUMNS': 1,
            'LEGEND_FRAME': True,
            }
