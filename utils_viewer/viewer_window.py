"""
The plot window of the experiment browser: one window that is redrawn after each answer.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import matplotlib.pyplot as plt
from matplotlib.figure import Figure


# ---- CONSTANTS -----------------------------------------------------------------------
WINDOW_TITLE = 'DePalencify preview'
PREVIEW_DPI = 200
# Interactive backends tried in order; the first one that starts is used.
BACKENDS_MAC = ('MacOSX', 'QtAgg', 'TkAgg')
BACKENDS_OTHER = ('QtAgg', 'TkAgg')


# ---- ViewerWindow --------------------------------------------------------------------
class ViewerWindow:
    """
    ---- Summary ----
    One plot window that shows the preview of the current step. When no plot window can
    be opened (no display, or no GUI library) the preview is saved to a picture file
    instead, which is opened in the default picture viewer.

    ---- Attributes ----
    preview_path : Path
        Picture file used when no plot window can be opened.
    is_window : bool
        True when previews appear in a plot window, False when they go to the file.
    backend_name : Optional[str]
        Name of the matplotlib backend of the plot window, None for the file.
    fig : Optional[Figure]
        The figure being redrawn, None before the first preview.

    ---- Globals read ----
    BACKENDS_MAC, BACKENDS_OTHER, PREVIEW_DPI, WINDOW_TITLE (module constants).

    ---- Methods ----
    __init__
    _backend_starter
    _file_opener
    figure_getter
    window_closer
    window_refresher
    """

    # ---- __init__ --------------------------------------------------------------------
    def __init__(self, preview_path: Path) -> None:
        """
        ---- Summary ----
        Method to set up the window object without opening anything yet.

        ---- Inputs ----
        preview_path : Path
            Picture file used when no plot window can be opened.

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
        self.is_window = False
        self.backend_name: Optional[str] = None
        self.fig: Optional[Figure] = None
        self._has_tried = False
        self._has_opened_file = False

    # ---- WINDOW HELPERS --------------------------------------------------------------

    # ---- _backend_starter ------------------------------------------------------------
    def _backend_starter(self) -> None:
        """
        ---- Summary ----
        Method to switch matplotlib to the first interactive backend that works, once.
        The program normally runs on the non-interactive Agg backend.

        ---- Inputs ----
        None.

        ---- Globals read ----
        BACKENDS_MAC, BACKENDS_OTHER (module constants).

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Switches the matplotlib backend and sets is_window and backend_name
        (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        if self._has_tried:
            return
        self._has_tried = True
        if sys.platform not in ('win32', 'darwin') and not (
                os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY')):
            return  # no display, so no window can open
        for name in (BACKENDS_MAC if sys.platform == 'darwin' else BACKENDS_OTHER):
            try:
                plt.switch_backend(name)
                self.fig = plt.figure(WINDOW_TITLE, dpi=PREVIEW_DPI)
            except Exception:  # missing GUI library, or no display: try the next one
                plt.close('all')
                continue
            self.is_window = True
            self.backend_name = name
            plt.ion()
            return
        plt.switch_backend('Agg')

    # ---- _file_opener ----------------------------------------------------------------
    def _file_opener(self) -> None:
        """
        ---- Summary ----
        Method to open the preview picture in the default picture viewer (once), so the
        preview can be seen without a plot window.

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

    # ---- figure_getter ---------------------------------------------------------------
    def figure_getter(self) -> Figure:
        """
        ---- Summary ----
        Method to give the figure to draw the next preview in. The plot window is opened
        on the first call and opened again if the user closed it.

        ---- Inputs ----
        None.

        ---- Globals read ----
        PREVIEW_DPI, WINDOW_TITLE (module constants).

        ---- Outputs ----
        Figure
            The figure; the caller clears and redraws it.

        ---- Globals mutated ----
        None. May open the plot window and prints a note when it falls back to a picture
        file (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _backend_starter
        """

        # ---- 1 Open the window the first time ----------------------------------------
        was_tried = self._has_tried
        self._backend_starter()
        if not was_tried and not self.is_window:
            print(f'No plot window can be opened here, so each preview is saved as a '
                  f'picture instead: {self.preview_path}',
                  )

        # ---- 2 Reopen a window the user closed ---------------------------------------
        is_closed = self.fig is None or not plt.fignum_exists(self.fig.number)
        if self.is_window and is_closed:
            self.fig = plt.figure(WINDOW_TITLE, dpi=PREVIEW_DPI)
        if not self.is_window and self.fig is None:
            self.fig = Figure(dpi=PREVIEW_DPI)
        return self.fig

    # ---- window_closer ---------------------------------------------------------------
    def window_closer(self) -> None:
        """
        ---- Summary ----
        Method to close the plot window and put matplotlib back on the Agg backend, so
        the rest of the run draws and saves figures as it always did.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Closes all figures and switches the matplotlib backend (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        plt.close('all')
        if self.is_window:
            plt.ioff()
            plt.switch_backend('Agg')
        self.is_window = False
        self.fig = None

    # ---- window_refresher ------------------------------------------------------------
    def window_refresher(self) -> None:
        """
        ---- Summary ----
        Method to show the figure that was just drawn: repaint the plot window, or save
        the picture file and tell the user where it is.

        ---- Inputs ----
        None.

        ---- Globals read ----
        PREVIEW_DPI (module constant).

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Repaints the window or writes the preview picture (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _file_opener
        """

        if self.is_window:
            self.fig.canvas.draw_idle()
            plt.pause(0.1)  # lets the window paint before the terminal waits for typing
            return
        self.fig.savefig(self.preview_path, dpi=PREVIEW_DPI)
        print(f'  Preview picture: {self.preview_path}')
        self._file_opener()
