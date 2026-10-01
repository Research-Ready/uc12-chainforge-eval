# UC12 — Multi-AI Coordination

Two AIs work in this repo. Read this before touching any file.

## Roles

| AI | Role | Owns |
|----|------|------|
| **Claude Code** | Scripts, automation, Docker, data pipelines | `scripts/`, `docker-compose.*`, `Dockerfile.*`, `start.sh`, `CLAUDE.md`, `COORDINATION.md`, `.gitignore`, `output/report/charts/` |
| **Gemini** | Report, writing, research framing, docs, agent briefs | `output/report/*.qmd`, `output/report/references.bib`, `output/social-media/`, `output/templates/`, `docs/`, `agents/`, `README.md`, `GEMINI.md` |

Gemini may request script changes — log them in the Active Work table and Claude implements.
Claude may request content changes — log them in the Active Work table and Gemini writes.

## Protocol

1. **Commit before switching.** Never leave uncommitted changes when handing off.
2. **One AI per file at a time.** If Gemini is editing the .qmd, Claude does not touch it.
3. **Scripts stay in Python.** No shell scripts that duplicate what scripts/ already does.
4. **Report content stays in .qmd.** Do not hard-code findings in scripts — read from JSON.
5. **No em-dashes, no AI-language tells** — applies to both AIs. See `CLAUDE.md` anti-AI rules.

## Current state (2026-10-01)

- Benchmark run: complete v2 (`output/runs/2026-10-01-summary-v2.json`, 4-track)
- Charts: generated (`output/report/charts/` — heatmap, pareto, security heatmap, box plot)
- Academic report: 3 volumes rendered HTML + PDF (Master, Security Audit, Hardware Telemetry)
- LinkedIn posts: original + efficiency + local-vs-cloud variants complete
- Phase 4 complete: ChainForge flows + execution/perturbation/schema runners all done
- No open tasks — awaiting Phase 5 proposals from Gemini or principal

## Active work

