# -*- coding: utf-8 -*-
"""Settings for convert_chamber_data.py.

The answers given in the terminal (see convert_chamber_data.py) are turned into the same
figure style, sizes and plot settings that
the original OCR/haem scripts use. Nothing here needs editing for normal use; the
journal sizes and the default look can be changed below.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
from types import SimpleNamespace
from typing import Dict, List, Optional, Tuple

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.figure_layout import (figure_size_calculator,
                                        figure_style_builder,
                                        figure_style_checker,
                                        )
from utils_shared.helpers import name_simplifier


# ---- CONSTANTS -----------------------------------------------------------------------
DEFAULT_ANSWERS = {
    # skipped when baselines, % ranges and y-axis limits are worked out (the data is
    # still plotted)
    'ignore_first_minutes': 5.0,
    # the same at the end of the recording
    'ignore_last_minutes': 0.0,
    'decompose': False,
    'fit_file': None,
    'decomposition_dataset': 'Cyt',
    'normalise_od': False,
    'averaging': False,
    'window_minutes': 2.0,
    'gap_minutes': 0.5,
    'final_gap_minutes': 0.5,
    'plot_o2': True,
    'plot_ocr': True,
    # "raw", "od" or "percent"
    'ocr_mode': 'od',
    # event label rotation in degrees: 0 = horizontal, 90 = vertical
    'event_label_angle': 45,
    'plot_haems': False,
    'haems': [],
    # "abs", "delta", "conc" or "percent"
    'haem_mode': 'delta',
    # divide the haem values (not "percent") by OD x volume x dilution when OD scaling
    # is on
    'haem_per_od': True,
    # Figure sizes. Each figure has its own journal, width (columns) and height
    # (fraction of a page).
    # The *_size_mode answer is "default" (the journal question was answered None:
    # Nature and the size below) or "custom".
    'journal': 'nature',
    'columns': 1,
    'height': 0.5,
    'size_mode': 'default',
    'plot_comparison': False,
    'comparison_journal': 'nature',
    'comparison_columns': 1.5,
    'comparison_height': 0.5,
    'comparison_size_mode': 'default',
    'plot_exemplar': False,
    'ho_exemplar_run': 1,
    'ex_journal': 'nature',
    'ho_ex_columns': 1.5,
    'ho_ex_height': 0.75,
    'ex_size_mode': 'default',
    'export_full': False,
    'export_spectra': False,
    # special figures (see utils_custom): time response, and haem and OCR response
    'plot_time_response': False,
    'plot_haem_ocr': False,
    'tr_groups': ['knockdown', 'control'],
    'tr_window_minutes': 1.0,
    'tr_gap_minutes': 0.5,
    'tr_final_gap_minutes': 0.5,
    'tr_examples': [],
    'tr_journal': 'nature',
    'tr_columns': 2,
    'tr_height': 0.75,
    'tr_size_mode': 'default',
    'ho_haem_mode': 'delta',
    'ho_per_od': True,
    'ho_metric': 'delta',
    'ho_haems': [],
    'ho_ocr_mode': 'od',
    'ho_window_minutes': 2.0,
    'ho_gap_minutes': 0.5,
    'ho_final_gap_minutes': 0.5,
    'ho_journal': 'nature',
    'ho_pub_columns': 2,
    'ho_pub_height': 0.75,
    'ho_size_mode': 'default',
}
TRANSMISSION_MODE = 'fraction'  # "fraction", "percentage" or "absorbance"
DEGREE_OF_SCATTER = 1
HAEM_FACTOR = 1_000_000
DELTA_ABS_WINDOW_SECONDS = 30
PERCENT_AVERAGE_WINDOW_SECONDS = 30
# axis-label size. Tick labels, legends and event labels are 1 pt smaller and titles 1
# pt larger; panel letters follow the journal.
BASE_FONT_PT = 6
# all paddings and gaps: 1.0 = default, 1.2 = 20 % looser, 0.8 = 20 % tighter
SPACING = 1.0
# data lines; axes, reference and event lines, error bars and markers are scaled from it
LINE_WIDTH_PT = 0.75
# Plot source names (see utils_shared.schema): chosen in the terminal as a "kind" and,
# when OD scaling is on, "per OD".
HAEM_SOURCE_BY_MODE = {'conc': ('raw', 'od'),
                       'abs': ('abs', 'abs_od'),
                       'delta': ('delta_abs', 'delta_abs_od'),
                       'percent': ('percent', 'percent'),
                       }
OCR_SOURCES = ('raw', 'od', 'percent')
FALLBACK_WITHOUT_OD = {'od': 'raw', 'abs_od': 'abs', 'delta_abs_od': 'delta_abs'}
HAEM_COLOURS = {'cytc1': '#ff3636',
                'cytcc': '#ff3636',
                'cytbh': '#3131ff',
                'cytbl': '#0d0d87',
                'cyta605': '#00b050',
                'cytb557': '#00b0db',
                }
EXTRA_COLOURS = ['#e69f00',
                 '#cc79a7',
                 '#56b4e9',
                 '#009e73',
                 '#d55e00',
                 '#0072b2',
                 '#f0e442',
                 '#7f7f7f',
                 ]
# What each journal asks for. Only the Nature numbers were checked against the journal's
# own figure guide (research-figure-guide.nature.com;
# its 170 mm height is the maximum when the legend sits under the figure, 247 mm is the
# full page). The PNAS widths are from the PNAS
# template; every other number (marked "check") came from secondary sources: confirm it
# in the journal's author instructions before submitting.
JOURNAL_SPECS = {
    'nature': {
        'widths_mm': {1: 89, 1.5: 120, 2: 183},
        'page_height_mm': 170,
        'max_height_mm': 170,
        'font_min_pt': 5,
        'font_max_pt': 7,
        # 8 pt bold lowercase a, b, c
        'panel_letter_pt': 8,
        'panel_letter_case': 'lower',
        'font_family': ['Arial', 'Helvetica'],
        'dpi': 300,
    },
    # check: sources disagree on the widths
    'science': {
        'widths_mm': {1: 55, 1.5: 120, 2: 175},
        'page_height_mm': 230,
        'max_height_mm': 230,
        'font_min_pt': 5,
        'font_max_pt': 8,
        'panel_letter_pt': 8,
        'panel_letter_case': 'upper',
        'font_family': ['Arial', 'Helvetica'],
        'dpi': 300,
    },
    # check: widths 85 / 114 / 174 mm are widely quoted; heights and fonts are not
    # confirmed
    'cell': {
        'widths_mm': {1: 85, 1.5: 114, 2: 174},
        'page_height_mm': 225,
        'max_height_mm': 225,
        'font_min_pt': 6,
        'font_max_pt': 8,
        'panel_letter_pt': 8,
        'panel_letter_case': 'upper',
        'font_family': ['Arial', 'Helvetica'],
        'dpi': 300,
    },
    # widths from the PNAS template; check height and fonts
    'pnas': {
        'widths_mm': {1: 87, 1.5: 114, 2: 178},
        'page_height_mm': 225,
        'max_height_mm': 225,
        'font_min_pt': 6,
        'font_max_pt': 8,
        'panel_letter_pt': 8,
        'panel_letter_case': 'upper',
        'font_family': ['Arial', 'Helvetica'],
        'dpi': 300,
    },
}


# ---- CONFIG --------------------------------------------------------------------------
class Config:
    """
    Everything derived from the answers: figure style and sizes, matplotlib settings,
    and the settings of the individual plot.
    """

    # ---- __INIT__ --------------------------------------------------------------------
    def __init__(self, answers: dict) -> None:
        """
        ---- Summary ----
        Method to build the figure style, matplotlib settings and sizes of one figure
        from the terminal answers.

        ---- Inputs ----
        answers : dict
            Terminal answers; missing keys are filled from DEFAULT_ANSWERS.

        ---- Globals read ----
        DEFAULT_ANSWERS, JOURNAL_SPECS, BASE_FONT_PT, SPACING, LINE_WIDTH_PT (module
        constants); make_style, check_style, figure_size_inches (imported).

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Sets the answers, SPEC, STYLE, FONTS, UNIT, FIGURE_SIZE, FIGURE_DPI,
        STYLE_WARNINGS and RC_PARAMS attributes on the instance.

        ---- Equations ----
        None.

        ---- Helpers ----
        figure_size_calculator
        figure_style_builder
        figure_style_checker
        """

        # ---- 1 Store the answers -----------------------------------------------------
        self.answers = dict(DEFAULT_ANSWERS, **answers)
        a = self.answers

        # ---- 2 Build the figure style ------------------------------------------------
        self.SPEC = JOURNAL_SPECS[a['journal']]
        self.STYLE = figure_style_builder(self.SPEC,
                                          BASE_FONT_PT,
                                          SPACING,
                                          LINE_WIDTH_PT,
                                          )
        self.FONTS, self.UNIT = self.STYLE['fonts'], self.STYLE['unit']
        self.FIGURE_SIZE = figure_size_calculator(self.SPEC, a['columns'], a['height'])
        self.FIGURE_DPI = self.SPEC['dpi']
        self.STYLE_WARNINGS = figure_style_checker(a['journal'],
                                                   self.SPEC,
                                                   self.FONTS,
                                                   self.FIGURE_SIZE,
                                                   'individual figure: ',
                                                   )

        # ---- 3 Build the matplotlib settings -----------------------------------------
        style, fonts, spec = self.STYLE, self.FONTS, self.SPEC
        self.RC_PARAMS = {
            'font.family': 'sans-serif',
            # the first one installed is used
            'font.sans-serif': spec['font_family'] + ['Liberation Sans', 'DejaVu Sans'],
            'font.size': fonts['tick'],
            'axes.labelsize': fonts['label'],
            'axes.titlesize': fonts['title'],
            'axes.titlepad': style['title_pad'],
            'axes.labelpad': style['label_pad'],
            'lines.linewidth': style['line_width'],
            'axes.linewidth': style['axes_line_width'],
            'xtick.major.width': style['axes_line_width'],
            'ytick.major.width': style['axes_line_width'],
            'xtick.major.size': style['tick_length'],
            'ytick.major.size': style['tick_length'],
            'xtick.major.pad': style['tick_pad'],
            'ytick.major.pad': style['tick_pad'],
            'legend.fontsize': fonts['tick'],
            'legend.handlelength': 1.6,
            'legend.borderpad': 0.3,
            'legend.labelspacing': 0.25,
            'legend.handletextpad': 0.5,
            'legend.borderaxespad': 0.4,
            'legend.edgecolor': '0.25',
            'legend.fancybox': False,
            'legend.framealpha': 0.9,
            # keeps text as editable text in the SVG
            'svg.fonttype': 'none',
            'pdf.fonttype': 42,
        }

    # ---- which data is plotted and averaged ------------------------------------------

    # ---- SOURCE CHOOSER --------------------------------------------------------------
    def source_chooser(self, od_available: bool = True) -> Tuple[str, Optional[str]]:
        """
        ---- Summary ----
        Method to choose the OCR source and haem source used for the plot and the event
        averages.

        ---- Inputs ----
        od_available : bool
            True when the experiment has OD, volume and dilution factor.

        ---- Globals read ----
        FALLBACK_WITHOUT_OD, HAEM_SOURCE_BY_MODE (module constants).

        ---- Outputs ----
        Tuple[str, Optional[str]]
            (OCR source, haem source), for example ("od", "delta_abs_od"). The haem
            source is None when nothing is decomposed; OD sources fall back to raw ones
            without OD.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        # ---- 1 Choose the VO2 source -------------------------------------------------
        a = self.answers
        use_od = a['normalise_od'] and od_available
        vo2 = a['ocr_mode'] if a['plot_ocr'] else ('od' if use_od else 'raw')
        if vo2 == 'od' and not use_od:
            vo2 = FALLBACK_WITHOUT_OD['od']

        # ---- 2 Choose the haem source ------------------------------------------------
        haem = None
        if a['decompose']:
            haem_mode = a['haem_mode'] if a['plot_haems'] else 'delta'
            per_od_pair = HAEM_SOURCE_BY_MODE[haem_mode]
            haem = (per_od_pair[1]
                    if (use_od and a.get('haem_per_od', True))
                    else per_od_pair[0]
                    )
        return vo2, haem

    # ---- PERCENT NEED CHECKER --------------------------------------------------------
    def percent_need_checker(self) -> Tuple[bool, bool]:
        """
        ---- Summary ----
        Method to say whether the percent-of-range versions of the OCR and haem data
        have to be calculated.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        Tuple[bool, bool]
            (OCR percent needed, haem percent needed).

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        a = self.answers
        return (a['plot_ocr'] and a['ocr_mode'] == 'percent',
                a['decompose'] and a['plot_haems'] and a['haem_mode'] == 'percent',
                )

    # ---- the settings of the individual-experiment plot (same keys and defaults as the
    # original PLOT_CONFIG) ----

    # ---- PLOT CONFIG BUILDER ---------------------------------------------------------
    def plot_config_builder(self,
                            vo2_source: str,
                            haem_source: Optional[str],
                            ignore_first: Optional[float] = None,
                            ignore_last: Optional[float] = None,
                            ) -> dict:
        """
        ---- Summary ----
        Method to build the settings dictionary of one individual-experiment figure.

        ---- Inputs ----
        vo2_source : str
            OCR source plotted: "raw", "od" or "percent".
        haem_source : Optional[str]
            Haem source plotted, for example "delta_abs_od", or None for no haem panels.
        ignore_first : Optional[float]
            Minutes ignored at the start for the axis limits; None uses the answers.
        ignore_last : Optional[float]
            Minutes ignored at the end for the axis limits; None uses the answers.

        ---- Globals read ----
        haem_colours (module function); the style, font and size attributes of the
        instance.

        ---- Outputs ----
        dict
            Plot settings in the format used by plot_experiment.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        haem_colour_mapper
        """

        # ---- 1 Gather the settings ---------------------------------------------------
        a, style, fonts = self.answers, self.STYLE, self.FONTS
        haems = (list(a['haems'])
                 if (a['decompose'] and a['plot_haems'] and haem_source)
                 else []
                 )

        # ---- 2 Build the plot configuration ------------------------------------------
        return {
            # Output
            'SHOW_INDIVIDUAL_FIGURES': False,
            'SAVE_FIGURES': True,
            'FIGURE_SIZE': self.FIGURE_SIZE,
            'FIGURE_DPI': self.FIGURE_DPI,
            'TIGHT_BBOX': False,
            'FIT_MARGINS': True,
            'LAYOUT_PAD_PT': style['edge_pad'],
            'TITLE_GAP_PT': style['title_gap'],
            'TITLE_PAD_PT': style['title_pad'],
            'HIDE_TOUCHING_TICK_LABELS': True,
            'FIGURE_TITLE': '{experiment_name}',
            'TITLE_STYLE': 'watermark',
            'WATERMARK_FONT_SIZE': fonts['tick'],
            'WATERMARK_COLOUR': '0.35',
            'WATERMARK_ALPHA': 0.5,
            'TITLE_FONT_SIZE': fonts['title'],
            'LABEL_FONT_SIZE': fonts['label'],
            'SUBPLOT_HSPACE': 0.0,
            'PANEL_HEIGHT_RATIOS': {'oxygen': 2, 'vo2': 2, 'haem': 5},
            'EQUAL_PANEL_HEIGHTS': True,
            # Time axis
            'TIME_AXIS_LABEL': 'Time (minutes)',
            'TIME_AXIS_LABEL_PAD': style['label_pad'],
            'X_MIN': None,
            'X_MAX': None,
            'X_NUM_TICKS': None,
            'Y_SCALE_IGNORE_FIRST_MINUTES': (a['ignore_first_minutes']
                                             if ignore_first is None
                                             else ignore_first
                                             ),
            'Y_SCALE_IGNORE_LAST_MINUTES': (a['ignore_last_minutes']
                                            if ignore_last is None
                                            else ignore_last
                                            ),
            'Y_LABEL_PAD': style['label_pad'],
            'ALIGN_Y_LABELS': True,
            'TICK_FONT_SIZE': fonts['tick'],
            'LINE_WIDTH': style['line_width'],
            'AXES_TOP_SPINE': False,
            'AXES_RIGHT_SPINE': False,
            # Events
            'PLOT_EVENTS': True,
            'EVENT_LINE_STYLE': '--',
            'EVENT_LINE_WIDTH': style['thin_line_width'],
            'EVENT_LINE_COLOUR': '0.35',
            'EVENT_LINE_ALPHA': 0.8,
            'EVENT_LABELS': True,
            'EVENT_LABELS_ON_TOP': True,
            'EVENT_LABEL_ROTATION': a['event_label_angle'],
            'EVENT_LABEL_FONTSIZE': fonts['tick'],
            'EVENT_LABEL_ANCHOR': 'start',
            'EVENT_LABEL_OFFSET': style['event_label_offset'],
            # Averaging windows
            'PLOT_AVERAGING_WINDOWS': a['averaging'],
            'AVERAGING_WINDOW_COLOUR': '#4C9BE8',
            'AVERAGING_WINDOW_ALPHA': 0.18,
            'AVERAGING_WINDOW_EDGE_COLOUR': '#2878B5',
            'AVERAGING_WINDOW_EDGE_LINE_WIDTH': style['thin_line_width'],
            'AVERAGING_WINDOW_LABEL_FORMAT': '',
            'AVERAGING_WINDOW_LABEL_FONT_SIZE': fonts['tick'],
            # Oxygen panel
            'PLOT_SET_AND_MEASURED_O2': a['plot_o2'],
            'O2_PANEL_TITLE': 'Oxygen concentration',
            'O2_AXIS_LABEL': '[O$_2$](µM)',
            'SET_O2_LABEL': 'Set [O$_2$]',
            'MEASURED_O2_LABEL': 'Measured [O$_2$]',
            'SET_O2_COLOUR': None,
            'MEASURED_O2_COLOUR': None,
            'SET_O2_LINE_STYLE': '--',
            'MEASURED_O2_LINE_STYLE': '-',
            'O2_Y_MIN': None,
            'O2_Y_MAX': None,
            'O2_Y_NUM_TICKS': None,
            # VO2 panel
            'PLOT_VO2': a['plot_ocr'],
            'VO2_PANEL_TITLE': 'Oxygen consumption',
            'VO2_LABEL': 'VO2',
            'VO2_COLOUR': None,
            'VO2_PLOT_VALUES': vo2_source,
            'VO2_AXIS_LABELS': {'raw': 'OCR (µM min$^{-1}$)',
                                'od': "OCR (µM\nmin$^{-1}$ OD$^{-1}$)",
                                'percent': 'OCR (% of range)',
                                },
            'VO2_Y_MIN': 0,
            'VO2_Y_MAX': None,
            'VO2_Y_NUM_TICKS': None,
            'VO2_Y_SPIKE_WINDOW_FRACTION': 0.02,
            'VO2_Y_HEADROOM': 0.05,
            # Haem panels (one per selected haem)
            'HAEM_PLOT_VALUES': haem_source,
            'HAEM_AXIS_LABELS': {'raw': 'Haem concentration',
                                 'od': 'Haem concentration (/OD)',
                                 'percent': 'Oxidised haem (%)',
                                 'abs': 'Haem absorbance (mOD)',
                                 'abs_od': 'Haem absorbance (mOD OD$^{-1}$)',
                                 'delta_abs': 'ΔA (mOD)',
                                 'delta_abs_od': 'ΔA (mOD OD$^{-1}$)',
                                 },
            'HAEM_Y_MIN': None,
            'HAEM_Y_MAX': None,
            'HAEM_Y_NUM_TICKS': None,
            'HAEM_SPAN_LABEL_PAD': style['label_pad'],
            'HAEM_PANELS': [{'label': '', 'haems': [name]} for name in haems],
            'HAEM_COLOURS': haem_colour_mapper(haems),
            # Legend
            'SHOW_LEGENDS': {'oxygen': True, 'vo2': False, 'haem': True},
            'LEGEND_FONT_SIZE': fonts['tick'],
            'LEGEND_LOCATION': 'upper right',
            'LEGEND_COLUMNS': 1,
            'LEGEND_FRAME': True,
            'LEGEND_FRAME_LINE_WIDTH': style['thin_line_width'],
            'HAEM_LEGEND_TEXT_ONLY': True,
        }


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- HAEM COLOUR MAPPER --------------------------------------------------------------
def haem_colour_mapper(names: List[str]) -> Dict[str, str]:
    """
    ---- Summary ----
    Main function to give each haem a plot colour: the original colour for the usual
    haems, otherwise the next unused extra colour.

    ---- Inputs ----
    names : List[str]
        Haem names as written in the fit file.

    ---- Globals read ----
    HAEM_COLOURS, EXTRA_COLOURS (module constants).

    ---- Outputs ----
    Dict[str, str]
        {haem name: hex colour}.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    name_simplifier
    """

    colours, spare = {}, iter(EXTRA_COLOURS * 3)
    for name in names:
        colours[name] = HAEM_COLOURS.get(name_simplifier(name)) or next(spare)
    return colours
