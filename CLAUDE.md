# perfect-ascii

Claude skill for creating perfectly aligned ASCII diagrams.

## Project structure

- `SKILL.md` — the skill being iterated on. This is the **target** for swarmy runs.
- `bench/scenarios.md` — benchmark prompts. **Read-only** during swarmy runs.
- `bench/render.html` — HTML template for rendering ASCII as monospace image. **Read-only**.
- `bench/eval-guide.md` — tester agent instructions. **Read-only**.
- `bench/output/` — scratch space for generated HTML/screenshots. Gitignored.

## Eval flow (for tester agents)

1. Read SKILL.md to understand the current technique
2. For each scenario in bench/scenarios.md, generate an ASCII diagram following SKILL.md
3. Wrap each diagram in bench/render.html template, write to bench/output/
4. Open each in Chrome DevTools, screenshot it
5. Analyze each screenshot for misalignment issues
6. Produce a score per scenario and an aggregate score

See bench/eval-guide.md for detailed instructions.
