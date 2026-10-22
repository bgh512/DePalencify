# -*- coding: utf-8 -*-
"""Read an Espana Scientific Software .paf file directly (no bins/txt exports needed).

The decoded layout (see the notes at the bottom of this file) was checked against the software's own exports: intensity files are
byte-identical, transmission agrees to 1 ulp, and the .txt traces are identical.
"""
# %% IMPORTS -----------------------------------------------------------------------------------------------------------------------------------------
import bisect
import mmap
import re
import struct
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from utils_shared.schema import TIME_COLUMN

MARK = b"\x06Espana\x00\x00\x00\x00\x00"


class PafError(Exception):
    """The file is not a .paf, is truncated, or has a layout this reader does not know."""


def warn(msg):
    print("  WARNING: " + msg)
# %% LOW-LEVEL RECORD PARSING ------------------------------------------------------------------------------------------------------------------------


def u32(buf, off):
    return struct.unpack_from("<I", buf, off)[0]


def read_tokens(buf, start, end):
    """Length-prefixed UTF-16LE strings inside [start, end): 02 00 00 00 <n> <chars>."""
    out = []
    p = start
    pat = b"\x02\x00\x00\x00"
    while True:
        p = buf.find(pat, p, end - 8)
        if p < 0:
            break
        n = u32(buf, p + 4)
        if 1 <= n <= 4096 and p + 8 + 2 * n <= end:   # empty strings are skipped (they only produced false hits)
            try:
                s = bytes(buf[p + 8:p + 8 + 2 * n]).decode("utf-16-le")
            except UnicodeDecodeError:
                s = None
            if s is not None and all(c >= " " or c in "\r\n\t" for c in s):
                out.append((s, p, p + 8 + 2 * n))
                p += 8 + 2 * n
                continue
        p += 1
    return out


def rtf_to_text(rtf):
    s = rtf.decode("cp1252", errors="replace")
    skip_dest = {"fonttbl", "colortbl", "stylesheet", "info", "generator", "pict"}
    out, stack, ignore, i = [], [], False, 0
    while i < len(s):
        c = s[i]
        if c == "{":
            stack.append(ignore)
            i += 1
        elif c == "}":
            ignore = stack.pop() if stack else False
            i += 1
        elif c == "\\":
            i += 1
            if i >= len(s):
                break
            c = s[i]
            if c in "\\{}":
                if not ignore:
                    out.append(c)
                i += 1
            elif c == "'":
                if not ignore:
                    out.append(bytes([int(s[i + 1:i + 3], 16)]).decode("cp1252", "replace"))
                i += 3
            elif c == "*":
                ignore = True
                i += 1
            else:
                m = re.match(r"([a-zA-Z]+)(-?\d+)? ?", s[i:])
                if not m:
                    i += 1
                    continue
                word, arg = m.group(1), m.group(2)
                i += m.end()
                if word in skip_dest:
                    ignore = True
                elif word in ("par", "line") and not ignore:
                    out.append("\n")
                elif word == "tab" and not ignore:
                    out.append("\t")
                elif word == "u" and arg is not None and not ignore:
                    out.append(chr(int(arg) % 65536))
                    if i < len(s):
                        i += 1          # the fallback character
        else:
            if not ignore and c not in "\r\n":
                out.append(c)
            i += 1
    text = "".join(out)
    return "\n".join(l.rstrip() for l in text.split("\n")).strip("\n") + "\n"


class Spectra:
    pass


