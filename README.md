# fast-folder
A simple CLI tool to navigate to saved locations faster.

## Requirements
- Windows with PowerShell

## Install
1. Download the latest `fast-folder-windows.zip` from the
   [Releases](../../releases) page and extract it (anywhere, even a Downloads
   folder).
2. Double-click `fast-folder.exe`. It copies itself and `ff.ps1` to
   `%LOCALAPPDATA%\fast-folder` and adds the dot-source line to your
   `$PROFILE` automatically.
3. Open a new PowerShell window (or run `. $PROFILE`) and `ff` is available.

### Running from source (development)
If you'd rather run from a cloned copy of the repo, set up the Python
environment first — [uv](https://docs.astral.sh/uv/) is recommended
(`uv sync`), but any package manager works as long as `fast-folder` is
runnable, since `scripts\ff.ps1` falls back to
`uv run --project <repo path> fast-folder` when no `fast-folder.exe` sits
next to it.

Then run the setup script from the repo root to wire up your `$PROFILE`:

```powershell
.\scripts\dev-setup.ps1
```

It adds the dot-source line for `scripts\ff.ps1` to your `$PROFILE`. Open a
new PowerShell window (or run `. $PROFILE`) and `ff` is available.

## Usage
```powershell
ff save <name>     # save the current directory under <name>
ff <name>          # jump to the directory saved as <name>
ff go <name>       # jump to the directory saved as <name> (explicit form)
ff remove <name>   # remove a saved location
ff list             # list all saved locations
ff menu             # pick a saved location from an interactive menu
ff install          # copy fast-folder to a permanent location and wire up your PowerShell profile
```

`save`, `remove`, `list`, `menu`, `go`, and `install` are reserved words and
cannot be used as location names.

Saved locations are stored in `%USERPROFILE%\.ff\locations.json`.
