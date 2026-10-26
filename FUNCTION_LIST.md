# Function list

Generated from the source. Names starting with `_` are private helpers.

## DePalencify.py

- `comparison_maker`: Main function to draw the side-by-side figure of two chosen experiments, or to say why it cannot be made.
- `event_settings_merger`: Main function to copy the label, concentration and ignored flag entered for each event onto the experiment, and to move ignored events out of the working event list.
- `everything_asker`: Main function to ask every question of the run in numbered sections (files, trimming and ignoring, analysis, plots, summary figures, export) and to build the per-file information.
- `experiment_processor`: Main function to read, process, plot and export one .paf file. Each step reports its own problem so the next step still runs.
- `last_answers_loader`: Main function to read the answers remembered from the last run.
- `last_answers_saver`: Main function to remember the answers of this run for the next one.
- `main`: Main function of the program: ask the questions, process every file, then draw the comparison and special figures, logging the output to a file.
- `special_figures_maker`: Main function to draw the time response, haem and OCR response and 2x2 grid figures; each is skipped, with the reason, if it cannot be made.

## config.py

- `haem_colour_mapper`: Main function to give each haem a plot colour: the original colour for the usual haems, otherwise the next unused extra colour.

## utils_shared/attenuation.py

- `attenuation_converter`: Main function to convert transmission spectra to attenuation (log10 of the transmittance).
- `experiment_attenuation_adder`: Main function to add an attenuation array to the spectral datasets of an experiment.

## utils_shared/averaging.py

- `_baseline_change_adder`: Helper function to add the change from the baseline window to the statistics of a window.
- `experiment_averages_calculator`: Main function to calculate event-window statistics for VoO2 and haem data and store them in the experiment.
- `window_statistics_calculator`: Main function to calculate the mean and sample SD of every measurement column inside a time window.

## utils_shared/comparison_plotter.py

- `_overhang_calculator`: Helper function to measure how far the labels of a plot stick out to the left and right of its main axes.
- `_renderer_getter`: Helper function to get the renderer of a figure canvas.
- `comparison_figure_plotter`: Main function to draw two experiments side by side with their own y axes, panel letters a and b and a gap sized to their labels, and save it as svg and png.

## utils_shared/figure_layout.py

- `_free_top_finder`: Helper function to find the highest edge of anything a panel draws within a horizontal range.
- `_renderer_getter`: Helper function to get the renderer of a figure canvas.
- `figure_canvas_fitter`: Main function to set the figure margins so that everything drawn sits a fixed padding inside the figure edge, whatever the figure size, font size or label lengths.
- `figure_size_calculator`: Main function to calculate the (width, height) of a figure in inches from a journal specification.
- `figure_style_builder`: Main function to derive every font size, padding and line width of the figures from the journal specification and three master settings.
- `figure_style_checker`: Main function to list warnings for fonts outside the journal range or a figure taller than the journal allows.
- `gap_space_calculator`: Main function to calculate the GridSpec wspace or hspace that leaves a given gap between equal cells.
- `panel_letter_adder`: Main function to write each panel letter at the top-left corner of everything its panel draws.
- `text_extent_calculator`: Main function to calculate the width and height of the bounding box of a piece of text after rotating it.

## utils_shared/helpers.py

- `concentration_formatter`: Main function to write a concentration given in micromolar with the most readable unit: M from 1 000 000 uM, mM from 1000 uM and uM below that.
- `excel_sheet_namer`: Main function to make a valid, unique Excel sheet name (at most 31 characters, no special characters).
- `figure_saver`: Main function to save a figure in each requested format at exactly the requested size. The size is pinned again just before saving because interactive backends resize figures, and tight cropping is off unless requested.
- `file_name_sanitiser`: Main function to replace the characters that are illegal in file names.
- `name_simplifier`: Main function to simplify a name for matching by lower-casing it and removing everything except letters and digits, so "Cyt $c_1$" equals "cyt c1".

## utils_shared/individual_experiment_exporter.py

- `_spectral_csv_exporter`: Helper function to write one CSV per spectral dataset and data type, with wavelengths down and one column per spectrum.
- `averages_table_builder`: Main function to build the Averages worksheet table: one row per window with the mean, SD and change from baseline of VoO2 and of each haem.
- `experiment_workbook_exporter`: Main function to export one experiment to <output_dir>/<name>/<name>.xlsx, with the CcO2, CsO2 and VoO2 sheets, Averages, Events and Metadata, and optionally every processed table and the spectral CSV files.
- `saved_settings_reader`: Main function to read the OD, volume, dilution factor and events saved in the workbook of an earlier export.
- `workbook_path_builder`: Main function to build the path of the workbook of an experiment.

