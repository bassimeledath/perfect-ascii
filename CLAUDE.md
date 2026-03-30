# perfect-ascii

MCP server for rendering perfectly aligned ASCII diagrams.

## Project structure

- `server.py` — MCP server entry point. The `render_ascii` tool docstring contains all mode documentation (replaces the old SKILL.md).
- `pyproject.toml` — package metadata, dependencies, and `perfect-ascii` script entry point.
- `bin/ascii-render` — the rendering engine (pure Python, reads JSON from stdin, writes ASCII to stdout). **Do not refactor** — `server.py` calls it via subprocess.
- `bench/scenarios.md` — benchmark prompts. **Read-only** during swarmy runs.
- `bench/render.html` — HTML template for rendering ASCII as monospace image. **Read-only**.
- `bench/eval-guide.md` — tester agent instructions. **Read-only**.
- `bench/output/` — scratch space for generated HTML/screenshots. Gitignored.

## Eval flow (for tester agents)

1. Read the `render_ascii` tool docstring in `server.py` to understand the current technique
2. For each scenario in bench/scenarios.md, generate an ASCII diagram following the tool docs
3. Wrap each diagram in bench/render.html template, write to bench/output/
4. Open each in Chrome DevTools, screenshot it
5. Analyze each screenshot for misalignment issues
6. Produce a score per scenario and an aggregate score

See bench/eval-guide.md for detailed instructions.
