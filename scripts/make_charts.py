#!/usr/bin/env python3
"""
UC12 — Chart generator v2
Reads latest *-summary-v2.json → writes SVG charts to output/report/charts/.

Charts produced:
  bar_chart.svg        grouped bar: model × cognitive category
  radar_chart.svg      spider: cognitive profile per model
  heatmap.svg          model × category heatmap
  box_plot.svg         score distribution (requires individual run CSV)
  scatter_size_score.svg  model size (GB) vs total score
  pareto_scatter.svg   tokens/sec vs total score (efficiency frontier)

Usage: python3 scripts/make_charts.py
"""

import json
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

BASE      = Path(__file__).parent.parent
RUNS      = BASE / "output" / "runs"
CHART_DIR = BASE / "output" / "report" / "charts"
CHART_DIR.mkdir(parents=True, exist_ok=True)

MODEL_SIZES_GB = {
    "hermes3":   4.7,
    "qwen3":     9.3,
    "phi4":      9.1,
    "llama3.1":  4.9,
}

COLORS = ["#2563EB", "#DC2626", "#16A34A", "#D97706"]   # blue, red, green, amber

def load_latest() -> dict:
    files = sorted(RUNS.glob("*-summary-v2.json"), reverse=True)
    if not files:
        # Fall back to v1 summary
        files = sorted(RUNS.glob("*-summary.json"), reverse=True)
        if not files:
            sys.exit("No summary JSON found. Run run_benchmark.py first.")
    with open(files[0]) as f:
        data = json.load(f)
    print(f"Loaded: {files[0].name}")
    return data

def short(model: str) -> str:
    return model.split(":")[0]

def make_bar_chart(data: dict):
    results = data.get("cognitive_results") or data.get("results", {})
    models  = [short(m) for m in data["models"]]
    cats    = [c.replace("_", " ").title() for c in results]
    scores  = {short(m): [results[c][m] for c in results] for m in data["models"]}

    x = np.arange(len(cats))
    w = 0.8 / len(models)

    fig, ax = plt.subplots(figsize=(10, 5))
    for i, (m, color) in enumerate(zip(models, COLORS)):
        offset = (i - len(models) / 2 + 0.5) * w
        bars = ax.bar(x + offset, scores[m], w, label=m, color=color, alpha=0.85)
        for bar, val in zip(bars, scores[m]):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                    str(val), ha="center", va="bottom", fontsize=7)

    ax.set_xticks(x)
    ax.set_xticklabels(cats, rotation=20, ha="right", fontsize=9)
    ax.set_ylabel("Median Score (1–5)")
    ax.set_ylim(0, 5.8)
    ax.set_title("Cognitive Performance by Category", fontweight="bold")
    ax.legend(loc="upper right", fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    out = CHART_DIR / "bar_chart.svg"
    plt.savefig(out, format="svg")
    plt.close()
    print(f"  bar_chart.svg")

def make_radar_chart(data: dict):
    results = data.get("cognitive_results") or data.get("results", {})
    models  = [short(m) for m in data["models"]]
    cats    = list(results.keys())
    N       = len(cats)
    angles  = [2 * math.pi * i / N for i in range(N)] + [0]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={"polar": True})
    for m_full, color in zip(data["models"], COLORS):
        m = short(m_full)
        vals = [results[c][m_full] for c in cats] + [results[cats[0]][m_full]]
        ax.plot(angles, vals, color=color, linewidth=1.5, label=m)
        ax.fill(angles, vals, color=color, alpha=0.08)

    ax.set_thetagrids(
        [a * 180 / math.pi for a in angles[:-1]],
        [c.replace("_", " ").title() for c in cats],
        fontsize=8,
    )
    ax.set_ylim(0, 5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(["1", "2", "3", "4", "5"], fontsize=6)
    ax.set_title("Cognitive Capability Profile", fontweight="bold", pad=15)
    ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1), fontsize=8)
    plt.tight_layout()
    plt.savefig(CHART_DIR / "radar_chart.svg", format="svg")
    plt.close()
    print(f"  radar_chart.svg")

def make_heatmap(data: dict):
    results = data.get("cognitive_results") or data.get("results", {})
    models  = [short(m) for m in data["models"]]
    cats    = list(results.keys())

    matrix = np.array([[results[c][m] for m in data["models"]] for c in cats])

    fig, ax = plt.subplots(figsize=(7, 4))
    im = ax.imshow(matrix, cmap="YlGn", vmin=1, vmax=5, aspect="auto")

    ax.set_xticks(range(len(models)))
    ax.set_xticklabels(models, fontsize=9)
    ax.set_yticks(range(len(cats)))
    ax.set_yticklabels([c.replace("_", " ").title() for c in cats], fontsize=9)

    for i in range(len(cats)):
        for j in range(len(models)):
            ax.text(j, i, str(matrix[i, j]), ha="center", va="center",
                    fontsize=11, fontweight="bold",
                    color="white" if matrix[i, j] >= 4 else "black")

    plt.colorbar(im, ax=ax, label="Score (1–5)")
    ax.set_title("Performance Heatmap: Model × Category", fontweight="bold")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "heatmap.svg", format="svg")
    plt.close()
    print(f"  heatmap.svg")

