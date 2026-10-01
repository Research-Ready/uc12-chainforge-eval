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
- [x] `G8`  Gemini: write Phase 3 results sections in .qmd (pareto & security heatmap charts, unbundled analysis, HTML+PDF verified)
- [x] `G9`  Gemini: LinkedIn post comparing local vs cloud model results (`output/social-media/2026-10-01-linkedin-post-local-vs-cloud.md`)

## Phase 4 — Multi-Dimensional AI Evaluation (Beyond Prompt Injections)

- [x] `C16` Claude: Build ChainForge visual flow files in `chainforge/flows/*.cforge` (cognitive, security, schema, multi-judge)
- [x] `C17` Claude: Programmatic execution runner (`scripts/run_execution_bench.py`) — pass@1 metric, 4 functions, hidden test suites
- [x] `C18` Claude: Semantic perturbation invariance runner (`scripts/run_perturbation.py`) — 4 paired variants, delta metric
- [x] `C19` Claude: JSON schema conformance runner (`scripts/run_schema_bench.py`) — conformance/key/value accuracy across temperatures
- [x] `G10` Gemini: Expand `docs/test-protocol.md` to v3.0 with complete rubrics, ground-truth assert suites, and perturbation pairs
- [x] `G11` Gemini: Write academic report sections in `.qmd` analyzing execution pass rates, perturbation deltas, and epistemic robustness
- [x] `G12` Gemini: Draft comprehensive model evaluation guide for testing third-party AI systems (`output/third-party-evaluation-guide.md`)

---

## Blocked / Dependencies

| Task | Blocked by | Notes |
|------|-----------|-------|
| `C8` | `C1`–`C7` | Report generator needs all data tracks first |
| `C10`, `C11` | `C8` | Automation wraps the full pipeline |

---

## Completed

- `G1`–`G7`: Complete academic report rewrite, anti-AI linting, unbundled 4-track framing, real BibTeX citations, test protocol v2.0, Appendix raw table, and LinkedIn efficiency draft.

