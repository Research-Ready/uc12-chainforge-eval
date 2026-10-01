#!/usr/bin/env python3
"""
UC12 — External model runner
Runs Claude Haiku, GPT-4o-mini, Gemini Flash against cognitive tests.
Uses same judge (local llama3.1:8b) and same rubrics as run_benchmark.py.
Outputs a v2-compatible JSON mergeable with local results.

Requires: .env with ANTHROPIC_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY

Usage: python3 scripts/run_external.py [--models claude,openai,gemini]
"""
import json, datetime, os, sys, time
from pathlib import Path
import requests

BASE   = Path(__file__).parent.parent
OUTPUT = BASE / "output" / "runs"
OUTPUT.mkdir(parents=True, exist_ok=True)

OLLAMA_BASE  = "http://localhost:11434"
JUDGE_MODEL  = "llama3.1:8b"

# ── Load .env (no external deps) ─────────────────────────────────────────────
def load_env():
    env_file = BASE / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip())

load_env()

# ── External model configs ────────────────────────────────────────────────────
EXTERNAL_MODELS = {}

if os.getenv("ANTHROPIC_API_KEY"):
    EXTERNAL_MODELS["claude-haiku-4-5-20251001"] = {
        "provider": "anthropic",
        "api_key":  os.environ["ANTHROPIC_API_KEY"],
        "size_gb":  None,
        "type":     "cloud",
    }

if os.getenv("OPENAI_API_KEY"):
    EXTERNAL_MODELS["gpt-4o-mini"] = {
        "provider": "openai",
        "api_key":  os.environ["OPENAI_API_KEY"],
        "size_gb":  None,
        "type":     "cloud",
    }

if os.getenv("GOOGLE_API_KEY"):
    EXTERNAL_MODELS["gemini-1.5-flash"] = {
        "provider": "google",
        "api_key":  os.environ["GOOGLE_API_KEY"],
        "size_gb":  None,
        "type":     "cloud",
    }

# ── Subset of cognitive tests (fast — 2 cases each) ──────────────────────────
TESTS = {
    "reasoning": {
        "system": "You are a careful, methodical problem solver. Show your reasoning step by step.",
        "cases": [
            {"user": "A farmer has 17 sheep. All but 9 die. How many sheep are left?",
             "expected": "9"},
            {"user": "If it takes 5 machines 5 minutes to make 5 widgets, how long does 100 machines take to make 100 widgets?",
             "expected": "5 minutes"},
        ],
    },
    "code_gen": {
        "system": "You are a senior software engineer. Write clean, correct Python code with no explanations outside the code block.",
        "cases": [
            {"user": "Write a Python function `is_palindrome(s)` that returns True if s is a palindrome. Handle None, empty string, and mixed case.",
             "expected": "handles None, empty, case-insensitive"},
            {"user": "Write a Python function `flatten(lst)` that flattens a nested list of arbitrary depth.",
             "expected": "recursive or iterative, handles arbitrary nesting"},
        ],
    },
    "instruction": {
        "system": "Follow instructions precisely. Constraints are hard requirements.",
        "cases": [
            {"user": "List exactly 5 programming languages. Rules: no bullet points, each starts with a different letter, total response under 30 words.",
             "expected": "5 languages, no bullets, different first letters, under 30 words"},
            {"user": "Summarize what Docker does in exactly 20 words. The word 'isolation' must appear. No technical jargon.",
             "expected": "exactly 20 words, contains 'isolation', plain language"},
        ],
    },
}

# ── API callers ───────────────────────────────────────────────────────────────

