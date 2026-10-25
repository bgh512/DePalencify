"""Small helpers for asking numbered questions in the terminal.

Every question is printed on its own line, in colour, with a number (1.1, 1.1.1, ...)
and
its default in [brackets]; the answer is typed on the next line and Enter accepts the
default.
Information lines are printed normally, so the questions stand out.
"""

# ---- STANDARD IMPORTS ----------------------------------------------------------------
import os
import re
import sys
from typing import Callable, List, Optional, Sequence, Tuple


# ---- CONSTANTS -----------------------------------------------------------------------
COLOUR_QUESTION = '\x1b[1;38;5;213m'  # bold pink
COLOUR_SECTION = '\x1b[1;33m'  # bold yellow
ITALIC = '\x1b[3m'
RESET = '\x1b[0m'
INDENT = '   '
MAX_DEPTH = 6
_counters = [0] * MAX_DEPTH  # [section, question, sub question, ...]
_colour_ready = False
_tight_next = False  # True: the next question follows its heading line directly


# ---- USER QUIT -----------------------------------------------------------------------
class UserQuit(Exception):
    """
    Raised when the input ends (window closed, Ctrl+Z / Ctrl+D) so the program can stop
    cleanly.
    """


# ---- QUESTIONS HELPERS ---------------------------------------------------------------


# ---- _INPUT READER -------------------------------------------------------------------
def _input_reader(text: str, indent: str = '') -> str:
    """
    ---- Summary ----
    Helper function to show the answer prompt and read what the user types.

    ---- Inputs ----
    text : str
        The question text (not printed; kept so tests can replace this function and
        match on it).
    indent : str
        Indent placed before the "> " prompt.

    ---- Globals read ----
    input_flusher.

    ---- Outputs ----
    str
        The typed answer with surrounding spaces removed.

    ---- Globals mutated ----
    None. Reads from the terminal; raises UserQuit when the input ends (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    input_flusher
    """

    input_flusher()
    try:
        return input(f'{indent}> ').strip()
    except EOFError:
        raise UserQuit()


# ---- _NUMBER BUILDER -----------------------------------------------------------------
def _number_builder(depth: int) -> str:
    """
    ---- Summary ----
    Helper function to advance the counters and build the next question number.

    ---- Inputs ----
    depth : int
        Numbering depth (1 = 3.1, 2 = 3.1.1, ...).

    ---- Globals read ----
    MAX_DEPTH (module constant).

    ---- Outputs ----
    str
        Question number such as "3.1.2".

    ---- Globals mutated ----
    None. Increments the module counters _counters at the depth and resets deeper levels
    (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    _counters[depth] += 1
    for level in range(depth + 1, MAX_DEPTH):
        _counters[level] = 0
    return '.'.join(str(c) for c in _counters[:depth + 1])


# ---- _QUESTION PRINTER ---------------------------------------------------------------
def _question_printer(question: str, depth: int, hint: str = '') -> str:
    """
    ---- Summary ----
    Helper function to print the numbered, coloured question line.

    ---- Inputs ----
    question : str
        Question text, without its number.
    depth : int
        Numbering depth of the question (1 = 3.1, 2 = 3.1.1, ...).
    hint : str
        Text after the question, such as "[default]:" or "(y/N):"; may be empty.

    ---- Globals read ----
    INDENT (module constant); _tight_next (module state); text_colourer.

    ---- Outputs ----
    str
        Indent to use for the answer prompt and the option lines.

    ---- Globals mutated ----
    None. Prints to the terminal and clears the module flag _tight_next (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    _number_builder
    text_colourer
    """

    global _tight_next
    indent = INDENT * (depth - 1)
    line = f'{_number_builder(depth)} {question}'
    if hint:
        line += f' {hint}'
    print(f"{'' if _tight_next else chr(10)}{indent}{text_colourer(line)}")
    _tight_next = False
    return indent


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- CHOICE ASKER --------------------------------------------------------------------
def choice_asker(question: str,
                 options: Sequence[Tuple[str, str]],
                 default: Optional[str] = None,
                 depth: int = 1,
                 ) -> str:
    """
    ---- Summary ----
    Main function to ask a question answered by choosing one numbered option.

    ---- Inputs ----
    question : str
        Question text, without its number.
    options : Sequence[Tuple[str, str]]
        Choices as (key, label) pairs, shown as 1), 2), ...
    default : Optional[str]
        Key chosen when only Enter is pressed.
    depth : int
        Numbering depth of the question (1 = 3.1, 2 = 3.1.1, ...).

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        Key of the chosen option.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal (side effect); advances the question
    numbering counters.

    ---- Equations ----
    None.

    ---- Helpers ----
    _input_reader
    _question_printer
    """

    # ---- 1 Work out the default ------------------------------------------------------
    default_number = next((i
                           for i, (key, _) in enumerate(options, start=1)
                           if key == default
                           ),
                          None,
                          )
    hint = f'[{default_number}]:' if default_number else ''

    # ---- 2 Print the question and options --------------------------------------------
    indent = _question_printer(question, depth, hint)
    for number, (_, label) in enumerate(options, start=1):
        print(f'{indent}{INDENT}{number}) {label}')

    # ---- 3 Read and check the answer -------------------------------------------------
    while True:
        answer = _input_reader(question, indent)
        if not answer and default_number:
            return options[default_number - 1][0]
        if answer.isdigit() and 1 <= int(answer) <= len(options):
            return options[int(answer) - 1][0]
        print(f'{indent}Please type a number from 1 to {len(options)}.')


# ---- COLOUR CHECKER ------------------------------------------------------------------
def colour_checker() -> bool:
    """
    ---- Summary ----
    Main function to say whether the terminal can show colour; it also switches on
    colour codes in the Windows console the first time.

    ---- Inputs ----
    None.

    ---- Globals read ----
    os.environ, sys.stdout; _colour_ready (module state).

    ---- Outputs ----
    bool
        True when colour can be used (a terminal, and NO_COLOR is not set).

    ---- Globals mutated ----
    Sets the module state _colour_ready; may run an empty os.system call on Windows.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    global _colour_ready
    if 'NO_COLOR' in os.environ or not sys.stdout.isatty():
        return False
    if not _colour_ready:
        if os.name == 'nt':
            os.system('')  # switches on colour codes in the Windows console
        _colour_ready = True
    return True


