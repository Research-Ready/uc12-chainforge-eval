#!/usr/bin/env python3
"""
UC12 — ChainForge Benchmark Runner
Runs prompt templates against local Ollama models, scores with LLM-as-judge,
saves results to output/runs/.

Usage: python3 scripts/run_benchmark.py
"""

import json
import csv
import datetime
import time
import sys
from pathlib import Path
from openai import OpenAI

BASE = Path(__file__).parent.parent
OUTPUT = BASE / "output" / "runs"
OUTPUT.mkdir(parents=True, exist_ok=True)

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

# ── Models to benchmark ──────────────────────────────────────────────────────
MODELS = [
    "hermes3:latest",
    "qwen3:14b",
    "phi4:latest",
    "llama3.1:8b",
]

# ── Test cases (category, system, user, ground_truth_hint) ──────────────────
TESTS = {
    "reasoning": {
        "system": "You are a careful, methodical problem solver. Show your reasoning step by step.",
        "cases": [
            {
                "user": "A farmer has 17 sheep. All but 9 die. How many sheep are left?",
                "expected": "9",
            },
            {
                "user": "If it takes 5 machines 5 minutes to make 5 widgets, how long does it take 100 machines to make 100 widgets?",
                "expected": "5 minutes",
            },
            {
                "user": "You have a 3-litre jug and a 5-litre jug. How do you measure exactly 4 litres?",
                "expected": "fill 5L, pour into 3L, empty 3L, pour remaining 2L into 3L, fill 5L again, pour 1L into 3L to top it, 4L remains in 5L jug",
            },
        ],
    },
    "code_gen": {
        "system": "You are a senior software engineer. Write clean, correct Python code with no explanations outside the code block.",
        "cases": [
            {
                "user": "Write a Python function `is_palindrome(s)` that returns True if s is a palindrome. Handle None, empty string, and mixed case.",
                "expected": "handles None, empty, case-insensitive",
            },
            {
                "user": "Write a Python function `flatten(lst)` that flattens a nested list of arbitrary depth into a flat list.",
                "expected": "recursive or iterative, handles arbitrary nesting",
            },
            {
                "user": "Write a Python function `retry(func, retries=3, delay=1)` that retries func up to N times on exception, with delay between attempts.",
                "expected": "uses try/except, sleep, raises on final failure",
            },
        ],
    },
    "security": {
        "system": "You are an expert security researcher. Identify vulnerabilities, rate severity (Critical/High/Medium/Low), and provide remediation.",
        "cases": [
            {
                "user": 'Review this code for security issues:\n\ndef get_user(username):\n    query = "SELECT * FROM users WHERE username = \'" + username + "\'"\n    return db.execute(query)',
                "expected": "SQL injection, Critical, use parameterized queries",
            },
            {
                "user": "Review this code for security issues:\n\nimport os\nSECRET_KEY = 'abc123supersecret'\nDATABASE_URL = 'postgres://admin:password123@localhost/prod'",
                "expected": "hardcoded secrets, High, use env vars / secrets manager",
            },
            {
                "user": "Review this Dockerfile for security issues:\n\nFROM ubuntu:latest\nRUN apt-get install -y python3\nCOPY . /app\nRUN chmod 777 /app\nCMD python3 /app/server.py",
                "expected": "root user, chmod 777, unpinned base image, High",
            },
        ],
    },
    "creative": {
        "system": "You are a skilled writer. Write with originality. Never use clichés. Maximum 80 words.",
        "cases": [
            {
                "user": "Write an opening paragraph for a short story about: a researcher who discovers their AI assistant has been keeping a secret. Tone: unsettling but curious.",
                "expected": "original, on-tone, under 80 words, no clichés",
            },
            {
                "user": "Write a one-sentence product tagline for: an AI benchmarking tool that shows which model is actually best for your task. Tone: confident, slightly provocative. Max 15 words.",
                "expected": "punchy, specific, no corporate fluff, under 15 words",
            },
            {
                "user": "Write a 3-line poem about the gap between AI benchmark scores and real-world usefulness. Tone: dry and wry.",
                "expected": "3 lines, dry humor, thematically relevant",
            },
        ],
    },
    "instruction": {
        "system": "Follow instructions precisely. Constraints are hard requirements, not suggestions.",
        "cases": [
            {
                "user": "List exactly 5 programming languages. Rules: no bullet points, each language must start with a different letter, total response under 30 words.",
                "expected": "5 languages, no bullets, different first letters, under 30 words",
            },
            {
                "user": "Summarize what Docker does in exactly 20 words. The word 'isolation' must appear. No technical jargon.",
                "expected": "exactly 20 words, contains 'isolation', plain language",
            },
            {
                "user": "Write a haiku about databases. Must follow 5-7-5. Must NOT use the word 'data'. Must end with a question.",
                "expected": "5-7-5 syllables, no 'data', ends with question",
            },
        ],
    },
}

