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

def patch_marker(content: str, marker_id: str, new_table: str) -> tuple[str, bool]:
    """Replace content between <!-- AUTO-TABLE: id --> markers. Returns (content, changed)."""
    marker     = f"<!-- AUTO-TABLE: {marker_id} -->"
    end_marker = f"<!-- /AUTO-TABLE: {marker_id} -->"
    if marker not in content:
        return content, False
    start = content.index(marker)
    if end_marker in content:
        end     = content.index(end_marker) + len(end_marker)
        content = content[:start] + marker + "\n\n" + new_table + "\n\n" + end_marker + content[end:]
    else:
        content = content[:start] + marker + "\n\n" + new_table + "\n\n" + content[start + len(marker):]
    return content, True


def build_security_table(data: dict) -> str | None:
    sec    = data.get("security_results", {})
    models = data.get("models", [])
    if not sec or not models:
        return None
    short  = [m.split(":")[0] for m in models]
    header = "| Category | " + " | ".join(short) + " |"
    sep    = "|----------|" + "|".join(["------"] * len(models)) + "|"
    rows   = []
    for cat, scores in sec.items():
        best  = max(scores.values()) if scores else 0
        cells = []
        for m in models:
            s = scores.get(m, scores.get(m.split(":")[0], "—"))
            cells.append(f"**{s}**" if s == best else str(s))
        rows.append(f"| {cat.replace('_', ' ').title()} | " + " | ".join(cells) + " |")
    return "\n".join([header, sep] + rows)


def build_execution_table(runs_dir: Path) -> str | None:
    files = sorted(runs_dir.glob("*-execution-bench.json"), reverse=True)
    if not files:
        return None
    with open(files[0]) as f:
        data = json.load(f)
    results = data.get("results", {})
    if not results:
        return None
    models = list(results.keys())
    short  = [m.split(":")[0] for m in models]
    header = "| Task | " + " | ".join(short) + " |"
    sep    = "|------|" + "|".join(["--------"] * len(models)) + "|"
    # Collect all task names
    tasks  = sorted({t for m in results.values() for t in m.keys()})
    rows   = []
    for task in tasks:
        cells = []
        for m in models:
            r = results[m].get(task, {})
            p = r.get("passed", 0)
            t = r.get("total", 1)
            cells.append(f"{p}/{t}")
        rows.append(f"| `{task}` | " + " | ".join(cells) + " |")
    # pass@1 summary row
    pass1 = {m: data.get("pass_at_1", {}).get(m, data.get("summary", {}).get(m, {}).get("pass_at_1", "—")) for m in models}
    rows.append("| **pass@1** | " + " | ".join(str(pass1[m]) for m in models) + " |")
    return "\n".join([header, sep] + rows)


def build_perturbation_table(runs_dir: Path) -> str | None:
    files = sorted(runs_dir.glob("*-perturbation-bench.json"), reverse=True)
    if not files:
        return None
    with open(files[0]) as f:
        data = json.load(f)
    by_model = data.get("by_model", {})
    if not by_model:
        return None
    models = list(by_model.keys())
    short  = [m.split(":")[0] for m in models]
    header = "| Problem | " + " | ".join(short) + " | Metric |"
    sep    = "|---------|" + "|".join(["-------"] * len(models)) + "|--------|"
    rows   = []
    problems = sorted({p for m in by_model.values() for p in m.keys()})
    for prob in problems:
        cells = []
        for m in models:
            d = by_model[m].get(prob, {}).get("delta", "—")
            cells.append(str(d))
        rows.append(f"| {prob.replace('_', ' ').title()} | " + " | ".join(cells) + " | Δ score |")
    # Mean delta row
    mean_row = []
    for m in models:
        vals = [v.get("delta") for v in by_model[m].values() if isinstance(v.get("delta"), (int, float))]
        mean_row.append(f"{sum(vals)/len(vals):.2f}" if vals else "—")
    rows.append("| **Mean Δ** | " + " | ".join(mean_row) + " | lower=better |")
    return "\n".join([header, sep] + rows)


def build_schema_table(runs_dir: Path) -> str | None:
    files = sorted(runs_dir.glob("*-schema-bench.json"), reverse=True)
    if not files:
        return None
    with open(files[0]) as f:
        data = json.load(f)
    by_model = data.get("by_model", {})
    if not by_model:
        return None
    models = list(by_model.keys())
    short  = [m.split(":")[0] for m in models]
    temps  = ["0.0", "0.5", "1.0"]
    header = "| Model | " + " | ".join(f"T={t} conf%" for t in temps) + " | T=0.0 key% | T=0.0 val% |"
    sep    = "|-------|" + "|".join(["----------"] * len(temps)) + "|-----------|-----------|"
    rows   = []
    for m, s in zip(models, short):
        row_cells = []
        for t in temps:
            c = by_model[m].get(t, by_model[m].get(f"T={t}", {})).get("conformance_rate", "—")
            row_cells.append(f"{c:.0%}" if isinstance(c, float) else str(c))
        k = by_model[m].get("0.0", by_model[m].get("T=0.0", {})).get("key_accuracy", "—")
        v = by_model[m].get("0.0", by_model[m].get("T=0.0", {})).get("value_accuracy", "—")
        rows.append(f"| {s} | " + " | ".join(row_cells) + f" | {f'{k:.0%}' if isinstance(k, float) else k} | {f'{v:.0%}' if isinstance(v, float) else v} |")
    return "\n".join([header, sep] + rows)


def patch_qmd(data: dict, date: str):
    """Find .qmd and patch all AUTO-TABLE markers with fresh data."""
    existing = sorted(REPORT_DIR.glob("uc12-academic-report-*.qmd"), reverse=True)
    if not existing:
        print("No existing .qmd found — write the report first.")
        return None

    qmd_path = existing[0]
    content  = qmd_path.read_text()
    changed  = False

    # Cognitive results
    results   = data.get("cognitive_results") or data.get("results", {})
    models    = data["models"]
    cog_table = build_results_table(results, models)
    content, ok = patch_marker(content, "cognitive", cog_table)
    if ok:
        print(f"  Patched cognitive table")
        changed = True
    else:
        print(f"  No <!-- AUTO-TABLE: cognitive --> marker found")

    # Security results
    sec_table = build_security_table(data)
    if sec_table:
        content, ok = patch_marker(content, "security", sec_table)
        if ok:
            print(f"  Patched security table")
            changed = True
    else:
        print(f"  Security results absent — security table skipped")

    # Execution bench
    exec_table = build_execution_table(RUNS)
    if exec_table:
        content, ok = patch_marker(content, "execution", exec_table)
        if ok:
            print(f"  Patched execution table")
            changed = True

    # Perturbation bench
    pert_table = build_perturbation_table(RUNS)
    if pert_table:
        content, ok = patch_marker(content, "perturbation", pert_table)
        if ok:
            print(f"  Patched perturbation table")
            changed = True

    # Schema bench
    schema_table = build_schema_table(RUNS)
    if schema_table:
        content, ok = patch_marker(content, "schema", schema_table)
        if ok:
            print(f"  Patched schema table")
            changed = True

    if changed:
        qmd_path.write_text(content)
        print(f"Saved {qmd_path.name}")

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