def parse_spectra(mm, off, markers):
    """Parse one 'Spectra: CCD' record starting at marker offset `off`."""
    sp = Spectra()
    sp.offset = off
    limit = min(len(mm), off + 4096)
    tok = read_tokens(mm, off + 40, limit)
    if len(tok) < 3:
        raise PafError("spectra record at %d: header strings not found" % off)
    sp.name = tok[2][0]
    idx_pat = struct.pack("<4I", 1, 2, 3, 4)
    p = mm.find(idx_pat, tok[2][2], limit)
    if p < 0:
        raise PafError("spectra record at %d: frame index table not found" % off)
    sp.nframes, sp.npix = u32(mm, p - 12), u32(mm, p - 8)
    if not (0 < sp.nframes < 10**7 and 0 < sp.npix < 10**5):
        raise PafError("spectra record at %d: implausible size %d x %d" % (off, sp.nframes, sp.npix))
    index = np.frombuffer(mm, dtype="<u4", count=sp.nframes, offset=p)
    if not np.array_equal(index, np.arange(1, sp.nframes + 1, dtype="<u4")):
        raise PafError("spectra record at %d: frame index table is not 1..N" % off)
    e = p + 4 * sp.nframes
    # wavelength axis: npix strictly increasing float32, a few dozen bytes after the index table
    sp.wl_off = None
    for o in range(e, min(e + 512, len(mm) - 4 * sp.npix)):
        a = struct.unpack_from("<3f", mm, o)
        if not (150 < a[0] < 2500 and a[0] < a[1] < a[2] < a[0] + 5):
            continue
        w = np.frombuffer(mm, dtype="<f4", count=sp.npix, offset=o)
        if 150 < w[-1] < 3000 and np.all(np.diff(w) > 0):
            sp.wl_off = o
            break
    if sp.wl_off is None:
        raise PafError("spectra record at %d: wavelength axis not found" % off)
    sp.wavelengths = np.frombuffer(mm, dtype="<f4", count=sp.npix, offset=sp.wl_off)
    sp.data_off = sp.wl_off + 4 * sp.npix
    nrows = sp.nframes + 2
    sp.data_end = sp.data_off + 4 * sp.npix * nrows
    if sp.data_end > len(mm):
        raise PafError("spectra record at %d: file is truncated (needs %d bytes, has %d)"
                       % (off, sp.data_end, len(mm)))
    sp.log = np.frombuffer(mm, dtype="<f4", count=sp.npix * nrows, offset=sp.data_off).reshape(nrows, sp.npix)
    k = bisect.bisect_left(markers, sp.data_end)
    sp.rec_end = markers[k] if k < len(markers) else len(mm)
    if sp.rec_end - sp.data_end > 4096:
        warn("spectra '%s': %d unexpected bytes after the data block" % (sp.name, sp.rec_end - sp.data_end))
    # acquisition parameters (layout verified on one file only)
    gap = bytes(mm[e:sp.wl_off])
    sp.params = {}
    if len(gap) == 56:
        sp.params = {
            "centre_wavelength_nm": round(struct.unpack_from("<f", gap, 24)[0], 3),
            "slit_um": struct.unpack_from("<f", gap, 32)[0],
            "unidentified_value": struct.unpack_from("<f", gap, 40)[0],
        }
    sp.trailer = [t[0] for t in read_tokens(mm, sp.data_end, sp.rec_end)]
    sp.checks = {}
    if np.any(sp.log[0] != 0):
        sp.checks["row0_not_zero"] = True
    sp.ref = sp.log[1].astype("f8")
    return sp


def scan(mm):
    markers = [m.start() for m in re.finditer(re.escape(MARK), mm)]
    if not markers or markers[0] > 64:
        raise PafError("this does not look like a .paf file (no 'Espana' record header near the start)")
    recs, spectra, skip_until = [], [], 0
    all_markers = markers
    for i, off in enumerate(all_markers):
        if off < skip_until:
            continue                       # marker-like bytes inside a spectra block
        tok = read_tokens(mm, off + 40, min(off + 1200, len(mm)))
        typ = tok[0][0] if tok else None
        if typ == "Spectra: CCD":
            sp = parse_spectra(mm, off, all_markers)
            spectra.append(sp)
            skip_until = sp.data_end
            recs.append(dict(off=off, end=sp.rec_end, type=typ, tokens=tok[:3]))
            continue
        k = bisect.bisect_right(all_markers, off)
        end = all_markers[k] if k < len(all_markers) else len(mm)
        recs.append(dict(off=off, end=end, type=typ, tokens=tok))
    # tokens were scanned over up to 1200 bytes: cut to the real record
    for r in recs:
        r["tokens"] = [t for t in r["tokens"] if t[2] <= r["end"]]
    return recs, spectra


