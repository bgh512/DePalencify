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
from utils_shared.questions import UserQuit, ask_yes_no, heading, section_starter
from utils_shared.survey import (analysis_asker, files_asker, multi_experiment_asker, plot_asker,
                                 trim_asker)
from utils_shared.run_logging import start_logging, stop_logging
from utils_custom.custom_questions import summary_figure_asker
from utils_custom.custom_runner import (exemplar_runner, experiment_preparer, haem_ocr_runner,
                                        time_response_runner)
from utils_shared.spectral_decomposer import decompose_experiment

FITS_FOLDER = HERE / "fits"
LAST_ANSWERS_FILE = HERE / "last_answers.json"
from utils_shared.survey import JOURNAL_NAMES
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


def ask_everything():
    """Ask all the questions. Returns (answers, results folder, per-experiment info, fit, comparison pair or None)."""
    last = load_last_answers()
    defaults = dict(settings.DEFAULT_ANSWERS, **last.get("answers", {}))
    answers = dict(defaults)
    remembered = last.get("files", {})

    print("=" * 70)
    print("  DePalencify  V2.0 beta")
    print("  Questions are in colour and numbered. Type your answer on the line below")
    print("  each question; Enter accepts the value shown in [brackets].")
    print("=" * 70)

    section_starter("Your files")
    folder, summaries, export_root = files_asker(last)
    names = [s["name"] for s in summaries]

    section_starter("Trimming and ignoring")
    limits = trim_asker(summaries, remembered)
    answers["ignore_first_minutes"] = max(v["ignore_start"] for v in limits.values())
    answers["ignore_last_minutes"] = max(v["ignore_end"] for v in limits.values())

    section_starter("Analysis")
    fit, details = analysis_asker(summaries, answers, defaults, FITS_FOLDER, export_root)

    section_starter("Individual experiment plots")
    plotted = plot_asker(answers, defaults, fit)

    section_starter("Multi-experiment plots")
    comparison, exemplar_names = multi_experiment_asker(summaries, answers, defaults, plotted)

    section_starter("Experiment summaries")
    fit, custom = summary_figure_asker(names, answers, defaults, summaries, fit, FITS_FOLDER)

    section_starter("Data export")
    print("  Every experiment always gets a workbook with CcO2, CsO2, VoO2, the events and your OD/volume/dilution entries.")
    answers["export_full"] = ask_yes_no("Do you want to put every processed table in the workbook (OD-scaled, haems, percent, ...)?", defaults["export_full"])
    answers["export_spectra"] = ask_yes_no("Do you want to export the spectra as csv files (large, and it takes a while)?", defaults["export_spectra"])

    experiments = []
    for s in summaries:
        name = s["name"]
        info = {"path": s["path"], "name": name, "duration": s["duration_min"],
                "trim_start": limits[name]["trim_start"], "trim_end": limits[name]["trim_end"],
                "ignore_start": limits[name]["ignore_start"], "ignore_end": limits[name]["ignore_end"],
                "custom": {"time_response_group": (custom["time_response"] or {}).get(name),
                           "haem_ocr": name in (custom["haem_ocr"] or [])},
                "exemplar": name in (exemplar_names or [])}
        info["keep"] = (bool(comparison) and name in comparison["runs"]) or info["exemplar"] \
            or bool(info["custom"]["time_response_group"]) or info["custom"]["haem_ocr"]
        info.update(details[name])
        experiments.append(info)

    section_starter("Summary")
    print(f"  Files:            {len(experiments)} from {folder}")
    print(f"  Results to:       {export_root}")
    spans = {}
    for name, v in limits.items():
        if v["trim_start"] or v["trim_end"]:
            spans.setdefault((v["trim_start"] or 0, v["trim_end"]), []).append(name)
    trimmed = [f"{('all files' if len(names) == len(limits) else ', '.join(names))}: "
               f"{'from %g ' % start if start else ''}{'to %g ' % end if end else ''}min"
               for (start, end), names in spans.items()]
    print(f"  Trimmed:          {', '.join(trimmed) or 'none'}")
    print(f"  Ignored:          first {answers['ignore_first_minutes']:g} min, last {answers['ignore_last_minutes']:g} min (largest over the files)")
    print(f"  Decomposition:    {answers['fit_file'] if answers['decompose'] else 'no'}")
    print(f"  OD scaling:       {'yes' if answers['normalise_od'] else 'no'}")
    print(f"  Event averaging:  {'%g min window, ending %g min before the next addition' % (answers['window_minutes'], answers['gap_minutes']) if answers['averaging'] else 'no'}")
    shown = [name for name, on in (("O2", answers["plot_o2"]), (f"OCR ({answers['ocr_mode']})", answers["plot_ocr"]),
                                   (f"haems {', '.join(answers['haems'])} ({answers['haem_mode']})", answers["plot_haems"])) if on]
    print(f"  Plots:            {'; '.join(shown) or 'none'}")
    print(f"  Individual:       {JOURNAL_NAMES[answers['journal']]}, {answers['columns']:g} column(s), height {answers['height']:g} of a page")
    if comparison:
        print(f"  Side by side:     {comparison['runs'][0]} (a) vs {comparison['runs'][1]} (b), {JOURNAL_NAMES[answers['comparison_journal']]}, {comparison['columns']:g} column(s), height {comparison['height']:g}")
    if exemplar_names:
        print(f"  2x2 grid:         run {answers['ho_exemplar_run']}, {JOURNAL_NAMES[answers['ex_journal']]}, {answers['ho_ex_columns']:g} column(s), height {answers['ho_ex_height']:g}")
    if answers["plot_time_response"]:
        print(f"  Time response:    groups {', '.join(answers['tr_groups'])}, {JOURNAL_NAMES[answers['tr_journal']]}, {answers['tr_columns']:g} column(s), height {answers['tr_height']:g}")
    if answers["plot_haem_ocr"]:
        print(f"  Haem and OCR:     {len(custom['haem_ocr'])} file(s), {JOURNAL_NAMES[answers['ho_journal']]}, {answers['ho_pub_columns']:g} column(s), height {answers['ho_pub_height']:g}")
    print(f"  Workbooks:        {'all processed data' if answers['export_full'] else 'CcO2, CsO2, VoO2'}{' + spectra csv' if answers['export_spectra'] else ''}")
    if not ask_yes_no("Do you want to start?", True):
        raise UserQuit()

    files = dict(remembered)
    files.update({name: dict(v) for name, v in limits.items()})
    save_last_answers({"data_folder": str(folder), "export_folder": str(export_root), "files": files,
                       "answers": {k: v for k, v in answers.items() if k not in ("haems", "ho_haems") or v}})
    return answers, export_root, experiments, fit, comparison, exemplar_names
