"""
The experiment browser window: a text terminal on the left that asks the questions, and
the plots on the right with a file selector and arrows to flick through the files.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import base64
import builtins
import io
import os
import queue
import sys
import threading
import traceback
from contextlib import contextmanager
from typing import Any, Callable, Dict, Iterator, List, Optional

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
from PIL import Image

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.output_capture import output_capturer
from utils_viewer.viewer_preview import PreviewSpec, ViewerSession
from utils_viewer.viewer_renderer import PreviewRenderer
from utils_viewer.viewer_terminal import (ansi_splitter,
                                          ansi_style_updater,
                                          OutputRouter,
                                          )


# ---- CONSTANTS -----------------------------------------------------------------------
MONO_FONTS = ('Menlo', 'Consolas', 'DejaVu Sans Mono', 'Liberation Mono', 'Courier New')
TERMINAL_BACKGROUND = '#1e1e1e'
TERMINAL_TEXT = '#d4d4d4'
ANSWER_COLOUR = '#9cdcfe'
ERROR_COLOUR = '#ff7b86'
ENTRY_BACKGROUND = '#2b2b2b'
PLOT_BACKGROUND = '#f2f2f2'
_CLOSED = object()
_active_gui: Optional['ViewerGui'] = None


# ---- GuiUnavailable ------------------------------------------------------------------
class GuiUnavailable(Exception):
    """
    ---- Summary ----
    Raised when the browser window cannot be opened (no Tkinter, no display, or the
    window was switched off), so the program can use the terminal instead.

    ---- Attributes ----
    None.

    ---- Globals read ----
    None.

    ---- Methods ----
    None.
    """


# ---- ViewerGui -----------------------------------------------------------------------
class ViewerGui:
    """
    ---- Summary ----
    The experiment browser window. The program's questions run in their own thread and
    their text and answers pass through the terminal on the left, so the plot on the
    right stays usable while a question waits. Previews are drawn by a third thread.

    ---- Attributes ----
    is_interactive : bool
        Always True: the window has its own file controls.
    logic_thread : Optional[threading.Thread]
        The thread running the program, whose output belongs in the terminal.
    exit_code : int
        What the program returned (1 when it was stopped).

    ---- Globals read ----
    MONO_FONTS and the colour constants (module constants).

    ---- Methods ----
    __init__
    _answer_sender
    _closing_handler
    _drain_runner
    _event_handler
    _history_stepper
    _image_receiver
    _logic_runner
    _navigator
    _pane_writer
    _picture_shower
    _step_taker
    _widgets_builder
    file_focuser
    figure_shower
    input_reader
    output_capturer
    run
    session_attacher
    spec_publisher
    text_sender
    window_closer
    """

    is_interactive = True

    # ---- __init__ --------------------------------------------------------------------
    def __init__(self,
                 tk: Any,
                 root: Any,
                 program: Callable[[], int],
                 title: str,
                 ) -> None:
        """
        ---- Summary ----
        Method to build the window and set up the queues between its threads.

        ---- Inputs ----
        tk : Any
            The tkinter module.
        root : Any
            The Tk root window.
        program : Callable[[], int]
            The program to run; it asks the questions and returns its exit code.
        title : str
            Window title.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Sets the attributes on the instance and builds the widgets.

        ---- Equations ----
        None.

        ---- Helpers ----
        _widgets_builder
        """

        self._tk = tk
        self._root = root
        self._program = program
        self.logic_thread: Optional[threading.Thread] = None
        self.exit_code = 1
        self._events: 'queue.Queue' = queue.Queue()
        self._answers: 'queue.Queue' = queue.Queue()
        self._session: Optional[ViewerSession] = None
        self._renderer: Optional[PreviewRenderer] = None
        self._names: List[str] = []
        self._index = 0
        self._version = 0
        self._has_spec = False
        self._images: Dict[str, bytes] = {}
        self._previous: Dict[str, bytes] = {}
        self._notes: Dict[str, str] = {}
        self._failures: Dict[str, str] = {}
        self._photo: Any = None
        self._decoded: Any = None
        self._resize_job: Any = None
        self._is_waiting = False
        self._is_finished = False
        self._is_destroyed = False
        self._style: Dict[str, Any] = {'fg': None, 'bold': False, 'italic': False}
        self._is_carriage = False
        self._history: List[str] = []
        self._history_position = 0
        self._fonts: Dict[tuple, Any] = {}
        root.title(title)
        self._widgets_builder()

    # ---- WINDOW HELPERS --------------------------------------------------------------

    # ---- _widgets_builder ------------------------------------------------------------
    def _widgets_builder(self) -> None:
        """
        ---- Summary ----
        Method to build the terminal, the answer box, the plot and its file controls.

        ---- Inputs ----
        None.

        ---- Globals read ----
        MONO_FONTS and the colour constants (module constants).

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Creates the widgets (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        tk = self._tk
        from tkinter import font as tkfont, ttk
        root = self._root
        root.geometry('1500x860')
        root.minsize(900, 500)
        families = set(tkfont.families(root))
        self._family = next((f for f in MONO_FONTS if f in families), 'Courier')
        self._size = 11
        panes = ttk.PanedWindow(root, orient='horizontal')
        panes.pack(fill='both', expand=True)

        # ---- 1 The terminal on the left ----------------------------------------------
        left = tk.Frame(panes, bg=TERMINAL_BACKGROUND)
        self._text = tk.Text(left,
                             bg=TERMINAL_BACKGROUND,
                             fg=TERMINAL_TEXT,
                             insertbackground=TERMINAL_TEXT,
                             font=(self._family, self._size),
                             wrap='word',
                             state='disabled',
                             borderwidth=0,
                             highlightthickness=0,
                             padx=10,
                             pady=8,
                             width=70,
                             )
        scroll = ttk.Scrollbar(left, command=self._text.yview)
        self._text.configure(yscrollcommand=scroll.set)
        bottom = tk.Frame(left, bg=TERMINAL_BACKGROUND)
        self._hint = tk.Label(bottom,
                              text='Starting ...',
                              bg=TERMINAL_BACKGROUND,
                              fg='#808080',
                              anchor='w',
                              font=(self._family, 9),
                              )
        self._hint.pack(fill='x', padx=10)
        row = tk.Frame(bottom, bg=TERMINAL_BACKGROUND)
        tk.Label(row,
                 text='>',
                 bg=TERMINAL_BACKGROUND,
                 fg=ANSWER_COLOUR,
                 font=(self._family, self._size, 'bold'),
                 ).pack(side='left', padx=(10, 4))
        self._entry = tk.Entry(row,
                               bg=ENTRY_BACKGROUND,
                               fg=TERMINAL_TEXT,
                               insertbackground=TERMINAL_TEXT,
                               disabledbackground=TERMINAL_BACKGROUND,
                               disabledforeground='#606060',
                               font=(self._family, self._size),
                               relief='flat',
                               highlightthickness=1,
                               highlightbackground='#3c3c3c',
                               highlightcolor=ANSWER_COLOUR,
                               state='disabled',
                               )
        self._entry.pack(side='left', fill='x', expand=True, padx=(0, 10), ipady=5)
        row.pack(fill='x', pady=(2, 10))
        bottom.pack(side='bottom', fill='x')
        scroll.pack(side='right', fill='y')
        self._text.pack(side='left', fill='both', expand=True)
        panes.add(left, weight=1)
        self._entry.bind('<Return>', self._answer_sender)
        self._entry.bind('<Up>', lambda e: self._history_stepper(-1))
        self._entry.bind('<Down>', lambda e: self._history_stepper(1))

        # ---- 2 The plot on the right -------------------------------------------------
        right = tk.Frame(panes, bg=PLOT_BACKGROUND)
        controls = tk.Frame(right, bg=PLOT_BACKGROUND)
        controls.pack(side='bottom', pady=(4, 8))
        self._status = tk.Label(right,
                                text='',
                                bg=PLOT_BACKGROUND,
                                fg='#8a5a00',
                                wraplength=600,
                                justify='center',
                                )
        self._status.pack(side='bottom', fill='x')
        self._canvas = tk.Canvas(right,
                                 bg='white',
                                 highlightthickness=0,
                                 )
        self._canvas.pack(side='top', fill='both', expand=True, padx=8, pady=8)
        self._previous_button = ttk.Button(controls,
                                           text='< Prev',
                                           width=7,
                                           command=lambda: self._step_taker(-1),
                                           )
        self._combo = ttk.Combobox(controls, state='disabled', width=42)
        self._next_button = ttk.Button(controls,
                                       text='Next >',
                                       width=7,
                                       command=lambda: self._step_taker(1),
                                       )
        self._counter = tk.Label(controls, text='', bg=PLOT_BACKGROUND, width=9)
        self._previous_button.pack(side='left', padx=4)
        self._combo.pack(side='left', padx=4)
        self._next_button.pack(side='left', padx=4)
        self._counter.pack(side='left', padx=4)
        panes.add(right, weight=2)
        self._combo.bind('<<ComboboxSelected>>',
                         lambda e: self._navigator(self._combo.current(), True),
                         )
        self._canvas.bind('<Configure>', self._resizer)
        root.bind_all('<Prior>', lambda e: self._step_taker(-1))
        root.bind_all('<Next>', lambda e: self._step_taker(1))
        root.protocol('WM_DELETE_WINDOW', self._closing_handler)
        self._nav_state(False)
        self._message_shower('The plots appear here once the experiment browser '
                             'starts.')

    # ---- _nav_state ------------------------------------------------------------------
    def _nav_state(self, enabled: bool) -> None:
        """
        ---- Summary ----
        Method to switch the file selector and arrows on or off.

        ---- Inputs ----
        enabled : bool
            True to allow navigation.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the widget states (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        state = 'normal' if enabled else 'disabled'
        self._previous_button.configure(state=state)
        self._next_button.configure(state=state)
        self._combo.configure(state='readonly' if enabled else 'disabled')

    # ---- _message_shower -------------------------------------------------------------
    def _message_shower(self, text: str) -> None:
        """
        ---- Summary ----
        Method to replace the plot with a short message.

        ---- Inputs ----
        text : str
            Message to show.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Redraws the plot area (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self._canvas.delete('all')
        self._photo = None
        width = max(self._canvas.winfo_width(), 200)
        height = max(self._canvas.winfo_height(), 100)
        self._canvas.create_text(width // 2,
                                 height // 2,
                                 text=text,
                                 fill='#707070',
                                 width=int(width * 0.8),
                                 justify='center',
                                 font=(self._family, 12),
                                 )

    # ---- _resizer --------------------------------------------------------------------
    def _resizer(self, event: Any) -> None:
        """
        ---- Summary ----
        Method to redraw the picture at the new size once the window has stopped
        changing size.

        ---- Inputs ----
        event : Any
            The Tk configure event (unused).

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Schedules a redraw (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _picture_shower
        """

        if self._resize_job is not None:
            self._root.after_cancel(self._resize_job)
        self._resize_job = self._root.after(120, self._picture_shower)

    # ---- _picture_shower -------------------------------------------------------------
    def _picture_shower(self) -> None:
        """
        ---- Summary ----
        Method to show the picture of the current file, scaled to fit the plot area, or
        say why there is none yet.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Redraws the plot area and the status line (side effect).

        ---- Equations ----
        scale = min(width / picture width, height / picture height), at most 1.5.

        ---- Helpers ----
        _message_shower
        """

        self._resize_job = None
        if self._is_destroyed or not self._has_spec or not self._names:
            return
        name = self._names[self._index]
        png = self._images.get(name)
        failure = self._failures.get(name)
        is_stale = False
        if png is None and failure is None:
            png = self._previous.get(name)
            is_stale = png is not None
        if png is None:
            self._status.configure(text='')
            self._message_shower(failure or f'Drawing {name} ...')
            return
        key = (name, id(png))
        if self._decoded is None or self._decoded[0] != key:
            self._decoded = (key, Image.open(io.BytesIO(png)))
        picture = self._decoded[1]
        width = max(self._canvas.winfo_width() - 4, 50)
        height = max(self._canvas.winfo_height() - 4, 50)
        scale = min(width / picture.width, height / picture.height, 1.5)
        size = (max(int(picture.width * scale), 1), max(int(picture.height * scale), 1))
        resampling = getattr(Image, 'Resampling', Image)
        shown = picture.resize(size, resampling.LANCZOS)
        buffer = io.BytesIO()
        shown.save(buffer, format='PNG')
        self._photo = self._tk.PhotoImage(
            data=base64.b64encode(buffer.getvalue()).decode('ascii'),
        )
        self._canvas.delete('all')
        self._canvas.create_image(self._canvas.winfo_width() // 2,
                                  self._canvas.winfo_height() // 2,
                                  image=self._photo,
                                  )
        note = self._notes.get(name, '')
        if is_stale:
            note = 'Redrawing ... (this is the previous picture)'
        self._status.configure(text=note)

    # ---- _navigator ------------------------------------------------------------------
    def _navigator(self, index: int, is_from_user: bool = False) -> None:
        """
        ---- Summary ----
        Method to make a file the current one and show it.

        ---- Inputs ----
        index : int
            Position of the file in the list.
        is_from_user : bool
            True when the user chose it, so the answer box gets the keyboard back.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Updates the selector, the plot and the renderer's order (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _picture_shower
        """

        if not self._names:
            return
        self._index = index % len(self._names)
        self._combo.current(self._index)
        self._counter.configure(text=f'{self._index + 1} of {len(self._names)}')
        if self._session is not None:
            self._session.current = self._index
        if self._renderer is not None:
            self._renderer.wanted_setter(self._index)
        self._picture_shower()
        if is_from_user and self._is_waiting:
            self._entry.focus_set()

    # ---- _step_taker -----------------------------------------------------------------
    def _step_taker(self, step: int) -> None:
        """
        ---- Summary ----
        Method to move to the next or previous file, looping round at the ends.

        ---- Inputs ----
        step : int
            +1 for the next file, -1 for the previous one.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the current file (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        _navigator
        """

        if str(self._combo.cget('state')) == 'disabled':
            return
        self._navigator(self._index + step, True)

    # ---- _pane_writer ----------------------------------------------------------------
    def _pane_writer(self, text: str, kind: str = 'out') -> None:
        """
        ---- Summary ----
        Method to add text to the terminal, with its colours, overwriting the line when
        the text starts with a carriage return (progress messages).

        ---- Inputs ----
        text : str
            Text as printed.
        kind : str
            'out' (normal), 'err' (error text) or 'answer' (what the user typed).

        ---- Globals read ----
        ANSWER_COLOUR, ERROR_COLOUR (module constants).

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Adds text to the terminal and scrolls it (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        ansi_splitter
        ansi_style_updater
        """

        from tkinter import font as tkfont
        widget = self._text
        at_end = widget.yview()[1] > 0.98
        widget.configure(state='normal')
        for part_kind, value in ansi_splitter(text):
            if part_kind == 'code':
                self._style = ansi_style_updater(self._style, value)
                continue
            if part_kind == 'return':
                self._is_carriage = True
                continue
            if self._is_carriage:
                widget.delete('end-1c linestart', 'end-1c')
                self._is_carriage = False
            value = ''.join(c if ord(c) <= 0xFFFF else '?' for c in value)
            colour = {'err': ERROR_COLOUR, 'answer': ANSWER_COLOUR}.get(
                kind, self._style['fg'],
            )
            bold = self._style['bold'] or kind == 'answer'
            tag = f"{colour}|{bold}|{self._style['italic']}"
            if tag not in self._fonts:
                self._fonts[tag] = tkfont.Font(family=self._family,
                                               size=self._size,
                                               weight='bold' if bold else 'normal',
                                               slant=('italic'
                                                      if self._style['italic']
                                                      else 'roman'
                                                      ),
                                               )
                widget.tag_configure(tag,
                                     foreground=colour or TERMINAL_TEXT,
                                     font=self._fonts[tag],
                                     )
            widget.insert('end', value, tag)
        widget.configure(state='disabled')
        if at_end:
            widget.see('end')

    # ---- _answer_sender --------------------------------------------------------------
    def _answer_sender(self, event: Any = None) -> None:
        """
        ---- Summary ----
        Method to pass the typed answer to the question that is waiting for it.

        ---- Inputs ----
        event : Any
            The Tk key event (unused).

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Writes the answer into the terminal, clears and disables the answer box
        and wakes the question thread (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _pane_writer
        """

        if not self._is_waiting:
            return
        answer = self._entry.get()
        self._is_waiting = False
        if answer.strip():
            self._history.append(answer)
        self._history_position = len(self._history)
        self._entry.delete(0, 'end')
        self._entry.configure(state='disabled')
        self._hint.configure(text='Working ...')
        self._pane_writer(answer + '\n', 'answer')
        self._answers.put(answer)

    # ---- _history_stepper ------------------------------------------------------------
    def _history_stepper(self, step: int) -> None:
        """
        ---- Summary ----
        Method to recall an earlier answer in the answer box with the up and down keys.

        ---- Inputs ----
        step : int
            -1 for the previous answer, +1 for the next one.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the text of the answer box (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        if not self._history:
            return
        position = min(max(self._history_position + step, 0), len(self._history))
        self._history_position = position
        self._entry.delete(0, 'end')
        if position < len(self._history):
            self._entry.insert(0, self._history[position])

    # ---- _image_receiver -------------------------------------------------------------
    def _image_receiver(self,
                        version: int,
                        name: str,
                        png: Optional[bytes],
                        notes: str,
                        ) -> None:
        """
        ---- Summary ----
        Method to take a finished preview from the renderer and show it if it is the
        current file. Previews of older settings are dropped.

        ---- Inputs ----
        version : int
            Number of the request the preview was drawn for.
        name : str
            File name.
        png : Optional[bytes]
            Picture, or None when it could not be drawn.
        notes : str
            Warnings, or the reason when there is no picture.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Stores the preview and may redraw the plot area (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _picture_shower
        """

        if version != self._version:
            return
        if png is None:
            self._failures[name] = notes
        else:
            self._images[name] = png
            self._notes[name] = notes
        if self._names and name == self._names[self._index]:
            self._picture_shower()

    # ---- _event_handler --------------------------------------------------------------
    def _event_handler(self, event: tuple) -> None:
        """
        ---- Summary ----
        Method to carry out one message from the other threads, on the window thread.

        ---- Inputs ----
        event : tuple
            (kind, ...) with kind 'prompt', 'spec', 'focus', 'session', 'image',
            'closed' or 'finished'.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the window (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _image_receiver
        _navigator
        _pane_writer
        _picture_shower
        """

        kind = event[0]
        if kind == 'prompt':
            self._pane_writer(event[1])
            self._is_waiting = True
            self._entry.configure(state='normal')
            self._entry.focus_set()
            self._hint.configure(text='Type your answer and press Enter')
        elif kind == 'session':
            self._session = event[1]
            self._names = [s['name'] for s in self._session.summaries]
            self._combo.configure(values=self._names)
            self._renderer = PreviewRenderer(self._session, self._image_deliverer)
            self._renderer.start()
            self._nav_state(True)
            self._navigator(self._session.current)
        elif kind == 'spec':
            spec, name = event[1], event[2]
            self._version += 1
            self._previous = {**self._previous, **self._images}
            self._images, self._notes, self._failures = {}, {}, {}
            self._has_spec = True
            if name in self._names:
                self._index = self._names.index(name)
            self._renderer.request_setter(spec, self._version, self._index)
            self._navigator(self._index)
        elif kind == 'focus':
            if event[1] in self._names:
                self._navigator(self._names.index(event[1]))
        elif kind == 'image':
            self._image_receiver(*event[1:])
        elif kind == 'closed':
            self._nav_state(False)
            self._status.configure(text=self._status.cget('text'))
        elif kind == 'finished':
            self._is_finished = True
            self._nav_state(False)
            self._hint.configure(text='Finished - close this window when you are done')
            self._pane_writer('\n[Finished. You can close this window.]\n', 'answer')

    # ---- _drain_runner ---------------------------------------------------------------
    def _drain_runner(self) -> None:
        """
        ---- Summary ----
        Method that runs on the window thread every few milliseconds and carries out the
        messages the other threads have queued, joining consecutive text into one
        insert.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Changes the window and schedules itself again (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _event_handler
        _pane_writer
        """

        if self._is_destroyed:
            return
        pending: List[str] = []
        pending_kind = 'out'

        def flush() -> None:
            if pending:
                self._pane_writer(''.join(pending), pending_kind)
                pending.clear()

        try:
            for _ in range(400):
                event = self._events.get_nowait()
                if event[0] == 'text':
                    if pending and event[2] != pending_kind:
                        flush()
                    pending_kind = event[2]
                    pending.append(event[1])
                    continue
                flush()
                self._event_handler(event)
        except queue.Empty:
            pass
        flush()
        self._root.after(25, self._drain_runner)

    # ---- _closing_handler ------------------------------------------------------------
    def _closing_handler(self) -> None:
        """
        ---- Summary ----
        Method to close the window. While the program is still running the user is asked
        first, and a question that is waiting is ended so the program stops cleanly.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Stops the threads and closes the window (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        if not self._is_finished:
            from tkinter import messagebox
            if not messagebox.askokcancel('Close DePalencify',
                                          'The program has not finished. Close the '
                                          'window and stop it? A file that is being '
                                          'written may be left incomplete.',
                                          parent=self._root,
                                          ):
                return
        self._is_destroyed = True
        self._answers.put(_CLOSED)
        if self._renderer is not None:
            self._renderer.stopper()
        self._root.destroy()

    # ---- _logic_runner ---------------------------------------------------------------
    def _logic_runner(self) -> None:
        """
        ---- Summary ----
        Method that runs the program in its own thread and reports when it is done.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Sets exit_code and queues the finished message (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        try:
            self.exit_code = self._program()
        except SystemExit as exc:
            self.exit_code = exc.code if isinstance(exc.code, int) else 1
        except BaseException:  # show the problem in the window, then finish
            traceback.print_exc()
            self.exit_code = 1
        finally:
            self._events.put(('finished',))

    # ---- MAIN METHODS ----------------------------------------------------------------

    # ---- file_focuser ----------------------------------------------------------------
    def file_focuser(self, name: str) -> None:
        """
        ---- Summary ----
        Method to show the file a question is about. It is called from the question
        thread.

        ---- Inputs ----
        name : str
            Name of the file.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Queues the change for the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self._events.put(('focus', name))

    # ---- figure_shower ---------------------------------------------------------------
    def figure_shower(self, figure: Any) -> None:
        """
        ---- Summary ----
        Method that is never needed: the window draws its own previews from the
        settings (spec_publisher).

        ---- Inputs ----
        figure : Any
            A drawn figure (ignored).

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

    # ---- input_reader ----------------------------------------------------------------
    def input_reader(self, prompt: Any = '') -> str:
        """
        ---- Summary ----
        Method that replaces the built-in input while the window is open: it shows the
        prompt in the terminal and waits for the answer typed in the answer box. Other
        threads still use the real input.

        ---- Inputs ----
        prompt : Any
            The prompt text, for example "   > ".

        ---- Globals read ----
        None.

        ---- Outputs ----
        str
            The typed answer. Raises EOFError when the window is closed.

        ---- Globals mutated ----
        None. Waits for the user (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        if threading.current_thread() is not self.logic_thread:
            return self._real_input(prompt)
        self._events.put(('prompt', str(prompt)))
        answer = self._answers.get()
        if answer is _CLOSED:
            raise EOFError
        return answer

    # ---- output_capturer -------------------------------------------------------------
    @contextmanager
    def output_capturer(self) -> Iterator[io.StringIO]:
        """
        ---- Summary ----
        Method to capture what the current thread prints (the preview thread), without
        touching the terminal or the log file.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        Iterator[io.StringIO]
            The buffer the output is collected in.

        ---- Globals mutated ----
        None. Captures the output of the current thread (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        output_capturer
        """

        with output_capturer() as buffer:
            yield buffer

    # ---- run -------------------------------------------------------------------------
    def run(self) -> int:
        """
        ---- Summary ----
        Method to run the program in the window: take over the output streams and the
        input, start the program thread, and run the window until it is closed.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        int
            The exit code of the program (1 when the window was closed before it
            finished).

        ---- Globals mutated ----
        None. Replaces sys.stdout, sys.stderr and the built-in input while the window
        runs, and restores them afterwards (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        _drain_runner
        _logic_runner
        """

        global _active_gui
        self._real_input = builtins.input
        original = (sys.stdout, sys.stderr)
        owner = lambda: None if self._is_destroyed else self.logic_thread
        sys.stdout = OutputRouter(original[0], self.text_sender, 'out', owner)
        sys.stderr = OutputRouter(original[1], self.text_sender, 'err', owner)
        builtins.input = self.input_reader
        _active_gui = self
        self.logic_thread = threading.Thread(target=self._logic_runner,
                                             name='program',
                                             daemon=True,
                                             )
        try:
            self.logic_thread.start()
            self._root.after(25, self._drain_runner)
            try:
                self._root.mainloop()
            except KeyboardInterrupt:
                self._is_destroyed = True
                self._answers.put(_CLOSED)
            self.logic_thread.join(timeout=3)
        finally:
            sys.stdout, sys.stderr = original
            builtins.input = self._real_input
            _active_gui = None
        return self.exit_code

    # ---- session_attacher ------------------------------------------------------------
    def session_attacher(self, session: ViewerSession) -> None:
        """
        ---- Summary ----
        Method to give the window the files of the browser session, which fills the
        file selector and starts the preview thread.

        ---- Inputs ----
        session : ViewerSession
            The browser session.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Queues the session for the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self._events.put(('session', session))

    # ---- spec_publisher --------------------------------------------------------------
    def spec_publisher(self, spec: PreviewSpec, name: Optional[str]) -> None:
        """
        ---- Summary ----
        Method to give the window new settings: every file is drawn again with them.

        ---- Inputs ----
        spec : PreviewSpec
            The settings to draw with.
        name : Optional[str]
            File to show first, or None to stay on the current file.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Queues the settings for the window (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self._events.put(('spec', spec, name))

    # ---- text_sender -----------------------------------------------------------------
    def text_sender(self, text: str, kind: str) -> None:
        """
        ---- Summary ----
        Method to queue text from the program thread for the terminal.

        ---- Inputs ----
        text : str
            Text as printed.
        kind : str
            'out' or 'err'.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Queues the text (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self._events.put(('text', text, kind))

    # ---- window_closer ---------------------------------------------------------------
    def window_closer(self) -> None:
        """
        ---- Summary ----
        Method to end the previews when the browser steps are over: the preview thread
        is stopped (so it cannot clash with the processing that follows) and the file
        controls are switched off. The last picture stays on show.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Stops the preview thread and queues the change (side effects).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        if self._renderer is not None:
            self._renderer.stopper()
        self._events.put(('closed',))

    # ---- _image_deliverer ------------------------------------------------------------
    def _image_deliverer(self,
                         version: int,
                         name: str,
                         png: Optional[bytes],
                         notes: str,
                         ) -> None:
        """
        ---- Summary ----
        Method to queue a finished preview from the preview thread for the window.

        ---- Inputs ----
        version : int
            Number of the request it was drawn for.
        name : str
            File name.
        png : Optional[bytes]
            Picture, or None when it could not be drawn.
        notes : str
            Warnings, or the reason when there is no picture.

        ---- Globals read ----
        None.

        ---- Outputs ----
        None
            Nothing.

        ---- Globals mutated ----
        None. Queues the preview (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        self._events.put(('image', version, name, png, notes))


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- active_gui_getter ---------------------------------------------------------------
def active_gui_getter() -> Optional[ViewerGui]:
    """
    ---- Summary ----
    Main function to give the browser window that is open, if any.

    ---- Inputs ----
    None.

    ---- Globals read ----
    _active_gui (module state).

    ---- Outputs ----
    Optional[ViewerGui]
        The open window, or None when the program runs in the terminal.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return _active_gui


# ---- gui_runner ----------------------------------------------------------------------
def gui_runner(program: Callable[[], int], title: str) -> Optional[int]:
    """
    ---- Summary ----
    Main function to run the whole program inside the browser window. It returns None
    without running anything when the window cannot be opened, so the caller can run
    the program in the terminal instead.

    ---- Inputs ----
    program : Callable[[], int]
        The program; it asks the questions and returns its exit code.
    title : str
        Window title.

    ---- Globals read ----
    os.environ["DEPALENCIFY_NO_GUI"] (set to anything to keep the terminal).

    ---- Outputs ----
    Optional[int]
        The exit code of the program, or None when the window could not be opened.

    ---- Globals mutated ----
    None. Opens the window and runs the program (side effects); prints why the window
    could not open when it could not.

    ---- Equations ----
    None.

    ---- Helpers ----
    ViewerGui
    """

    try:
        if os.environ.get('DEPALENCIFY_NO_GUI'):
            raise GuiUnavailable('DEPALENCIFY_NO_GUI is set')
        try:
            import tkinter as tk
        except ImportError:
            raise GuiUnavailable('Tkinter is not installed')
        has_display = (os.environ.get('DISPLAY')
                       or os.environ.get('WAYLAND_DISPLAY')
                       )
        if sys.platform.startswith('linux') and not has_display:
            raise GuiUnavailable('there is no display')
        if sys.platform == 'win32':
            try:
                import ctypes
                ctypes.windll.shcore.SetProcessDpiAwareness(1)  # sharp text
            except Exception:
                pass
        try:
            root = tk.Tk()
        except tk.TclError as exc:
            raise GuiUnavailable(str(exc))
    except GuiUnavailable as exc:
        print(f'The experiment browser window cannot open ({exc}), so the questions '
              f'run in this terminal and previews are saved as a picture.',
              )
        return None
    return ViewerGui(tk, root, program, title).run()
