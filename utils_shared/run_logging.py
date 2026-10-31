"""
Mirror console output to a timestamped log file for the duration of a run.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.output_capture import captured_buffer_getter


# ---- _Tee ----------------------------------------------------------------------------
class _Tee:
    """
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
    """

    # ---- __init__ --------------------------------------------------------------------
    def __init__(self, *streams: Any) -> None:
        """
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
        """

        self.streams = streams

    # ---- SPECIAL METHODS -------------------------------------------------------------

    # ---- __getattr__ -----------------------------------------------------------------
    def __getattr__(self, name: str) -> Any:
        """
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
        """

        return getattr(self.streams[0], name)

    # ---- MAIN METHODS ----------------------------------------------------------------

    # ---- flush -----------------------------------------------------------------------
    def flush(self) -> None:
        """
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
        """

        for stream in self.streams:
            stream.flush()

    # ---- isatty ----------------------------------------------------------------------
    def isatty(self) -> bool:
        """
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
        """

        return self.streams[0].isatty()

    # ---- write -----------------------------------------------------------------------
    def write(self, text: str) -> int:
        """
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
        """

        captured = captured_buffer_getter()
        if captured is not None:  # a thread that is capturing its output
            return captured.write(text)
        for stream in self.streams:
            stream.write(text)
            stream.flush()
        return len(text)


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- logging_starter -----------------------------------------------------------------
def logging_starter(export_root: Path, version: str, settings: dict) -> dict:
    """
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
    """

    # ---- 1 Prepare the log file ------------------------------------------------------
    export_root = Path(export_root)
    log_folder = export_root / 'logs'
    log_folder.mkdir(parents=True, exist_ok=True)
    log_path = log_folder / f'{datetime.now():%Y_%m_%d-%H_%M_%S}.log'
    log_file = log_path.open('w', encoding='utf-8', buffering=1)
    log_file.write(f'DePalencify V{version}\n')
    log_file.write('Random seed: none (the program does not use random numbers)\n')
    log_file.write('Settings:\n')
    for key, value in sorted(settings.items()):
        log_file.write(f'  {key}: {json.dumps(value, default=str)}\n')
    log_file.write('\n')
    session = {'log_path': log_path,
               'log_file': log_file,
               'original_stdout': sys.stdout,
               'original_stderr': sys.stderr,
               'closed': False,
               }

    # ---- 2 Redirect the output streams -----------------------------------------------
    session['tee_stdout'] = _Tee(sys.stdout, log_file)
    session['tee_stderr'] = _Tee(sys.stderr, log_file)
    sys.stdout, sys.stderr = session['tee_stdout'], session['tee_stderr']
    print(f'Logging output to: {log_path.relative_to(export_root)}')
    return session


# ---- logging_stopper -----------------------------------------------------------------
def logging_stopper(session: Optional[dict]) -> None:
    """
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
    """

    # ---- 1 Check the session ---------------------------------------------------------
    if session is None or session['closed']:
        return

    # ---- 2 Flush the files and restore the streams -----------------------------------
    try:
        session['tee_stdout'].flush()
        session['tee_stderr'].flush()
    finally:
        # Only restore streams we installed ourselves.
        if sys.stdout is session['tee_stdout']:
            sys.stdout = session['original_stdout']
        if sys.stderr is session['tee_stderr']:
            sys.stderr = session['original_stderr']
        try:
            session['log_file'].flush()
        finally:
            session['log_file'].close()
            session['closed'] = True
