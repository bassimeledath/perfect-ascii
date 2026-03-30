# perfect-ascii

A Claude skill for creating perfectly aligned ASCII diagrams. Built with iterative improvement via [swarmy](https://github.com/bassimeledath/swarmy).

## Structure

```
SKILL.md              # The skill — what gets iterated on
bench/
  scenarios.md        # Benchmark prompts (complex diagrams)
  render.html         # HTML template for monospace rendering
  eval-guide.md       # Instructions for tester agents
  output/             # Generated outputs (gitignored)
```

## How it works

The skill is improved through swarmy's explore-implement-test loop:

1. **Explorer** analyzes current failures and proposes improvements
2. **Implementer** updates SKILL.md with better techniques
3. **Tester** generates diagrams from benchmarks, screenshots them, and scores visual alignment

The tester uses Chrome DevTools to render ASCII output as monospace images, then visually evaluates alignment quality.
