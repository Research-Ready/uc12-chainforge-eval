# UC12 — Forensic Test Protocol v1.0

> This protocol defines EXACTLY how to run the benchmark so any third party can reproduce the results.
> Before running: every field marked [FILL] must be completed. Do not run without filling them.

## Pre-run checklist (Infra Engineer owns this)

- [ ] ChainForge version: `chainforge --version` → [FILL: _____]
- [ ] Hardware: CPU [FILL], RAM [FILL], GPU [FILL / none]
- [ ] OS: [FILL]
- [ ] Run date: [FILL]
- [ ] All local models pulled and verified:

```bash
# Run this and paste output here:
ollama list
```

| Model | ID (first 8 chars) | Size |
|-------|-------------------|------|
| [FILL] | [FILL] | [FILL] |

- [ ] Prompt files committed to git. Record commit hash: [FILL]
- [ ] External models used (if any): [FILL]
- [ ] Temperature setting for all runs: **0.7** (default — change only if testing temperature sensitivity)
- [ ] Runs per prompt per model: **3** (take median score)

---

## Test categories and scoring rubrics

Each category uses a 1–5 rubric. Score each of 3 runs; record all 3 scores; report median.

### 1. Reasoning
**Prompt file:** `chainforge/prompts/reasoning.txt`
**Rubric:**
- 5: Correct answer with clear, correct logic chain
- 4: Correct answer, logic partially explained
- 3: Partially correct or correct answer with flawed logic
- 2: Incorrect answer but demonstrates reasoning attempt
- 1: No reasoning shown or completely wrong

### 2. Code Generation
**Prompt file:** `chainforge/prompts/code-gen.txt`
**Rubric:**
- 5: Code runs correctly, idiomatic, handles edge cases
- 4: Code runs correctly, minor style issues
- 3: Code runs with small fixes needed
- 2: Code has logic errors but structure is right
- 1: Non-functional or missing

### 3. Code Review
**Prompt file:** `chainforge/prompts/code-review.txt` *(use security.txt with review task)*
**Rubric:**
- 5: Finds all seeded bugs, correct severity, actionable fix
- 4: Finds major bugs, misses minor ones
- 3: Finds some bugs, misses critical one
- 2: Finds surface issues only
- 1: Misses all seeded bugs

### 4. Summarization
**Prompt file:** `chainforge/prompts/summarization.txt`
**Rubric:**
- 5: All key facts preserved, nothing hallucinated, correct length
- 4: All key facts, minor length deviation
- 3: Most key facts, 1 hallucination or omission
- 2: Several facts missed or one major hallucination
- 1: Fails to summarize or major hallucination

### 5. Classification
**Prompt file:** `chainforge/prompts/classification.txt`
**Rubric:**
- 5: Correct label, output is ONLY the label
- 4: Correct label with brief explanation (did not follow format)
- 3: Wrong label but plausible reasoning
- 2: Wrong label, no reasoning
- 1: Refuses or incoherent

### 6. Creative Writing
**Prompt file:** `chainforge/prompts/creative.txt`
**Rubric:**
- 5: Meets all constraints, genuinely original, no clichés
- 4: Meets constraints, competent but predictable
- 3: Breaks one constraint OR uses clichés
- 2: Breaks multiple constraints
- 1: Ignores constraints or produces filler

### 7. Factual QA
**Prompt file:** `chainforge/prompts/factual-qa.txt`
**Scoring:** Verify answer against ground-truth source (link required).
- 5: Correct + correctly calibrated confidence
- 4: Correct but overconfident or underconfident
- 3: Partially correct
- 2: Incorrect but acknowledges uncertainty
- 1: Incorrect and confident

### 8. Security Analysis
**Prompt file:** `chainforge/prompts/security.txt`
**Rubric:**
- 5: Finds all seeded vulnerabilities, correct severity, correct remediation
- 4: Finds all vulns, minor remediation gap
- 3: Misses one vuln
- 2: Finds only obvious vulns
- 1: Misses critical vuln or hallucinates non-existent vulns

### 9. Instruction Following
**Prompt file:** `chainforge/prompts/instruction.txt`
**Scoring:** Binary per constraint. Final score = (constraints met / total constraints) × 5, rounded.

### 10. Translation (NL ↔ EN)
**Prompt file:** `chainforge/prompts/translation.txt`
**Scoring:** Rate by a native speaker after the run.
- 5: Fluent, accurate, correct register
- 4: Accurate, minor phrasing issues
- 3: Accurate meaning, noticeable awkward phrasing
- 2: Some meaning lost
- 1: Meaning changed or wrong register

---

## Results table (Research Lead fills this after runs)

| Category | hermes3 | qwen3:14b | gemma3:27b | phi4 | deepseek-r1 | llama3.1:8b | [ext-1] | [ext-2] |
|----------|---------|-----------|-----------|------|------------|------------|---------|---------|
| Reasoning | | | | | | | | |
| Code Gen | | | | | | | | |
| Code Review | | | | | | | | |
| Summarization | | | | | | | | |
| Classification | | | | | | | | |
| Creative | | | | | | | | |
| Factual QA | | | | | | | | |
| Security | | | | | | | | |
| Instruction | | | | | | | | |
| Translation | | | | | | | | |
| **TOTAL** | | | | | | | | |
| **Avg** | | | | | | | | |

---

## Raw run log location

Save all ChainForge CSV exports to: `output/runs/YYYY-MM-DD-run-N.csv`
Name format: `2026-10-01-run-1.csv`

---

## Reproducibility statement (copy to report when filled)

> This benchmark was run on [FILL: hardware] on [FILL: date] using ChainForge [FILL: version].
> All prompts are in `chainforge/prompts/` at git commit [FILL: hash].
> Models were run at temperature 0.7 with 3 runs per task per model (median reported).
> Raw outputs are in `output/runs/`. To reproduce: clone the repo, follow `docs/setup.md`, and re-run the flows in `chainforge/flows/`.
