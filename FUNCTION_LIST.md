# Function list

Generated from the source. Names starting with `_` are private helpers.

## DePalencify.py

- `load_last_answers`
- `save_last_answers`
- `find_paf_files`
- `ask_files`: Ask for the folder of .paf files; returns (folder, [summary of each readable file]).
- `ask_trimming`: Returns {file name: {"start": minutes or None, "end": minutes or None}}. All times are on the original recording's clock.
- `ask_decomposition`: Returns (decompose, fit_file, fit, dataset). ``forced`` skips the yes/no question (the special figures need the haems).
- `ask_experiment_details`: OD, volume, dilution factor and event labels for one file; offers the values saved in its workbook last time.
- `ask_everything`: Ask all the questions. Returns (answers, results folder, per-experiment info, fit, comparison pair or None).
- `merge_event_settings`: Copy the label and concentration entered for each event onto the experiment's events (matched by datapoint).
- `process_experiment`: Read, process, plot and export one .paf. Each step reports its own problem and the next step still runs.
- `make_comparison`: The side-by-side figure of the two chosen runs (skipped, with the reason, if either one failed or they were plotted differently).
- `make_special_figures`: The time response and the haem and OCR response figures (each skipped, with the reason, if it cannot be made).
- `main`

## config.py

- `haem_colours`: Colour for each haem name: the original colours for the usual haems, otherwise the next unused colour.

## utils_shared/attenuation.py

- `transmission_to_attenuation`: Convert one transmission spectrum to attenuation
- `add_attenuation_to_experiment`: Add an ``attenuation`` array (spectra x wavelengths) to the datasets in ``raw_spectra`` (all of them if ``datasets`` is None).

## utils_shared/averaging.py

- `window_statistics`: Mean and sample SD of every measurement column within [start_time, end_time]
- `_add_change_from_baseline`: Add ``change`` (window mean as % of the baseline mean) and ``delta`` (window mean minus baseline mean)
- `calculate_experiment_averages`: Calculate event-window statistics and store them in ``experiment["averages"]``

## utils_shared/comparison_plotter.py

- `_renderer`
- `_overhang_pt`: (points the labels of ``members`` stick out to the left of ``main``, to the right of it)
- `plot_comparison`: Draw ``first`` (left, panel a) and ``second`` (right, panel b) with the individual-experiment settings in ``config``

## utils_shared/figure_layout.py

- `figure_size_inches`: (width, height) in inches for a journal spec
- `make_style`: Every font size, padding and line width of the figures, derived from the journal spec and three master settings
- `check_style`: Warnings (a list of strings) for fonts outside the journal's range or a figure taller than it allows.
- `text_extent_pt`: (width, height) in points of the bounding box of ``text`` after rotating it (plain text, no mathtext).
- `gap_to_space`: The GridSpec ``wspace``/``hspace`` that leaves a gap of ``gap_pt`` points between ``n`` equal cells spread over ``extent_pt``
- `_renderer`
- `fit_figure_to_canvas`: Set the figure margins so everything drawn (axes, tick and axis labels, event labels, legends, panel letters) sits
- `_free_top`: Highest edge (pixels) of anything the panel draws between ``left_px`` and ``right_px`` horizontally.
- `add_panel_letters`: Write each panel's letter at the top-left corner of everything that panel draws (labels, ticks, titles)

## utils_shared/helpers.py

- `simplify_name`: Lower-case and strip everything except letters/digits, so 'Cyt $c_1$' == 'cyt c1'.
- `safe_file_name`: Replace characters that are illegal in file names.
- `excel_sheet_name`: Return a valid, unique Excel sheet name (<= 31 chars, no special characters)
- `save_figure_exact`: Save ``fig`` as ``<folder>/<stem>.<ext>`` for each extension, at exactly ``size`` inches (width, height)

## utils_shared/individual_experiment_exporter.py

- `_export_spectral_csvs`: Write one CSV per dataset/type (wavelengths down, one column per spectrum); returns a list of records.
- `averages_table`: Build the Averages worksheet table
- `workbook_path`
- `read_saved_settings`: Return ``{"OD", "volume", "dilution_factor", "events": [{"datapoint", "label", "concentration_uM"}]}`` from an earlier export, or None.
- `export_individual_experiment`: Export one experiment to ``<output_dir>/<experiment name>/<experiment name>.xlsx``

## utils_shared/individual_experiment_plotter.py

