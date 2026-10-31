"""
The background thread of the experiment browser window that draws the previews.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import io
import threading
from typing import Callable, List, Optional, Tuple

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_viewer.viewer_preview import (PREVIEW_DPI,
                                         PreviewSpec,
                                         preview_figure_builder,
                                         ViewerSession,
                                         )


# ---- PreviewRenderer -----------------------------------------------------------------
class PreviewRenderer(threading.Thread):
    """
    ---- Summary ----
    Thread that draws the preview of every file with the latest settings, the file being
    looked at first and then its neighbours, so the files can be flicked through while a
    question waits. A newer request makes it drop the work for the older one.

    ---- Attributes ----
    None public.

    ---- Globals read ----
    PREVIEW_DPI (imported constant).

    ---- Methods ----
    __init__
    _next_picker
    _picture_maker
    request_setter
    run
    stopper
    wanted_setter
    """

    # ---- __init__ --------------------------------------------------------------------
    def __init__(self,
                 session: ViewerSession,
                 deliver: Callable[[int, str, Optional[bytes], str], None],
                 ) -> None:
        """
        ---- Summary ----
        Method to set up the thread (it is started by the caller).

        ---- Inputs ----
        session : ViewerSession
            The browser session (files, cache).
        deliver : Callable[[int, str, Optional[bytes], str], None]
            Function called with (version, file name, PNG bytes or None, notes) for each
            finished preview. It is called from this thread.

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

        super().__init__(daemon=True, name='preview-renderer')
        self._session = session
        self._deliver = deliver
        self._names: List[str] = [s['name'] for s in session.summaries]
        self._condition = threading.Condition()
        self._spec: Optional[PreviewSpec] = None
        self._version = 0
        self._wanted = 0
        self._done: set = set()
        self._is_stopped = False

    # ---- RENDERER HELPERS ------------------------------------------------------------

    # ---- _next_picker ----------------------------------------------------------------
    def _next_picker(self) -> Optional[str]:
        """
        ---- Summary ----
        Method to pick the file to draw next: the nearest one to the file being looked
        at that has not been drawn with the current settings. The caller holds the lock.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        Optional[str]
            File name, or None when every file is drawn.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        total = len(self._names)
        remaining = [i for i in range(total) if self._names[i] not in self._done]
        if not remaining:
            return None
        # distance around the loop, forward first on a tie
        best = min(remaining,
                   key=lambda i: (min((i - self._wanted) % total,
                                      (self._wanted - i) % total,
                                      ),
                                  (i - self._wanted) % total,
                                  ),
                   )
        return self._names[best]

    # ---- _picture_maker --------------------------------------------------------------
    def _picture_maker(self,
                       spec: PreviewSpec,
                       name: str,
                       ) -> Tuple[Optional[bytes], str]:
        """
        ---- Summary ----
        Method to draw one file and turn the figure into a PNG picture.

        ---- Inputs ----
        spec : PreviewSpec
            The settings to draw with.
        name : str
            Name of the file.

        ---- Globals read ----
        PREVIEW_DPI (imported constant).

        ---- Outputs ----
        Tuple[Optional[bytes], str]
            (PNG bytes, notes); the bytes are None when the preview could not be drawn
            and the notes then say why.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        preview_figure_builder
        """

        try:
            figure, notes = preview_figure_builder(self._session, spec, name)
            if figure is None:
                return None, notes
            buffer = io.BytesIO()
            figure.savefig(buffer, format='png', dpi=PREVIEW_DPI)
            return buffer.getvalue(), notes
        except Exception as exc:  # a preview problem must never stop the questions
            return None, f'Preview not drawn for {name}: {type(exc).__name__}: {exc}'

    # ---- MAIN METHODS ----------------------------------------------------------------

    # ---- request_setter --------------------------------------------------------------
    def request_setter(self, spec: PreviewSpec, version: int, wanted: int) -> None:
        """
        ---- Summary ----
        Method to ask for every file to be drawn again with new settings.

        ---- Inputs ----
        spec : PreviewSpec
            The new settings.
        version : int
            Number of this request; results carry it so old ones can be dropped.
        wanted : int
            Index of the file being looked at, which is drawn first.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Replaces the work of the thread (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        with self._condition:
            self._spec = spec
            self._version = version
            self._wanted = wanted
            self._done = set()
            self._condition.notify_all()

    # ---- run -------------------------------------------------------------------------
    def run(self) -> None:
        """
        ---- Summary ----
        Method that draws previews until stopped. The name is fixed by the thread
        protocol.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Passes each finished preview to the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _next_picker
        _picture_maker
        """

        while True:
            with self._condition:
                while not self._is_stopped:
                    name = self._next_picker() if self._spec is not None else None
                    if name is not None:
                        break
                    self._condition.wait()
                if self._is_stopped:
                    return
                spec, version = self._spec, self._version
            picture, notes = self._picture_maker(spec, name)
            with self._condition:
                if version == self._version:
                    self._done.add(name)
            self._deliver(version, name, picture, notes)

    # ---- stopper ---------------------------------------------------------------------
    def stopper(self) -> None:
        """
        ---- Summary ----
        Method to stop the thread and wait until it has finished its current preview.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Stops the thread (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        with self._condition:
            self._is_stopped = True
            self._condition.notify_all()
        if self.is_alive() and threading.current_thread() is not self:
            self.join()

    # ---- wanted_setter ---------------------------------------------------------------
    def wanted_setter(self, wanted: int) -> None:
        """
        ---- Summary ----
        Method to say which file is being looked at, so it is drawn next.

        ---- Inputs ----
        wanted : int
            Index of the file.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the order of the work (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        with self._condition:
            self._wanted = wanted
            self._condition.notify_all()