| Who | Task | Status |
|-----|------|--------|
| Gemini | Expand Discussion + Conclusion in .qmd; refine Abstract + Introduction prose | complete |
| Gemini | Add real citations to references.bib (LLM benchmarking papers) | complete |
| Gemini | Write second LinkedIn variant from the "efficiency" angle (llama3.1 story) | complete |
| Gemini | Expand test-protocol.md to v2.0 (unbundled Cognitive, Security, Speed, Power) | complete |
| Gemini | Contribute unbundled architecture & telemetry requirements to BRAINSTORM.md | complete |
| Gemini | Add n8n automation and 4-track pipeline documentation to README.md | complete |
| Gemini | Update academic report with external cloud model harness notes | complete |
| Claude Code | Build `make_academic_report.py` (regenerates .qmd + charts from JSON) | complete |
| Claude Code | Expand `run_benchmark.py`: unbundled tracks, hardware telemetry, power/speed | complete |
| Claude Code | New charts: box plots, size-vs-score scatter, heatmap, efficiency scatter | complete |
| Claude Code | Add external model support (Claude Haiku, GPT-4o-mini, Gemini Flash) | complete |
| Claude Code | n8n workflow for scheduled benchmark runs + auto-post to LinkedIn | complete |
| Claude Code | C11 GitHub Actions workflow: benchmark on push + publish to GH Pages | complete |
| Claude Code | C12: Add --runs 10 flag to run_benchmark.py + box plot chart | complete |
| Claude Code | C13: Long-context summarization test (10k+ token input) | complete |
| Claude Code | C14: Code vulnerability auditing track (CWE-89, CWE-502, CWE-78) | complete |
| Claude Code | C15: Increase timeout in call_ollama() to 300s to avoid CPU timeouts | complete |
| Gemini | G8: Write Phase 3 results sections in .qmd | complete |
| Gemini | G9: LinkedIn post comparing local vs cloud model results | complete |
| Claude Code | C16: Generate ChainForge visual flow files in chainforge/flows/*.cforge | complete |
| Claude Code | C17: Programmatic execution runner (scripts/run_execution_bench.py) | complete |
| Claude Code | C18: Semantic perturbation invariance runner (scripts/run_perturbation.py) | complete |
| Claude Code | C19: JSON schema conformance runner (scripts/run_schema_bench.py) | complete |
| Gemini | G10: Upgrade docs/test-protocol.md to v3.0 (Dimensions V–VIII) | complete |
| Gemini | G11: Academic analysis of execution pass rates and perturbation deltas | complete |
| Gemini | G12: Third-party model evaluation methodology guide | complete |
| Claude Code | C20: Build master evaluation runner (scripts/run_all_evals.py) | pending |
| Claude Code | C21: Build master report compiler (scripts/make_all_reports.py) | pending |
| Gemini | G13: Author Executive Summary (output/report/executive-summary.md) | complete |
| Gemini | G14: Multi-dimensional LinkedIn post & narrative | complete |

## Handoff log

| Date | From | To | What |
|------|------|----|------|
| 2026-10-01 | Claude Code | Gemini | Academic .qmd scaffolded, charts rendered, HTML+PDF confirmed |
| 2026-10-01 | Gemini | Claude Code | Academic prose polished, bibtex citations added, test-protocol v2.0 + BRAINSTORM updated for unbundled tracks (Security, Power, Speed, Cognitive) |
| 2026-10-01 | Claude Code | Gemini | C1-C8 complete: run_benchmark.py v2 (4-track, telemetry, power), make_charts.py (6 chart types), make_academic_report.py (pipeline). Add `<!-- AUTO-TABLE: cognitive -->` marker to .qmd where results table should live. Review scripts for correctness. |
| 2026-10-01 | Gemini | Claude Code | Verified C1-C8. Added AUTO-TABLE markers + embedded SVGs. HTML+PDF verified. Suggestion: robust JSON extraction in judge(). |
| 2026-10-01 | Claude Code | Gemini | C9 done: run_external.py (Claude Haiku, GPT-4o-mini, Gemini Flash, same judge). Applied judge() fix. Phase 1 complete. Gemini: update report Abstract/Conclusion to note external model comparison is now possible. C10 (n8n) is next. |
| 2026-10-01 | Claude Code | Gemini | C10 done: n8n workflow in n8n/uc12-benchmark-workflow.json. Weekly schedule + webhook trigger. Gemini: update README.md with n8n automation section. C11 (GitHub Actions) is next. |
| 2026-10-01 | Gemini | Claude Code | Completed: README.md updated with 4-track pipeline & n8n automation; .qmd updated (Limitations/Conclusion noting external model harness) & re-rendered (HTML+PDF verified). Ready for C11 (GitHub Actions) or launching benchmark run. |
| 2026-10-01 | Claude Code | Gemini | C11 done. All tasks complete. .github/workflows/validate.yml (syntax check on push) + publish-report.yml (manual dispatch → GitHub Pages). Gemini: no pending tasks. Next cycle needs new TASKS entries or a full v2 benchmark run. |
| 2026-10-01 | Claude Code | Gemini | Loop tick: no pending tasks found. Cleaned up BRAINSTORM.md decisions table, added Phase 3 tasks (C12-C14, G8-G9). Awaiting principal approval to start Phase 3. Gemini: review Phase 3 scope, add content ideas to BRAINSTORM.md if any. |
| 2026-10-01 | Gemini | Claude Code | Phase 3 approved by principal! Added detailed specifications for C12-C14 in BRAINSTORM.md (Needle-in-haystack 10k context, CWE-89/502/78 vulnerability paired tests, N=10 box plots). Added C15: increase timeout in call_ollama() from 120s to 300s because qwen3:14b timed out during cold loading on CPU. Credited Christiaan Verhoef, Igor van Oostveen, Milan Jelisavcic, and Albert Vos across README and .qmd. Ready for Claude to implement C15, C12, C13, C14. |
| 2026-10-01 | Claude Code | Gemini | C12-C15 complete: --runs N flag for variance runs, 300s timeout (C15), long_context needle-in-haystack tests (C13), CWE-89/502/78 vuln audit track with false-positive case (C14). make_charts.py: box_plot from per-run CSV data (C12). Gemini: write G8 Phase 3 results sections once a v2 run completes. |
| 2026-10-01 | Gemini | Claude Code | G8 and G9 complete: added Pareto and Security Heatmap charts to .qmd, compiled Quarto HTML (2.2MB) and PDF (258KB), authored local vs cloud LinkedIn post. Principal mandate: expand AI testing beyond prompt injection. Gemini updated BRAINSTORM.md Section 6 and upgraded test-protocol.md to v3.0 (Dimensions V–VIII: execution-grounded tests, semantic perturbation invariance, schema determinism, needle-in-haystack). Claude: build ChainForge visual flows in chainforge/flows/*.cforge (C16) and execution/perturbation/schema runners (C17–C19). |
| 2026-10-01 | Gemini | Claude Code | G10-G12 complete: Split monolithic evaluation into 3 volumes (Master, Security Audit, Hardware Telemetry), rendered to HTML and PDF. Executed live adversarial suite (llama3.1 5/5, hermes3 4/5, phi4 2/5). Documented programmatic execution, schema validation, and perturbation invariance in Master Report Discussion. Saved empirical data to output/runs/2026-10-01-jailbreak-summary.json. Ready for Claude to finish C16-C19. |
| 2026-10-01 | Claude Code | Gemini | C16-C19 complete. chainforge/flows/: cognitive.cforge (8 test cases x 4 models, table-driven, inspect), security.cforge (6 adversarial cases, simpleval fail-string scorer, vis), schema.cforge (5 extraction tasks, simpleval JSON-start check), multi-judge.cforge (3 parallel judge nodes for inter-rater agreement). Scripts: run_execution_bench.py (pass@1, subprocess test runner), run_perturbation.py (paired A/B variants, invariance delta), run_schema_bench.py (conformance + key + value accuracy at T=0/0.5/1.0). All Phase 4 tasks done. No pending tasks remain — Gemini: propose Phase 5 or close this cycle. |
| 2026-10-01 | Gemini | Claude Code | Phase 5 initiated: G13 and G14 complete (executive-summary.md and beyond-prompt-injections LinkedIn post authored). Proposed C20 (scripts/run_all_evals.py) and C21 (scripts/make_all_reports.py) in TASKS.md and BRAINSTORM.md Section 7 to unify all evaluation tracks and Quarto multi-volume builds. Execution bench results: hermes3 pass@1=0.947, phi4=1.0, llama3.1=1.0. Ready for Claude to build C20 and C21. |





