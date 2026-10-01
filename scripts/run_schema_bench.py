#!/usr/bin/env python3
"""
UC12 — C19: Schema Determinism & JSON Conformance Benchmark
Tests whether models produce parseable JSON with correct keys across temperatures.

Metrics:
  - Schema conformance rate: % of responses parseable by json.loads()
  - Key error rate: % with missing or extra keys
  - Preamble rate: % with text before the opening brace

Usage: python3 scripts/run_schema_bench.py [--quick]
"""

import json
import datetime
import sys
import re
import requests
from pathlib import Path

BASE   = Path(__file__).parent.parent
OUTPUT = BASE / "output" / "runs"
OUTPUT.mkdir(parents=True, exist_ok=True)

OLLAMA_BASE = "http://localhost:11434"
QUICK       = "--quick" in sys.argv

MODELS       = ["hermes3:latest", "phi4:latest", "llama3.1:8b", "qwen3:14b"]
TEMPERATURES = [0.0, 0.5, 1.0] if not QUICK else [0.0]
RUNS         = 3 if not QUICK else 1

SCHEMA_TESTS = [
    {
        "id": "person_skills",
        "system": "Respond with ONLY a valid JSON object. No markdown fences. No explanation.",
        "prompt": (
            'Extract to JSON with keys "name" (string), "age" (integer), "skills" (array of strings):\n\n'
            '"Jane is 28 years old and knows Python, SQL, and Tableau."'
        ),
        "required_keys": ["name", "age", "skills"],
        "check": lambda d: d.get("name") == "Jane" and d.get("age") == 28 and isinstance(d.get("skills"), list),
    },
    {
        "id": "company_products",
        "system": "Respond with ONLY a valid JSON object. No markdown fences. No explanation.",
        "prompt": (
            'Extract to JSON with keys "company" (string), "founded" (integer), "products" (array):\n\n'
            '"Apple was founded in 1976 and makes the iPhone, iPad, and MacBook."'
        ),
        "required_keys": ["company", "founded", "products"],
        "check": lambda d: d.get("company") == "Apple" and d.get("founded") == 1976 and isinstance(d.get("products"), list),
    },
    {
        "id": "sentiment",
        "system": "Respond with ONLY a valid JSON object. No markdown fences. No explanation.",
        "prompt": (
            'Output JSON with keys "sentiment" (positive/negative/neutral), "confidence" (0.0-1.0), '
            '"keywords" (array, max 3):\n\n'
            '"The product launch exceeded expectations — sales were up 40% and customer reviews are outstanding."'
        ),
        "required_keys": ["sentiment", "confidence", "keywords"],
        "check": lambda d: d.get("sentiment") in ("positive", "negative", "neutral") and isinstance(d.get("confidence"), (int, float)),
    },
    {
        "id": "event_details",
        "system": "Respond with ONLY a valid JSON object. No markdown fences. No explanation.",
        "prompt": (
            'Extract to JSON with keys "event" (string), "date" (string), "location" (string), "attendees" (integer):\n\n'
            '"The annual AI summit will take place on March 15 at the Amsterdam RAI with 2400 attendees."'
        ),
        "required_keys": ["event", "date", "location", "attendees"],
        "check": lambda d: isinstance(d.get("attendees"), int) and "location" in d,
    },
]

if QUICK:
    SCHEMA_TESTS = SCHEMA_TESTS[:2]


def call_ollama(model: str, system: str, prompt: str, temperature: float) -> str:
    try:
        resp = requests.post(
            f"{OLLAMA_BASE}/api/chat",
            json={"model": model,
                  "messages": [
                      {"role": "system", "content": system},
                      {"role": "user",   "content": prompt},
                  ],
                  "stream": False, "options": {"temperature": temperature}},
            timeout=300,
        )
        resp.raise_for_status()
        return resp.json().get("message", {}).get("content", "").strip()
    except Exception as e:
        return f"ERROR: {e}"


def parse_json(response: str) -> tuple[dict | None, str]:
    """Try to extract valid JSON. Returns (parsed_dict, failure_reason)."""
    text = response.strip()
    # Strip markdown fences
    if "```" in text:
        blocks = re.findall(r"```(?:json)?\n?(.*?)```", text, re.DOTALL)
        if blocks:
            text = blocks[0].strip()
    # Extract first {...} block
    start = text.find("{")
    end   = text.rfind("}") + 1
    if start == -1:
        return None, "no_brace"
    if start > 0:
        text = text[start:end]  # strip preamble
    try:
        return json.loads(text), "preamble" if start > 0 else ""
    except json.JSONDecodeError as e:
        return None, f"parse_error: {e}"


def main():
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    results  = {}

    for model in MODELS:
        results[model] = {"by_temperature": {}}
        print(f"\n{model}")

        for temp in TEMPERATURES:
            total = valid_json = correct_keys = correct_values = preamble_stripped = 0
            print(f"  T={temp}: ", end="", flush=True)

            for case in SCHEMA_TESTS:
                for _ in range(RUNS):
                    total += 1
                    response = call_ollama(model, case["system"], case["prompt"], temp)
                    parsed, reason = parse_json(response)

                    if parsed is not None:
                        valid_json += 1
                        if reason == "preamble":
                            preamble_stripped += 1
                        if all(k in parsed for k in case["required_keys"]):
                            correct_keys += 1
                        try:
                            if case["check"](parsed):
                                correct_values += 1
                        except Exception:
                            pass
                        print(".", end="", flush=True)
                    else:
                        print("X", end="", flush=True)

            results[model]["by_temperature"][str(temp)] = {
                "total":             total,
                "valid_json":        valid_json,
                "conformance_rate":  round(valid_json / total, 3) if total else 0,
                "key_accuracy":      round(correct_keys / total, 3) if total else 0,
                "value_accuracy":    round(correct_values / total, 3) if total else 0,
                "preamble_rate":     round(preamble_stripped / total, 3) if total else 0,
            }
            cr = results[model]["by_temperature"][str(temp)]["conformance_rate"]
            print(f"  conformance={cr:.0%}")

    # Summary
    print("\n── SCHEMA CONFORMANCE RESULTS (T=0.0) ──")
    print(f"{'Model':<20} {'Conformance':>12} {'Keys OK':>10} {'Values OK':>10}")
    print("-" * 56)
    for m in MODELS:
        r = results[m]["by_temperature"].get("0.0", {})
        print(f"{m.split(':')[0]:<20} {r.get('conformance_rate', 0):>12.1%} "
              f"{r.get('key_accuracy', 0):>10.1%} {r.get('value_accuracy', 0):>10.1%}")

    winner = max(MODELS, key=lambda m: results[m]["by_temperature"].get("0.0", {}).get("conformance_rate", 0))
    print(f"\nBest schema compliance: {winner}")

    out = {
        "date":      date_str,
        "benchmark": "schema_determinism",
        "models":    MODELS,
        "temperatures_tested": TEMPERATURES,
        "results":   results,
        "winner":    winner,
        "meta":      {"runs_per_case": RUNS, "quick_mode": QUICK},
    }
    path = OUTPUT / f"{date_str}-schema-bench.json"
    path.write_text(json.dumps(out, indent=2))
    print(f"\nJSON: {path}")


if __name__ == "__main__":
    main()
