# General Coding Style Guide

**MUST** marks rules that should almost always be followed (mainly formatting). **SHOULD** marks rules that may occasionally be broken. British English spelling is used throughout, except where an external API requires otherwise.

## 1. Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Variables | `snake_case` | `mean_intensity` |
| Boolean variables | `snake_case`, reads as a true/false statement | `is_valid`, `has_header`, `normalisation_enabled` |
| Constants | `UPPER_SNAKE_CASE` | `DEFAULT_DPI` |
| Classes | `PascalCase` | `SpectrumProcessor` |
| Enums | `PascalCase` class, `UPPER_SNAKE_CASE` members | `Unit.NANOMETRE` |
| Main / public functions and methods | `snake_case`, ending in `-er` or `-or` | `spectrum_loader()` |
| Private / helper functions and methods | `_snake_case`, starting with `_` and ending in `-er` or `-or` | `_spectrum_validator()` |
| Files / modules | `snake_case` | `spectrum_tools.py` |
| Strings | Use `''` not `""` (docstrings use `"""`) | `'text goes here'` |

- Function names start with the subject so related functions group together: `spectrum_calculator()`, `spectrum_loader()`.
- Dunder methods (e.g. `__init__`) are exempt from the `-er` / `-or` rule.
- Units SHOULD be part of the name when they are not obvious: `wavelength_nm`.

## 2. General Formatting

| Element | Rule |
|---|---|
| Indentation | 4 spaces per level |
| Maximum line length | 88 characters, comments included |
| Blank lines (top level) | 2 blank lines between top-level functions and classes |
| Blank lines (inside functions and classes) | None, except 1 after the docstring and 1 before each separator |
| Operators | Spaces around operators, e.g. `value = data / od` |
| Commas | One space after each comma |
| Multiline layouts | Calls, definitions, lists, dicts and tuples all follow section 3.1 |
| Trailing commas | Required after the final element in multiline calls, definitions and collections |
| Docstrings | `"""`, followed by 1 blank line before any code |
| Comments | SHOULD be rare; separators (sections 3.2 to 3.5) replace descriptive comments. Comments do not end in a full stop, unless they are full sentences such as a summary |

## 3. Function Formatting

### 3.1 Multiline Layouts

One element per line, aligned with the first element, trailing comma after the last. The closing delimiter MUST be on its own line, aligned with the elements.

```python
example_function(variable1,
                 variable2,
                 variable3,
                 )

def example_function(variable1: int,
                     variable2: int,
                     ) -> int:

settings = {'dpi': DEFAULT_DPI,
            'width': 6.0,
            }
```

### 3.2 Section Separators

Helper functions SHOULD be listed first, in logical groups (e.g. all decomposer helpers together), with the main functions last. Within each group, functions are sorted alphabetically. Each group starts with a group separator.

```python
# ---- DECOMPOSER HELPERS --------------------------------------------------------------


# ---- _SPECTRUM DECOMPOSER ------------------------------------------------------------
def _spectrum_decomposer(...) -> ...:
    ...


# ---- _SPECTRUM FITTER ----------------------------------------------------------------
def _spectrum_fitter(...) -> ...:
    ...


# ---- MAIN FUNCTIONS ------------------------------------------------------------------


# ---- EXPERIMENT PROCESSOR ------------------------------------------------------------
def experiment_processor(...) -> ...:
    ...
```

### 3.3 Function Separators

Place a separator directly above each `def`, using the function name in uppercase with underscores as spaces. Private functions keep their leading `_`.

```python
# ---- SPECTRUM LOADER -----------------------------------------------------------------
def spectrum_loader(file_path: Path) -> np.ndarray:
```

Adjust the trailing hyphens to keep the line at 88 characters.

### 3.4 Major Processing Stages

Separate major stages within a function using sequential numbering.

```python
    # ---- 1 Import and prepare data ---------------------------------------------------
    # ---- 2 Process data --------------------------------------------------------------
    # ---- 3 Export results ------------------------------------------------------------
```

Use `0` for initialisation when it forms a distinct, meaningful stage. Otherwise, begin at `1`.

### 3.5 Substeps

Use hierarchical numbering for meaningful substeps.

```python
    # ---- 1.1 Extract wavelength values -----------------------------------------------
    # ---- 1.2 Extract intensity values ------------------------------------------------
    # ---- 2.1 Apply normalisation -----------------------------------------------------
```

- Major stages use `1`, `2`, `3`, etc.
- Substeps use `1.1`, `1.2`, `2.1`, etc.
- Numbering restarts for each function.
- Number meaningful processing stages, not individual lines of code.

### 3.6 Type Annotations

All function inputs and return values MUST have type annotations.

```python
def spectrum_loader(file_path: Path) -> np.ndarray:
    ...
```

Type annotations describe expected types; they do not replace input validation or necessary type conversions.

### 3.7 Docstring Format

Every function MUST have a docstring using the following section order:

```python
def _spectrum_loader(file_path: Path) -> np.ndarray:
    """
    ---- Summary ----
    Helper function to load and return spectral data.

    ---- Inputs ----
    file_path : Path
        Path to the input file.

    ---- Globals read ----
    None.

    ---- Outputs ----
    np.ndarray
        Spectral data array, shape (n_wavelengths, n_timepoints).

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None.

    ---- Helpers ----
    None.
    """
```

