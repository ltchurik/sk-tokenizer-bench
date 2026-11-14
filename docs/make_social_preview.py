#!/usr/bin/env python3
"""Render docs/social-preview.png (1280x640, GitHub social preview + README hero) from results/flores.

    pip install matplotlib
    python docs/make_social_preview.py
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

r = json.load(open(ROOT / "results" / "flores" / "results.json", encoding="utf-8"))
pick = [("GPT-4 / 3.5", "GPT-4 / 3.5 (cl100k_base)"), ("Qwen 2.5 / 3", "Qwen 2.5 / 3"),
        ("DeepSeek V3", "DeepSeek V3 / V3.1 / R1"), ("Llama 3", "Llama 3.x"),
        ("GPT-4o / GPT-5", "GPT-4o / 4.1 / 5 (o200k_base)"), ("Mistral", "Mistral Nemo / Small 3 / Large 2 (tekken)"),
        ("Gemma 3", "Gemma 2 / 3"), ("Llama 4", "Llama 4"), ("EuroLLM", "EuroLLM")]
data = [(lab, r[k]["ratio_vs_en"]["sk"]["ALL"]) for lab, k in pick]
SURF, INK, INK2, MUTED, BLUE = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8984", "#2a78d6"
plt.rcParams["font.family"] = "DejaVu Sans"
W, H, L = 1280, 640, 64
fig = plt.figure(figsize=(W / 100, H / 100), dpi=100, facecolor=SURF)
fig.text(L / W, 1 - 92 / H, "sk-tokenizer-bench", fontsize=21, color=BLUE, weight="bold", va="top")
fig.text(L / W, 1 - 146 / H, "How much more\ndoes Slovak cost\nin LLM tokens?", fontsize=33, color=INK, weight="bold", va="top", linespacing=1.18)
fig.text(L / W, 1 - 330 / H, "Same text, Slovak vs English:\n1.6× – 2.3× more tokens\non mainstream models.", fontsize=18, color=INK2, va="top", linespacing=1.45)
fig.text(L / W, 72 / H, "32 tokenizers · FLORES-200 · sk · cs · pl · hu · de\ngithub.com/ltchurik/sk-tokenizer-bench", fontsize=13, color=MUTED, va="bottom", linespacing=1.6)
ax = fig.add_axes([770 / W, 120 / H, 420 / W, 410 / H], facecolor=SURF)
n, bh = len(data), 0.52
for i, (lab, v) in enumerate(data):
    y = n - 1 - i
    ax.add_patch(FancyBboxPatch((0, y - bh / 2), v, bh, boxstyle="round,pad=0,rounding_size=0.06", mutation_aspect=4.5, fc=BLUE, ec="none"))
    ax.add_patch(plt.Rectangle((0, y - bh / 2), v - 0.1, bh, fc=BLUE, ec="none", antialiased=False))
    ax.text(v + 0.05, y, f"{v:.2f}×", va="center", ha="left", fontsize=15, color=INK, weight="bold")
    ax.text(-0.06, y, lab, va="center", ha="right", fontsize=14, color=INK2)
top = n - 0.35
ax.plot([1, 1], [-0.6, top], color=SURF, lw=2.5, zorder=3, solid_capstyle="butt")
ax.plot([1, 1], [-0.6, top], color=INK, lw=1.2, zorder=4, solid_capstyle="butt")
ax.text(1.0, top + 0.1, "English = 1×", ha="center", va="bottom", fontsize=13, color=INK2)
ax.set_xlim(0, 2.55); ax.set_ylim(-0.6, n + 0.3); ax.axis("off")
ax.text(-0.75, -1.1, "Slovak tokens ÷ English tokens, same content", fontsize=12, color=MUTED, ha="left", va="center")
fig.savefig(ROOT / "docs" / "social-preview.png", dpi=100, facecolor=SURF)
