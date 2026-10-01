#!/usr/bin/env python3
"""
UC12 — C23: ChainForge Flow Describer
Reads .cforge JSON files and generates Markdown documentation of each flow.
Output is intended for embedding in the academic report via the
<!-- AUTO-SECTION: chainforge-flows --> marker.

Usage:
  python3 scripts/describe_flows.py            # prints Markdown to stdout
  python3 scripts/describe_flows.py --patch    # patches it into the .qmd
"""

import json
import sys
from pathlib import Path

BASE       = Path(__file__).parent.parent
FLOWS_DIR  = BASE / "chainforge" / "flows"
REPORT_DIR = BASE / "output" / "report"


def describe_flow(path: Path) -> str:
    data  = json.loads(path.read_text())
    nodes = data["flow"]["nodes"]
    edges = data["flow"].get("edges", [])

    by_type: dict[str, list[dict]] = {}
    for n in nodes:
        t = n.get("type", "unknown")
        by_type.setdefault(t, []).append(n)

    lines = [f"### `{path.name}`"]

    # Comment node = description
    for c in by_type.get("comment", []):
        title = c["data"].get("title", "")
        text  = c["data"].get("text", "").strip()
        if title:
            lines.append(f"\n**{title}**\n")
        if text:
            lines.append(text)

    # Table node = inputs
    for t in by_type.get("table", []):
        cols = [col["header"] for col in t["data"].get("columns", [])]
        rows = t["data"].get("rows", [])
        title = t["data"].get("title", "Input data")
        lines.append(f"\n**{title}:** {len(rows)} rows × {len(cols)} columns ({', '.join(cols)})")

    # TextFields node = variable inputs
    for tf in by_type.get("textfields", []):
        fields = tf["data"].get("fields", {})
        title  = tf["data"].get("title", "Text inputs")
        lines.append(f"\n**{title}:** {len(fields)} variants")

    # Prompt node = LLM config
    for p in by_type.get("prompt", []):
        llms     = p["data"].get("llms", [])
        template = p["data"].get("prompt", "").strip()
        names    = [m.get("name", m.get("model", "?")) for m in llms]
        temp     = llms[0].get("temp", "?") if llms else "?"
        lines.append(f"\n**Models:** {', '.join(names)} (temperature {temp})")
        if template:
            short = template[:200].replace("\n", " / ")
            if len(template) > 200:
                short += "..."
            lines.append(f"\n**Prompt template:** `{short}`")

    # Simpleval node = scorer
    for sv in by_type.get("simpleval", []):
        op    = sv["data"].get("operation", "?")
        val   = sv["data"].get("textValue", "?")
        title = sv["data"].get("title", "Scorer")
        lines.append(f"\n**Scorer:** {title} — operation: *{op}* `{val}`")

    # Node topology summary
    type_counts = {t: len(ns) for t, ns in by_type.items()}
    topology    = " → ".join(f"{t}({n})" for t, n in type_counts.items())
    lines.append(f"\n**Flow topology:** {topology} ({len(edges)} edges)")

    return "\n".join(lines)


def generate_section() -> str:
    flows = sorted(FLOWS_DIR.glob("*.cforge"))
    if not flows:
        return "_No ChainForge flows found in `chainforge/flows/`._"

    parts = [
        "## ChainForge Visual Evaluation Flows",
        "",
        "Each flow is loadable in the ChainForge UI at `http://localhost:8765`. "
        "Flows connect data table nodes to LLM prompt nodes to scoring and inspection nodes, "
        "allowing interactive exploration of model behaviour on the same test cases used in the "
        "automated benchmark scripts.",
        "",
    ]
    for flow in flows:
        parts.append(describe_flow(flow))
        parts.append("")
    return "\n".join(parts)


def patch_qmd(section: str):
    existing = sorted(REPORT_DIR.glob("uc12-academic-report-*.qmd"), reverse=True)
    if not existing:
        print("No .qmd found — cannot patch.")
        return
    qmd_path = existing[0]
    content  = qmd_path.read_text()
    marker   = "<!-- AUTO-SECTION: chainforge-flows -->"
    end_m    = "<!-- /AUTO-SECTION: chainforge-flows -->"

    if marker not in content:
        print(f"Marker {marker!r} not in {qmd_path.name} — appending to end of file.")
        content += f"\n\n{marker}\n\n{section}\n\n{end_m}\n"
    else:
        start = content.index(marker)
        if end_m in content:
            end = content.index(end_m) + len(end_m)
            content = content[:start] + marker + "\n\n" + section + "\n\n" + end_m + content[end:]
        else:
            content = content[:start] + marker + "\n\n" + section + "\n\n" + content[start + len(marker):]
    qmd_path.write_text(content)
    print(f"Patched ChainForge flows section into {qmd_path.name}")


def main():
    section = generate_section()
    if "--patch" in sys.argv:
        patch_qmd(section)
    else:
        print(section)


if __name__ == "__main__":
    main()
