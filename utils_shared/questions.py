# -*- coding: utf-8 -*-
"""Small helpers for asking questions in the terminal. Every question shows its default in [brackets]; Enter accepts it."""
import re
import sys


class UserQuit(Exception):
    """Raised when the input ends (window closed, Ctrl+Z / Ctrl+D) so the program can stop cleanly."""


def _read(prompt):
    try:
        return input(prompt).strip()
    except EOFError:
        raise UserQuit()


def heading(text):
    print(f"\n{text}\n{'-' * len(text)}")


def ask_text(question, default=None):
    suffix = f" [{default}]" if default not in (None, "") else ""
    answer = _read(f"{question}{suffix}: ")
    return answer if answer else default


def ask_yes_no(question, default=False):
    hint = "Y/n" if default else "y/N"
    while True:
        answer = _read(f"{question} ({hint}): ").lower()
        if not answer:
            return default
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("  Please answer y or n.")


def ask_number(question, default=None, minimum=None, maximum=None, exclusive_minimum=False, allow_blank=False):
    """A number; with ``allow_blank`` an empty answer gives None (when there is no default)."""
    suffix = f" [{default:g}]" if isinstance(default, (int, float)) else (" [Enter to skip]" if allow_blank else "")
    while True:
        answer = _read(f"{question}{suffix}: ").replace(",", ".")
        if not answer:
            if default is not None:
                return default
            if allow_blank:
                return None
            print("  A number is needed here.")
            continue
        try:
            value = float(answer)
        except ValueError:
            print("  That is not a number.")
            continue
        if minimum is not None and (value <= minimum if exclusive_minimum else value < minimum):
            print(f"  The value must be {'above' if exclusive_minimum else 'at least'} {minimum:g}.")
            continue
        if maximum is not None and value > maximum:
            print(f"  The value must be at most {maximum:g}.")
            continue
        return value


def ask_choice(question, options, default=None):
    """
    ``options`` is a list of (key, label). The user types the number; returns the key. ``default`` is a key.
    """
    print(question)
    for number, (_, label) in enumerate(options, start=1):
        print(f"  {number}) {label}")
    default_number = next((i for i, (key, _) in enumerate(options, start=1) if key == default), None)
    while True:
        suffix = f" [{default_number}]" if default_number else ""
        answer = _read(f"Choose 1-{len(options)}{suffix}: ")
        if not answer and default_number:
            return options[default_number - 1][0]
        if answer.isdigit() and 1 <= int(answer) <= len(options):
            return options[int(answer) - 1][0]
        print(f"  Please type a number from 1 to {len(options)}.")


def ask_multi(question, options, default_all=True):
    """Several of ``options`` (a list of labels): numbers separated by commas, or Enter for all. Returns the chosen labels."""
    print(question)
    for number, label in enumerate(options, start=1):
        print(f"  {number}) {label}")
    while True:
        answer = _read(f"Numbers separated by commas{' (Enter = all)' if default_all else ''}: ")
        if not answer and default_all:
            return list(options)
        picked = [p for p in re.split(r"[,\s]+", answer) if p]
        if picked and all(p.isdigit() and 1 <= int(p) <= len(options) for p in picked):
            return [options[i] for i in sorted({int(p) - 1 for p in picked})]
        print(f"  Please type numbers from 1 to {len(options)}, e.g. 1,3.")


def clean_path(text):
    """A path typed or dragged into the window: drop surrounding quotes and spaces."""
    return text.strip().strip('"').strip("'").strip()
