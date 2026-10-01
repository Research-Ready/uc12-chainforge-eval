#!/usr/bin/env python3
"""
UC12 — C21: Master Artifact Compiler
Runs the full report-build pipeline across all three Quarto volumes:
  1. Regenerate all SVG charts (make_charts.py)
  2. Patch ChainForge flow descriptions into master .qmd (describe_flows.py --patch)
  3. Patch cognitive results table into master .qmd (same logic as make_academic_report.py)
  4. Render all three volumes to HTML and PDF

Volumes:
  - uc12-academic-report-*.qmd          (master)
  - uc12-security-audit-report-*.qmd    (security)
  - uc12-hardware-telemetry-report-*.qmd (telemetry)

Usage:
  python3 scripts/make_all_reports.py [--skip-render]
  --skip-render   Patch data and flows but skip quarto rendering
"""

import json
import subprocess
import sys
from pathlib import Path

BASE       = Path(__file__).parent.parent
SCRIPTS    = BASE / "scripts"
RUNS       = BASE / "output" / "runs"
REPORT_DIR = BASE / "output" / "report"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

SKIP_RENDER = "--skip-render" in sys.argv


def run(cmd: list[str], label: str) -> bool:
    print(f"\n[{label}]")
    result = subprocess.run(cmd, cwd=BASE)
    ok = result.returncode == 0
    if not ok:
        print(f"  WARNING: {label} exited with code {result.returncode}")
    return ok


def load_latest() -> tuple[dict, str] | tuple[None, None]:
    for pattern in ("*-combined-summary.json", "*-summary-v2.json", "*-summary.json"):
        files = sorted(RUNS.glob(pattern), reverse=True)
        if files:
            with open(files[0]) as f:
                return json.load(f), files[0].name
    return None, None


def build_results_table(results: dict, models: list[str]) -> str:
    short  = [m.split(":")[0] for m in models]
    header = "| Category | " + " | ".join(short) + " |"
    sep    = "|----------|" + "|".join(["------"] * len(models)) + "|"
    rows   = []
    for cat, scores in results.items():
        best  = max(scores.values())
        cells = []
        for m in models:
            s = scores.get(m, scores.get(m.split(":")[0], 0))
            cells.append(f"**{s}**" if s == best else str(s))
        rows.append(f"| {cat.replace('_', ' ').title()} | " + " | ".join(cells) + " |")
    totals     = {m: sum(r.get(m, r.get(m.split(":")[0], 0)) for r in results.values()) for m in models}
    best_total = max(totals.values()) if totals else 0
    total_row  = "| **Total** | " + " | ".join(
        f"**{totals[m]}**" if totals[m] == best_total else str(totals[m]) for m in models
    ) + " |"
    return "\n".join([header, sep] + rows + [total_row])


def patch_cognitive_table(data: dict) -> bool:
    existing = sorted(REPORT_DIR.glob("uc12-academic-report-*.qmd"), reverse=True)
    if not existing:
        print("  No master .qmd found — skipping cognitive table patch.")
        return False

    qmd_path = existing[0]
    content  = qmd_path.read_text()
    results  = data.get("cognitive_results") or data.get("results", {})
    models   = data.get("models", [])

    if not results or not models:
        print("  No cognitive_results/models in JSON — skipping table patch.")
        return False

    new_table  = build_results_table(results, models)
    marker     = "<!-- AUTO-TABLE: cognitive -->"
    end_marker = "<!-- /AUTO-TABLE: cognitive -->"

    if marker not in content:
        print(f"  No {marker!r} in {qmd_path.name} — table patch skipped.")
        return False

    start = content.index(marker)
    if end_marker in content:
        end     = content.index(end_marker) + len(end_marker)
        content = content[:start] + marker + "\n\n" + new_table + "\n\n" + end_marker + content[end:]
    else:
        content = content[:start] + marker + "\n\n" + new_table + "\n\n" + content[start + len(marker):]

    qmd_path.write_text(content)
    print(f"  Patched cognitive table in {qmd_path.name}")
    return True


def render_volume(qmd_path: Path, fmt: str) -> bool:
    result = subprocess.run(
        ["quarto", "render", str(qmd_path), "--to", fmt],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"  {fmt.upper()} render error ({qmd_path.name}): {result.stderr[-400:]}")
        return False
    ext = "html" if fmt == "html" else "pdf"
    out = qmd_path.with_suffix("." + ext)
    print(f"  {fmt.upper()}: {out}")
    return True


def main():
    import datetime
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    print(f"UC12 Master Report Compiler — {date_str}")
    errors = []

    # Step 1: Regenerate charts
    ok = run([sys.executable, str(SCRIPTS / "make_charts.py")], "Charts")
    if not ok:
        errors.append("make_charts.py")

    # Step 2: Patch ChainForge flow descriptions into master .qmd
    ok = run(
        [sys.executable, str(SCRIPTS / "describe_flows.py"), "--patch"],
        "ChainForge flows patch",
    )
    if not ok:
        errors.append("describe_flows.py --patch")

    # Step 3: Patch cognitive results table
    data, source = load_latest()
    if data:
        print(f"\n[Cognitive table patch] source: {source}")
        patch_cognitive_table(data)
    else:
        print("\n[Cognitive table patch] No JSON found — skipped.")

    if SKIP_RENDER:
        print("\n--skip-render set — skipping Quarto rendering.")
    else:
        # Step 4: Render all three volumes
        volumes = sorted(REPORT_DIR.glob("uc12-*-report-*.qmd"), reverse=True)
        seen    = set()
        unique  = []
        for v in volumes:
            key = v.name.rsplit("-", 1)[0]   # strip date suffix variant
            if key not in seen:
                seen.add(key)
                unique.append(v)

        if not unique:
            print("\nNo .qmd volumes found — nothing to render.")
        else:
            print(f"\n[Quarto render] {len(unique)} volume(s)")
            for vol in unique:
                for fmt in ("html", "pdf"):
                    ok = render_volume(vol, fmt)
                    if not ok:
                        errors.append(f"{vol.name} ({fmt})")

    print(f"\n{'='*60}")
    print("REPORT COMPILER COMPLETE")
    print("=" * 60)
    if errors:
        print(f"Errors in: {', '.join(errors)}")
    else:
        print("All steps OK.")
    print("\nNext step:")
    print("  python3 scripts/run_all_benchmarks.py --quick  # fresh data run")


if __name__ == "__main__":
    main()
