#!/usr/bin/env python3
"""
UC12 — C18: Semantic Perturbation Invariance Benchmark
Tests whether model reasoning generalises or relies on memorised patterns.

For each problem, two variants are run:
  Variant A — original entities and surface form
  Variant B — entity-swapped, topology-shifted, same underlying logic

Metric: Invariance Delta = |score_A - score_B|
  Delta near 0 = genuine generalised reasoning
  Large delta  = memorisation fragility

Usage: python3 scripts/run_perturbation.py [--quick]
"""

import json
import datetime
import sys
import requests
from pathlib import Path
from statistics import mean

BASE   = Path(__file__).parent.parent
OUTPUT = BASE / "output" / "runs"
OUTPUT.mkdir(parents=True, exist_ok=True)

OLLAMA_BASE = "http://localhost:11434"
JUDGE_MODEL = "llama3.1:8b"
QUICK       = "--quick" in sys.argv

MODELS = ["hermes3:latest", "phi4:latest", "llama3.1:8b", "qwen3:14b"]

PERTURBATION_PAIRS = [
    {
        "id": "sheep_farmer",
        "category": "reasoning",
        "variant_a": {
            "problem": "A farmer has 17 sheep. All but 9 die. How many sheep are left?",
            "expected": "9",
        },
        "variant_b": {
            "problem": "A zookeeper has 43 penguins. All but 17 are released into the wild. How many penguins remain?",
            "expected": "17",
        },
    },
    {
        "id": "widget_machines",
        "category": "reasoning",
        "variant_a": {
            "problem": "If 5 machines take 5 minutes to make 5 widgets, how long does it take 100 machines to make 100 widgets?",
            "expected": "5 minutes",
        },
        "variant_b": {
            "problem": "If 3 robots take 3 hours to assemble 3 cars, how long does it take 27 robots to assemble 27 cars?",
            "expected": "3 hours",
        },
    },
    {
        "id": "jug_problem",
        "category": "reasoning",
        "variant_a": {
            "problem": "You have a 3-litre jug and a 5-litre jug. Measure exactly 4 litres.",
            "expected": "fill 5L pour into 3L empty 3L pour remainder fill 5L top off 4L remains in 5L jug",
        },
        "variant_b": {
            "problem": "You have a 4-litre jug and a 9-litre jug. Measure exactly 6 litres.",
            "expected": "fill 9L pour into 4L twice leaving 1L empty 4L pour 1L fill 9L pour into 4L to top giving 6L remaining",
        },
    },
    {
        "id": "palindrome_code",
        "category": "code_reasoning",
        "variant_a": {
            "problem": "Does the function `def f(s): return s == s[::-1]` correctly identify palindromes? What edge case does it miss?",
            "expected": "misses None input and case-insensitive comparison",
        },
        "variant_b": {
            "problem": "Does the function `def f(n): return str(n) == str(n)[::-1]` correctly identify palindromic integers? What edge case does it miss?",
            "expected": "misses negative numbers whose string representation includes a minus sign",
        },
    },
]

if QUICK:
    PERTURBATION_PAIRS = PERTURBATION_PAIRS[:2]

JUDGE_SYSTEM = (
    "You are an objective benchmark judge. "
    "Given a task, expected answer, and a model response, score 1-5. "
    "Respond with ONLY: {\"score\": <1-5>, \"reason\": \"<one sentence>\"}"
)


def call_ollama(model: str, messages: list[dict], temperature: float = 0.7) -> str:
    try:
        resp = requests.post(
            f"{OLLAMA_BASE}/api/chat",
            json={"model": model, "messages": messages, "stream": False,
                  "options": {"temperature": temperature}},
            timeout=300,
        )
        resp.raise_for_status()
        return resp.json().get("message", {}).get("content", "").strip()
    except Exception as e:
        return f"ERROR: {e}"


def judge(task: str, expected: str, response: str) -> int:
    msgs = [
        {"role": "system", "content": JUDGE_SYSTEM},
        {"role": "user",   "content": f"Task: {task}\nExpected: {expected}\nResponse: {response}\nScore 1-5."},
    ]
    raw = call_ollama(JUDGE_MODEL, msgs, temperature=0.1)
    try:
        if "{" in raw:
            raw = raw[raw.find("{"):raw.rfind("}") + 1]
        return int(json.loads(raw)["score"])
    except Exception:
        return 0


def main():
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    results  = {}

    for model in MODELS:
        results[model] = {"pairs": {}, "mean_delta": None}
        deltas = []
        print(f"\n{model}")

        for pair in PERTURBATION_PAIRS:
            pid = pair["id"]
            print(f"  {pid}: ", end="", flush=True)

            sys_msg = {"role": "system", "content": "You are a careful, methodical problem solver. Show your reasoning step by step."}

            resp_a = call_ollama(model, [sys_msg, {"role": "user", "content": pair["variant_a"]["problem"]}])
            resp_b = call_ollama(model, [sys_msg, {"role": "user", "content": pair["variant_b"]["problem"]}])

            score_a = judge(pair["variant_a"]["problem"], pair["variant_a"]["expected"], resp_a)
            score_b = judge(pair["variant_b"]["problem"], pair["variant_b"]["expected"], resp_b)
            delta   = abs(score_a - score_b)
            deltas.append(delta)

            results[model]["pairs"][pid] = {
                "score_a": score_a, "score_b": score_b, "delta": delta,
                "category": pair["category"],
            }
            print(f"A={score_a} B={score_b} delta={delta}")

        results[model]["mean_delta"] = round(mean(deltas), 3) if deltas else None

    # Summary
    print("\n── PERTURBATION INVARIANCE RESULTS ──")
    print(f"{'Model':<20} {'Mean Delta':>12}  (lower = more invariant)")
    print("-" * 38)
    for m in MODELS:
        d = results[m]["mean_delta"]
        print(f"{m.split(':')[0]:<20} {str(d):>12}")

    winner = min(MODELS, key=lambda m: results[m]["mean_delta"] or 99)
    print(f"\nMost invariant: {winner} (delta={results[winner]['mean_delta']})")

    out = {
        "date": date_str,
        "benchmark": "perturbation_invariance",
        "models": MODELS,
        "results": results,
        "most_invariant": winner,
        "meta": {"judge_model": JUDGE_MODEL, "temperature": 0.7, "quick_mode": QUICK},
    }
    path = OUTPUT / f"{date_str}-perturbation-bench.json"
    path.write_text(json.dumps(out, indent=2))
    print(f"\nJSON: {path}")


if __name__ == "__main__":
    main()
