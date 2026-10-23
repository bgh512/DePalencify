# General Coding Style Guide

(Copy of the project's CODING_STYLE.md; the project document is the master.)

## 1. Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Variables | `snake_case` | `mean_intensity` |
| Constants | `UPPER_SNAKE_CASE` | `DEFAULT_DPI` |
| Classes | `PascalCase` | `SpectrumProcessor` |
| Main / public functions | `snake_case`, ending in `-er` | `spectrum_loader()` |
| Private / helper functions | `_snake_case`, starting with `_` and ending in `-er` | `_spectrum_validator()` |
| Boolean variables | Clear, unambiguous names | `normalisation_enabled` |
| Strings | Use '' not " | 'text goes here' |

## 2. General Formatting

- 4 spaces per level; maximum line length 88; 2 blank lines between top-level functions.
- Spaces around operators; one space after each comma.
- Multiline arguments: one per line, aligned with the first argument, trailing comma, closing delimiter on its own line.

## 3. Functions

- Separator per function: `# ---- SPECTRUM LOADER ----...` (to 88 characters).
- Numbered stages `# ---- 1 Title ----`, substeps `# ---- 1.1 Title ----`, restarting in each function.
- All inputs and return values have type annotations; inputs are validated where bad data would give wrong results.
- Docstring sections, in order: Summary, Inputs, Globals read, Outputs, Globals mutated, Equations (`None.` when nothing applies).
- Public functions coordinate; helpers do one specific job. Side effects are documented.

## 4. Project Documentation

The project root contains README.md, FUNCTION_LIST.md, DATA_FORMAT.md and CODING_STYLE.md, and they are updated whenever the code or data formats change.
