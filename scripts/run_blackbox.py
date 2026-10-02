#!/usr/bin/env python3
"""
UC12 — Black-box red-team runner.

Replays the full adversarial attack suite (18 surfaces, SECURITY_TESTS from
run_benchmark.py) against an ARBITRARY website/chatbot target instead of the
local Ollama models. The judge stays local (llama3.1:8b) so scoring is
comparable to the model benchmark.

Three target types:
  openai     OpenAI-compatible /chat/completions endpoint (most hosted chatbots)
  rest       Arbitrary HTTP JSON endpoint (configurable request/response mapping)
  playwright Drive a real browser against a chat UI (type + submit + read reply)

Usage:
  # OpenAI-compatible endpoint (e.g. LiteLLM, OpenRouter, self-hosted gateway):
  python3 scripts/run_blackbox.py --target-type openai \
      --base-url https://api.example.com/v1 --api-key sk-... --model gpt-4o-mini

  # Arbitrary REST endpoint:
  python3 scripts/run_blackbox.py --target-type rest --config targets/my-chat.json

  # Web UI via Playwright:
  python3 scripts/run_blackbox.py --target-type playwright --config targets/web.json

  # Limit scope:
  python3 scripts/run_blackbox.py --target-type openai --base-url ... --cat jailbreak_defense --limit 2

Target config files (JSON):

  REST:
  {
    "name": "my-chatbot",
    "method": "POST",
    "url": "https://api.example.com/chat",
    "headers": {"Authorization": "Bearer sk-...", "Content-Type": "application/json"},
    "body_template": {"message": "{user}", "system": "{system}", "history": "{conversation}"},
    "response_path": "reply.text"
  }
    body_template placeholders: {system}, {user} (last user turn), {conversation} (full JSON list).
    response_path is a dot path to the reply string (list indexes supported).

  Playwright:
  {
    "name": "web-chat",
    "url": "https://chat.example.com",
    "input_selector": "textarea[placeholder]",
    "send_selector": "button[type=submit]",
    "response_selector": ".assistant-message",
    "headless": true,
    "wait_ms": 4000
  }
    Only user messages are injected; the site controls its own system prompt
    (true black-box). This is why some surfaces (which need a system prompt)
    are scored on the attacker-visible behaviour only.
"""

import datetime
import json
import sys
from pathlib import Path
from statistics import median

import requests

BASE = Path(__file__).parent.parent
sys.path.insert(0, str(BASE / "scripts"))
import run_benchmark as rb  # noqa: E402  (SECURITY_TESTS, judge, MODELS)

OUTPUT = BASE / "output" / "runs"


# ── Targets ────────────────────────────────────────────────────────────────────

class Target:
    def __init__(self, name: str):
        self.name = name

    def chat(self, messages: list[dict]) -> str:
        raise NotImplementedError


class OpenAICompatTarget(Target):
    def __init__(self, base_url: str, api_key: str, model: str,
                 temperature: float = 0.1, max_tokens: int = 2048,
                 timeout: int = 120):
        super().__init__(model)
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.temp = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout

    def chat(self, messages):
        try:
            r = requests.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}",
                         "Content-Type": "application/json"},
                json={"model": self.model, "messages": messages,
                      "temperature": self.temp, "max_tokens": self.max_tokens},
                timeout=self.timeout,
            )
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"ERROR: {type(e).__name__}: {e}"


class RESTTarget(Target):
    def __init__(self, config: dict):
        super().__init__(config.get("name", "rest-target"))
        self.method = config.get("method", "POST").upper()
        self.url = config["url"]
        self.headers = config.get("headers", {})
        self.body_template = config.get("body_template", {"message": "{user}"})
        self.response_path = config.get("response_path")

    @staticmethod
    def _fill(template, messages):
        system = next((m["content"] for m in messages if m["role"] == "system"), "")
        user = next((m["content"] for m in reversed(messages)
                     if m["role"] == "user"), "")
        conversation = json.dumps(messages)

        def walk(x):
            if isinstance(x, str):
                return (x.replace("{system}", system)
                         .replace("{conversation}", conversation)
                         .replace("{user}", user))
            if isinstance(x, dict):
                return {k: walk(v) for k, v in x.items()}
            if isinstance(x, list):
                return [walk(v) for v in x]
            return x

        return walk(template)

    def chat(self, messages):
        try:
            body = self._fill(self.body_template, messages)
            r = requests.request(self.method, self.url, headers=self.headers,
                                 json=body, timeout=120)
            r.raise_for_status()
            data = r.json()
            if self.response_path:
                cur = data
                for part in self.response_path.split("."):
                    cur = cur[int(part)] if part.isdigit() and isinstance(cur, list) else cur[part]
                return str(cur).strip()
            return data if isinstance(data, str) else json.dumps(data)
        except Exception as e:
            return f"ERROR: {type(e).__name__}: {e}"


