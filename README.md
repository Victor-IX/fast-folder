# fast-folder
A simple CLI tool to navigate to saved locations faster.

## Requirements
- Windows with PowerShell

## Install
1. Download the latest `fast-folder-windows.zip` from the
   [Releases](../../releases) page and extract it somewhere permanent (e.g.
   `C:\Tools\fast-folder`).
2. Add the shell integration to your PowerShell profile so `ff` is available
   in every session. Add this line to your `$PROFILE`, pointing at the folder
   where you extracted the zip:

   ```powershell
   . "C:\Tools\fast-folder\ff.ps1"
   ```
3. Reload your profile (`. $PROFILE`) or open a new terminal.

`ff.ps1` looks for `fast-folder.exe` next to itself, so keep both files in
the same folder.

### Running from source (development)
If you'd rather run from a cloned copy of the repo, install
[uv](https://docs.astral.sh/uv/) and run `uv sync`. `scripts\ff.ps1` falls
back to `uv run --project <repo path>` whenever `fast-folder.exe` isn't
found next to it, so update `$ProjectPath` in that script to point at your
clone.

## Usage
```powershell
ff save <name>     # save the current directory under <name>
ff <name>          # jump to the directory saved as <name>
ff remove <name>   # remove a saved location
ff list             # list all saved locations
ff menu             # pick a saved location from an interactive menu
```

`save`, `remove`, `list`, `menu`, and `go` are reserved words and cannot be
used as location names.

Saved locations are stored in `%USERPROFILE%\.ff\locations.json`.

## Releasing
Pushing a tag matching `v*` (e.g. `v0.1.0`) triggers the `Release` GitHub
Actions workflow, which builds `fast-folder.exe` with PyInstaller and
publishes a `fast-folder-windows.zip` (exe + `ff.ps1` + docs) as a GitHub
Release.
