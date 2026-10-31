# . - Function List

- **Project:** .
- **Version:** V2.3
- **Date:** 31/10/2026

## Contents

- [`config.py`](#configpy)
    - [`Config`](#config)
    - [`haem_colour_mapper`](#haem_colour_mapper)
- [`main.py`](#mainpy)
    - [`comparison_maker`](#comparison_maker)
    - [`everything_asker`](#everything_asker)
    - [`experiment_processor`](#experiment_processor)
    - [`last_answers_loader`](#last_answers_loader)
    - [`last_answers_saver`](#last_answers_saver)
    - [`program_runner`](#program_runner)
    - [`main`](#main)
    - [`special_figures_maker`](#special_figures_maker)
- [`utils_custom/custom_config.py`](#utils_customcustom_configpy)
    - [`exemplar_config_builder`](#exemplar_config_builder)
    - [`haem_labeller`](#haem_labeller)
    - [`individual_config_builder`](#individual_config_builder)
    - [`ocr_and_haem_response_config_builder`](#ocr_and_haem_response_config_builder)
    - [`source_selector`](#source_selector)
    - [`time_response_config_builder`](#time_response_config_builder)
- [`utils_custom/custom_figure_saver.py`](#utils_customcustom_figure_saverpy)
    - [`custom_figure_saver`](#custom_figure_saver)
- [`utils_custom/custom_questions.py`](#utils_customcustom_questionspy)
    - [`_example_pair_maker`](#_example_pair_maker)
    - [`_haem_ocr_asker`](#_haem_ocr_asker)
    - [`_saved_example_finder`](#_saved_example_finder)
    - [`_time_response_asker`](#_time_response_asker)
    - [`_window_ensurer`](#_window_ensurer)
    - [`summary_figure_asker`](#summary_figure_asker)
- [`utils_custom/custom_runner.py`](#utils_customcustom_runnerpy)
    - [`_ocr_and_haem_response_preparer`](#_ocr_and_haem_response_preparer)
    - [`_time_response_preparer`](#_time_response_preparer)
    - [`exemplar_runner`](#exemplar_runner)
    - [`experiment_preparer`](#experiment_preparer)
    - [`ocr_and_haem_response_runner`](#ocr_and_haem_response_runner)
    - [`time_response_runner`](#time_response_runner)
- [`utils_custom/exemplar_plotter.py`](#utils_customexemplar_plotterpy)
    - [`_crop_start_finder`](#_crop_start_finder)
    - [`_exemplar_gap_calculator`](#_exemplar_gap_calculator)
    - [`_exemplar_plotter`](#_exemplar_plotter)
    - [`_exemplar_selector`](#_exemplar_selector)
    - [`_experiment_cropper`](#_experiment_cropper)
    - [`exemplar_figure_plotter`](#exemplar_figure_plotter)
- [`utils_custom/ocr_and_haem_response_exporter.py`](#utils_customocr_and_haem_response_exporterpy)
    - [`_baseline_sheet_writer`](#_baseline_sheet_writer)
    - [`_condition_sheet_writer`](#_condition_sheet_writer)
    - [`_measurement_table_writer`](#_measurement_table_writer)
    - [`_statistics_writer`](#_statistics_writer)
    - [`_test_row_writer`](#_test_row_writer)
    - [`_tests_sheet_writer`](#_tests_sheet_writer)
    - [`ocr_and_haem_response_exporter`](#ocr_and_haem_response_exporter)
- [`utils_custom/ocr_and_haem_response_plotter.py`](#utils_customocr_and_haem_response_plotterpy)
    - [`_axes_styler`](#_axes_styler)
    - [`_baseline_bar_plotter`](#_baseline_bar_plotter)
    - [`_block_gap_calculator`](#_block_gap_calculator)
    - [`_column_chooser`](#_column_chooser)
    - [`_condition_indexer`](#_condition_indexer)
    - [`_finite_run_filter`](#_finite_run_filter)
    - [`_haem_block_plotter`](#_haem_block_plotter)
    - [`_haem_label_finder`](#_haem_label_finder)
    - [`_haem_label_pad_calculator`](#_haem_label_pad_calculator)
    - [`_haem_row_selector`](#_haem_row_selector)
    - [`_haem_source_finder`](#_haem_source_finder)
    - [`_layout_validator`](#_layout_validator)
    - [`_legend_handle_builder`](#_legend_handle_builder)
    - [`_mean_ylim_setter`](#_mean_ylim_setter)
    - [`_measurement_finder`](#_measurement_finder)
    - [`_metric_field_selector`](#_metric_field_selector)
    - [`_ocr_block_plotter`](#_ocr_block_plotter)
    - [`_offset_transformer`](#_offset_transformer)
    - [`_outside_bar_drawer`](#_outside_bar_drawer)
    - [`_p_value_adjuster`](#_p_value_adjuster)
    - [`_panel_labeller`](#_panel_labeller)
    - [`_reference_level_finder`](#_reference_level_finder)
    - [`_reference_selector`](#_reference_selector)
    - [`_response_axes_preparer`](#_response_axes_preparer)
    - [`_response_metric_checker`](#_response_metric_checker)
    - [`_response_series_drawer`](#_response_series_drawer)
    - [`_response_window_tester`](#_response_window_tester)
    - [`_row_ylim_sharer`](#_row_ylim_sharer)
    - [`_significance_bar_drawer`](#_significance_bar_drawer)
    - [`_significance_formatter`](#_significance_formatter)
    - [`_test_bar_drawer`](#_test_bar_drawer)
    - [`_tick_label_builder`](#_tick_label_builder)
    - [`_window_orderer`](#_window_orderer)
    - [`ocr_and_haem_response_figure_plotter`](#ocr_and_haem_response_figure_plotter)
- [`utils_custom/publication_plotter.py`](#utils_custompublication_plotterpy)
    - [`_axes_styler`](#_axes_styler)
    - [`_baseline_bar_plotter`](#_baseline_bar_plotter)
    - [`_block_gap_calculator`](#_block_gap_calculator)
    - [`_column_chooser`](#_column_chooser)
    - [`_condition_indexer`](#_condition_indexer)
    - [`_crop_start_finder`](#_crop_start_finder)
    - [`_exemplar_gap_calculator`](#_exemplar_gap_calculator)
    - [`_exemplar_plotter`](#_exemplar_plotter)
    - [`_exemplar_selector`](#_exemplar_selector)
    - [`_experiment_classifier`](#_experiment_classifier)
    - [`_experiment_cropper`](#_experiment_cropper)
    - [`_figure_finisher`](#_figure_finisher)
    - [`_haem_block_plotter`](#_haem_block_plotter)
    - [`_haem_label_finder`](#_haem_label_finder)
    - [`_haem_label_pad_calculator`](#_haem_label_pad_calculator)
    - [`_haem_row_selector`](#_haem_row_selector)
    - [`_haem_source_finder`](#_haem_source_finder)
    - [`_layout_validator`](#_layout_validator)
    - [`_legend_handle_builder`](#_legend_handle_builder)
    - [`_mean_ylim_setter`](#_mean_ylim_setter)
    - [`_measurement_finder`](#_measurement_finder)
    - [`_metric_field_selector`](#_metric_field_selector)
    - [`_ocr_block_plotter`](#_ocr_block_plotter)
    - [`_outside_bar_drawer`](#_outside_bar_drawer)
    - [`_p_value_adjuster`](#_p_value_adjuster)
    - [`_reference_level_finder`](#_reference_level_finder)
    - [`_reference_selector`](#_reference_selector)
    - [`_response_axes_preparer`](#_response_axes_preparer)
    - [`_response_metric_checker`](#_response_metric_checker)
    - [`_response_series_drawer`](#_response_series_drawer)
    - [`_response_window_tester`](#_response_window_tester)
    - [`_row_ylim_sharer`](#_row_ylim_sharer)
    - [`_significance_bar_drawer`](#_significance_bar_drawer)
    - [`_significance_formatter`](#_significance_formatter)
    - [`_test_bar_drawer`](#_test_bar_drawer)
    - [`_tick_label_builder`](#_tick_label_builder)
    - [`_window_orderer`](#_window_orderer)
    - [`exemplar_figure_plotter`](#exemplar_figure_plotter)
    - [`publication_figure_plotter`](#publication_figure_plotter)
    - [`publication_figure_saver`](#publication_figure_saver)
- [`utils_custom/run_namer.py`](#utils_customrun_namerpy)
    - [`_group_matcher`](#_group_matcher)
    - [`_natural_sorter`](#_natural_sorter)
    - [`_order_sorter`](#_order_sorter)
    - [`condition_classifier`](#condition_classifier)
    - [`condition_grouper`](#condition_grouper)
    - [`experiment_classifier`](#experiment_classifier)
    - [`group_assigner`](#group_assigner)
    - [`hours_parser`](#hours_parser)
    - [`run_name_lister`](#run_name_lister)
    - [`run_name_parser`](#run_name_parser)
- [`utils_custom/spectral_difference.py`](#utils_customspectral_differencepy)
    - [`difference_spectrum_calculator`](#difference_spectrum_calculator)
    - [`difference_spectrum_decomposer`](#difference_spectrum_decomposer)
    - [`spectral_averager`](#spectral_averager)
    - [`window_definer`](#window_definer)
- [`utils_custom/time_response_exporter.py`](#utils_customtime_response_exporterpy)
    - [`_difference_sheet_writer`](#_difference_sheet_writer)
    - [`_haem_sheet_writer`](#_haem_sheet_writer)
    - [`_picks_sheet_writer`](#_picks_sheet_writer)
    - [`_waterfall_sheet_writer`](#_waterfall_sheet_writer)
    - [`time_response_exporter`](#time_response_exporter)
- [`utils_custom/time_response_plotter.py`](#utils_customtime_response_plotterpy)
    - [`_event_label_height_calculator`](#_event_label_height_calculator)
    - [`_example_finder`](#_example_finder)
    - [`_example_viewer`](#_example_viewer)
    - [`_haem_scale_sharer`](#_haem_scale_sharer)
    - [`_haem_window_drawer`](#_haem_window_drawer)
    - [`_legend_drawer`](#_legend_drawer)
    - [`_time_axes_styler`](#_time_axes_styler)
    - [`_time_gap_calculator`](#_time_gap_calculator)
    - [`_title_styler`](#_title_styler)
    - [`decomposition_plotter`](#decomposition_plotter)
    - [`group_collector`](#group_collector)
    - [`shared_baseline_subtracter`](#shared_baseline_subtracter)
    - [`time_label_builder`](#time_label_builder)
    - [`time_response_figure_plotter`](#time_response_figure_plotter)
    - [`waterfall_plotter`](#waterfall_plotter)
- [`utils_custom/triplicate_averager.py`](#utils_customtriplicate_averagerpy)
    - [`_run_summariser`](#_run_summariser)
    - [`_run_value_getter`](#_run_value_getter)
    - [`_window_sorter`](#_window_sorter)
    - [`triplicate_averager`](#triplicate_averager)
- [`utils_custom/triplicate_exporter.py`](#utils_customtriplicate_exporterpy)
    - [`triplicate_exporter`](#triplicate_exporter)
- [`utils_custom/workbook_helpers.py`](#utils_customworkbook_helperspy)
    - [`formula_writer`](#formula_writer)
    - [`number_writer`](#number_writer)
    - [`workbook_formats_builder`](#workbook_formats_builder)
- [`utils_shared/attenuation.py`](#utils_sharedattenuationpy)
    - [`attenuation_converter`](#attenuation_converter)
    - [`experiment_attenuation_adder`](#experiment_attenuation_adder)
- [`utils_shared/averaging.py`](#utils_sharedaveragingpy)
    - [`_baseline_change_adder`](#_baseline_change_adder)
    - [`experiment_averages_calculator`](#experiment_averages_calculator)
    - [`window_statistics_calculator`](#window_statistics_calculator)
- [`utils_shared/comparison_plotter.py`](#utils_sharedcomparison_plotterpy)
    - [`_overhang_calculator`](#_overhang_calculator)
    - [`_renderer_getter`](#_renderer_getter)
    - [`comparison_figure_plotter`](#comparison_figure_plotter)
- [`utils_shared/experiment_processing.py`](#utils_sharedexperiment_processingpy)
    - [`event_settings_merger`](#event_settings_merger)
    - [`experiment_data_processor`](#experiment_data_processor)
- [`utils_shared/figure_layout.py`](#utils_sharedfigure_layoutpy)
    - [`_renderer_getter`](#_renderer_getter)
    - [`figure_canvas_fitter`](#figure_canvas_fitter)
    - [`figure_finisher`](#figure_finisher)
    - [`figure_size_calculator`](#figure_size_calculator)
    - [`figure_style_builder`](#figure_style_builder)
    - [`figure_style_checker`](#figure_style_checker)
    - [`gap_space_calculator`](#gap_space_calculator)
    - [`panel_letter_adder`](#panel_letter_adder)
    - [`stack_legend_drawer`](#stack_legend_drawer)
    - [`text_extent_calculator`](#text_extent_calculator)
- [`utils_shared/helpers.py`](#utils_sharedhelperspy)
    - [`concentration_formatter`](#concentration_formatter)
    - [`excel_sheet_namer`](#excel_sheet_namer)
    - [`figure_saver`](#figure_saver)
    - [`file_name_sanitiser`](#file_name_sanitiser)
    - [`name_simplifier`](#name_simplifier)
- [`utils_shared/individual_experiment_exporter.py`](#utils_sharedindividual_experiment_exporterpy)
    - [`_frame_writer`](#_frame_writer)
    - [`_name_lister`](#_name_lister)
    - [`_spectral_csv_exporter`](#_spectral_csv_exporter)
    - [`averages_table_builder`](#averages_table_builder)
    - [`experiment_workbook_exporter`](#experiment_workbook_exporter)
    - [`saved_settings_reader`](#saved_settings_reader)
    - [`workbook_path_builder`](#workbook_path_builder)
- [`utils_shared/individual_experiment_plotter.py`](#utils_sharedindividual_experiment_plotterpy)
    - [`_HideTopTickLabels`](#_hidetopticklabels)
    - [`_axes_legend_drawer`](#_axes_legend_drawer)
    - [`_first_series_getter`](#_first_series_getter)
    - [`_haem_data_selector`](#_haem_data_selector)
    - [`_height_ratio_calculator`](#_height_ratio_calculator)
    - [`_min_ticks_setter`](#_min_ticks_setter)
    - [`_panel_builder`](#_panel_builder)
    - [`_vo2_ymax_calculator`](#_vo2_ymax_calculator)
    - [`_window_drawer`](#_window_drawer)
    - [`_window_label_builder`](#_window_label_builder)
    - [`_ylim_calculator`](#_ylim_calculator)
    - [`experiment_drawer`](#experiment_drawer)
    - [`experiment_plotter`](#experiment_plotter)
    - [`experiment_title_builder`](#experiment_title_builder)
    - [`watermark_style_builder`](#watermark_style_builder)
- [`utils_shared/normalisation.py`](#utils_sharednormalisationpy)
    - [`_frame_normaliser`](#_frame_normaliser)
    - [`data_normaliser`](#data_normaliser)
    - [`experiment_normaliser`](#experiment_normaliser)
    - [`percent_converter`](#percent_converter)
    - [`percent_scaler`](#percent_scaler)
- [`utils_shared/output_capture.py`](#utils_sharedoutput_capturepy)
    - [`captured_buffer_getter`](#captured_buffer_getter)
    - [`output_capturer`](#output_capturer)
- [`utils_shared/paf_reader.py`](#utils_sharedpaf_readerpy)
    - [`PafError`](#paferror)
    - [`Spectra`](#spectra)
    - [`PafFile`](#paffile)
    - [`dataset_namer`](#dataset_namer)
    - [`experiment_end_trimmer`](#experiment_end_trimmer)
    - [`experiment_paf_loader`](#experiment_paf_loader)
    - [`experiment_summary_reader`](#experiment_summary_reader)
    - [`record_scanner`](#record_scanner)
    - [`rtf_converter`](#rtf_converter)
    - [`spectra_parser`](#spectra_parser)
    - [`stream_extractor`](#stream_extractor)
    - [`token_reader`](#token_reader)
    - [`u32_reader`](#u32_reader)
    - [`warning_printer`](#warning_printer)
- [`utils_shared/questions.py`](#utils_sharedquestionspy)
    - [`UserQuit`](#userquit)
    - [`_input_reader`](#_input_reader)
    - [`_number_builder`](#_number_builder)
    - [`_question_printer`](#_question_printer)
    - [`choice_asker`](#choice_asker)
    - [`colour_checker`](#colour_checker)
    - [`heading_printer`](#heading_printer)
    - [`info_printer`](#info_printer)
    - [`input_flusher`](#input_flusher)
    - [`multi_asker`](#multi_asker)
    - [`number_asker`](#number_asker)
    - [`numbering_getter`](#numbering_getter)
    - [`numbering_restarter`](#numbering_restarter)
    - [`numbering_setter`](#numbering_setter)
    - [`numbers_asker`](#numbers_asker)
    - [`path_cleaner`](#path_cleaner)
    - [`progress_clearer`](#progress_clearer)
    - [`progress_printer`](#progress_printer)
    - [`section_starter`](#section_starter)
    - [`text_asker`](#text_asker)
    - [`text_colourer`](#text_colourer)
    - [`text_italiser`](#text_italiser)
    - [`yes_no_asker`](#yes_no_asker)
- [`utils_shared/run_logging.py`](#utils_sharedrun_loggingpy)
    - [`_Tee`](#_tee)
    - [`logging_starter`](#logging_starter)
    - [`logging_stopper`](#logging_stopper)
- [`utils_shared/schema.py`](#utils_sharedschemapy)
    - [`finite_float_converter`](#finite_float_converter)
    - [`measurement_column_finder`](#measurement_column_finder)
    - [`source_resolver`](#source_resolver)
    - [`time_getter`](#time_getter)
    - [`value_getter`](#value_getter)
- [`utils_shared/spectral_decomposer.py`](#utils_sharedspectral_decomposerpy)
    - [`_wavelength_masker`](#_wavelength_masker)
    - [`data_filterer`](#data_filterer)
    - [`delta_abs_calculator`](#delta_abs_calculator)
    - [`experiment_decomposer`](#experiment_decomposer)
    - [`fit_importer`](#fit_importer)
    - [`s_array_generator`](#s_array_generator)
    - [`spectrum_decomposer`](#spectrum_decomposer)
- [`utils_shared/survey.py`](#utils_sharedsurveypy)
    - [`_file_focuser`](#_file_focuser)
    - [`_columns_text_builder`](#_columns_text_builder)
    - [`_event_line_builder`](#_event_line_builder)
    - [`_first_event_finder`](#_first_event_finder)
    - [`_last_event_finder`](#_last_event_finder)
    - [`_limits_asker`](#_limits_asker)
    - [`_maths_converter`](#_maths_converter)
    - [`_natural_sorter`](#_natural_sorter)
    - [`_subscript_stripper`](#_subscript_stripper)
    - [`analysis_asker`](#analysis_asker)
    - [`averaging_asker`](#averaging_asker)
    - [`decomposition_asker`](#decomposition_asker)
    - [`event_asker`](#event_asker)
    - [`file_focus_setter`](#file_focus_setter)
    - [`files_asker`](#files_asker)
    - [`haem_form_option_builder`](#haem_form_option_builder)
    - [`haem_name_formatter`](#haem_name_formatter)
    - [`haem_name_sorter`](#haem_name_sorter)
    - [`multi_experiment_asker`](#multi_experiment_asker)
    - [`ocr_option_builder`](#ocr_option_builder)
    - [`od_asker`](#od_asker)
    - [`od_scaling_asker`](#od_scaling_asker)
    - [`paf_finder`](#paf_finder)
    - [`plot_asker`](#plot_asker)
    - [`saved_values_reader`](#saved_values_reader)
    - [`size_asker`](#size_asker)
    - [`trim_asker`](#trim_asker)
- [`utils_shared/trimming.py`](#utils_sharedtrimmingpy)
    - [`experiment_trimmer`](#experiment_trimmer)
- [`utils_viewer/viewer_gui.py`](#utils_viewerviewer_guipy)
    - [`GuiUnavailable`](#guiunavailable)
    - [`ViewerGui`](#viewergui)
    - [`active_gui_getter`](#active_gui_getter)
    - [`gui_runner`](#gui_runner)
- [`utils_viewer/viewer_preview.py`](#utils_viewerviewer_previewpy)
    - [`PreviewSpec`](#previewspec)
    - [`ViewerSession`](#viewersession)
    - [`_info_builder`](#_info_builder)
    - [`_loaded_experiment_getter`](#_loaded_experiment_getter)
    - [`_overlay_drawer`](#_overlay_drawer)
    - [`preview_drawer`](#preview_drawer)
    - [`preview_figure_builder`](#preview_figure_builder)
- [`utils_viewer/viewer_renderer.py`](#utils_viewerviewer_rendererpy)
    - [`PreviewRenderer`](#previewrenderer)
- [`utils_viewer/viewer_stages.py`](#utils_viewerviewer_stagespy)
    - [`_answers_previewer`](#_answers_previewer)
    - [`_file_chooser`](#_file_chooser)
    - [`_limits_lister`](#_limits_lister)
    - [`_review_asker`](#_review_asker)
    - [`analysis_stage_runner`](#analysis_stage_runner)
    - [`browser_stage_runner`](#browser_stage_runner)
    - [`plots_stage_runner`](#plots_stage_runner)
    - [`trim_stage_runner`](#trim_stage_runner)
    - [`viewer_asker`](#viewer_asker)
- [`utils_viewer/viewer_terminal.py`](#utils_viewerviewer_terminalpy)
    - [`OutputRouter`](#outputrouter)
    - [`ansi_colour_getter`](#ansi_colour_getter)
    - [`ansi_splitter`](#ansi_splitter)
    - [`ansi_style_updater`](#ansi_style_updater)
- [`utils_viewer/viewer_window.py`](#utils_viewerviewer_windowpy)
    - [`PictureWindow`](#picturewindow)

## `config.py`

Settings and defaults of DePalencify: figure styles, journal sizes and colours.

### CLASSES

#### `Config`

```text
---- Summary ----
Everything derived from the answers: figure style and sizes, matplotlib settings,
and the settings of the individual plot.

---- Attributes ----
answers : dict
    Terminal answers merged over DEFAULT_ANSWERS.
SPEC : dict
    Journal specification (widths, fonts, dpi) of the chosen journal.
STYLE : dict
    Figure style from figure_style_builder (fonts, unit and spacing in points).
FONTS : dict
    Font sizes in points.
UNIT : float
    Spacing unit in points.
FIGURE_SIZE : Tuple[float, float]
    Figure width and height in inches.
FIGURE_DPI : int
    Resolution of saved figures in dots per inch.
STYLE_WARNINGS : List[str]
    Warnings about the figure style, printed by the caller.
RC_PARAMS : dict
    matplotlib rcParams of the figure style.

---- Globals read ----
BASE_FONT_PT, DEFAULT_ANSWERS, JOURNAL_SPECS, LINE_WIDTH_PT, SPACING.

---- Methods ----
__init__
percent_need_checker
plot_config_builder
source_chooser
```

##### `__init__`

```text
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
```

##### `percent_need_checker`

```text
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
```

##### `plot_config_builder`

```text
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
```

##### `source_chooser`

```text
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
```

### MAIN FUNCTIONS

#### `haem_colour_mapper`

```text
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
```

## `main.py`

Main program: read .paf files, process them and export figures and workbooks.

### MAIN FUNCTIONS

#### `comparison_maker`

```text
---- Summary ----
Main function to draw the side-by-side figure of two chosen experiments, or to say
why it cannot be made.

---- Inputs ----
comparison : dict
    Side-by-side settings: {runs: (left, right), columns, height}.
kept : dict
    Results of experiment_processor keyed by experiment name.
cfg : settings.Config
    Figure style and settings derived from the answers (config.py).
export_root : Path
    Results folder.

---- Globals read ----
settings.Config (the comparison journal is read from the answers).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Writes the comparison figure files and prints the outcome (side effects).

---- Equations ----
None.

---- Helpers ----
comparison_figure_plotter
figure_size_calculator
plot_config_builder
```

#### `everything_asker`

```text
---- Summary ----
Main function to ask every question of the run in numbered sections (files, trimming
and ignoring, analysis, plots, summary figures, export) and to build the per-file
information.

---- Inputs ----
None.

---- Globals read ----
FITS_FOLDER, JOURNAL_NAMES (module constants); settings.DEFAULT_ANSWERS.

---- Outputs ----
Tuple[dict, Path, List[dict], Optional[dict], Optional[dict], Optional[List[str]]]
    (answers, results folder, per-experiment info dictionaries, fit, side-by-side
    comparison settings or None, names of the 2x2 grid experiments or None). Raises
    UserQuit if the user declines to start.

---- Globals mutated ----
None. Reads from and prints to the terminal; writes last_answers.json through
last_answers_saver (side effects).

---- Equations ----
None.

---- Helpers ----
analysis_asker
files_asker
haem_name_formatter
last_answers_loader
last_answers_saver
multi_experiment_asker
plot_asker
section_starter
summary_figure_asker
trim_asker
viewer_asker
yes_no_asker
```

#### `experiment_processor`

```text
---- Summary ----
Main function to read, process, plot and export one .paf file. Each step reports its
own problem so the next step still runs.

---- Inputs ----
info : dict
    Per-file information from everything_asker: path, name, trim and ignore times,
    OD values, events, custom and keep flags.
cfg : settings.Config
    Figure style and settings derived from the answers (config.py).
fit : Optional[dict]
    Fit dictionary from import_fit ({haem_list, data}), or None when the haems are
    not decomposed.
export_root : Path
    Results folder.

---- Globals read ----
plt (matplotlib.pyplot).

---- Outputs ----
Optional[dict]
    {experiment, vo2_source, haem_source, prepared} when the experiment is needed
    again for the comparison or special figures (info["keep"]), otherwise None.

---- Globals mutated ----
None. Writes the figure and the workbook files and prints progress (side effects).

---- Equations ----
None.

---- Helpers ----
experiment_data_processor
experiment_plotter
experiment_preparer
experiment_workbook_exporter
plot_config_builder
```

#### `last_answers_loader`

```text
---- Summary ----
Main function to read the answers remembered from the last run.

---- Inputs ----
None.

---- Globals read ----
LAST_ANSWERS_FILE (module constant).

---- Outputs ----
dict
    Contents of last_answers.json (data_folder, export_folder, answers, files); an
    empty dict when the file is missing or unreadable.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `last_answers_saver`

```text
---- Summary ----
Main function to remember the answers of this run for the next one.

---- Inputs ----
values : dict
    Content to write to last_answers.json: data_folder, export_folder, files and
    answers.

---- Globals read ----
LAST_ANSWERS_FILE (module constant).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Writes last_answers.json (side effect); a read-only folder is ignored
silently.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `program_runner`

```text
---- Summary ----
Main function to run the program: ask the questions, process every file, then draw
the comparison and special figures, logging the output to a file.

---- Inputs ----
None.

---- Globals read ----
VERSION (written to the log).

---- Outputs ----
int
    0 when every file finished, 1 when the run was cancelled or a file failed.

---- Globals mutated ----
None. Reads from and prints to the terminal, sets the matplotlib rcParams, writes
results and a log file, and replaces sys.stdout and sys.stderr while logging (side
effects).

---- Equations ----
None.

---- Helpers ----
comparison_maker
everything_asker
experiment_processor
logging_starter
logging_stopper
special_figures_maker
```

#### `main`

```text
---- Summary ----
Main function of the program: run it in the experiment browser window (terminal on
the left, plots on the right), or in the terminal when the window cannot open.

---- Inputs ----
None.

---- Globals read ----
VERSION (shown in the window title).

---- Outputs ----
int
    0 when every file finished, 1 when the run was cancelled or a file failed.

---- Globals mutated ----
None. Opens the window or runs in the terminal (side effects).

---- Equations ----
None.

---- Helpers ----
gui_runner
program_runner
```

#### `special_figures_maker`

```text
---- Summary ----
Main function to draw the time response, haem and OCR response and 2x2 grid figures;
each is skipped, with the reason, if it cannot be made.

---- Inputs ----
kept : dict
    Results of experiment_processor keyed by experiment name.
cfg : settings.Config
    Figure style and settings derived from the answers (config.py).
fit : Optional[dict]
    Fit dictionary from import_fit ({haem_list, data}), or None when the haems are
    not decomposed.
export_root : Path
    Results folder.
exemplar_names : Optional[List[str]]
    Names of the four experiments of the 2x2 grid, or None.

---- Globals read ----
settings.Config; time_response_runner, ocr_and_haem_response_runner and
exemplar_runner (imported).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Writes the figure files and prints the outcome (side effects).

---- Equations ----
None.

---- Helpers ----
exemplar_runner
ocr_and_haem_response_runner
time_response_runner
```

## `utils_custom/custom_config.py`

Settings dictionaries of the custom figures, built from the terminal answers.

### MAIN FUNCTIONS

#### `exemplar_config_builder`

```text
---- Summary ----
Main function to build the settings of the four-run exemplar figure.

---- Inputs ----
cfg : Config
    Figure style derived from the answers (config.py).
answers : dict
    Terminal answers; uses ho_exemplar_run, ho_ex_columns and ho_ex_height.

---- Globals read ----
ORDER_COLUMNS, STRAIN_ROWS, SAVE_FORMATS.

---- Outputs ----
dict
    Settings for exemplar_figure_plotter and custom_figure_saver.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
figure_size_calculator
```

#### `haem_labeller`

```text
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
```

#### `individual_config_builder`

```text
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
```

#### `ocr_and_haem_response_config_builder`

```text
---- Summary ----
Main function to build the settings of the OCR and haem response figure.

---- Inputs ----
cfg : Config
    Figure style derived from the answers (config.py).
answers : dict
    Terminal answers; uses ho_haems, ho_metric, ho_pub_columns and ho_pub_height.
haem_names : list
    Haem names of the fit, in fit order.

---- Globals read ----
ORDER_COLUMNS, STRAIN_ROWS, GROUP_STYLES, SAVE_FORMATS.

---- Outputs ----
dict
    Settings for ocr_and_haem_response_figure_plotter and custom_figure_saver.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
figure_size_calculator
haem_labeller
```

#### `source_selector`

```text
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
```

#### `time_response_config_builder`

```text
---- Summary ----
Main function to build the settings of the time response figure.

---- Inputs ----
cfg : Config
    Figure style derived from the answers (config.py).
answers : dict
    Terminal answers; uses tr_groups, tr_examples, tr_decompositions,
    tr_skip_hours, tr_columns and tr_height.
haem_names : list
    Haem names of the fit, used to colour the decomposition panels.

---- Globals read ----
SAVE_FORMATS.

---- Outputs ----
dict
    Settings for time_response_figure_plotter, custom_figure_saver and
    time_response_exporter.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
figure_size_calculator
haem_colour_mapper
```

## `utils_custom/custom_figure_saver.py`

Saving of the custom figures into the results folder.

### MAIN FUNCTIONS

#### `custom_figure_saver`

```text
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
```

## `utils_custom/custom_questions.py`

Numbered terminal questions of the time response and the OCR and haem response.

### CUSTOM QUESTIONS HELPERS

#### `_example_pair_maker`

```text
---- Summary ----
Helper function to describe an experiment as the (group, hours) pair that is saved
with the answers.

---- Inputs ----
members : dict
    {experiment name: group}.
name : str
    Experiment name with the hours in it, e.g. 'control_7hours'.

---- Globals read ----
None.

---- Outputs ----
list
    [group, hours] of the experiment.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
hours_parser
```

#### `_haem_ocr_asker`

```text
---- Summary ----
Helper function to ask the settings of the haem and OCR response figure (6.2.x).

---- Inputs ----
names : List[str]
    Experiment names (file names without the extension).
answers : dict
    Answers dictionary the settings are stored in.
defaults : dict
    Default answers.
fit : dict
    Fit dictionary (haem_list) used to list the haems.

---- Globals read ----
None.

---- Outputs ----
Optional[List[str]]
    Names of the experiments that belong to the figure, or None when it cannot be
    made from these files.

---- Globals mutated ----
None. Stores the settings in ``answers`` (side effect).

---- Equations ----
None.

---- Helpers ----
choice_asker
haem_form_option_builder
haem_name_formatter
haem_name_sorter
info_printer
multi_asker
ocr_option_builder
run_name_lister
size_asker
yes_no_asker
```

#### `_saved_example_finder`

```text
---- Summary ----
Helper function to find the experiments that match the (group, hours) pairs
remembered from the last run.

---- Inputs ----
defaults : dict
    Saved answers of the last run.
key : str
    Answer holding the pairs, e.g. 'tr_examples'.
members : dict
    {experiment name: group}.
timed : list
    Names of the experiments that have hours in their name.

---- Globals read ----
None.

---- Outputs ----
list
    Names of the experiments that match a saved pair, in the order of the pairs.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
hours_parser
```

#### `_time_response_asker`

```text
---- Summary ----
Helper function to ask the settings of the time response figure (6.1.x).

---- Inputs ----
names : List[str]
    Experiment names (file names without the extension).
answers : dict
    Answers dictionary the settings are stored in.
defaults : dict
    Default answers.

---- Globals read ----
None.

---- Outputs ----
Optional[dict]
    {experiment name: group} of the experiments that belong to the figure, or
    None when the figure cannot be made from these files.

---- Globals mutated ----
None. Stores the settings in ``answers`` (side effect).

---- Equations ----
None.

---- Helpers ----
_example_pair_maker
_saved_example_finder
choice_asker
group_assigner
hours_parser
info_printer
size_asker
text_asker
```

#### `_window_ensurer`

```text
---- Summary ----
Helper function to make sure the event-window settings exist for the special
figures: they reuse the section 3 settings, which are asked here if event
averaging was switched off there.

---- Inputs ----
answers : dict
    Answers dictionary; uses averaging, window_minutes and gap_minutes.
defaults : dict
    Default answers.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Stores the tr_* and ho_* window answers in ``answers`` (side effect).

---- Equations ----
None.

---- Helpers ----
averaging_asker
info_printer
```

### MAIN FUNCTIONS

#### `summary_figure_asker`

```text
---- Summary ----
Main function to ask section 6: whether to plot a time response and a haem and
OCR response, and the settings of each one chosen. Both need the haem fit, which
is asked for here if it was not chosen in section 3.

---- Inputs ----
names : List[str]
    Experiment names (file names without the extension).
answers : dict
    Answers dictionary the settings are stored in.
defaults : dict
    Default answers.
summaries : List[dict]
    File summaries (DATA_FORMAT.md), used if the fit has to be asked for.
fit : Optional[dict]
    Fit dictionary chosen in section 3, or None.
fits_folder : Path
    Folder holding the fit .csv files.

---- Globals read ----
None.

---- Outputs ----
tuple
    (fit, result). result is {'time_response': {name: group} or None,
    'haem_ocr': [names] or None}; None means that figure will not be made.

---- Globals mutated ----
None. Stores the settings in ``answers`` (side effect).

---- Equations ----
None.

---- Helpers ----
_haem_ocr_asker
_time_response_asker
_window_ensurer
decomposition_asker
info_printer
yes_no_asker
```

## `utils_custom/custom_runner.py`

Preparation of single experiments and drawing of the custom figures.

### CUSTOM RUNNER HELPERS

#### `_ocr_and_haem_response_preparer`

```text
---- Summary ----
Helper function to calculate the event-window averages used by the haem and OCR
response figures, on a copy of one experiment.

---- Inputs ----
experiment : dict
    Processed experiment (DATA_FORMAT.md).
answers : dict
    Terminal answers; uses the ho_* settings.
od_available : bool
    True when OD, volume and dilution factor were available for this experiment.

---- Globals read ----
None.

---- Outputs ----
Optional[dict]
    Shallow copy with 'averages' added, or None when the experiment lacks the OD
    values the chosen sources need (it would not be comparable with the others).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
experiment_averages_calculator
source_selector
```

#### `_time_response_preparer`

```text
---- Summary ----
Helper function to average the spectra in the event windows, subtract the last two
windows and decompose the difference spectrum, on a copy of one experiment.

---- Inputs ----
experiment : dict
    Processed experiment with attenuation spectra (DATA_FORMAT.md).
group : str
    Group the experiment belongs to.
answers : dict
    Terminal answers; uses decomposition_dataset and the tr_* windows.
fit : dict
    Fit dictionary from import_fit.

---- Globals read ----
config.DEGREE_OF_SCATTER, config.HAEM_FACTOR.

---- Outputs ----
dict
    Shallow copy of the experiment with group, spectral_averages,
    difference_spectrum and difference_decomposition added.

---- Globals mutated ----
None.

---- Equations ----
None. See spectral_difference.py.

---- Helpers ----
difference_spectrum_calculator
difference_spectrum_decomposer
spectral_averager
```

### MAIN FUNCTIONS

#### `exemplar_runner`

```text
---- Summary ----
Main function to draw the 2x2 figure: one experiment for each strain and addition
order, plotted like the individual experiment figures.

---- Inputs ----
chosen : dict
    {experiment name: kept result of process_experiment} with the keys
    experiment, vo2_source and haem_source (DATA_FORMAT.md).
cfg : Config
    Figure style of this figure (its own journal).
answers : dict
    Terminal answers; uses haems, plot_haems and the ho_ex_* and ho_exemplar_run
    settings.
fit : Optional[dict]
    Fit dictionary, or None when the haems were not decomposed.
export_root : Path
    Results folder.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing; the figure files are written.

---- Globals mutated ----
None. Writes the figure files (side effect).

---- Equations ----
None.

---- Helpers ----
custom_figure_saver
exemplar_config_builder
exemplar_figure_plotter
individual_config_builder
```

#### `experiment_preparer`

```text
---- Summary ----
Main function to prepare one processed experiment for the special figures. Each
figure is prepared on its own, so a problem with one does not stop the other.

---- Inputs ----
experiment : dict
    Processed experiment with its spectra still attached (DATA_FORMAT.md).
custom : dict
    {'time_response_group': group or None, 'haem_ocr': bool} for this experiment.
answers : dict
    Terminal answers.
fit : Optional[dict]
    Fit dictionary from import_fit.
od_available : bool
    True when OD, volume and dilution factor were available.

---- Globals read ----
None.

---- Outputs ----
dict
    {'time_response': prepared experiment or None, 'haem_ocr': prepared
    experiment or None}.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_ocr_and_haem_response_preparer
_time_response_preparer
```

#### `ocr_and_haem_response_runner`

```text
---- Summary ----
Main function to combine the runs of each condition, draw the OCR and haem response
figure and write the workbook behind it. A problem with the figure does not stop
the workbook, and neither stops the 2x2 figure, which is drawn separately.

---- Inputs ----
experiments : dict
    Prepared experiments keyed by name, each with averages (DATA_FORMAT.md).
cfg : Config
    Figure style derived from the answers.
answers : dict
    Terminal answers.
fit : dict
    Fit dictionary from import_fit.
export_root : Path
    Results folder.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing; files are written.

---- Globals mutated ----
None. Writes ocr_and_haem_response.xlsx and the figure files to ``export_root``
(side effect).

---- Equations ----
None.

---- Helpers ----
custom_figure_saver
ocr_and_haem_response_config_builder
ocr_and_haem_response_exporter
ocr_and_haem_response_figure_plotter
triplicate_averager
```

#### `time_response_runner`

```text
---- Summary ----
Main function to draw the time response figure from the prepared experiments and
write the workbook behind it.

---- Inputs ----
experiments : dict
    Prepared experiments keyed by name, each with group and
    difference_decomposition (DATA_FORMAT.md).
cfg : Config
    Figure style derived from the answers.
answers : dict
    Terminal answers.
fit : dict
    Fit dictionary from import_fit.
export_root : Path
    Results folder.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing; files are written.

---- Globals mutated ----
None. Writes time_response.xlsx and the figure files to ``export_root`` (side
effect).

---- Equations ----
None.

---- Helpers ----
custom_figure_saver
individual_config_builder
time_response_config_builder
time_response_exporter
time_response_figure_plotter
```

## `utils_custom/exemplar_plotter.py`

Figure of four exemplar experiments in a 2x2 grid.

### EXEMPLAR HELPERS

#### `_crop_start_finder`

```text
---- Summary ----
Helper function to find the time at which an exemplar crop begins.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
mode : str
    'baseline' (start of the average0 window) or 'first_addition'.
before_minutes : float
    Minutes kept before the first addition.
margin_minutes : float
    Extra minutes kept before the baseline window.

---- Globals read ----
None.

---- Outputs ----
float
    Crop start time in minutes.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_exemplar_gap_calculator`

```text
---- Summary ----
Helper function to calculate the gap between rows and between columns of the
exemplar quadrants.

---- Inputs ----
config : dict
    Figure settings dictionary built in custom_config.py.
individual_config : dict
    Individual-experiment plot settings, as returned by Config.plot_config in
    config.py.
n_rows : int
    Number of group rows.
n_columns : int
    Number of addition-order columns.

---- Globals read ----
None.

---- Outputs ----
tuple
    (hspace, wspace) as GridSpec fractions.

---- Globals mutated ----
None.

---- Equations ----
row_gap = 1.2 tick + 0.5 unit + label pad + 1.2 label + 1.0 unit; column_gap = lines
x 1.2 label + y label pad + 5 x 0.55 tick + 0.5 unit + 1.5 unit (points) for one
column, 1.5 unit when there are several (the later columns have no y labels).

---- Helpers ----
gap_space_calculator
```

#### `_exemplar_plotter`

```text
---- Summary ----
Helper function to draw one experiment exactly as the individual plotter does.

---- Inputs ----
fig : Figure
    Matplotlib figure.
subplot_spec : SubplotSpec
    Grid cell the experiment is drawn in.
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
individual_config : dict
    Individual-experiment plot settings, as returned by Config.plot_config in
    config.py.

---- Globals read ----
None.

---- Outputs ----
list
    Axes of the stacked panels.

---- Globals mutated ----
None. Adds axes to ``fig`` (side effect).

---- Equations ----
None.

---- Helpers ----
experiment_drawer
```

#### `_exemplar_selector`

```text
---- Summary ----
Helper function to pick the experiment of one run number for every (strain, order)
cell.

---- Inputs ----
experiments : dict
    Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.
run : int
    Run number shown for each condition.

---- Globals read ----
None.

---- Outputs ----
dict
    {(strain, order): experiment}. Raises ValueError if two experiments match one
    cell.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
experiment_classifier
```

#### `_experiment_cropper`

```text
---- Summary ----
Helper function to copy an experiment cropped to begin at a chosen time, with time
measured from there.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
start : float
    Time in minutes at which the crop begins.

---- Globals read ----
None.

---- Outputs ----
tuple
    (cropped experiment copy, last time in minutes).

---- Globals mutated ----
None.

---- Equations ----
t_new = t - start; rows with t_new < 0 are dropped.

---- Helpers ----
time_getter
```

### MAIN FUNCTIONS

#### `exemplar_figure_plotter`

```text
---- Summary ----
Main function to build the exemplar figure: one run per condition, each drawn by the
individual plotter in its own quadrant.

---- Inputs ----
experiments : dict
    Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.
config : dict
    Exemplar figure settings from custom_config.exemplar_config_builder.
individual_config : dict
    Individual-experiment plot settings, as returned by Config.plot_config in
    config.py.

---- Globals read ----
None.

---- Outputs ----
tuple
    (fig, axes); axes maps (strain, order) to its list of axes and 'letters' to
    {letter: experiment name}.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_crop_start_finder
_exemplar_gap_calculator
_exemplar_plotter
_exemplar_selector
_experiment_cropper
experiment_title_builder
figure_finisher
stack_legend_drawer
watermark_style_builder
```

## `utils_custom/ocr_and_haem_response_exporter.py`

Export of the OCR and haem response to a workbook that can be checked by hand.

### HELPERS

#### `_baseline_sheet_writer`

```text
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
```

#### `_condition_sheet_writer`

```text
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
```

#### `_measurement_table_writer`

```text
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
```

#### `_statistics_writer`

```text
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
```

#### `_test_row_writer`

```text
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
```

#### `_tests_sheet_writer`

```text
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
```

### MAIN FUNCTIONS

#### `ocr_and_haem_response_exporter`

```text
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
```

## `utils_custom/ocr_and_haem_response_plotter.py`

Figure of the baseline OCR, the OCR response and the haem response.

### OCR AND HAEM RESPONSE HELPERS

#### `_axes_styler`

```text
---- Summary ----
Helper function to apply the tick, grid and spine style of the response and baseline
panels.

---- Inputs ----
ax : Axes
    Matplotlib axes to draw on.
config : dict
    Figure settings dictionary built in custom_config.py.
tick_size : float
    Tick label size in points.
pad : Optional[float]
    Tick label pad in points, or None for the default.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes the style of ``ax`` (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_baseline_bar_plotter`

```text
---- Summary ----
Helper function to draw the baseline OCR (average0) bar chart per group, with every
run overlaid and a Student t-test bracket between the two groups.

---- Inputs ----
ax : Axes
    Matplotlib axes to draw on.
experiments : dict
    Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.
strains : tuple
    Group names (rows or bars), in drawing order.
config : dict
    Figure settings dictionary built in custom_config.py.
tests : list
    List collecting one dictionary per t-test comparison.

---- Globals read ----
None.

---- Outputs ----
dict
    Baseline summary for the workbook: 'strains', 'vo2_source' and 'runs' ({group:
    {experiment name: baseline OCR}}).

---- Globals mutated ----
None. Draws on ``ax`` and appends the baseline t-test to ``tests`` (side effects).

---- Equations ----
Bar height = mean of the run baselines; error bar = SEM = SD / sqrt(n). Student
t-test with equal variances between the two groups.

---- Helpers ----
_axes_styler
_column_chooser
_significance_bar_drawer
_significance_formatter
experiment_classifier
finite_float_converter
```

#### `_block_gap_calculator`

```text
---- Summary ----
Helper function to calculate the gap below each block of the OCR and haem response
figure (each gap is sized for what it holds) and the gap between the response
columns.

---- Inputs ----
config : dict
    Figure settings dictionary built in custom_config.py.
blocks : list
    Block names from top to bottom ('baseline', 'ocr_response', 'haem_response').
n_columns : int
    Number of addition-order columns.

---- Globals read ----
None.

---- Outputs ----
tuple
    (gaps in points, one per block but the last; wspace as a GridSpec fraction).

---- Globals mutated ----
None.

---- Equations ----
A gap above the first response block = x tick labels + 0.5 unit + title and legend
row + 1.0 unit. The gap between the OCR and haem responses = two-line tick labels +
0.5 unit + the significance bars' headroom + 0.5 unit. column_gap = 5 x 0.55 tick +
0.5 unit + 1.5 unit (points).

---- Helpers ----
gap_space_calculator
```

#### `_column_chooser`

```text
---- Summary ----
Helper function to choose the OCR column: the preferred one if set, else VoO2, else
the first available.

---- Inputs ----
available : Iterable
    Column names that are available.
preferred : Optional[str]
    Column requested in the settings, or None.

---- Globals read ----
None.

---- Outputs ----
Optional[str]
    Chosen column name, or None if none is available.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_condition_indexer`

```text
---- Summary ----
Helper function to map each (strain, order) pair to its condition name in the
triplicate results.

---- Inputs ----
triplicates : dict
    Across-run statistics per condition, from triplicate_averager (DATA_FORMAT.md).

---- Globals read ----
None.

---- Outputs ----
dict
    {(strain, order): condition name}. Raises ValueError if two conditions match one
    pair.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
condition_classifier
```

#### `_finite_run_filter`

```text
---- Summary ----
Helper function to keep the runs that have a finite value.

---- Inputs ----
runs : dict
    {run number or experiment name: value}; values may be NaN.

---- Globals read ----
None.

---- Outputs ----
dict
    The same mapping without the runs whose value is NaN or infinite; values are
    floats.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_haem_block_plotter`

```text
---- Summary ----
Helper function to draw the haem response: one row per haem, one column per addition
order, a line per group.

---- Inputs ----
fig : Figure
    Matplotlib figure.
spec : SubplotSpec
    Grid cell the block is drawn in.
orders : tuple
    Addition-order names (columns), in drawing order.
strains : tuple
    Group names (rows or bars), in drawing order.
triplicates : dict
    Across-run statistics per condition, from triplicate_averager (DATA_FORMAT.md).
conditions : dict
    Lookup {(strain, order): condition name}.
references : dict
    Lookup {order: experiment or None} used for the event tick labels.
config : dict
    Figure settings dictionary built in custom_config.py.
rows : list
    Haem row dictionaries {haem, label}.
haem_source : str
    Haem source key, for example 'delta_abs_od'.
tests : Optional[list]
    List collecting t-test comparisons, or None to skip the tests.
bars_above : bool
    True draws the top row's significance bars in the white space above the block
    (between it and the block above) instead of inside the axes.

---- Globals read ----
None.

---- Outputs ----
tuple
    (grid of axes [row][column], invisible axes carrying the shared y label).

---- Globals mutated ----
None. Adds axes to ``fig`` and appends to ``tests`` (side effects).

---- Equations ----
None.

---- Helpers ----
_haem_label_finder
_haem_label_pad_calculator
_mean_ylim_setter
_measurement_finder
_outside_bar_drawer
_reference_level_finder
_response_axes_preparer
_response_series_drawer
_response_window_tester
_row_ylim_sharer
_tick_label_builder
_window_orderer
```

#### `_haem_label_finder`

```text
---- Summary ----
Helper function to find the shared y label of the haem response rows.

---- Inputs ----
config : dict
    Figure settings dictionary built in custom_config.py.
metric : str
    Response metric: 'delta', 'change' or 'value'.
haem_source : str
    Haem source key, for example 'delta_abs_od'.

---- Globals read ----
None.

---- Outputs ----
str
    Label text from HAEM_RESPONSE_AXIS_LABELS for the metric and source.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_haem_label_pad_calculator`

```text
---- Summary ----
Helper function to calculate the points between the shared haem label and the haem
axes.

---- Inputs ----
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
None.

---- Outputs ----
float
    Label pad in points.

---- Globals mutated ----
None.

---- Equations ----
pad = 1.2 label font + 0.5 unit + 5 x 0.55 tick font + 0.5 unit (points).

---- Helpers ----
None.
```

#### `_haem_row_selector`

```text
---- Summary ----
Helper function to select the haem response rows to draw, in the order listed in
HAEM_RESPONSE_SHOW.

---- Inputs ----
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
None.

---- Outputs ----
list
    Row dictionaries {haem, label}. Every row is returned when HAEM_RESPONSE_SHOW is
    empty. Entries are matched to a row label or haem name ignoring case and
    punctuation.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
name_simplifier
```

#### `_haem_source_finder`

```text
---- Summary ----
Helper function to find the haem source that every condition's averages were
calculated from.

---- Inputs ----
triplicates : dict
    Across-run statistics per condition, from triplicate_averager (DATA_FORMAT.md).

---- Globals read ----
None.

---- Outputs ----
str
    Haem source key, for example 'delta_abs_od'. Raises ValueError if the conditions
    differ.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_layout_validator`

```text
---- Summary ----
Helper function to check that the layout options of the OCR and haem response
figure are recognised and to return the group and order lists.

---- Inputs ----
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
ORDER_TITLES, BLOCK_NAMES, RESPONSE_METRICS (module constants).

---- Outputs ----
tuple
    (orders, strains): addition orders (columns) and groups (rows), as tuples.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_legend_handle_builder`

```text
---- Summary ----
Helper function to build legend entries showing each group's colour, line style and
marker.

---- Inputs ----
strains : tuple
    Group names (rows or bars), in drawing order.
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
None.

---- Outputs ----
list
    Line2D handles, one per group.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_mean_ylim_setter`

```text
---- Summary ----
Helper function to set the y range of a response panel from the group means (and
the baseline level) only, so that a single outlier run or a very large error bar
does not stretch the axis. Points and error bars beyond the range are clipped.

---- Inputs ----
ax : Axes
    Response panel, with the series already drawn.
series_list : list
    One list of window statistics per strain, as drawn by _response_series_drawer.
metric : str
    Response metric, which decides the field holding the mean.
baseline_level : Optional[float]
    Reference level that must stay in view (for example 100 for % of baseline).
margin : float
    Fraction of the mean range added above and below.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None. Sets the y limits of ``ax`` (side effect); does nothing when no mean is
finite.

---- Equations ----
low = min(means) - margin x range; high = max(means) + margin x range, where the
range is max(means) - min(means) (at least 1 % of the largest absolute mean). When
all means are on one side of the baseline, the baseline side gets a 3 % margin.

---- Helpers ----
_metric_field_selector
```

#### `_measurement_finder`

```text
---- Summary ----
Helper function to find the column matching a wanted name, ignoring case and
punctuation.

---- Inputs ----
available : Iterable
    Column names that are available.
wanted : str
    Name to look for.

---- Globals read ----
None.

---- Outputs ----
Optional[str]
    Matching column name, or None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
name_simplifier
```

#### `_metric_field_selector`

```text
---- Summary ----
Helper function to name the keys of the triplicate statistics used by a response
metric.

---- Inputs ----
metric : str
    Response metric: 'delta', 'change' or 'value'.

---- Globals read ----
None.

---- Outputs ----
tuple
    (mean key, sem key, n key, per-run values key).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_ocr_block_plotter`

```text
---- Summary ----
Helper function to draw the OCR response (percent of each run's baseline, mean and
SEM across runs), one axes per addition order.

---- Inputs ----
fig : Figure
    Matplotlib figure.
spec : SubplotSpec
    Grid cell the block is drawn in.
orders : tuple
    Addition-order names (columns), in drawing order.
strains : tuple
    Group names (rows or bars), in drawing order.
triplicates : dict
    Across-run statistics per condition, from triplicate_averager (DATA_FORMAT.md).
conditions : dict
    Lookup {(strain, order): condition name}.
references : dict
    Lookup {order: experiment or None} used for the event tick labels.
config : dict
    Figure settings dictionary built in custom_config.py.
tests : Optional[list]
    List collecting t-test comparisons, or None to skip the tests.

---- Globals read ----
None.

---- Outputs ----
list
    The axes, one per addition order.

---- Globals mutated ----
None. Adds axes to ``fig`` and appends to ``tests`` (side effects).

---- Equations ----
None.

---- Helpers ----
_column_chooser
_response_axes_preparer
_response_series_drawer
_response_window_tester
_row_ylim_sharer
_tick_label_builder
_window_orderer
```

#### `_offset_transformer`

```text
---- Summary ----
Helper function to build a transform that shifts data coordinates upward by a
number of points.

---- Inputs ----
ax : Axes
    Matplotlib axes whose data coordinates are shifted.
points : float
    Upward shift in points.

---- Globals read ----
None.

---- Outputs ----
Any
    Matplotlib transform.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_outside_bar_drawer`

```text
---- Summary ----
Helper function to draw the significance bars stored by _response_window_tester in
the white space just above an axes, so the plot keeps its full height.

---- Inputs ----
ax : Axes
    Response panel whose y range is final.
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Draws on ``ax`` (side effect).

---- Equations ----
None.

---- Helpers ----
_test_bar_drawer
```

#### `_p_value_adjuster`

```text
---- Summary ----
Helper function to adjust a list of p values for multiple comparisons.

---- Inputs ----
p_values : Iterable
    Raw p values.
method : str
    'none', 'bonferroni' or 'holm'.

---- Globals read ----
None.

---- Outputs ----
np.ndarray
    Adjusted p values, same order as the input.

---- Globals mutated ----
None.

---- Equations ----
Bonferroni: p_adj = min(n p, 1). Holm: sort ascending, p_adj(i) = min(max over j <=
i of (n - j) p(j), 1) with j counted from 0.

---- Helpers ----
None.
```

#### `_panel_labeller`

```text
---- Summary ----
Helper function to give the next letter to a panel.

---- Inputs ----
state : dict
    Lettering state with keys 'letters' (iterator of letters), 'names' ({letter:
    panel name}) and 'panels' (list of (letter, main axes, member axes)).
main_ax : Axes
    Main axes of the panel.
members : list
    All axes that belong to the panel.
name : str
    Panel name used in the printed panel list.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Advances ``state['letters']`` and appends to ``state['names']`` and
``state['panels']`` (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_reference_level_finder`

```text
---- Summary ----
Helper function to find the height of the dashed reference line of the haem
response.

---- Inputs ----
metric : str
    Response metric: 'delta', 'change' or 'value'.
haem_source : str
    Haem source key, for example 'delta_abs_od'.

---- Globals read ----
None.

---- Outputs ----
Optional[float]
    0 for a change, 100 for percent of baseline, 0 for a delta abs value, otherwise
    None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_reference_selector`

```text
---- Summary ----
Helper function to pick, for each addition order, the first run of the first
available group (used for the event tick labels).

---- Inputs ----
experiments : dict
    Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.
triplicates : dict
    Across-run statistics per condition, from triplicate_averager (DATA_FORMAT.md).
conditions : dict
    Lookup {(strain, order): condition name}.
orders : tuple
    Addition-order names (columns), in drawing order.
strains : tuple
    Group names (rows or bars), in drawing order.

---- Globals read ----
None.

---- Outputs ----
dict
    {order: experiment or None}.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_response_axes_preparer`

```text
---- Summary ----
Helper function to draw the baseline reference line and set the window ticks of a
response panel.

---- Inputs ----
ax : Axes
    Matplotlib axes to draw on.
window_names : list
    Averaging window names, for example ['average0', 'average1'].
tick_labels : list
    Tick label of every window.
show_xlabels : bool
    True to write the tick labels.
config : dict
    Figure settings dictionary built in custom_config.py.
baseline_level : Optional[float]
    Height of the reference line, or None for no line.

---- Globals read ----
None.

---- Outputs ----
np.ndarray
    x positions of the windows.

---- Globals mutated ----
None. Changes the style of ``ax`` (side effect).

---- Equations ----
None.

---- Helpers ----
_axes_styler
```

#### `_response_metric_checker`

```text
---- Summary ----
Helper function to reject a percent-of-baseline response for the delta abs sources,
which start at 0.

---- Inputs ----
metric : str
    Response metric: 'delta', 'change' or 'value'.
haem_source : str
    Haem source key, for example 'delta_abs_od'.

---- Globals read ----
DELTA_HAEM_SOURCES (schema constant).

---- Outputs ----
None
    Nothing. Raises ValueError for the combination that is not allowed.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_response_series_drawer`

```text
---- Summary ----
Helper function to plot every run as a point, the mean as a line and SEM error bars
for one group.

---- Inputs ----
ax : Axes
    Matplotlib axes to draw on.
x : Iterable
    x positions of the windows.
stats_list : list
    Statistics dictionary (or None) for each window.
style : dict
    Group style: colour, linestyle, marker.
config : dict
    Figure settings dictionary built in custom_config.py.
label : Optional[str]
    Unused legend text.
metric : str
    Response metric: 'delta', 'change' or 'value'.
offset : float
    Horizontal shift in x units so groups sit side by side.

---- Globals read ----
None.

---- Outputs ----
bool
    True if anything was drawn.

---- Globals mutated ----
None. Draws on ``ax`` (side effect).

---- Equations ----
None.

---- Helpers ----
_metric_field_selector
```

#### `_response_window_tester`

```text
---- Summary ----
Helper function to run a Student t-test between the two groups at every window of a
response panel and mark the significant windows.

---- Inputs ----
ax : Axes
    Matplotlib axes to draw on.
x : np.ndarray
    x positions of the windows.
windows : list
    Window names.
series_by_strain : dict
    {strain: [statistics per window]}.
strains : tuple
    Group names (rows or bars), in drawing order.
metric : str
    Response metric: 'delta', 'change' or 'value'.
config : dict
    Figure settings dictionary built in custom_config.py.
panel_name : str
    Panel name written to the test table.
tests : list
    List collecting one dictionary per t-test comparison.
outside : bool
    True keeps the axis range as it is and stores the marks on ``ax`` for
    _outside_bar_drawer, which draws them in the space above the axes.
measurement : str
    Name of the measurement tested (OCR or haem column), written to the test table.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Appends one dictionary per comparison to ``tests`` (the keys are listed in
DATA_FORMAT.md) and draws on ``ax`` (side effects); with ``outside`` it sets
``ax.outside_marks`` instead of drawing.

---- Equations ----
Equal-variance Student t-test per window; p values adjusted across the windows of
the panel (RESPONSE_TEST_CORRECTION); significant if p_adj < RESPONSE_TEST_ALPHA.

---- Helpers ----
_finite_run_filter
_metric_field_selector
_p_value_adjuster
_test_bar_drawer
```

#### `_row_ylim_sharer`

```text
---- Summary ----
Helper function to give every axes in a row the union of their y ranges.

---- Inputs ----
axes_row : list
    Axes of one row.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Sets the y limits of the axes (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_significance_bar_drawer`

```text
---- Summary ----
Helper function to draw a bracket between two x positions with text centred above
it.

---- Inputs ----
ax : Axes
    Matplotlib axes to draw on.
x_left : float
    Left end of the bracket (data units).
x_right : float
    Right end of the bracket (data units).
y : float
    Height of the bracket (data units).
text : str
    Text written above the bracket.
tick_size : float
    Tick label size in points.
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Draws on ``ax`` (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_significance_formatter`

```text
---- Summary ----
Helper function to format a p value as stars or as text.

---- Inputs ----
p_value : float
    p value.
style : str
    'stars' or 'p'.

---- Globals read ----
None.

---- Outputs ----
str
    '***', '**', '*' or 'ns' (stars style) or the p value text.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_test_bar_drawer`

```text
---- Summary ----
Helper function to draw a small bracket joining the two groups' points at one window
with text above it.

---- Inputs ----
ax : Axes
    Matplotlib axes to draw on.
x_left : float
    Left end (data units).
x_right : float
    Right end (data units).
y : float
    Data height the clearances are measured from.
text : str
    Stars written above the bracket.
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Draws on ``ax`` (side effect).

---- Equations ----
None.

---- Helpers ----
_offset_transformer
```

#### `_tick_label_builder`

```text
---- Summary ----
Helper function to build the x tick labels of the averaging windows: Baseline, then
the addition that precedes each window.

---- Inputs ----
experiment : Optional[dict]
    Reference experiment whose events label the windows, or None.
window_names : list
    Averaging window names, for example ['average0', 'average1'].

---- Globals read ----
None.

---- Outputs ----
list
    One label per window; additions are written as label and concentration.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
concentration_formatter
finite_float_converter
```

#### `_window_orderer`

```text
---- Summary ----
Helper function to list the averaging windows present in any condition of one
addition order.

---- Inputs ----
order : str
    Addition order name.
strains : tuple
    Group names (rows or bars), in drawing order.
triplicates : dict
    Across-run statistics per condition, from triplicate_averager (DATA_FORMAT.md).
conditions : dict
    Lookup {(strain, order): condition name}.

---- Globals read ----
None.

---- Outputs ----
list
    Window names in numerical order.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `ocr_and_haem_response_figure_plotter`

```text
---- Summary ----
Main function to build the OCR and haem response figure: baseline OCR, OCR response
and haem response blocks.

---- Inputs ----
experiments : dict
    Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.
triplicates : dict
    Across-run statistics from triplicate_averager.
config : dict
    Figure settings from custom_config.ocr_and_haem_response_config_builder.

---- Globals read ----
None.

---- Outputs ----
tuple
    (fig, axes); axes holds 'baseline', 'ocr_response', 'haem_response' and
    'letters' ({letter: panel name}).

---- Globals mutated ----
None. Stores the t-test records on the returned figure as ``fig.response_tests`` and
the baseline summary as ``fig.response_baseline`` (None without a baseline block).

---- Equations ----
None.

---- Helpers ----
_baseline_bar_plotter
_block_gap_calculator
_condition_indexer
_haem_block_plotter
_haem_row_selector
_haem_source_finder
_layout_validator
_legend_handle_builder
_ocr_block_plotter
_panel_labeller
_reference_selector
_response_metric_checker
experiment_classifier
figure_finisher
```

## `utils_custom/publication_plotter.py`

Publication figure (baseline OCR, OCR response, haem response), exemplars.

### _AXES STYLER

#### `_axes_styler`

```text
---- Summary ----
Helper function to apply the tick, grid and spine style of the response and baseline
panels.

---- Inputs ----
ax : Axes
    Matplotlib axes to draw on.
config : dict
    Figure settings dictionary built in custom_config.py.
tick_size : float
    Tick label size in points.
pad : Optional[float]
    Tick label pad in points, or None for the default.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes the style of ``ax`` (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

### _BASELINE BAR PLOTTER

#### `_baseline_bar_plotter`

```text
---- Summary ----
Helper function to draw the baseline OCR (average0) bar chart per group, with every
run overlaid and a Student t-test bracket between the two groups.

---- Inputs ----
ax : Axes
    Matplotlib axes to draw on.
experiments : dict
    Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.
strains : tuple
    Group names (rows or bars), in drawing order.
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Draws on ``ax`` (side effect).

---- Equations ----
Bar height = mean of the run baselines; error bar = SEM = SD / sqrt(n). Student
t-test with equal variances between the two groups.

---- Helpers ----
_axes_styler
_column_chooser
_experiment_classifier
_significance_bar_drawer
_significance_formatter
finite_float_converter
```

### _BLOCK GAP CALCULATOR

#### `_block_gap_calculator`

```text
---- Summary ----
Helper function to calculate the gap below each block of the publication figure
(each gap is sized for what it holds) and the gap between the response columns.

---- Inputs ----
config : dict
    Figure settings dictionary built in custom_config.py.
blocks : list
    Block names from top to bottom ('baseline', 'ocr_response', 'haem_response').
n_columns : int
    Number of addition-order columns.

---- Globals read ----
None.

---- Outputs ----
tuple
    (gaps in points, one per block but the last; wspace as a GridSpec fraction).

---- Globals mutated ----
None.

---- Equations ----
A gap above the first response block = x tick labels + 0.5 unit + title and legend
row + 1.0 unit. The gap between the OCR and haem responses = two-line tick labels +
0.5 unit + the significance bars' headroom + 0.5 unit. column_gap = 5 x 0.55 tick +
0.5 unit + 1.5 unit (points).

---- Helpers ----
gap_space_calculator
```

### _COLUMN CHOOSER

#### `_column_chooser`

```text
---- Summary ----
Helper function to choose the OCR column: the preferred one if set, else VoO2, else
the first available.

---- Inputs ----
available : Iterable
    Column names that are available.
preferred : Optional[str]
    Column requested in the settings, or None.

---- Globals read ----
None.

---- Outputs ----
Optional[str]
    Chosen column name, or None if none is available.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### _CONDITION INDEXER

#### `_condition_indexer`

```text
---- Summary ----
Helper function to map each (strain, order) pair to its condition name in the
triplicate results.

---- Inputs ----
triplicates : dict
    Across-run statistics per condition, from triplicate_averager (DATA_FORMAT.md).

---- Globals read ----
None.

---- Outputs ----
dict
    {(strain, order): condition name}. Raises ValueError if two conditions match one
    pair.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
condition_classifier
```

### _CROP START FINDER

#### `_crop_start_finder`

```text
---- Summary ----
Helper function to find the time at which an exemplar crop begins.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
mode : str
    'baseline' (start of the average0 window) or 'first_addition'.
before_minutes : float
    Minutes kept before the first addition.
margin_minutes : float
    Extra minutes kept before the baseline window.

---- Globals read ----
None.

---- Outputs ----
float
    Crop start time in minutes.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### _EXEMPLAR GAP CALCULATOR

#### `_exemplar_gap_calculator`

```text
---- Summary ----
Helper function to calculate the gap between rows and between columns of the
exemplar quadrants.

---- Inputs ----
config : dict
    Figure settings dictionary built in custom_config.py.
individual_config : dict
    Individual-experiment plot settings, as returned by Config.plot_config in
    config.py.
n_rows : int
    Number of group rows.
n_columns : int
    Number of addition-order columns.

---- Globals read ----
None.

---- Outputs ----
tuple
    (hspace, wspace) as GridSpec fractions.

---- Globals mutated ----
None.

---- Equations ----
row_gap = 1.2 tick + 0.5 unit + label pad + 1.2 label + 1.0 unit; column_gap = lines
x 1.2 label + y label pad + 5 x 0.55 tick + 0.5 unit + 1.5 unit (points) for one
column, 1.5 unit when there are several (the later columns have no y labels).

---- Helpers ----
gap_space_calculator
```

### _EXEMPLAR PLOTTER

#### `_exemplar_plotter`

```text
---- Summary ----
Helper function to draw one experiment exactly as the individual plotter does.

---- Inputs ----
fig : Figure
    Matplotlib figure.
subplot_spec : SubplotSpec
    Grid cell the experiment is drawn in.
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
individual_config : dict
    Individual-experiment plot settings, as returned by Config.plot_config in
    config.py.

---- Globals read ----
None.

---- Outputs ----
list
    Axes of the stacked panels.

---- Globals mutated ----
None. Adds axes to ``fig`` (side effect).

---- Equations ----
None.

---- Helpers ----
experiment_drawer
```

### _EXEMPLAR SELECTOR

#### `_exemplar_selector`

```text
---- Summary ----
Helper function to pick the experiment of one run number for every (strain, order)
cell.

---- Inputs ----
experiments : dict
    Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.
run : int
    Run number shown for each condition.

---- Globals read ----
None.

---- Outputs ----
dict
    {(strain, order): experiment}. Raises ValueError if two experiments match one
    cell.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_experiment_classifier
```

### _EXPERIMENT CLASSIFIER

#### `_experiment_classifier`

```text
---- Summary ----
Helper function to identify the strain, addition order and run number from an
experiment name.

---- Inputs ----
name : str
    Experiment name such as 'control_kcn_then_bd_run1'.

---- Globals read ----
None.

---- Outputs ----
tuple
    (strain, order, run); entries are None where they cannot be identified.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
condition_classifier
run_name_parser
```

### _EXPERIMENT CROPPER

#### `_experiment_cropper`

```text
---- Summary ----
Helper function to copy an experiment cropped to begin at a chosen time, with time
measured from there.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
start : float
    Time in minutes at which the crop begins.

---- Globals read ----
None.

---- Outputs ----
tuple
    (cropped experiment copy, last time in minutes).

---- Globals mutated ----
None.

---- Equations ----
t_new = t - start; rows with t_new < 0 are dropped.

---- Helpers ----
time_getter
```

### _FIGURE FINISHER

#### `_figure_finisher`

```text
---- Summary ----
Helper function to fit the margins to the drawn content, add the panel letters at
the top-left of each panel and fit again.

---- Inputs ----
fig : Figure
    Matplotlib figure.
config : dict
    Figure settings dictionary built in custom_config.py.
panels : list
    List of (letter, main axes, [axes of the panel]) tuples.
suptitle : Any
    Figure title text object, or None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Resizes the layout of ``fig`` and adds text to it (side effect).

---- Equations ----
None.

---- Helpers ----
figure_canvas_fitter
panel_letter_adder
```

### _HAEM BLOCK PLOTTER

#### `_haem_block_plotter`

```text
---- Summary ----
Helper function to draw the haem response: one row per haem, one column per addition
order, a line per group.

---- Inputs ----
fig : Figure
    Matplotlib figure.
spec : SubplotSpec
    Grid cell the block is drawn in.
orders : tuple
    Addition-order names (columns), in drawing order.
strains : tuple
    Group names (rows or bars), in drawing order.
triplicates : dict
    Across-run statistics per condition, from triplicate_averager (DATA_FORMAT.md).
conditions : dict
    Lookup {(strain, order): condition name}.
references : dict
    Lookup {order: experiment or None} used for the event tick labels.
config : dict
    Figure settings dictionary built in custom_config.py.
rows : list
    Haem row dictionaries {haem, label}.
haem_source : str
    Haem source key, for example 'delta_abs_od'.
tests : Optional[list]
    List collecting t-test comparisons, or None to skip the tests.
bars_above : bool
    True draws the top row's significance bars in the white space above the block
    (between it and the block above) instead of inside the axes.

---- Globals read ----
None.

---- Outputs ----
tuple
    (grid of axes [row][column], invisible axes carrying the shared y label).

---- Globals mutated ----
None. Adds axes to ``fig`` and appends to ``tests`` (side effects).

---- Equations ----
None.

---- Helpers ----
_haem_label_finder
_haem_label_pad_calculator
_legend_handle_builder
_measurement_finder
_outside_bar_drawer
_reference_level_finder
_response_axes_preparer
_response_series_drawer
_response_window_tester
_row_ylim_sharer
_tick_label_builder
_window_orderer
```

### _HAEM LABEL FINDER

#### `_haem_label_finder`

```text
---- Summary ----
Helper function to find the shared y label of the haem response rows.

---- Inputs ----
config : dict
    Figure settings dictionary built in custom_config.py.
metric : str
    Response metric: 'delta', 'change' or 'value'.
haem_source : str
    Haem source key, for example 'delta_abs_od'.

---- Globals read ----
None.

---- Outputs ----
str
    Label text from HAEM_RESPONSE_AXIS_LABELS for the metric and source.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### _HAEM LABEL PAD CALCULATOR

#### `_haem_label_pad_calculator`

```text
---- Summary ----
Helper function to calculate the points between the shared haem label and the haem
axes.

---- Inputs ----
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
None.

---- Outputs ----
float
    Label pad in points.

---- Globals mutated ----
None.

---- Equations ----
pad = 1.2 label font + 0.5 unit + 5 x 0.55 tick font + 0.5 unit (points).

---- Helpers ----
None.
```

### _HAEM ROW SELECTOR

#### `_haem_row_selector`

```text
---- Summary ----
Helper function to select the haem response rows to draw, in the order listed in
HAEM_RESPONSE_SHOW.

---- Inputs ----
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
None.

---- Outputs ----
list
    Row dictionaries {haem, label}. Every row is returned when HAEM_RESPONSE_SHOW is
    empty. Entries are matched to a row label or haem name ignoring case and
    punctuation.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
name_simplifier
```

### _HAEM SOURCE FINDER

#### `_haem_source_finder`

```text
---- Summary ----
Helper function to find the haem source that every condition's averages were
calculated from.

---- Inputs ----
triplicates : dict
    Across-run statistics per condition, from triplicate_averager (DATA_FORMAT.md).

---- Globals read ----
None.

---- Outputs ----
str
    Haem source key, for example 'delta_abs_od'. Raises ValueError if the conditions
    differ.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### _LAYOUT VALIDATOR

#### `_layout_validator`

```text
---- Summary ----
Helper function to check that the layout options of the publication figure are
recognised and to return the group and order lists.

---- Inputs ----
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
ORDER_TITLES, BLOCK_NAMES, RESPONSE_METRICS (module constants).

---- Outputs ----
tuple
    (orders, strains): addition orders (columns) and groups (rows), as tuples.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### _LEGEND HANDLE BUILDER

#### `_legend_handle_builder`

```text
---- Summary ----
Helper function to build legend entries showing each group's colour, line style and
marker.

---- Inputs ----
strains : tuple
    Group names (rows or bars), in drawing order.
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
None.

---- Outputs ----
list
    Line2D handles, one per group.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### _MEAN YLIM SETTER

#### `_mean_ylim_setter`

```text
---- Summary ----
Helper function to set the y range of a response panel from the group means (and
the baseline level) only, so that a single outlier run or a very large error bar
does not stretch the axis. Points and error bars beyond the range are clipped.

---- Inputs ----
ax : Axes
    Response panel, with the series already drawn.
series_list : list
    One list of window statistics per strain, as drawn by _response_series_drawer.
metric : str
    Response metric, which decides the field holding the mean.
baseline_level : Optional[float]
    Reference level that must stay in view (for example 100 for % of baseline).
margin : float
    Fraction of the mean range added above and below.

---- Globals read ----
None.

---- Outputs ----
None.

---- Globals mutated ----
None. Sets the y limits of ``ax`` (side effect); does nothing when no mean is
finite.

---- Equations ----
low = min(means) - margin x range; high = max(means) + margin x range, where the
range is max(means) - min(means) (at least 1 % of the largest absolute mean). When
all means are on one side of the baseline, the baseline side gets a 3 % margin.

---- Helpers ----
_metric_field_selector
```

### _MEASUREMENT FINDER

#### `_measurement_finder`

```text
---- Summary ----
Helper function to find the column matching a wanted name, ignoring case and
punctuation.

---- Inputs ----
available : Iterable
    Column names that are available.
wanted : str
    Name to look for.

---- Globals read ----
None.

---- Outputs ----
Optional[str]
    Matching column name, or None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
name_simplifier
```

### _METRIC FIELD SELECTOR

#### `_metric_field_selector`

```text
---- Summary ----
Helper function to name the keys of the triplicate statistics used by a response
metric.

---- Inputs ----
metric : str
    Response metric: 'delta', 'change' or 'value'.

---- Globals read ----
None.

---- Outputs ----
tuple
    (mean key, sem key, n key, per-run values key).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### _OCR BLOCK PLOTTER

#### `_ocr_block_plotter`

```text
---- Summary ----
Helper function to draw the OCR response (percent of each run's baseline, mean and
SEM across runs), one axes per addition order.

---- Inputs ----
fig : Figure
    Matplotlib figure.
spec : SubplotSpec
    Grid cell the block is drawn in.
orders : tuple
    Addition-order names (columns), in drawing order.
strains : tuple
    Group names (rows or bars), in drawing order.
triplicates : dict
    Across-run statistics per condition, from triplicate_averager (DATA_FORMAT.md).
conditions : dict
    Lookup {(strain, order): condition name}.
references : dict
    Lookup {order: experiment or None} used for the event tick labels.
config : dict
    Figure settings dictionary built in custom_config.py.
tests : Optional[list]
    List collecting t-test comparisons, or None to skip the tests.

---- Globals read ----
None.

---- Outputs ----
list
    The axes, one per addition order.

---- Globals mutated ----
None. Adds axes to ``fig`` and appends to ``tests`` (side effects).

---- Equations ----
None.

---- Helpers ----
_column_chooser
_legend_handle_builder
_response_axes_preparer
_response_series_drawer
_response_window_tester
_row_ylim_sharer
_tick_label_builder
_window_orderer
```

### _OUTSIDE BAR DRAWER

#### `_outside_bar_drawer`

```text
---- Summary ----
Helper function to draw the significance bars stored by _response_window_tester in
the white space just above an axes, so the plot keeps its full height.

---- Inputs ----
ax : Axes
    Response panel whose y range is final.
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Draws on ``ax`` (side effect).

---- Equations ----
None.

---- Helpers ----
_test_bar_drawer
```

### _P VALUE ADJUSTER

#### `_p_value_adjuster`

```text
---- Summary ----
Helper function to adjust a list of p values for multiple comparisons.

---- Inputs ----
p_values : Iterable
    Raw p values.
method : str
    'none', 'bonferroni' or 'holm'.

---- Globals read ----
None.

---- Outputs ----
np.ndarray
    Adjusted p values, same order as the input.

---- Globals mutated ----
None.

---- Equations ----
Bonferroni: p_adj = min(n p, 1). Holm: sort ascending, p_adj(i) = min(max over j <=
i of (n - j) p(j), 1) with j counted from 0.

---- Helpers ----
None.
```

### _REFERENCE LEVEL FINDER

#### `_reference_level_finder`

```text
---- Summary ----
Helper function to find the height of the dashed reference line of the haem
response.

---- Inputs ----
metric : str
    Response metric: 'delta', 'change' or 'value'.
haem_source : str
    Haem source key, for example 'delta_abs_od'.

---- Globals read ----
None.

---- Outputs ----
Optional[float]
    0 for a change, 100 for percent of baseline, 0 for a delta abs value, otherwise
    None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### _REFERENCE SELECTOR

#### `_reference_selector`

```text
---- Summary ----
Helper function to pick, for each addition order, the first run of the first
available group (used for the event tick labels).

---- Inputs ----
experiments : dict
    Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.
triplicates : dict
    Across-run statistics per condition, from triplicate_averager (DATA_FORMAT.md).
conditions : dict
    Lookup {(strain, order): condition name}.
orders : tuple
    Addition-order names (columns), in drawing order.
strains : tuple
    Group names (rows or bars), in drawing order.

---- Globals read ----
None.

---- Outputs ----
dict
    {order: experiment or None}.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### _RESPONSE AXES PREPARER

#### `_response_axes_preparer`

```text
---- Summary ----
Helper function to draw the baseline reference line and set the window ticks of a
response panel.

---- Inputs ----
ax : Axes
    Matplotlib axes to draw on.
window_names : list
    Averaging window names, for example ['average0', 'average1'].
tick_labels : list
    Tick label of every window.
show_xlabels : bool
    True to write the tick labels.
config : dict
    Figure settings dictionary built in custom_config.py.
baseline_level : Optional[float]
    Height of the reference line, or None for no line.

---- Globals read ----
None.

---- Outputs ----
np.ndarray
    x positions of the windows.

---- Globals mutated ----
None. Changes the style of ``ax`` (side effect).

---- Equations ----
None.

---- Helpers ----
_axes_styler
```

### _RESPONSE METRIC CHECKER

#### `_response_metric_checker`

```text
---- Summary ----
Helper function to reject a percent-of-baseline response for the delta abs sources,
which start at 0.

---- Inputs ----
metric : str
    Response metric: 'delta', 'change' or 'value'.
haem_source : str
    Haem source key, for example 'delta_abs_od'.

---- Globals read ----
DELTA_HAEM_SOURCES (schema constant).

---- Outputs ----
None
    Nothing. Raises ValueError for the combination that is not allowed.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### _RESPONSE SERIES DRAWER

#### `_response_series_drawer`

```text
---- Summary ----
Helper function to plot every run as a point, the mean as a line and SEM error bars
for one group.

---- Inputs ----
ax : Axes
    Matplotlib axes to draw on.
x : Iterable
    x positions of the windows.
stats_list : list
    Statistics dictionary (or None) for each window.
style : dict
    Group style: colour, linestyle, marker.
config : dict
    Figure settings dictionary built in custom_config.py.
label : Optional[str]
    Unused legend text.
metric : str
    Response metric: 'delta', 'change' or 'value'.
offset : float
    Horizontal shift in x units so groups sit side by side.

---- Globals read ----
None.

---- Outputs ----
bool
    True if anything was drawn.

---- Globals mutated ----
None. Draws on ``ax`` (side effect).

---- Equations ----
None.

---- Helpers ----
_metric_field_selector
```

### _RESPONSE WINDOW TESTER

#### `_response_window_tester`

```text
---- Summary ----
Helper function to run a Student t-test between the two groups at every window of a
response panel and mark the significant windows.

---- Inputs ----
ax : Axes
    Matplotlib axes to draw on.
x : np.ndarray
    x positions of the windows.
windows : list
    Window names.
series_by_strain : dict
    {strain: [statistics per window]}.
strains : tuple
    Group names (rows or bars), in drawing order.
metric : str
    Response metric: 'delta', 'change' or 'value'.
config : dict
    Figure settings dictionary built in custom_config.py.
panel_name : str
    Panel name written to the test table.
tests : list
    List collecting one dictionary per t-test comparison.
outside : bool
    True keeps the axis range as it is and stores the marks on ``ax`` for
    _outside_bar_drawer, which draws them in the space above the axes.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Appends one dictionary per comparison to ``tests`` and draws on ``ax`` (side
effects); with ``outside`` it sets ``ax.outside_marks`` instead of drawing.

---- Equations ----
Equal-variance Student t-test per window; p values adjusted across the windows of
the panel (RESPONSE_TEST_CORRECTION); significant if p_adj < RESPONSE_TEST_ALPHA.

---- Helpers ----
_metric_field_selector
_p_value_adjuster
_test_bar_drawer
```

### _ROW YLIM SHARER

#### `_row_ylim_sharer`

```text
---- Summary ----
Helper function to give every axes in a row the union of their y ranges.

---- Inputs ----
axes_row : list
    Axes of one row.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Sets the y limits of the axes (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

### _SIGNIFICANCE BAR DRAWER

#### `_significance_bar_drawer`

```text
---- Summary ----
Helper function to draw a bracket between two x positions with text centred above
it.

---- Inputs ----
ax : Axes
    Matplotlib axes to draw on.
x_left : float
    Left end of the bracket (data units).
x_right : float
    Right end of the bracket (data units).
y : float
    Height of the bracket (data units).
text : str
    Text written above the bracket.
tick_size : float
    Tick label size in points.
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Draws on ``ax`` (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

### _SIGNIFICANCE FORMATTER

#### `_significance_formatter`

```text
---- Summary ----
Helper function to format a p value as stars or as text.

---- Inputs ----
p_value : float
    p value.
style : str
    'stars' or 'p'.

---- Globals read ----
None.

---- Outputs ----
str
    '***', '**', '*' or 'ns' (stars style) or the p value text.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### _TEST BAR DRAWER

#### `_test_bar_drawer`

```text
---- Summary ----
Helper function to draw a small bracket joining the two groups' points at one window
with text above it.

---- Inputs ----
ax : Axes
    Matplotlib axes to draw on.
x_left : float
    Left end (data units).
x_right : float
    Right end (data units).
y : float
    Data height the clearances are measured from.
text : str
    Stars written above the bracket.
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Draws on ``ax`` (side effect).

---- Equations ----
None.

---- Helpers ----
_offset_transformer
```

### _TICK LABEL BUILDER

#### `_tick_label_builder`

```text
---- Summary ----
Helper function to build the x tick labels of the averaging windows: Baseline, then
the addition that precedes each window.

---- Inputs ----
experiment : Optional[dict]
    Reference experiment whose events label the windows, or None.
window_names : list
    Averaging window names, for example ['average0', 'average1'].

---- Globals read ----
None.

---- Outputs ----
list
    One label per window; additions are written as label and concentration.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
finite_float_converter
```

### _WINDOW ORDERER

#### `_window_orderer`

```text
---- Summary ----
Helper function to list the averaging windows present in any condition of one
addition order.

---- Inputs ----
order : str
    Addition order name.
strains : tuple
    Group names (rows or bars), in drawing order.
triplicates : dict
    Across-run statistics per condition, from triplicate_averager (DATA_FORMAT.md).
conditions : dict
    Lookup {(strain, order): condition name}.

---- Globals read ----
None.

---- Outputs ----
list
    Window names in numerical order.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### EXEMPLAR FIGURE PLOTTER

#### `exemplar_figure_plotter`

```text
---- Summary ----
Main function to build the exemplar figure: one run per condition, each drawn by the
individual plotter in its own quadrant.

---- Inputs ----
experiments : dict
    Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.
config : dict
    Exemplar figure settings from custom_config.exemplar_config_builder.
individual_config : dict
    Individual-experiment plot settings, as returned by Config.plot_config in
    config.py.

---- Globals read ----
None.

---- Outputs ----
tuple
    (fig, axes); axes maps (strain, order) to its list of axes and 'letters' to
    {letter: experiment name}.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_crop_start_finder
_exemplar_gap_calculator
_exemplar_plotter
_exemplar_selector
_experiment_cropper
_figure_finisher
experiment_title_builder
stack_legend_drawer
watermark_style_builder
```

### PUBLICATION FIGURE PLOTTER

#### `publication_figure_plotter`

```text
---- Summary ----
Main function to build the publication figure: baseline OCR, OCR response and haem
response blocks.

---- Inputs ----
experiments : dict
    Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.
triplicates : dict
    Across-run statistics from triplicate_averager.
config : dict
    Publication figure settings from custom_config.publication_config_builder.

---- Globals read ----
None.

---- Outputs ----
tuple
    (fig, axes); axes holds 'baseline', 'ocr_response', 'haem_response' and
    'letters' ({letter: panel name}).

---- Globals mutated ----
None. Stores the t-test table on the returned figure as ``fig.response_tests``.

---- Equations ----
None.

---- Helpers ----
_baseline_bar_plotter
_block_gap_calculator
_condition_indexer
_experiment_classifier
_figure_finisher
_haem_block_plotter
_haem_row_selector
_haem_source_finder
_layout_validator
_ocr_block_plotter
_panel_labeller
_reference_selector
_response_metric_checker
```

### PUBLICATION FIGURE SAVER

#### `publication_figure_saver`

```text
---- Summary ----
Main function to save a publication or exemplar figure at its exact size, plus the
t-test table when there is one.

---- Inputs ----
fig : Figure
    Figure returned by publication_figure_plotter or exemplar_figure_plotter.
export_root : Path
    Results folder.
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
None.

---- Outputs ----
list
    Paths of the files written.

---- Globals mutated ----
None. Writes the figure under <export_root>/<OUTPUT_SUBFOLDER> and the test table
under <export_root>/<DATA_SUBFOLDER> (side effects).

---- Equations ----
None.

---- Helpers ----
figure_saver
```

## `utils_custom/run_namer.py`

Experiment (run) name parsing: conditions, run numbers, groups and hours.

### RUN NAMER HELPERS

#### `_group_matcher`

```text
---- Summary ----
Helper function to find the first group word that appears in an experiment name.

---- Inputs ----
name : str
    Experiment name.
groups : Sequence[str]
    Group names in priority order.

---- Globals read ----
None.

---- Outputs ----
Optional[str]
    Matching group, or None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_natural_sorter`

```text
---- Summary ----
Helper function to build a sort key that orders numbers inside names numerically.

---- Inputs ----
name : str
    Name to sort.

---- Globals read ----
None.

---- Outputs ----
list
    Alternating text and integer parts.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_order_sorter`

```text
---- Summary ----
Helper function to build the sort key of one (group, name, experiment) item.

---- Inputs ----
item : tuple
    (group, name, experiment).
groups : Sequence[str]
    Group names in the wanted order.

---- Globals read ----
None.

---- Outputs ----
tuple
    (group index, no-hours flag, hours, natural name key).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_natural_sorter
hours_parser
```

### MAIN FUNCTIONS

#### `condition_classifier`

```text
---- Summary ----
Main function to identify the strain and the addition order from a condition name.

---- Inputs ----
condition : str
    Condition name such as 'knockdown_kcn_then_bd'.

---- Globals read ----
None.

---- Outputs ----
tuple
    (strain, order). strain is 'knockdown' (the word knockdown or a kd token),
    'control' or None; order is 'bd_then_kcn' or 'kcn_then_bd' from the position of
    the bd and kcn tokens, or None.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `condition_grouper`

```text
---- Summary ----
Main function to group experiments by condition and run number.

---- Inputs ----
experiments : dict
    Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.

---- Globals read ----
None.

---- Outputs ----
dict
    {condition: {run number: experiment}}. Experiments without a run suffix are
    skipped with a message; a duplicate run number raises ValueError.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
run_name_parser
```

#### `experiment_classifier`

```text
---- Summary ----
Helper function to identify the strain, addition order and run number from an
experiment name.

---- Inputs ----
name : str
    Experiment name such as 'control_kcn_then_bd_run1'.

---- Globals read ----
None.

---- Outputs ----
tuple
    (strain, order, run); entries are None where they cannot be identified.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
condition_classifier
run_name_parser
```

#### `group_assigner`

```text
---- Summary ----
Main function to give every experiment a group from its name and to order the
experiments by group and then by hours.

---- Inputs ----
experiments : dict
    Experiment dictionaries keyed by experiment name (DATA_FORMAT.md).
groups : Sequence[str]
    Group names in the order they should appear, for example
    ('control', 'knockdown'). An experiment belongs to the first group whose name
    is a word (or the start) of its name.

---- Globals read ----
None.

---- Outputs ----
dict
    Same experiments, ordered, each with a 'group' key added. Experiments that
    match no group are left out with a message.

---- Globals mutated ----
None. Adds the 'group' key to the experiment dictionaries (side effect).

---- Equations ----
None.

---- Helpers ----
_group_matcher
_order_sorter
```

#### `hours_parser`

```text
---- Summary ----
Main function to read the number of hours from an experiment name.

---- Inputs ----
name : str
    Experiment name such as 'control_7hours'.

---- Globals read ----
HOURS_PATTERN (module constant).

---- Outputs ----
Optional[float]
    Hours, or None if the name has none.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `run_name_lister`

```text
---- Summary ----
Main function to describe how each experiment name is read by the haem and OCR
response figures, for showing to the user before they choose.

---- Inputs ----
names : Sequence[str]
    Experiment names (the .paf file names without the extension).

---- Globals read ----
None.

---- Outputs ----
list
    One dictionary per name: {name, condition, run, strain, order}; entries are
    None where the name does not identify them.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
condition_classifier
run_name_parser
```

#### `run_name_parser`

```text
---- Summary ----
Main function to split an experiment name of the form <condition>_run<N> into its
condition and run number.

---- Inputs ----
name : str
    Experiment name, for example 'knockdown_kcn_then_bd_run1'.

---- Globals read ----
RUN_NAME_PATTERN (module constant).

---- Outputs ----
Optional[tuple]
    (condition, run number), or None if the name has no run suffix.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

## `utils_custom/spectral_difference.py`

Event-window spectral averages, their difference spectrum and its decomposition.

### MAIN FUNCTIONS

#### `difference_spectrum_calculator`

```text
---- Summary ----
Main function to subtract one averaged spectrum from another.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
minuend : str
    Window name or role ('penultimate', 'final') to subtract from.
subtrahend : str
    Window name or role to subtract.

---- Globals read ----
None.

---- Outputs ----
dict
    The experiment, with difference_spectrum added (DATA_FORMAT.md).

---- Globals mutated ----
None. Adds ``difference_spectrum`` to the experiment (side effect).

---- Equations ----
difference = mean spectrum of the minuend window - mean spectrum of the subtrahend
window.

---- Helpers ----
None.
```

#### `difference_spectrum_decomposer`

```text
---- Summary ----
Main function to decompose the difference spectrum into haem contributions using the
shared decomposition.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
fit : dict
    Fit dictionary from import_fit: {haem_list, data}.
degree_of_scatter : int
    Number of scatter terms in the decomposition.
haemfactor : float
    Scale factor applied to the fit spectra.
percent_basis : str
    'signed' (coefficient / sum of coefficients) or 'absolute' (coefficient / sum of
    absolute coefficients).

---- Globals read ----
None.

---- Outputs ----
dict
    The experiment, with difference_decomposition added (DATA_FORMAT.md).

---- Globals mutated ----
None. Adds ``difference_decomposition`` to the experiment (side effect).

---- Equations ----
percent_i = 100 c_i / sum(c) ('signed') or 100 c_i / sum(|c|) ('absolute'); NaN when
the denominator is about 0.

---- Helpers ----
spectrum_decomposer
```

#### `spectral_averager`

```text
---- Summary ----
Main function to average the chosen spectra in each event window.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
dataset_name : str
    Spectrometer dataset, for example 'Cyt'.
spectrum_type : str
    Spectrum field, for example 'attenuation'.
window_minutes : float
    Length of each window in minutes.
gap_minutes : float
    Gap between a window and the next addition in minutes.
final_window_gap_minutes : float
    Gap between the last window and the end of the data in minutes.
expected_events : Optional[int]
    Raise if the run has a different number of events; None skips the check.

---- Globals read ----
None.

---- Outputs ----
dict
    The experiment, with spectral_averages added (DATA_FORMAT.md).

---- Globals mutated ----
None. Adds ``spectral_averages`` to the experiment (side effect).

---- Equations ----
None.

---- Helpers ----
window_definer
```

#### `window_definer`

```text
---- Summary ----
Helper function to lay out the averaging windows of one run.

---- Inputs ----
event_times : Iterable
    Event times in minutes.
recording_end : float
    Last time of the recording in minutes.
window_minutes : float
    Length of each window.
gap_minutes : float
    Gap between the end of a window and the next addition.
final_window_gap_minutes : float
    Gap between the last window and the end of the data.

---- Globals read ----
None.

---- Outputs ----
list
    [(name, start, end, previous event time or None), ...].

---- Globals mutated ----
None.

---- Equations ----
average0 ends gap_minutes before the first addition; averageN ends gap_minutes
before addition N + 1; the last window ends final_window_gap_minutes before the end.
start = end - window_minutes.

---- Helpers ----
None.
```

## `utils_custom/time_response_exporter.py`

Export of the time response to a workbook that can be checked by hand.

### HELPERS

#### `_difference_sheet_writer`

```text
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
```

#### `_haem_sheet_writer`

```text
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
```

#### `_picks_sheet_writer`

```text
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
```

#### `_waterfall_sheet_writer`

```text
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
```

### MAIN FUNCTIONS

#### `time_response_exporter`

```text
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
```

## `utils_custom/time_response_plotter.py`

Time response figure: waterfalls, example time courses and decompositions.

### TIME RESPONSE PLOTTER HELPERS

#### `_event_label_height_calculator`

```text
---- Summary ----
Helper function to calculate the height the rotated event labels above the example
time courses need.

---- Inputs ----
experiments : list
    Example experiments.
individual_config : dict
    Individual-experiment plot settings, as returned by Config.plot_config in
    config.py.

---- Globals read ----
None.

---- Outputs ----
float
    Height in points; 0 when the labels are not drawn on top.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
concentration_formatter
text_extent_calculator
```

#### `_example_finder`

```text
---- Summary ----
Helper function to find the experiment of one group at a given number of hours.

---- Inputs ----
groups : dict
    {group: [(time label, experiment), ...]}.
group : str
    Group name.
hours : float
    Hours in the experiment name.

---- Globals read ----
None.

---- Outputs ----
tuple
    (time label, experiment). Raises ValueError if there is none.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
hours_parser
```

#### `_example_viewer`

```text
---- Summary ----
Helper function to copy an experiment so that its individual figure shows only the
two windows its difference spectrum came from.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.

---- Globals read ----
None.

---- Outputs ----
dict
    Copy with averages holding the penultimate and final spectral windows.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_haem_scale_sharer`

```text
---- Summary ----
Helper function to give each haem the same y range in every stack, so that all the
a haems share one scale, all the cc haems another, and so on.

---- Inputs ----
stacks : list
    Axes lists of the kinetic traces (each from experiment_drawer).
config : dict
    Figure settings; uses HAEM_Y_MAX_TICKS to thin the tick labels again.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Sets the y limits and ticks of the haem axes (side effect).

---- Equations ----
Limits are the union of the stacks' limits for the same haem.

---- Helpers ----
None.
```

#### `_haem_window_drawer`

```text
---- Summary ----
Helper function to shade, behind the spectra, a window around the peak of every
haem in the haem's own colour, to show where each haem should appear.

---- Inputs ----
ax : Axes
    Matplotlib axes with wavelength on the x axis.
decomposition : dict
    difference_decomposition of an experiment (DATA_FORMAT.md).
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
config keys HAEM_COLOURS, HAEM_WINDOW_HALF_WIDTH_NM and HAEM_WINDOW_ALPHA.

---- Outputs ----
None

---- Globals mutated ----
None. Draws on ``ax`` and leaves its x limits as they were (side effect).

---- Equations ----
window = peak +- HAEM_WINDOW_HALF_WIDTH_NM, where the peak is the wavelength of the
largest absolute value of the haem's fitted component.

---- Helpers ----
name_simplifier
```

#### `_legend_drawer`

```text
---- Summary ----
Helper function to draw a legend in the journal style: small text and an optional
thin box.

---- Inputs ----
ax : Axes
    Matplotlib axes to draw on.
config : dict
    Figure settings dictionary built in custom_config.py.
location : str
    Matplotlib legend location.
columns : Optional[int]
    Number of legend columns, or None for the setting.
outside : bool
    True puts the legend in the white space to the right of the axes.
anchor : Optional[tuple]
    Axes-coordinate anchor of the legend's ``location`` point, which overrides
    ``outside``.

---- Globals read ----
None.

---- Outputs ----
Any
    The legend.

---- Globals mutated ----
None. Adds a legend to ``ax`` (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_time_axes_styler`

```text
---- Summary ----
Helper function to apply the tick direction, label size and spine style.

---- Inputs ----
ax : Axes
    Matplotlib axes to draw on.
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes the style of ``ax`` (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_time_gap_calculator`

```text
---- Summary ----
Helper function to calculate the gaps of the time response figure: the white space
under the first and under the second row, and the gap between columns.

---- Inputs ----
config : dict
    Figure settings dictionary built in custom_config.py.
individual_config : dict
    Individual-experiment plot settings, as returned by Config.plot_config in
    config.py.
label_height_pt : float
    Height of the event labels in points.
legend_rows : int
    Number of text rows of the legends that hang under the second row.

---- Globals read ----
None.

---- Outputs ----
tuple
    (gap under row 1, gap under row 2, column gap), all in points.

---- Globals mutated ----
None.

---- Equations ----
x_block = 1.2 tick + 0.5 unit + label pad + 1.2 label; gap 1 = x_block + max(event
label height, 1.2 title + 0.8 unit) + 1.0 unit; gap 2 = x_block + legend rows x 1.35
legend font + 1.2 unit + 1.2 title + 0.8 unit + 1.0 unit; column_gap = 1.2 label +
0.5 unit + 5 x 0.55 tick + 0.5 unit + 1.5 unit.

---- Helpers ----
None.
```

#### `_title_styler`

```text
---- Summary ----
Helper function to set a panel title in the figure style.

---- Inputs ----
ax : Axes
    Matplotlib axes to draw on.
text : str
    Title text.
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Sets the title of ``ax`` (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `decomposition_plotter`

```text
---- Summary ----
Main function to draw a difference spectrum with its scatter-free fit, residual and
each haem contribution.

---- Inputs ----
ax : Axes
    Matplotlib axes to draw on.
decomposition : dict
    difference_decomposition of an experiment (DATA_FORMAT.md).
config : dict
    Figure settings dictionary built in custom_config.py.
show_legend : bool
    True draws the legend inside the axes; False leaves it to the caller.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Draws on ``ax`` (side effect).

---- Equations ----
None.

---- Helpers ----
_haem_window_drawer
_legend_drawer
_time_axes_styler
name_simplifier
```

#### `group_collector`

```text
---- Summary ----
Main function to collect the decomposed experiments of each group, with their time
labels.

---- Inputs ----
experiments : dict
    Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.
config : dict
    Figure settings dictionary built in custom_config.py.

---- Globals read ----
None.

---- Outputs ----
dict
    {group: [(time label, experiment), ...]}. Experiments without a difference
    decomposition are reported and left out; ValueError if a group is empty.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
time_label_builder
```

#### `shared_baseline_subtracter`

```text
---- Summary ----
Main function to subtract one shared polynomial baseline, fitted to the mean
spectrum, from every spectrum.

---- Inputs ----
wavelengths : np.ndarray
    Wavelengths, shape (n_wavelengths, n_spectra), nm.
spectra : np.ndarray
    Spectra, shape (n_wavelengths, n_spectra).
x_min : Optional[float]
    Lower wavelength of the fit range, or None.
x_max : Optional[float]
    Upper wavelength of the fit range, or None.
degree : int
    Polynomial degree, at least 1.

---- Globals read ----
None.

---- Outputs ----
tuple
    (corrected spectra, shared baseline), both shaped like ``spectra``.

---- Globals mutated ----
None.

---- Equations ----
baseline(w) = polynomial fitted to mean over spectra of S(w) within [x_min, x_max];
corrected = S - baseline.

---- Helpers ----
None.
```

#### `time_label_builder`

```text
---- Summary ----
Main function to build the label of a time point from the experiment name.

---- Inputs ----
experiment_name : str
    Experiment name such as 'control_7hours'.
label_format : str
    Format string with an {hours} field.

---- Globals read ----
None.

---- Outputs ----
str
    For example '7 hours'; the experiment name when it contains no hours.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
hours_parser
```

#### `time_response_figure_plotter`

```text
---- Summary ----
Main function to build the time response figure as a 3 x 3 grid. Plots 1 and 4 are
the waterfalls of the two groups, plots 2-3 and 5-6 are two kinetic traces (each
spanning two columns) and plots 7, 8 and 9 are three decomposition plots.

---- Inputs ----
experiments : dict
    Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.
config : dict
    Time response settings from custom_config.time_response_config_builder.
individual_config : dict
    Individual-experiment plot settings, as returned by Config.plot_config in
    config.py.

---- Globals read ----
None.

---- Outputs ----
tuple
    (fig, axes); axes maps the panel letters 'A'-'G' (reading order) to axes; the
    kinetic traces give their list of axes.

---- Globals mutated ----
None. Sets ``fig.time_response_picks`` (the examples shown, used by the exporter)
(side effect).

---- Equations ----
The legend of the waterfalls hangs under plot 4 and the legend of the kinetic traces
under plots 5-6, both in the gap above the decomposition row; the three
decomposition plots share the width left of one legend at the far right.

---- Helpers ----
_event_label_height_calculator
_example_finder
_example_viewer
_haem_scale_sharer
_time_gap_calculator
_title_styler
decomposition_plotter
experiment_drawer
figure_canvas_fitter
gap_space_calculator
group_collector
hours_parser
panel_letter_adder
stack_legend_drawer
waterfall_plotter
```

#### `waterfall_plotter`

```text
---- Summary ----
Main function to draw the offset difference spectra of one group, first time point
at the top, with additive peak alignment.

---- Inputs ----
ax : Axes
    Matplotlib axes to draw on.
items : list
    [(time label, experiment), ...] of one group.
config : dict
    Figure settings dictionary built in custom_config.py.
show_legend : bool
    True to draw the legend.
marked : Optional[dict]
    {time label: text} written in black just past the right end of that trace; the
    text is the letter of the kinetic trace panel drawn from that time point.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Draws on ``ax`` (side effect).

---- Equations ----
aligned = S + (1 - max of S within [ALIGN_MIN, ALIGN_MAX]); shifted_i = aligned_i -
min(aligned_i) + (n - 1 - i) x offset; offset defaults to 0.75 x the largest span.

---- Helpers ----
_haem_window_drawer
_legend_drawer
_time_axes_styler
shared_baseline_subtracter
```

## `utils_custom/triplicate_averager.py`

Across-run (triplicate) statistics of the event-window averages.

### TRIPLICATE AVERAGER HELPERS

#### `_run_summariser`

```text
---- Summary ----
Helper function to summarise the finite values of one window across runs.

---- Inputs ----
values : Iterable
    Values to summarise (one per run).

---- Globals read ----
None.

---- Outputs ----
tuple
    (mean, sample SD, SEM, N). SD and SEM are NaN for N < 2; all NaN with N = 0 when
    no value is finite.

---- Globals mutated ----
None.

---- Equations ----
SD = sqrt(sum((x - mean)^2) / (N - 1)); SEM = SD / sqrt(N).

---- Helpers ----
None.
```

#### `_run_value_getter`

```text
---- Summary ----
Helper function to read one statistic of one window and measurement for every run.

---- Inputs ----
windows_by_run : dict
    {run number: {window name: window record}} from the runs' averages.
window_name : str
    Window name such as 'average3'.
kind : str
    'vo2' or 'haem'.
measurement : str
    Measurement (column) name.
field : str
    Statistic name: 'mean', 'sd', 'change' or 'delta'.

---- Globals read ----
None.

---- Outputs ----
dict
    {run number: value}, NaN where a run lacks the window.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_window_sorter`

```text
---- Summary ----
Helper function to sort averaging window names numerically.

---- Inputs ----
window_name : str
    Window name such as 'average3'.

---- Globals read ----
None.

---- Outputs ----
int
    Window number.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `triplicate_averager`

```text
---- Summary ----
Main function to combine the per-experiment event averages across the runs of each
condition.

---- Inputs ----
experiments : dict
    Experiment dictionaries keyed by experiment name, as defined in DATA_FORMAT.md.
min_runs : int
    Conditions with fewer runs that have averages are skipped.

---- Globals read ----
None.

---- Outputs ----
dict
    {condition: result}; result holds runs, run_numbers, windows, window_times,
    settings and, for vo2 and haem, per-window statistics (DATA_FORMAT.md).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_run_summariser
_run_value_getter
_window_sorter
condition_grouper
```

## `utils_custom/triplicate_exporter.py`

Export of the across-run (triplicate) statistics to an Excel workbook.

### TRIPLICATE EXPORTER

#### `triplicate_exporter`

```text
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
```

## `utils_custom/workbook_helpers.py`

Cell formats and cell writers shared by the workbook exporters.

### MAIN FUNCTIONS

#### `formula_writer`

```text
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
```

#### `number_writer`

```text
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
```

#### `workbook_formats_builder`

```text
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
```

## `utils_shared/attenuation.py`

Convert transmission spectra to the attenuation spectra used for decomposition.

### MAIN FUNCTIONS

#### `attenuation_converter`

```text
---- Summary ----
Main function to convert transmission spectra to attenuation (log10 of the
transmittance).

---- Inputs ----
transmission : Union[Sequence[float], np.ndarray]
    Transmission values, any shape.
mode : str
    Meaning of the input: 'fraction' (0-1), 'percentage' (0-100) or 'absorbance'
    (already converted, returned as is).

---- Globals read ----
None.

---- Outputs ----
np.ndarray
    Attenuation with the shape of the input. Zero, negative or non-finite
    transmission becomes NaN. Raises ValueError for an unknown mode.

---- Globals mutated ----
None.

---- Equations ----
attenuation = log10(T), where T is the transmittance (fraction). This is the
NEGATIVE of the conventional -log10(T); the decomposition basis spectra are negated
too, so the two signs cancel (change both together or neither).

---- Helpers ----
None.
```

#### `experiment_attenuation_adder`

```text
---- Summary ----
Main function to add an attenuation array to the spectral datasets of an experiment.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
mode : str
    Transmission mode passed to attenuation_converter ('fraction', 'percentage' or
    'absorbance').
datasets : Optional[Sequence[str]]
    Dataset names to convert; None converts all of them.

---- Globals read ----
None.

---- Outputs ----
dict
    The same experiment dictionary. Raises ValueError if a transmission array is not
    2D.

---- Globals mutated ----
experiment: adds raw_spectra[dataset]["attenuation"] (n_spectra x n_wavelengths) for
each converted dataset; prints a warning with the number of blank values (side
effect).

---- Equations ----
None.

---- Helpers ----
attenuation_converter
```

## `utils_shared/averaging.py`

Event-window averaging of OCR and haem data for one experiment.

### AVERAGING HELPERS

#### `_baseline_change_adder`

```text
---- Summary ----
Helper function to add the change from the baseline window to the statistics of a
window.

---- Inputs ----
window_stats : Dict[str, Dict[str, float]]
    Statistics of one window, from window_statistics_calculator; modified in place.
baseline_stats : Dict[str, Dict[str, float]]
    Statistics of the baseline window (average0).
percent_of_baseline : bool
    False for sources that already are a change from a reference (baseline near 0),
    where a percentage is meaningless.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
window_stats: adds "delta" and "change" to every column.

---- Equations ----
delta = mean - baseline_mean; change = mean / baseline_mean x 100 (NaN if
percent_of_baseline is False, the baseline is 0 or a value is not finite).

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `experiment_averages_calculator`

```text
---- Summary ----
Main function to calculate event-window statistics for VoO2 and haem data and store
them in the experiment.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
window_minutes : float
    Length of each averaging window, in minutes (> 0).
gap_minutes : float
    How long before the next addition each window ends, in minutes (>= 0).
final_window_gap_minutes : float
    How long before the end of the recording the last window ends, in minutes (>=
    0).
vo2_source : Optional[str]
    VoO2 source key (e.g. 'od', 'raw', 'percent'); None leaves VoO2 out.
haem_source : Optional[str]
    Haem source key (e.g. 'abs', 'delta_abs_od'); None leaves the haems out.

---- Globals read ----
schema.VO2_KEYS, HAEM_KEYS and DELTA_HAEM_SOURCES; schema.resolve_source, get_times.

---- Outputs ----
dict
    The same experiment dictionary. Raises ValueError for invalid settings, no
    source, no events, invalid times or windows that do not fit between the
    additions.

---- Globals mutated ----
experiment: adds experiment["averages"] = {"settings", "windows"} (layout in
DATA_FORMAT.md).

---- Equations ----
average0 ends gap_minutes before the first event; averageN ends gap_minutes before
event N+1 (final_window_gap_minutes before the end of the recording for the last
event); each window starts window_minutes before its end. change = mean /
mean(average0) x 100 (NaN for delta abs sources); delta = mean - mean(average0).

---- Helpers ----
_baseline_change_adder
source_resolver
time_getter
window_statistics_calculator
```

#### `window_statistics_calculator`

```text
---- Summary ----
Main function to calculate the mean and sample SD of every measurement column inside
a time window.

---- Inputs ----
df : pd.DataFrame
    Data frame with a time column and measurement columns (DATA_FORMAT.md).
start_time : float
    Window start, in minutes.
end_time : float
    Window end, in minutes.

---- Globals read ----
None.

---- Outputs ----
Dict[str, Dict[str, float]]
    {column: {"mean", "sd"}}. Values are NaN when no finite point falls in the
    window (SD: fewer than two).

---- Globals mutated ----
None.

---- Equations ----
mean = sum(x) / n; SD = sqrt(sum((x - mean)^2) / (n - 1)) over the finite points
with start_time <= t <= end_time.

---- Helpers ----
measurement_column_finder
time_getter
value_getter
```

## `utils_shared/comparison_plotter.py`

Two experiments side by side in one figure.

### COMPARISON PLOTTER HELPERS

#### `_overhang_calculator`

```text
---- Summary ----
Helper function to measure how far the labels of a plot stick out to the left and
right of its main axes.

---- Inputs ----
fig : Figure
    Matplotlib figure.
members : List[Axes]
    All axes of the plot.
main : Axes
    Main axes the overhang is measured from.

---- Globals read ----
Needs a figure that has been drawn or can be rendered.

---- Outputs ----
Tuple[float, float]
    (points to the left, points to the right).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_renderer_getter
```

#### `_renderer_getter`

```text
---- Summary ----
Helper function to get the renderer of a figure canvas.

---- Inputs ----
fig : Figure
    Matplotlib figure.

---- Globals read ----
None.

---- Outputs ----
Any
    Matplotlib renderer.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `comparison_figure_plotter`

```text
---- Summary ----
Main function to draw two experiments side by side with their own y axes, panel
letters a and b and a gap sized to their labels, and save it as svg and png.

---- Inputs ----
first : dict
    Experiment drawn on the left (panel a).
second : dict
    Experiment drawn on the right (panel b).
config : dict
    Individual-experiment plot settings (config.py); uses LAYOUT_PAD_PT, FIGURE_DPI,
    TITLE_GAP_PT and TIGHT_BBOX.
export_root : Path
    Results folder.
figure_size : Tuple[float, float]
    (width, height) of the whole figure in inches.
spec : dict
    Journal specification (config.JOURNAL_SPECS entry).
share_time_axis : bool
    True gives both plots the same time range.

---- Globals read ----
GAP_EXTRA_PT_PER_PAD (module constant).

---- Outputs ----
str
    File stem of the saved figure.

---- Globals mutated ----
None. Writes <export_root>/<stem>.svg and .png (side effect); the figure
is closed before returning.

---- Equations ----
None.

---- Helpers ----
_overhang_calculator
experiment_drawer
figure_canvas_fitter
figure_saver
file_name_sanitiser
gap_space_calculator
panel_letter_adder
watermark_style_builder
```

## `utils_shared/experiment_processing.py`

Reading and processing of one experiment (everything before the figure and the export).

### MAIN FUNCTIONS

#### `event_settings_merger`

```text
---- Summary ----
Main function to copy the label, concentration and ignored flag entered for each
event onto the experiment, and to move ignored events out of the working event list.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
events : List[dict]
    Entered events: {datapoint, label, concentration_uM, ignored}.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Updates experiment["metadata"]["events"] in place and adds
experiment["metadata"]["ignored_events"] (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `experiment_data_processor`

```text
---- Summary ----
Main function to read (or take) one experiment and process its data: trim, decompose
into haems, scale by OD, convert to percentages, choose the plotted sources and
average around the events. It draws and saves nothing.

---- Inputs ----
info : dict
    Per-file information from everything_asker: path, name, trim and ignore times,
    OD values and events.
cfg : settings.Config
    Figure style and settings derived from the answers (config.py).
fit : Optional[dict]
    Fit dictionary from import_fit ({haem_list, data}), or None when the haems are
    not decomposed.
experiment : Optional[dict]
    An experiment already read from the file (the experiment browser keeps a copy
    so the file is not read again). It is processed in place. None reads the file.

---- Globals read ----
settings.TRANSMISSION_MODE, settings.DEGREE_OF_SCATTER, settings.HAEM_FACTOR,
settings.DELTA_ABS_WINDOW_SECONDS, settings.PERCENT_AVERAGE_WINDOW_SECONDS.

---- Outputs ----
dict
    {experiment, od_available, vo2_source, haem_source}. Prints progress and the
    reason when a step is skipped (side effect).

---- Globals mutated ----
None. Processes the experiment dictionary in place (side effect).

---- Equations ----
None.

---- Helpers ----
event_settings_merger
experiment_attenuation_adder
experiment_averages_calculator
experiment_decomposer
experiment_normaliser
experiment_paf_loader
experiment_trimmer
percent_converter
percent_need_checker
source_chooser
```

## `utils_shared/figure_layout.py`

Journal-aware figure sizing and automatic layout.

### FIGURE LAYOUT HELPERS

#### `_renderer_getter`

```text
---- Summary ----
Helper function to get the renderer of a figure canvas.

---- Inputs ----
fig : Figure
    Matplotlib figure.

---- Globals read ----
None.

---- Outputs ----
Any
    Matplotlib renderer.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `figure_canvas_fitter`

```text
---- Summary ----
Main function to set the figure margins so that everything drawn sits a fixed
padding inside the figure edge, whatever the figure size, font size or label
lengths.

---- Inputs ----
fig : Figure
    Matplotlib figure.
pad_pt : float
    Whitespace between the content and the figure edge in points.
suptitle : Optional[Any]
    Optional figure title (Text from fig.suptitle); it is placed pad_pt below the
    top edge.
suptitle_gap_pt : float
    Gap between the title and the content in points.
iterations : int
    Maximum number of fitting passes.
tolerance_pt : float
    Stop when no margin moves by more than this many points.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing; the figure margins are changed in place. Raises ValueError when the
    contents leave no room for the axes.

---- Globals mutated ----
None. Changes the subplot margins of ``fig`` and the layout flag and position of
``suptitle`` (side effect).

---- Equations ----
Each margin = (pad + width of the decoration outside the axes) / figure size,
repeated until the largest change is below tolerance_pt.

---- Helpers ----
_renderer_getter
```

#### `figure_finisher`

```text
---- Summary ----
Helper function to fit the margins to the drawn content, add the panel letters at
the top-left of each panel and fit again.

---- Inputs ----
fig : Figure
    Matplotlib figure.
config : dict
    Figure settings dictionary built in custom_config.py.
panels : list
    List of (letter, main axes, [axes of the panel]) tuples.
suptitle : Any
    Figure title text object, or None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Resizes the layout of ``fig`` and adds text to it (side effect).

---- Equations ----
None.

---- Helpers ----
figure_canvas_fitter
panel_letter_adder
```

#### `figure_size_calculator`

```text
---- Summary ----
Main function to calculate the (width, height) of a figure in inches from a journal
specification.

---- Inputs ----
spec : dict
    Journal specification (config.JOURNAL_SPECS entry).
columns : float
    Key of spec["widths_mm"]: 1, 1.5 or 2 columns wide.
height : float
    Fraction of the journal page height (spec["page_height_mm"]), above 0 and at
    most 1; 0.5 is half a page.

---- Globals read ----
MM_PER_INCH (module constant).

---- Outputs ----
Tuple[float, float]
    (width, height) in inches. Raises ValueError for an unknown column count or a
    height outside (0, 1].

---- Globals mutated ----
None.

---- Equations ----
width_in = widths_mm[columns] / 25.4; height_in = page_height_mm x height / 25.4.

---- Helpers ----
None.
```

#### `figure_style_builder`

```text
---- Summary ----
Main function to derive every font size, padding and line width of the figures from
the journal specification and three master settings.

---- Inputs ----
spec : dict
    Journal specification (config.JOURNAL_SPECS entry).
base_font_pt : float
    Axis-label size in points; tick labels are 1 pt smaller and titles 1 pt larger.
spacing : float
    Tightness of all paddings and gaps: 1.0 is the default, 1.2 is 20 % looser, 0.8
    is 20 % tighter.
line_width_pt : float
    Width of the data lines in points; axes, reference and event lines are scaled
    from it.

---- Globals read ----
None.

---- Outputs ----
dict
    Style dictionary with 'fonts' {tick, label, title, panel_letter} and the points
    values unit, tick_length, tick_pad, label_pad, title_pad, edge_pad, title_gap,
    event_label_offset, line_width, axes_line_width and thin_line_width.

---- Globals mutated ----
None.

---- Equations ----
unit = base_font_pt x spacing; every padding is a multiple of unit (for example
title_pad = 0.8 x unit); axes_line_width = 0.65 x line_width_pt; thin_line_width =
0.5 x line_width_pt.

---- Helpers ----
None.
```

#### `figure_style_checker`

```text
---- Summary ----
Main function to list warnings for fonts outside the journal range or a figure
taller than the journal allows.

---- Inputs ----
journal : str
    Journal name, used in the warning text.
spec : dict
    Journal specification (config.JOURNAL_SPECS entry).
fonts : dict
    Font sizes in points keyed by role, as in make_style()['fonts'].
size_inches : Tuple[float, float]
    (width, height) of the figure in inches.
label : str
    Text put in front of each warning.

---- Globals read ----
MM_PER_INCH (module constant).

---- Outputs ----
List[str]
    Warning messages; empty when the style fits the journal.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `gap_space_calculator`

```text
---- Summary ----
Main function to calculate the GridSpec wspace or hspace that leaves a given gap
between equal cells.

---- Inputs ----
gap_pt : float
    Wanted gap between neighbouring cells in points.
extent_pt : float
    Total width or height covered by the cells and gaps in points.
n : int
    Number of equal cells.

---- Globals read ----
None.

---- Outputs ----
float
    GridSpec spacing as a fraction of the average cell size; 0 for a single cell.
    Raises ValueError when the gaps do not fit in extent_pt.

---- Globals mutated ----
None.

---- Equations ----
room = extent_pt - gap_pt x (n - 1); space = gap_pt x n / room.

---- Helpers ----
None.
```

#### `panel_letter_adder`

```text
---- Summary ----
Main function to write each panel letter just above the top edge of its panel's
main axes, to the left of everything the panel draws on that side.

---- Inputs ----
fig : Figure
    Matplotlib figure.
panels : list
    [(letter, main axes, [axes of the panel]), ...]; a fourth item (text, text
    keyword arguments) adds a small note after the letter.
font_pt : float
    Letter size in points.
case : str
    'upper' or 'lower'.
weight : str
    Matplotlib font weight of the letters.
gap_pt : float
    Extra gap above the panel in points.

---- Globals read ----
None.

---- Outputs ----
list
    The annotation artists created. Raises ValueError for an unknown case.

---- Globals mutated ----
None. Adds annotations to the main axes of each panel (side effect); call
figure_canvas_fitter afterwards so the letters are inside the margins.

---- Equations ----
None.

---- Helpers ----
_renderer_getter
```

#### `stack_legend_drawer`

```text
---- Summary ----
Main function to draw one legend for a vertical stack of axes (an individual
experiment plot). By default it sits in the white space to the right of the stack,
centred on the height of the stack (or on the span down to ``bottom``); with
``below_pt`` it sits centred under the stack instead. It holds every labelled line
of the stack (set and measured O2, then each haem) except the OCR trace.

---- Inputs ----
axes : List[Axes]
    Axes of the stack, top first.
config : dict
    Settings; uses LEGEND_FONT_SIZE, LEGEND_FRAME, LEGEND_FRAME_LINE_WIDTH
    (optional) and VO2_LABEL (optional).
bottom : Optional[Axes]
    Lowest axes of the span to centre on (for example the bottom row of a grid of
    stacks), or None for the stack itself.
below_pt : Optional[float]
    When set, the legend hangs this many points below the stack's lowest axes
    instead of sitting at the right.
columns : int
    Number of legend columns.

---- Globals read ----
None.

---- Outputs ----
Optional[Any]
    The legend, or None when the stack has no labelled lines.

---- Globals mutated ----
None. Adds a legend to an axes of the stack (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `text_extent_calculator`

```text
---- Summary ----
Main function to calculate the width and height of the bounding box of a piece of
text after rotating it.

---- Inputs ----
text : str
    Plain text without mathtext.
size_pt : float
    Font size in points.
rotation_deg : float
    Rotation of the text in degrees.

---- Globals read ----
None.

---- Outputs ----
Tuple[float, float]
    (width, height) in points of the rotated bounding box; the unrotated height is
    at least 1.2 x size_pt.

---- Globals mutated ----
None.

---- Equations ----
w = |W cos(a)| + |H sin(a)|; h = |W sin(a)| + |H cos(a)|, where W and H are the
unrotated text width and height and a is the rotation angle.

---- Helpers ----
None.
```

## `utils_shared/helpers.py`

Small, generic utilities shared by several modules.

### MAIN FUNCTIONS

#### `concentration_formatter`

```text
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
```

#### `excel_sheet_namer`

```text
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
```

#### `figure_saver`

```text
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
```

#### `file_name_sanitiser`

```text
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
```

#### `name_simplifier`

```text
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
```

## `utils_shared/individual_experiment_exporter.py`

Export of one processed experiment to an Excel workbook.

### INDIVIDUAL EXPERIMENT EXPORTER HELPERS

#### `_frame_writer`

```text
---- Summary ----
Helper function to write a DataFrame as a formatted worksheet.

---- Inputs ----
sheets : tuple
    (open ExcelWriter, header format, set of sheet names already used).
frame : pd.DataFrame
    Data to write.
sheet_title : str
    Wanted sheet name; made unique and valid for Excel.
first_col_width : float
    Width of the first column.

---- Globals read ----
None.

---- Outputs ----
Any
    The xlsxwriter worksheet.

---- Globals mutated ----
None. Adds a sheet to the open workbook and records its name (side effect).

---- Equations ----
None.

---- Helpers ----
excel_sheet_namer
```

#### `_name_lister`

```text
---- Summary ----
Helper function to list the measurement names of one kind (vo2 or haem) over all
windows, in first-seen order.

---- Inputs ----
windows : dict
    Window name -> window record, each holding 'vo2' and 'haem' dicts.
kind : str
    'vo2' or 'haem'.

---- Globals read ----
None.

---- Outputs ----
List[str]
    Unique measurement names.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_spectral_csv_exporter`

```text
---- Summary ----
Helper function to write one CSV per spectral dataset and data type, with
wavelengths down and one column per spectrum.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
folder : Path
    Existing folder the CSV files are written to.

---- Globals read ----
SPECTRAL_CSV_TYPES (module constant).

---- Outputs ----
List[dict]
    One record per CSV file: Dataset, Data type, CSV file, Wavelengths, Timepoints.
    Raises ValueError when a spectrum length does not match the wavelengths.

---- Globals mutated ----
None. Writes CSV files into ``folder`` (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `averages_table_builder`

```text
---- Summary ----
Main function to build the Averages worksheet table: one row per window with the
mean, SD and change from baseline of VoO2 and of each haem.

---- Inputs ----
averages : dict
    Event-window averages, as added to the experiment by
    calculate_experiment_averages (DATA_FORMAT.md); uses averages['windows'].

---- Globals read ----
None.

---- Outputs ----
pd.DataFrame
    Columns Average, Start time (min), End time (min), then mean, SD and change from
    baseline (%) for VoO2 and each haem.

---- Globals mutated ----
None.

---- Equations ----
Change from baseline = window mean as a percentage of the average0 mean (calculated
in the averaging step).

---- Helpers ----
_name_lister
```

#### `experiment_workbook_exporter`

```text
---- Summary ----
Main function to export one experiment to <output_dir>/<name>/<name>.xlsx, with the
CcO2, CsO2 and VoO2 sheets, Averages, Events and Metadata, and optionally every
processed table and the spectral CSV files.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
output_dir : Path
    Results folder.
full : bool
    True adds every processed table in the order of DATA_SHEETS.
spectra : bool
    True also writes the spectral CSV files next to the workbook (large and slow)
    and an index sheet linking to them.

---- Globals read ----
BASIC_SHEETS, DATA_SHEETS and schema.DELTA_HAEM_SOURCES.

---- Outputs ----
Path
    Path of the workbook.

---- Globals mutated ----
None. Creates the folder, the workbook and optional CSV files (side effect).

---- Equations ----
None.

---- Helpers ----
_frame_writer
_spectral_csv_exporter
averages_table_builder
file_name_sanitiser
```

#### `saved_settings_reader`

```text
---- Summary ----
Main function to read the OD, volume, dilution factor and events saved in the
workbook of an earlier export.

---- Inputs ----
output_dir : Path
    Results folder.
experiment_name : str
    Experiment name (file name without the extension).

---- Globals read ----
SETTINGS_KEYS (module constant).

---- Outputs ----
Optional[dict]
    {'OD', 'volume', 'dilution_factor', 'events': [{'datapoint', 'label',
    'concentration_uM', 'ignored'}]}, or None when there is no readable workbook or
    nothing was saved.

---- Globals mutated ----
None. Reads the workbook from disk.

---- Equations ----
None.

---- Helpers ----
workbook_path_builder
```

#### `workbook_path_builder`

```text
---- Summary ----
Main function to build the path of the workbook of an experiment.

---- Inputs ----
output_dir : Path
    Results folder.
experiment_name : str
    Experiment name; made safe for file names.

---- Globals read ----
None.

---- Outputs ----
Path
    <output_dir>/<name>/<name>.xlsx.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
file_name_sanitiser
```

## `utils_shared/individual_experiment_plotter.py`

Plot of one experiment: oxygen, OCR and haem panels.

### CLASSES

#### `_HideTopTickLabels`

```text
---- Summary ----
A y-axis formatter that leaves out the tick label nearest the top edge when it would
run into the panel above. Stacked panels touch, so a label at the very top of one
panel overlaps the bottom label of the panel above it; a label is dropped if its
tick lies within 0.7 x ``font_pt`` points (the height of a digit) of the top of the
axis, whatever the panel's height.

---- Attributes ----
_font_pt : float
    Font size of the tick labels in points.

---- Globals read ----
None.

---- Methods ----
__init__
__call__
```

##### `__init__`

```text
---- Summary ----
Helper method to create the formatter.

---- Inputs ----
font_pt : float
    Font size of the tick labels in points.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

##### `__call__`

```text
---- Summary ----
Helper method to format one tick label, returning an empty string for the label
nearest the top edge when it would run into the panel above.

---- Inputs ----
x : float
    Tick value.
pos : Optional[int]
    Tick position, as passed by matplotlib.

---- Globals read ----
None.

---- Outputs ----
str
    Tick label text, or an empty string for a label within 0.7 x font_pt points
    of the top of the axis.

---- Globals mutated ----
None.

---- Equations ----
A label is dropped when x >= high - (high - low) x min(0.5, 0.7 x font_pt /
axes_height_pt), where low and high are the view limits.

---- Helpers ----
None.
```

### INDIVIDUAL EXPERIMENT PLOTTER HELPERS

#### `_axes_legend_drawer`

```text
---- Summary ----
Helper function to draw a legend with an optional thin box.

---- Inputs ----
ax : Axes
    Matplotlib axes.
config : dict
    Individual-experiment plot settings, as built by Config.plot_config in
    config.py.
text_only : bool
    True drops the coloured line beside each entry (used for haem panels, where the
    colour already identifies the trace).
location : Optional[str]
    Legend location; None uses config["LEGEND_LOCATION"].

---- Globals read ----
config keys LEGEND_LOCATION, LEGEND_COLUMNS, LEGEND_FRAME, LEGEND_FONT_SIZE,
LEGEND_FRAME_LINE_WIDTH and LEGENDS_OUTSIDE (legend in the white space right of
the axes).

---- Outputs ----
Legend
    The legend that was drawn.

---- Globals mutated ----
None. Adds a legend to ``ax`` (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_first_series_getter`

```text
---- Summary ----
Helper function to get the time and values of the first measurement column of a
DataFrame.

---- Inputs ----
df : pd.DataFrame
    Time-resolved data frame (DATA_FORMAT.md).

---- Globals read ----
None.

---- Outputs ----
Tuple[np.ndarray, np.ndarray]
    (times, values) of the first measurement column.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
measurement_column_finder
time_getter
value_getter
```

#### `_haem_data_selector`

```text
---- Summary ----
Helper function to pick the haem data frame the haem panels plot.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
config : dict
    Individual-experiment plot settings, as built by Config.plot_config in
    config.py.

---- Globals read ----
config keys HAEM_PANELS and HAEM_PLOT_VALUES; schema.HAEM_KEYS.

---- Outputs ----
Tuple[Optional[pd.DataFrame], Optional[str]]
    (haem data frame or None, source name). None when haem panels are off or the
    source is missing from the experiment (a warning is printed).

---- Globals mutated ----
None. Prints a warning when the source is missing (side effect).

---- Equations ----
None.

---- Helpers ----
source_resolver
```

#### `_height_ratio_calculator`

```text
---- Summary ----
Helper function to calculate the relative panel heights from PANEL_HEIGHT_RATIOS.

---- Inputs ----
panels : List[dict]
    Panel specifications; each has a "type" of oxygen, vo2 or haem.
config : dict
    Individual-experiment plot settings, as built by Config.plot_config in
    config.py.

---- Globals read ----
config keys PANEL_HEIGHT_RATIOS, EQUAL_PANEL_HEIGHTS and HAEM_PANEL_WEIGHT.

---- Outputs ----
List[float]
    Relative height of each panel. The haem weight is shared equally between the
    haem panels. Raises ValueError for a missing or non-positive weight.

---- Globals mutated ----
None.

---- Equations ----
ratio = weight for oxygen and vo2 panels; HAEM_PANEL_WEIGHT for each haem panel if
set, else weight / n_haem; 1 for every panel when EQUAL_PANEL_HEIGHTS is set.

---- Helpers ----
None.
```

#### `_min_ticks_setter`

```text
---- Summary ----
Helper function to make sure an axis has at least a given number of ticks, still at
round values.

---- Inputs ----
axis : Any
    Matplotlib axis object (ax.xaxis or ax.yaxis).
count : Optional[int]
    Minimum number of ticks; None leaves the ticks automatic.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing; the major locator of the axis is replaced.

---- Globals mutated ----
None. Sets the major locator of ``axis`` (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_panel_builder`

```text
---- Summary ----
Helper function to list the panels to draw: oxygen, VO2, then one for each
configured haem panel with matching data.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
config : dict
    Individual-experiment plot settings, as built by Config.plot_config in
    config.py.
haem_data : Optional[pd.DataFrame]
    Haem data frame, or None.

---- Globals read ----
config keys PLOT_SET_AND_MEASURED_O2, PLOT_VO2, O2_PANEL_TITLE, VO2_PANEL_TITLE and
HAEM_PANELS.

---- Outputs ----
List[dict]
    Panel specifications {type, title, haems}. Raises ValueError when no panel is
    selected.

---- Globals mutated ----
None. Prints a warning for haems missing from the data (side effect).

---- Equations ----
None.

---- Helpers ----
measurement_column_finder
name_simplifier
```

#### `_vo2_ymax_calculator`

```text
---- Summary ----
Helper function to choose the top of the OCR axis so that the whole run is shown
(including the start) while a narrow spike, such as the one when dithionite is
added, does not stretch the axis.

---- Inputs ----
y : np.ndarray
    OCR values of the whole run (NaN allowed).
window_fraction : float
    Width of the rolling median as a fraction of the number of points; spikes
    narrower than half of it are removed from the envelope.
headroom : float
    Fraction of the envelope height added above the highest smoothed value.

---- Globals read ----
None.

---- Outputs ----
float
    Top of the axis; NaN when there are no finite values.

---- Globals mutated ----
None.

---- Equations ----
smooth = rolling median of y (window = window_fraction x n points, at least 5);
noise = 95th percentile of |y - smooth|;
top = max(smooth) + noise + headroom x max(smooth).

---- Helpers ----
None.
```

#### `_window_drawer`

```text
---- Summary ----
Helper function to draw the averaging windows behind the data on every axis.

---- Inputs ----
axes : List[Axes]
    Axes of the experiment, top to bottom.
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
config : dict
    Individual-experiment plot settings, as built by Config.plot_config in
    config.py.

---- Globals read ----
config keys PLOT_AVERAGING_WINDOWS and the AVERAGING_WINDOW_* appearance settings.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Adds shaded spans and labels to the axes (side effect).

---- Equations ----
None.

---- Helpers ----
_window_label_builder
```

#### `_window_label_builder`

```text
---- Summary ----
Helper function to build the text of an averaging window from
AVERAGING_WINDOW_LABEL_FORMAT.

---- Inputs ----
window_name : str
    Window name, for example 'average3'.
config : dict
    Individual-experiment plot settings, as built by Config.plot_config in
    config.py.

---- Globals read ----
config key AVERAGING_WINDOW_LABEL_FORMAT ({n} is the number, {name} the window
name).

---- Outputs ----
str
    Label text; empty when the format is empty.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_ylim_calculator`

```text
---- Summary ----
Helper function to calculate y limits from the data after the ignored start and
before the ignored end, plus a margin.

---- Inputs ----
times : np.ndarray
    Times in minutes.
series : List[np.ndarray]
    Value arrays on the same time axis.
ignore_minutes : float
    Minutes at the start left out of the limits.
margin : float
    Fraction of the data range added on both sides.
ignore_last_minutes : float
    Minutes at the end left out of the limits.

---- Globals read ----
None.

---- Outputs ----
Optional[Tuple[float, float]]
    (low, high), or None when no finite data remain.

---- Globals mutated ----
None.

---- Equations ----
pad = (max - min) x margin (1 if the range is 0); limits = (min - pad, max + pad).

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `experiment_drawer`

```text
---- Summary ----
Main function to draw one experiment's stacked panels into a cell of an existing
figure. It adds no title, adjusts no margins and saves nothing; event labels hang
below the lowest axis, so room is needed underneath the cell.

---- Inputs ----
fig : Figure
    Matplotlib figure.
subplot_spec : SubplotSpec
    Grid cell the experiment is drawn in.
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
config : dict
    Individual-experiment plot settings, as built by Config.plot_config in
    config.py.

---- Globals read ----
Many config keys (panels, axes labels, colours, events, windows; see
Config.plot_config in config.py) and schema.VO2_KEYS.

---- Outputs ----
Tuple[List[Axes], List[dict]]
    (axes from top to bottom, panel specifications drawn).

---- Globals mutated ----
None. Adds axes and artists to ``fig`` (side effect).

---- Equations ----
None.

---- Helpers ----
_axes_legend_drawer
_first_series_getter
_haem_data_selector
_height_ratio_calculator
_min_ticks_setter
_panel_builder
_vo2_ymax_calculator
_window_drawer
_ylim_calculator
concentration_formatter
name_simplifier
source_resolver
time_getter
value_getter
```

#### `experiment_plotter`

```text
---- Summary ----
Main function to plot one experiment in its own figure, optionally save it as svg
and png, then show or close it.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
config : dict
    Individual-experiment plot settings, as built by Config.plot_config in
    config.py.
export_root : Path
    Results folder.
fig : Optional[Figure]
    An existing figure to clear and draw in (the experiment browser redraws one
    window). It is left open. None makes a new figure.

---- Globals read ----
config keys FIGURE_SIZE, FIGURE_DPI, TITLE_STYLE, LAYOUT_PAD_PT, FIT_MARGINS,
TITLE_GAP_PT, SAVE_FIGURES, TIGHT_BBOX, SHOW_INDIVIDUAL_FIGURES and the title
settings.

---- Outputs ----
Tuple[Figure, List[Axes]]
    The figure (already closed unless SHOW_INDIVIDUAL_FIGURES is set or a figure was
    given) and its axes.

---- Globals mutated ----
None. Writes <export_root>/<name>/<name>.svg and .png and prints a message (side
effect).

---- Equations ----
None.

---- Helpers ----
experiment_drawer
experiment_title_builder
figure_canvas_fitter
figure_saver
watermark_style_builder
```

#### `experiment_title_builder`

```text
---- Summary ----
Main function to build the title of an experiment from the FIGURE_TITLE format.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
config : dict
    Individual-experiment plot settings, as built by Config.plot_config in
    config.py.

---- Globals read ----
config key FIGURE_TITLE ({experiment_name} is replaced).

---- Outputs ----
str
    Title text.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `watermark_style_builder`

```text
---- Summary ----
Main function to build the text keyword arguments of the faint run-name watermark.

---- Inputs ----
config : dict
    Individual-experiment plot settings, as built by Config.plot_config in
    config.py.

---- Globals read ----
config keys WATERMARK_FONT_SIZE, TICK_FONT_SIZE, WATERMARK_COLOUR and
WATERMARK_ALPHA.

---- Outputs ----
dict
    Keyword arguments fontsize, color and alpha for matplotlib text.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

## `utils_shared/normalisation.py`

Normalisation of OCR and haem data by OD and to a relative scale.

### NORMALISATION HELPERS

#### `_frame_normaliser`

```text
---- Summary ----
Helper function to OD-normalise the measurement columns of a data frame, leaving the
time and index columns untouched.

---- Inputs ----
df : pd.DataFrame
    Data frame with a time column and measurement columns.
**kwargs : Any
    optical_density, volume and dilution_factor, passed to data_normaliser.

---- Globals read ----
None.

---- Outputs ----
pd.DataFrame
    Scaled copy of the data frame.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
data_normaliser
measurement_column_finder
```

### MAIN FUNCTIONS

#### `data_normaliser`

```text
---- Summary ----
Main function to divide numeric data by dilution factor x optical density x volume.

---- Inputs ----
data : Union[pd.DataFrame, pd.Series, np.ndarray]
    Numeric data to scale.
optical_density : float
    OD of the sample (> 0).
volume : float
    Volume of the sample (> 0).
dilution_factor : float
    Dilution factor (> 0).

---- Globals read ----
None.

---- Outputs ----
Union[pd.DataFrame, pd.Series, np.ndarray]
    Scaled data of the same kind as the input. Raises ValueError if the denominator
    is not positive and finite.

---- Globals mutated ----
None.

---- Equations ----
scaled = data / (dilution_factor x optical_density x volume).

---- Helpers ----
None.
```

#### `experiment_normaliser`

```text
---- Summary ----
Main function to OD-normalise VoO2 and, when present, the haem data of an
experiment.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.

---- Globals read ----
None. Calls schema.measurement_columns.

---- Outputs ----
dict
    The same experiment dictionary. Raises KeyError if dilution_factor, OD or volume
    is missing from the metadata, and ValueError if VoO2 has no measurement columns.

---- Globals mutated ----
experiment: adds VoO2_OD and, for each of haem_conc, haem_abs and haem_delta_abs
that exists, haem_OD, haem_abs_OD and haem_delta_abs_OD.

---- Equations ----
x_OD = x / (dilution_factor x OD x volume). Dividing by a constant commutes with the
shift behind delta abs, so haem_delta_abs_OD equals the shifted haem_abs_OD.

---- Helpers ----
_frame_normaliser
measurement_column_finder
```

#### `percent_converter`

```text
---- Summary ----
Main function to scale one table of an experiment to 0-100 % and store it under a
new key.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
source_key : str
    Key of the table to scale, e.g. 'haem_conc' or 'VoO2'.
target_key : str
    Key the scaled table is stored under, e.g. 'haem_percent'.
**scaling_kwargs : Any
    exclude_first_minutes, exclude_last_minutes and window_seconds, passed to
    percent_scaler.

---- Globals read ----
None.

---- Outputs ----
dict
    The same experiment dictionary. Raises ValueError if the source table is
    unavailable.

---- Globals mutated ----
experiment: adds experiment[target_key].

---- Equations ----
None.

---- Helpers ----
percent_scaler
```

#### `percent_scaler`

```text
---- Summary ----
Main function to scale each measurement column of a data frame to a relative 0-100 %
range.

---- Inputs ----
df : pd.DataFrame
    Data frame with a time column (minutes) and measurement columns.
label : str
    Name used in error messages.
exclude_first_minutes : float
    Windows must start at least this long after the first measurement.
exclude_last_minutes : float
    Windows must finish at least this long before the last measurement.
window_seconds : float
    Length of each averaging window, in seconds (> 0).

---- Globals read ----
schema.get_times, measurement_columns.

---- Outputs ----
pd.DataFrame
    Scaled copy; the windows used are stored in result.attrs["percent_scaling"]. A
    constant column becomes NaN. Raises ValueError for invalid settings or when no
    complete window remains.

---- Globals mutated ----
None.

---- Equations ----
percent = (value - low) / (high - low) x 100, where low and high are the lowest and
highest window means (windows must contain data spanning at least 80 % of their
length). Values outside the range are kept.

---- Helpers ----
measurement_column_finder
time_getter
```

## `utils_shared/output_capture.py`

Per-thread capture of printed output, so one thread can print without the text reaching

### MAIN FUNCTIONS

#### `captured_buffer_getter`

```text
---- Summary ----
Main function to give the buffer that the current thread's output is being captured
in, if any. Output streams that support the capture check this before they write.

---- Inputs ----
None.

---- Globals read ----
_local (module state).

---- Outputs ----
Optional[io.StringIO]
    The buffer of the current thread, or None when its output is not captured.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `output_capturer`

```text
---- Summary ----
Main function to capture everything the current thread prints, while other threads
keep printing normally. Only output streams that check captured_buffer_getter honour
it (the experiment browser window and the log copier do).

---- Inputs ----
None.

---- Globals read ----
_local (module state).

---- Outputs ----
Iterator[io.StringIO]
    The buffer the output is collected in; read it with getvalue().

---- Globals mutated ----
None. Sets and clears the capture of the current thread (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

## `utils_shared/paf_reader.py`

Direct reader of Espana Scientific Software .paf files.

### CLASSES

#### `PafError`

```text
---- Summary ----
Raised when the file is not a .paf, is truncated, or has a layout this reader does
not know.

---- Attributes ----
None.

---- Globals read ----
None.

---- Methods ----
None.
```

#### `Spectra`

```text
---- Summary ----
One parsed 'Spectra: CCD' record (one spectrometer) of a .paf file.
Detailed structure can be found in DATA_FORMAT.md.
```

#### `PafFile`

```text
---- Summary ----
An open .paf file (memory-mapped, so a 100 MB file is not read into RAM). Use ``with
PafFile(path) as paf:``. Everything handed out by the methods is a copy, so it stays
valid after the file is closed.

---- Attributes ----
path : Path
    Path to the .paf file.
records : List[dict]
    Record table from record_scanner (see DATA_FORMAT.md).
spectra : List[Spectra]
    Parsed spectrometer records.
time_s : np.ndarray
    Time of every frame in seconds, shape (n_frames,).

---- Globals read ----
None.

---- Methods ----
__init__
__enter__
__exit__
acquisition_reader
closer
dataset_name_lister
duration_finder
events_reader
frame_counter
notes_reader
spectra_dataset_reader
stream_name_lister
stream_reader
```

##### `__init__`

```text
---- Summary ----
Main method to open a .paf file, memory-map it, scan its records and find the
time base and the traces that cover it.

---- Inputs ----
path : Union[str, Path]
    Path to the .paf file.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing. Sets path, records, spectra, time_s (seconds) and the private
    stream tables. Raises PafError for a file that is too small, has no Time
    stream or cannot be read.

---- Globals mutated ----
None. Opens the file and the memory map (side effect); closes them again if
reading fails.

---- Equations ----
None.

---- Helpers ----
closer
record_scanner
stream_extractor
```

##### `__enter__`

```text
---- Summary ----
Main method to support `with PafFile(path) as paf:`.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
PafFile
    The open file itself.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

##### `__exit__`

```text
---- Summary ----
Main method to close the file when the `with` block ends.

---- Inputs ----
*exc : Any
    Exception information passed by Python (ignored).

---- Globals read ----
None.

---- Outputs ----
None
    Nothing. The exception, if any, is not suppressed.

---- Globals mutated ----
None. Closes the file (side effect).

---- Equations ----
None.

---- Helpers ----
closer
```

##### `acquisition_reader`

```text
---- Summary ----
Main method to summarise the acquisition settings of every spectrometer.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
List[dict]
    One dictionary per spectrometer: dataset, spectrometer, frames, wavelengths,
    wavelength_range_nm, the parameters read from the file, and other_fields.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
dataset_namer
```

##### `closer`

```text
---- Summary ----
Main method to release the memory map and the file handle and clear the parsed
tables.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing. Anything handed out earlier stays valid because it is a copy.

---- Globals mutated ----
None. Resets the records, spectra and stream tables of the instance and closes
the file (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `dataset_name_lister`

```text
---- Summary ----
Main method to list the spectral datasets in the file.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
List[str]
    Dataset names in file order.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
dataset_namer
```

##### `duration_finder`

```text
---- Summary ----
Main property to give the length of the recording in minutes.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
float
    Largest time value, in minutes.

---- Globals mutated ----
None.

---- Equations ----
duration (min) = max(time_s) / 60.

---- Helpers ----
None.
```

##### `events_reader`

```text
---- Summary ----
Main method to read the text events (additions) stored in the file.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
List[dict]
    [{'name', 'text', 'datapoint'}] sorted by datapoint; datapoint is the
    1-based spectrum number stored with the event. Events with no stored
    position are ignored with a warning.

---- Globals mutated ----
None. Prints warnings (side effect).

---- Equations ----
None.

---- Helpers ----
u32_reader
warning_printer
```

##### `frame_counter`

```text
---- Summary ----
Main property to give the number of time points (frames) in the recording.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
int
    Length of the time base.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

##### `notes_reader`

```text
---- Summary ----
Main method to read the experiment notes (PaneNote record) as plain text.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
str
    Notes text, or an empty string if there are none.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
rtf_converter
```

##### `spectra_dataset_reader`

```text
---- Summary ----
Main method to read one spectrometer as the dictionary used by the rest of the
program.

---- Inputs ----
name : str
    Dataset name from dataset_name_lister, e.g. 'Cyt'.
with_intensity : bool
    True to also return the integer counts.
chunk : int
    Number of spectra converted at a time (limits memory use).

---- Globals read ----
LN10 (module constant).

---- Outputs ----
dict
    {'wavelengths' (nm, n_wavelengths), 'spectrum_indices' (n_spectra), 'time'
    (min, n_spectra; NaN if the time count differs), 'transmission' (n_spectra x
    n_wavelengths)[, 'intensity']}; float64 copies. Raises PafError for an
    unknown dataset.

---- Globals mutated ----
None. Prints a warning if spectrum times are unavailable (side effect).

---- Equations ----
transmission = 10^(log - log_ref) = exp((log - log_ref) ln 10); intensity =
round(10^log). log is the stored log10 row and log_ref the stored reference row.

---- Helpers ----
dataset_name_lister
dataset_namer
warning_printer
```

##### `stream_name_lister`

```text
---- Summary ----
Main method to list the traces that cover the whole recording.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
List[str]
    Trace names, e.g. 'CsO2', 'CcO2', 'VoO2'.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

##### `stream_reader`

```text
---- Summary ----
Main method to read one trace on the common time base.

---- Inputs ----
name : str
    Trace name, e.g. 'VoO2'.

---- Globals read ----
None.

---- Outputs ----
Optional[np.ndarray]
    float64 array with one value per time point (NaN where the software has no
    value, e.g. the start of VoO2), or None if the trace does not exist.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `dataset_namer`

```text
---- Summary ----
Main function to turn a spectrometer name in the file into the dataset name used by
the rest of the program.

---- Inputs ----
spectra_name : str
    Spectrometer name as stored in the file, e.g. 'Cytochromes'.

---- Globals read ----
DATASET_ALIAS (module constant).

---- Outputs ----
str
    Alias from DATASET_ALIAS (e.g. 'Cyt'), otherwise the name with non-word
    characters replaced by underscores.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `experiment_end_trimmer`

```text
---- Summary ----
Main function to discard everything recorded after a given time.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
end_time : float
    Time in minutes after which data is removed.

---- Globals read ----
schema.TIME_COLUMN.

---- Outputs ----
dict
    The same experiment dictionary, with the traces and spectra shortened and
    metadata["trimmed_after_minutes"] set. The input is modified in place. Raises
    ValueError if an event occurs later, a trace is left empty or spectrum times are
    unavailable.

---- Globals mutated ----
experiment: replaces CcO2, CsO2 and VoO2 and shortens the fields of every
raw_spectra dataset; adds metadata["trimmed_after_minutes"].

---- Equations ----
None.

---- Helpers ----
None.
```

#### `experiment_paf_loader`

```text
---- Summary ----
Main function to build the experiment dictionary straight from a .paf file.

---- Inputs ----
path : Union[str, Path]
    Path to the .paf file.
spectral_datasets : Optional[Sequence[str]]
    Spectrometers to read (None = all, () = none). Spectra are the memory-heavy
    part, so read only what is needed.
with_intensity : bool
    True to also read the integer counts of each spectrum.

---- Globals read ----
TRACE_COLUMNS (module constant), schema.TIME_COLUMN.

---- Outputs ----
dict
    Experiment dictionary (DATA_FORMAT.md) with CsO2, CcO2 and VoO2 data frames,
    raw_spectra and metadata (paf_file, events, acquisition, notes). Raises PafError
    if the VoO2 trace is missing.

---- Globals mutated ----
None. Prints warnings for missing traces and events outside the recording (side
effect).

---- Equations ----
None.

---- Helpers ----
acquisition_reader
dataset_name_lister
events_reader
notes_reader
spectra_dataset_reader
stream_reader
warning_printer
```

#### `experiment_summary_reader`

```text
---- Summary ----
Main function to take a quick look at a .paf file without reading its spectra.

---- Inputs ----
path : Union[str, Path]
    Path to the .paf file.

---- Globals read ----
None.

---- Outputs ----
dict
    {'name' (file stem), 'duration_min', 'frames', 'datasets', 'events' (each with
    'time' in minutes), 'traces'}.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
dataset_name_lister
duration_finder
events_reader
frame_counter
stream_name_lister
```

#### `record_scanner`

```text
---- Summary ----
Main function to split the whole file into records and parse the spectra records.

---- Inputs ----
mm : mmap.mmap
    Read-only memory map of the .paf file.

---- Globals read ----
MARK (module constant).

---- Outputs ----
Tuple[List[dict], List[Spectra]]
    (records, spectra). Each record is {off, end, type, tokens}; spectra holds one
    parsed Spectra per spectrometer. Raises PafError if the file does not start with
    an Espana record.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
spectra_parser
token_reader
```

#### `rtf_converter`

```text
---- Summary ----
Main function to convert the rich text of a PaneNote record to plain text.

---- Inputs ----
rtf : bytes
    RTF bytes (cp1252).

---- Globals read ----
None.

---- Outputs ----
str
    Plain text with one line per paragraph, trailing spaces removed and a final
    newline.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `spectra_parser`

```text
---- Summary ----
Main function to parse one 'Spectra: CCD' record: frame count, wavelength axis,
log10 data block, acquisition parameters and trailer strings.

---- Inputs ----
mm : mmap.mmap
    Read-only memory map of the .paf file.
off : int
    Byte offset of the record marker.
markers : List[int]
    Byte offsets of every record marker in the file, ascending.

---- Globals read ----
None. Calls the Spectra class, token_reader, u32_reader and warning_printer.

---- Outputs ----
Spectra
    Object with offset, name, nframes, npix, wl_off, wavelengths, data_off,
    data_end, log (nrows x npix float32 view), rec_end, params, trailer, checks and
    ref attributes. Raises PafError if the layout is not recognised, implausible or
    truncated.

---- Globals mutated ----
None. Prints a warning for unexpected trailing bytes (side effect).

---- Equations ----
None.

---- Helpers ----
token_reader
u32_reader
warning_printer
```

#### `stream_extractor`

```text
---- Summary ----
Main function to extract every trace (DataItem followed by Measurement record) as a
float32 array.

---- Inputs ----
mm : mmap.mmap
    Read-only memory map of the .paf file.
recs : List[dict]
    Records from record_scanner, in file order.

---- Globals read ----
None.

---- Outputs ----
List[dict]
    One {name, n, offset, values, quantity, unit} dictionary per trace. Traces with
    disagreeing counts, no samples or a record that is too short are skipped with a
    warning.

---- Globals mutated ----
None. Prints warnings (side effect).

---- Equations ----
None.

---- Helpers ----
token_reader
u32_reader
warning_printer
```

#### `token_reader`

```text
---- Summary ----
Main function to find the length-prefixed UTF-16LE strings inside a byte range of
the file.

---- Inputs ----
buf : Union[bytes, mmap.mmap]
    Buffer to search.
start : int
    First byte offset of the range.
end : int
    Offset one past the last byte of the range.

---- Globals read ----
None.

---- Outputs ----
List[Tuple[str, int, int]]
    One (text, start offset, end offset) tuple per string found, in file order.
    Empty strings and strings with control characters are skipped.

---- Globals mutated ----
None.

---- Equations ----
A string is stored as 02 00 00 00, n (uint32), then n UTF-16LE characters (2n
bytes).

---- Helpers ----
u32_reader
```

#### `u32_reader`

```text
---- Summary ----
Main function to read one little-endian unsigned 32-bit integer from a buffer.

---- Inputs ----
buf : Union[bytes, mmap.mmap]
    Buffer to read from.
off : int
    Byte offset of the integer.

---- Globals read ----
None.

---- Outputs ----
int
    The integer value.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `warning_printer`

```text
---- Summary ----
Main function to print a reader warning, unless it is one of the harmless messages
in QUIET_WARNINGS.

---- Inputs ----
msg : str
    Warning text, without the "WARNING" prefix.

---- Globals read ----
QUIET_WARNINGS (module constant).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Prints to the terminal (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

## `utils_shared/questions.py`

Helpers for asking numbered questions in the terminal.

### CLASSES

#### `UserQuit`

```text
---- Summary ----
Raised when the input ends (window closed, Ctrl+Z / Ctrl+D) so the program can stop
cleanly.

---- Attributes ----
None.

---- Globals read ----
None.

---- Methods ----
None.
```

### QUESTIONS HELPERS

#### `_input_reader`

```text
---- Summary ----
Helper function to show the answer prompt and read what the user types.

---- Inputs ----
text : str
    The question text (not printed; kept so tests can replace this function and
    match on it).
indent : str
    Indent placed before the "> " prompt.

---- Globals read ----
input_flusher.

---- Outputs ----
str
    The typed answer with surrounding spaces removed.

---- Globals mutated ----
None. Reads from the terminal; raises UserQuit when the input ends (side effect).

---- Equations ----
None.

---- Helpers ----
input_flusher
```

#### `_number_builder`

```text
---- Summary ----
Helper function to advance the counters and build the next question number.

---- Inputs ----
depth : int
    Numbering depth (1 = 3.1, 2 = 3.1.1, ...).

---- Globals read ----
MAX_DEPTH (module constant).

---- Outputs ----
str
    Question number such as "3.1.2".

---- Globals mutated ----
None. Increments the module counters _counters at the depth and resets deeper levels
(side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_question_printer`

```text
---- Summary ----
Helper function to print the numbered, coloured question line.

---- Inputs ----
question : str
    Question text, without its number.
depth : int
    Numbering depth of the question (1 = 3.1, 2 = 3.1.1, ...).
hint : str
    Text after the question, such as "[default]:" or "(y/N):"; may be empty.

---- Globals read ----
INDENT (module constant); _tight_next (module state); text_colourer.

---- Outputs ----
str
    Indent to use for the answer prompt and the option lines.

---- Globals mutated ----
None. Prints to the terminal and clears the module flag _tight_next (side effects).

---- Equations ----
None.

---- Helpers ----
_number_builder
text_colourer
```

### MAIN FUNCTIONS

#### `choice_asker`

```text
---- Summary ----
Main function to ask a question answered by choosing one numbered option.

---- Inputs ----
question : str
    Question text, without its number.
options : Sequence[Tuple[str, str]]
    Choices as (key, label) pairs, shown as 1), 2), ...
default : Optional[str]
    Key chosen when only Enter is pressed.
depth : int
    Numbering depth of the question (1 = 3.1, 2 = 3.1.1, ...).

---- Globals read ----
None.

---- Outputs ----
str
    Key of the chosen option.

---- Globals mutated ----
None. Reads from and prints to the terminal (side effect); advances the question
numbering counters.

---- Equations ----
None.

---- Helpers ----
_input_reader
_question_printer
```

#### `colour_checker`

```text
---- Summary ----
Main function to say whether the terminal can show colour; it also switches on
colour codes in the Windows console the first time.

---- Inputs ----
None.

---- Globals read ----
os.environ, sys.stdout; _colour_ready (module state).

---- Outputs ----
bool
    True when colour can be used (a terminal, and NO_COLOR is not set).

---- Globals mutated ----
Sets the module state _colour_ready; may run an empty os.system call on Windows.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `heading_printer`

```text
---- Summary ----
Main function to print a plain heading, for example the summary.

---- Inputs ----
text : str
    Heading text.

---- Globals read ----
COLOUR_SECTION (module constant); text_colourer.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Prints to the terminal (side effect).

---- Equations ----
None.

---- Helpers ----
text_colourer
```

#### `info_printer`

```text
---- Summary ----
Main function to print an information line (not a question), indented to sit under
the question above.

---- Inputs ----
text : str
    Text to print or process.
depth : int
    Numbering depth of the question (1 = 3.1, 2 = 3.1.1, ...).
tight : bool
    True to make the next question follow this line without a blank line.

---- Globals read ----
INDENT (module constant).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Prints to the terminal and sets the module flag _tight_next (side effects).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `input_flusher`

```text
---- Summary ----
Main function to throw away keys pressed while the program was busy, so a stray
Enter cannot answer a question.

---- Inputs ----
None.

---- Globals read ----
os.name, sys.stdin.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Empties the keyboard input buffer; does nothing when the input is not a
terminal (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `multi_asker`

```text
---- Summary ----
Main function to ask a question answered by choosing several numbered options.

---- Inputs ----
question : str
    Question text, without its number.
options : Sequence[str]
    Option names, shown as 1), 2), ...
default_all : bool
    True to choose all options when only Enter is pressed and nothing is remembered.
keep_order : bool
    True to return the options in the order typed instead of list order.
depth : int
    Numbering depth of the question (1 = 3.1, 2 = 3.1.1, ...).
default_values : Optional[Sequence[str]]
    Choice from last time, used for Enter when given.
label_formatter : Optional[Callable[[str], str]]
    Function that changes how an option is shown, not what is returned.

---- Globals read ----
None.

---- Outputs ----
List[str]
    The chosen options.

---- Globals mutated ----
None. Reads from and prints to the terminal (side effect); advances the question
numbering counters.

---- Equations ----
None.

---- Helpers ----
_input_reader
_question_printer
```

#### `number_asker`

```text
---- Summary ----
Main function to ask a question answered with a number, asking again until the value
is valid.

---- Inputs ----
question : str
    Question text, without its number.
default : Optional[float]
    Answer used when only Enter is pressed.
minimum : Optional[float]
    Smallest accepted value.
maximum : Optional[float]
    Largest accepted value.
exclusive_minimum : bool
    True when the minimum itself is not accepted.
allow_blank : bool
    True to accept an empty answer as None when there is no default.
depth : int
    Numbering depth of the question (1 = 3.1, 2 = 3.1.1, ...).
blank_label : str
    Word shown in [brackets] for an empty answer.

---- Globals read ----
None.

---- Outputs ----
Optional[float]
    The number, the default, or None for an accepted empty answer.

---- Globals mutated ----
None. Reads from and prints to the terminal (side effect); advances the question
numbering counters.

---- Equations ----
None.

---- Helpers ----
_input_reader
_question_printer
```

#### `numbering_getter`

```text
---- Summary ----
Main function to read the current number at a depth, so it can be restored with
numbering_setter after questions are asked again.

---- Inputs ----
depth : int
    Numbering depth to read (0 = the section number).

---- Globals read ----
_counters (module state).

---- Outputs ----
int
    Current number at that depth.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `numbering_restarter`

```text
---- Summary ----
Main function to make the next question at a depth (and deeper) start again from 1.

---- Inputs ----
depth : int
    Numbering depth to restart; deeper levels restart too.

---- Globals read ----
MAX_DEPTH (module constant).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Resets entries of the module counters _counters (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `numbering_setter`

```text
---- Summary ----
Main function to set the current number at a depth, for example so the next
sub-questions are numbered 3.4.3.1.

---- Inputs ----
depth : int
    Numbering depth to set.
value : int
    Number to make current at that depth.

---- Globals read ----
MAX_DEPTH (module constant).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Sets and resets entries of the module counters _counters (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `numbers_asker`

```text
---- Summary ----
Main function to ask a question answered by numbers from 1 to a count, separated by
commas.

---- Inputs ----
question : str
    Question text, without its number.
count : int
    Largest number accepted.
depth : int
    Numbering depth of the question (1 = 3.1, 2 = 3.1.1, ...).

---- Globals read ----
None.

---- Outputs ----
List[int]
    The chosen numbers in ascending order; an empty list for Enter (none).

---- Globals mutated ----
None. Reads from and prints to the terminal (side effect); advances the question
numbering counters.

---- Equations ----
None.

---- Helpers ----
_input_reader
_question_printer
```

#### `path_cleaner`

```text
---- Summary ----
Main function to clean a path typed or dragged into the window by removing
surrounding quotes and spaces.

---- Inputs ----
text : str
    Text as received from the terminal.

---- Globals read ----
None.

---- Outputs ----
str
    Path text without surrounding quotes or spaces.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `progress_clearer`

```text
---- Summary ----
Main function to remove the progress line from the terminal.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Prints to the terminal (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `progress_printer`

```text
---- Summary ----
Main function to show a one-line progress message that the next message overwrites.

---- Inputs ----
text : str
    Message to show.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Prints to the terminal without a new line (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `section_starter`

```text
---- Summary ----
Main function to start the next numbered section and print its heading.

---- Inputs ----
title : str
    Section title, without its number.

---- Globals read ----
COLOUR_SECTION, MAX_DEPTH (module constants).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Advances the module numbering counters _counters and prints the heading (side
effects).

---- Equations ----
None.

---- Helpers ----
text_colourer
```

#### `text_asker`

```text
---- Summary ----
Main function to ask a question answered with a line of text.

---- Inputs ----
question : str
    Question text, without its number.
default : Optional[str]
    Answer used when only Enter is pressed; shown as [default]:.
depth : int
    Numbering depth of the question (1 = 3.1, 2 = 3.1.1, ...).

---- Globals read ----
None.

---- Outputs ----
Optional[str]
    The typed text, or the default when Enter is pressed.

---- Globals mutated ----
None. Reads from and prints to the terminal (side effect); advances the question
numbering counters.

---- Equations ----
None.

---- Helpers ----
_input_reader
_question_printer
```

#### `text_colourer`

```text
---- Summary ----
Main function to wrap text in a colour code when colour is available.

---- Inputs ----
text : str
    Text to colour.
code : str
    ANSI colour code (COLOUR_QUESTION by default).

---- Globals read ----
COLOUR_QUESTION, RESET (module constants); colour_checker.

---- Outputs ----
str
    The coloured text, or the text unchanged without colour.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
colour_checker
```

#### `text_italiser`

```text
---- Summary ----
Main function to write text in italics when the terminal supports it.

---- Inputs ----
text : str
    Text to put in italics.

---- Globals read ----
ITALIC, RESET (module constants); colour_checker.

---- Outputs ----
str
    The italic text, or the text unchanged without colour support.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
colour_checker
```

#### `yes_no_asker`

```text
---- Summary ----
Main function to ask a yes/no question.

---- Inputs ----
question : str
    Question text, without its number.
default : bool
    Answer used when only Enter is pressed (the capital letter in the hint).
depth : int
    Numbering depth of the question (1 = 3.1, 2 = 3.1.1, ...).

---- Globals read ----
None.

---- Outputs ----
bool
    True for y or yes, False for n or no, the default for Enter.

---- Globals mutated ----
None. Reads from and prints to the terminal (side effect); advances the question
numbering counters.

---- Equations ----
None.

---- Helpers ----
_input_reader
_question_printer
```

## `utils_shared/run_logging.py`

Mirror console output to a timestamped log file for the duration of a run.

### CLASSES

#### `_Tee`

```text
---- Summary ----
File-like object that writes everything to several streams at once.

---- Attributes ----
streams : Tuple[Any, ...]
    File-like objects every write is copied to.

---- Globals read ----
None.

---- Methods ----
__init__
__getattr__
flush
isatty
write
```

##### `__init__`

```text
---- Summary ----
Method to store the streams that every write is copied to.

---- Inputs ----
*streams : Any
    File-like objects (for example the console and the log file).

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Sets the streams attribute on the instance.

---- Equations ----
None.

---- Helpers ----
None.
```

##### `__getattr__`

```text
---- Summary ----
Method to pass any other attribute lookup (such as encoding) to the first
stream.

---- Inputs ----
name : str
    Attribute name that was not found on the instance.

---- Globals read ----
None.

---- Outputs ----
Any
    The attribute of the first stream.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

##### `flush`

```text
---- Summary ----
Method to flush every stream. The name is fixed by the file-like protocol.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Flushes every stream (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `isatty`

```text
---- Summary ----
Method to say whether the first stream is a terminal. The name is fixed by the
file-like protocol.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
bool
    True when the first stream is an interactive terminal.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

##### `write`

```text
---- Summary ----
Method to write text to every stream and flush it, unless the current thread is
capturing its output (see output_capture), in which case it is kept by the
capture. The name is fixed by the file-like protocol.

---- Inputs ----
text : str
    Text to write.

---- Globals read ----
None.

---- Outputs ----
int
    Number of characters written.

---- Globals mutated ----
None. Writes to and flushes every stream (side effect).

---- Equations ----
None.

---- Helpers ----
captured_buffer_getter
```

### MAIN FUNCTIONS

#### `logging_starter`

```text
---- Summary ----
Main function to start copying everything printed to a timestamped log file.

---- Inputs ----
export_root : Path
    Results folder; the log goes to <export_root>/logs/YYYY_MM_DD-HH_MM_SS.log.
version : str
    Project version (as in the VERSION file), written on the first line of the log.
settings : dict
    Terminal answers of the run, written at the top of the log.

---- Globals read ----
None.

---- Outputs ----
dict
    Session dictionary {log_path, log_file, original_stdout, original_stderr,
    tee_stdout, tee_stderr, closed}, to be passed to logging_stopper.

---- Globals mutated ----
None. Creates the log folder and file, writes the version, seed and settings to
its first lines, replaces sys.stdout and sys.stderr with copying streams and
prints the log location (side effects).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `logging_stopper`

```text
---- Summary ----
Main function to restore the console streams and close the log file.

---- Inputs ----
session : Optional[dict]
    Session dictionary from logging_starter, or None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Restores sys.stdout and sys.stderr, closes the log file and marks the session
closed (side effects).

---- Equations ----
None.

---- Helpers ----
None.
```

## `utils_shared/schema.py`

Names and conventions of the experiment data model.

### MAIN FUNCTIONS

#### `finite_float_converter`

```text
---- Summary ----
Main function to convert a value to a finite float, or NaN when that is not
possible.

---- Inputs ----
value : Any
    Value to convert.

---- Globals read ----
None.

---- Outputs ----
float
    The value as a float, or NaN when it is not a number or not finite.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `measurement_column_finder`

```text
---- Summary ----
Main function to list the measurement columns of an experiment DataFrame.

---- Inputs ----
df : pd.DataFrame
    Time-resolved DataFrame with TIME_COLUMN.

---- Globals read ----
TIME_COLUMN, SPECTRUM_INDEX_COLUMN (module constants).

---- Outputs ----
List[str]
    Every column except TIME_COLUMN and SPECTRUM_INDEX_COLUMN.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `source_resolver`

```text
---- Summary ----
Main function to look up a dataset of an experiment by its source name from the
settings.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
source : str
    Source name, one of the keys of ``keys`` (for example "raw", "od", "percent").
keys : Dict[str, str]
    VO2_KEYS or HAEM_KEYS: {source name: experiment dictionary key}.
what : str
    Label used in error messages, for example "VO2" or "haem".

---- Globals read ----
None.

---- Outputs ----
Tuple[str, pd.DataFrame]
    (experiment dictionary key, the DataFrame). Raises ValueError when the source
    name is invalid or the dataset has not been calculated.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `time_getter`

```text
---- Summary ----
Main function to read the time column of an experiment DataFrame.

---- Inputs ----
df : pd.DataFrame
    Time-resolved DataFrame; must hold TIME_COLUMN.

---- Globals read ----
TIME_COLUMN (module constant).

---- Outputs ----
np.ndarray
    Times in minutes as a float array, shape (n_points,); unreadable values are NaN.
    Raises KeyError when the column is missing.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `value_getter`

```text
---- Summary ----
Main function to read one measurement column as a float array.

---- Inputs ----
df : pd.DataFrame
    Time-resolved DataFrame.
column : str
    Name of the measurement column.

---- Globals read ----
None.

---- Outputs ----
np.ndarray
    Values as a float array, shape (n_points,); unreadable values are NaN.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

## `utils_shared/spectral_decomposer.py`

Spectral fit loading and haem decomposition routines.

### SPECTRAL DECOMPOSER HELPERS

#### `_wavelength_masker`

```text
---- Summary ----
Helper function to select the wavelengths inside the range shared by all fits.

---- Inputs ----
wavelengths : np.ndarray
    Wavelengths of the spectrum (nm).
fit_data : pd.DataFrame
    Fit table from fit_importer.

---- Globals read ----
None.

---- Outputs ----
np.ndarray
    Boolean mask, True inside the shared range.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `data_filterer`

```text
---- Summary ----
Main function to restrict experimental data to the wavelength range shared by all
fits.

---- Inputs ----
experimental_data : np.ndarray
    Array of (wavelength, value) rows, shape (n_wavelengths, 2).
fit_data : pd.DataFrame
    Fit table from fit_importer.

---- Globals read ----
None. Calls _wavelength_masker.

---- Outputs ----
np.ndarray
    The rows inside the shared range.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_wavelength_masker
```

#### `delta_abs_calculator`

```text
---- Summary ----
Main function to shift each haem absorbance so that its reference level is 0, giving
a change in absorbance (mOD).

---- Inputs ----
haem_abs : pd.DataFrame
    Haem absorbance table in mOD (time, spectrum index and one column per haem).
exclude_first_minutes : float
    Start of the reference window, in minutes after the first measurement.
window_seconds : float
    Length of the reference window, in seconds (> 0).
label : str
    Name used in error messages.

---- Globals read ----
schema.get_times, get_values, measurement_columns.

---- Outputs ----
pd.DataFrame
    Shifted copy; the reference window and the means are stored in
    result.attrs["delta_abs_baseline"]. Raises ValueError for invalid settings or
    when no spectra fall in the window.

---- Globals mutated ----
None.

---- Equations ----
delta_abs = abs - mean(abs inside the reference window), per haem. Only a constant
is subtracted, so differences between points are unchanged.

---- Helpers ----
measurement_column_finder
time_getter
value_getter
```

#### `experiment_decomposer`

```text
---- Summary ----
Main function to decompose every spectrum of one dataset into haem concentrations
and absorbances.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
fit : dict
    Fit dictionary from fit_importer.
dataset_name : str
    Spectral dataset to decompose.
spectrum_type : str
    Field of the dataset to decompose, e.g. 'attenuation'.
degree_of_scatter : int
    Number of scatter terms.
haemfactor : float
    Scale factor applied to the haem basis spectra.
delta_exclude_first_minutes : float
    Start of the delta absorbance reference window, in minutes after the first
    spectrum.
delta_window_seconds : float
    Length of the delta absorbance reference window, in seconds.

---- Globals read ----
schema.TIME_COLUMN, SPECTRUM_INDEX_COLUMN.

---- Outputs ----
dict
    The same experiment dictionary. Raises ValueError for an invalid fit or dataset
    or inconsistent array shapes.

---- Globals mutated ----
experiment: adds haem_conc (time, spectrum index, one column per haem), haem_abs
(mOD, same layout; attrs["peak_amplitude_OD"]) and haem_delta_abs
(delta_abs_calculator).

---- Equations ----
c = (S^T S)^-1 S^T a for every spectrum (projector built once); haem_abs = c x peak
amplitude of the haem basis spectrum x 1000 (OD to mOD); haem_delta_abs = haem_abs -
mean over the reference window.

---- Helpers ----
_wavelength_masker
delta_abs_calculator
s_array_generator
```

#### `fit_importer`

```text
---- Summary ----
Main function to import a haem spectral fit CSV.

---- Inputs ----
filename : Path
    CSV with (wavelength, response) column pairs, one pair per haem; the header of
    each wavelength column names the haem.

---- Globals read ----
None.

---- Outputs ----
Dict[str, Any]
    {"haem_list": haem names in file order, "data": the table as a data frame}.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `s_array_generator`

```text
---- Summary ----
Main function to generate the haem and scatter basis components for one spectrum.

---- Inputs ----
experimental_data : np.ndarray
    Array of (wavelength, value) rows.
fit_data : pd.DataFrame
    Fit table from fit_importer.
degree_of_scatter : int
    Number of 1/wavelength^k scatter terms.
haemfactor : float
    Scale factor applied to the haem basis spectra.

---- Globals read ----
None.

---- Outputs ----
np.ndarray
    Basis matrix, shape (n_filtered_wavelengths, n_haems + degree_of_scatter + 1):
    negated haem fits (interpolated, times haemfactor), a constant column, then the
    normalised scatter terms.

---- Globals mutated ----
None.

---- Equations ----
haem column = -interp(fit) x haemfactor; scatter term k = (1/wl^k - min) / (max -
min) of 1/wl^k.

---- Helpers ----
data_filterer
```

#### `spectrum_decomposer`

```text
---- Summary ----
Main function to decompose one experimental spectrum into haem contributions and
scatter.

---- Inputs ----
experimental_data : np.ndarray
    Array of (wavelength, value) rows.
fit_data : pd.DataFrame
    Fit table from fit_importer.
degree_of_scatter : int
    Number of scatter terms.
haemfactor : float
    Scale factor applied to the haem basis spectra.

---- Globals read ----
None.

---- Outputs ----
Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray,
List[np.ndarray], np.ndarray]
    (c_array, filtered_data, scatter, background_subtracted, haems, haem_individual,
    residual); the spectra are (wavelength, value) columns. Useful for inspecting
    one fit; experiment_decomposer uses an equivalent, faster route.

---- Globals mutated ----
None.

---- Equations ----
c = (S^T S)^-1 S^T a, where S is the basis matrix and a the spectrum; residual = a -
(haems + scatter).

---- Helpers ----
data_filterer
s_array_generator
```

## `utils_shared/survey.py`

Numbered terminal questions of the main program (sections 1 to 5).

### SURVEY HELPERS

#### `_file_focuser`

```text
---- Summary ----
Helper function to tell the experiment browser which file the next question is
about, so its window shows that file. Does nothing without the browser.

---- Inputs ----
name : str
    File name.

---- Globals read ----
_file_focus_hook (module state).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Calls the hook (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_columns_text_builder`

```text
---- Summary ----
Helper function to write a figure width in columns, e.g. '1 column' or
'1.5 columns'.

---- Inputs ----
columns : float
    Number of journal columns.

---- Globals read ----
None.

---- Outputs ----
str
    Text such as '2 columns'.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_event_line_builder`

```text
---- Summary ----
Helper function to write one event as 'label, time' for the event listings.

---- Inputs ----
event : dict
    Event from the file summary (time in minutes).
entry : dict
    Current label, concentration_uM and ignored flag of that event.

---- Globals read ----
None.

---- Outputs ----
str
    For example '  15.01 min: nd-011992' or with the concentration and
    '[IGNORED]' when they apply.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_first_event_finder`

```text
---- Summary ----
Helper function to find the time of the first event of an experiment.

---- Inputs ----
summary : dict
    Experiment summary with events and duration_min.

---- Globals read ----
None.

---- Outputs ----
float
    First event time in minutes; the duration when there are no events.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_last_event_finder`

```text
---- Summary ----
Helper function to find the time of the last event of an experiment.

---- Inputs ----
summary : dict
    Experiment summary with events.

---- Globals read ----
None.

---- Outputs ----
float
    Last event time in minutes; 0 when there are no events.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_limits_asker`

```text
---- Summary ----
Helper function to ask one yes/no question and then one number per file (trim or
ignore, start or end), offering the values remembered from the last run.

---- Inputs ----
summaries : List[dict]
    File summaries (DATA_FORMAT.md).
remembered : dict
    {file name: {key: value}} from the last run.
key : str
    Name of the limit, for example 'trim_start'.
question : str
    The yes/no question.
per_file : str
    Question for each file; {name} is replaced by the file name.
fallback : Optional[float]
    Default for a file with no remembered value; None means 'none' and one
    value is asked per file. A number means one value is asked for all files,
    then optionally one per file.
all_text : str
    The question for the value that applies to all files (ignore only).
bounds_builder : Callable[[dict, dict], dict]
    Function (summary, limits collected so far for that file) giving the
    minimum and maximum accepted for the file.
note_builder : Callable[[dict], str]
    Function (summary) giving the information line shown before the question.
collected : dict
    {file name: {key: value}} of the limits asked so far.

---- Globals read ----
None.

---- Outputs ----
Dict[str, Optional[float]]
    {file name: minutes or None}.

---- Globals mutated ----
None. Reads from and prints to the terminal (side effect).

---- Equations ----
None.

---- Helpers ----
_file_focuser
info_printer
number_asker
yes_no_asker
```

#### `_maths_converter`

```text
    ---- Summary ----
    Helper function to convert the contents of one $...$ maths span to plain text
    with Unicode subscripts and italic letters.

    ---- Inputs ----
    match : re.Match
        Match whose group 1 is the text between the dollar signs.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        The converted text.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    _subscript_stripper
text_italiser
    
```

#### `_natural_sorter`

```text
---- Summary ----
Helper function to build a sort key that puts numbers in numerical order, so
'control_7hours' comes before 'control_24hours'.

---- Inputs ----
name : str
    File or experiment name.

---- Globals read ----
None.

---- Outputs ----
list
    Key of alternating lower-case text and integer parts (text first).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_subscript_stripper`

```text
---- Summary ----
Helper function to turn a matched subscript (_x or _{xy}) into plain text, since
Unicode subscripts are hard to read in a terminal.

---- Inputs ----
match : re.Match
    Match whose group 1 or 2 holds the subscript text.

---- Globals read ----
None.

---- Outputs ----
str
    The subscript text without the underscore.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `analysis_asker`

```text
---- Summary ----
Main function to ask section 3: haem decomposition, OD scaling, event averaging
and the event labels.

---- Inputs ----
summaries : List[dict]
    File summaries (DATA_FORMAT.md).
answers : dict
    Answers dictionary the values are stored in.
defaults : dict
    Default answers.
fits_folder : Path
    Folder holding the fit .csv files.
export_root : Path
    Results folder, where the saved OD and event values are looked for.

---- Globals read ----
None.

---- Outputs ----
tuple
    (fit, details). details is {file name: {'OD', 'volume', 'dilution_factor',
    'events'}}; the OD entries are only present when scaling by OD.

---- Globals mutated ----
None. Stores the answers in ``answers`` (side effect).

---- Equations ----
None.

---- Helpers ----
averaging_asker
decomposition_asker
event_asker
od_scaling_asker
saved_values_reader
```

#### `averaging_asker`

```text
---- Summary ----
Main function to ask whether to average around the events, and the window
settings.

---- Inputs ----
answers : dict
    Answers dictionary the values are stored in.
defaults : dict
    Default answers (averaging, window_minutes, gap_minutes).
forced : bool
    True to skip the yes/no question and only ask the window settings (a figure
    that needs the averages was chosen). The averaging answer is not changed.
depth : int
    Numbering depth of the first question.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Stores window_minutes and gap_minutes (and averaging) in ``answers``.

---- Equations ----
None.

---- Helpers ----
number_asker
yes_no_asker
```

#### `decomposition_asker`

```text
---- Summary ----
Main function to ask whether to decompose the spectra into haems and which fit to
use.

---- Inputs ----
summaries : List[dict]
    File summaries (DATA_FORMAT.md); the spectrometers in common are used.
defaults : dict
    Default answers (decompose, fit_file, decomposition_dataset).
fits_folder : Path
    Folder holding the fit .csv files.
forced : bool
    True to skip the yes/no question (a figure that needs the haems was chosen).
depth : int
    Numbering depth of the questions (1 = 3.1, 2 = 3.1.1).

---- Globals read ----
None.

---- Outputs ----
tuple
    (decompose, fit_file, fit, dataset). fit is the dictionary from import_fit,
    or None when no decomposition will be done.

---- Globals mutated ----
None. Reads from and prints to the terminal (side effect).

---- Equations ----
None.

---- Helpers ----
choice_asker
fit_importer
info_printer
yes_no_asker
```

#### `event_asker`

```text
---- Summary ----
Main function to ask whether to change the event labels, concentrations and which
events to ignore, file by file.

---- Inputs ----
summaries : List[dict]
    File summaries (DATA_FORMAT.md).
saved : dict
    {file name: values read from its workbook} (read_saved_settings).

---- Globals read ----
None.

---- Outputs ----
Dict[str, List[dict]]
    {file name: [{'datapoint', 'label', 'concentration_uM', 'ignored'}, ...]}.
    A label of 'ignore' marks an event that was not an addition.

---- Globals mutated ----
None. Reads from and prints to the terminal (side effect).

---- Equations ----
None.

---- Helpers ----
_event_line_builder
_file_focuser
info_printer
number_asker
numbering_setter
numbers_asker
text_asker
yes_no_asker
```

#### `file_focus_setter`

```text
---- Summary ----
Main function to set (or clear, with None) the function that is told which file a
question is about.

---- Inputs ----
hook : Optional[Callable[[str], None]]
    Function taking the file name, or None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
Sets _file_focus_hook (module state).

---- Equations ----
None.

---- Helpers ----
None.
```

#### `files_asker`

```text
---- Summary ----
Main function to ask for the folder of .paf files (1.1) and the results folder
(1.2), and to read a summary of every file.

---- Inputs ----
last : dict
    Remembered answers (last_answers.json); uses data_folder and export_folder.

---- Globals read ----
None.

---- Outputs ----
Tuple[Path, List[dict], Path]
    (data folder, summary of each readable file, results folder). Each summary
    has name, path, duration_min, events and datasets (DATA_FORMAT.md).

---- Globals mutated ----
None. Reads from and prints to the terminal (side effect).

---- Equations ----
None.

---- Helpers ----
experiment_summary_reader
info_printer
paf_finder
path_cleaner
progress_clearer
progress_printer
text_asker
```

#### `haem_form_option_builder`

```text
---- Summary ----
Helper function to build the (key, label) choices for the 'how to show the
haems' questions. The delta A line explains itself in italics.

---- Inputs ----
include_percent : bool
    True to offer the % oxidised choice.

---- Globals read ----
None.

---- Outputs ----
List[Tuple[str, str]]
    [(key, label), ...]: abs, delta, conc and optionally percent.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
text_italiser
```

#### `haem_name_formatter`

```text
---- Summary ----
Main function to write a haem name for the terminal: the $...$ maths markers are
removed, subscripts are written as plain characters (Unicode subscripts are hard to
read) and the maths part is shown in italics, e.g. 'Cyt $b_H$' becomes 'Cyt bH'.

---- Inputs ----
name : str
    Haem name as written in the fit file.

---- Globals read ----
None.

---- Outputs ----
str
    Name for display only; the original name is still used everywhere else.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_maths_converter
```

#### `haem_name_sorter`

```text
---- Summary ----
Main function to put haem names in alphabetical order of the name as shown (ignoring
case and punctuation), for example a605, b557, bH, bL, cc.

---- Inputs ----
names : List[str]
    Haem names as written in the fit file.

---- Globals read ----
None.

---- Outputs ----
List[str]
    The same names, sorted; the input list is not changed.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
name_simplifier
```

#### `multi_experiment_asker`

```text
---- Summary ----
Main function to ask section 5: the side-by-side figure of two experiments and
the 2x2 figure of four experiments.

---- Inputs ----
summaries : List[dict]
    File summaries (DATA_FORMAT.md).
answers : dict
    Answers dictionary the values are stored in.
defaults : dict
    Default answers.
plotted : bool
    True when section 4 plots at least one panel (both figures reuse its choices).

---- Globals read ----
None.

---- Outputs ----
tuple
    (comparison, exemplar_names). comparison is {'runs': (left, right),
    'columns', 'height'} or None; exemplar_names is the list of the four
    experiments of the 2x2 figure, or None.

---- Globals mutated ----
None. Stores the answers in ``answers`` (side effect).

---- Equations ----
None.

---- Helpers ----
averaging_asker
choice_asker
info_printer
run_name_lister
size_asker
yes_no_asker
```

#### `ocr_option_builder`

```text
---- Summary ----
Helper function to build the (key, label) choices for the OCR questions, using
the units of the plot axes.

---- Inputs ----
keys : List[str]
    OCR kinds offered: 'raw', 'od' and/or 'percent'.

---- Globals read ----
OCR_LABELS (module constant).

---- Outputs ----
List[Tuple[str, str]]
    [(key, label), ...] in the order of ``keys``.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `od_asker`

```text
---- Summary ----
Main function to ask the OD, volume and dilution factor of every file, offering the
values saved in each experiment's workbook.

---- Inputs ----
summaries : List[dict]
    File summaries (DATA_FORMAT.md).
saved : dict
    {file name: values read from its workbook} (read_saved_settings).

---- Globals read ----
None.

---- Outputs ----
Dict[str, dict]
    {file name: {'OD', 'volume', 'dilution_factor'}}.

---- Globals mutated ----
None. Reads from and prints to the terminal (side effect).

---- Equations ----
None.

---- Helpers ----
_file_focuser
info_printer
number_asker
numbering_restarter
```

#### `od_scaling_asker`

```text
---- Summary ----
Main function to ask whether to scale by OD and, if so, the OD, volume and dilution
factor of every file, offering the stored values.

---- Inputs ----
summaries : List[dict]
    File summaries (DATA_FORMAT.md).
answers : dict
    Answers dictionary the values are stored in.
defaults : dict
    Default answers (normalise_od).
saved : dict
    {file name: values read from its workbook} (saved_values_reader).

---- Globals read ----
None.

---- Outputs ----
Dict[str, dict]
    {file name: {'OD', 'volume', 'dilution_factor'}}; the dictionaries are empty
    when not scaling by OD.

---- Globals mutated ----
None. Stores normalise_od in ``answers`` and reads from and prints to the terminal
(side effects).

---- Equations ----
None.

---- Helpers ----
info_printer
od_asker
yes_no_asker
```

#### `paf_finder`

```text
---- Summary ----
Helper function to list the .paf files directly inside a folder, by name.

---- Inputs ----
folder : Path
    Existing folder.

---- Globals read ----
None.

---- Outputs ----
List[Path]
    The .paf files, sorted case-insensitively by name.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
_natural_sorter
```

#### `plot_asker`

```text
---- Summary ----
Main function to ask section 4: what the individual experiment figures show and
how they are sized.

---- Inputs ----
answers : dict
    Answers dictionary the values are stored in; must hold normalise_od and
    decompose.
defaults : dict
    Default answers.
fit : Optional[dict]
    Fit dictionary (haem_list) used to list the haems, or None.

---- Globals read ----
None.

---- Outputs ----
bool
    True when at least one panel is plotted.

---- Globals mutated ----
None. Stores the answers in ``answers`` (side effect).

---- Equations ----
None.

---- Helpers ----
choice_asker
haem_form_option_builder
haem_name_formatter
haem_name_sorter
info_printer
multi_asker
number_asker
ocr_option_builder
size_asker
yes_no_asker
```

#### `saved_values_reader`

```text
---- Summary ----
Main function to read the OD and event values saved in each experiment's workbook
from an earlier run, so they can be offered as defaults.

---- Inputs ----
summaries : List[dict]
    File summaries (DATA_FORMAT.md).
export_root : Path
    Results folder, where the saved workbooks are looked for.

---- Globals read ----
None.

---- Outputs ----
Dict[str, dict]
    {file name: values read from its workbook, or None when there is none}.

---- Globals mutated ----
None. Prints progress and a note when earlier values are found (side effects).

---- Equations ----
None.

---- Helpers ----
info_printer
progress_clearer
progress_printer
saved_settings_reader
```

#### `size_asker`

```text
---- Summary ----
Main function to ask the journal, width and height of one figure. Answering None
to the journal question uses Nature with the fallback width and height.

---- Inputs ----
answers : dict
    Answers dictionary the values are stored in.
defaults : dict
    Default answers.
keys : dict
    Names of the answers: {'journal', 'columns', 'height', 'mode'}.
fallback : Tuple[float, float]
    (columns, height) used when the journal is None.
depth : int
    Numbering depth of the journal question.

---- Globals read ----
config.JOURNAL_SPECS.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Stores the four answers in ``answers`` (side effect).

---- Equations ----
None.

---- Helpers ----
_columns_text_builder
choice_asker
number_asker
```

#### `trim_asker`

```text
---- Summary ----
Main function to ask section 2: which data is trimmed away (start, end) and which
is ignored in the calculations (start, end), per file.

---- Inputs ----
summaries : List[dict]
    File summaries (DATA_FORMAT.md).
remembered : dict
    {file name: {trim_start, trim_end, ignore_start, ignore_end}} from the last
    run; offered as the defaults.

---- Globals read ----
config.DEFAULT_ANSWERS (default ignore time at the start).

---- Outputs ----
Dict[str, dict]
    {file name: {'trim_start', 'trim_end' (minutes on the original recording, or
    None), 'ignore_start', 'ignore_end' (minutes, counted from the new 0 time)}}.

---- Globals mutated ----
None. Reads from and prints to the terminal (side effect).

---- Equations ----
None.

---- Helpers ----
_first_event_finder
_last_event_finder
_limits_asker
info_printer
```

## `utils_shared/trimming.py`

Trimming of the start and end of an experiment.

### MAIN FUNCTIONS

#### `experiment_trimmer`

```text
---- Summary ----
Main function to keep only the part of an experiment between a start and an end
time. After a start trim the time axis is re-zeroed so the chosen start becomes 0,
and events keep their original datapoint numbers.

---- Inputs ----
experiment : dict
    Experiment dictionary, as defined in DATA_FORMAT.md.
start_time : Optional[float]
    Start of the part kept, in minutes on the original recording; None keeps the
    start.
end_time : Optional[float]
    End of the part kept, in minutes on the original recording; None keeps the end.

---- Globals read ----
TIME_COLUMN (module constant).

---- Outputs ----
dict
    The same experiment dictionary, trimmed in place. Raises ValueError for an
    invalid time range, events outside the range, no data left, or missing spectrum
    times.

---- Globals mutated ----
None. Trims CcO2, CsO2, VoO2 and the raw spectra, shifts the event times and sets
metadata trimmed_before_minutes / trimmed_after_minutes in place (side effects).

---- Equations ----
t_new = t - start_time; rows kept where start_time <= t <= end_time.

---- Helpers ----
None.
```

## `utils_viewer/viewer_gui.py`

The experiment browser window: a text terminal on the left that asks the questions, and

### CLASSES

#### `GuiUnavailable`

```text
---- Summary ----
Raised when the browser window cannot be opened (no Tkinter, no display, or the
window was switched off), so the program can use the terminal instead.

---- Attributes ----
None.

---- Globals read ----
None.

---- Methods ----
None.
```

#### `ViewerGui`

```text
---- Summary ----
The experiment browser window. The program's questions run in their own thread and
their text and answers pass through the terminal on the left, so the plot on the
right stays usable while a question waits. Previews are drawn by a third thread.

---- Attributes ----
is_interactive : bool
    Always True: the window has its own file controls.
logic_thread : Optional[threading.Thread]
    The thread running the program, whose output belongs in the terminal.
exit_code : int
    What the program returned (1 when it was stopped).

---- Globals read ----
MONO_FONTS and the colour constants (module constants).

---- Methods ----
__init__
_answer_sender
_closing_handler
_drain_runner
_event_handler
_history_stepper
_image_receiver
_logic_runner
_navigator
_pane_writer
_picture_shower
_step_taker
_widgets_builder
file_focuser
figure_shower
input_reader
output_capturer
run
session_attacher
spec_publisher
text_sender
window_closer
```

##### `__init__`

```text
---- Summary ----
Method to build the window and set up the queues between its threads.

---- Inputs ----
tk : Any
    The tkinter module.
root : Any
    The Tk root window.
program : Callable[[], int]
    The program to run; it asks the questions and returns its exit code.
title : str
    Window title.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Sets the attributes on the instance and builds the widgets.

---- Equations ----
None.

---- Helpers ----
_widgets_builder
```

##### `_widgets_builder`

```text
---- Summary ----
Method to build the terminal, the answer box, the plot and its file controls.

---- Inputs ----
None.

---- Globals read ----
MONO_FONTS and the colour constants (module constants).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Creates the widgets (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `_nav_state`

```text
---- Summary ----
Method to switch the file selector and arrows on or off.

---- Inputs ----
enabled : bool
    True to allow navigation.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes the widget states (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `_message_shower`

```text
---- Summary ----
Method to replace the plot with a short message.

---- Inputs ----
text : str
    Message to show.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Redraws the plot area (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `_resizer`

```text
---- Summary ----
Method to redraw the picture at the new size once the window has stopped
changing size.

---- Inputs ----
event : Any
    The Tk configure event (unused).

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Schedules a redraw (side effect).

---- Equations ----
None.

---- Helpers ----
_picture_shower
```

##### `_picture_shower`

```text
---- Summary ----
Method to show the picture of the current file, scaled to fit the plot area, or
say why there is none yet.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Redraws the plot area and the status line (side effect).

---- Equations ----
scale = min(width / picture width, height / picture height), at most 1.5.

---- Helpers ----
_message_shower
```

##### `_navigator`

```text
---- Summary ----
Method to make a file the current one and show it.

---- Inputs ----
index : int
    Position of the file in the list.
is_from_user : bool
    True when the user chose it, so the answer box gets the keyboard back.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Updates the selector, the plot and the renderer's order (side effects).

---- Equations ----
None.

---- Helpers ----
_picture_shower
```

##### `_step_taker`

```text
---- Summary ----
Method to move to the next or previous file, looping round at the ends.

---- Inputs ----
step : int
    +1 for the next file, -1 for the previous one.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes the current file (side effect).

---- Equations ----
None.

---- Helpers ----
_navigator
```

##### `_pane_writer`

```text
---- Summary ----
Method to add text to the terminal, with its colours, overwriting the line when
the text starts with a carriage return (progress messages).

---- Inputs ----
text : str
    Text as printed.
kind : str
    'out' (normal), 'err' (error text) or 'answer' (what the user typed).

---- Globals read ----
ANSWER_COLOUR, ERROR_COLOUR (module constants).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Adds text to the terminal and scrolls it (side effects).

---- Equations ----
None.

---- Helpers ----
ansi_splitter
ansi_style_updater
```

##### `_answer_sender`

```text
---- Summary ----
Method to pass the typed answer to the question that is waiting for it.

---- Inputs ----
event : Any
    The Tk key event (unused).

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Writes the answer into the terminal, clears and disables the answer box
and wakes the question thread (side effects).

---- Equations ----
None.

---- Helpers ----
_pane_writer
```

##### `_history_stepper`

```text
---- Summary ----
Method to recall an earlier answer in the answer box with the up and down keys.

---- Inputs ----
step : int
    -1 for the previous answer, +1 for the next one.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes the text of the answer box (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `_image_receiver`

```text
---- Summary ----
Method to take a finished preview from the renderer and show it if it is the
current file. Previews of older settings are dropped.

---- Inputs ----
version : int
    Number of the request the preview was drawn for.
name : str
    File name.
png : Optional[bytes]
    Picture, or None when it could not be drawn.
notes : str
    Warnings, or the reason when there is no picture.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Stores the preview and may redraw the plot area (side effects).

---- Equations ----
None.

---- Helpers ----
_picture_shower
```

##### `_event_handler`

```text
---- Summary ----
Method to carry out one message from the other threads, on the window thread.

---- Inputs ----
event : tuple
    (kind, ...) with kind 'prompt', 'spec', 'focus', 'session', 'image',
    'closed' or 'finished'.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes the window (side effects).

---- Equations ----
None.

---- Helpers ----
_image_receiver
_navigator
_pane_writer
_picture_shower
```

##### `_drain_runner`

```text
---- Summary ----
Method that runs on the window thread every few milliseconds and carries out the
messages the other threads have queued, joining consecutive text into one
insert.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes the window and schedules itself again (side effects).

---- Equations ----
None.

---- Helpers ----
_event_handler
_pane_writer
```

##### `_closing_handler`

```text
---- Summary ----
Method to close the window. While the program is still running the user is asked
first, and a question that is waiting is ended so the program stops cleanly.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Stops the threads and closes the window (side effects).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `_logic_runner`

```text
---- Summary ----
Method that runs the program in its own thread and reports when it is done.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Sets exit_code and queues the finished message (side effects).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `file_focuser`

```text
---- Summary ----
Method to show the file a question is about. It is called from the question
thread.

---- Inputs ----
name : str
    Name of the file.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Queues the change for the window (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `figure_shower`

```text
---- Summary ----
Method that is never needed: the window draws its own previews from the
settings (spec_publisher).

---- Inputs ----
figure : Any
    A drawn figure (ignored).

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

##### `input_reader`

```text
---- Summary ----
Method that replaces the built-in input while the window is open: it shows the
prompt in the terminal and waits for the answer typed in the answer box. Other
threads still use the real input.

---- Inputs ----
prompt : Any
    The prompt text, for example "   > ".

---- Globals read ----
None.

---- Outputs ----
str
    The typed answer. Raises EOFError when the window is closed.

---- Globals mutated ----
None. Waits for the user (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `output_capturer`

```text
---- Summary ----
Method to capture what the current thread prints (the preview thread), without
touching the terminal or the log file.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
Iterator[io.StringIO]
    The buffer the output is collected in.

---- Globals mutated ----
None. Captures the output of the current thread (side effect).

---- Equations ----
None.

---- Helpers ----
output_capturer
```

##### `run`

```text
---- Summary ----
Method to run the program in the window: take over the output streams and the
input, start the program thread, and run the window until it is closed.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
int
    The exit code of the program (1 when the window was closed before it
    finished).

---- Globals mutated ----
None. Replaces sys.stdout, sys.stderr and the built-in input while the window
runs, and restores them afterwards (side effects).

---- Equations ----
None.

---- Helpers ----
_drain_runner
_logic_runner
```

##### `session_attacher`

```text
---- Summary ----
Method to give the window the files of the browser session, which fills the
file selector and starts the preview thread.

---- Inputs ----
session : ViewerSession
    The browser session.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Queues the session for the window (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `spec_publisher`

```text
---- Summary ----
Method to give the window new settings: every file is drawn again with them.

---- Inputs ----
spec : PreviewSpec
    The settings to draw with.
name : Optional[str]
    File to show first, or None to stay on the current file.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Queues the settings for the window (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `text_sender`

```text
---- Summary ----
Method to queue text from the program thread for the terminal.

---- Inputs ----
text : str
    Text as printed.
kind : str
    'out' or 'err'.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Queues the text (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `window_closer`

```text
---- Summary ----
Method to end the previews when the browser steps are over: the preview thread
is stopped (so it cannot clash with the processing that follows) and the file
controls are switched off. The last picture stays on show.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Stops the preview thread and queues the change (side effects).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `_image_deliverer`

```text
---- Summary ----
Method to queue a finished preview from the preview thread for the window.

---- Inputs ----
version : int
    Number of the request it was drawn for.
name : str
    File name.
png : Optional[bytes]
    Picture, or None when it could not be drawn.
notes : str
    Warnings, or the reason when there is no picture.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Queues the preview (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `active_gui_getter`

```text
---- Summary ----
Main function to give the browser window that is open, if any.

---- Inputs ----
None.

---- Globals read ----
_active_gui (module state).

---- Outputs ----
Optional[ViewerGui]
    The open window, or None when the program runs in the terminal.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `gui_runner`

```text
---- Summary ----
Main function to run the whole program inside the browser window. It returns None
without running anything when the window cannot be opened, so the caller can run
the program in the terminal instead.

---- Inputs ----
program : Callable[[], int]
    The program; it asks the questions and returns its exit code.
title : str
    Window title.

---- Globals read ----
os.environ["DEPALENCIFY_NO_GUI"] (set to anything to keep the terminal).

---- Outputs ----
Optional[int]
    The exit code of the program, or None when the window could not be opened.

---- Globals mutated ----
None. Opens the window and runs the program (side effects); prints why the window
could not open when it could not.

---- Equations ----
None.

---- Helpers ----
ViewerGui
```

## `utils_viewer/viewer_preview.py`

Processing and drawing of one experiment as a preview figure.

### CLASSES

#### `PreviewSpec`

```text
---- Summary ----
The settings a preview is drawn with: the answers given so far. Every file is drawn
with the same spec, so the files can be compared.
Detailed structure can be found in DATA_FORMAT.md.
```

#### `ViewerSession`

```text
---- Summary ----
Everything the experiment browser keeps between steps: the files, the window and the
recently read experiments.
Detailed structure can be found in DATA_FORMAT.md.
```

### PREVIEW HELPERS

#### `_info_builder`

```text
---- Summary ----
Helper function to build the per-file information dictionary that
experiment_data_processor needs, from the answers given so far.

---- Inputs ----
summary : dict
    File summary (DATA_FORMAT.md).
limits : dict
    {file name: {trim_start, trim_end, ignore_start, ignore_end}} in minutes; may
    lack the file.
details : dict
    {file name: {OD, volume, dilution_factor, events}}; may lack the file.

---- Globals read ----
None.

---- Outputs ----
dict
    Per-file information (as built in everything_asker).

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_loaded_experiment_getter`

```text
---- Summary ----
Helper function to give a fresh copy of an experiment read from its file. The file
is read once and kept for the next previews (the last few files only), and read
again when the spectra of a dataset are needed that were not read before.

---- Inputs ----
session : ViewerSession
    The browser session holding the cache.
summary : dict
    File summary (DATA_FORMAT.md).
dataset : Optional[str]
    Spectral dataset needed for the haem decomposition, or None for no spectra.

---- Globals read ----
MAX_CACHED_FILES (module constant).

---- Outputs ----
dict
    A deep copy of the experiment dictionary, safe to trim and process in place.

---- Globals mutated ----
None. Updates the cache of the session (side effect).

---- Equations ----
None.

---- Helpers ----
experiment_paf_loader
```

#### `_overlay_drawer`

```text
---- Summary ----
Helper function to shade regions of the time axis on every panel of the preview.

---- Inputs ----
fig : Figure
    The preview figure.
axes : list
    Panels of the preview, top to bottom.
regions : list
    [(start_min, end_min, kind)] with kind 'trim' (grey hatched) or 'ignore'
    (amber).
note : str
    Short explanation of the shading, written in the corner of the figure; may be
    empty.

---- Globals read ----
IGNORE_COLOUR, TRIM_COLOUR (module constants).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Adds shaded regions and the note to the figure (side effects).

---- Equations ----
None.

---- Helpers ----
None.
```

### MAIN FUNCTIONS

#### `preview_drawer`

```text
---- Summary ----
Main function to show the answers given so far in the window. A window with its own
controls (the experiment browser window) is given the settings and draws every file
the user looks at with them; otherwise the current file is drawn and saved as a
picture. Problems are reported, never raised, so the questions carry on.

---- Inputs ----
session : ViewerSession
    The browser session (files, window, cache, current file).
answers : dict
    Answers so far; missing keys come from config.DEFAULT_ANSWERS.
limits : dict
    {file name: {trim_start, trim_end, ignore_start, ignore_end}} in minutes.
fit : Optional[dict]
    Fit dictionary from fit_importer, or None.
details : dict
    {file name: {OD, volume, dilution_factor, events}}.
show_trim : bool
    True to draw the whole recording and shade the part that would be trimmed, so
    the trim limits can be judged. False draws the trimmed data.
show_ignored : bool
    True to shade the ignored start and end in amber.
name : Optional[str]
    File to show; None keeps the file being looked at.

---- Globals read ----
None.

---- Outputs ----
bool
    True when the preview was drawn (or handed to the window), False when it could
    not be.

---- Globals mutated ----
None. Draws in the window or writes the preview picture (side effects).

---- Equations ----
None.

---- Helpers ----
preview_figure_builder
```

#### `preview_figure_builder`

```text
---- Summary ----
Main function to process one file with the answers of a spec and draw it in a new
figure. Problems are reported, never raised.

---- Inputs ----
session : ViewerSession
    The browser session (files, window, cache).
spec : PreviewSpec
    The settings to draw with.
name : str
    Name of the file to draw.

---- Globals read ----
settings.Config; PREVIEW_DPI (module constant).

---- Outputs ----
Tuple[Optional[Figure], str]
    (figure, notes). The figure is None when the preview could not be drawn, and
    the notes then say why. Otherwise the notes are the warnings of the processing
    (a skipped step, a missing OD), one per line, and may be empty.

---- Globals mutated ----
None. Sets the matplotlib rcParams of the figure style (side effect). Nothing is
printed; the caller decides where the notes go.

---- Equations ----
None.

---- Helpers ----
_info_builder
_loaded_experiment_getter
_overlay_drawer
```

## `utils_viewer/viewer_renderer.py`

The background thread of the experiment browser window that draws the previews.

### CLASSES

#### `PreviewRenderer`

```text
---- Summary ----
Thread that draws the preview of every file with the latest settings, the file being
looked at first and then its neighbours, so the files can be flicked through while a
question waits. A newer request makes it drop the work for the older one.

---- Attributes ----
None public.

---- Globals read ----
PREVIEW_DPI (imported constant).

---- Methods ----
__init__
_next_picker
_picture_maker
request_setter
run
stopper
wanted_setter
```

##### `__init__`

```text
---- Summary ----
Method to set up the thread (it is started by the caller).

---- Inputs ----
session : ViewerSession
    The browser session (files, cache).
deliver : Callable[[int, str, Optional[bytes], str], None]
    Function called with (version, file name, PNG bytes or None, notes) for each
    finished preview. It is called from this thread.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Sets the attributes on the instance.

---- Equations ----
None.

---- Helpers ----
None.
```

##### `_next_picker`

```text
---- Summary ----
Method to pick the file to draw next: the nearest one to the file being looked
at that has not been drawn with the current settings. The caller holds the lock.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
Optional[str]
    File name, or None when every file is drawn.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

##### `_picture_maker`

```text
---- Summary ----
Method to draw one file and turn the figure into a PNG picture.

---- Inputs ----
spec : PreviewSpec
    The settings to draw with.
name : str
    Name of the file.

---- Globals read ----
PREVIEW_DPI (imported constant).

---- Outputs ----
Tuple[Optional[bytes], str]
    (PNG bytes, notes); the bytes are None when the preview could not be drawn
    and the notes then say why.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
preview_figure_builder
```

##### `request_setter`

```text
---- Summary ----
Method to ask for every file to be drawn again with new settings.

---- Inputs ----
spec : PreviewSpec
    The new settings.
version : int
    Number of this request; results carry it so old ones can be dropped.
wanted : int
    Index of the file being looked at, which is drawn first.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Replaces the work of the thread (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `run`

```text
---- Summary ----
Method that draws previews until stopped. The name is fixed by the thread
protocol.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Passes each finished preview to the window (side effect).

---- Equations ----
None.

---- Helpers ----
_next_picker
_picture_maker
```

##### `stopper`

```text
---- Summary ----
Method to stop the thread and wait until it has finished its current preview.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Stops the thread (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `wanted_setter`

```text
---- Summary ----
Method to say which file is being looked at, so it is drawn next.

---- Inputs ----
wanted : int
    Index of the file.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Changes the order of the work (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

## `utils_viewer/viewer_stages.py`

The steps of the experiment browser: ask, redraw the plot window, then accept or repeat.

### STAGE HELPERS

#### `_answers_previewer`

```text
---- Summary ----
Helper function to build the answers used to draw a preview: the raw data while
browsing and trimming, and the analysis chosen so far afterwards.

---- Inputs ----
answers : dict
    Answers given so far.
fit : Optional[dict]
    Fit dictionary, used to list the haems to show.
kind : str
    'raw' (O2 and the raw OCR only), 'analysis' (also the haems and the OD scaling
    chosen so far, in a wide preview) or 'final' (exactly as the figure will be).

---- Globals read ----
BROWSING_ANSWERS (module constant).

---- Outputs ----
dict
    A copy of the answers with the preview settings; ``answers`` is not changed.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `_file_chooser`

```text
---- Summary ----
Helper function to ask which file to look at and make it the current one.

---- Inputs ----
session : ViewerSession
    The browser session; its current file is changed.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Sets session.current and reads from and prints to the terminal (side
effects).

---- Equations ----
None.

---- Helpers ----
choice_asker
```

#### `_limits_lister`

```text
---- Summary ----
Helper function to print the trim and ignore limits of every file in one list.

---- Inputs ----
summaries : List[dict]
    File summaries (DATA_FORMAT.md).
limits : Dict[str, dict]
    {file name: {trim_start, trim_end, ignore_start, ignore_end}} in minutes.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Prints to the terminal (side effect).

---- Equations ----
None.

---- Helpers ----
info_printer
```

#### `_review_asker`

```text
---- Summary ----
Helper function to ask whether the user accepts what the plot window shows. In the
browser window the user flicks through the files while the question waits; with the
picture fallback the user can ask to look at another file, which redraws it.

---- Inputs ----
session : ViewerSession
    The browser session; its current file may be changed.
question : str
    The accept question, for example 'Do you accept these limits?'.
change_label : str
    Label of the answer that asks the questions of the step again.
redraw : Callable[[], bool]
    Function that draws the preview of the current file.

---- Globals read ----
None.

---- Outputs ----
bool
    True when accepted, False when the user wants to answer the step again.

---- Globals mutated ----
None. Reads from and prints to the terminal and redraws the window (side effects).

---- Equations ----
None.

---- Helpers ----
_file_chooser
choice_asker
```

### MAIN FUNCTIONS

#### `analysis_stage_runner`

```text
---- Summary ----
Main function to ask the analysis questions (haem decomposition, OD scaling, event
averaging and event labels) one at a time, redrawing the plot window after each so
the result can be accepted or asked again.

---- Inputs ----
session : ViewerSession
    The browser session.
answers : dict
    Answers dictionary the values are stored in.
defaults : dict
    Default answers offered by the questions.
limits : Dict[str, dict]
    Trim and ignore limits of every file (trim_asker).
fits_folder : Path
    Folder holding the fit .csv files.
details_before : Optional[Dict[str, dict]]
    OD values and events from an earlier pass, offered as defaults when the step is
    asked again.

---- Globals read ----
None.

---- Outputs ----
Tuple[Optional[dict], Dict[str, dict]]
    (fit, details) exactly as analysis_asker returns them.

---- Globals mutated ----
None. Stores the answers in ``answers`` (side effect).

---- Equations ----
None.

---- Helpers ----
_answers_previewer
_review_asker
averaging_asker
decomposition_asker
event_asker
od_scaling_asker
preview_drawer
saved_values_reader
```

#### `browser_stage_runner`

```text
---- Summary ----
Main function to let the user look through the files in the plot window (the set and
measured O2 and the OCR, with the events) before answering any questions about
them.

---- Inputs ----
session : ViewerSession
    The browser session; its current file is changed.
answers : dict
    Answers so far, used for the figure style of the preview.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Reads from and prints to the terminal and draws the plot window (side
effects).

---- Equations ----
None.

---- Helpers ----
_answers_previewer
_file_chooser
choice_asker
info_printer
preview_drawer
```

#### `plots_stage_runner`

```text
---- Summary ----
Main function to ask what the individual figures show and how they are sized, then
draw the figure as it will be saved and ask whether to accept it.

---- Inputs ----
session : ViewerSession
    The browser session.
answers : dict
    Answers dictionary the values are stored in.
defaults : dict
    Default answers offered by the questions.
limits : Dict[str, dict]
    Trim and ignore limits of every file.
fit : Optional[dict]
    Fit dictionary, or None.
details : Dict[str, dict]
    OD values and events of every file.

---- Globals read ----
None.

---- Outputs ----
bool
    True when at least one panel is plotted (as plot_asker returns it).

---- Globals mutated ----
None. Stores the answers in ``answers`` (side effect).

---- Equations ----
None.

---- Helpers ----
_answers_previewer
_review_asker
plot_asker
preview_drawer
```

#### `trim_stage_runner`

```text
---- Summary ----
Main function to ask the trim and ignore questions, shade the trimmed and ignored
parts in the plot window, and ask whether to accept them.

---- Inputs ----
session : ViewerSession
    The browser session.
answers : dict
    Answers so far, used for the figure style of the preview.
remembered : Dict[str, dict]
    {file name: {trim_start, trim_end, ignore_start, ignore_end}} offered as the
    defaults (from the last run, or from the previous attempt).

---- Globals read ----
None.

---- Outputs ----
Dict[str, dict]
    The limits of every file, exactly as trim_asker returns them.

---- Globals mutated ----
None. Reads from and prints to the terminal and draws the plot window (side
effects).

---- Equations ----
None.

---- Helpers ----
_answers_previewer
_limits_lister
_review_asker
preview_drawer
trim_asker
```

#### `viewer_asker`

```text
---- Summary ----
Main function to ask the questions of the experiment browser: the file browser,
trimming and ignoring, the analysis and the individual figures. The plot window is
redrawn after each answer, and at the end any step can be gone back to.

---- Inputs ----
summaries : List[dict]
    File summaries (DATA_FORMAT.md).
answers : dict
    Answers dictionary the values are stored in.
defaults : dict
    Default answers offered by the questions.
remembered : Dict[str, dict]
    {file name: limits} from the last run.
fits_folder : Path
    Folder holding the fit .csv files.
export_root : Path
    Results folder.

---- Globals read ----
PREVIEW_FILE, STAGE_TITLES (module constants).

---- Outputs ----
Tuple[Dict[str, dict], Optional[dict], Dict[str, dict], bool]
    (limits, fit, details, plotted) as the same questions return them when they are
    asked without the browser.

---- Globals mutated ----
None. Stores the answers in ``answers``, reads from and prints to the terminal,
draws and closes the plot window (side effects).

---- Equations ----
None.

---- Helpers ----
analysis_stage_runner
browser_stage_runner
choice_asker
file_focus_setter
heading_printer
numbering_getter
numbering_setter
plots_stage_runner
section_starter
trim_stage_runner
```

## `utils_viewer/viewer_terminal.py`

Pieces of the text terminal in the experiment browser window: colour codes and the

### CLASSES

#### `OutputRouter`

```text
---- Summary ----
File-like object that replaces sys.stdout and sys.stderr while the browser window
is open. What the program's own thread prints goes to the terminal in the window;
what other threads print goes to the real stream; and a thread that is capturing its
output (output_capturer) keeps it to itself.

---- Attributes ----
encoding : str
    Always "utf-8".

---- Globals read ----
None.

---- Methods ----
__init__
__getattr__
fileno
flush
isatty
reconfigure
write
```

##### `__init__`

```text
---- Summary ----
Method to store where the text goes.

---- Inputs ----
original : Any
    The stream that was replaced; used for other threads and after the window is
    closed.
sender : Callable[[str, str], None]
    Function that passes (text, kind) to the window.
kind : str
    'out' for standard output or 'err' for standard error.
owner : Callable[[], Optional[threading.Thread]]
    Function that gives the thread whose output belongs in the window (None
    once the window is closed).

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Sets the attributes on the instance.

---- Equations ----
None.

---- Helpers ----
None.
```

##### `__getattr__`

```text
---- Summary ----
Method to pass any other attribute lookup to the stream that was replaced.

---- Inputs ----
name : str
    Attribute name that was not found on the instance.

---- Globals read ----
None.

---- Outputs ----
Any
    The attribute of the original stream.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

##### `fileno`

```text
---- Summary ----
Method that says there is no file descriptor, so libraries that ask for one fall
back to plain writes. The name is fixed by the file-like protocol.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
int
    Never returns; raises io.UnsupportedOperation.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

##### `flush`

```text
---- Summary ----
Method that does nothing: text is passed on as soon as it is written. The name
is fixed by the file-like protocol.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

##### `isatty`

```text
---- Summary ----
Method to say that the stream shows colour, because the terminal in the window
does. The name is fixed by the file-like protocol.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
bool
    Always True.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

##### `reconfigure`

```text
---- Summary ----
Method that accepts and ignores new stream settings, because the window shows
every symbol.

---- Inputs ----
**kwargs : Any
    Stream settings (ignored).

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

##### `write`

```text
---- Summary ----
Method to send text where it belongs: the capture of the thread, the window, or
the real stream. The name is fixed by the file-like protocol.

---- Inputs ----
text : str
    Text to write.

---- Globals read ----
None.

---- Outputs ----
int
    Number of characters written.

---- Globals mutated ----
None. Passes text to the window or the real stream (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

### TERMINAL HELPERS

#### `ansi_colour_getter`

```text
---- Summary ----
Main function to give the colour of an entry of the 256-colour terminal palette.

---- Inputs ----
index : int
    Palette number, 0 to 255 (0-15 basic, 16-231 colour cube, 232-255 greys).

---- Globals read ----
BASIC_COLOURS (module constant).

---- Outputs ----
str
    The colour as "#rrggbb".

---- Globals mutated ----
None.

---- Equations ----
Cube colours: each of red, green and blue is 0 for level 0 and 55 + 40 * level
for levels 1 to 5, where index - 16 = 36 * red level + 6 * green level + blue
level. Greys: 8 + 10 * (index - 232).

---- Helpers ----
None.
```

#### `ansi_splitter`

```text
---- Summary ----
Main function to cut printed text into plain text, colour codes and carriage
returns, in order, so a text window can colour the text and overwrite progress
lines.

---- Inputs ----
text : str
    Text as printed, possibly with colour codes (ESC[...m) and carriage returns.

---- Globals read ----
_CODE_PATTERN (module constant).

---- Outputs ----
List[Tuple[str, str]]
    [(kind, value)] with kind 'text' (the characters), 'code' (the numbers of a
    colour code, for example "1;33") or 'return' (value empty). A carriage return
    directly before a new line is part of the line ending and is dropped.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

#### `ansi_style_updater`

```text
---- Summary ----
Main function to apply one colour code to the current text style.

---- Inputs ----
style : Dict[str, Any]
    {fg, bold, italic}: colour as "#rrggbb" or None for the default, and two flags.
code : str
    Numbers of the colour code, separated by semicolons ("" means reset).

---- Globals read ----
BASIC_COLOURS (module constant).

---- Outputs ----
Dict[str, Any]
    The new style; ``style`` is not changed.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
ansi_colour_getter
```

## `utils_viewer/viewer_window.py`

The fallback preview of the experiment browser: one picture file that is rewritten after

### CLASSES

#### `PictureWindow`

```text
---- Summary ----
The stand-in for the browser window when no window can be opened (no display, or no
Tkinter). Each preview is saved as a picture file, which is opened in the default
picture viewer the first time. It has the same methods as ViewerGui so the questions
do not need to know which one they are using.

---- Attributes ----
preview_path : Path
    Picture file the previews are saved to.
is_interactive : bool
    Always False: the picture cannot be navigated, only rewritten.

---- Globals read ----
PREVIEW_DPI (module constant).

---- Methods ----
__init__
_file_opener
figure_shower
file_focuser
output_capturer
session_attacher
window_closer
```

##### `__init__`

```text
---- Summary ----
Method to set up the stand-in without writing anything yet.

---- Inputs ----
preview_path : Path
    Picture file the previews are saved to.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Sets the attributes on the instance.

---- Equations ----
None.

---- Helpers ----
None.
```

##### `_file_opener`

```text
---- Summary ----
Method to open the preview picture in the default picture viewer (once).

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Starts the picture viewer; a failure to start it is ignored (side
effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `figure_shower`

```text
---- Summary ----
Method to save the preview figure to the picture file and tell the user where it
is.

---- Inputs ----
figure : Figure
    The drawn preview.

---- Globals read ----
PREVIEW_DPI (module constant).

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None. Writes the picture file and prints its path (side effects).

---- Equations ----
None.

---- Helpers ----
_file_opener
```

##### `file_focuser`

```text
---- Summary ----
Method that does nothing: a picture file has no file selector.

---- Inputs ----
name : str
    Name of the file being asked about.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

##### `output_capturer`

```text
---- Summary ----
Method to capture what the processing of a preview prints, so it does not
clutter the questions.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
Iterator[io.StringIO]
    The buffer the output is collected in.

---- Globals mutated ----
None. Replaces sys.stdout while the block runs (side effect).

---- Equations ----
None.

---- Helpers ----
None.
```

##### `session_attacher`

```text
---- Summary ----
Method that does nothing: the picture needs no list of files.

---- Inputs ----
session : Any
    The browser session.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```

##### `window_closer`

```text
---- Summary ----
Method that does nothing: the picture file stays where it is.

---- Inputs ----
None.

---- Globals read ----
None.

---- Outputs ----
None
    Nothing.

---- Globals mutated ----
None.

---- Equations ----
None.

---- Helpers ----
None.
```