# ---- HEADING PRINTER -----------------------------------------------------------------
def heading_printer(text: str) -> None:
    """
    ---- Summary ----
    Main function to print a plain heading, for example the summary.

    ---- Inputs ----
    text : str
        Heading text.

    ---- Globals read ----
    COLOUR_SECTION (module constant); text_colourer.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Prints to the terminal (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    text_colourer
    """

    print(f"\n{text_colourer(text, COLOUR_SECTION)}\n{'-' * len(text)}")


# ---- INFO PRINTER --------------------------------------------------------------------
def info_printer(text: str, depth: int = 1, tight: bool = False) -> None:
    """
    ---- Summary ----
    Main function to print an information line (not a question), indented to sit under
    the question above.

    ---- Inputs ----
    text : str
        Text to print or process.
    depth : int
        Numbering depth of the question (1 = 3.1, 2 = 3.1.1, ...).
    tight : bool
        True to make the next question follow this line without a blank line.

    ---- Globals read ----
    INDENT (module constant).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Prints to the terminal and sets the module flag _tight_next (side effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    global _tight_next
    print(f'{INDENT * (depth - 1)}{text}')
    _tight_next = tight


# ---- INPUT FLUSHER -------------------------------------------------------------------
def input_flusher() -> None:
    """
    ---- Summary ----
    Main function to throw away keys pressed while the program was busy, so a stray
    Enter cannot answer a question.

    ---- Inputs ----
    None.

    ---- Globals read ----
    os.name, sys.stdin.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Empties the keyboard input buffer; does nothing when the input is not a
    terminal (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    try:
        if os.name == 'nt':
            import msvcrt
            while msvcrt.kbhit():
                msvcrt.getwch()
        else:
            import termios
            termios.tcflush(sys.stdin, termios.TCIFLUSH)
    except Exception:  # not a real terminal (a pipe, a test): nothing to flush
        pass


# ---- MULTI ASKER ---------------------------------------------------------------------
def multi_asker(question: str,
                options: Sequence[str],
                default_all: bool = True,
                keep_order: bool = False,
                depth: int = 1,
                default_values: Optional[Sequence[str]] = None,
                label_formatter: Optional[Callable[[str], str]] = None,
                ) -> List[str]:
    """
    ---- Summary ----
    Main function to ask a question answered by choosing several numbered options.

    ---- Inputs ----
    question : str
        Question text, without its number.
    options : Sequence[str]
        Option names, shown as 1), 2), ...
    default_all : bool
        True to choose all options when only Enter is pressed and nothing is remembered.
    keep_order : bool
        True to return the options in the order typed instead of list order.
    depth : int
        Numbering depth of the question (1 = 3.1, 2 = 3.1.1, ...).
    default_values : Optional[Sequence[str]]
        Choice from last time, used for Enter when given.
    label_formatter : Optional[Callable[[str], str]]
        Function that changes how an option is shown, not what is returned.

    ---- Globals read ----
    None.

    ---- Outputs ----
    List[str]
        The chosen options.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal (side effect); advances the question
    numbering counters.

    ---- Equations ----
    None.

    ---- Helpers ----
    _input_reader
    _question_printer
    """

    # ---- 1 Work out the defaults -----------------------------------------------------
    remembered = [v for v in (default_values or []) if v in options]
    fallback = remembered or (list(options) if default_all else [])
    if remembered:
        numbers_text = ','.join(str(options.index(v) + 1) for v in remembered)
        hint = f'(numbers separated by commas, Enter = {numbers_text}):'
    else:
        hint = ('(numbers separated by commas, Enter = all):'
                if default_all
                else '(numbers separated by commas):'
                )

    # ---- 2 Print the question and options --------------------------------------------
    indent = _question_printer(question, depth, hint)
    for number, label in enumerate(options, start=1):
        shown = label_formatter(label) if label_formatter else label
        print(f'{indent}{INDENT}{number}) {shown}')

    # ---- 3 Read and check the answer -------------------------------------------------
    while True:
        answer = _input_reader(question, indent)
        if not answer and fallback:
            return list(fallback)
        picked = [p for p in re.split(r'[,\s]+', answer) if p]
        if picked and all(p.isdigit() and 1 <= int(p) <= len(options) for p in picked):
            numbers = (list(dict.fromkeys(int(p) - 1 for p in picked))
                       if keep_order
                       else sorted({int(p) - 1 for p in picked})
                       )
            return [options[i] for i in numbers]
        print(f'{indent}Please type numbers from 1 to {len(options)}, e.g. 1,3.')


# ---- NUMBER ASKER --------------------------------------------------------------------
def number_asker(question: str,
                 default: Optional[float] = None,
                 minimum: Optional[float] = None,
                 maximum: Optional[float] = None,
                 exclusive_minimum: bool = False,
                 allow_blank: bool = False,
                 depth: int = 1,
                 blank_label: str = 'none',
                 ) -> Optional[float]:
    """
    ---- Summary ----
    Main function to ask a question answered with a number, asking again until the value
    is valid.

    ---- Inputs ----
    question : str
        Question text, without its number.
    default : Optional[float]
        Answer used when only Enter is pressed.
    minimum : Optional[float]
        Smallest accepted value.
    maximum : Optional[float]
        Largest accepted value.
    exclusive_minimum : bool
        True when the minimum itself is not accepted.
    allow_blank : bool
        True to accept an empty answer as None when there is no default.
    depth : int
        Numbering depth of the question (1 = 3.1, 2 = 3.1.1, ...).
    blank_label : str
        Word shown in [brackets] for an empty answer.

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[float]
        The number, the default, or None for an accepted empty answer.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal (side effect); advances the question
    numbering counters.

    ---- Equations ----
    None.

    ---- Helpers ----
    _input_reader
    _question_printer
    """

    # ---- 1 Format the default --------------------------------------------------------
    if isinstance(default, (int, float)):
        hint = f'[{default:g}]:'
    else:
        hint = f'[{blank_label}]:' if allow_blank else ''

    # ---- 2 Print the question --------------------------------------------------------
    indent = _question_printer(question, depth, hint)

    # ---- 3 Read and check the answer -------------------------------------------------
    while True:
        answer = _input_reader(question, indent).replace(',', '.')
        if not answer:
            if default is not None:
                return default
            if allow_blank:
                return None
            print(f'{indent}A number is needed here.')
            continue
        try:
            value = float(answer)
        except ValueError:
            print(f'{indent}That is not a number.')
            continue
        if (minimum is not None and
            (value <= minimum if exclusive_minimum else value < minimum)
            ):
            print(f'{indent}The value must be '
                  f"{'above' if exclusive_minimum else 'at least'} {minimum:g}.",
                  )
            continue
        if maximum is not None and value > maximum:
            print(f'{indent}The value must be at most {maximum:g}.')
            continue
        return value


# ---- NUMBERING RESTARTER -------------------------------------------------------------
def numbering_restarter(depth: int) -> None:
    """
    ---- Summary ----
    Main function to make the next question at a depth (and deeper) start again from 1.

    ---- Inputs ----
    depth : int
        Numbering depth to restart; deeper levels restart too.

    ---- Globals read ----
    MAX_DEPTH (module constant).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Resets entries of the module counters _counters (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    for level in range(depth, MAX_DEPTH):
        _counters[level] = 0


# ---- NUMBERING SETTER ----------------------------------------------------------------
def numbering_setter(depth: int, value: int) -> None:
    """
    ---- Summary ----
    Main function to set the current number at a depth, for example so the next
    sub-questions are numbered 3.4.3.1.

    ---- Inputs ----
    depth : int
        Numbering depth to set.
    value : int
        Number to make current at that depth.

    ---- Globals read ----
    MAX_DEPTH (module constant).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Sets and resets entries of the module counters _counters (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    _counters[depth] = value
    for level in range(depth + 1, MAX_DEPTH):
        _counters[level] = 0


# ---- NUMBERS ASKER -------------------------------------------------------------------
def numbers_asker(question: str, count: int, depth: int = 1) -> List[int]:
    """
    ---- Summary ----
    Main function to ask a question answered by numbers from 1 to a count, separated by
    commas.

    ---- Inputs ----
    question : str
        Question text, without its number.
    count : int
        Largest number accepted.
    depth : int
        Numbering depth of the question (1 = 3.1, 2 = 3.1.1, ...).

    ---- Globals read ----
    None.

    ---- Outputs ----
    List[int]
        The chosen numbers in ascending order; an empty list for Enter (none).

    ---- Globals mutated ----
    None. Reads from and prints to the terminal (side effect); advances the question
    numbering counters.

    ---- Equations ----
    None.

    ---- Helpers ----
    _input_reader
    _question_printer
    """

    # ---- 1 Print the question --------------------------------------------------------
    indent = _question_printer(question,
                               depth,
                               '(numbers separated by commas, Enter = none):',
                               )

    # ---- 2 Read and check the answer -------------------------------------------------
    while True:
        answer = _input_reader(question, indent)
        if not answer:
            return []
        picked = [p for p in re.split(r'[,\s]+', answer) if p]
        if all(p.isdigit() and 1 <= int(p) <= count for p in picked):
            return sorted({int(p) for p in picked})
        print(f'{indent}Please type numbers from 1 to {count}, e.g. 1,3.')


# ---- PATH CLEANER --------------------------------------------------------------------
def path_cleaner(text: str) -> str:
    """
    ---- Summary ----
    Main function to clean a path typed or dragged into the window by removing
    surrounding quotes and spaces.

    ---- Inputs ----
    text : str
        Text as received from the terminal.

    ---- Globals read ----
    None.

    ---- Outputs ----
    str
        Path text without surrounding quotes or spaces.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    return text.strip().strip('"').strip("'").strip()


# ---- PROGRESS CLEARER ----------------------------------------------------------------
def progress_clearer() -> None:
    """
    ---- Summary ----
    Main function to remove the progress line from the terminal.

    ---- Inputs ----
    None.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Prints to the terminal (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    print('\r' + ' ' * 100 + '\r', end='', flush=True)


# ---- PROGRESS PRINTER ----------------------------------------------------------------
def progress_printer(text: str) -> None:
    """
    ---- Summary ----
    Main function to show a one-line progress message that the next message overwrites.

    ---- Inputs ----
    text : str
        Message to show.

    ---- Globals read ----
    None.

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Prints to the terminal without a new line (side effect).

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """

    print(f'\r{text}'.ljust(100), end='', flush=True)


# ---- SECTION STARTER -----------------------------------------------------------------
def section_starter(title: str) -> None:
    """
    ---- Summary ----
    Main function to start the next numbered section and print its heading.

    ---- Inputs ----
    title : str
        Section title, without its number.

    ---- Globals read ----
    COLOUR_SECTION, MAX_DEPTH (module constants).

    ---- Outputs ----
    None
        Nothing.

    ---- Globals mutated ----
    None. Advances the module numbering counters _counters and prints the heading (side
    effects).

    ---- Equations ----
    None.

    ---- Helpers ----
    text_colourer
    """

    _counters[0] += 1
    for level in range(1, MAX_DEPTH):
        _counters[level] = 0
    text = f'{_counters[0]}. {title}'
    print(f"\n{text_colourer(text, COLOUR_SECTION)}\n{'-' * len(text)}")


# ---- TEXT ASKER ----------------------------------------------------------------------
def text_asker(question: str,
               default: Optional[str] = None,
               depth: int = 1,
               ) -> Optional[str]:
    """
    ---- Summary ----
    Main function to ask a question answered with a line of text.

    ---- Inputs ----
    question : str
        Question text, without its number.
    default : Optional[str]
        Answer used when only Enter is pressed; shown as [default]:.
    depth : int
        Numbering depth of the question (1 = 3.1, 2 = 3.1.1, ...).

    ---- Globals read ----
    None.

    ---- Outputs ----
    Optional[str]
        The typed text, or the default when Enter is pressed.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal (side effect); advances the question
    numbering counters.

    ---- Equations ----
    None.

    ---- Helpers ----
    _input_reader
    _question_printer
    """

    hint = f'[{default}]:' if default not in (None, '') else ''
    indent = _question_printer(question, depth, hint)
    answer = _input_reader(question, indent)
    return answer if answer else default


# ---- TEXT COLOURER -------------------------------------------------------------------
def text_colourer(text: str, code: str = COLOUR_QUESTION) -> str:
    """
    ---- Summary ----
    Main function to wrap text in a colour code when colour is available.

    ---- Inputs ----
    text : str
        Text to colour.
    code : str
        ANSI colour code (COLOUR_QUESTION by default).

    ---- Globals read ----
    COLOUR_QUESTION, RESET (module constants); colour_checker.

    ---- Outputs ----
    str
        The coloured text, or the text unchanged without colour.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    colour_checker
    """

    return f'{code}{text}{RESET}' if colour_checker() else text


# ---- TEXT ITALISER -------------------------------------------------------------------
def text_italiser(text: str) -> str:
    """
    ---- Summary ----
    Main function to write text in italics when the terminal supports it.

    ---- Inputs ----
    text : str
        Text to put in italics.

    ---- Globals read ----
    ITALIC, RESET (module constants); colour_checker.

    ---- Outputs ----
    str
        The italic text, or the text unchanged without colour support.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    colour_checker
    """

    return f'{ITALIC}{text}{RESET}' if colour_checker() else text


# ---- YES NO ASKER --------------------------------------------------------------------
def yes_no_asker(question: str, default: bool = False, depth: int = 1) -> bool:
    """
    ---- Summary ----
    Main function to ask a yes/no question.

    ---- Inputs ----
    question : str
        Question text, without its number.
    default : bool
        Answer used when only Enter is pressed (the capital letter in the hint).
    depth : int
        Numbering depth of the question (1 = 3.1, 2 = 3.1.1, ...).

    ---- Globals read ----
    None.

    ---- Outputs ----
    bool
        True for y or yes, False for n or no, the default for Enter.

    ---- Globals mutated ----
    None. Reads from and prints to the terminal (side effect); advances the question
    numbering counters.

    ---- Equations ----
    None.

    ---- Helpers ----
    _input_reader
    _question_printer
    """

    # ---- 1 Print the question --------------------------------------------------------
    hint = '(Y/n):' if default else '(y/N):'
    indent = _question_printer(question, depth, hint)

    # ---- 2 Read and check the answer -------------------------------------------------
    while True:
        answer = _input_reader(question, indent).lower()
        if not answer:
            return default
        if answer in ('y', 'yes'):
            return True
        if answer in ('n', 'no'):
            return False
        print(f'{indent}Please answer y or n.')
