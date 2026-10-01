# UC12 — Shared Task Board

Both AIs update this. Principal approves priorities.
Format: `[ ]` pending · `[~]` in progress · `[x]` done · `[!]` blocked (reason)

---

## Phase 1 — Expanded Evaluation Engine (Claude Code)

- [x] `C1` Implement 4-track JSON schema in `run_benchmark.py` (per Gemini's spec in BRAINSTORM.md)
- [x] `C2` Add latency telemetry: gen tok/s, TTFT, prompt eval tok/s
- [x] `C3` Add GPU power sampling via `nvidia-smi` (100ms intervals, energy per query)
- [x] `C4` Add new test categories: multi-turn, structured output, negative constraint
- [x] `C5` Add security tracks: prompt injection, secret/PII leakage, sycophancy
- [x] `C6` Add negative constraint adherence tests
- [x] `C7` New charts: heatmap, size-vs-score scatter, pareto scatter, security heatmap
- [x] `C8` Build `make_academic_report.py`: load v2 JSON → run charts → render .qmd
- [x] `C9` External model support: Claude Haiku, GPT-4o-mini, Gemini Flash

## Phase 1 — Report & Content (Gemini)

- [x] `G1` Expand Discussion section: explain why phi4 wins, why llama3.1 is the efficiency story
- [x] `G2` Expand Conclusion: practical model selection guide, limitations, future work
- [x] `G3` Add real citations to `references.bib` (LLM benchmarking papers — HELM, BIG-Bench, etc.)
- [x] `G4` Write second LinkedIn post: efficiency angle (score/second, score/watt)
- [x] `G5` Update test protocol in `docs/test-protocol.md` to reflect 4-track structure
- [x] `G6` Refine Abstract + Introduction prose for the expanded scope
- [x] `G7` Draft Appendix: raw scores table, hardware spec, rubric definitions per track

## Phase 2 — Automation (Claude Code, after Phase 1)

- [x] `C10` n8n workflow: scheduled benchmark run → auto-generate report → notify
- [x] `C11` GitHub Actions: run benchmark on push, publish report to GitHub Pages

## Phase 3 — Depth (approved by principal)

- [x] `C12` Add `--runs 10` flag to run_benchmark.py + box plot chart from variance data
- [x] `C13` Long-context summarization test (10k+ token input, tests VRAM limits)
- [x] `C14` Code vulnerability auditing track (CWE-89 SQLi, CWE-502 deserialization)
- [x] `C15` Increase timeout in `call_ollama()` from 120s to 300s (prevents ReadTimeout on 14B CPU inference)
- [~] `G8`  Gemini: write Phase 3 results sections in .qmd (running full 14-track benchmark task-672)
- [ ] `G9`  Gemini: LinkedIn post comparing local vs cloud model results (after run_external.py run)

---

## Blocked / Dependencies

| Task | Blocked by | Notes |
|------|-----------|-------|
| `C8` | `C1`–`C7` | Report generator needs all data tracks first |
| `C10`, `C11` | `C8` | Automation wraps the full pipeline |

---

## Completed

- `G1`–`G7`: Complete academic report rewrite, anti-AI linting, unbundled 4-track framing, real BibTeX citations, test protocol v2.0, Appendix raw table, and LinkedIn efficiency draft.

