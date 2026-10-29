# DePalencify

Follow the project style guide:

@style/CODING_STYLE.md

- Entry point: `main.py`. Launchers: `run.bat`, `run.command`, `run.sh`.
- After changing code, run the shared tools from `style/tools/`: the banner formatter,
  then the function list generator (`FUNCTION_LIST.md`).
- Keep `README.md`, `FUNCTION_LIST.md` and `DATA_FORMAT.md` in step with the code.
- The program has no automated tests; check a change by running it on a few `.paf`
  files and opening the exported workbooks.