# %% PROCESSING --------------------------------------------------------------------------------------------------------------------------------------


def merge_event_settings(experiment, events):
    """Copy the label and concentration entered for each event onto the experiment's events (matched by datapoint)."""
    entered = {e["datapoint"]: e for e in events}
    for event in experiment["metadata"].get("events", []):
        item = entered.get(event["datapoint"])
        if item:
            event["label"] = item["label"] or event["text"]
            event["concentration_uM"] = item["concentration_uM"]
            event["ignored"] = bool(item.get("ignored", False))
    # Ignored events leave the working list (so nothing plots or averages them) but are
    # kept in metadata["ignored_events"] so the workbook still records them.
    metadata = experiment["metadata"]
    events = metadata.get("events", [])
    metadata["ignored_events"] = [e for e in events if e.get("ignored")]
    metadata["events"] = [e for e in events if not e.get("ignored")]


def process_experiment(info, cfg, fit, export_root):
    """Read, process, plot and export one .paf. Each step reports its own problem and the next step still runs."""
    a = cfg.answers
    name = info["name"]
    ignore_first, ignore_last = info["ignore_start"], info["ignore_end"]
    print(f"\nProcessing: {name}")
    datasets = None if a["export_spectra"] else ((a["decomposition_dataset"],) if a["decompose"] else ())
    experiment = load_experiment_from_paf(info["path"], spectral_datasets=datasets, with_intensity=a["export_spectra"])
    metadata = experiment["metadata"]
    for key in ("OD", "volume", "dilution_factor"):
        if info.get(key) is not None:
            metadata[key] = info[key]
    merge_event_settings(experiment, info.get("events", []))
    skipped = len(metadata.get("ignored_events", []))
    print(f"  Read {len(experiment['CcO2'])} points, {len(metadata['events'])} event(s)"
          + (f" ({skipped} ignored)" if skipped else ""))

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
                                 delta_exclude_first_minutes=ignore_first,
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
                convert_to_percent(experiment, source_key, target_key, exclude_first_minutes=ignore_first,
                                   exclude_last_minutes=ignore_last, window_seconds=settings.PERCENT_AVERAGE_WINDOW_SECONDS)
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
            plot_experiment(experiment, cfg.plot_config(vo2_source, haem_source if haem_panels else None,
                                                        ignore_first, ignore_last), export_root)
        except Exception as exc:                                   # a figure problem must not lose the data export
            print(f"  Figure not made: {type(exc).__name__}: {exc}")
            plt.close("all")

    # Workbook.
    metadata.update({"ignore_first_minutes": ignore_first, "ignore_last_minutes": ignore_last, "fit_file": a["fit_file"] if a["decompose"] else None,
                     "processed": datetime.now().strftime("%Y-%m-%d %H:%M")})
    print("  Exporting ...")
    export_individual_experiment(experiment, export_root, full=a["export_full"], spectra=a["export_spectra"])

    prepared = experiment_preparer(experiment, info["custom"], a, fit, od_available)     # the special figures

    if info.get("keep"):                                            # needed again for the comparison and special figures
        experiment["raw_spectra"] = {}
        for item in prepared.values():
            if item is not None:
                item["raw_spectra"] = {}
        return {"experiment": experiment, "vo2_source": vo2_source, "haem_source": haem_source if haem_panels else None,
                "prepared": prepared}
    return None
