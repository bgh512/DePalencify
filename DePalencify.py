# -*- coding: utf-8 -*-
"""
DePalencify: read .paf files, process them and export figures and data.

Start it with run.bat (Windows), run.command (Mac, double-click) or run.sh (Linux/Mac terminal). It asks a few questions, then for every .paf file in the chosen folder it
    reads the file directly (no export from the original software needed),
    optionally trims it, decomposes the spectra into haems with a fit, scales by OD, and averages around the additions,
    draws one figure per experiment (svg + png, sized for the chosen journal),
    and writes an Excel workbook per experiment (CcO2, CsO2, VoO2, events, metadata; optionally everything).
What you type for each experiment (OD, volume, dilution factor, event labels and concentrations) is saved in that experiment's
workbook (sheets "Metadata" and "Events") and offered again the next time.
"""
# %% IMPORTS -----------------------------------------------------------------------------------------------------------------------------------------
import gc
import json
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")                      # figures are saved to files; no window is needed
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import config as settings
from utils_shared.attenuation import add_attenuation_to_experiment
from utils_shared.averaging import calculate_experiment_averages
from utils_shared.individual_experiment_exporter import export_individual_experiment, read_saved_settings
from utils_shared.individual_experiment_plotter import plot_experiment
from utils_shared.normalisation import normalise_experiment, convert_to_percent
from utils_shared.comparison_plotter import plot_comparison
from utils_shared.figure_layout import figure_size_inches
from utils_shared.paf_reader import PafError, load_experiment_from_paf, read_experiment_summary
from utils_shared.trimming import trim_experiment
from utils_shared.questions import (UserQuit, ask_choice, ask_multi, ask_number, ask_text, ask_yes_no, clean_path, heading)
from utils_shared.run_logging import start_logging, stop_logging
from utils_shared.spectral_decomposer import import_fit, decompose_experiment

FITS_FOLDER = HERE / "fits"
LAST_ANSWERS_FILE = HERE / "last_answers.json"
JOURNAL_NAMES = {"nature": "Nature", "science": "Science", "cell": "Cell", "pnas": "PNAS"}
# %% QUESTIONS ---------------------------------------------------------------------------------------------------------------------------------------


