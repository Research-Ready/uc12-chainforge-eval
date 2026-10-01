#!/usr/bin/env python3
"""
UC12 — Auto Report Generator
Reads latest benchmark JSON → generates Quarto .qmd → renders to HTML + PDF.

Usage: python3 scripts/make_report.py
Output: output/report/uc12-benchmark-YYYY-MM-DD.html  (+ .pdf)
"""
import json
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).parent.parent
RUNS = BASE / "output" / "runs"
REPORT_DIR = BASE / "output" / "report"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

def load_latest():
    files = sorted(RUNS.glob("*-summary.json"), reverse=True)
    if not files:
        sys.exit("No summary JSON found. Run run_benchmark.py first.")
    with open(files[0]) as f:
        return json.load(f)

def build_qmd(data: dict) -> str:
    date = data["date"]
    models = [m.split(":")[0] for m in data["models"]]
    categories = list(data["results"].keys())
    results = {cat: {m.split(":")[0]: s for m, s in scores.items()}
               for cat, scores in data["results"].items()}
    totals = {m.split(":")[0]: t for m, t in data["totals"].items()}
    winner = data["winner"].split(":")[0]

    # Build markdown table
    header = "| Category | " + " | ".join(models) + " |"
    sep    = "|----------|" + "|".join(["------"] * len(models)) + "|"
    rows   = []
    for cat in categories:
        best_score = max(results[cat].values())
        cells = []
        for m in models:
            s = results[cat][m]
            cells.append(f"**{s}**" if s == best_score else str(s))
        rows.append(f"| {cat.replace('_',' ').title()} | " + " | ".join(cells) + " |")
    total_row = "| **Total** | " + " | ".join(
        f"**{totals[m]}**" if totals[m] == max(totals.values()) else str(totals[m])
        for m in models
    ) + " |"
    table = "\n".join([header, sep] + rows + [total_row])

    # Build winner analysis
    cat_winners = {}
    for cat in categories:
        best = max(results[cat], key=results[cat].get)
        cat_winners[cat] = (best, results[cat][best])

    findings = []
    for cat, (mod, score) in cat_winners.items():
        findings.append(f"- **{cat.replace('_',' ').title()}**: {mod} ({score}/5)")

    flat_cats = [c for c, (m, s) in cat_winners.items() if len(set(results[c].values())) == 1]
    flat_note = ""
    if flat_cats:
        flat_note = (
            f"\n> **Notable:** {', '.join(c.replace('_',' ').title() for c in flat_cats)} "
            f"scored identically across all models — no local model differentiates here."
        )

    # Read report section if it exists
    section_files = sorted((BASE / "output" / "social-media").glob(f"{date}-report-section.md"), reverse=True)
    report_body = ""
    if section_files:
        raw = section_files[0].read_text()
        # Extract just the "Report Section" content
        if "## Report Section" in raw:
            report_body = raw.split("## Report Section")[1].strip()

    return f"""---
title: "ResearchReady AI Model Benchmark"
subtitle: "Local LLM Evaluation — {date}"
author: "ResearchReady UC12"
date: "{date}"
format:
  html:
    toc: true
    toc-depth: 3
    theme: flatly
    embed-resources: true
  pdf:
    toc: true
    colorlinks: true
execute:
  echo: false
  warning: false
---

## Summary

**{winner}** achieved the highest overall score ({totals[winner]}/{len(categories)*5}) across {len(categories)} task categories, tested on local hardware (AMD Ryzen 7 8845HS, RTX 4060 8 GB, 46 GB RAM) using [ChainForge](https://github.com/ianarawjo/ChainForge).

## Results

{table}

*Bold = category winner. Scores are medians across 3 runs, rated 1–5 by LLM-as-judge (llama3.1:8b).*

## Category Winners

{chr(10).join(findings)}
{flat_note}

## Analysis

{report_body if report_body else "_Run generate_report.py to populate this section._"}

## Methodology

- **Tool:** ChainForge {date} via Ollama OpenAI-compatible API (`localhost:11434/v1`)
- **Temperature:** 0.7 for all models
- **Runs per task:** 3 (median reported)
- **Judge model:** llama3.1:8b at temperature 0.1
- **Scoring rubric:** 1–5 per category (see `docs/test-protocol.md`)

### Models tested

| Model | Size | Type |
|-------|------|------|
| hermes3:latest | 4.7 GB | Local (Ollama) |
| qwen3:14b | 9.3 GB | Local (Ollama) |
| phi4:latest | 9.1 GB | Local (Ollama) |
| llama3.1:8b | 4.9 GB | Local (Ollama) |

## Reproduce This

```bash
git clone https://github.com/Research-Ready/uc12-chainforge-eval
cp .env.example .env
./start.sh          # starts ChainForge + Ollama via Docker
python3 scripts/run_benchmark.py
python3 scripts/make_report.py
```

Raw data: `output/runs/{date}-run-1.csv`

---
*ResearchReady — [github.com/Research-Ready/uc12-chainforge-eval](https://github.com/Research-Ready/uc12-chainforge-eval)*
"""

def main():
    data = load_latest()
    date = data["date"]
    qmd_path = REPORT_DIR / f"uc12-benchmark-{date}.qmd"

    print(f"Building report for {date}...")
    qmd_path.write_text(build_qmd(data))
    print(f"Quarto source: {qmd_path}")

    print("Rendering HTML...")
    result = subprocess.run(
        ["quarto", "render", str(qmd_path), "--to", "html"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("HTML render error:", result.stderr[-500:])
    else:
        print(f"HTML: {REPORT_DIR}/uc12-benchmark-{date}.html")

    print("Rendering PDF...")
    result = subprocess.run(
        ["quarto", "render", str(qmd_path), "--to", "pdf"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("PDF render error (install tinytex: quarto install tinytex):", result.stderr[-300:])
    else:
        print(f"PDF: {REPORT_DIR}/uc12-benchmark-{date}.pdf")

    print("\nDone. Open report:")
    print(f"  xdg-open {REPORT_DIR}/uc12-benchmark-{date}.html")

if __name__ == "__main__":
    main()
