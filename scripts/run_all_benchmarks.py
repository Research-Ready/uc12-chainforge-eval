#!/usr/bin/env python3
"""
UC12 — C20: Unified Benchmark Runner
Runs all benchmark scripts in sequence and produces a combined summary JSON.

Scripts run (in order):
  1. run_benchmark.py       — 4-track cognitive + security + telemetry
  2. run_external.py        — external API models (Claude Haiku, GPT-4o-mini, Gemini Flash)
  3. run_execution_bench.py — code execution pass@1
  4. run_perturbation.py    — semantic invariance delta
  5. run_schema_bench.py    — JSON conformance across temperatures

Usage:
  python3 scripts/run_all_benchmarks.py [--quick] [--skip-external]
  --quick          Run each script in quick mode
  --skip-external  Skip run_external.py (no API keys configured)
"""

import json
import subprocess
import sys
import datetime
from pathlib import Path

BASE   = Path(__file__).parent.parent
SCRIPTS = BASE / "scripts"
OUTPUT  = BASE / "output" / "runs"
OUTPUT.mkdir(parents=True, exist_ok=True)

QUICK         = "--quick" in sys.argv
SKIP_EXTERNAL = "--skip-external" in sys.argv

PIPELINE = [
    {
        "id":     "cognitive",
        "script": "run_benchmark.py",
        "args":   ["--quick"] if QUICK else [],
        "output": "*-summary-v2.json",
        "skip":   False,
    },
    {
        "id":     "external",
        "script": "run_external.py",
        "args":   [],
        "output": "*-external.json",
        "skip":   SKIP_EXTERNAL,
    },
    {
        "id":     "execution",
        "script": "run_execution_bench.py",
        "args":   ["--quick"] if QUICK else [],
        "output": "*-execution-bench.json",
        "skip":   False,
    },
    {
        "id":     "perturbation",
        "script": "run_perturbation.py",
        "args":   ["--quick"] if QUICK else [],
        "output": "*-perturbation-bench.json",
        "skip":   False,
    },
    {
        "id":     "schema",
        "script": "run_schema_bench.py",
        "args":   ["--quick"] if QUICK else [],
        "output": "*-schema-bench.json",
        "skip":   False,
    },
]


def run_script(script: str, args: list[str]) -> tuple[bool, str]:
    cmd = [sys.executable, str(SCRIPTS / script)] + args
    print(f"\n{'='*60}")
    print(f"Running: {script} {' '.join(args)}")
    print("=" * 60)
    result = subprocess.run(cmd, cwd=BASE)
    return result.returncode == 0, script


def load_latest(pattern: str) -> dict | None:
    files = sorted(OUTPUT.glob(pattern), reverse=True)
    if not files:
        return None
    with open(files[0]) as f:
        return json.load(f)


def main():
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    print(f"UC12 Full Benchmark Suite — {date_str}")
    print(f"Mode: {'quick' if QUICK else 'full'}")
    if SKIP_EXTERNAL:
        print("External models: skipped")
    print()

    results_summary = {"date": date_str, "stages": {}, "errors": []}

    for stage in PIPELINE:
        if stage["skip"]:
            print(f"\nSkipping {stage['id']} ({stage['script']})")
            results_summary["stages"][stage["id"]] = "skipped"
            continue

        ok, script = run_script(stage["script"], stage["args"])
        results_summary["stages"][stage["id"]] = "ok" if ok else "error"
        if not ok:
            results_summary["errors"].append(script)
            print(f"\nWARNING: {script} exited with errors — continuing pipeline.")

    # Load and merge all outputs into one combined summary
    combined = {"date": date_str, "pipeline": results_summary["stages"]}

    for stage in PIPELINE:
        if stage["skip"]:
            continue
        data = load_latest(stage["output"])
        if data:
            combined[stage["id"]] = {
                k: v for k, v in data.items()
                if k not in ("date",)
            }

    out_path = OUTPUT / f"{date_str}-combined-summary.json"
    out_path.write_text(json.dumps(combined, indent=2))

    print(f"\n{'='*60}")
    print("PIPELINE COMPLETE")
    print("=" * 60)
    for stage_id, status in results_summary["stages"].items():
        icon = "OK" if status == "ok" else ("--" if status == "skipped" else "ERR")
        print(f"  [{icon}] {stage_id}")
    if results_summary["errors"]:
        print(f"\nErrors in: {', '.join(results_summary['errors'])}")
    print(f"\nCombined JSON: {out_path}")
    print("\nNext step:")
    print(f"  python3 scripts/make_academic_report.py")


if __name__ == "__main__":
    main()
