"""Tool: new_canvas — create a new Aseprite sprite."""

import subprocess
import tempfile
import textwrap
from pathlib import Path

from ase_ai.config import ASEPRITE_PATH, LUA_TEMP_DIR


def new_canvas(width: int, height: int, output_path: str, color_mode: str = "rgb") -> str:
    """Create a new blank sprite and save it to *output_path*.

    Args:
        width: Canvas width in pixels.
        height: Canvas height in pixels.
        output_path: Where to save the .aseprite file (absolute path).
        color_mode: One of "rgb", "gray", or "indexed". Defaults to "rgb".
    """
    mode_map = {"rgb": "ColorMode.RGB", "gray": "ColorMode.GRAYSCALE", "indexed": "ColorMode.INDEXED"}
    lua_mode = mode_map.get(color_mode.lower(), "ColorMode.RGB")
    output_path = str(Path(output_path).resolve()).replace("\\", "/")

    lua = textwrap.dedent(f"""\
        local spr = Sprite({width}, {height}, {lua_mode})
        spr:saveAs("{output_path}")
        app.exit()
    """)

    return _run_lua(lua, "new_canvas")


def _run_lua(script: str, tag: str) -> str:
    lua_file = LUA_TEMP_DIR / f"{tag}.lua"
    lua_file.write_text(script, encoding="utf-8")
    try:
        result = subprocess.run(
            [ASEPRITE_PATH, "--batch", "--script", str(lua_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return f"Error: {result.stderr.strip() or result.stdout.strip()}"
        return "OK"
    except FileNotFoundError:
        return f"Aseprite not found at: {ASEPRITE_PATH}"
    except subprocess.TimeoutExpired:
        return "Error: Aseprite timed out after 30 seconds"
    finally:
        lua_file.unlink(missing_ok=True)
