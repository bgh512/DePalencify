@echo off
rem Creates <project-folder-name>.zip in this folder containing only the relevant
rem project files. What is left out is listed at the top of the PowerShell part below.
rem Add the word nopause (make_zip.bat nopause) to skip the final pause.
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$s = Get-Content -Raw -LiteralPath '%~f0'; Invoke-Expression $s.Substring($s.IndexOf('#'+'PS#'))"
if /i not "%~1"=="nopause" pause
exit /b
#PS#
# ---- Settings you may want to edit ---------------------------------------------------
$excludedFolders = @('.git', '.venv', 'venv', 'build', '__pycache__', 'logs', 'style',
                     '.vscode', '.github', '.ruff_cache', '.pytest_cache', '.mypy_cache')
$excludedFiles = @('.clang-format', '.clang-tidy', '.style.yapf', 'ruff.toml',
                   'cspell.json', 'CLAUDE.md', '.gitignore', '.gitattributes',
                   '.gitmodules')
# Any folder whose name ends in _data is always left out as well

Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
$root = (Get-Location).Path
$name = Split-Path -Leaf $root
$zipPath = Join-Path $root "$name.zip"

# ---- 1 List the files ----------------------------------------------------------------
# Inside a git repository: tracked files plus new files that are not git-ignored.
$isRepo = $false
if (Get-Command git -ErrorAction SilentlyContinue) {
    git rev-parse --is-inside-work-tree 2>$null | Out-Null
    $isRepo = ($LASTEXITCODE -eq 0)
}
if ($isRepo) {
    $files = @(git -c core.quotepath=false ls-files --cached --others --exclude-standard)
} else {
    $files = @(Get-ChildItem -Recurse -File -Force | ForEach-Object {
        $_.FullName.Substring($root.Length + 1) -replace '\\', '/'
    })
}

# ---- 2 Drop the files that are not needed ---------------------------------------------
$kept = @()
foreach ($file in $files) {
    $parts = $file -split '/'
    $leaf = $parts[$parts.Count - 1]
    $skip = $false
    for ($i = 0; $i -lt $parts.Count - 1; $i++) {
        if ($excludedFolders -contains $parts[$i] -or $parts[$i] -like '*_data') {
            $skip = $true
        }
    }
    if ($excludedFiles -contains $leaf -or $leaf -eq "$name.zip" -or $leaf -like '*.pyc') {
        $skip = $true
    }
    if (-not $skip) { $kept += $file }
}
if ($kept.Count -eq 0) {
    Write-Host 'No files to zip.'
    exit 1
}

# ---- 3 Create the zip -----------------------------------------------------------------
if (Test-Path -LiteralPath $zipPath) { Remove-Item -LiteralPath $zipPath -Force }
$archive = [System.IO.Compression.ZipFile]::Open($zipPath, 'Create')
try {
    foreach ($file in $kept) {
        $full = Join-Path $root $file
        if (Test-Path -LiteralPath $full -PathType Leaf) {
            [void][System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile(
                $archive, $full, "$name/$file", 'Optimal')
        }
    }
} finally {
    $archive.Dispose()
}
$size = [math]::Round((Get-Item -LiteralPath $zipPath).Length / 1MB, 2)
Write-Host "Created $zipPath ($($kept.Count) files, $size MB)"
