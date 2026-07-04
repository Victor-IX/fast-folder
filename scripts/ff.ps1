# fast-folder shell integration for PowerShell.

function ff {
    param(
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]]$Arguments
    )

    $ProjectPath = "H:\Projects\fast-folder"
    $HandoffFile = Join-Path $env:USERPROFILE ".ff\.last_target"

    if (Test-Path $HandoffFile) {
        Remove-Item $HandoffFile -Force
    }

    $ExePath = Join-Path $PSScriptRoot "fast-folder.exe"
    if (Test-Path $ExePath) {
        & $ExePath @Arguments
    }
    else {
        uv run --project $ProjectPath fast-folder @Arguments
    }

    if (Test-Path $HandoffFile) {
        $target = (Get-Content $HandoffFile -Raw).Trim()
        Remove-Item $HandoffFile -Force
        if ($target) {
            Set-Location -LiteralPath $target
        }
    }
}
