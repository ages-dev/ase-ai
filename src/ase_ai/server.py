"""ase-ai MCP server — exposes Aseprite controls to Claude Desktop."""

from mcp.server.fastmcp import FastMCP

from ase_ai.config import ASEPRITE_PATH
from ase_ai.tools.canvas import new_canvas as _new_canvas
from ase_ai.tools.drawing import flood_fill as _flood_fill
from ase_ai.tools.drawing import paint_pixel as _paint_pixel
from ase_ai.tools.export import save_sprite as _save_sprite

mcp = FastMCP(
    "ase-ai",
    instructions=(
        "Controls Aseprite via Lua scripts. "
        "Always use absolute file paths. "
        f"Aseprite detected at: {ASEPRITE_PATH}"
    ),
)


@mcp.tool()
def new_canvas(
    width: int,
    height: int,
    output_path: str,
    color_mode: str = "rgb",
) -> str:
    """Create a new blank sprite and save it as an .aseprite file.

    Args:
        width: Canvas width in pixels (e.g. 64).
        height: Canvas height in pixels (e.g. 64).
        output_path: Absolute path where the sprite will be saved, e.g. "C:/sprites/hero.aseprite".
        color_mode: Color mode — "rgb" (default), "gray", or "indexed".
    """
    result = _new_canvas(width, height, output_path, color_mode)
    if result == "OK":
        return f"Canvas {width}x{height} created at {output_path}"
    return result


@mcp.tool()
def paint_pixel(
    sprite_path: str,
    x: int,
    y: int,
    r: int,
    g: int,
    b: int,
    a: int = 255,
) -> str:
    """Set a single pixel in an existing sprite to the given RGBA color.

    Args:
        sprite_path: Absolute path to the .aseprite file to edit.
        x: Column index of the pixel (0-based, from the left).
        y: Row index of the pixel (0-based, from the top).
        r: Red value 0-255.
        g: Green value 0-255.
        b: Blue value 0-255.
        a: Alpha value 0-255. Defaults to 255 (fully opaque).
    """
    result = _paint_pixel(sprite_path, x, y, r, g, b, a)
    if result == "OK":
        return f"Pixel ({x},{y}) set to rgba({r},{g},{b},{a}) in {sprite_path}"
    return result


@mcp.tool()
def flood_fill(
    sprite_path: str,
    x: int,
    y: int,
    r: int,
    g: int,
    b: int,
    a: int = 255,
) -> str:
    """Flood-fill an area from position (x, y) with the given RGBA color.

    Works like the paint-bucket tool: fills all contiguous pixels of the same color.

    Args:
        sprite_path: Absolute path to the .aseprite file to edit.
        x: Column to start filling from (0-based).
        y: Row to start filling from (0-based).
        r: Red value 0-255.
        g: Green value 0-255.
        b: Blue value 0-255.
        a: Alpha value 0-255. Defaults to 255 (fully opaque).
    """
    result = _flood_fill(sprite_path, x, y, r, g, b, a)
    if result == "OK":
        return f"Flood-filled from ({x},{y}) with rgba({r},{g},{b},{a}) in {sprite_path}"
    return result


@mcp.tool()
def save_sprite(sprite_path: str, output_path: str) -> str:
    """Export an Aseprite sprite to an image file.

    The output format is determined by the file extension (png, gif, bmp, jpg, webp, etc.).

    Args:
        sprite_path: Absolute path to the source .aseprite file.
        output_path: Absolute path for the exported image, e.g. "C:/output/hero.png".
    """
    result = _save_sprite(sprite_path, output_path)
    if result == "OK":
        return f"Sprite exported to {output_path}"
    return result


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
