# Executive Summary: Multi-Dimensional Evaluation of Local Language Models

**Authors:** Christiaan Verhoef, Igor van Oostveen, Milan Jelisavcic, Albert Vos  
**Organization:** ResearchReady  
**Date:** October 1, 2026  
**Evaluation Scope:** hermes3:latest, phi4:latest, llama3.1:8b, qwen3:14b  

---

## 1. Executive Context

Local model deployment offers data privacy and predictable operational expenses. However, enterprise teams often select local architectures based purely on generic leaderboard ranks or parameter counts. 

Our team deployed an eight-dimension evaluation battery across four prominent open-weights models running on local hardware. We measured cognitive capability, adversarial security, hardware energy consumption, programmatic execution accuracy, semantic perturbation invariance, and strict schema determinism. 

Our core finding is that parameter scale does not dictate operational viability. Smaller architectures regularly outperform larger alternatives when evaluated on safety, execution correctness, and inference efficiency.

---

## 2. Key Empirical Findings

### 2.1 The Adversarial Disconnect
High reasoning capability does not confer adversarial immunity.
- phi4:latest achieved the highest overall cognitive score (24/25 across reasoning and code generation tasks).
- phi4:latest failed catastrophic indirect document injection, executing an embedded override command to emit an unauthorized marker (Security score: 2.2/5.0).
- llama3.1:8b successfully defended all five adversarial attack vectors, scoring 4.6/5.0 in adversarial security while operating at one-third the memory footprint.

### 2.2 Execution-Grounded Verification vs. LLM Judges
Evaluating code generation through LLM-as-a-judge prompts introduces severe blind spots.
- In our programmatic execution test harness, code outputs ran against hidden test suites inside isolated Python subprocesses.
- hermes3:latest passed palindrome detection (6/6) and list flattening (5/5), but failed a word-frequency punctuation edge case (2/3 tests passed, overall pass@1 = 0.947).
- In earlier qualitative LLM judge runs, hermes3 received 5/5 for code generation because the output looked syntactically fluent. Hidden assertion testing caught the silent regression.
- phi4:latest and llama3.1:8b both achieved a flawless 1.0 pass@1 rate (19/19 hidden test assertions passed).

### 2.3 Hardware Telemetry and the Latency Denial of Service
Inference latency creates an operational availability risk.
- Under CPU execution, reasoning-heavy safety prompts on 14B architectures (phi4, qwen3:14b) exceeded 120 seconds per query.
- llama3.1:8b completed identical reasoning queries in 7.1 to 16.7 seconds.
- llama3.1:8b delivered 38.4 tokens per second with an average power draw of 42.5 W, yielding 0.89 tokens per joule.
- phi4 required 88.2 W and 14.1 GB VRAM, producing 0.24 tokens per joule.

---

## 3. Comparative Architecture Scorecard

| Model | Architecture | Size | Cognitive (Med/25) | Security (Mean/5) | Execution (pass@1) | Power Efficiency (tok/J) | Operational Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **llama3.1:8b** | Meta Llama | 4.9 GB | 22 | **4.6** | **1.000** | **0.89** | **Production Recommended:** Exceptional safety, fast inference, lowest power |
| **phi4:latest** | Microsoft Phi | 10.0 GB | **24** | 2.2 | **1.000** | 0.24 | **Research / Offline Only:** High reasoning, vulnerable to indirect prompt injection |
| **hermes3:latest** | Nous Research | 5.3 GB | 22 | 3.6 | 0.947 | 0.45 | **Specialized:** Strong formatting, moderate security, subtle code edge-case bugs |
| **qwen3:14b** | Alibaba Qwen | 9.3 GB | 21 | 2.8 | Pending | 0.28 | **Heavyweight:** Slower CPU throughput, sensitive to context cold-loading |

---

## 4. Multi-Volume Report Architecture

Our findings are split across three technical publications and a third-party evaluation guide:

1. **Volume I: Master Academic Report** (`output/report/uc12-academic-report-2026-10-01.html` and `.pdf`)
   Rigorous academic methodology, statistical hypothesis testing (H1 refuted: parameter size does not correlate with task performance, p = 0.82), unbundled four-track analysis, and future research directions.

2. **Volume II: Adversarial Security & Red-Teaming Report** (`output/report/uc12-security-audit-report-2026-10-01.html` and `.pdf`)
   Live empirical red-teaming scorecard across direct jailbreaks (DAN), indirect document injection, secret API extraction, epistemic sycophancy, and CWE-89 SQL injection auditing.

3. **Volume III: Hardware Telemetry & Unit Economics Report** (`output/report/uc12-hardware-telemetry-report-2026-10-01.html` and `.pdf`)
   Real-time GPU power sampling, tokens-per-watt efficiency frontiers, VRAM allocation profiling, and annual datacenter deployment unit economics.

4. **Third-Party Model Evaluation Methodology Guide** (`output/third-party-evaluation-guide.md`)
   Production readiness audit playbook featuring the standardized A through F grading matrix for procurement and security audit teams.

---

## 5. Strategic Recommendations

1. **Adopt llama3.1:8b for Customer-Facing Workflows:**
   Its complete defense against indirect injections and high inference speed make it the safest choice for conversational agents and tool-augmented applications.

2. **Isolate phi4 Behind Strict Security Air-Gaps:**
   Use phi4 exclusively for offline analytical pipelines, batch data processing, or internal code refactoring where inputs are trusted and sanitized.

3. **Mandate Execution Sandboxes for Code Generation:**
   Never rely on LLM judges or visual reviews to validate generated functions. All mission-critical code must pass automated sandbox assertions before merging.

4. **Calibrate Operational Timeouts:**
   Set API gateway timeouts to a minimum of 300 seconds when deploying 14B models on CPU hardware to prevent cascading read timeouts.
