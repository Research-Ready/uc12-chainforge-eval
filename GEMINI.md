# UC12 — Gemini Context

Read `COORDINATION.md` first. This file is your working brief.

## Your role

Content writer and academic analyst. You expand and refine the report text. You do not touch scripts, Docker, or infrastructure files.

## Your files

- `output/report/uc12-academic-report-YYYY-MM-DD.qmd` — the main academic report
- `output/report/references.bib` — bibliography (add citations here)
- `output/social-media/` — LinkedIn posts, report sections
- `output/templates/` — reusable templates
- `docs/` — documentation

## Report structure (current .qmd)

Sections already scaffolded:
1. Abstract
2. Introduction
3. Hypothesis
4. Methodology
5. Results
6. Discussion ← needs expansion
7. Conclusion ← needs expansion
8. Appendix

## Data source

All benchmark numbers come from:
`output/runs/2026-10-01-summary.json`

Scores are medians /5 across 3 runs, rated 1–5 by llama3.1:8b at temp 0.1.

Current results:

| Category | hermes3 | qwen3:14b | phi4 | llama3.1:8b |
|----------|---------|-----------|------|-------------|
| Reasoning | 4 | 5 | 5 | 4 |
| Code gen | 5 | 4 | 5 | 5 |
| Security | 5 | 4 | 5 | 5 |
| Creative | 4 | 4 | 4 | 4 |
| Instruction | 4 | 4 | 5 | 4 |
| **Total** | **22** | **21** | **24** | **22** |

Winner: phi4 (24/25). llama3.1:8b ties phi4 on 3 of 5 categories at 4.9 GB.

## Writing rules (enforced — no exceptions)

- First-person plural ("we found", "our results show")
- Numbers before interpretation: "phi4 scored 24/25 — higher than qwen3:14b (21/25)"
- Varied sentence length: short punches + longer analysis
- No em-dashes
- No contrastives ("it's not X, it's Y")
- No AI-language tells: no "delve", "leverage", "robust", "it is worth noting"
- Formal but readable — no bullet points in prose sections
- Cite real papers where possible (add to references.bib)

## Commit protocol

Commit your changes before handing back to Claude Code. Use:
```
git add output/report/ output/social-media/ docs/
git commit -m "content: <what you changed>"
```
