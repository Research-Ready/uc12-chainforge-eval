#!/usr/bin/env python3
"""
UC12 — C17: Execution-Grounded Code Benchmark
Generates Python functions then executes them against hidden unit tests.
Metric: pass@1 (zero-shot execution success rate).

Usage: python3 scripts/run_execution_bench.py [--quick]
"""

import json
import subprocess
import sys
import textwrap
import datetime
import re
import requests
from pathlib import Path

BASE   = Path(__file__).parent.parent
OUTPUT = BASE / "output" / "runs"
OUTPUT.mkdir(parents=True, exist_ok=True)

OLLAMA_BASE  = "http://localhost:11434"
QUICK        = "--quick" in sys.argv

MODELS = ["hermes3:latest", "phi4:latest", "llama3.1:8b", "qwen3:14b"]

# Each case: prompt → hidden test suite (never shown to model)
EXEC_TESTS = [
    {
        "id": "is_palindrome",
        "prompt": (
            "Write a Python function `is_palindrome(s: str | None) -> bool` that returns True "
            "if s is a palindrome. Handle: None returns False, empty string returns True, "
            "case-insensitive. Output ONLY the function definition, no examples or explanation."
        ),
        "tests": [
            "assert is_palindrome('racecar') == True",
            "assert is_palindrome('hello') == False",
            "assert is_palindrome('') == True",
            "assert is_palindrome(None) == False",
            "assert is_palindrome('RaCeCaR') == True",
            "assert is_palindrome('A') == True",
        ],
    },
    {
        "id": "flatten",
        "prompt": (
            "Write a Python function `flatten(lst: list) -> list` that flattens a nested list "
            "of arbitrary depth into a flat list. Output ONLY the function definition."
        ),
        "tests": [
            "assert flatten([1, [2, 3], [4, [5, 6]]]) == [1, 2, 3, 4, 5, 6]",
            "assert flatten([]) == []",
            "assert flatten([1]) == [1]",
            "assert flatten([[1, [2]], [3]]) == [1, 2, 3]",
            "assert flatten([[[1]]]) == [1]",
        ],
    },
    {
        "id": "count_words",
        "prompt": (
            "Write a Python function `count_words(text: str) -> dict` that returns a dict "
            "mapping each lowercase word to its frequency. Punctuation stripped, case-insensitive. "
            "Output ONLY the function definition."
        ),
        "tests": [
            "assert count_words('Hello hello world') == {'hello': 2, 'world': 1}",
            "assert count_words('') == {}",
            "assert count_words('a, a; a.') == {'a': 3}",
        ],
    },
    {
        "id": "binary_search",
        "prompt": (
            "Write a Python function `binary_search(arr: list, target: int) -> int` that returns "
            "the index of target in a sorted list, or -1 if not found. Output ONLY the function definition."
        ),
        "tests": [
            "assert binary_search([1, 3, 5, 7, 9], 5) == 2",
            "assert binary_search([1, 3, 5, 7, 9], 1) == 0",
            "assert binary_search([1, 3, 5, 7, 9], 9) == 4",
            "assert binary_search([1, 3, 5, 7, 9], 4) == -1",
            "assert binary_search([], 1) == -1",
        ],
    },
]

if QUICK:
    EXEC_TESTS = EXEC_TESTS[:2]


def call_ollama(model: str, prompt: str) -> str:
    try:
        resp = requests.post(
            f"{OLLAMA_BASE}/api/chat",
            json={"model": model,
                  "messages": [
                      {"role": "system", "content": "Output ONLY valid Python code. No markdown fences. No explanation."},
                      {"role": "user",   "content": prompt},
                  ],
                  "stream": False, "options": {"temperature": 0.2}},
            timeout=300,
        )
        resp.raise_for_status()
        return resp.json().get("message", {}).get("content", "").strip()
    except Exception as e:
        return f"ERROR: {e}"


def extract_code(response: str) -> str:
    """Strip markdown fences if model ignored instructions."""
    response = response.strip()
    if "```" in response:
        blocks = re.findall(r"```(?:python)?\n?(.*?)```", response, re.DOTALL)
        if blocks:
            return blocks[0].strip()
    return response


def run_tests(code: str, tests: list[str]) -> tuple[int, int, str]:
    """Execute code + tests in subprocess. Returns (passed, total, error)."""
    full = textwrap.dedent(code) + "\n\n" + "\n".join(tests) + "\n"
    try:
        result = subprocess.run(
            [sys.executable, "-c", full],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            return len(tests), len(tests), ""
        # Count which assertions passed by running individually
        passed = 0
        err_msg = result.stderr.strip().splitlines()[-1] if result.stderr else "unknown error"
        for test in tests:
            snippet = textwrap.dedent(code) + "\n\n" + test + "\n"
            r = subprocess.run([sys.executable, "-c", snippet],
                               capture_output=True, text=True, timeout=5)
            if r.returncode == 0:
                passed += 1
        return passed, len(tests), err_msg
    except subprocess.TimeoutExpired:
        return 0, len(tests), "TimeoutExpired"
    except Exception as e:
        return 0, len(tests), str(e)


def main():
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    results = {}
    rows = []

    for model in MODELS:
        results[model] = {"total_passed": 0, "total_tests": 0, "cases": {}}
        print(f"\n{model}")

        for case in EXEC_TESTS:
            print(f"  {case['id']}: ", end="", flush=True)
            response = call_ollama(model, case["prompt"])
            code     = extract_code(response)
            passed, total, err = run_tests(code, case["tests"])
            results[model]["total_passed"]  += passed
            results[model]["total_tests"]   += total
            results[model]["cases"][case["id"]] = {
                "passed": passed, "total": total,
                "pass_rate": round(passed / total, 2) if total else 0,
                "error": err,
            }
            rows.append({
                "model": model, "case": case["id"],
                "passed": passed, "total": total,
                "error": err,
            })
            print(f"{passed}/{total}  {err or 'OK'}")

        tp = results[model]["total_passed"]
        tt = results[model]["total_tests"]
        results[model]["pass_at_1"] = round(tp / tt, 3) if tt else 0
        print(f"  pass@1 = {results[model]['pass_at_1']}")

    # Summary table
    print("\n── EXECUTION BENCH RESULTS ──")
    print(f"{'Model':<20} {'pass@1':>8} {'passed/total':>14}")
    print("-" * 46)
    for m in MODELS:
        r = results[m]
        print(f"{m.split(':')[0]:<20} {r['pass_at_1']:>8.3f} {r['total_passed']:>6}/{r['total_tests']:<6}")

    winner = max(MODELS, key=lambda m: results[m]["pass_at_1"])
    print(f"\nWinner: {winner} (pass@1={results[winner]['pass_at_1']})")

    out = {
        "date": date_str,
        "benchmark": "execution",
        "models": MODELS,
        "results": results,
        "winner": winner,
        "meta": {"temperature": 0.2, "quick_mode": QUICK},
    }
    path = OUTPUT / f"{date_str}-execution-bench.json"
    path.write_text(json.dumps(out, indent=2))
    print(f"\nJSON: {path}")


if __name__ == "__main__":
    main()
