from __future__ import annotations

from pathlib import Path

from storage import get_config_dir

HANDOFF_FILE_NAME = ".last_target"


def get_handoff_file() -> Path:
    return get_config_dir() / HANDOFF_FILE_NAME


def write_target(path: Path) -> None:
    get_handoff_file().write_text(str(path), encoding="utf-8")