## utils_shared/individual_experiment_plotter.py

- `_axes_legend_drawer`: Helper function to draw a legend with an optional thin box.
- `_first_series_getter`: Helper function to get the time and values of the first measurement column of a DataFrame.
- `_haem_data_selector`: Helper function to pick the haem data frame the haem panels plot.
- `_height_ratio_calculator`: Helper function to calculate the relative panel heights from PANEL_HEIGHT_RATIOS.
- `_min_ticks_setter`: Helper function to make sure an axis has at least a given number of ticks, still at round values.
- `_panel_builder`: Helper function to list the panels to draw: oxygen, VO2, then one for each configured haem panel with matching data.
- `_window_drawer`: Helper function to draw the averaging windows behind the data on every axis.
- `_window_label_builder`: Helper function to build the text of an averaging window from AVERAGING_WINDOW_LABEL_FORMAT.
- `_ylim_calculator`: Helper function to calculate y limits from the data after the ignored start and before the ignored end, plus a margin.
- `experiment_drawer`: Main function to draw one experiment's stacked panels into a cell of an existing figure. It adds no title, adjusts no margins and saves nothing; event labels hang below the lowest axis, so room is needed underneath the cell.
- `experiment_plotter`: Main function to plot one experiment in its own figure, optionally save it as svg and png, then show or close it.
- `experiment_title_builder`: Main function to build the title of an experiment from the FIGURE_TITLE format.
- `watermark_style_builder`: Main function to build the text keyword arguments of the faint run-name watermark.

## utils_shared/normalisation.py

- `_frame_normaliser`: Helper function to OD-normalise the measurement columns of a data frame, leaving the time and index columns untouched.
- `data_normaliser`: Main function to divide numeric data by dilution factor x optical density x volume.
- `experiment_normaliser`: Main function to OD-normalise VoO2 and, when present, the haem data of an experiment.
- `percent_converter`: Main function to scale one table of an experiment to 0-100 % and store it under a new key.
- `percent_scaler`: Main function to scale each measurement column of a data frame to a relative 0-100 % range.

## utils_shared/paf_reader.py

- `dataset_namer`: Main function to turn a spectrometer name in the file into the dataset name used by the rest of the program.
- `experiment_end_trimmer`: Main function to discard everything recorded after a given time.
- `experiment_paf_loader`: Main function to build the experiment dictionary straight from a .paf file.
- `experiment_summary_reader`: Main function to take a quick look at a .paf file without reading its spectra.
- `record_scanner`: Main function to split the whole file into records and parse the spectra records.
- `rtf_converter`: Main function to convert the rich text of a PaneNote record to plain text.
- `spectra_parser`: Main function to parse one 'Spectra: CCD' record: frame count, wavelength axis, log10 data block, acquisition parameters and trailer strings.
- `stream_extractor`: Main function to extract every trace (DataItem followed by Measurement record) as a float32 array.
- `token_reader`: Main function to find the length-prefixed UTF-16LE strings inside a byte range of the file.
- `u32_reader`: Main function to read one little-endian unsigned 32-bit integer from a buffer.
- `warning_printer`: Main function to print a reader warning, unless it is one of the harmless messages in QUIET_WARNINGS.

## utils_shared/questions.py

- `_input_reader`: Helper function to show the answer prompt and read what the user types.
- `_number_builder`: Helper function to advance the counters and build the next question number.
- `_question_printer`: Helper function to print the numbered, coloured question line.
- `choice_asker`: Main function to ask a question answered by choosing one numbered option.
- `colour_checker`: Main function to say whether the terminal can show colour; it also switches on colour codes in the Windows console the first time.
- `heading_printer`: Main function to print a plain heading, for example the summary.
- `info_printer`: Main function to print an information line (not a question), indented to sit under the question above.
- `input_flusher`: Main function to throw away keys pressed while the program was busy, so a stray Enter cannot answer a question.
- `multi_asker`: Main function to ask a question answered by choosing several numbered options.
- `number_asker`: Main function to ask a question answered with a number, asking again until the value is valid.
- `numbering_restarter`: Main function to make the next question at a depth (and deeper) start again from 1.
- `numbering_setter`: Main function to set the current number at a depth, for example so the next sub-questions are numbered 3.4.3.1.
- `numbers_asker`: Main function to ask a question answered by numbers from 1 to a count, separated by commas.
- `path_cleaner`: Main function to clean a path typed or dragged into the window by removing surrounding quotes and spaces.
- `progress_clearer`: Main function to remove the progress line from the terminal.
- `progress_printer`: Main function to show a one-line progress message that the next message overwrites.
- `section_starter`: Main function to start the next numbered section and print its heading.
- `text_asker`: Main function to ask a question answered with a line of text.
- `text_colourer`: Main function to wrap text in a colour code when colour is available.
- `text_italiser`: Main function to write text in italics when the terminal supports it.
- `yes_no_asker`: Main function to ask a yes/no question.