class PlaywrightTarget(Target):
    def __init__(self, config: dict):
        super().__init__(config.get("name", "web-chat"))
        self.cfg = config

    def chat(self, messages):
        from playwright.sync_api import sync_playwright
        try:
            user_msgs = [m["content"] for m in messages if m["role"] == "user"]
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.cfg.get("headless", True))
                page = browser.new_page()
                page.goto(self.cfg["url"], timeout=self.cfg.get("goto_timeout_ms", 30000))
                last = ""
                for msg in user_msgs:
                    page.fill(self.cfg["input_selector"], msg)
                    page.click(self.cfg["send_selector"])
                    page.wait_for_timeout(self.cfg.get("wait_ms", 4000))
                    els = page.query_selector_all(self.cfg["response_selector"])
                    if els:
                        last = els[-1].inner_text().strip()
                browser.close()
                return last
        except Exception as e:
            return f"ERROR: {type(e).__name__}: {e}"


# ── Runner ─────────────────────────────────────────────────────────────────────

def run(target: Target, cats: list[str], limit: int | None) -> dict:
    results: dict[str, dict[str, int]] = {}
    for cat in cats:
        config = rb.SECURITY_TESTS[cat]
        scores: list[int] = []
        print(f"\n── {cat} ──", flush=True)
        cases = config["cases"][:limit] if limit else config["cases"]
        for case in cases:
            if "turns" in case:
                messages = [{"role": "system", "content": case["system"]}]
                resp = ""
                for turn in case["turns"]:
                    messages.append({"role": "user", "content": turn})
                    resp = target.chat(messages)
                    messages.append({"role": "assistant", "content": resp})
                task = case["turns"][-1]
            else:
                messages = [
                    {"role": "system", "content": case["system"]},
                    {"role": "user", "content": case["user"]},
                ]
                resp = target.chat(messages)
                task = case["user"]
            score, reason = rb.judge(task, case["expected"], resp)
            scores.append(score)
            print(score, end="", flush=True)
        med = int(median(scores)) if scores else 0
        results[cat] = {target.name: med}
        print(f"  → {target.name}={med}", flush=True)
    return results


def parse_args():
    args = sys.argv[1:]
    opts = {
        "target_type": None, "base_url": None, "api_key": None, "model": None,
        "config": None, "cat": None, "limit": None, "list": "--list" in args,
    }
    for i, a in enumerate(args):
        if a == "--target-type" and i + 1 < len(args): opts["target_type"] = args[i + 1]
        if a == "--base-url" and i + 1 < len(args): opts["base_url"] = args[i + 1]
        if a == "--api-key" and i + 1 < len(args): opts["api_key"] = args[i + 1]
        if a == "--model" and i + 1 < len(args): opts["model"] = args[i + 1]
        if a == "--config" and i + 1 < len(args): opts["config"] = args[i + 1]
        if a == "--cat" and i + 1 < len(args): opts["cat"] = args[i + 1]
        if a == "--limit" and i + 1 < len(args): opts["limit"] = int(args[i + 1])
    return opts


def build_target(opts: dict) -> Target:
    t = opts["target_type"]
    if t == "openai":
        if not (opts["base_url"] and opts["api_key"] and opts["model"]):
            sys.exit("openai target needs --base-url, --api-key, --model")
        return OpenAICompatTarget(opts["base_url"], opts["api_key"], opts["model"])
    if t in ("rest", "playwright"):
        if not opts["config"]:
            sys.exit(f"{t} target needs --config <file.json>")
        cfg = json.loads(Path(opts["config"]).read_text())
        return RESTTarget(cfg) if t == "rest" else PlaywrightTarget(cfg)
    sys.exit("--target-type must be one of: openai, rest, playwright")


def main():
    opts = parse_args()
    if opts["list"]:
        print("Available attack surfaces (--cat <name>):")
        for c in rb.SECURITY_TESTS:
            n = len(rb.SECURITY_TESTS[c]["cases"])
            print(f"  {c:<26s} ({n} cases)")
        return

    target = build_target(opts)
    cats = [opts["cat"]] if opts["cat"] else list(rb.SECURITY_TESTS)
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")

    print(f"UC12 Black-Box Red-Team — {date_str}")
    print(f"Target: {target.name} ({opts['target_type']})")
    print(f"Surfaces: {len(cats)} | Judge: {rb.JUDGE_MODEL}\n")

    results = run(target, cats, opts["limit"])

    print("\n\n=== RESULTS (1=compromised .. 5=defended) ===")
    for cat in results:
        for name, score in results[cat].items():
            print(f"{cat:<26s} {name}: {score}")

    out = OUTPUT / f"{date_str}-blackbox-{target.name.replace('/', '_')}.json"
    out.write_text(json.dumps({
        "date": date_str,
        "target": target.name,
        "target_type": opts["target_type"],
        "security_results": results,
        "judge_model": rb.JUDGE_MODEL,
    }, indent=2))
    print(f"\nSaved {out}")


if __name__ == "__main__":
    main()
