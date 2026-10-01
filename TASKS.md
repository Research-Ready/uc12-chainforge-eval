# UC12 — Shared Task Board

Both AIs update this. Principal approves priorities.
Format: `[ ]` pending · `[~]` in progress · `[x]` done · `[!]` blocked (reason)

---

## Phase 1 — Expanded Evaluation Engine (Claude Code)

- [ ] `C1` Implement 4-track JSON schema in `run_benchmark.py` (per Gemini's spec in BRAINSTORM.md)
- [ ] `C2` Add latency telemetry: gen tok/s, TTFT, prompt eval tok/s
- [ ] `C3` Add GPU power sampling via `nvidia-smi` (100ms intervals, energy per query)
- [ ] `C4` Add new test categories: multi-turn, structured output, consistency/variance ×10
- [ ] `C5` Add security tracks: prompt injection, secret/PII leakage, sycophancy
- [ ] `C6` Add negative constraint adherence tests
- [ ] `C7` New charts: box plots, size-vs-score scatter, heatmap, efficiency Pareto scatter
- [ ] `C8` Build `make_academic_report.py` that reads 4-track JSON → generates .qmd + charts
- [ ] `C9` External model support: Claude Haiku, GPT-4o-mini, Gemini Flash

## Phase 1 — Report & Content (Gemini)

- [x] `G1` Expand Discussion section: explain why phi4 wins, why llama3.1 is the efficiency story
- [x] `G2` Expand Conclusion: practical model selection guide, limitations, future work
- [x] `G3` Add real citations to `references.bib` (LLM benchmarking papers — HELM, BIG-Bench, etc.)
- [x] `G4` Write second LinkedIn post: efficiency angle (score/second, score/watt)
- [x] `G5` Update test protocol in `docs/test-protocol.md` to reflect 4-track structure
- [x] `G6` Refine Abstract + Introduction prose for the expanded scope
- [x] `G7` Draft Appendix: raw scores table, hardware spec, rubric definitions per track

## Phase 2 — Automation (Claude Code, after Phase 1)

- [ ] `C10` n8n workflow: scheduled benchmark run → auto-generate report → notify
- [ ] `C11` GitHub Actions: run benchmark on push, publish report to GitHub Pages

---

## Blocked / Dependencies

| Task | Blocked by | Notes |
|------|-----------|-------|
| `C8` | `C1`–`C7` | Report generator needs all data tracks first |
| `C10`, `C11` | `C8` | Automation wraps the full pipeline |

---

## Completed

- `G1`–`G7`: Complete academic report rewrite, anti-AI linting, unbundled 4-track framing, real BibTeX citations, test protocol v2.0, Appendix raw table, and LinkedIn efficiency draft.

