"""Tools: paint_pixel, flood_fill — pixel drawing operations."""

import subprocess
import textwrap
from pathlib import Path

from ase_ai.config import ASEPRITE_PATH, LUA_TEMP_DIR


def paint_pixel(sprite_path: str, x: int, y: int, r: int, g: int, b: int, a: int = 255) -> str:
    """Set a single pixel in an existing sprite to an RGBA color.

    Args:
        sprite_path: Absolute path to the .aseprite file.
        x: Pixel column (0-based).
        y: Pixel row (0-based).
        r: Red channel 0-255.
        g: Green channel 0-255.
        b: Blue channel 0-255.
        a: Alpha channel 0-255. Defaults to 255 (fully opaque).
    """
    sprite_path = str(Path(sprite_path).resolve()).replace("\\", "/")

    lua = textwrap.dedent(f"""\
        local spr = Sprite{{fromFile="{sprite_path}"}}
        local image = spr.cels[1].image
        image:putPixel({x}, {y}, Color{{r={r}, g={g}, b={b}, a={a}}})
        spr:save()
        app.exit()
    """)

    return _run_lua(lua, "paint_pixel")


def flood_fill(sprite_path: str, x: int, y: int, r: int, g: int, b: int, a: int = 255) -> str:
    """Flood-fill an area starting at (x, y) with the given RGBA color.

    Uses Aseprite's paint-bucket tool internally, respecting contiguous pixel boundaries.

    Args:
        sprite_path: Absolute path to the .aseprite file.
        x: Starting column (0-based).
        y: Starting row (0-based).
        r: Red channel 0-255.
        g: Green channel 0-255.
        b: Blue channel 0-255.
        a: Alpha channel 0-255. Defaults to 255 (fully opaque).
    """
    sprite_path = str(Path(sprite_path).resolve()).replace("\\", "/")

    lua = textwrap.dedent(f"""\
        local spr = Sprite{{fromFile="{sprite_path}"}}
        app.activeSprite = spr
        local cel = spr.cels[1]
        app.useTool{{
            tool = "paint_bucket",
            color = Color{{r={r}, g={g}, b={b}, a={a}}},
            cel = cel,
            image = cel.image,
            points = {{Point({x}, {y})}}
        }}
        spr:save()
        app.exit()
    """)

    return _run_lua(lua, "flood_fill")


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
