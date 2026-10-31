"""
Per-thread capture of printed output, so one thread can print without the text reaching
the terminal or the log file.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import io
import threading
from contextlib import contextmanager
from typing import Iterator, Optional


# ---- CONSTANTS -----------------------------------------------------------------------
_local = threading.local()


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- captured_buffer_getter ----------------------------------------------------------
def captured_buffer_getter() -> Optional[io.StringIO]:
    """
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
    """

    return getattr(_local, 'buffer', None)


# ---- output_capturer -----------------------------------------------------------------
@contextmanager
def output_capturer() -> Iterator[io.StringIO]:
    """
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
    """

    previous = getattr(_local, 'buffer', None)
    buffer = io.StringIO()
    _local.buffer = buffer
    try:
        yield buffer
    finally:
        _local.buffer = previous
