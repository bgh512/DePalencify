# Creates DePalencify shortcuts (Desktop and Start menu) pointing at run.bat. Called by run.bat the first time it runs.
param([string]$Folder)
try {
    $target = Join-Path $Folder 'run.bat'
    $icon = Join-Path $Folder 'assets\icon.ico'
    $shell = New-Object -ComObject WScript.Shell
    foreach ($place in @([Environment]::GetFolderPath('Desktop'), [Environment]::GetFolderPath('Programs'))) {
        if (-not $place -or -not (Test-Path $place)) { continue }
        $link = $shell.CreateShortcut((Join-Path $place 'DePalencify.lnk'))
        $link.TargetPath = $target
        $link.WorkingDirectory = $Folder
        $link.IconLocation = "$icon,0"
        $link.Description = 'DePalencify: convert chamber .paf files to figures and data'
        $link.Save()
    }
    [IO.File]::WriteAllText((Join-Path $Folder '.shortcut_made'), $Folder, (New-Object Text.UTF8Encoding $false))
    Write-Host 'Created a DePalencify icon on your Desktop and in the Start menu.'
} catch {
    # A missing shortcut must never stop the program from starting.
}