- `_first_series`: Return (time, values) for the first measurement column of a DataFrame.
- `_legend`: Legend with an optional thin box. ``text_only`` drops the coloured line beside each entry (used for the haem panels,
- `watermark_style`: Text keyword arguments for the faint run-name watermark (TITLE_STYLE = "watermark").
- `_set_min_ticks`: Make sure an axis has at least ``count`` ticks (None = automatic). Positions stay 'nice' round values, so it can be one more.
- `_ylim_ignoring_start`: (low, high) of the data after the first ``ignore_minutes``, plus a margin; None if no finite data remain.
- `_height_ratios`: Relative panel heights from PANEL_HEIGHT_RATIOS ({"oxygen": a, "vo2": b, "haem": c})
- `_window_label`: Text for an averaging window from AVERAGING_WINDOW_LABEL_FORMAT ({n} = number, {name} = e.g. "average3"; "" = no label).
- `_select_haem_data`: Return (haem DataFrame or None, source name).
- `_build_panels`: List the panels to draw: oxygen, VO2, then one per configured haem panel with matching data.
- `_draw_windows`: Draw the averaging windows behind the data on every axis.
- `experiment_title`: The figure/panel title for an experiment, from ``config["FIGURE_TITLE"]``.
- `draw_experiment`: Draw one experiment's stacked panels into a cell of an existing figure
- `plot_experiment`: Plot one experiment in its own figure, optionally save SVG/PNG to ``<export_root>/<name>/``, then show or close it.

## utils_shared/normalisation.py

- `normalise_data`: Divide numeric data by dilution factor x optical density x volume.
- `_normalise_frame`: OD-normalise the measurement columns of a DataFrame, leaving time/index columns untouched.
- `normalise_experiment`: OD-normalise VoO2 and (if present) the haem data
- `scale_to_percent`: Scale each measurement column to a relative 0-100 % range
- `convert_to_percent`: Scale ``experiment[source_key]`` to 0-100 % and store it as ``experiment[target_key]``

## utils_shared/paf_reader.py

- `warn`
- `u32`
- `read_tokens`: Length-prefixed UTF-16LE strings inside [start, end): 02 00 00 00 <n> <chars>.
- `rtf_to_text`
- `parse_spectra`: Parse one 'Spectra: CCD' record starting at marker offset `off`.
- `scan`
- `extract_streams`
- `dataset_name`
- `read_experiment_summary`: Quick look at a file (no spectra read): duration, events, which spectrometers it holds.
- `load_experiment_from_paf`: Build the experiment dictionary (see utils_shared.schema) straight from a .paf
- `trim_experiment`: Discard everything recorded after ``end_time`` (minutes), e.g. noise from a run that was never stopped.

## utils_shared/questions.py

- `_read`
- `heading`
- `ask_text`
- `ask_yes_no`
- `ask_number`: A number; with ``allow_blank`` an empty answer gives None (when there is no default).
- `ask_choice`: ``options`` is a list of (key, label). The user types the number; returns the key. ``default`` is a key.
- `ask_multi`: Several of ``options`` (a list of labels): numbers separated by commas, or Enter for all. Returns the chosen labels.
- `clean_path`: A path typed or dragged into the window: drop surrounding quotes and spaces.

## utils_shared/run_logging.py

- `start_logging`: Start copying stdout/stderr to ``<export_root>/logs/run_log_<timestamp>.txt``; returns a session dict.
- `stop_logging`: Restore the console streams and close the log file.

## utils_shared/schema.py

- `measurement_columns`: Return the measurement columns of a DataFrame (everything except time/index).
- `get_times`: Return the TIME_COLUMN of a DataFrame as a float array (minutes).
- `get_values`: Return one measurement column as a float array.
- `resolve_source`: Look up a dataset by its config source name
- `finite_or_nan`: Convert to a finite float, or NaN.

## utils_shared/spectral_decomposer.py

- `import_fit`: Import a haem spectral fit CSV
- `_wavelength_mask`: Boolean mask selecting wavelengths inside the range shared by all fits.
- `filter_data`: Filter experimental data (wavelength, value columns) to the wavelength range shared by all fits.
- `s_array_generator`: Generate haem and scatter basis components for one spectrum.
- `decomposition`: Decompose one experimental spectrum into haem contributions and scatter
- `calculate_delta_abs`: Shift every haem's absorbance additively so that its reference level is 0, giving a change in absorbance (mOD)
- `decompose_experiment`: Decompose every spectrum of one dataset and store ``experiment["haem_conc"]``, ``experiment["haem_abs"]`` and

## utils_shared/trimming.py

- `trim_experiment`: Keep only ``start_time <= t <= end_time`` (either may be None)

## utils_custom/custom_config.py

- `haem_labeller`: Main function to give a haem its short y-axis label, for example '$b_H$'.
- `source_selector`: Main function to choose the OCR and haem data sources of the haem and OCR response figures from the answers.
- `publication_config_builder`: Main function to build the settings of the haem and OCR publication figure.
- `exemplar_config_builder`: Main function to build the settings of the four-run exemplar figure.
- `time_response_config_builder`: Main function to build the settings of the time response figure.
- `individual_config_builder`: Main function to build the individual-experiment plot settings used inside the custom figures: oxygen, OCR and one panel per chosen haem.

## utils_custom/custom_questions.py

- `custom_choice_asker`: Main function to ask which of the special figures to make.
- `_size_asker`: Helper function to ask the width and height of one custom figure.
- `_time_response_asker`: Helper function to ask the settings of the time response figure.
- `_haem_ocr_asker`: Helper function to ask the settings of the haem and OCR response figures.
- `custom_detail_asker`: Main function to ask the settings of the special figures that were chosen, after the journal is known.

## utils_custom/custom_runner.py

- `_time_response_preparer`: Helper function to average the spectra in the event windows, subtract the last two windows and decompose the difference spectrum, on a copy of one experiment.
- `_haem_ocr_preparer`: Helper function to calculate the event-window averages used by the haem and OCR response figures, on a copy of one experiment.
- `experiment_preparer`: Main function to prepare one processed experiment for the special figures. Each figure is prepared on its own, so a problem with one does not stop the other.
- `time_response_runner`: Main function to export and draw the time response figure from the prepared experiments.
- `haem_ocr_runner`: Main function to combine the runs of each condition and draw the haem and OCR response: the publication figure and the four-run exemplar figure. The two figures are drawn independently, so a problem with one does not stop the other.

## utils_custom/publication_plotter.py

- `_layout_validator`: Helper function to check that the layout options of the publication figure are recognised and to return the group and order lists.
- `_haem_row_selector`: Helper function to select the haem response rows to draw, in the order listed in HAEM_RESPONSE_SHOW.
- `_experiment_classifier`: Helper function to identify the strain, addition order and run number from an experiment name.
- `_exemplar_selector`: Helper function to pick the experiment of one run number for every (strain, order) cell.
- `_condition_indexer`: Helper function to map each (strain, order) pair to its condition name in the triplicate results.
- `_column_chooser`: Helper function to choose the OCR column: the preferred one if set, else VoO2, else the first available.
- `_measurement_finder`: Helper function to find the column matching a wanted name, ignoring case and punctuation.
- `_axes_styler`: Helper function to apply the tick, grid and spine style of the response and baseline panels.
- `_figure_finisher`: Helper function to fit the margins to the drawn content, add the panel letters at the top-left of each panel and fit again.
- `_block_gap_calculator`: Helper function to calculate the gap between the blocks and between the response columns of the publication figure.
- `_tick_label_builder`: Helper function to build the x tick labels of the averaging windows: Baseline, then the addition that precedes each window.
- `_window_orderer`: Helper function to list the averaging windows present in any condition of one addition order.
- `_reference_selector`: Helper function to pick, for each addition order, the first run of the first available group (used for the event tick labels).
- `_exemplar_gap_calculator`: Helper function to calculate the gap between rows and between columns of the exemplar quadrants.
- `_crop_start_finder`: Helper function to find the time at which an exemplar crop begins.
- `_experiment_cropper`: Helper function to copy an experiment cropped to begin at a chosen time, with time measured from there.
- `_exemplar_plotter`: Helper function to draw one experiment exactly as the individual plotter does.
- `_significance_formatter`: Helper function to format a p value as stars or as text.
- `_significance_bar_drawer`: Helper function to draw a bracket between two x positions with text centred above it.
- `_baseline_bar_plotter`: Helper function to draw the baseline OCR (average0) bar chart per group, with every run overlaid and a Student t-test bracket between the two groups.
- `_metric_field_selector`: Helper function to name the keys of the triplicate statistics used by a response metric.
- `_response_series_drawer`: Helper function to plot every run as a point, the mean as a line and SEM error bars for one group.
- `_p_value_adjuster`: Helper function to adjust a list of p values for multiple comparisons.
- `_test_bar_drawer`: Helper function to draw a small bracket joining the two groups' points at one window with text above it.
- `_response_window_tester`: Helper function to run a Student t-test between the two groups at every window of a response panel and mark the significant windows.
- `_legend_handle_builder`: Helper function to build legend entries showing each group's colour, line style and marker.
- `_response_axes_preparer`: Helper function to draw the baseline reference line and set the window ticks of a response panel.
- `_row_ylim_sharer`: Helper function to give every axes in a row the union of their y ranges.
- `_ocr_block_plotter`: Helper function to draw the OCR response (percent of each run's baseline, mean and SEM across runs), one axes per addition order.
- `_haem_source_finder`: Helper function to find the haem source that every condition's averages were calculated from.
- `_response_metric_checker`: Helper function to reject a percent-of-baseline response for the delta abs sources, which start at 0.
- `_reference_level_finder`: Helper function to find the height of the dashed reference line of the haem response.
- `_haem_label_finder`: Helper function to find the shared y label of the haem response rows.
- `_haem_label_pad_calculator`: Helper function to calculate the points between the shared haem label and the haem axes.
- `_haem_block_plotter`: Helper function to draw the haem response: one row per haem, one column per addition order, a line per group.
- `publication_figure_plotter`: Main function to build the publication figure: baseline OCR, OCR response and haem response blocks.
- `exemplar_figure_plotter`: Main function to build the exemplar figure: one run per condition, each drawn by the individual plotter in its own quadrant.
- `publication_figure_saver`: Main function to save a publication or exemplar figure at its exact size, plus the t-test table when there is one.

## utils_custom/run_namer.py

- `run_name_parser`: Main function to split an experiment name of the form <condition>_run<N> into its condition and run number.
- `condition_classifier`: Main function to identify the strain and the addition order from a condition name.
- `condition_grouper`: Main function to group experiments by condition and run number.
- `hours_parser`: Main function to read the number of hours from an experiment name.
- `_natural_sorter`: Helper function to build a sort key that orders numbers inside names numerically.
- `_group_matcher`: Helper function to find the first group word that appears in an experiment name.
- `group_assigner`: Main function to give every experiment a group from its name and to order the experiments by group and then by hours.
- `run_name_lister`: Main function to describe how each experiment name is read by the haem and OCR response figures, for showing to the user before they choose.

## utils_custom/spectral_difference.py

- `window_definer`: Helper function to lay out the averaging windows of one run.
- `spectral_averager`: Main function to average the chosen spectra in each event window.
- `difference_spectrum_calculator`: Main function to subtract one averaged spectrum from another.
- `difference_spectrum_decomposer`: Main function to decompose the difference spectrum into haem contributions using the shared decomposition.

## utils_custom/time_response_exporter.py

- `time_response_exporter`: Main function to write the haem percentages and difference spectra of each group as CSV files.

## utils_custom/time_response_plotter.py

- `time_label_builder`: Main function to build the label of a time point from the experiment name.
- `shared_baseline_subtracter`: Main function to subtract one shared polynomial baseline, fitted to the mean spectrum, from every spectrum.
- `_title_styler`: Helper function to set a panel title in the figure style.
- `_legend_drawer`: Helper function to draw a legend in the journal style: small text and an optional thin box.
- `_event_label_height_calculator`: Helper function to calculate the height the rotated event labels above the example time courses need.
- `_time_gap_calculator`: Helper function to calculate the row and column gaps of the time response figure from the font sizes and the figure size.
- `_time_axes_styler`: Helper function to apply the tick direction, label size and spine style.
- `group_collector`: Main function to collect the decomposed experiments of each group, with their time labels.
- `waterfall_plotter`: Main function to draw the offset difference spectra of one group, first time point at the top, with additive peak alignment.
- `decomposition_plotter`: Main function to draw a difference spectrum with its scatter-free fit, residual and each haem contribution.
- `_example_finder`: Helper function to find the experiment of one group at a given number of hours.
- `_example_viewer`: Helper function to copy an experiment so that its individual figure shows only the two windows its difference spectrum came from.
- `time_response_figure_plotter`: Main function to build the time response figure: waterfalls, then two examples (time course and decomposition).
- `time_response_figure_saver`: Main function to save the time response figure at its exact size.

## utils_custom/triplicate_averager.py

- `_run_summariser`: Helper function to summarise the finite values of one window across runs.
- `_window_sorter`: Helper function to sort averaging window names numerically.
- `triplicate_averager`: Main function to combine the per-experiment event averages across the runs of each condition.

## utils_custom/triplicate_exporter.py

- `triplicate_exporter`: Main function to write one worksheet per condition of the across-run statistics to an Excel workbook.
