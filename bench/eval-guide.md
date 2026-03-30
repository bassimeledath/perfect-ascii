# Evaluation Guide for Tester Agents

You are evaluating the `SKILL.md` skill for ASCII diagram quality. Your job: generate diagrams using the skill's rules, render them as images, and score visual alignment.

## Setup

```bash
mkdir -p bench/output
```

## For each scenario in bench/scenarios.md:

### Step 1: Generate the diagram

Read `SKILL.md` carefully. Then generate the ASCII diagram for the scenario, strictly following the skill's instructions. Write ONLY the raw ASCII art — no markdown fences, no explanation.

### Step 2: Render as image

Create an HTML file for the diagram by copying `bench/render.html` and replacing `PASTE_ASCII_HERE` with the generated ASCII content. Write it to `bench/output/scenario-N.html`.

**Important**: The ASCII must be HTML-escaped (replace `<` with `&lt;`, `>` with `&gt;`, `&` with `&amp;`). Do NOT alter spacing or alignment when escaping.

### Step 3: Screenshot

Use Chrome DevTools MCP tools:
1. `navigate_page` to `file:///absolute/path/to/bench/output/scenario-N.html`
2. `take_screenshot` to capture the rendered diagram
3. **Save a copy** of each screenshot to `/Users/bassime/Downloads/perfect-ascii-progress/i<N>-scenario-<M>.png` so progress is visible across iterations.

### Step 4: Analyze the screenshot

Look at the screenshot image carefully. Score each dimension 1-5:

- **box_closure**: Are all boxes properly closed? Do corners meet edges? (5 = every box perfect, 1 = multiple broken boxes)
- **vertical_alignment**: Do vertical lines (`|`) in the same logical column appear in the same pixel column? (5 = perfect, 1 = visibly jagged)
- **horizontal_alignment**: Do horizontal lines (`-`) in the same logical row stay on the same line? (5 = perfect, 1 = visibly uneven)
- **connector_routing**: Do arrows/connectors cleanly connect to their source and destination boxes? No floating endpoints? (5 = all connect, 1 = multiple disconnected)
- **text_centering**: Is text properly positioned within boxes? (5 = well-centered, 1 = clearly off)
- **overall_readability**: Does the diagram read clearly as what it's supposed to represent? (5 = immediately clear, 1 = confusing)

### Step 5: Record score

Write results to `.swarmy/results/i<N>-c<M>.txt` in this format:

```
scenario_1: box=? vert=? horiz=? conn=? text=? read=? subtotal=?/30
scenario_2: box=? vert=? horiz=? conn=? text=? read=? subtotal=?/30
scenario_3: box=? vert=? horiz=? conn=? text=? read=? subtotal=?/30
scenario_4: box=? vert=? horiz=? conn=? text=? read=? subtotal=?/30
scenario_5: box=? vert=? horiz=? conn=? text=? read=? subtotal=?/30
scenario_6: box=? vert=? horiz=? conn=? text=? read=? subtotal=?/30
score=?/180
```

## Important rules

- Follow SKILL.md exactly as written. Do not use techniques not in the skill.
- Do not modify any files in bench/ except bench/output/.
- The rendered screenshot is the source of truth, not the raw text. If the text "looks right" in your context but the screenshot shows misalignment, that's a failure.
- Be harsh. If a vertical line is off by even one character, deduct points. The goal is PERFECT alignment.
- Do not give the benefit of the doubt. Real misalignment must be scored down.
