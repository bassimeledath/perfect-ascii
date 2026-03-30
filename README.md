# perfect-ascii

MCP server for rendering perfectly aligned ASCII diagrams.

## What it does

Exposes a `render_ascii` tool that takes structured JSON and returns pixel-perfect ASCII art. Supports flowcharts, tables, architecture diagrams, and sequence diagrams.

LLMs can't count characters. This tool handles precise alignment so the LLM only needs to describe *what* to draw, not *how* to draw it.

## Install

### Claude Desktop

```bash
git clone https://github.com/bassimehdi/perfect-ascii.git
cd perfect-ascii
pip install .
```

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "perfect-ascii": {
      "command": "perfect-ascii"
    }
  }
}
```

Restart Claude Desktop.

### Claude Code

```bash
claude mcp add perfect-ascii -- perfect-ascii
```

Or with uv (no install needed):

```bash
claude mcp add perfect-ascii -- uv run --directory /path/to/perfect-ascii python server.py
```

## Tool Reference

### `render_ascii`

**Input:** `json_input` (string) — JSON describing the diagram.

The JSON must contain exactly one top-level key that selects the mode:

| Key | Use for |
|-----|---------|
| `diagram` | Flowcharts, ER diagrams, state machines, block diagrams |
| `table` | Data grids, comparison matrices (auto-splits at 78 chars) |
| `layers` | Layered architecture diagrams with bus connectors |
| `sequence` | Sequence diagrams with lifelines and message arrows |

**Output:** Plain text ASCII diagram, or an error message.

**Constraints:** 78-column max width, rectangular boxes only, labels under ~15 chars.

See the full tool docstring in `server.py` for detailed JSON format documentation and examples for each mode.

## Development

Run the rendering engine directly:

```bash
cat <<'EOF' | python3 bin/ascii-render
{"diagram": {"boxes": [{"id": "a", "label": "Hello"}, {"id": "b", "label": "World"}], "grid": [["a"], ["b"]], "connectors": [{"from": "a", "to": "b"}]}}
EOF
```

Run benchmarks — see `bench/eval-guide.md`.

## License

MIT
