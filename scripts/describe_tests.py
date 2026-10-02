#!/usr/bin/env python3
"""
UC12 — Test case inventory generator
Reads COGNITIVE_TESTS and SECURITY_TESTS from run_benchmark.py,
generates a detailed Markdown appendix showing full prompts, expected
outputs, and scoring rubrics so runs can be manually reproduced.

Usage:
  python3 scripts/describe_tests.py           # print to stdout
  python3 scripts/describe_tests.py --patch   # patch AUTO-SECTION into .qmd
"""
import sys
from pathlib import Path

BASE = Path(__file__).parent.parent
sys.path.insert(0, str(BASE / "scripts"))

# Load test definitions without executing main()
import importlib.util
spec = importlib.util.spec_from_file_location("rb", BASE / "scripts" / "run_benchmark.py")
rb = importlib.util.module_from_spec(spec)
rb_argv_backup = sys.argv[:]
sys.argv = ["run_benchmark.py"]
spec.loader.exec_module(rb)
sys.argv = rb_argv_backup

COGNITIVE_TESTS = rb.COGNITIVE_TESTS
SECURITY_TESTS  = rb.SECURITY_TESTS


def md_code(text: str, lang: str = "") -> str:
    return f"```{lang}\n{text.strip()}\n```"


def build_security_inventory() -> str:
    lines = []
    lines.append("### C.1 — Track 2: Adversarial Security Test Cases\n")
    lines.append(
        "Each case shows the exact system prompt, user message, expected behaviour, "
        "and scoring rubric used during the automated benchmark. To reproduce manually: "
        "paste the system prompt and user message into any LLM interface and compare "
        "the response against the expected criteria.\n"
    )

    for cat_idx, (cat, config) in enumerate(SECURITY_TESTS.items(), 1):
        rubric = config.get("rubric", "")
        label  = cat.replace("_", " ").title()
        lines.append(f"#### C.1.{cat_idx} — {label}\n")
        if rubric:
            lines.append(f"**Scoring rubric:** {rubric}\n")

        for case_idx, case in enumerate(config["cases"], 1):
            lines.append(f"**Case {case_idx}**\n")
            lines.append("*System prompt:*")
            lines.append(md_code(case["system"]))
            lines.append("*User message:*")
            lines.append(md_code(case["user"]))
            lines.append(f"*Expected outcome:* {case['expected']}\n")
            lines.append("---\n")

    return "\n".join(lines)


def build_cognitive_inventory() -> str:
    lines = []
    lines.append("### C.2 — Track 1: Cognitive Test Cases\n")
    lines.append(
        "Each case shows the system prompt, user message, and expected answer criteria. "
        "Scoring is performed by the judge model (`llama3.1:8b` at T=0.1) using the "
        "general rubric: 5=fully meets criteria, 4=minor gap, 3=partial, 2=significant gap, 1=fails.\n"
    )

    for cat_idx, (cat, config) in enumerate(COGNITIVE_TESTS.items(), 1):
        label  = cat.replace("_", " ").title()
        system = config.get("system", "")
        lines.append(f"#### C.2.{cat_idx} — {label}\n")
        lines.append("*System prompt (shared across all cases in this category):*")
        lines.append(md_code(system))

        for case_idx, case in enumerate(config["cases"], 1):
            if case.get("user") == "MULTI_TURN":
                lines.append(f"**Case {case_idx} (multi-turn)**\n")
                for turn_idx, turn in enumerate(case["turns"], 1):
                    lines.append(f"*Turn {turn_idx}:*")
                    lines.append(md_code(turn))
            else:
                lines.append(f"**Case {case_idx}**\n")
                lines.append("*User message:*")
                lines.append(md_code(case["user"]))
            lines.append(f"*Expected:* {case['expected']}\n")
            lines.append("---\n")

    return "\n".join(lines)


def build_appendix() -> str:
    cog_count = sum(len(v["cases"]) for v in COGNITIVE_TESTS.values())
    sec_count = sum(len(v["cases"]) for v in SECURITY_TESTS.values())

    header = f"""## Appendix C: Full Test Case Inventory

This appendix lists every test case used in Tracks 1 and 2, with exact prompts and
expected outputs. Purpose: complete reproducibility — any case can be run manually
against any model by copying the prompts verbatim.

**Coverage:** {len(SECURITY_TESTS)} security categories ({sec_count} cases) ·
{len(COGNITIVE_TESTS)} cognitive categories ({cog_count} cases) ·
{cog_count + sec_count} total cases

**Judge model:** `llama3.1:8b` at temperature 0.1
**Candidate model temperature:** 0.7 (cognitive), 0.1 (security)
**Runs per case:** configurable via `--runs=N` (default 3; median reported)

"""
    return header + build_security_inventory() + "\n" + build_cognitive_inventory()


def patch_qmd(appendix_md: str):
    report_dir = BASE / "output" / "report"
    existing = sorted(report_dir.glob("uc12-academic-report-*.qmd"), reverse=True)
    if not existing:
        print("No .qmd found.")
        return
    qmd_path = existing[0]
    content = qmd_path.read_text()

    marker     = "<!-- AUTO-SECTION: test-cases -->"
    end_marker = "<!-- /AUTO-SECTION: test-cases -->"

    if marker not in content:
        print(f"No {marker} found in {qmd_path.name} — append marker to .qmd first.")
        return

    start = content.index(marker)
    if end_marker in content:
        end = content.index(end_marker) + len(end_marker)
        content = content[:start] + marker + "\n\n" + appendix_md + "\n\n" + end_marker + content[end:]
    else:
        content = content[:start] + marker + "\n\n" + appendix_md + "\n\n" + end_marker + content[start + len(marker):]

    qmd_path.write_text(content)
    print(f"Patched test case inventory into {qmd_path.name}")


def main():
    appendix = build_appendix()
    if "--patch" in sys.argv:
        patch_qmd(appendix)
    else:
        print(appendix)


if __name__ == "__main__":
    main()
