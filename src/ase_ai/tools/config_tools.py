"""Tools: set_default_folder, get_default_folder — manage the default save location."""

import json
from pathlib import Path

_CONFIG_FILE = Path(__file__).parent.parent.parent.parent / "ase_ai_config.json"


def _load() -> dict:
    if _CONFIG_FILE.exists():
        return json.loads(_CONFIG_FILE.read_text(encoding="utf-8"))
    return {}


def _save(data: dict) -> None:
    _CONFIG_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def set_default_folder(folder_path: str) -> str:
    """Set the default folder where new sprites are saved.

    Args:
        folder_path: Absolute path to the folder, e.g. "C:/Users/axel/Desktop/sprites"
    """
    path = Path(folder_path)
    path.mkdir(parents=True, exist_ok=True)
    data = _load()
    data["default_folder"] = str(path)
    _save(data)
    return f"Default folder set to: {path}"


def get_default_folder() -> str:
    """Return the current default save folder for sprites.

    Returns the configured folder, or the user's Desktop if none has been set.
    """
    data = _load()
    folder = data.get("default_folder")
    if folder and Path(folder).exists():
        return folder
    desktop = str(Path.home() / "Desktop")
    return f"{desktop} (default — use set_default_folder to change)"
