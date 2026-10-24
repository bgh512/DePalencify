"""Small helpers for asking numbered questions in the terminal.

Every question is printed on its own line, in colour, with a number (1.1, 1.1.1, ...) and
its default in [brackets]; the answer is typed on the next line and Enter accepts the default.
Information lines are printed normally, so the questions stand out.
"""
import os
import re
import sys
from typing import Callable, List, Optional, Sequence, Tuple

COLOUR_QUESTION = '\x1b[1;36m'      # bold cyan
COLOUR_SECTION = '\x1b[1;33m'       # bold yellow
ITALIC = '\x1b[3m'
RESET = '\x1b[0m'
INDENT = '   '
MAX_DEPTH = 6

_counters = [0] * MAX_DEPTH         # [section, question, sub question, ...]
_colour_ready = False


class UserQuit(Exception):
    """Raised when the input ends (window closed, Ctrl+Z / Ctrl+D) so the program can stop cleanly."""


# ---- COLOUR ----

def colour_enabled() -> bool:
    """True when the terminal can show colour (and NO_COLOR is not set)."""
    global _colour_ready
    if 'NO_COLOR' in os.environ or not sys.stdout.isatty():
        return False
    if not _colour_ready:
        if os.name == 'nt':
            os.system('')              # switches on colour codes in the Windows console
        _colour_ready = True
    return True


def coloured(text: str, code: str = COLOUR_QUESTION) -> str:
    """``text`` wrapped in a colour code, or unchanged when colour is not available."""
    return f'{code}{text}{RESET}' if colour_enabled() else text


def italic(text: str) -> str:
    """``text`` in italics when the terminal supports it, otherwise in plain brackets-free text."""
    return f'{ITALIC}{text}{RESET}' if colour_enabled() else text


# ---- NUMBERING ----

def section_starter(title: str) -> None:
    """Start the next numbered section and print its heading."""
    _counters[0] += 1
    for level in range(1, MAX_DEPTH):
        _counters[level] = 0
    text = f'{_counters[0]}. {title}'
    print(f"\n{coloured(text, COLOUR_SECTION)}\n{'-' * len(text)}")


def numbering_restarter(depth: int) -> None:
    """Make the next question at ``depth`` (and deeper) start again from 1."""
    for level in range(depth, MAX_DEPTH):
        _counters[level] = 0


def _number_builder(depth: int) -> str:
    """The next question number at ``depth`` (1 = 3.1, 2 = 3.1.1, ...)."""
    _counters[depth] += 1
    for level in range(depth + 1, MAX_DEPTH):
        _counters[level] = 0
    return '.'.join(str(c) for c in _counters[:depth + 1])


def _question_printer(question: str, depth: int, hint: str = '') -> str:
    """Print the numbered question line; returns the indent used for the answer prompt."""
    indent = INDENT * (depth - 1)
    line = f'{_number_builder(depth)} {question}'
    if hint:
        line += f' {hint}'
    print(f'\n{indent}{coloured(line)}')
    return indent


def _read(text: str, indent: str = '') -> str:
    """Show the answer prompt and return what was typed (``text`` is the question, for tests)."""
    try:
        return input(f'{indent}> ').strip()
    except EOFError:
        raise UserQuit()


def info(text: str, depth: int = 1) -> None:
    """Print an information line (not a question), indented to sit under the question above."""
    print(f'{INDENT * (depth - 1)}{text}')


# ---- QUESTIONS ----

def ask_text(question: str, default: Optional[str] = None, depth: int = 1) -> Optional[str]:
    """A line of text; Enter gives ``default``. The default is shown as [default]:"""
    hint = f'[{default}]:' if default not in (None, '') else ''
    indent = _question_printer(question, depth, hint)
    answer = _read(question, indent)
    return answer if answer else default


def ask_yes_no(question: str, default: bool = False, depth: int = 1) -> bool:
    """y or n; Enter gives ``default`` (the capital letter in the hint)."""
    hint = '(Y/n):' if default else '(y/N):'
    indent = _question_printer(question, depth, hint)
    while True:
        answer = _read(question, indent).lower()
        if not answer:
            return default
        if answer in ('y', 'yes'):
            return True
        if answer in ('n', 'no'):
            return False
        print(f'{indent}Please answer y or n.')


def ask_number(question: str,
               default: Optional[float] = None,
               minimum: Optional[float] = None,
               maximum: Optional[float] = None,
               exclusive_minimum: bool = False,
               allow_blank: bool = False,
               depth: int = 1,
               blank_label: str = 'none',
               ) -> Optional[float]:
    """A number; with ``allow_blank`` an empty answer (when there is no default) gives None."""
    if isinstance(default, (int, float)):
        hint = f'[{default:g}]:'
    else:
        hint = f'[{blank_label}]:' if allow_blank else ''
    indent = _question_printer(question, depth, hint)
    while True:
        answer = _read(question, indent).replace(',', '.')
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
        if minimum is not None and (value <= minimum if exclusive_minimum else value < minimum):
            print(f"{indent}The value must be {'above' if exclusive_minimum else 'at least'} {minimum:g}.")
            continue
        if maximum is not None and value > maximum:
            print(f'{indent}The value must be at most {maximum:g}.')
            continue
        return value


def ask_choice(question: str,
               options: Sequence[Tuple[str, str]],
               default: Optional[str] = None,
               depth: int = 1,
               ) -> str:
    """``options`` is a list of (key, label). The user types the number; returns the key. ``default`` is a key."""
    default_number = next((i for i, (key, _) in enumerate(options, start=1) if key == default), None)
    hint = f'[{default_number}]:' if default_number else ''
    indent = _question_printer(question, depth, hint)
    for number, (_, label) in enumerate(options, start=1):
        print(f'{indent}{INDENT}{number}) {label}')
    while True:
        answer = _read(question, indent)
        if not answer and default_number:
            return options[default_number - 1][0]
        if answer.isdigit() and 1 <= int(answer) <= len(options):
            return options[int(answer) - 1][0]
        print(f'{indent}Please type a number from 1 to {len(options)}.')


def ask_multi(question: str,
              options: Sequence[str],
              default_all: bool = True,
              keep_order: bool = False,
              depth: int = 1,
              ) -> List[str]:
    """Several of ``options``: numbers separated by commas (Enter = all). With ``keep_order`` the typed order is kept."""
    indent = _question_printer(question, depth, '(numbers separated by commas, Enter = all):' if default_all
                               else '(numbers separated by commas):')
    for number, label in enumerate(options, start=1):
        print(f'{indent}{INDENT}{number}) {label}')
    while True:
        answer = _read(question, indent)
        if not answer and default_all:
            return list(options)
        picked = [p for p in re.split(r'[,\s]+', answer) if p]
        if picked and all(p.isdigit() and 1 <= int(p) <= len(options) for p in picked):
            numbers = list(dict.fromkeys(int(p) - 1 for p in picked)) if keep_order else sorted({int(p) - 1 for p in picked})
            return [options[i] for i in numbers]
        print(f'{indent}Please type numbers from 1 to {len(options)}, e.g. 1,3.')


def clean_path(text: str) -> str:
    """A path typed or dragged into the window: drop surrounding quotes and spaces."""
    return text.strip().strip('"').strip("'").strip()


def heading(text: str) -> None:
    """A plain heading (used for the summary)."""
    print(f"\n{coloured(text, COLOUR_SECTION)}\n{'-' * len(text)}")
