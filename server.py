#!/usr/bin/env python3
"""perfect-ascii MCP server — pixel-perfect ASCII diagrams via structured JSON."""

import json
import subprocess
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("perfect-ascii")

# Locate the rendering engine relative to this file
RENDER_SCRIPT = str(Path(__file__).parent / "bin" / "ascii-render")


@mcp.tool()
def render_ascii(json_input: str) -> str:
    """Render a perfectly aligned ASCII diagram from structured JSON.

    Takes a JSON string and returns pixel-perfect ASCII art. The JSON must
    contain exactly one top-level key that selects the rendering mode:

    - "diagram" — flowcharts, ER diagrams, state machines, block diagrams
    - "table"   — data grids, comparison matrices (auto-splits at 78 chars)
    - "layers"  — layered architecture diagrams with bus connectors
    - "sequence" — sequence diagrams with lifelines and message arrows

    ## Constraints

    - **78-column max width** — the renderer errors if output exceeds this.
    - **Rectangular boxes only** — no diamonds, circles, or other shapes.
    - **Keep labels short** (under ~15 chars) to fit within width limits.

    ## diagram mode

    Describe boxes in a grid with connectors between them. Use `body` for
    multi-line boxes (e.g. ER diagrams with attribute lists).

    ```json
    {
      "diagram": {
        "title": "Login Flow",
        "boxes": [
          {"id": "start", "label": "Start"},
          {"id": "creds", "label": "Enter Credentials"},
          {"id": "valid", "label": "Valid?"},
          {"id": "ok", "label": "Grant Access"},
          {"id": "fail", "label": "Lock Account"}
        ],
        "grid": [
          ["start"],
          ["creds"],
          ["valid"],
          ["ok", null, "fail"]
        ],
        "connectors": [
          {"from": "start", "to": "creds"},
          {"from": "creds", "to": "valid"},
          {"from": "valid", "to": "ok", "label": "yes"},
          {"from": "valid", "to": "fail", "label": "no"}
        ]
      }
    }
    ```

    - `grid`: 2D array of box IDs or `null` for empty cells. Each row is a
      horizontal layer.
    - `connectors`: `from`/`to` with optional `label`. Same-column = vertical
      line, same-row = horizontal, different = L-shape elbow.
    - `body`: optional list of strings for multi-line boxes (adds a separator
      between label and body).
    - `lanes`: optional list of row labels (e.g. branch names). Adds left-margin
      labels like layers mode.

    ### Lane-labeled diagrams (git graphs, pipelines)

    ```json
    {
      "diagram": {
        "lanes": ["main", "feature"],
        "boxes": [
          {"id": "m1", "label": "v1.0"},
          {"id": "m2", "label": "v1.1"},
          {"id": "f1", "label": "auth"},
          {"id": "f2", "label": "tests"}
        ],
        "grid": [
          ["m1", null, "m2"],
          [null, "f1", "f2"]
        ],
        "connectors": [
          {"from": "m1", "to": "m2"},
          {"from": "m1", "to": "f1", "label": "branch"},
          {"from": "f1", "to": "f2"},
          {"from": "f2", "to": "m2", "label": "merge"}
        ]
      }
    }
    ```

    ## table mode

    ```json
    {
      "table": {
        "headers": [
          ["Region", "Q1 2025", "", "Q2 2025", "", "Annual"],
          ["", "Rev", "Growth", "Rev", "Growth", "Total"]
        ],
        "align": ["left", "right", "right", "right", "right", "right"],
        "rows": [
          ["North", "$1.2M", "+12%", "$1.4M", "+15%", "$2.6M"],
          ["South", "$890K", "+5%", "$920K", "+3%", "$1.8M"]
        ],
        "separator_after": [-1],
        "footer": ["Total", "$2.1M", "", "$2.3M", "", "$4.4M"]
      }
    }
    ```

    - `headers`: multi-row headers supported. Use `""` for blank cells.
    - `align`: per-column (`left`, `right`, `center`).
    - `separator_after`: row indices after which to draw a line. `-1` = after
      headers.
    - **Cell spanning**: use `{"text": "...", "span": N}` instead of a plain
      string to span N columns.
    - Auto-splits wide tables at 78 chars, repeating the first column.

    ### Cell spanning example (packet header)

    ```json
    {
      "table": {
        "align": ["center", "center", "center", "center"],
        "rows": [
          ["Version", "IHL", "Type of Svc", "Total Length"],
          [{"text": "Identification", "span": 2}, "Flags", "Frag Offset"],
          ["TTL", "Protocol", {"text": "Header Checksum", "span": 2}],
          [{"text": "Source IP Address", "span": 4}],
          [{"text": "Destination IP Address", "span": 4}]
        ],
        "separator_after": [0, 1, 2, 3]
      }
    }
    ```

    ## layers mode

    Shortcut for layered architecture diagrams with automatic connectors.

    ```json
    {
      "layers": {
        "title": "System Architecture",
        "levels": [
          {"label": "Presentation", "boxes": ["Web App", "Mobile", "CLI"]},
          {"label": "API", "boxes": ["API Gateway"]},
          {"label": "Services", "boxes": ["Auth", "Orders", "Inventory"]},
          {"label": "Data", "boxes": ["PostgreSQL", "Redis", "S3"]}
        ],
        "connections": "between_layers"
      }
    }
    ```

    - Each level becomes a centered row of boxes.
    - `"connections": "between_layers"` auto-generates connectors using bus
      patterns (fan-out/fan-in).
    - Layer labels appear on the left margin.

    ## sequence mode

    Sequence diagrams with actors, lifelines, message arrows, and notes.

    ```json
    {
      "sequence": {
        "actors": ["User", "Frontend", "API Server", "Database"],
        "messages": [
          {"from": "User", "to": "Frontend", "label": "Click checkout", "style": "solid"},
          {"from": "Frontend", "to": "API Server", "label": "POST /checkout", "style": "solid"},
          {"from": "API Server", "to": "Database", "label": "INSERT order", "style": "solid"},
          {"from": "Database", "to": "API Server", "label": "OK", "style": "dashed"},
          {"from": "API Server", "to": "Frontend", "label": "200 OK", "style": "dashed"}
        ],
        "notes": [
          {"between": ["Frontend", "API Server"], "text": "Timeout after 30s", "after_message": 1}
        ]
      }
    }
    ```

    - `actors`: ordered list of participant names (left to right).
    - `messages`: each has `from`, `to`, `label`, and `style` (`"solid"` for
      requests `-->`, `"dashed"` for responses `- ->`).
    - `notes`: optional boxed text between two actors. `after_message` is the
      0-based message index after which to place the note.
    - Lifelines are `|` characters; arrows are `-->` (solid) or `- ->` (dashed).

    ## Tips

    - Keep labels short (< 15 chars). The renderer enforces 78-char max width.
    - For decision points, use labels like "Valid?" and branch with labeled
      connectors.
    - For ER diagrams, use `body` to list attributes.
    - If the renderer errors, check your JSON structure matches the examples.
    - Place boxes intentionally in the grid — `null` creates empty cells for
      spacing.
    - Connectors that skip grid rows automatically route around intermediate
      boxes.
    - For sequence diagrams, keep actor names short and limit to 4-5 actors to
      fit within 78 chars.

    Args:
        json_input: JSON string describing the diagram. Must contain exactly one
            top-level key: 'diagram', 'table', 'layers', or 'sequence'.

    Returns:
        The rendered ASCII diagram as plain text, or an error message string.
    """
    # Validate JSON before passing to renderer
    try:
        data = json.loads(json_input)
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON: {e}"

    # Validate mode key
    valid_keys = {"diagram", "table", "layers", "sequence"}
    found = valid_keys & set(data.keys())
    if not found:
        return "Error: JSON must contain one of: 'diagram', 'table', 'layers', 'sequence'"

    # Call the rendering engine
    try:
        result = subprocess.run(
            [sys.executable, RENDER_SCRIPT],
            input=json_input,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return f"Error: {result.stderr.strip()}"
        return result.stdout.rstrip()
    except subprocess.TimeoutExpired:
        return "Error: Rendering timed out (>10s)"
    except Exception as e:
        return f"Error: {e}"


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
