---
name: perfect-ascii
description: "Create perfectly aligned ASCII diagrams. Use when the user asks for any ASCII art, diagram, flowchart, table, sequence diagram, architecture diagram, or visual representation using text characters. Triggers on: 'ascii diagram', 'text diagram', 'draw in ascii', 'ascii art', 'box diagram', or any request for a visual diagram that should be rendered in plain text."
license: MIT
version: "0.7.0"
last_updated: "2026-03-29"
user_invocable: true
---

# Perfect ASCII Diagrams

When asked for an ASCII diagram, use the `ascii-render` CLI tool. **Never draw ASCII manually** -- always produce JSON and let the CLI handle alignment, box borders, and connectors.

## Constraints

- **78-column max width** — the renderer errors if output exceeds this.
- **Rectangular boxes only** — no diamonds, circles, or other shapes.
- **Long labels may need shortening** — keep labels under ~15 chars to fit.

## Step 1: Choose a mode

- **Flowcharts, ER diagrams, block diagrams** -> `diagram` mode
- **Data tables, comparison grids** -> `table` mode
- **Layered architecture** -> `layers` mode
- **Sequence diagrams** -> `sequence` mode

## Step 2: Write the JSON input

### diagram mode

Describe boxes in a grid with connectors between them. Use `body` for multi-line boxes (ER diagrams).

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

- `grid`: 2D array of box IDs or `null` for empty cells. Each row is a horizontal layer.
- `connectors`: `from`/`to` with optional `label`. Same-column = vertical line, same-row = horizontal, different = L-shape elbow.
- `body`: optional list of strings for multi-line boxes (adds a separator between label and body).

### table mode

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

- `headers`: multi-row headers supported. Use `""` for blank placeholder cells.
- `align`: per-column (`left`, `right`, `center`).
- `separator_after`: row indices after which to draw a line. `-1` = after headers.
- **Cell spanning**: use `{"text": "...", "span": N}` instead of a plain string to span N columns.
- Auto-splits wide tables at 78 chars, repeating the first column.

#### Cell spanning example (packet header)

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

### layers mode

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
- `"connections": "between_layers"` auto-generates connectors using bus patterns (fan-out/fan-in).
- Layer labels appear on the left margin.

### sequence mode

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
- `messages`: each has `from`, `to`, `label`, and `style` (`"solid"` for requests `-->`, `"dashed"` for responses `- ->`).
- `notes`: optional boxed text between two actors. `after_message` is the 0-based message index after which to place the note.
- Lifelines are `|` characters; arrows are `-->` (solid) or `- ->` (dashed).

## Step 3: Render

```bash
cat <<'EOF' | python3 bin/ascii-render
{ ...your JSON... }
EOF
```

## Step 4: Present

Show the CLI output to the user in a fenced code block. Do not modify the output.

## Tips

- Keep labels short (< 15 chars). The CLI enforces 78-char max width.
- For decision points, use labels like `"Valid?"` and branch with labeled connectors.
- For ER diagrams, use `body` to list attributes.
- If the CLI errors, check your JSON structure matches the examples above.
- Place boxes intentionally in the grid -- `null` creates empty cells for spacing.
- Connectors that skip grid rows automatically route around intermediate boxes.
- For sequence diagrams, keep actor names short and limit to 4-5 actors to fit within 78 chars.
