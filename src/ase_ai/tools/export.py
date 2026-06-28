"""Tool: save_sprite — export an Aseprite sprite to an image file."""

import subprocess
import textwrap
from pathlib import Path

from ase_ai.config import ASEPRITE_PATH, LUA_TEMP_DIR


def save_sprite(sprite_path: str, output_path: str) -> str:
    """Export an Aseprite sprite to an image file (PNG, GIF, BMP, etc.).

    The output format is inferred from the file extension of *output_path*.

    Args:
        sprite_path: Absolute path to the source .aseprite file.
        output_path: Absolute path for the exported image (e.g. "C:/out/sprite.png").
    """
    sprite_path = str(Path(sprite_path).resolve()).replace("\\", "/")
    output_path = str(Path(output_path).resolve()).replace("\\", "/")

    lua = textwrap.dedent(f"""\
        local spr = Sprite{{fromFile="{sprite_path}"}}
        spr:saveCopyAs("{output_path}")
        app.exit()
    """)

    return _run_lua(lua, "save_sprite")


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