**Docstring requirements:**

- **Summary:** One or two sentences stating whether the function is a main/public function or a helper, and what it does.
- **Inputs:** Names, types, expected formats, shapes, units and constraints.
- **Globals read:** Global variables, configuration values and external constants the function needs. The docstring MUST list everything the function needs beyond its arguments, so it can be understood and reused out of context.
- **Outputs:** Return type, structure, shape, units and meaning.
- **Globals mutated:** Global variables modified by the function.
- **Equations:** Equations used, with symbols and assumptions explained.
- **Helpers:** Helper functions used.

Use `None` explicitly for Globals read, Globals mutated, Equations or Helpers when nothing applies.

### 3.8 Function Structure

- Main/public functions SHOULD coordinate the workflow using clearly named helper functions.
- Helper functions SHOULD perform specific, well-defined operations.
- Functions SHOULD be divided into numbered stages and substeps where this improves readability.
- Inputs MUST be validated where invalid data could produce incorrect results. Invalid input MUST raise a specific exception (e.g. `ValueError`, `TypeError`) with a descriptive message; bare `except:` MUST NOT be used.
- Global state SHOULD be avoided where practical; dependencies SHOULD be passed as arguments.
- Functions that modify input objects or produce other side effects MUST document that behaviour in the outputs section.

### Example

```python
# ---- EXPERIMENT PROCESSOR ------------------------------------------------------------
def experiment_processor(experiment: dict) -> dict:
    """
    ---- Summary ----
    Main function to process an experiment's spectral data.

    ---- Inputs ----
    experiment : dict
        Experiment dictionary, as defined in DATA_FORMAT.md.

    ---- Globals read ----
    None.

    ---- Outputs ----
    dict
        Updated experiment dictionary containing processed spectra.

    ---- Globals mutated ----
    None.

    ---- Equations ----
    None. Processing equations are documented in the relevant helpers.

    ---- Helpers ----
    _spectrum_normaliser
    """

    # ---- 1 Retrieve input data -------------------------------------------------------
    spectra = experiment['spectra']

    # ---- 2 Process data --------------------------------------------------------------
    # ---- 2.1 Apply normalisation -----------------------------------------------------
    normalised_spectra = _spectrum_normaliser(spectra)

    # ---- 3 Store results -------------------------------------------------------------
    experiment['normalised_spectra'] = normalised_spectra

    return experiment
```

## 4. File Layout

Order within a Python file: imports, constants, helper groups, main functions.

```python
# ---- STANDARD IMPORTS ----------------------------------------------------------------
from pathlib import Path

# ---- 3RD PARTY IMPORTS ---------------------------------------------------------------
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ---- LOCAL IMPORTS -------------------------------------------------------------------
from spectrum_tools import spectrum_loader


# ---- CONSTANTS -----------------------------------------------------------------------
DEFAULT_DPI = 300
```

- Imports are split into standard library, third party and local sections, in that order, each under its own separator. Empty sections are omitted.
- Imports are sorted alphabetically within each section, with 1 blank line before each separator.
- Standard aliases: `np` (numpy), `pd` (pandas), `plt` (matplotlib.pyplot).
- Wildcard imports are permitted where needed.

## 5. Project Documentation

The project root MUST contain the following Markdown documents.

| File | Purpose |
|---|---|
| `README.md` | Project overview, installation instructions including relevant commands to download from GitHub, execution instructions, output |
| `FUNCTION_LIST.md` | Functions grouped by Python file, with concise summaries, inputs and outputs |
| `DATA_FORMAT.md` | Definitions of custom dictionaries, data structures, array shapes, units and formats |
| `CODING_STYLE.md` | The coding and formatting standards defined in this document |

The Python docstring is the primary technical definition of each function. `FUNCTION_LIST.md` provides a concise, organised index of those definitions.

Custom data structures MUST be documented in `DATA_FORMAT.md` rather than repeatedly redefined in individual function docstrings.

Documentation MUST be updated when the relevant code or data formats change.

## 6. C++ Notes

Sections 1 to 5 apply to C++ unless stated below. Comments use `//`.

| Element | Rule |
|---|---|
| Braces | Allman: opening brace on its own line |
| Separators | `// ----` banners, same width, naming and numbering as Python |
| Docstrings | Doxygen `/** ... */` block with the same section order, in the header beside the declaration |
| Includes | `// ---- STANDARD INCLUDES ----`, `// ---- 3RD PARTY INCLUDES ----`, `// ---- LOCAL INCLUDES ----` |
| Header guard | `#pragma once` |
| Namespaces | No `using namespace std;` |
| Constants | `constexpr`, `UPPER_SNAKE_CASE` |
| Private members and methods | `_snake_case` for class members; file-scope helpers go in an anonymous namespace (a leading `_` at global scope is reserved) |
| Pointers and references | Attached to the type: `int* value`, `int& value` |
| Multiline calls | One argument per line, aligned with the first; closing parenthesis follows the last argument (clang-format cannot place it on its own line) |
| Trailing commas | Only in braced initialiser lists and enums (invalid in calls and parameter lists) |
| Not applicable | Single-quote rule and type annotations |

V1.3 - 23/10/2026