## utils_shared/run_logging.py

- `logging_starter`: Main function to start copying everything printed to a timestamped log file.
- `logging_stopper`: Main function to restore the console streams and close the log file.

## utils_shared/schema.py

- `finite_float_converter`: Main function to convert a value to a finite float, or NaN when that is not possible.
- `measurement_column_finder`: Main function to list the measurement columns of an experiment DataFrame.
- `source_resolver`: Main function to look up a dataset of an experiment by its source name from the settings.
- `time_getter`: Main function to read the time column of an experiment DataFrame.
- `value_getter`: Main function to read one measurement column as a float array.

## utils_shared/spectral_decomposer.py

- `_wavelength_masker`: Helper function to select the wavelengths inside the range shared by all fits.
- `data_filterer`: Main function to restrict experimental data to the wavelength range shared by all fits.
- `delta_abs_calculator`: Main function to shift each haem absorbance so that its reference level is 0, giving a change in absorbance (mOD).
- `experiment_decomposer`: Main function to decompose every spectrum of one dataset into haem concentrations and absorbances.
- `fit_importer`: Main function to import a haem spectral fit CSV.
- `s_array_generator`: Main function to generate the haem and scatter basis components for one spectrum.
- `spectrum_decomposer`: Main function to decompose one experimental spectrum into haem contributions and scatter.

## utils_shared/survey.py

- `_columns_text_builder`: Helper function to write a figure width in columns, e.g. '1 column' or '1.5 columns'.
- `_event_line_builder`: Helper function to write one event as 'label, time' for the event listings.
- `_limits_asker`: Helper function to ask one yes/no question and then one number per file (trim or ignore, start or end), offering the values remembered from the last run.
- `_natural_sorter`: Helper function to build a sort key that puts numbers in numerical order, so 'control_7hours' comes before 'control_24hours'.
- `analysis_asker`: Main function to ask section 3: haem decomposition, OD scaling, event averaging and the event labels.
- `averaging_asker`: Main function to ask whether to average around the events, and the window settings.
- `decomposition_asker`: Main function to ask whether to decompose the spectra into haems and which fit to use.
- `event_asker`: Main function to ask whether to change the event labels, concentrations and which events to ignore, file by file.
- `files_asker`: Main function to ask for the folder of .paf files (1.1) and the results folder (1.2), and to read a summary of every file.
- `haem_form_option_builder`: Helper function to build the (key, label) choices for the 'how to show the haems' questions. The delta A line explains itself in italics.
- `haem_name_formatter`: Main function to write a haem name for the terminal: the $...$ maths markers are removed, subscripts become subscript characters where they exist, and the maths part is shown in italics, e.g. 'Cyt $b_H$' becomes 'Cyt bₕ'.
- `multi_experiment_asker`: Main function to ask section 5: the side-by-side figure of two experiments and the 2x2 figure of four experiments.
- `ocr_option_builder`: Helper function to build the (key, label) choices for the OCR questions, using the units of the plot axes.
- `od_asker`: Main function to ask the OD, volume and dilution factor of every file, offering the values saved in each experiment's workbook.
- `paf_finder`: Helper function to list the .paf files directly inside a folder, by name.
- `plot_asker`: Main function to ask section 4: what the individual experiment figures show and how they are sized.
- `size_asker`: Main function to ask the journal, width and height of one figure. Answering None to the journal question uses Nature with the fallback width and height.
- `trim_asker`: Main function to ask section 2: which data is trimmed away (start, end) and which is ignored in the calculations (start, end), per file.

## utils_shared/trimming.py

- `experiment_trimmer`: Main function to keep only the part of an experiment between a start and an end time. After a start trim the time axis is re-zeroed so the chosen start becomes 0, and events keep their original datapoint numbers.

## utils_custom/custom_config.py

