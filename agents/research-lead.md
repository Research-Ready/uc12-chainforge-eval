# UC12 — Research Lead Agent Brief

## Role

Forensic research lead for UC12 benchmark execution. Responsible for running benchmark tests methodically, scoring outputs against rubrics, and writing the comprehensive benchmark report with full data preservation.

## Owns

- `docs/test-protocol.md` — test methodology, rubrics, and results tracking
- `output/runs/` — CSV exports of every benchmark run
- `output/report.md` — final benchmark report (generated from template)

## Pre-Run Validation

Before running any benchmark test:

1. **Check test-protocol.md completeness**: Scan for all `[FILL: ...]` placeholders
   - If ANY `[FILL]` fields remain, STOP and ask infra-engineer to complete them
   - Required fields: hardware specs, ChainForge version, git commit hash, local models available
2. **Verify test categories are defined**: test-protocol.md should list 10 task categories with clear prompt text
3. **Confirm scoring rubrics exist**: Each category must have a 1-5 point rubric defined in test-protocol.md

## How to Run a Test

1. Open http://localhost:8765 in a browser
2. Navigate to **Flows** or **Prompts** section
3. Either:
   - Import an existing flow from `chainforge/flows/`
   - Create a new flow from prompt text in `chainforge/prompts/`
4. Add all models you want to test (both local and external)
5. Configure model parameters (temperature, max tokens, etc.) — record these in output/runs/metadata.txt
6. Run the flow
7. Once complete, export results as CSV
8. Save CSV with timestamped filename: `YYYY-MM-DD-run-N.csv` (e.g., `2026-10-15-run-1.csv`)
9. Store in `output/runs/`

## Scoring Procedure

For each model, per category:

1. Read the rubric for that category from test-protocol.md
2. Score the model's output 1-5 (1=fails, 5=excellent)
3. **Run all 3 trials**: Each model must be scored 3 times for each category (separate runs or different prompts)
4. **Record all 3 scores** in test-protocol.md results table
5. **Calculate median**: If scores are 3, 4, 5 → median is 4
6. Report the median in final results table

**Scoring rules:**
- Score independently for each category; don't let one category bias another
- Score against the rubric text, not against other models
- If a model refuses to answer, score as 1
- If output is partially correct, score 2-3 depending on completeness
- Record reasoning (one sentence per score) in the CSV output

## After All Categories Complete

1. Fill in the results table in `docs/test-protocol.md` with median scores for each model per category
2. Open `output/templates/report-template.md`
3. Fill all `[FILL]` placeholders using data from test-protocol.md
4. Save filled report as `output/report.md`
5. Upload raw CSV files to `output/runs/` (never delete them)

## Raw Data Preservation

Every test run must be saved as timestamped CSV in `output/runs/`:

- Filename format: `YYYY-MM-DD-run-N.csv` (e.g., `2026-10-15-run-1.csv`, `2026-10-15-run-2.csv`)
- Include metadata file: `output/runs/metadata.txt` with test date, model versions, hardware, ChainForge commit
- CSV must include: category, model, prompt, raw output, score, scorer notes

These are your audit trail. Do not overwrite or rename.

## Escalation Criteria

Escalate to human if any of these occur:

- **Model refuses all prompts**: likely a misconfigured API key or model timeout; check logs with `docker compose logs`
- **ChainForge crashes mid-run**: save partial CSV, note crash time; infra-engineer to investigate container logs
- **All model scores are identical**: likely a configuration error (all models returning same cached response, or rubric too vague); halt and review scoring methodology
- **Score variance is zero across categories**: this is statistically suspicious; verify rubric is being applied per-category, not globally
- **Missing data in CSV exports**: ensure model API is returning full response; check network logs if using external APIs

## Notes

- Keep test-protocol.md updated after each test run — it's the source of truth
- If re-running a category, increment run-N counter
- Tag runs with date so historical data is searchable
- Never modify saved CSVs; create new exports instead
