# UC12 — ChainForge AI Model Evaluation

Multi-model prompt evaluation platform. Tests local (Ollama) and external AI models across
10+ task categories, then uses those results to produce data-driven social media content and reports.

## Pipeline

```
ChainForge tests → benchmark results → LinkedIn post / report
```

ResearchReady's position: we actually test AI — and we show the receipts.

## Quick start

```bash
# Install (once)
pip install chainforge

# Start on port 8765 (LangGraph uses 8000)
chainforge serve --port 8765
# Open http://localhost:8765
```

## Test categories

| Category | File | What it measures |
|----------|------|-----------------|
| Reasoning | `chainforge/flows/reasoning.cforge` | Logic, multi-step problems |
| Code generation | `chainforge/flows/code-gen.cforge` | Correct code from spec |
| Code review | `chainforge/flows/code-review.cforge` | Bug finding, suggestions |
| Summarization | `chainforge/flows/summarization.cforge` | Compression accuracy |
| Classification | `chainforge/flows/classification.cforge` | Labels, structured output |
| Creative writing | `chainforge/flows/creative.cforge` | Tone, style, originality |
| Factual QA | `chainforge/flows/factual-qa.cforge` | Accuracy on verifiable facts |
| Security analysis | `chainforge/flows/security.cforge` | Spot vulns in code/config |
| Instruction following | `chainforge/flows/instruction.cforge` | Format & constraint adherence |
| Translation | `chainforge/flows/translation.cforge` | NL ↔ EN accuracy |

## Output

1. **`output/runs/`** — raw ChainForge exports (CSV/JSON)
2. **`output/model-selection-guide.md`** — which model wins per category
3. **`output/social-media/`** — LinkedIn posts and reports generated FROM the benchmark data
4. **`chainforge/prompts/results-to-linkedin.txt`** — prompt template: feed results in, get post out

## Models tested

### Local (Ollama on localhost:11434)
- hermes3:latest, qwen3:14b, gemma3:27b, phi4:latest, deepseek-r1:14b, llama3.1:8b

### External Cloud Models (requires `.env` — copy `.env.example`)
- Anthropic Claude Haiku (`claude-haiku-4-5-20251001`)
- OpenAI GPT-4o-mini (`gpt-4o-mini`)
- Google Gemini Flash (`gemini-1.5-flash`)

## Connecting local models in ChainForge
- Provider: OpenAI (custom base URL)
- Base URL: `http://localhost:11434/v1`
- API key: `ollama`
- Model: exact name from `ollama list`

## Automated 4-Track Benchmark & Academic Pipeline

```bash
# Run local 4-track benchmark (cognitive, security, latency, and GPU power)
python3 scripts/run_benchmark.py

# Run external frontier models against the same local judge
python3 scripts/run_external.py

# Regenerate SVGs, patch .qmd tables, and compile academic HTML + PDF
python3 scripts/make_academic_report.py
```

## Scheduled Automation via n8n

The benchmark suite includes an end-to-end automation workflow for [n8n](http://localhost:5678):
- **Workflow File:** `n8n/uc12-benchmark-workflow.json`
- **Schedule:** Runs weekly on Sundays at 02:00 local time (configurable).
- **Webhook Trigger:** Instant on-demand execution via POST to `http://localhost:5678/webhook/uc12-benchmark-trigger`.
- **Pipeline:** Automated execution of benchmarks, chart generation, Quarto compilation, draft LinkedIn post generation, git commit, and webhook notification.
- See [`n8n/README.md`](n8n/README.md) for full configuration instructions.

