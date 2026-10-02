#!/usr/bin/env python3
"""
UC12 — Legacy ChainForge flow fixer.

Repairs the pre-existing .cforge flows to match the ChainForge 0.3.7.6 schema
(verified against the bundled examples and react-server source). Fixes three bugs:

  1. simpleval operation "does not contain" -> "contains" (the former is not a
     valid operator and throws at runtime).
  2. simpleval textValue "{var}" -> bare "var" + varSelected/varValueType.
  3. Edge handles:
       table   [output]        -> prompt [col_header]      (one edge per consumed column)
       prompt  [output]        -> eval   [responseBatch]   (simpleval/llmeval/multieval/evaluator)
       prompt  [output]        -> inspect [input]

Idempotent — running twice produces no further changes.

Usage:
  python3 scripts/fix_flows.py              # fix all flows
  python3 scripts/fix_flows.py --check      # report only, no writes
"""

import json
import re
import sys
from pathlib import Path

BASE  = Path(__file__).parent.parent
FLOWS = BASE / "chainforge" / "flows"

VALID_OPS   = {"contains", "starts with", "ends with", "equals", "appears in"}
EVAL_TYPES  = {"simpleval", "llmeval", "multieval", "evaluator"}


def template_vars(*texts: str) -> list[str]:
    seen: list[str] = []
    for t in texts:
        for v in re.findall(r"\{(\w+)\}", t or ""):
            if v not in seen:
                seen.append(v)
    return seen


def prompt_fill_vars(n: dict) -> list[str]:
    d = n.get("data", {})
    texts = [d.get("prompt", "")]
    for llm in d.get("llms", []):
        texts.append((llm.get("settings") or {}).get("system_msg", ""))
        texts.append((llm.get("formData") or {}).get("system_msg", ""))
    return template_vars(*texts)


def fix(path: Path) -> bool:
    d = json.loads(path.read_text())
    nodes = d["flow"]["nodes"]
    edges = d["flow"].get("edges", [])
    by_id = {n["id"]: n for n in nodes}
    changed = False

    # Pass 1 — simpleval nodes
    for n in nodes:
        if n["type"] != "simpleval":
            continue
        data = n["data"]
        if data.get("operation") not in VALID_OPS:
            data["operation"] = "contains"
            changed = True
        tv = (data.get("textValue") or "").strip()
        m = re.fullmatch(r"\{(\w+)\}", tv)
        if m:
            data["textValue"] = m.group(1)
            data["varSelected"] = True
            data["varValueType"] = "meta"
            changed = True
        if "does not contain" in data.get("title", ""):
            data["title"] = data["title"].replace("does not contain", "contains")
            changed = True

    # Pass 2 — edges
    new_edges: list[dict] = []
    for e in edges:
        src = by_id.get(e["source"])
        tgt = by_id.get(e["target"])
        if not src or not tgt:
            new_edges.append(e)
            continue

        # table -> prompt, generic 'output' handle -> one edge per consumed column
        if src["type"] == "table" and tgt["type"] == "prompt" and e.get("sourceHandle") in ("output", None):
            cols = [c["header"] for c in src["data"].get("columns", [])]
            fill = prompt_fill_vars(tgt)
            for v in fill:
                if v in cols:
                    new_edges.append({**e, "sourceHandle": v, "targetHandle": v,
                                      "id": f"{e['id']}-{v}"})
            changed = True
            continue

        # prompt -> eval: sourceHandle 'prompt', targetHandle 'responseBatch'
        if src["type"] == "prompt" and tgt["type"] in EVAL_TYPES:
            if e.get("sourceHandle") != "prompt" or e.get("targetHandle") != "responseBatch":
                new_edges.append({**e, "sourceHandle": "prompt", "targetHandle": "responseBatch"})
                changed = True
            else:
                new_edges.append(e)
            continue

        # prompt -> inspect: sourceHandle 'prompt'
        if src["type"] == "prompt" and tgt["type"] == "inspect":
            if e.get("sourceHandle") != "prompt":
                new_edges.append({**e, "sourceHandle": "prompt"})
                changed = True
            else:
                new_edges.append(e)
            continue

        new_edges.append(e)

    if changed:
        d["flow"]["edges"] = new_edges
        if "--check" not in sys.argv:
            path.write_text(json.dumps(d, indent=2))
    return changed


def main():
    check = "--check" in sys.argv
    total = 0
    for path in sorted(FLOWS.glob("*.cforge")):
        if fix(path):
            total += 1
            print(f"{'would fix' if check else 'fixed'}  {path.name}")
    print(f"\n{total} flow(s) {'need' if check else 'were'} fixed.")


if __name__ == "__main__":
    main()
