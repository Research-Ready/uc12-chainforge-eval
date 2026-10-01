# Model Selection Guide — ResearchReady

Empirical model selection recommendations based on local workstation benchmarks (AMD Ryzen 7 8845HS, RTX 4060 8 GB, 46 GB RAM). Last updated: 2026-10-01.

---

## 1. Category Recommendations

| Category | Best Local Model | Score (/5) | Best External Model | Recommended Tier | Architectural Rationale |
|----------|-----------------|------------|---------------------|------------------|-------------------------|
| **Mathematical & Multi-step Reasoning** | `phi4:latest` / `qwen3:14b` | 5 | Claude 3.5 Sonnet / GPT-4o | Local High-Capability | Strong chain-of-thought pre-training; resolves distractor clauses. |
| **Code Generation & Syntax** | `llama3.1:8b` / `phi4:latest` | 5 | Claude 3.5 Sonnet | Local Efficiency Baseline | `llama3.1:8b` matches 14B models on recursion, edge-case handling, and typing with half the memory footprint. |
| **Security Vulnerability Auditing** | `hermes3:latest` / `phi4:latest` / `llama3.1:8b` | 5 | GPT-4o / Claude 3.5 Sonnet | Local Efficiency Baseline | Identifies SQLi, hardcoded credentials, and Docker root vulnerabilities with actionable remediation steps. |
| **Instruction Following & Constraints** | `phi4:latest` | 5 | GPT-4o | Local High-Capability | Highest compliance with negative constraints and strict word limits. |
| **Creative Writing & Marketing** | All local models plateau | 4 | Claude 3.5 Sonnet / Gemini 1.5 Pro | External Cloud API | All open-weight models converge at 4/5 due to predictable instruction cadences. Outsource to cloud for high originality. |
| **Structured Output (JSON/YAML)** | `phi4:latest` / `llama3.1:8b` | 5 | GPT-4o-mini | Local Efficiency Baseline | Strict JSON schema extraction without conversational preamble or Markdown fence leakage. |
| **Multi-Turn Context Tracking** | `phi4:latest` | 5 | Claude 3.5 Sonnet | Local High-Capability | Maintains entity state and user constraints across conversational turns. |

---

## 2. Deployment Decision Matrix

### Workstation Tier A: Maximum Cognitive Capability
* **Default Choice:** `phi4:latest` (14.7B parameters, 9.1 GB on disk).
* **Overall Score:** 24/25 points across core categories.
* **When to use:** Complex logic, enterprise rule compliance, multi-turn reasoning, and applications where output accuracy takes precedence over generation speed.

### Workstation Tier B: Maximum Throughput & Energy Efficiency
* **Default Choice:** `llama3.1:8b` (8.0B parameters, 4.9 GB on disk).
* **Overall Score:** 22/25 points.
* **When to use:** Real-time linting, automated vulnerability review, background task processing, and resource-constrained edge deployments where low memory pressure and fast tokens/sec matter.

### Workstation Tier C: Creative Tasks Requiring High Originality
* **Default Choice:** External Cloud API (`claude-haiku-4-5-20251001` or `gpt-4o-mini`).
* **When to use:** Storytelling, high-stakes brand copywriting, and novel marketing angles where local open-weight models exhibit synthetic stylistic plateaus.

---

## 3. Repositories and Audit Receipts

* **Benchmark Scripts:** `scripts/run_benchmark.py` (v2 4-track engine)
* **External Model Harness:** `scripts/run_external.py`
* **Raw Run Logs:** `output/runs/2026-10-01-run-1.csv`
* **Academic Paper:** `output/report/uc12-academic-report-2026-10-01.html`
