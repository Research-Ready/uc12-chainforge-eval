# ResearchReady AI Model Benchmark — [FILL: Date]

## Executive Summary

[FILL: 2-3 sentences summarizing the most important findings and which model(s) won. Example: "We benchmarked 8 open-source AI models across 10 task categories. Model X emerged as the strongest all-around performer, while Model Y specialized in coding tasks. On average, local models scored within 1 point of commercial APIs."]

## Methodology

We used **ChainForge** [FILL: version], running on [FILL: hardware specs], to evaluate multiple AI models across [FILL: number] task categories. Each model was tested [FILL: number of trials per category] times per category using identical prompts. Scoring followed rubrics defined in our test protocol with a 5-point scale (1=fails, 5=excellent). Full methodological details and reproducibility instructions are available in `docs/test-protocol.md` and `docs/setup.md`. Benchmark run: [FILL: date], Git commit [FILL: commit hash].

## Models Tested

| Model | Type | Parameters | Provider |
|-------|------|------------|----------|
| [FILL: Model A] | [FILL: local/external] | [FILL: 7B/13B/etc] | [FILL: organization] |
| [FILL: Model B] | [FILL: local/external] | [FILL: 7B/13B/etc] | [FILL: organization] |
| [FILL: Model C] | [FILL: local/external] | [FILL: 7B/13B/etc] | [FILL: organization] |
| [FILL: Model D] | [FILL: local/external] | [FILL: 7B/13B/etc] | [FILL: organization] |
| [FILL: Model E] | [FILL: local/external] | [FILL: 7B/13B/etc] | [FILL: organization] |

## Results by Category

### Category 1: [FILL: Category Name]

**Best model:** [FILL: Model Name] (score: [FILL: X]/5)

[FILL: One sentence of analysis. Example: "This model demonstrated superior reasoning on multi-step problems and provided well-structured outputs."]

### Category 2: [FILL: Category Name]

**Best model:** [FILL: Model Name] (score: [FILL: X]/5)

[FILL: One sentence of analysis.]

### Category 3: [FILL: Category Name]

**Best model:** [FILL: Model Name] (score: [FILL: X]/5)

[FILL: One sentence of analysis.]

### Category 4: [FILL: Category Name]

**Best model:** [FILL: Model Name] (score: [FILL: X]/5)

[FILL: One sentence of analysis.]

### Category 5: [FILL: Category Name]

**Best model:** [FILL: Model Name] (score: [FILL: X]/5)

[FILL: One sentence of analysis.]

### Category 6: [FILL: Category Name]

**Best model:** [FILL: Model Name] (score: [FILL: X]/5)

[FILL: One sentence of analysis.]

### Category 7: [FILL: Category Name]

**Best model:** [FILL: Model Name] (score: [FILL: X]/5)

[FILL: One sentence of analysis.]

### Category 8: [FILL: Category Name]

**Best model:** [FILL: Model Name] (score: [FILL: X]/5)

[FILL: One sentence of analysis.]

### Category 9: [FILL: Category Name]

**Best model:** [FILL: Model Name] (score: [FILL: X]/5)

[FILL: One sentence of analysis.]

### Category 10: [FILL: Category Name]

**Best model:** [FILL: Model Name] (score: [FILL: X]/5)

[FILL: One sentence of analysis.]

## Overall Rankings

Copy your completed results table from `docs/test-protocol.md` here. Table should show all models and their median score in each category, plus overall average.

| Model | [Category 1] | [Category 2] | [Category 3] | [Category 4] | [Category 5] | [Category 6] | [Category 7] | [Category 8] | [Category 9] | [Category 10] | **Average** |
|-------|---|---|---|---|---|---|---|---|---|---|---|
| [FILL: Model A] | [FILL] | [FILL] | [FILL] | [FILL] | [FILL] | [FILL] | [FILL] | [FILL] | [FILL] | [FILL] | [FILL] |
| [FILL: Model B] | [FILL] | [FILL] | [FILL] | [FILL] | [FILL] | [FILL] | [FILL] | [FILL] | [FILL] | [FILL] | [FILL] |
| [FILL: Model C] | [FILL] | [FILL] | [FILL] | [FILL] | [FILL] | [FILL] | [FILL] | [FILL] | [FILL] | [FILL] | [FILL] |
| [FILL: Model D] | [FILL] | [FILL] | [FILL] | [FILL] | [FILL] | [FILL] | [FILL] | [FILL] | [FILL] | [FILL] | [FILL] |
| [FILL: Model E] | [FILL] | [FILL] | [FILL] | [FILL] | [FILL] | [FILL] | [FILL] | [FILL] | [FILL] | [FILL] | [FILL] |

## Key Findings

- [FILL: Most important finding #1]
- [FILL: Most important finding #2]
- [FILL: Most important finding #3]
- [FILL: Most important finding #4]
- [FILL: Most important finding #5]

## Recommended Model per Use Case

| Use Case | Recommended Model | Why |
|----------|-------------------|-----|
| Coding | [FILL: Model Name] | [FILL: Reasoning — e.g., "Highest score on code generation (4.8/5), consistent across all code categories."] |
| Writing | [FILL: Model Name] | [FILL: Reasoning] |
| Factual Research | [FILL: Model Name] | [FILL: Reasoning] |
| Security Review | [FILL: Model Name] | [FILL: Reasoning] |
| Classification/Automation | [FILL: Model Name] | [FILL: Reasoning] |
| Multilingual Work | [FILL: Model Name] | [FILL: Reasoning] |

## How to Reproduce

This benchmark is fully reproducible. To re-run:

1. Clone or download this repository
2. Follow setup instructions in `docs/setup.md`
3. Start the Docker stack: `./start.sh`
4. Open the test protocol: `docs/test-protocol.md`
5. Follow the testing procedure step-by-step
6. Record scores in the same rubrics provided
7. Compare your results to those in this report

All model versions, hardware specs, and ChainForge settings are documented in `docs/test-protocol.md` to ensure reproducibility.

## About ResearchReady

[FILL: 2 sentences about ResearchReady. Example: "ResearchReady is a multi-use-case AI platform for evaluating, benchmarking, and deploying AI models in production. We publish transparent, reproducible benchmarks to help teams choose the right model for their specific task."]

---

**Report generated:** [FILL: timestamp]
**Data location:** `output/runs/`
**Raw test protocol:** `docs/test-protocol.md`
**Reproducibility guide:** `docs/setup.md`
