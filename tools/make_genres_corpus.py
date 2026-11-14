#!/usr/bin/env python3
"""Build corpus/genres.jsonl: real Slovak/English text by genre, from two openly licensed sources.

    python tools/make_genres_corpus.py

- WMT24++ (Google, Apache 2.0), en-sk_SK: social-media posts, speech transcripts, literary prose
  and news, human-translated into Slovak and post-edited. Segments flagged `is_bad_source` and
  the canary line are left out.
- EUR-Lex (© European Union, reuse authorised under Commission Decision 2011/833/EU): paragraphs
  of three EU acts in their official Slovak and English versions, fetched from the Publications
  Office (Cellar). Both language versions have the same paragraph structure, so paragraphs are
  aligned by position.

The output is deterministic; corpus/README.md documents the result.
"""
import html
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "corpus" / "genres.jsonl"

WMT_REV = "fd7405c06494bc66a57b25f55d217a72f96e60dc"
WMT_URL = f"https://huggingface.co/datasets/google/wmt24pp/resolve/{WMT_REV}/en-sk_SK.jsonl"
WMT_DOMAINS = ["social", "speech", "literary", "news"]

ACTS = {  # CELEX number: short name
    "32016R0679": "GDPR",
    "32024R1689": "AI Act",
    "32011L0083": "Consumer Rights Directive",
}
PER_ACT = 100     # paragraphs taken from each act, evenly spaced
MIN_CHARS = 60    # skip numbering, headings and one-liners


def get(url, headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": "sk-tokenizer-bench", **(headers or {})})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read().decode("utf-8")


def wmt_rows():
    rows = []
    for line in get(WMT_URL).splitlines():
        r = json.loads(line)
        if r["domain"] not in WMT_DOMAINS or r["is_bad_source"]:
            continue
        sk, en = r["target"].strip(), r["source"].strip()
        if sk and en:
            rows.append({"id": f"wmt24pp-{r['segment_id']}", "domain": r["domain"], "sk": sk, "en": en})
    return rows


def act_paragraphs(celex, lang):
    xhtml = get(f"http://publications.europa.eu/resource/celex/{celex}",
                {"Accept": "application/xhtml+xml", "Accept-Language": lang})
    out = []
    for cls, body in re.findall(r'<p[^>]*class="([^"]*)"[^>]*>(.*?)</p>', xhtml, re.S):
        text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", body))).strip()
        out.append((cls, text))
    return out


def law_rows():
    rows = []
    for celex, name in ACTS.items():
        sk, en = act_paragraphs(celex, "slk"), act_paragraphs(celex, "eng")
        if [c for c, _ in sk] != [c for c, _ in en]:
            raise SystemExit(f"{name}: Slovak and English paragraph structure differ, cannot align")
        pairs = [(i, s, e) for i, ((c, s), (_, e)) in enumerate(zip(sk, en))
                 if c == "oj-normal" and len(s) >= MIN_CHARS and len(e) >= MIN_CHARS]
        step = len(pairs) / PER_ACT
        for k in range(min(PER_ACT, len(pairs))):
            i, s, e = pairs[int(k * step)]
            rows.append({"id": f"eurlex-{celex}-{i}", "domain": "law", "sk": s, "en": e})
    return rows


def main():
    rows = wmt_rows() + law_rows()
    with open(OUT, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    counts = {}
    for r in rows:
        counts[r["domain"]] = counts.get(r["domain"], 0) + 1
    print(f"wrote {len(rows)} rows to {OUT.relative_to(ROOT)}: {counts}")


if __name__ == "__main__":
    main()