# %% MAIN --------------------------------------------------------------------------------------------------------------------------------------------


def make_comparison(comparison, kept, cfg, export_root):
    cfg = settings.Config(dict(cfg.answers, journal=cfg.answers["comparison_journal"]))
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


def make_special_figures(kept, cfg, fit, export_root, exemplar_names):
    """The time response, haem and OCR response and 2x2 figures (each skipped, with the reason, if it cannot be made)."""
    a = cfg.answers
    journals = {"time_response": "tr_journal", "haem_ocr": "ho_journal"}
    for key, enabled, title, runner in (("time_response", a["plot_time_response"], "Time response", time_response_runner),
                                        ("haem_ocr", a["plot_haem_ocr"], "Haem and OCR response", haem_ocr_runner)):
        if not enabled:
            continue
        print(f"\n{title}")
        prepared = {name: item["prepared"][key] for name, item in kept.items() if item["prepared"].get(key) is not None}
        if len(prepared) < 2:
            print(f"  Not made: only {len(prepared)} file(s) could be prepared (at least two are needed).")
            continue
        try:
            figure_cfg = settings.Config(dict(a, journal=a[journals[key]]))
            runner(prepared, figure_cfg, a, fit, export_root)
        except Exception as exc:                               # one special figure must not stop the others
            print(f"  Not made: {type(exc).__name__}: {exc}")
            print(traceback.format_exc())
            plt.close("all")
    if a["plot_exemplar"]:
        print("\n2x2 figure")
        chosen = {name: kept[name] for name in (exemplar_names or []) if name in kept}
        if len(chosen) < 4:
            print(f"  Not made: only {len(chosen)} of the four experiments finished.")
            return
        try:
            exemplar_runner(chosen, settings.Config(dict(a, journal=a["ex_journal"])), a, fit, export_root)
        except Exception as exc:
            print(f"  Not made: {type(exc).__name__}: {exc}")
            print(traceback.format_exc())
            plt.close("all")


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")      # symbols such as the delta never stop the program
        except (AttributeError, ValueError):
            pass
    try:
        answers, export_root, experiments, fit, comparison, exemplar_names = ask_everything()
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
        make_special_figures(kept, cfg, fit, export_root, exemplar_names)
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
