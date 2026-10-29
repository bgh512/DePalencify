@echo off
rem Zips the relevant project files into <project-folder-name>.zip.
rem Edit the two lists below to change what is left out.
setlocal
set "SKIP_FOLDERS=style .vscode .venv .venv_unix build logs"
set "SKIP_FILES=.gitignore .gitattributes .gitmodules CLAUDE.md ruff.toml cspell.json last_answers.json"

cd /d "%~dp0"
for %%I in ("%CD%") do set "NAME=%%~nxI"
set "LIST=%TEMP%\%NAME%_zip_list.txt"
if exist "%NAME%.zip" del "%NAME%.zip"

rem List what git tracks or would track, minus the lists above and any *_data folder.
powershell -NoProfile -Command "$f = $env:SKIP_FOLDERS -split ' '; $s = $env:SKIP_FILES -split ' '; git ls-files --cached --others --exclude-standard | Where-Object { $p = $_ -split '/'; -not ($f -contains $p[0]) -and -not ($s -contains $p[-1]) -and -not ($p[0] -like '*_data') } | Set-Content -Encoding ASCII '%LIST%'"
if errorlevel 1 goto :failed

tar -a -c -f "%NAME%.zip" -T "%LIST%"
if errorlevel 1 goto :failed
del "%LIST%"
echo Created %NAME%.zip
exit /b 0

:failed
echo Could not create the zip. Git must be installed and this folder must be a git repository.
exit /b 1
