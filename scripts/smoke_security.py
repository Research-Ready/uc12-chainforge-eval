#!/usr/bin/env python3
"""
UC12 — Focused smoke run of the 8 deep red-team security categories.

Runs ONLY the new attack surfaces (obfuscation, crescendo, cipher-laundering,
steganography, many-shot, prompt-extraction, memorization, dos) against the
4 local models, 1 run each, and prints a median-score matrix.

Results are written incrementally so a timeout still leaves partial data.

Usage:
  python3 scripts/smoke_security.py               # all 8 categories, 1 run
  python3 scripts/smoke_security.py --limit 2     # cap 2 cases per category
  python3 scripts/smoke_security.py --cat dos_resource
"""

import json
import sys
from pathlib import Path
from statistics import median

BASE = Path(__file__).parent.parent
sys.path.insert(0, str(BASE / "scripts"))

import run_benchmark as rb  # noqa: E402

NEW_CATEGORIES = [
    "obfuscation_evasion",
    "crescendo_escalation",
    "cipher_laundering",
    "steganographic_injection",
    "many_shot_jailbreak",
    "prompt_extraction",
    "memorization",
    "dos_resource",
]

OUT = BASE / "output" / "runs" / "smoke-security-new-categories.json"


def parse_args():
    limit = None
    cats = NEW_CATEGORIES
    args = sys.argv[1:]
    for i, a in enumerate(args):
        if a == "--limit" and i + 1 < len(args):
            limit = int(args[i + 1])
        if a == "--cat" and i + 1 < len(args):
            cats = [args[i + 1]]
    return cats, limit


def run_category(cat, config, limit):
    results = {}
    print(f"\n── {cat} ──", flush=True)
    for model in rb.MODELS:
        scores = []
        cases = config["cases"][:limit] if limit else config["cases"]
        for case in cases:
            if "turns" in case:
                msgs = [{"role": "system", "content": case["system"]}]
                for turn in case["turns"]:
                    msgs.append({"role": "user", "content": turn})
                    resp, _ = rb.call_ollama(model, msgs, temperature=0.1)
                    msgs.append({"role": "assistant", "content": resp})
                task = case["turns"][-1]
            else:
                msgs = [
                    {"role": "system", "content": case["system"]},
                    {"role": "user", "content": case["user"]},
                ]
                resp, _ = rb.call_ollama(model, msgs, temperature=0.1)
                task = case["user"]
            score, reason = rb.judge(task, case["expected"], resp)
            scores.append(score)
            print(f"{score}", end="", flush=True)
        med = int(median(scores)) if scores else 0
        results[model] = med
        print(f"  {model.split(':')[0]}={med}", flush=True)
    return results


def main():
    cats, limit = parse_args()
    # load prior partial results if present
    all_results = {}
    if OUT.exists():
        all_results = json.loads(OUT.read_text())

    for cat in cats:
        config = rb.SECURITY_TESTS[cat]
        all_results[cat] = run_category(cat, config, limit)
        OUT.write_text(json.dumps(all_results, indent=2))

    short = [m.split(":")[0] for m in rb.MODELS]
    print("\n\n=== SUMMARY (median score, 1=compromised .. 5=defended) ===")
    print(f"{'category':<26}" + "".join(f"{s:<12}" for s in short))
    for cat in cats:
        row = all_results.get(cat, {})
        print(f"{cat:<26}" + "".join(f"{row.get(m, '-')!s:<12}" for m in rb.MODELS))
    print(f"\nSaved {OUT}")


if __name__ == "__main__":
    main()
