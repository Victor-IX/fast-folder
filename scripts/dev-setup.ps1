$ErrorActionPreference = "Stop"

$MarkerComment = "# fast-folder shell integration (dev)"
$Ps1Path = Join-Path $PSScriptRoot "ff.ps1"

$ProfilePath = $PROFILE
$ProfileDir = Split-Path -Parent $ProfilePath
if (-not (Test-Path $ProfileDir)) {
    New-Item -ItemType Directory -Path $ProfileDir -Force | Out-Null
}

$DotSourceLine = ". `"$Ps1Path`""
$Existing = if (Test-Path $ProfilePath) { Get-Content -LiteralPath $ProfilePath -Raw } else { "" }

if ($Existing -notlike "*$DotSourceLine*") {
    $Suffix = ""
    if ($Existing -and -not $Existing.EndsWith("`n")) {
        $Suffix = "`n"
    }
    Add-Content -LiteralPath $ProfilePath -Value "$Suffix`n$MarkerComment`n$DotSourceLine"
    Write-Host "Added shell integration to $ProfilePath"
}
else {
    Write-Host "Shell integration already present in $ProfilePath"
}

Write-Host "Dev setup complete."
Write-Host "Open a new PowerShell window (or run '. `$PROFILE') and 'ff' will be available."
