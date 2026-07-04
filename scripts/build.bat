@echo off
REM Build a standalone fast-folder.exe using PyInstaller via uv.
REM Usage: scripts\build.bat  (run from the repository root)

setlocal

set "SCRIPT_DIR=%~dp0"
set "REPO_ROOT=%SCRIPT_DIR%.."

pushd "%REPO_ROOT%" || exit /b 1

echo Building fast-folder standalone executable...
uv run pyinstaller --onefile --name fast-folder --paths src --add-data "scripts\ff.ps1;." src\cli.py
if errorlevel 1 (
    echo Build failed.
    popd
    exit /b 1
)

echo Build succeeded: dist\fast-folder.exe
popd
exit /b 0
