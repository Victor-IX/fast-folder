from __future__ import annotations

import ctypes
import os
import shutil
import subprocess
import sys
from pathlib import Path

INSTALL_DIR_NAME = "fast-folder"
EXE_NAME = "fast-folder.exe"
SHELL_SCRIPT_NAME = "ff.ps1"
MARKER_COMMENT = "# fast-folder shell integration"


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def get_bundled_ps1_path() -> Path | None:
    """Path to ff.ps1 packaged alongside the code"""
    if is_frozen():
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            candidate = Path(meipass) / SHELL_SCRIPT_NAME
            if candidate.exists():
                return candidate
        return None

    candidate = Path(__file__).resolve().parent.parent / "scripts" / SHELL_SCRIPT_NAME
    return candidate if candidate.exists() else None


def is_launched_by_double_click() -> bool:
    try:
        kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
        buffer = (ctypes.c_uint * 4)()
        count = kernel32.GetConsoleProcessList(buffer, len(buffer))
    except (AttributeError, OSError):
        return False
    return count <= 1


def get_install_dir() -> Path:
    base = Path(os.environ.get("LOCALAPPDATA", str(Path.home())))
    return base / INSTALL_DIR_NAME


def get_profile_path() -> Path:
    """Ask PowerShell for the current user's $PROFILE path"""
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", "$PROFILE"],
            capture_output=True,
            text=True,
            check=True,
        )
        value = result.stdout.strip()
        if value:
            return Path(value)
    except (OSError, subprocess.SubprocessError):
        pass
    return Path.home() / "Documents" / "WindowsPowerShell" / "Microsoft.PowerShell_profile.ps1"


def install() -> None:
    """Copy the exe + ff.ps1 to a permanent folder and wire up $PROFILE."""
    print("Installing fast-folder...")

    source_dir = Path(sys.executable).resolve().parent if is_frozen() else Path(__file__).resolve().parent
    target_dir = get_install_dir()
    target_dir.mkdir(parents=True, exist_ok=True)

    target_exe = target_dir / EXE_NAME
    if is_frozen():
        source_exe = Path(sys.executable).resolve()
        if source_exe != target_exe:
            shutil.copy2(source_exe, target_exe)

    target_ps1 = target_dir / SHELL_SCRIPT_NAME
    source_ps1 = source_dir / SHELL_SCRIPT_NAME
    if source_ps1.exists() and source_ps1 != target_ps1:
        shutil.copy2(source_ps1, target_ps1)
    else:
        bundled_ps1 = get_bundled_ps1_path()
        if bundled_ps1 is not None:
            shutil.copy2(bundled_ps1, target_ps1)
        elif not target_ps1.exists():
            print(
                "Warning: could not find ff.ps1 next to the executable or bundled inside it; "
                "shell integration will be incomplete.",
                file=sys.stderr,
            )

    profile_path = get_profile_path()
    profile_path.parent.mkdir(parents=True, exist_ok=True)
    dot_source_line = f'. "{target_ps1}"'
    existing = profile_path.read_text(encoding="utf-8") if profile_path.exists() else ""

    if dot_source_line not in existing:
        with profile_path.open("a", encoding="utf-8") as handle:
            if existing and not existing.endswith("\n"):
                handle.write("\n")
            handle.write(f"\n{MARKER_COMMENT}\n{dot_source_line}\n")
        print(f"Added shell integration to {profile_path}")
    else:
        print(f"Shell integration already present in {profile_path}")

    print(f"Installed fast-folder to {target_dir}")
    print("Open a new PowerShell window (or run '. $PROFILE') and 'ff' will be available.")
