# perfect-ascii

A Claude skill for creating perfectly aligned ASCII diagrams using a CLI-based rendering engine.

## How it works

Instead of asking the LLM to draw ASCII directly (which leads to character-counting errors), this skill splits the work:

- **SKILL.md** teaches Claude to describe diagrams as structured JSON
- **bin/ascii-render** is a Python CLI that takes that JSON and outputs pixel-perfect ASCII

Claude handles the creative/semantic decisions (what goes where), and the CLI handles precise character placement.

## Modes

- **diagram** — flowcharts, ER diagrams, state machines, block diagrams
- **table** — data grids, comparison matrices, with auto-split at 78 chars
- **layers** — layered architecture diagrams with bus connectors
- **sequence** — sequence diagrams with lifelines and message arrows

## Structure

```
SKILL.md              # Skill instructions for Claude
bin/ascii-render      # Python CLI renderer (stdin JSON → stdout ASCII)
bench/
  scenarios.md        # Benchmark prompts (v1)
  scenarios-v2.md     # Benchmark prompts (v2)
  render.html         # HTML template for monospace rendering
  eval-guide.md       # Evaluation scoring guide
```

## Usage

```bash
cat <<'EOF' | python3 bin/ascii-render
{"diagram": {"boxes": [{"id": "a", "label": "Hello"}, {"id": "b", "label": "World"}], "grid": [["a"], ["b"]], "connectors": [{"from": "a", "to": "b"}]}}
EOF
```
