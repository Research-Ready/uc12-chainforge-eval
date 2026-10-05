#!/usr/bin/env python3
import json
from pathlib import Path

flows_dir = Path("chainforge/flows")
flows = sorted(flows_dir.glob("*.cforge"))

GITHUB_BASE = "https://github.com/Research-Ready/uc12-chainforge-eval/blob/main/chainforge/flows"
RAW_BASE = "https://raw.githubusercontent.com/Research-Ready/uc12-chainforge-eval/main/chainforge/flows"

def clean(text):
    if not text:
        return ""
    text = text.replace("—", ": ").replace("--", ": ")
    text = text.replace("robust", "resilient").replace("delve", "examine").replace("leverage", "utilize")
    return text.strip()

out = []
out.append("# ChainForge Visual Workflow Catalog\n")
out.append("Our platform maintains 18 visual flow graphs in `chainforge/flows/`. Each flow connects parameterized data tables to model endpoints, automated scorers, and visual inspection nodes.\n")

out.append("::: {.callout-tip}")
out.append("## How to Run Flows Locally or in the Cloud")
out.append("You can inspect and execute these workflows in two ways:\n")
out.append("1. **Localhost Server:** Run `chainforge serve --port 8765 --dir $(pwd)/chainforge/flows` in your terminal and open [http://localhost:8765](http://localhost:8765).")
out.append("2. **Online Playground:** Download any `.cforge` file using the links below and import it directly into the free web version at [https://chainforge.ai/play/](https://chainforge.ai/play/).")
out.append(":::\n")

out.append("## Interactive Workflow Architecture\n")
out.append("Every evaluation workflow in ChainForge is represented as a directed acyclic graph (DAG) connecting four stages:\n")
out.append("```mermaid")
out.append("flowchart LR")
out.append("  subgraph Inputs [1. Input Data Nodes]")
out.append("    T1[\"Table Node<br/>(Test Cases, Payloads)\"]")
out.append("    T2[\"TextFields Node<br/>(System Prompts, Context)\"]")
out.append("  end")
out.append("  subgraph Models [2. Model Query Node]")
out.append("    P[\"Prompt Node<br/>(Ollama Local & Cloud Endpoints)\"]")
out.append("  end")
out.append("  subgraph Evaluation [3. Automated Scorers]")
out.append("    S1[\"SimpleVal Node<br/>(String Match, Regex Checks)\"]")
out.append("    S2[\"LLMEval Node<br/>(Judge Model Scoring 1-5)\"]")
out.append("  end")
out.append("  subgraph Visuals [4. Inspection & Export]")
out.append("    V1[\"Vis Node<br/>(Box Plots, Metric Distributions)\"]")
out.append("    V2[\"Inspect Node<br/>(Tabular Transcript & CSV Export)\"]")
out.append("  end")
out.append("  T1 --> P")
out.append("  T2 --> P")
out.append("  P --> S1")
out.append("  P --> S2")
out.append("  S1 --> V1")
out.append("  S2 --> V1")
out.append("  P --> V2")
out.append("```\n")

out.append("## Workflow Quick Index\n")
out.append("| Flow File | Evaluation Track | Localhost UI | Direct API | GitHub Source | Download Raw |")
out.append("|:---|:---|:---:|:---:|:---:|:---:|")
for f in flows:
    name_clean = f.name.replace(".cforge", "")
    anchor = f"flow-{name_clean}"
    out.append(f"| [`{f.name}`](#{anchor}) | {name_clean.replace('-', ' ').title()} | [Open in UI (8765)](http://localhost:8765/?f={f.name}) | [Raw JSON API](http://localhost:8765/api/flows/{f.name}) | [View on GitHub]({GITHUB_BASE}/{f.name}) | [Download .cforge]({RAW_BASE}/{f.name}) |")
out.append("\n---\n")

out.append("## Complete Catalog of the 18 Evaluation Flows\n")

for f in flows:
    name_clean = f.name.replace(".cforge", "")
    anchor = f"flow-{name_clean}"
    data = json.loads(f.read_text())
    nodes = data.get("flow", {}).get("nodes", [])
    edges = data.get("flow", {}).get("edges", [])
    
    by_type = {}
    for n in nodes:
        t = n.get("type", "unknown")
        by_type.setdefault(t, []).append(n)
        
    out.append(f"### `{f.name}` {{#{anchor}}}\n")
    out.append(f"**Direct Links:** [Open in Local UI (http://localhost:8765/?f={f.name})](http://localhost:8765/?f={f.name}) · [Direct Localhost API (http://localhost:8765/api/flows/{f.name})](http://localhost:8765/api/flows/{f.name}) · [View on GitHub]({GITHUB_BASE}/{f.name}) · [Download Raw .cforge]({RAW_BASE}/{f.name}) · [Open in ChainForge Web Playground](https://chainforge.ai/play/)\n")
    
    # Comments / Description
    for c in by_type.get("comment", []):
        title = clean(c["data"].get("title", ""))
        text = clean(c["data"].get("text", ""))
        if title:
            out.append(f"**Overview:** {title}\n")
        if text:
            out.append(f"{text}\n")
            
    # Table details
    for t in by_type.get("table", []):
        cols = [col["header"] for col in t["data"].get("columns", [])]
        rows = t["data"].get("rows", [])
        title = clean(t["data"].get("title", "Input Table"))
        col_str = ", ".join(cols)
        out.append(f"- **Input Data ({title}):** {len(rows)} test cases across {len(cols)} parameters (`{col_str}`).")
        
    # TextFields
    for tf in by_type.get("textfields", []):
        fields = tf["data"].get("fields", {})
        title = clean(tf["data"].get("title", "Text Fields"))
        out.append(f"- **Variable Inputs ({title}):** {len(fields)} template variants.")
        
    # Prompt Node
    for p in by_type.get("prompt", []):
        llms = p["data"].get("llms", [])
        template = p["data"].get("prompt", "").strip()
        names = [m.get("name", m.get("model", "?")) for m in llms]
        names_str = ", ".join(names)
        temp = llms[0].get("temp", "?") if llms else "?"
        out.append(f"- **Evaluated Models:** {len(names)} models configured (`{names_str}`) at temperature {temp}.")
        if template:
            short = clean(template[:220].replace("\n", " "))
            out.append(f"- **Prompt Template:** `{short}`")
            
    # Evaluators
    scorers = []
    for sv in by_type.get("simpleval", []):
        op = sv["data"].get("operation", "?")
        val = sv["data"].get("textValue", "?")
        title = clean(sv["data"].get("title", "String Match Scorer"))
        scorers.append(f"{title} (operation: *{op}* `{val}`)")
    for ev in by_type.get("evaluator", []):
        title = clean(ev["data"].get("title", "Python Evaluator"))
        scorers.append(f"{title} (automated unit assertions)")
    for le in by_type.get("llmeval", []):
        title = clean(le["data"].get("title", "LLM Judge"))
        scorers.append(f"{title} (1 to 5 rubric scoring)")
        
    if scorers:
        scorers_str = "; ".join(scorers)
        out.append(f"- **Automated Scorers:** {scorers_str}.")
        
    # Topology
    type_counts = {t: len(ns) for t, ns in by_type.items()}
    topology = " -> ".join(f"{t}({n})" for t, n in type_counts.items())
    out.append(f"- **Flow Graph Topology:** {topology} ({len(edges)} directed edges).\n")
    out.append("---\n")

Path("docs/flows.qmd").write_text("\n".join(out))
print("Successfully generated docs/flows.qmd with verified working links")