- `exemplar_config_builder`: Main function to build the settings of the four-run exemplar figure.
- `haem_labeller`: Main function to give a haem its short y-axis label, for example '$b_H$'.
- `individual_config_builder`: Main function to build the individual-experiment plot settings used inside the custom figures: oxygen, OCR and one panel per chosen haem.
- `publication_config_builder`: Main function to build the settings of the haem and OCR publication figure.
- `source_selector`: Main function to choose the OCR and haem data sources of the haem and OCR response figures from the answers.
- `time_response_config_builder`: Main function to build the settings of the time response figure.

## utils_custom/custom_questions.py

- `_haem_ocr_asker`: Helper function to ask the settings of the haem and OCR response figure (6.2.x).
- `_time_response_asker`: Helper function to ask the settings of the time response figure (6.1.x).
- `_window_ensurer`: Helper function to make sure the event-window settings exist for the special figures: they reuse the section 3 settings, which are asked here if event averaging was switched off there.
- `summary_figure_asker`: Main function to ask section 6: whether to plot a time response and a haem and OCR response, and the settings of each one chosen. Both need the haem fit, which is asked for here if it was not chosen in section 3.

## utils_custom/custom_runner.py

- `_haem_ocr_preparer`: Helper function to calculate the event-window averages used by the haem and OCR response figures, on a copy of one experiment.
- `_time_response_preparer`: Helper function to average the spectra in the event windows, subtract the last two windows and decompose the difference spectrum, on a copy of one experiment.
- `exemplar_runner`: Main function to draw the 2x2 figure: one experiment for each strain and addition order, plotted like the individual experiment figures.
- `experiment_preparer`: Main function to prepare one processed experiment for the special figures. Each figure is prepared on its own, so a problem with one does not stop the other.
- `haem_ocr_runner`: Main function to combine the runs of each condition and draw the haem and OCR response: the publication figure and the four-run exemplar figure. The two figures are drawn independently, so a problem with one does not stop the other.
- `time_response_runner`: Main function to export and draw the time response figure from the prepared experiments.

## utils_custom/publication_plotter.py

