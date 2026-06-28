"""Aseprite path detection and runtime configuration."""

import os
from pathlib import Path

_STEAM_CANDIDATES = [
    r"C:\Program Files (x86)\Steam\steamapps\common\Aseprite\Aseprite.exe",
    r"C:\Program Files\Steam\steamapps\common\Aseprite\Aseprite.exe",
    str(Path.home() / "AppData/Local/Steam/steamapps/common/Aseprite/Aseprite.exe"),
    "/Applications/Aseprite.app/Contents/MacOS/aseprite",
    "/usr/bin/aseprite",
    "/usr/local/bin/aseprite",
]


def find_aseprite() -> str:
    """Return the path to the Aseprite executable.

    Priority: ASEPRITE_PATH env var → known Steam/OS locations → 'aseprite' (PATH fallback).
    """
    if env := os.environ.get("ASEPRITE_PATH"):
        return env
    for candidate in _STEAM_CANDIDATES:
        if Path(candidate).exists():
            return candidate
    return "aseprite"


ASEPRITE_PATH: str = find_aseprite()

# Folder where temporary Lua scripts are written before execution
LUA_TEMP_DIR: Path = Path(__file__).parent.parent.parent / "lua_scripts"
LUA_TEMP_DIR.mkdir(exist_ok=True)
