# ase-ai

An MCP server that lets Claude Desktop control [Aseprite](https://www.aseprite.org/) via Lua scripts.

Each tool generates a temporary Lua script and executes it through Aseprite's `--batch --script` interface.

## Tools

| Tool | Description |
|------|-------------|
| `new_canvas` | Create a new sprite with given dimensions and color mode |
| `paint_pixel` | Set a single pixel to an RGB color |
| `flood_fill` | Flood-fill an area from a starting point |
| `save_sprite` | Export a sprite to PNG, GIF, or other formats |

## Requirements

- Python 3.11+
- [Aseprite](https://www.aseprite.org/) (Steam or standalone)
- [Claude Desktop](https://claude.ai/download)

## Installation

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/ase-ai.git
cd ase-ai

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -e .
```

## Configuration

By default, ase-ai looks for Aseprite at these paths (Windows):
- `C:\Program Files (x86)\Steam\steamapps\common\Aseprite\Aseprite.exe`
- `C:\Program Files\Steam\steamapps\common\Aseprite\Aseprite.exe`

Override with an environment variable if needed:
```bash
set ASEPRITE_PATH=C:\path\to\Aseprite.exe
```

## Claude Desktop Setup

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ase-ai": {
      "command": "python",
      "args": ["-m", "ase_ai.server"],
      "env": {
        "PYTHONPATH": "C:\\path\\to\\ase-ai\\src"
      }
    }
  }
}
```

Or if installed via pip:
```json
{
  "mcpServers": {
    "ase-ai": {
      "command": "ase-ai"
    }
  }
}
```

## Example prompts for Claude

> "Create a 64x64 pixel art canvas"

> "Paint pixel at (10, 20) with color red (255, 0, 0)"

> "Fill the background with color #1a1a2e"

> "Export the sprite to desktop as PNG"