def load_last_answers():
    try:
        return json.loads(LAST_ANSWERS_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_last_answers(values):
    try:
        LAST_ANSWERS_FILE.write_text(json.dumps(values, indent=2), encoding="utf-8")
    except OSError:
        pass                                   # a read-only folder just means the defaults are not remembered


def find_paf_files(folder):
    return sorted((p for p in Path(folder).iterdir() if p.is_file() and p.suffix.lower() == ".paf"), key=lambda p: p.name.lower())


def ask_files(last):
    """Ask for the folder of .paf files; returns (folder, [summary of each readable file])."""
    heading("1. Your files")
    while True:
        text = ask_text("Folder containing the .paf files", last.get("data_folder"))
        if not text:
            print("  Please type or drag in a folder.")
            continue
        folder = Path(clean_path(text)).expanduser()
        if not folder.is_dir():
            print("  That folder does not exist.")
            continue
        files = find_paf_files(folder)
        if not files:
            print("  There are no .paf files directly inside that folder.")
            continue
        break

    summaries = []
    for path in files:
        try:
            summary = read_experiment_summary(path)
        except PafError as exc:
            print(f"  Skipping {path.name}: {exc}")
            continue
        summary["path"] = path
        summaries.append(summary)
    if not summaries:
        raise SystemExit("None of the .paf files could be read.")
    print(f"\n  Found {len(summaries)} readable file(s):")
    for s in summaries:
        print(f"    {s['name']}: {s['duration_min']:.1f} min, {len(s['events'])} event(s)")
    return folder, summaries


def ask_trimming(summaries):
    """Returns {file name: {"start": minutes or None, "end": minutes or None}}. All times are on the original recording's clock."""
    trims = {s["name"]: {"start": None, "end": None} for s in summaries}
    if ask_yes_no("Do any of the files need trimming at the START (everything before a chosen time is discarded, and that time becomes 0)?", False):
        for s in summaries:
            first_event = min((e["time"] for e in s["events"]), default=s["duration_min"])
            value = ask_number(f"  Start time for {s['name']} in minutes (first event is at {first_event:.1f} min; Enter = keep it all)",
                               None, minimum=0, maximum=first_event, allow_blank=True)
            if value:
                trims[s["name"]]["start"] = value
    if ask_yes_no("Do any of the files need trimming at the END (everything after a chosen time is discarded)?", False):
        for s in summaries:
            last_event = max((e["time"] for e in s["events"]), default=0.0)
            start = trims[s["name"]]["start"] or 0.0
            value = ask_number(f"  End time for {s['name']} in minutes (recording is {s['duration_min']:.1f} min, last event at {last_event:.1f}; Enter = keep it all)",
                               None, minimum=max(last_event, start), allow_blank=True)
            if value is not None and value < s["duration_min"]:
                trims[s["name"]]["end"] = value
    return trims


def ask_decomposition(summaries, defaults):
    """Returns (decompose, fit_file, fit, dataset)."""
    fits = sorted(FITS_FOLDER.glob("*.csv"), key=lambda p: p.name.lower())
    if not fits:
        print(f"  No fit files (.csv) were found in {FITS_FOLDER}, so haems cannot be decomposed this time.")
        print("  Put a fit .csv in that folder and run again to get haem results.")
        return False, None, None, defaults["decomposition_dataset"]
    if not ask_yes_no("Decompose the spectra into haems?", defaults["decompose"]):
        return False, None, None, defaults["decomposition_dataset"]
    names = [p.name for p in fits]
    fit_file = ask_choice("Which fit?", [(n, n) for n in names], defaults.get("fit_file") if defaults.get("fit_file") in names else names[0])
    try:
        fit = import_fit(FITS_FOLDER / fit_file)
    except Exception as exc:
        print(f"  The fit file could not be read ({exc}); haems will not be decomposed.")
        return False, None, None, defaults["decomposition_dataset"]
    common = set(summaries[0]["datasets"])
    for s in summaries[1:]:
        common &= set(s["datasets"])
    if not common:
        print("  The files have no spectrometer in common, so haems cannot be decomposed.")
        return False, None, None, defaults["decomposition_dataset"]
    dataset = defaults["decomposition_dataset"]
    if dataset not in common:
        options = sorted(common)
        dataset = options[0] if len(options) == 1 else ask_choice("Which spectrometer holds the haem spectra?", [(o, o) for o in options], options[0])
    return True, fit_file, fit, dataset


def ask_experiment_details(summary, answers, export_root):
    """OD, volume, dilution factor and event labels for one file; offers the values saved in its workbook last time."""
    print(f"\n  {summary['name']}")
    saved = read_saved_settings(export_root, summary["name"]) or {}
    if saved:
        print("    (earlier values found in this experiment's workbook are offered as defaults)")
    details = {}
    if answers["normalise_od"]:
        details["OD"] = ask_number("    OD of the sample", saved.get("OD"), minimum=0, exclusive_minimum=True)
        details["volume"] = ask_number("    Volume (same units as always)", saved.get("volume"), minimum=0, exclusive_minimum=True)
        details["dilution_factor"] = ask_number("    Dilution factor", saved.get("dilution_factor", 1.0), minimum=0, exclusive_minimum=True)

    saved_events = {e["datapoint"]: e for e in saved.get("events", [])}
    events = []
    if summary["events"]:
        for number, event in enumerate(summary["events"], start=1):
            old = saved_events.get(event["datapoint"], {})
            events.append({"datapoint": event["datapoint"], "label": old.get("label") or event["text"],
                           "concentration_uM": old.get("concentration_uM")})
        print("    Events in the file:")
        for number, (event, entry) in enumerate(zip(summary["events"], events), start=1):
            conc = "" if entry["concentration_uM"] is None else f"{entry['concentration_uM']:g} uM "
            print(f"      {number}) {event['time']:.2f} min   {conc}{entry['label']}")
        if ask_yes_no("    Change any labels or concentrations?", False):
            for number, (event, entry) in enumerate(zip(summary["events"], events), start=1):
                entry["label"] = ask_text(f"      Event {number} ({event['time']:.2f} min) label", entry["label"]) or entry["label"]
                entry["concentration_uM"] = ask_number(f"      Event {number} concentration in uM (Enter = unknown)",
                                                       entry["concentration_uM"], minimum=0, allow_blank=True)
    details["events"] = events
    return details


def ask_everything():
    """Ask all the questions. Returns (answers, results folder, per-experiment info, fit, comparison pair or None)."""
    last = load_last_answers()
    defaults = dict(settings.DEFAULT_ANSWERS, **last.get("answers", {}))
    answers = dict(defaults)

    print("=" * 70)
    print("  DePalencify")
    print("  Press Enter to accept the value shown in [brackets].")
    print("=" * 70)

    folder, summaries = ask_files(last)
    heading("2. Where the results go")
    text = ask_text("Folder for the results", last.get("export_folder") if last.get("data_folder") == str(folder) else str(folder / "export"))
    export_root = Path(clean_path(text)).expanduser()

    heading("3. Trimming and settling time")
    print("  (Trim times are the times on the original recording, as the event times listed above are.)")
    trims = ask_trimming(summaries)
    answers["ignore_first_minutes"] = ask_number(
        "After trimming, how many minutes at the start should be ignored in calculations (while things settle)? These points are still\n"
        "plotted and exported, but are left out of baselines (delta A), % ranges and axis limits", defaults["ignore_first_minutes"], minimum=0)

    heading("4. Analysis")
    answers["decompose"], answers["fit_file"], fit, answers["decomposition_dataset"] = ask_decomposition(summaries, defaults)
    answers["normalise_od"] = ask_yes_no("Scale by OD (divide by dilution factor x OD x volume)?", defaults["normalise_od"])
    answers["averaging"] = ask_yes_no("Do event averaging (average a window before each addition)?", defaults["averaging"])
    if answers["averaging"]:
        answers["window_minutes"] = ask_number("  How long a window to average (minutes)", defaults["window_minutes"], minimum=0, exclusive_minimum=True)
        answers["gap_minutes"] = ask_number("  How long before the next addition should each window end (minutes)", defaults["gap_minutes"], minimum=0)

    heading("5. What to plot")
    answers["plot_o2"] = ask_yes_no("Plot the set and measured oxygen (CsO2 and CcO2)?", defaults["plot_o2"])
    answers["plot_ocr"] = ask_yes_no("Plot the oxygen consumption rate (OCR)?", defaults["plot_ocr"])
    if answers["plot_ocr"]:
        options = [("raw", "Raw OCR")]
        if answers["normalise_od"]:
            options.append(("od", "OCR per OD (OCR/OD)"))
        options.append(("percent", "OCR as a % of its range (lowest to highest)"))
        keys = [k for k, _ in options]
        answers["ocr_mode"] = ask_choice("  Which OCR?", options, defaults["ocr_mode"] if defaults["ocr_mode"] in keys else keys[0])
    answers["plot_haems"] = False
    if answers["decompose"]:
        answers["plot_haems"] = ask_yes_no("Plot the haems?", defaults["plot_haems"])
        if answers["plot_haems"]:
            names = list(fit["haem_list"])
            answers["haems"] = ask_multi("  Which haems?", names, default_all=True)
            answers["haem_mode"] = ask_choice("  Plot them as", [
                ("abs", "Absorbance (mOD)"), ("delta", "Delta A (change in absorbance from the start, mOD)"),
                ("conc", "Concentration"), ("percent", "% oxidised (lowest to highest = 0 to 100 %)")], defaults["haem_mode"])
            if answers["normalise_od"] and answers["haem_mode"] != "percent":
                answers["haem_per_od"] = ask_yes_no("  Divide the haem values by OD as well?", defaults["haem_per_od"])
    comparison = None
    if not (answers["plot_o2"] or answers["plot_ocr"] or answers["plot_haems"]):
        print("  Nothing is set to be plotted, so no figures will be made.")
    else:
        answers["event_label_angle"] = ask_number("Angle of the event labels in degrees (0 = horizontal, 90 = vertical)",
                                                  defaults["event_label_angle"], minimum=0, maximum=90)
        if len(summaries) >= 2 and ask_yes_no("Also plot a comparison of two runs side by side?", False):
            names = [(s["name"], s["name"]) for s in summaries]
            first = ask_choice("  Which run goes on the left?", names)
            second = ask_choice("  Which run goes on the right?", [n for n in names if n[0] != first])
            comparison = {"runs": (first, second)}

    heading("6. Figure size")
    answers["journal"] = ask_choice("Paper format (journal)", [(k, v) for k, v in JOURNAL_NAMES.items()], defaults["journal"])
    spec = settings.JOURNAL_SPECS[answers["journal"]]
    columns = [(c, f"{c:g} column{'s' if c != 1 else ''} wide ({mm} mm)") for c, mm in spec["widths_mm"].items()]
    answers["columns"] = ask_choice("Figure width", columns, defaults["columns"] if defaults["columns"] in spec["widths_mm"] else columns[0][0])
    answers["height"] = ask_number(f"Figure height as a fraction of the page height (0.5 = half a page = {0.5 * spec['page_height_mm']:g} mm)",
                                   defaults["height"], minimum=0, exclusive_minimum=True, maximum=1)
    if comparison:
        print("\n  The comparison figure has its own size:")
        wide = [(c, f"{c:g} column{'s' if c != 1 else ''} wide ({mm} mm)") for c, mm in spec["widths_mm"].items()]
        comparison["columns"] = answers["comparison_columns"] = ask_choice(
            "Comparison figure width", wide, defaults["comparison_columns"] if defaults["comparison_columns"] in spec["widths_mm"] else wide[-1][0])
        comparison["height"] = answers["comparison_height"] = ask_number(
            f"Comparison figure height as a fraction of the page height (0.5 = half a page = {0.5 * spec['page_height_mm']:g} mm)",
            defaults["comparison_height"], minimum=0, exclusive_minimum=True, maximum=1)

    heading("7. Data export")
    print("  Every experiment always gets a workbook with CcO2, CsO2, VoO2, the events and your OD/volume/dilution entries.")
    answers["export_full"] = ask_yes_no("Also put every processed table in it (OD-scaled, haems, percent, ...)?", defaults["export_full"])
    answers["export_spectra"] = ask_yes_no("Also export the spectra as csv files? (large, and it takes a while)", defaults["export_spectra"])

    heading("8. Details for each experiment")
    experiments = []
    for s in summaries:
        info = {"path": s["path"], "name": s["name"], "trim_start": trims[s["name"]]["start"], "trim_end": trims[s["name"]]["end"],
                "duration": s["duration_min"], "keep": bool(comparison) and s["name"] in comparison["runs"]}
        info.update(ask_experiment_details(s, answers, export_root))
        experiments.append(info)

    heading("Summary")
    print(f"  Files:            {len(experiments)} from {folder}")
    print(f"  Results to:       {export_root}")
    print(f"  Ignore first:     {answers['ignore_first_minutes']:g} min")
    trimmed = [f"{k} {('from %g ' % v['start']) if v['start'] else ''}{('to %g ' % v['end']) if v['end'] else ''}min" for k, v in trims.items() if v["start"] or v["end"]]
    print(f"  Trimmed:          {', '.join(trimmed) or 'none'}")
    print(f"  Decomposition:    {answers['fit_file'] if answers['decompose'] else 'no'}")
    print(f"  OD scaling:       {'yes' if answers['normalise_od'] else 'no'}")
    print(f"  Event averaging:  {'%g min window, ending %g min before the next addition' % (answers['window_minutes'], answers['gap_minutes']) if answers['averaging'] else 'no'}")
    shown = [name for name, on in (("O2", answers["plot_o2"]), (f"OCR ({answers['ocr_mode']})", answers["plot_ocr"]),
                                   (f"haems {', '.join(answers['haems'])} ({answers['haem_mode']})", answers["plot_haems"])) if on]
    print(f"  Plots:            {'; '.join(shown) or 'none'}")
    if comparison:
        print(f"  Comparison:       {comparison['runs'][0]} (a) vs {comparison['runs'][1]} (b), {comparison['columns']:g} column(s), height {comparison['height']:g} of a page")
    print(f"  Figure:           {JOURNAL_NAMES[answers['journal']]}, {answers['columns']:g} column(s), height {answers['height']:g} of a page")
    print(f"  Workbooks:        {'all processed data' if answers['export_full'] else 'CcO2, CsO2, VoO2'}{' + spectra csv' if answers['export_spectra'] else ''}")
    if not ask_yes_no("\nStart?", True):
        raise UserQuit()

    save_last_answers({"data_folder": str(folder), "export_folder": str(export_root),
                       "answers": {k: v for k, v in answers.items() if k != "haems" or v}})
    return answers, export_root, experiments, fit, comparison
# %% PROCESSING --------------------------------------------------------------------------------------------------------------------------------------


def merge_event_settings(experiment, events):
    """Copy the label and concentration entered for each event onto the experiment's events (matched by datapoint)."""
    entered = {e["datapoint"]: e for e in events}
    for event in experiment["metadata"].get("events", []):
        item = entered.get(event["datapoint"])
        if item:
            event["label"] = item["label"] or event["text"]
            event["concentration_uM"] = item["concentration_uM"]


def process_experiment(info, cfg, fit, export_root):
    """Read, process, plot and export one .paf. Each step reports its own problem and the next step still runs."""
    a = cfg.answers
    name = info["name"]
    print(f"\nProcessing: {name}")
    datasets = None if a["export_spectra"] else ((a["decomposition_dataset"],) if a["decompose"] else ())
    experiment = load_experiment_from_paf(info["path"], spectral_datasets=datasets, with_intensity=a["export_spectra"])
    metadata = experiment["metadata"]
    for key in ("OD", "volume", "dilution_factor"):
        if info.get(key) is not None:
            metadata[key] = info[key]
    merge_event_settings(experiment, info.get("events", []))
    print(f"  Read {len(experiment['CcO2'])} points, {len(metadata['events'])} event(s)")

    if info.get("trim_start") is not None or info.get("trim_end") is not None:
        trim_experiment(experiment, start_time=info.get("trim_start"), end_time=info.get("trim_end"))
        if info.get("trim_start") is not None:
            print(f"  Trimmed: data before {info['trim_start']:g} min discarded (that point is now time 0)")
        if info.get("trim_end") is not None:
            print(f"  Trimmed: data after {info['trim_end']:g} min discarded")

    od_available = False
    if a["normalise_od"]:
        od_available = all(metadata.get(k) for k in ("OD", "volume", "dilution_factor"))
        if not od_available:
            print("  Warning: OD, volume or dilution factor is missing, so this file is not scaled by OD (raw values are used instead).")

    # Attenuation and decomposition into haems.
    if a["decompose"]:
        try:
            add_attenuation_to_experiment(experiment, mode=settings.TRANSMISSION_MODE,
                                          datasets=None if a["export_spectra"] else (a["decomposition_dataset"],))
            print("  Decomposing ...")
            decompose_experiment(experiment, fit, dataset_name=a["decomposition_dataset"], spectrum_type="attenuation",
                                 degree_of_scatter=settings.DEGREE_OF_SCATTER, haemfactor=settings.HAEM_FACTOR,
                                 delta_exclude_first_minutes=a["ignore_first_minutes"],
                                 delta_window_seconds=settings.DELTA_ABS_WINDOW_SECONDS)
            reference = experiment["haem_delta_abs"].attrs["delta_abs_baseline"]
            print(f"  Decomposed with {a['fit_file']}; delta A reference: {reference['start_time']:.2f}-{reference['end_time']:.2f} min")
        except (KeyError, ValueError, PafError) as exc:
            print(f"  Decomposition skipped: {exc}")
    elif a["export_spectra"]:
        add_attenuation_to_experiment(experiment, mode=settings.TRANSMISSION_MODE)

    # OD scaling and relative (%) scaling.
    if od_available:
        try:
            normalise_experiment(experiment)
            print(f"  OD scaling: OD {metadata['OD']:g}, volume {metadata['volume']:g}, dilution factor {metadata['dilution_factor']:g}")
        except (KeyError, ValueError) as exc:
            od_available = False
            print(f"  OD scaling skipped: {exc}")
    percent_vo2, percent_haem = cfg.needs_percent()
    for needed, source_key, target_key in ((percent_haem, "haem_conc", "haem_percent"), (percent_vo2, "VoO2", "VoO2_percent")):
        if needed and source_key in experiment:
            try:
                convert_to_percent(experiment, source_key, target_key, exclude_first_minutes=a["ignore_first_minutes"],
                                   exclude_last_minutes=0.0, window_seconds=settings.PERCENT_AVERAGE_WINDOW_SECONDS)
            except (KeyError, ValueError, TypeError) as exc:
                print(f"  {target_key} skipped: {exc}")

    vo2_source, haem_source = cfg.sources(od_available)
    if haem_source is not None and not (a["plot_haems"] or a["averaging"]):
        haem_source = None

    # Event-window averages.
    if a["averaging"]:
        if not metadata["events"]:
            print("  Averaging skipped: this file has no events.")
        else:
            try:
                calculate_experiment_averages(experiment, window_minutes=a["window_minutes"], gap_minutes=a["gap_minutes"],
                                              final_window_gap_minutes=a["final_gap_minutes"], vo2_source=vo2_source,
                                              haem_source=haem_source if "haem_conc" in experiment else None)
                print(f"  Calculated {len(experiment['averages']['windows'])} event averages")
            except (KeyError, ValueError, TypeError) as exc:
                print(f"  Averaging skipped: {exc}")

    # Figure.
    haem_panels = a["plot_haems"] and "haem_conc" in experiment
    if a["plot_o2"] or a["plot_ocr"] or haem_panels:
        try:
            print("  Plotting ...")
            plot_experiment(experiment, cfg.plot_config(vo2_source, haem_source if haem_panels else None), export_root)
        except Exception as exc:                                   # a figure problem must not lose the data export
            print(f"  Figure not made: {type(exc).__name__}: {exc}")
            plt.close("all")

    # Workbook.
    metadata.update({"ignore_first_minutes": a["ignore_first_minutes"], "fit_file": a["fit_file"] if a["decompose"] else None,
                     "processed": datetime.now().strftime("%Y-%m-%d %H:%M")})
    print("  Exporting ...")
    export_individual_experiment(experiment, export_root, full=a["export_full"], spectra=a["export_spectra"])

    if info.get("keep"):                                            # needed again for the comparison figure
        experiment["raw_spectra"] = {}
        return {"experiment": experiment, "vo2_source": vo2_source, "haem_source": haem_source if haem_panels else None}
    return None
# %% MAIN --------------------------------------------------------------------------------------------------------------------------------------------


def make_comparison(comparison, kept, cfg, export_root):
    """The side-by-side figure of the two chosen runs (skipped, with the reason, if either one failed or they were plotted differently)."""
    names = comparison["runs"]
    first, second = (kept.get(name) for name in names)
    print(f"\nComparison: {names[0]} (a) vs {names[1]} (b)")
    if not (first and second):
        print("  Not made: one of the two runs did not finish.")
        return
    if (first["vo2_source"], first["haem_source"]) != (second["vo2_source"], second["haem_source"]):
        print("  Not made: the two runs were plotted with different data (for example only one has an OD entered).")
        return
    try:
        size = figure_size_inches(cfg.SPEC, comparison["columns"], comparison["height"])
        stem = plot_comparison(first["experiment"], second["experiment"], cfg.plot_config(first["vo2_source"], first["haem_source"]),
                               export_root, size, cfg.SPEC)
        print(f"  Saved comparison/{stem} ({size[0] * 25.4:.0f} x {size[1] * 25.4:.0f} mm)")
    except Exception as exc:
        print(f"  Not made: {type(exc).__name__}: {exc}")
        plt.close("all")


def main():
    try:
        answers, export_root, experiments, fit, comparison = ask_everything()
    except (UserQuit, KeyboardInterrupt):
        print("\nCancelled. Nothing was changed.")
        return 1

    cfg = settings.Config(answers)
    plt.rcParams.update(cfg.RC_PARAMS)
    start = time.perf_counter()
    log_session = start_logging(export_root)
    failed = []
    kept = {}
    try:
        for warning in cfg.STYLE_WARNINGS:
            print(f"Figure style warning: {warning}")
        for info in experiments:
            try:
                result = process_experiment(info, cfg, fit, export_root)
                if result:
                    kept[info["name"]] = result
            except KeyboardInterrupt:
                raise
            except Exception as exc:
                print(f"  FAILED: {info['name']}: {type(exc).__name__}: {exc}")
                print(traceback.format_exc())
                failed.append(info["name"])
            finally:
                plt.close("all")
                gc.collect()
        if comparison:
            make_comparison(comparison, kept, cfg, export_root)
        minutes, seconds = divmod(time.perf_counter() - start, 60)
        print(f"\nFinished {len(experiments) - len(failed)} of {len(experiments)} file(s) in {int(minutes)} min {seconds:.0f} s.")
        if failed:
            print("Not completed: " + ", ".join(failed) + " (details above and in the log file)")
        print(f"Results are in: {export_root}")
    except KeyboardInterrupt:
        print("\nStopped. Files finished so far are in: " + str(export_root))
    finally:
        stop_logging(log_session)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
