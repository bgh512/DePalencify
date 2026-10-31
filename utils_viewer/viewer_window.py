"""
The fallback preview of the experiment browser: one picture file that is rewritten after
each answer, for computers where the browser window cannot open.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import io
import os
import subprocess
import sys
from contextlib import contextmanager, redirect_stdout
from pathlib import Path
from typing import Any, Iterator

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
from matplotlib.figure import Figure


# ---- CONSTANTS -----------------------------------------------------------------------
PREVIEW_DPI = 200


# ---- PictureWindow -------------------------------------------------------------------
class PictureWindow:
    """
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
    """

    # ---- __init__ --------------------------------------------------------------------
    def __init__(self, preview_path: Path) -> None:
        """
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
        """

        self.preview_path = Path(preview_path)
        self.is_interactive = False
        self._has_opened_file = False

    # ---- WINDOW HELPERS --------------------------------------------------------------

    # ---- _file_opener ----------------------------------------------------------------
    def _file_opener(self) -> None:
        """
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
        """

        if self._has_opened_file:
            return
        self._has_opened_file = True
        try:
            if sys.platform == 'win32':
                os.startfile(str(self.preview_path))  # type: ignore[attr-defined]
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', str(self.preview_path)])
            else:
                subprocess.Popen(['xdg-open', str(self.preview_path)],
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL,
                                 )
        except (OSError, AttributeError):
            pass  # the path is printed, so the picture can still be opened by hand

    # ---- MAIN METHODS ----------------------------------------------------------------

    # ---- figure_shower ---------------------------------------------------------------
    def figure_shower(self, figure: Figure) -> None:
        """
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
        """

        figure.savefig(self.preview_path, dpi=PREVIEW_DPI)
        print(f'  Preview picture: {self.preview_path}')
        self._file_opener()

    # ---- file_focuser ----------------------------------------------------------------
    def file_focuser(self, name: str) -> None:
        """
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
        """

    # ---- output_capturer -------------------------------------------------------------
    @contextmanager
    def output_capturer(self) -> Iterator[io.StringIO]:
        """
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
        """

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            yield buffer

    # ---- session_attacher ------------------------------------------------------------
    def session_attacher(self, session: Any) -> None:
        """
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
        """

    # ---- window_closer ---------------------------------------------------------------
    def window_closer(self) -> None:
        """
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
        """
