# Skill: ChainForge Run

Run a ChainForge evaluation flow end-to-end and feed the results into a LinkedIn post or report section.

---

## Step 1 — Start ChainForge

```bash
chainforge serve --port 8765
```

Verify it is running: open `http://localhost:8765`. If you see a port conflict, check `lsof -i :8765`.

---

## Step 2 — Load a Flow

1. In ChainForge, click **File → Import**.
2. Navigate to `chainforge/flows/` and select the `.cforge` file for your evaluation category.
3. The flow opens with prompt templates, model nodes, and an Inspect node pre-wired.

If you are building a flow manually:
- Add a **TextFields** node and paste the prompt from `chainforge/prompts/`.
- Add one **Model** node per model under test (Ollama or external).
- Wire each model node to an **Inspect** node.

---

## Step 3 — Run the Evaluation

1. Click **Run** (the play button) on the flow canvas.
2. ChainForge sends each prompt variant to each model in parallel.
3. Watch the Inspect node populate with responses. Large models (gemma3:27b, deepseek-r1:14b) will be slower — expect 30-120 seconds per prompt on local hardware.

---

## Step 4 — Export Results

1. Click the **Inspect** node.
2. Click **Export → CSV** (or JSON).
3. Save the file to `output/runs/` with a descriptive name:
   `output/runs/YYYY-MM-DD-<category>.csv`
4. CSV and JSON files in `output/runs/` are gitignored. Commit only the summary table you produce next.

---

## Step 5 — Feed Results into an Output Prompt

Open a new ChainForge flow (or use Claude directly) with one of the output templates:

**For a LinkedIn post:**
- Template: `chainforge/prompts/results-to-linkedin.txt`
- Paste the exported results table into `{benchmark_summary}`
- Set `{company}` to `ResearchReady`
- Set `{audience}` to `AI practitioners, tech leaders, potential clients`
- Save the output to `output/social-media/YYYY-MM-DD-linkedin.txt`

**For a report section:**
- Template: `chainforge/prompts/results-to-report.txt`
- Paste the exported results table into `{benchmark_summary}`
- Save the output to `output/runs/YYYY-MM-DD-report-section.md`
- This format is suitable for UC1 pipeline ingestion

---

## Step 6 — Update the Model Selection Guide

After each benchmark run, update the relevant rows in `output/model-selection-guide.md` with the top-performing local and external models and their scores.

---

## Notes

- Run each task category on a fresh flow to keep results isolated.
- Use consistent test inputs across model comparisons — vary only the model, not the prompt or inputs.
- If a model returns an error or times out, note it in the guide rather than re-running indefinitely.
- The results-to-linkedin and results-to-report prompts are post-processing steps, not benchmarks — do not include their outputs in the benchmark results table.