def make_size_score_scatter(data: dict):
    totals = data.get("cognitive_totals") or data.get("totals", {})
    models = data["models"]

    fig, ax = plt.subplots(figsize=(6, 5))
    for m_full, color in zip(models, COLORS):
        m = short(m_full)
        size  = MODEL_SIZES_GB.get(m, 0)
        score = totals.get(m_full, totals.get(m, 0))
        ax.scatter(size, score, color=color, s=120, zorder=3)
        ax.annotate(m, (size, score), textcoords="offset points",
                    xytext=(8, 4), fontsize=9)

    ax.set_xlabel("Model Size (GB)")
    ax.set_ylabel("Total Cognitive Score")
    ax.set_title("Model Size vs. Total Score\n(H1: no strong correlation expected)",
                 fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(CHART_DIR / "scatter_size_score.svg", format="svg")
    plt.close()
    print(f"  scatter_size_score.svg")

def make_pareto_scatter(data: dict):
    telemetry = data.get("telemetry", {})
    totals    = data.get("cognitive_totals") or data.get("totals", {})
    models    = data["models"]

    has_tps = any(
        telemetry.get(m, {}).get("gen_tokens_per_sec")
        for m in models
    )
    if not has_tps:
        print("  pareto_scatter.svg — skipped (no latency data; re-run with Ollama native API)")
        return

    fig, ax = plt.subplots(figsize=(6, 5))
    for m_full, color in zip(models, COLORS):
        m   = short(m_full)
        tps = telemetry.get(m_full, {}).get("gen_tokens_per_sec")
        score = totals.get(m_full, totals.get(m, 0))
        if tps is None:
            continue
        ax.scatter(tps, score, color=color, s=120, zorder=3)
        ax.annotate(m, (tps, score), textcoords="offset points",
                    xytext=(8, 4), fontsize=9)

    ax.set_xlabel("Generation Speed (tokens/sec)")
    ax.set_ylabel("Total Cognitive Score")
    ax.set_title("Efficiency Frontier: Speed vs. Quality", fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(CHART_DIR / "pareto_scatter.svg", format="svg")
    plt.close()
    print(f"  pareto_scatter.svg")

def make_security_heatmap(data: dict):
    sec = data.get("security_results", {})
    if not sec:
        print("  security_heatmap.svg — skipped (no security data)")
        return

    models = [short(m) for m in data["models"]]
    cats   = list(sec.keys())
    matrix = np.array([[sec[c][m] for m in data["models"]] for c in cats])

    fig, ax = plt.subplots(figsize=(7, 3.5))
    im = ax.imshow(matrix, cmap="RdYlGn", vmin=1, vmax=5, aspect="auto")

    ax.set_xticks(range(len(models)))
    ax.set_xticklabels(models, fontsize=9)
    ax.set_yticks(range(len(cats)))
    ax.set_yticklabels([c.replace("_", " ").title() for c in cats], fontsize=9)

    for i in range(len(cats)):
        for j in range(len(models)):
            ax.text(j, i, str(matrix[i, j]), ha="center", va="center",
                    fontsize=11, fontweight="bold",
                    color="white" if matrix[i, j] <= 2 else "black")

    plt.colorbar(im, ax=ax, label="Score (1=fail, 5=pass)")
    ax.set_title("Adversarial Security Posture", fontweight="bold")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "security_heatmap.svg", format="svg")
    plt.close()
    print(f"  security_heatmap.svg")

def make_box_plot(data: dict):
    """Box plot of per-run scores per model per category. Requires CSV with ≥5 rows per cell."""
    import csv
    csv_files = sorted(RUNS.glob("*-run-v2*.csv"), reverse=True)
    if not csv_files:
        csv_files = sorted(RUNS.glob("*-run-*.csv"), reverse=True)
    if not csv_files:
        print("  box_plot.svg — skipped (no CSV found)")
        return

    # Load all run rows
    rows = []
    with open(csv_files[0]) as f:
        for row in csv.DictReader(f):
            if row.get("track", "cognitive") == "cognitive":
                rows.append(row)

    if not rows:
        print("  box_plot.svg — skipped (no cognitive rows in CSV)")
        return

    models = [short(m) for m in data["models"]]
    results = data.get("cognitive_results") or data.get("results", {})
    cats = list(results.keys())

    # Group scores: {category: {model: [scores]}}
    score_map: dict[str, dict[str, list[int]]] = {c: {m: [] for m in models} for c in cats}
    for row in rows:
        cat = row.get("category", "")
        m   = short(row.get("model", ""))
        s   = row.get("score")
        if cat in score_map and m in score_map[cat] and s:
            score_map[cat][m].append(int(s))

    # Only plot if we have ≥4 data points for at least one cell
    has_data = any(
        len(score_map[c][m]) >= 4
        for c in cats for m in models
    )
    if not has_data:
        print("  box_plot.svg — skipped (need --runs 10 for meaningful box plots)")
        return

    for cat in cats:
        plot_data = [score_map[cat][m] or [0] for m in models]
        fig, ax = plt.subplots(figsize=(5, 4))
        bp = ax.boxplot(plot_data, patch_artist=True, widths=0.6)
        for patch, color in zip(bp["boxes"], COLORS):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        ax.set_title(f"Score Variance — {cat.replace('_', ' ').title()}", fontweight="bold")
        ax.set_xticks(range(1, len(models) + 1))
        ax.set_xticklabels(models, rotation=30, ha="right", fontsize=9)
        ax.set_ylabel("Score (1–5)")
        ax.set_ylim(0, 5.5)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        plt.tight_layout()
        fname = f"box_plot_{cat}.svg"
        plt.savefig(CHART_DIR / fname, format="svg")
        plt.close()
        print(f"  {fname}")


def main():
    data = load_latest()
    print("Generating charts:")
    make_bar_chart(data)
    make_radar_chart(data)
    make_heatmap(data)
    make_size_score_scatter(data)
    make_pareto_scatter(data)
    make_security_heatmap(data)
    make_box_plot(data)
    print(f"\nAll charts → {CHART_DIR}")

if __name__ == "__main__":
    main()