def extract_streams(mm, recs):
    streams = []
    for a, b in zip(recs, recs[1:]):
        if a["type"] != "DataItem" or b["type"] != "Measurement":
            continue
        if len(a["tokens"]) < 3:
            continue
        name = a["tokens"][2][0]
        n1, n2 = u32(mm, a["end"] - 28), u32(mm, a["end"] - 20)
        if n1 != n2:
            warn("stream %s: DataItem counts disagree (%d vs %d), skipped" % (name, n1, n2))
            continue
        if n1 == 0:
            continue
        arr_off = b["end"] - 8 - 4 * n1
        hdr_tokens = read_tokens(mm, b["off"] + 40, arr_off)
        if arr_off < b["off"] + 60 or not hdr_tokens:
            warn("stream %s: array does not fit in its record, skipped" % name)
            continue
        if bytes(mm[b["end"] - 8:b["end"]]) != b"\x02\x00\x00\x00\x00\x00\x00\x00":
            warn("stream %s: unexpected record trailer" % name)
        vals = np.frombuffer(mm, dtype="<f4", count=n1, offset=arr_off)
        strs = [t[0] for t in hdr_tokens]
        streams.append(dict(name=name, n=n1, offset=arr_off, values=vals,
                            quantity=strs[2] if len(strs) > 2 else "",
                            unit=strs[4] if len(strs) > 4 else ""))
    return streams


# %% HIGH-LEVEL ACCESS -------------------------------------------------------------------------------------------------------------------------------
DATASET_ALIAS = {"Cytochromes": "Cyt"}   # spectrometer name in the file -> dataset name used by the rest of the program
LN10 = float(np.log(10.0))


def dataset_name(spectra_name):
    return DATASET_ALIAS.get(spectra_name, re.sub(r"\W+", "_", spectra_name))