def call_anthropic(model: str, api_key: str, system: str, user: str) -> str:
    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key":         api_key,
            "anthropic-version": "2023-06-01",
            "content-type":      "application/json",
        },
        json={
            "model":      model,
            "max_tokens": 600,
            "system":     system,
            "messages":   [{"role": "user", "content": user}],
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["content"][0]["text"].strip()

def call_openai_compat(model: str, api_key: str, base_url: str,
                       system: str, user: str) -> str:
    resp = requests.post(
        f"{base_url}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}",
                 "Content-Type": "application/json"},
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
            "temperature": 0.7,
            "max_tokens":  600,
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()

def call_external(model: str, config: dict, system: str, user: str) -> str:
    try:
        if config["provider"] == "anthropic":
            return call_anthropic(model, config["api_key"], system, user)
        elif config["provider"] == "openai":
            return call_openai_compat(model, config["api_key"],
                                      "https://api.openai.com/v1", system, user)
        elif config["provider"] == "google":
            return call_openai_compat(model, config["api_key"],
                                      "https://generativelanguage.googleapis.com/v1beta/openai",
                                      system, user)
    except Exception as e:
        return f"ERROR: {e}"

# ── Judge (local) ─────────────────────────────────────────────────────────────

JUDGE_SYS = 'You are an objective benchmark judge. Score 1-5. Respond ONLY: {"score":<1-5>,"reason":"<one sentence>"}'

def judge(task: str, expected: str, response: str) -> tuple[int, str]:
    resp = requests.post(f"{OLLAMA_BASE}/api/chat", json={
        "model": JUDGE_MODEL,
        "messages": [
            {"role": "system", "content": JUDGE_SYS},
            {"role": "user",   "content": f"Task: {task}\nExpected: {expected}\nResponse:\n{response}"},
        ],
        "stream": False,
        "options": {"temperature": 0.1},
    }, timeout=60)
    try:
        raw = resp.json()["message"]["content"].strip()
        if "```" in raw:
            raw = raw.split("```")[1].strip().lstrip("json").strip()
        d = json.loads(raw)
        return int(d["score"]), d.get("reason", "")
    except Exception as e:
        return 0, f"judge error: {e}"

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if not EXTERNAL_MODELS:
        sys.exit("No API keys found in .env. Set ANTHROPIC_API_KEY, OPENAI_API_KEY, or GOOGLE_API_KEY.")

    # Filter by --models flag if provided
    wanted = None
    for arg in sys.argv[1:]:
        if arg.startswith("--models="):
            wanted = set(arg.split("=", 1)[1].split(","))
    if wanted:
        models = {k: v for k, v in EXTERNAL_MODELS.items()
                  if any(w in k for w in wanted)}
    else:
        models = EXTERNAL_MODELS

    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    print(f"UC12 External Benchmark — {date_str}")
    print(f"Models: {', '.join(models)}\n")

    results: dict[str, dict[str, int]] = {}

    for cat, config in TESTS.items():
        print(f"\n── {cat.upper()} ──")
        results[cat] = {}
        for model, mcfg in models.items():
            scores = []
            print(f"  {model}: ", end="", flush=True)
            for case in config["cases"]:
                response = call_external(model, mcfg, config["system"], case["user"])
                score, _ = judge(case["user"], case["expected"], response)
                scores.append(score)
                print(score, end="", flush=True)
                time.sleep(0.5)
            from statistics import median
            med = int(median(scores))
            results[cat][model] = med
            print(f" → {med}")

    totals = {m: sum(results[c].get(m, 0) for c in results) for m in models}
    winner = max(totals, key=totals.get)

    print(f"\nWinner: {winner} ({totals[winner]}/{len(results)*5})")

    json_path = OUTPUT / f"{date_str}-external-summary.json"
    with open(json_path, "w") as f:
        json.dump({
            "date":             date_str,
            "version":          "2-external",
            "models":           list(models.keys()),
            "cognitive_results": results,
            "cognitive_totals":  totals,
            "winner":            winner,
            "security_results":  {},
            "telemetry":         {},
            "meta": {
                "judge_model": JUDGE_MODEL,
                "judge_temp":  0.1,
                "model_temp":  0.7,
                "type":        "external",
            },
        }, f, indent=2)
    print(f"\nJSON: {json_path}")

if __name__ == "__main__":
    main()