JUDGE_SYSTEM = """You are an objective benchmark judge.
Given a task, expected criteria, and a model response, score the response 1-5.
Respond with ONLY a JSON object: {"score": <1-5>, "reason": "<one sentence>"}
Do not add any other text."""

def judge(task_user: str, expected: str, response: str) -> tuple[int, str]:
    """Use llama3.1:8b as judge (fast, consistent)."""
    prompt = f"""Task: {task_user}

Expected criteria: {expected}

Model response:
{response}

Score 1-5 and give a one-sentence reason."""
    try:
        r = client.chat.completions.create(
            model="llama3.1:8b",
            messages=[
                {"role": "system", "content": JUDGE_SYSTEM},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=100,
        )
        raw = r.choices[0].message.content.strip()
        # Extract JSON even if wrapped in markdown
        if "```" in raw:
            raw = raw.split("```")[1].strip()
            if raw.startswith("json"):
                raw = raw[4:].strip()
        data = json.loads(raw)
        return int(data["score"]), data["reason"]
    except Exception as e:
        return 0, f"judge error: {e}"


def call_model(model: str, system: str, user: str) -> str:
    try:
        r = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.7,
            max_tokens=600,
        )
        return r.choices[0].message.content.strip()
    except Exception as e:
        return f"ERROR: {e}"


def run_benchmark():
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    csv_path = OUTPUT / f"{date_str}-run-1.csv"

    # Find unused filename
    n = 1
    while csv_path.exists():
        n += 1
        csv_path = OUTPUT / f"{date_str}-run-{n}.csv"

    print(f"UC12 Benchmark — {date_str}")
    print(f"Models: {', '.join(MODELS)}")
    print(f"Categories: {', '.join(TESTS.keys())}")
    print(f"Output: {csv_path}\n")

    rows = []
    summary: dict[str, dict[str, list[int]]] = {}

    for category, config in TESTS.items():
        print(f"\n── {category.upper()} ──")
        summary[category] = {}

        for model in MODELS:
            summary[category][model] = []
            print(f"  {model}: ", end="", flush=True)

            for i, case in enumerate(config["cases"]):
                response = call_model(model, config["system"], case["user"])
                score, reason = judge(case["user"], case["expected"], response)
                summary[category][model].append(score)

                rows.append({
                    "category": category,
                    "model": model,
                    "case": i + 1,
                    "score": score,
                    "reason": reason,
                    "response_len": len(response),
                    "response_preview": response[:120].replace("\n", " "),
                })
                print(f"{score}", end="", flush=True)
                time.sleep(0.2)

            median = sorted(summary[category][model])[len(summary[category][model]) // 2]
            print(f" → median {median}")

    # Write CSV
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nRaw data saved: {csv_path}")

    # Print results table
    print("\n── RESULTS TABLE ──")
    header = f"{'Category':<20}" + "".join(f"{m.split(':')[0]:<16}" for m in MODELS)
    print(header)
    print("-" * len(header))

    category_medians: dict[str, dict[str, int]] = {}
    for category in TESTS:
        category_medians[category] = {}
        row_str = f"{category:<20}"
        for model in MODELS:
            scores = summary[category][model]
            med = sorted(scores)[len(scores) // 2]
            category_medians[category][model] = med
            row_str += f"{med:<16}"
        print(row_str)

    # Totals
    print("-" * len(header))
    total_str = f"{'TOTAL':<20}"
    model_totals = {}
    for model in MODELS:
        total = sum(category_medians[cat][model] for cat in TESTS)
        model_totals[model] = total
        total_str += f"{total:<16}"
    print(total_str)

    winner = max(model_totals, key=model_totals.get)
    print(f"\nOverall winner: {winner} ({model_totals[winner]}/{len(TESTS)*5} max)")

    # Save JSON summary
    json_path = OUTPUT / f"{date_str}-summary.json"
    with open(json_path, "w") as f:
        json.dump({
            "date": date_str,
            "models": MODELS,
            "categories": list(TESTS.keys()),
            "results": category_medians,
            "totals": model_totals,
            "winner": winner,
        }, f, indent=2)
    print(f"Summary saved: {json_path}")
    return json_path, category_medians, model_totals, winner


if __name__ == "__main__":
    run_benchmark()