class PafFile:
    """
    An open .paf file (memory-mapped, so a 100 MB file is not read into RAM). Use ``with PafFile(path) as paf:``.

    Everything handed out by the methods below is a copy, so it stays valid after the file is closed.
    """

    def __init__(self, path):
        self.path = Path(path)
        self._fh = open(self.path, "rb")
        self._mm = None
        try:
            if self.path.stat().st_size < 1024:
                raise PafError(f"{self.path.name}: file is too small to be a .paf")
            self._mm = mmap.mmap(self._fh.fileno(), 0, access=mmap.ACCESS_READ)
            self.records, self.spectra = scan(self._mm)
            self._streams = extract_streams(self._mm, self.records)
            times = [s for s in self._streams if s["name"] == "Time"]
            if not times:
                raise PafError(f"{self.path.name}: no Time stream found")
            main = max(times, key=lambda s: s["n"])
            self.time_s = np.array(main["values"], dtype=float)
            self._main = {}
            for s in self._streams:
                if s is not main and s["n"] >= 0.9 * len(self.time_s) and s["name"] not in self._main:
                    self._main[s["name"]] = s
        except PafError:
            self.close()
            raise
        except Exception as exc:                      # unexpected layout: report it as a file problem, not a crash
            self.close()
            raise PafError(f"{self.path.name}: could not be read ({type(exc).__name__}: {exc})")

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def close(self):
        self.records, self.spectra, self._streams, self._main = [], [], [], {}
        try:
            if self._mm is not None:
                self._mm.close()
        except BufferError:
            pass                                      # a view is still alive; it is released when it is garbage collected
        self._mm = None
        if not self._fh.closed:
            self._fh.close()

    # ---- simple facts
    @property
    def n_frames(self):
        return len(self.time_s)

    @property
    def duration_min(self):
        return float(np.nanmax(self.time_s)) / 60.0

    def stream_names(self):
        return list(self._main)

    def stream(self, name):
        """A trace as float64 on the time base (NaN where the software has no value, e.g. the start of VoO2)."""
        s = self._main.get(name)
        if s is None:
            return None
        out = np.full(len(self.time_s), np.nan)
        n = min(len(out), s["n"])
        out[:n] = np.asarray(s["values"][:n], dtype=float)
        return out

    def notes(self):
        for r in self.records:
            if r["type"] == "PaneNote":
                m = self._mm.find(b"{\\rtf1", r["off"], r["end"])
                if m >= 0:
                    return rtf_to_text(bytes(self._mm[m:r["end"]]).rstrip(b"\x00 \r\n"))
        return ""

    def events(self):
        """Text events as ``[{"name", "text", "datapoint"}]``; ``datapoint`` is the spectrum number stored with the event."""
        groups = {}
        for r in self.records:
            if r["type"] != "Text Event" or len(r["tokens"]) < 4:
                continue
            name, text = r["tokens"][2], r["tokens"][3]
            vpos = name[2] + 20
            value = u32(self._mm, vpos) if vpos + 4 <= text[1] else 0
            g = groups.setdefault(name[0], {"name": name[0], "text": text[0], "values": []})
            g["values"].append(value)
        events = []
        for g in groups.values():
            nonzero = sorted({v for v in g["values"] if v})
            if not nonzero:
                warn(f"event {g['name']!r} has no stored position and is ignored")
                continue
            if len(nonzero) > 1:
                warn(f"event {g['name']!r} has several stored positions {nonzero}; the first is used")
            events.append({"name": g["name"], "text": g["text"], "datapoint": int(nonzero[0])})
        return sorted(events, key=lambda e: e["datapoint"])

    def acquisition(self):
        return [{"dataset": dataset_name(sp.name), "spectrometer": sp.name, "frames": sp.nframes, "wavelengths": sp.npix,
                 "wavelength_range_nm": [round(float(sp.wavelengths[0]), 2), round(float(sp.wavelengths[-1]), 2)],
                 **sp.params, "other_fields": list(sp.trailer)} for sp in self.spectra]

    def dataset_names(self):
        return [dataset_name(sp.name) for sp in self.spectra]

    def spectra_dataset(self, name, with_intensity=False, chunk=128):
        """
        One spectrometer as the dictionary the rest of the program uses
        (wavelengths, spectrum_indices, time, transmission[, intensity]); float64 arrays copied out of the file.
        """
        sp = next((s for s in self.spectra if dataset_name(s.name) == name), None)
        if sp is None:
            raise PafError(f"{self.path.name}: no spectral dataset {name!r}; available: {', '.join(self.dataset_names()) or 'none'}")
        transmission = np.empty((sp.nframes, sp.npix))
        intensity = np.empty((sp.nframes, sp.npix)) if with_intensity else None
        ref = sp.log[1].astype("f8")
        for i0 in range(0, sp.nframes, chunk):
            i1 = min(sp.nframes, i0 + chunk)
            lg = sp.log[2 + i0:2 + i1].astype("f8")
            transmission[i0:i1] = np.exp((lg - ref[None, :]) * LN10)      # matches the software's export to 1 ulp
            if with_intensity:
                raw = 10.0 ** lg
                raw[~np.isfinite(raw)] = 0.0
                intensity[i0:i1] = np.round(raw)                           # identical to the software's integer counts
        times = self.time_s / 60.0 if len(self.time_s) == sp.nframes else np.full(sp.nframes, np.nan)
        if not np.all(np.isfinite(times)):
            warn(f"{name}: {sp.nframes} spectra but {len(self.time_s)} time points; spectrum times are unavailable")
        out = {"wavelengths": np.array(sp.wavelengths, dtype=float),
               "spectrum_indices": np.arange(1, sp.nframes + 1, dtype="<u4"),
               "time": times, "transmission": transmission}
        if with_intensity:
            out["intensity"] = intensity
        return out
# %% EXPERIMENT DICTIONARY ---------------------------------------------------------------------------------------------------------------------------
TRACE_COLUMNS = {"CsO2": "Set O2 (uM)", "CcO2": "Measured O2 (uM)", "VoO2": "VoO2"}


def read_experiment_summary(path):
    """Quick look at a file (no spectra read): duration, events, which spectrometers it holds."""
    with PafFile(path) as paf:
        times = paf.time_s / 60.0
        events = []
        for event in paf.events():
            row = event["datapoint"] - 1
            events.append(dict(event, time=float(times[row]) if 0 <= row < len(times) else np.nan))
        return {"name": Path(path).stem, "duration_min": paf.duration_min, "frames": paf.n_frames,
                "datasets": paf.dataset_names(), "events": events, "traces": paf.stream_names()}


