#!/usr/bin/env python3
"""
UC12 — Academic report pipeline
Loads latest v2 summary JSON → regenerates charts → renders Quarto .qmd to HTML + PDF.

Prose sections come from Gemini's .qmd (output/report/uc12-academic-report-*.qmd).
This script handles the data tables and chart references — not the written analysis.

Usage: python3 scripts/make_academic_report.py
"""
import json
import subprocess
import sys
from pathlib import Path

BASE       = Path(__file__).parent.parent
RUNS       = BASE / "output" / "runs"
REPORT_DIR = BASE / "output" / "report"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

def load_latest() -> tuple[dict, str]:
    for pattern in ("*-summary-v2.json", "*-summary.json"):
        files = sorted(RUNS.glob(pattern), reverse=True)
        if files:
            with open(files[0]) as f:
                return json.load(f), files[0].name
    sys.exit("No summary JSON found. Run run_benchmark.py first.")

def regenerate_charts():
    print("Regenerating charts...")
    result = subprocess.run(
        [sys.executable, str(BASE / "scripts" / "make_charts.py")],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"Chart warning: {result.stderr[-300:]}")
    else:
        print(result.stdout.strip())

def build_results_table(results: dict, models: list[str]) -> str:
    short = [m.split(":")[0] for m in models]
    header = "| Category | " + " | ".join(short) + " |"
    sep    = "|----------|" + "|".join(["------"] * len(models)) + "|"
    rows   = []
    for cat, scores in results.items():
        best = max(scores.values())
        cells = []
        for m in models:
            s = scores.get(m, scores.get(m.split(":")[0], 0))
            cells.append(f"**{s}**" if s == best else str(s))
        rows.append(f"| {cat.replace('_',' ').title()} | " + " | ".join(cells) + " |")
    totals = {m: sum(results[c].get(m, results[c].get(m.split(":")[0], 0))
                     for c in results) for m in models}
    best_total = max(totals.values())
    total_cells = [f"**{totals[m]}**" if totals[m] == best_total else str(totals[m])
                   for m in models]
    rows.append("| **Total** | " + " | ".join(total_cells) + " |")
    return "\n".join([header, sep] + rows)

def patch_qmd(data: dict, date: str):
    """Find Gemini's .qmd and patch the data tables section with fresh numbers."""
    existing = sorted(REPORT_DIR.glob("uc12-academic-report-*.qmd"), reverse=True)
    if not existing:
        print("No existing .qmd found — Gemini must write the report first.")
        return None

    qmd_path = existing[0]
    content  = qmd_path.read_text()

    results = data.get("cognitive_results") or data.get("results", {})
    models  = data["models"]

    new_table = build_results_table(results, models)
    marker    = "<!-- AUTO-TABLE: cognitive -->"

    if marker in content:
        # Replace between markers
        start = content.index(marker)
        end_marker = "<!-- /AUTO-TABLE: cognitive -->"
        if end_marker in content:
            end = content.index(end_marker) + len(end_marker)
            content = content[:start] + marker + "\n\n" + new_table + "\n\n" + end_marker + content[end:]
        else:
            content = content[:start] + marker + "\n\n" + new_table + "\n\n" + content[start + len(marker):]
        qmd_path.write_text(content)
        print(f"Patched data table in {qmd_path.name}")
    else:
        print(f"No {marker!r} in .qmd — table patch skipped. Ask Gemini to add the marker.")

    return qmd_path

def render(qmd_path: Path, fmt: str):
    result = subprocess.run(
        ["quarto", "render", str(qmd_path), "--to", fmt],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"{fmt.upper()} render error: {result.stderr[-400:]}")
        return False
    ext = "html" if fmt == "html" else "pdf"
    print(f"{fmt.upper()}: {qmd_path.with_suffix('.' + ext)}")
    return True

def main():
    data, source = load_latest()
    date = data["date"]
    print(f"UC12 Academic Report — {date} (source: {source})\n")

    regenerate_charts()
    qmd_path = patch_qmd(data, date)

    if qmd_path is None:
        sys.exit("No .qmd to render.")

    print("\nRendering...")
    render(qmd_path, "html")
    render(qmd_path, "pdf")

    print(f"\nDone. Open:")
    print(f"  xdg-open {qmd_path.with_suffix('.html')}")

if __name__ == "__main__":
    main()
