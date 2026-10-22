# -*- coding: utf-8 -*-
"""Small, generic utilities shared by several modules (names, file names, Excel sheet names)."""
import re
from pathlib import Path


def simplify_name(value):
    """Lower-case and strip everything except letters/digits, so 'Cyt $c_1$' == 'cyt c1'."""
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def safe_file_name(name, default="experiment"):
    """Replace characters that are illegal in file names."""
    cleaned = re.sub(r'[<>:"/\\|?*]', "_", str(name)).strip()
    return cleaned or default


def excel_sheet_name(name, used):
    """
    Return a valid, unique Excel sheet name (<= 31 chars, no special characters)

    ``used`` is a set of lower-cased names already taken; it is updated in place.
    """
    base = re.sub(r"[\[\]:*?/\\]", "_", str(name)).strip("'") or "Data"
    base = base[:31]
    candidate, counter = base, 2
    while candidate.lower() in used:
        suffix = f"_{counter}"
        candidate = base[:31 - len(suffix)] + suffix
        counter += 1
    used.add(candidate.lower())
    return candidate


def save_figure_exact(fig, folder, stem, formats, size, dpi, tight=False):
    """
    Save ``fig`` as ``<folder>/<stem>.<ext>`` for each extension, at exactly ``size`` inches (width, height)

    Interactive (GUI) backends resize a figure to fit their window, which silently overwrites the requested figsize, and
    ``bbox_inches="tight"`` crops or grows the canvas around the artists. So the size is pinned again immediately before
    saving (``forward=False`` leaves any window alone) and tight cropping is off unless ``tight`` is True. The saved
    pixel size is then exactly ``size * dpi``, and an SVG is exactly ``size`` inches.
    """
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    fig.set_size_inches(*size, forward=False)
    paths = []
    for extension in formats:
        path = folder / f"{stem}.{extension}"
        fig.savefig(path, format=extension, dpi=dpi, **({"bbox_inches": "tight"} if tight else {}))
        paths.append(path)
    return paths
