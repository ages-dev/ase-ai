"""Tools: paint_pixel, flood_fill, draw_pixels_batch, read_canvas."""

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
        spr:saveAs(spr.filename)
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
        spr:saveAs(spr.filename)
        app.exit()
    """)

    return _run_lua(lua, "flood_fill")


def draw_pixels_batch(sprite_path: str, pixels: list[dict]) -> str:
    """Draw many pixels in a single Aseprite call — efficient for drawing characters or shapes.

    All pixels are written in one Lua script execution, regardless of count.

    Args:
        sprite_path: Absolute path to the .aseprite file.
        pixels: List of pixel dicts, each with keys x, y, r, g, b (ints 0-255) and optional a (alpha, default 255).
                Example: [{"x": 5, "y": 3, "r": 255, "g": 0, "b": 0}, {"x": 6, "y": 3, "r": 0, "g": 255, "b": 0}]
    """
    sprite_path_lua = str(Path(sprite_path).resolve()).replace("\\", "/")

    put_calls = "\n".join(
        f"image:putPixel({int(p['x'])}, {int(p['y'])}, "
        f"Color{{r={int(p['r'])}, g={int(p['g'])}, b={int(p['b'])}, a={int(p.get('a', 255))}}})"
        for p in pixels
    )

    lua = textwrap.dedent(f"""\
        local spr = Sprite{{fromFile="{sprite_path_lua}"}}
        local image = spr.cels[1].image
        {put_calls}
        spr:saveAs(spr.filename)
        app.exit()
    """)

    result = _run_lua(lua, "draw_pixels_batch")
    if result == "OK":
        return f"Drew {len(pixels)} pixels in {sprite_path}"
    return result


def read_canvas(sprite_path: str, x1: int, y1: int, x2: int, y2: int) -> str:
    """Read pixel data from a rectangular area of a sprite.

    Returns a compact representation of the pixel colors so Claude can see what has been drawn
    and iterate on it. Transparent pixels are shown as '..', colored pixels as their hex value.

    Args:
        sprite_path: Absolute path to the .aseprite file.
        x1: Left column of the area to read (0-based, inclusive).
        y1: Top row of the area to read (0-based, inclusive).
        x2: Right column (inclusive).
        y2: Bottom row (inclusive).
    """
    sprite_path_lua = str(Path(sprite_path).resolve()).replace("\\", "/")
    output_file = LUA_TEMP_DIR / "read_canvas_output.txt"
    output_file_lua = str(output_file).replace("\\", "/")

    lua = textwrap.dedent(f"""\
        local spr = Sprite{{fromFile="{sprite_path_lua}"}}
        local image = spr.cels[1].image
        local lines = {{}}
        for y = {y1}, {y2} do
            for x = {x1}, {x2} do
                local c = image:getPixel(x, y)
                local r = app.pixelColor.rgbaR(c)
                local g = app.pixelColor.rgbaG(c)
                local b = app.pixelColor.rgbaB(c)
                local a = app.pixelColor.rgbaA(c)
                table.insert(lines, x..","..y..","..r..","..g..","..b..","..a)
            end
        end
        local f = io.open("{output_file_lua}", "w")
        f:write(table.concat(lines, "\\n"))
        f:close()
        app.exit()
    """)

    run_result = _run_lua(lua, "read_canvas")
    if run_result != "OK":
        return run_result

    if not output_file.exists():
        return "Error: Aseprite produced no output"

    raw = output_file.read_text(encoding="utf-8").strip()
    output_file.unlink(missing_ok=True)

    width = x2 - x1 + 1
    height = y2 - y1 + 1

    # Parse pixels
    pixel_map: dict[tuple[int, int], tuple[int, int, int, int]] = {}
    for line in raw.split("\n"):
        if not line:
            continue
        px, py, r, g, b, a = (int(v) for v in line.split(","))
        pixel_map[(px, py)] = (r, g, b, a)

    lines = [f"Canvas area ({x1},{y1})→({x2},{y2})  {width}×{height} pixels"]

    # Visual grid (shape only) — dots for empty, # for any colored pixel
    grid_lines = []
    for y in range(y1, y2 + 1):
        row = ""
        for x in range(x1, x2 + 1):
            r, g, b, a = pixel_map.get((x, y), (0, 0, 0, 0))
            row += "." if a == 0 else "#"
        grid_lines.append(row)
    lines.append("Shape (# = colored, . = transparent):")
    lines.extend(grid_lines)

    # Colored pixels list
    colored = [(x, y, r, g, b, a) for (x, y), (r, g, b, a) in pixel_map.items() if a > 0]
    lines.append(f"\n{len(colored)} colored pixels:")
    for x, y, r, g, b, a in sorted(colored, key=lambda p: (p[1], p[0]))[:150]:
        lines.append(f"  ({x},{y}) #{r:02X}{g:02X}{b:02X}" + (f" a={a}" if a < 255 else ""))
    if len(colored) > 150:
        lines.append(f"  … and {len(colored) - 150} more")

    return "\n".join(lines)


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
