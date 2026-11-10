# UC12 — ChainForge AI Model Evaluation

<!-- coordinator:start -->
## Reporting to the coordinator

Progress for all use cases is tracked in `ResearchReady/workbook/` (the coordinator). It **reads** this repo
and never edits it, so the workbook is only as correct as the files below. Keep them true at the end of every
session. Do not edit files in the workbook yourself.

| Report | Where, in which form |
|---|---|
| Task progress | `PLAN.md` (tasks in `TASKS.md`): `### T1 — title ✅ DONE`, `🟡 IN PROGRESS` or `⛔ BLOCKED` in the heading, plus a `**Status (YYYY-MM-DD):**` line saying what was verified |
| Current state | `PLAN.md` → `## Current status`: short, dated bullets. Name the machine (Ubuntu laptop / Fedora laptop) when it matters |
| Test evidence | `test-results/dry_run_YYYYMMDD_HHMMSS.json`: `{"timestamp": "...", "steps": [{"name": "...", "status": "PASS" / "FAIL" / "SKIP", "detail": "..."}]}`. Without this file the workbook shows "no evidence" or an old run |
| Dry-run headline | Optional: `## Dry-run status (YYYY-MM-DD)` in this file with `**N/M PASS**`. Update or delete it; an old headline is read as the latest result |
| Blockers | A `**Active blocker**: ...` line in this file, or a `BLOCKED.md` naming the infra issue ID (e.g. `D-3`). **Delete the line or the file as soon as it is no longer true**; stale blockers keep this use case amber |
| Workflow diagram | `docs/workflow.yml`: steps with `id`, `label`, `lane`, `status: working / partial / broken / planned` |
| Needs from the platform | Write `InstallLocalAiPackage/REQUEST-uc12-<topic>.md` (Report, Request, Done when). Do not edit infra issues or the stack yourself |

Rules: everything is local (no GitHub; the server may be down, see above). Uncommitted changes show as a
warning in the workbook; commit locally when the user asks.
<!-- coordinator:end -->

## What this is

General-purpose AI model evaluation platform using ChainForge. Runs structured tests across
local (Ollama) and external (Anthropic, OpenAI, Google) models to benchmark capability,
consistency, and cost across task categories.

**Output**: model comparison data — which model wins at what task type. Feeds model-selection
decisions across all other UCs.

## You are LAPTOP1

This UC lives on LAPTOP1. ChainForge runs locally on port 8765.
Larger GPU rig can be added later as a remote Ollama endpoint — see docs/setup.md.

## Local stack context (server down, local-only)

The Proxmox cluster is offline. Every `10.0.x.x` address and `*.research-ready.nl` are unreachable.

| Service | Address | Purpose |
|---------|---------|---------|
| ChainForge UI | http://localhost:8765 | Evaluation dashboard |
| Ollama | http://localhost:11434 | Local LLM backend |
| LiteLLM proxy | http://localhost:4000 | Unified gateway (when stack running) |

## Start ChainForge

```bash
# First time only
pip install chainforge

# Every session — port 8765 avoids conflict with LangGraph on 8000
chainforge serve --port 8765
```

Open http://localhost:8765.

## Local models (Ollama — already running)

| Model | Size | Notes |
|-------|------|-------|
| hermes3:latest | 4.7 GB | Conversational, instruction-following |
| qwen3:14b | 9.3 GB | Strong reasoning |
| gemma3:27b | 17 GB | High quality, slower |
| phi4:latest | 9.1 GB | Concise and fast |
| deepseek-r1:14b | 9.0 GB | Chain-of-thought tasks |
| llama3.1:8b | 4.9 GB | Fast baseline |

## Connecting local models in ChainForge

Provider: **OpenAI (custom base URL)**
- Base URL: `http://localhost:11434/v1`
- API key: `ollama` (any string)
- Model: exact name from `ollama list`

## External model API keys

Copy `.env.example` → `.env`. Never commit `.env`.

## Test categories

Flows live in `chainforge/flows/`, one file per category:

| Category | Flow file | What it tests |
|----------|-----------|--------------|
| Reasoning | `reasoning.cforge` | Logic puzzles, multi-step problems |
| Code generation | `code-gen.cforge` | Write correct code from spec |
| Code review | `code-review.cforge` | Find bugs, suggest fixes |
| Summarization | `summarization.cforge` | Compress long text accurately |
| Classification | `classification.cforge` | Label text, structured output |
| Creative writing | `creative.cforge` | Tone, style, originality |
| Factual QA | `factual-qa.cforge` | Accuracy on verifiable facts |
| Security analysis | `security.cforge` | Spot vulnerabilities in code/config |
| Instruction following | `instruction.cforge` | Format compliance, constraint adherence |
| Translation / localization | `translation.cforge` | NL ↔ EN accuracy |

## Results

ChainForge exports comparison tables. Save exports to `output/runs/`.
Summaries (which model wins per category) go in `output/model-selection-guide.md`.

## Hard rules

- No infra changes from this repo — use InstallLocalAiPackage
- Check `ResearchReadyDocumentation/COORDINATION/BLOCKED.md` before starting
- Update `COORDINATION/LAPTOP1.md` at session start and end
- Never commit `.env`

## Absolute Veracity & Real-World Deliverable Proof (Never False Completion)
- **Zero False Completion**: NEVER claim a feature, integration, or system is done, verified, or working based solely on isolated unit tests or files written to disk if the actual user-facing application (e.g., OpenWebUI, database, deployed service) is not genuinely configured, populated, and verified in reality.
- **Admit Gaps Explicitly**: Admitting an integration gap or failure immediately is mandatory. If assets exist on disk but have not been imported or wired into the running application/UI, state the exact truth: *"The assets exist on disk, but [Application/UI] is not yet configured and cannot use them yet."*
- **End-User Experience is Ground Truth**: A task is only complete when the user can open the target application and immediately use the functionality as intended.