def load_experiment_from_paf(path, spectral_datasets=("Cyt",), with_intensity=False):
    """
    Build the experiment dictionary (see utils_shared.schema) straight from a .paf

    spectral_datasets : which spectrometers to read (None = all, () = none). Spectra are the memory-heavy part, so
                        only read what is needed.
    """
    path = Path(path)
    with PafFile(path) as paf:
        time_min = paf.time_s / 60.0
        experiment = {"experiment_name": path.stem, "raw_spectra": {}}
        for key, column in TRACE_COLUMNS.items():
            values = paf.stream(key)
            if values is None:
                warn(f"{path.name}: no {key} trace in the file")
                continue
            frame = pd.DataFrame({TIME_COLUMN: time_min, column: values})
            if key == "VoO2":
                frame = frame.dropna(subset=[column]).reset_index(drop=True)   # the software's .txt export omits these rows
            experiment[key] = frame
        if "VoO2" not in experiment:
            raise PafError(f"{path.name}: no VoO2 trace in the file")

        wanted = paf.dataset_names() if spectral_datasets is None else list(spectral_datasets)
        for name in wanted:
            experiment["raw_spectra"][name] = paf.spectra_dataset(name, with_intensity=with_intensity)

        events = []
        for number, event in enumerate(paf.events(), start=1):
            row = event["datapoint"] - 1             # the stored number is the 1-based spectrum number (as in the original importer)
            if not 0 <= row < len(time_min):
                warn(f"{path.name}: {event['name']} points outside the recording and is ignored")
                continue
            events.append({"datapoint": event["datapoint"], "text": event["text"], "label": event["text"],
                           "concentration_uM": None, "time": float(time_min[row]), "row_index": row})
        experiment["metadata"] = {"paf_file": path.name, "events": sorted(events, key=lambda e: e["time"]),
                                  "acquisition": paf.acquisition(), "notes": paf.notes()}
    return experiment


def trim_experiment(experiment, end_time):
    """Discard everything recorded after ``end_time`` (minutes), e.g. noise from a run that was never stopped."""
    name = experiment["experiment_name"]
    late = [e for e in experiment["metadata"].get("events", []) if e["time"] > end_time]
    if late:
        raise ValueError(f"{name}: cannot trim at {end_time:g} min because {len(late)} event(s) occur later.")
    for key in ("CcO2", "CsO2", "VoO2"):
        frame = experiment.get(key)
        if frame is None:
            continue
        trimmed = frame.loc[frame[TIME_COLUMN].to_numpy(dtype=float) <= end_time].reset_index(drop=True)
        if trimmed.empty:
            raise ValueError(f"{name}: trimming {key} at {end_time:g} min leaves no data.")
        experiment[key] = trimmed
    for dataset_name_, dataset in experiment["raw_spectra"].items():
        if not np.all(np.isfinite(dataset["time"])):
            raise ValueError(f"{name}/{dataset_name_}: cannot trim because spectrum times are unavailable.")
        keep = dataset["time"] <= end_time
        for field in ("spectrum_indices", "time", "transmission", "intensity", "attenuation"):
            if field in dataset:
                dataset[field] = dataset[field][keep]
    experiment["metadata"]["trimmed_after_minutes"] = end_time
    return experiment
# %% FORMAT NOTES ------------------------------------------------------------------------------------------------------------------------------------
# * The file is a flat series of records, each starting 06 'Espana' 00 00 00 00 00 + a 16-byte class GUID. A header of
#   length-prefixed UTF-16 strings follows (02 00 00 00, nchars:u32, chars): type ('DataItem', 'Measurement', 'Spectra: CCD',
#   'Text Event', 'PaneNote', ...), vendor, name.
# * 'DataItem' + the 'Measurement' after it = one trace: the sample count n sits twice (at -28 and -20 from the DataItem's end);
#   the Measurement ends with n float32 values + 8 bytes. The Time trace is in seconds (0.5 s steps).
# * 'Spectra: CCD' = one spectrometer: nframes, npix, a 1..nframes index table, a parameter block, npix float32 wavelengths, then
#   (nframes + 2) rows of npix float32: zeros, log10(reference spectrum), then log10(counts) of every frame.
#   transmission = 10**(row - reference), intensity = round(10**row).
# * 'Text Event': the spectrum number (u32) of the event is stored 20 bytes after the end of its name string (zero in the
#   first, template copy of each event; the second copy holds the real value).