- `_axes_styler`: Helper function to apply the tick, grid and spine style of the response and baseline panels.
- `_baseline_bar_plotter`: Helper function to draw the baseline OCR (average0) bar chart per group, with every run overlaid and a Student t-test bracket between the two groups.
- `_block_gap_calculator`: Helper function to calculate the gap between the blocks and between the response columns of the publication figure.
- `_column_chooser`: Helper function to choose the OCR column: the preferred one if set, else VoO2, else the first available.
- `_condition_indexer`: Helper function to map each (strain, order) pair to its condition name in the triplicate results.
- `_crop_start_finder`: Helper function to find the time at which an exemplar crop begins.
- `_exemplar_gap_calculator`: Helper function to calculate the gap between rows and between columns of the exemplar quadrants.
- `_exemplar_plotter`: Helper function to draw one experiment exactly as the individual plotter does.
- `_exemplar_selector`: Helper function to pick the experiment of one run number for every (strain, order) cell.
- `_experiment_classifier`: Helper function to identify the strain, addition order and run number from an experiment name.
- `_experiment_cropper`: Helper function to copy an experiment cropped to begin at a chosen time, with time measured from there.
- `_figure_finisher`: Helper function to fit the margins to the drawn content, add the panel letters at the top-left of each panel and fit again.
- `_haem_block_plotter`: Helper function to draw the haem response: one row per haem, one column per addition order, a line per group.
- `_haem_label_finder`: Helper function to find the shared y label of the haem response rows.
- `_haem_label_pad_calculator`: Helper function to calculate the points between the shared haem label and the haem axes.
- `_haem_row_selector`: Helper function to select the haem response rows to draw, in the order listed in HAEM_RESPONSE_SHOW.
- `_haem_source_finder`: Helper function to find the haem source that every condition's averages were calculated from.
- `_layout_validator`: Helper function to check that the layout options of the publication figure are recognised and to return the group and order lists.
- `_legend_handle_builder`: Helper function to build legend entries showing each group's colour, line style and marker.
- `_mean_ylim_setter`: Helper function to set the y range of a response panel from the group means (and the baseline level) only, so that a single outlier run or a very large error bar does not stretch the axis. Points and error bars beyond the range are clipped.
- `_measurement_finder`: Helper function to find the column matching a wanted name, ignoring case and punctuation.
- `_metric_field_selector`: Helper function to name the keys of the triplicate statistics used by a response metric.
- `_ocr_block_plotter`: Helper function to draw the OCR response (percent of each run's baseline, mean and SEM across runs), one axes per addition order.
- `_p_value_adjuster`: Helper function to adjust a list of p values for multiple comparisons.
- `_reference_level_finder`: Helper function to find the height of the dashed reference line of the haem response.
- `_reference_selector`: Helper function to pick, for each addition order, the first run of the first available group (used for the event tick labels).
- `_response_axes_preparer`: Helper function to draw the baseline reference line and set the window ticks of a response panel.
- `_response_metric_checker`: Helper function to reject a percent-of-baseline response for the delta abs sources, which start at 0.
- `_response_series_drawer`: Helper function to plot every run as a point, the mean as a line and SEM error bars for one group.
- `_response_window_tester`: Helper function to run a Student t-test between the two groups at every window of a response panel and mark the significant windows.
- `_row_ylim_sharer`: Helper function to give every axes in a row the union of their y ranges.
- `_significance_bar_drawer`: Helper function to draw a bracket between two x positions with text centred above it.
- `_significance_formatter`: Helper function to format a p value as stars or as text.
- `_test_bar_drawer`: Helper function to draw a small bracket joining the two groups' points at one window with text above it.
- `_tick_label_builder`: Helper function to build the x tick labels of the averaging windows: Baseline, then the addition that precedes each window.
- `_window_orderer`: Helper function to list the averaging windows present in any condition of one addition order.
- `exemplar_figure_plotter`: Main function to build the exemplar figure: one run per condition, each drawn by the individual plotter in its own quadrant.
- `publication_figure_plotter`: Main function to build the publication figure: baseline OCR, OCR response and haem response blocks.
- `publication_figure_saver`: Main function to save a publication or exemplar figure at its exact size, plus the t-test table when there is one.

## utils_custom/run_namer.py

- `_group_matcher`: Helper function to find the first group word that appears in an experiment name.
- `_natural_sorter`: Helper function to build a sort key that orders numbers inside names numerically.
- `condition_classifier`: Main function to identify the strain and the addition order from a condition name.
- `condition_grouper`: Main function to group experiments by condition and run number.
- `group_assigner`: Main function to give every experiment a group from its name and to order the experiments by group and then by hours.
- `hours_parser`: Main function to read the number of hours from an experiment name.
- `run_name_lister`: Main function to describe how each experiment name is read by the haem and OCR response figures, for showing to the user before they choose.
- `run_name_parser`: Main function to split an experiment name of the form <condition>_run<N> into its condition and run number.

## utils_custom/spectral_difference.py

- `difference_spectrum_calculator`: Main function to subtract one averaged spectrum from another.
- `difference_spectrum_decomposer`: Main function to decompose the difference spectrum into haem contributions using the shared decomposition.
- `spectral_averager`: Main function to average the chosen spectra in each event window.
- `window_definer`: Helper function to lay out the averaging windows of one run.

## utils_custom/time_response_exporter.py

- `time_response_exporter`: Main function to write the haem percentages and difference spectra of each group as CSV files.

## utils_custom/time_response_plotter.py

- `_event_label_height_calculator`: Helper function to calculate the height the rotated event labels above the example time courses need.
- `_example_finder`: Helper function to find the experiment of one group at a given number of hours.
- `_example_viewer`: Helper function to copy an experiment so that its individual figure shows only the two windows its difference spectrum came from.
- `_legend_drawer`: Helper function to draw a legend in the journal style: small text and an optional thin box.
- `_time_axes_styler`: Helper function to apply the tick direction, label size and spine style.
- `_time_gap_calculator`: Helper function to calculate the row and column gaps of the time response figure from the font sizes and the figure size.
- `_title_styler`: Helper function to set a panel title in the figure style.
- `decomposition_plotter`: Main function to draw a difference spectrum with its scatter-free fit, residual and each haem contribution.
- `group_collector`: Main function to collect the decomposed experiments of each group, with their time labels.
- `shared_baseline_subtracter`: Main function to subtract one shared polynomial baseline, fitted to the mean spectrum, from every spectrum.
- `time_label_builder`: Main function to build the label of a time point from the experiment name.
- `time_response_figure_plotter`: Main function to build the time response figure: waterfalls, then two examples (time course and decomposition).
- `time_response_figure_saver`: Main function to save the time response figure at its exact size.
- `waterfall_plotter`: Main function to draw the offset difference spectra of one group, first time point at the top, with additive peak alignment.

## utils_custom/triplicate_averager.py

- `_run_summariser`: Helper function to summarise the finite values of one window across runs.
- `_window_sorter`: Helper function to sort averaging window names numerically.
- `triplicate_averager`: Main function to combine the per-experiment event averages across the runs of each condition.

## utils_custom/triplicate_exporter.py

- `triplicate_exporter`: Main function to write one worksheet per condition of the across-run statistics to an Excel workbook.
