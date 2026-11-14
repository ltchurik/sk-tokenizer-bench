"""Corpus loading, measurement and statistics."""
import json
import unicodedata
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
CORPORA = {
    "flores": ROOT / "corpus" / "flores200_devtest.jsonl",
    "custom": ROOT / "corpus" / "parallel.jsonl",
}
META_KEYS = {"id", "domain"}
BASE = "en"
NO_DIACRITICS = "sk_nd"  # derived column: Slovak with diacritics stripped (how much of the penalty is diacritics?)


def strip_diacritics(text):
    """ľščťžýáíéďňôúäŕĺ -> lsctzyaiednouarl; everything else untouched."""
    decomposed = unicodedata.normalize("NFD", text)
    return unicodedata.normalize("NFC", "".join(c for c in decomposed if not unicodedata.combining(c)))


def load_corpus(path):
    rows = [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]
    langs = [k for k in rows[0] if k not in META_KEYS]
    for r in rows:
        missing = [lg for lg in langs if not r.get(lg)]
        if missing:
            raise ValueError(f"{path}: row {r.get('id')} missing {missing}")
    if BASE not in langs:
        raise ValueError(f"{path}: baseline language {BASE!r} not in corpus")
    # baseline last, others in file order
    langs = [lg for lg in langs if lg != BASE] + [BASE]
    if "sk" in langs:
        for r in rows:
            r[NO_DIACRITICS] = strip_diacritics(r["sk"])
        langs.insert(langs.index("sk") + 1, NO_DIACRITICS)
    return rows, langs


def ratio_ci(num, den, n_boot=2000, seed=0):
    """95 % percentile bootstrap CI of sum(num)/sum(den), resampling sentences."""
    num, den = np.asarray(num, dtype=np.int64), np.asarray(den, dtype=np.int64)
    if n_boot <= 0 or len(num) < 2:
        r = num.sum() / den.sum()
        return float(r), float(r)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(num), size=(n_boot, len(num)))
    ratios = num[idx].sum(axis=1) / den[idx].sum(axis=1)
    lo, hi = np.percentile(ratios, [2.5, 97.5])
    return round(float(lo), 3), round(float(hi), 3)


def measure(counter, rows, langs, n_boot=2000):
    """Run one tokenizer over a corpus. Returns (summary dict, per-sentence counts)."""
    per_sentence = {lg: counter([r[lg] for r in rows]) for lg in langs}
    domains = sorted({r["domain"] for r in rows})
    tot = defaultdict(lambda: defaultdict(int))
    chars = defaultdict(int)
    for i, r in enumerate(rows):
        for lg in langs:
            n = per_sentence[lg][i]
            tot[lg][r["domain"]] += n
            tot[lg]["ALL"] += n
            chars[lg] += len(r[lg])
    summary = {
        "tokens": {lg: dict(tot[lg]) for lg in langs},
        "chars_per_token": {lg: round(chars[lg] / tot[lg]["ALL"], 3) for lg in langs},
        f"ratio_vs_{BASE}": {
            lg: {d: round(tot[lg][d] / tot[BASE][d], 3) for d in domains + ["ALL"]} for lg in langs if lg != BASE
        },
        f"ci95_vs_{BASE}": {
            lg: ratio_ci(per_sentence[lg], per_sentence[BASE], n_boot) for lg in langs if lg != BASE
        },
    }
    return summary, per_sentence


def mark_identical(results, counts):
    """Tag tokenizers whose per-sentence counts match an earlier one on every language."""
    seen = {}
    for name in results:
        sig = tuple(tuple(counts[name][lg]) for lg in sorted(counts[name]))
        results[name]["same_as"] = seen.get(sig)
        seen.setdefault(sig, name)
