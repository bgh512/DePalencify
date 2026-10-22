# -*- coding: utf-8 -*-
"""Mirror console output to a timestamped log file for the duration of a run."""
import sys
from datetime import datetime
from pathlib import Path


class _Tee:
    """File-like object that writes to several streams."""

    def __init__(self, *streams):
        self.streams = streams

    def write(self, text):
        for stream in self.streams:
            stream.write(text)
            stream.flush()
        return len(text)

    def flush(self):
        for stream in self.streams:
            stream.flush()

    def isatty(self):
        return self.streams[0].isatty()

    def __getattr__(self, name):
        return getattr(self.streams[0], name)


def start_logging(export_root):
    """Start copying stdout/stderr to ``<export_root>/logs/run_log_<timestamp>.txt``; returns a session dict."""
    export_root = Path(export_root)
    log_folder = export_root / "logs"
    log_folder.mkdir(parents=True, exist_ok=True)

    log_path = log_folder / f"run_log_{datetime.now():%Y%m%d_%H%M%S}.txt"
    log_file = log_path.open("w", encoding="utf-8", buffering=1)

    session = {
        "log_path": log_path,
        "log_file": log_file,
        "original_stdout": sys.stdout,
        "original_stderr": sys.stderr,
        "closed": False,
    }
    session["tee_stdout"] = _Tee(sys.stdout, log_file)
    session["tee_stderr"] = _Tee(sys.stderr, log_file)
    sys.stdout, sys.stderr = session["tee_stdout"], session["tee_stderr"]

    print(f"Logging output to: {log_path.relative_to(export_root)}")
    return session


def stop_logging(session):
    """Restore the console streams and close the log file."""
    if session is None or session["closed"]:
        return
    try:
        session["tee_stdout"].flush()
        session["tee_stderr"].flush()
    finally:
        # Only restore streams we installed ourselves.
        if sys.stdout is session["tee_stdout"]:
            sys.stdout = session["original_stdout"]
        if sys.stderr is session["tee_stderr"]:
            sys.stderr = session["original_stderr"]
        try:
            session["log_file"].flush()
        finally:
            session["log_file"].close()
            session["closed"] = True
