#!/usr/bin/env python3
"""Render docs/tokenizer-timeline.png: Slovak/English token ratio vs tokenizer release date.

    pip install matplotlib
    python docs/make_timeline.py
"""
import json
import sys
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from skbench.registry import LINEAGES, RELEASED  # noqa: E402

SURF, INK, INK2, MUTED, GRID, OTHER = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8984", "#e4e3df", "#b9b8b2"
# Reference categorical slots 1-4, fixed order (validated adjacent-pair palette).
COLORS = {"OpenAI": "#2a78d6", "Meta": "#eb6834", "Mistral": "#1baf7a", "Google": "#eda100"}
SHORT = {
    "GPT-4 / 3.5 (cl100k_base)": "GPT-4", "GPT-4o / 4.1 / 5 (o200k_base)": "GPT-4o / 5",
    "Llama 2": "Llama 2", "Llama 3.x": "Llama 3", "Llama 4": "Llama 4",
    "Mistral / Mixtral (v3)": "Mistral v3", "Mistral Nemo / Small 3 / Large 2 (tekken)": "tekken",
    "Gemma 1 / 2": "Gemma 1/2", "Gemma 3": "Gemma 3",
    "EuroLLM": "EuroLLM", "BLOOM": "BLOOM", "Falcon 3": "Falcon 3",
    "Qwen 2.5 / 3": "Qwen", "Teuken (OpenGPT-X)": "Teuken",
}
# direct-label placement in points: (dx, dy, horizontal alignment), checked by eye on the render
OFFSET = {
    "GPT-4 / 3.5 (cl100k_base)": (10, 0, "left"), "GPT-4o / 4.1 / 5 (o200k_base)": (-10, -2, "right"),
    "Llama 2": (10, -12, "left"), "Llama 3.x": (-10, 4, "right"), "Llama 4": (10, -6, "left"),
    "Mistral / Mixtral (v3)": (-10, 4, "right"), "Mistral Nemo / Small 3 / Large 2 (tekken)": (4, -30, "left"),
    "Gemma 1 / 2": (-10, -6, "right"), "Gemma 3": (10, 6, "left"),
    "EuroLLM": (8, 0, "left"), "BLOOM": (8, 0, "left"), "Falcon 3": (8, 0, "left"), "Qwen 2.5 / 3": (8, 0, "left"),
    "Teuken (OpenGPT-X)": (8, 0, "left"),
}


def when(ym):
    y, m = map(int, ym.split("-"))
    return date(y, m, 15)


def main():
    res = json.loads((ROOT / "results" / "flores" / "results.json").read_text(encoding="utf-8"))
    ratio = {n: r["ratio_vs_en"]["sk"]["ALL"] for n, r in res.items() if not r.get("same_as")}
    in_lineage = {n for names in LINEAGES.values() for n in names}

    plt.rcParams["font.family"] = "DejaVu Sans"
    fig, ax = plt.subplots(figsize=(12, 6), dpi=100, facecolor=SURF)
    ax.set_facecolor(SURF)
    fig.subplots_adjust(left=0.08, right=0.97, top=0.82, bottom=0.12)

    # other tokenizers: recessive gray context dots
    others = [n for n in ratio if n in RELEASED and n not in in_lineage]
    ax.scatter([when(RELEASED[n]) for n in others], [ratio[n] for n in others], s=46, color=OTHER,
               edgecolor=SURF, linewidth=2, zorder=2, label="other tokenizers")
    for n in others:
        if n in SHORT:
            dx, dy, ha = OFFSET.get(n, (8, 0, "left"))
            ax.annotate(SHORT[n], (when(RELEASED[n]), ratio[n]), xytext=(dx, dy),
                        textcoords="offset points", fontsize=10, color=MUTED, va="center", ha=ha)

    for vendor, names in LINEAGES.items():
        pts = [(when(RELEASED[n]), ratio[n], n) for n in names if n in ratio]
        ax.plot([p[0] for p in pts], [p[1] for p in pts], color=COLORS[vendor], lw=2, zorder=3,
                solid_capstyle="round", solid_joinstyle="round")
        ax.scatter([p[0] for p in pts], [p[1] for p in pts], s=72, color=COLORS[vendor], edgecolor=SURF,
                   linewidth=2, zorder=4, label=vendor)
        for x, y, n in pts:
            dx, dy, ha = OFFSET.get(n, (8, 6, "left"))
            ax.annotate(f"{SHORT[n]}  {y:.2f}×", (x, y), xytext=(dx, dy), textcoords="offset points",
                        fontsize=11, color=INK, va="center", ha=ha,
                        bbox=dict(boxstyle="square,pad=0.15", fc=SURF, ec="none", alpha=0.85))

    ax.axhline(1.0, color=INK2, lw=1, zorder=1)
    ax.annotate("English = 1×", (date(2022, 8, 1), 1.0), xytext=(0, 6), textcoords="offset points",
                fontsize=10, color=INK2)
    ax.set_ylim(0.9, 2.45)
    ax.set_xlim(date(2022, 5, 1), date(2026, 2, 1))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.1f}×"))
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.grid(axis="y", color=GRID, lw=1)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=11, length=0)
    ax.set_ylabel("Slovak tokens per English token", color=INK2, fontsize=11)

    fig.text(0.08, 0.93, "Slovak token tax by tokenizer release date", fontsize=18, weight="bold", color=INK)
    fig.text(0.08, 0.875, "FLORES-200 devtest, sk/en token ratio, tokenizers released since mid-2022. "
             "Lines connect successive tokenizers of one vendor; lower is cheaper.", fontsize=11, color=INK2)
    leg = ax.legend(loc="upper right", frameon=False, fontsize=11, labelcolor=INK2, ncol=5,
                    bbox_to_anchor=(1.0, 1.1), handletextpad=0.3, columnspacing=1.2)
    for h in leg.legend_handles:
        h.set_sizes([60])
    out = ROOT / "docs" / "tokenizer-timeline.png"
    fig.savefig(out, dpi=100, facecolor=SURF)
    print(out)


if __name__ == "__main__":
    main()
