"""
Pieces of the text terminal in the experiment browser window: colour codes and the
output streams that send the program's text to the window.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import io
import re
import threading
from typing import Any, Callable, Dict, List, Optional, Tuple

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from utils_shared.output_capture import captured_buffer_getter


# ---- CONSTANTS -----------------------------------------------------------------------
# The 16 basic terminal colours, chosen to be readable on the dark terminal background.
BASIC_COLOURS = ('#1e1e1e', '#e06c75', '#98c379', '#e5c07b',
                 '#61afef', '#c678dd', '#56b6c2', '#d4d4d4',
                 '#5c6370', '#ff7b86', '#b5e890', '#ffd98a',
                 '#82c4ff', '#e19cf5', '#7fdbe6', '#ffffff',
                 )
_CODE_PATTERN = re.compile(r'(\x1b\[[0-9;]*m|\r)')


# ---- TERMINAL HELPERS ----------------------------------------------------------------


# ---- ansi_colour_getter --------------------------------------------------------------
def ansi_colour_getter(index: int) -> str:
    """
    ---- Summary ----
    Main function to give the colour of an entry of the 256-colour terminal palette.

    ---- Inputs ----
    index : int
        Palette number, 0 to 255 (0-15 basic, 16-231 colour cube, 232-255 greys).

    ---- Globals read ----
    BASIC_COLOURS (module constant).

    ---- Outputs ----
    str
        The colour as "#rrggbb".

    ---- Globals mutated ----
    None.

    ---- Equations ----
    Cube colours: each of red, green and blue is 0 for level 0 and 55 + 40 * level
    for levels 1 to 5, where index - 16 = 36 * red level + 6 * green level + blue
    level. Greys: 8 + 10 * (index - 232).

    ---- Helpers ----
    None.
    """

    if index < 16:
        return BASIC_COLOURS[index]
    if index >= 232:
        grey = 8 + 10 * (index - 232)
        return f'#{grey:02x}{grey:02x}{grey:02x}'
    index -= 16
    levels = [(index // 36) % 6, (index // 6) % 6, index % 6]
    red, green, blue = [0 if level == 0 else 55 + 40 * level for level in levels]
    return f'#{red:02x}{green:02x}{blue:02x}'


# ---- ansi_splitter -------------------------------------------------------------------
def ansi_splitter(text: str) -> List[Tuple[str, str]]:
    """
    ---- Summary ----
    Main function to cut printed text into plain text, colour codes and carriage
    returns, in order, so a text window can colour the text and overwrite progress
    lines.

    ---- Inputs ----
    text : str
        Text as printed, possibly with colour codes (ESC[...m) and carriage returns.

    ---- Globals read ----
    _CODE_PATTERN (module constant).

    ---- Outputs ----
    List[Tuple[str, str]]
        [(kind, value)] with kind 'text' (the characters), 'code' (the numbers of a
        colour code, for example "1;33") or 'return' (value empty). A carriage return
        directly before a new line is part of the line ending and is dropped.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    text = text.replace('\r\n', '\n')
    parts: List[Tuple[str, str]] = []
    for piece in _CODE_PATTERN.split(text):
        if piece == '\r':
            parts.append(('return', ''))
        elif piece.startswith('\x1b['):
            parts.append(('code', piece[2:-1]))
        elif piece:
            parts.append(('text', piece))
    return parts


# ---- ansi_style_updater --------------------------------------------------------------
def ansi_style_updater(style: Dict[str, Any], code: str) -> Dict[str, Any]:
    """
    ---- Summary ----
    Main function to apply one colour code to the current text style.

    ---- Inputs ----
    style : Dict[str, Any]
        {fg, bold, italic}: colour as "#rrggbb" or None for the default, and two flags.
    code : str
        Numbers of the colour code, separated by semicolons ("" means reset).

    ---- Globals read ----
    BASIC_COLOURS (module constant).

    ---- Outputs ----
    Dict[str, Any]
        The new style; ``style`` is not changed.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    ansi_colour_getter
    """

    new = dict(style)
    numbers = [int(n) for n in code.split(';') if n.isdigit()] or [0]
    position = 0
    while position < len(numbers):
        n = numbers[position]
        if n == 0:
            new = {'fg': None, 'bold': False, 'italic': False}
        elif n == 1:
            new['bold'] = True
        elif n == 3:
            new['italic'] = True
        elif n == 22:
            new['bold'] = False
        elif n == 23:
            new['italic'] = False
        elif 30 <= n <= 37:
            new['fg'] = BASIC_COLOURS[n - 30]
        elif 90 <= n <= 97:
            new['fg'] = BASIC_COLOURS[n - 90 + 8]
        elif n == 39:
            new['fg'] = None
        elif n == 38 and position + 2 < len(numbers) and numbers[position + 1] == 5:
            new['fg'] = ansi_colour_getter(min(numbers[position + 2], 255))
            position += 2
        position += 1
    return new


# ---- OutputRouter --------------------------------------------------------------------
class OutputRouter:
    """
    ---- Summary ----
    File-like object that replaces sys.stdout and sys.stderr while the browser window
    is open. What the program's own thread prints goes to the terminal in the window;
    what other threads print goes to the real stream; and a thread that is capturing its
    output (output_capturer) keeps it to itself.

    ---- Attributes ----
    encoding : str
        Always "utf-8".

    ---- Globals read ----
    None.

    ---- Methods ----
    __init__
    __getattr__
    fileno
    flush
    isatty
    reconfigure
    write
    """

    encoding = 'utf-8'
    errors = 'replace'

    # ---- __init__ --------------------------------------------------------------------
    def __init__(self,
                 original: Any,
                 sender: Callable[[str, str], None],
                 kind: str,
                 owner: Callable[[], Optional[threading.Thread]],
                 ) -> None:
        """
        ---- Summary ----
        Method to store where the text goes.

        ---- Inputs ----
        original : Any
            The stream that was replaced; used for other threads and after the window is
            closed.
        sender : Callable[[str, str], None]
            Function that passes (text, kind) to the window.
        kind : str
            'out' for standard output or 'err' for standard error.
        owner : Callable[[], Optional[threading.Thread]]
            Function that gives the thread whose output belongs in the window (None
            once the window is closed).

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

        self._original = original
        self._sender = sender
        self._kind = kind
        self._owner = owner

    # ---- SPECIAL METHODS -------------------------------------------------------------

    # ---- __getattr__ -----------------------------------------------------------------
    def __getattr__(self, name: str) -> Any:
        """
        ---- Summary ----
        Method to pass any other attribute lookup to the stream that was replaced.

        ---- Inputs ----
        name : str
            Attribute name that was not found on the instance.

        ---- Globals read ----
        None.

        ---- Outputs ----
        Any
            The attribute of the original stream.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        return getattr(self._original, name)

    # ---- MAIN METHODS ----------------------------------------------------------------

    # ---- fileno ----------------------------------------------------------------------
    def fileno(self) -> int:
        """
        ---- Summary ----
        Method that says there is no file descriptor, so libraries that ask for one fall
        back to plain writes. The name is fixed by the file-like protocol.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        int
            Never returns; raises io.UnsupportedOperation.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        raise io.UnsupportedOperation('fileno')

    # ---- flush -----------------------------------------------------------------------
    def flush(self) -> None:
        """
        ---- Summary ----
        Method that does nothing: text is passed on as soon as it is written. The name
        is fixed by the file-like protocol.

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

    # ---- isatty ----------------------------------------------------------------------
    def isatty(self) -> bool:
        """
        ---- Summary ----
        Method to say that the stream shows colour, because the terminal in the window
        does. The name is fixed by the file-like protocol.

        ---- Inputs ----
        None.

        ---- Globals read ----
        None.

        ---- Outputs ----
        bool
            Always True.

        ---- Globals mutated ----
        None.

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        return True

    # ---- reconfigure -----------------------------------------------------------------
    def reconfigure(self, **kwargs: Any) -> None:
        """
        ---- Summary ----
        Method that accepts and ignores new stream settings, because the window shows
        every symbol.

        ---- Inputs ----
        **kwargs : Any
            Stream settings (ignored).

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

    # ---- write -----------------------------------------------------------------------
    def write(self, text: str) -> int:
        """
        ---- Summary ----
        Method to send text where it belongs: the capture of the thread, the window, or
        the real stream. The name is fixed by the file-like protocol.

        ---- Inputs ----
        text : str
            Text to write.

        ---- Globals read ----
        None.

        ---- Outputs ----
        int
            Number of characters written.

        ---- Globals mutated ----
        None. Passes text to the window or the real stream (side effect).

        ---- Equations ----
        None.

        ---- Helpers ----
        None.
        """

        captured = captured_buffer_getter()
        if captured is not None:
            return captured.write(text)
        owner = self._owner()
        if owner is not None and threading.current_thread() is owner:
            self._sender(text, self._kind)
        else:
            self._original.write(text)
        return len(text)
