---
name: perfect-ascii
description: "Create perfectly aligned ASCII diagrams. Use when the user asks for any ASCII art, diagram, flowchart, table, sequence diagram, architecture diagram, or visual representation using text characters. Triggers on: 'ascii diagram', 'text diagram', 'draw in ascii', 'ascii art', 'box diagram', or any request for a visual diagram that should be rendered in plain text."
license: MIT
version: "0.1.0"
last_updated: "2026-03-29"
user_invocable: true
---

# Perfect ASCII Diagrams

When creating ASCII diagrams, follow these rules:

## Characters

Use these standard characters for structure:
- Horizontal lines: `-`
- Vertical lines: `|`
- Corners: `+`
- Arrows: `>`, `<`, `^`, `v`
- Dots for open connectors: `.`

## Boxes

Draw boxes with `+` at corners, `-` for horizontal edges, `|` for vertical edges:

```
+--------+
| Label  |
+--------+
```

## Alignment

- Count characters carefully to ensure vertical lines align across rows.
- Center text within boxes by padding with spaces on both sides.
- Keep consistent spacing between connected elements.

## Connectors

Connect boxes with `|` (vertical) and `-` (horizontal). Use `+` where lines change direction.

```
+-----+     +-----+
| A   |---->| B   |
+-----+     +-----+
```

## General

- Use a monospace mental model: every character is exactly one column wide.
- Before finalizing, mentally verify that all vertical lines in the same column share the same column index.
- Verify all horizontal lines in the same row span the correct columns.
