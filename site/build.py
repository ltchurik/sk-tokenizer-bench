#!/usr/bin/env python3
"""Assemble the static web calculator into _site/.

    python site/build.py            # writes _site/ (index.html, app.js, style.css, data.json, images)
    python -m http.server -d _site  # preview at http://localhost:8000

data.json is derived from results/flores/results.json, prices.json and the registry, so the page
always shows the numbers of the last benchmark run. Tokenizer download sizes come from the
Hugging Face API (best effort; the page works without them).
"""
import gzip
import json
import shutil
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from skbench.registry import API_KINDS, RELEASED, TOKENIZERS, browser_repo  # noqa: E402

SITE, OUT = ROOT / "site", ROOT / "_site"
MULTILINGUAL = {"mT5", "EuroLLM", "Apertus (Swiss AI)", "Teuken (OpenGPT-X)"}


def group(name, kind):
    if kind in API_KINDS:
        return "api"
    if "(Slovak" in name or "(Czech" in name or "(Polish" in name:
        return "regional"
    return "multilingual" if name in MULTILINGUAL else "mainstream"


def size_mb(repo):
    try:
        url = f"https://huggingface.co/api/models/{repo}?blobs=true"
        with urllib.request.urlopen(url, timeout=20) as r:
            sib = {s["rfilename"]: s.get("size") for s in json.load(r)["siblings"]}
        return round(sib["tokenizer.json"] / 1e6, 1)
    except Exception as e:  # offline build: sizes are cosmetic
        print(f"size unknown for {repo}: {type(e).__name__}", file=sys.stderr)
        return None


def build_data():
    res = json.loads((ROOT / "results" / "flores" / "results.json").read_text(encoding="utf-8"))
    prices = json.loads((ROOT / "prices.json").read_text(encoding="utf-8"))
    # The page is about Slovak: merge tokenizers whose counts match on sk, sk_nd and en,
    # even if they differ on another language (e.g. tekken vs Apertus on one Ukrainian sentence).
    counts = json.loads(gzip.decompress((ROOT / "results" / "flores" / "counts.json.gz").read_bytes()))["counts"]
    first, aliases = {}, {}
    for name in res:
        sig = tuple(tuple(counts[name][lg]) for lg in ("sk", "sk_nd", "en"))
        if sig in first:
            aliases.setdefault(first[sig], []).append(name)
        else:
            first[sig] = name
    merged = {a for v in aliases.values() for a in v}
    rows = []
    for name, r in res.items():
        if name in merged:
            continue
        kind = TOKENIZERS[name][0]
        repo = browser_repo(name)
        R, C = r["ratio_vs_en"], r["chars_per_token"]
        rows.append({
            "name": name,
            "also": aliases.get(name, []),
            "group": group(name, kind),
            "repo": repo,
            "size_mb": size_mb(repo) if repo else None,
            "released": RELEASED.get(name),
            "ratio": {"sk": R["sk"]["ALL"], "sk_nd": R["sk_nd"]["ALL"]},
            "ci": r["ci95_vs_en"]["sk"],
            "cpt": {"sk": C["sk"], "sk_nd": C["sk_nd"], "en": C["en"]},
        })
    rows.sort(key=lambda x: x["ratio"]["sk"])
    names = {x["name"] for x in rows} | {a for x in rows for a in x["also"]}
    canon = {a: x["name"] for x in rows for a in [x["name"], *x["also"]]}
    price_rows = [{**p, "tokenizer": canon[p["tokenizer"]]} for p in prices["models"] if p["tokenizer"] in names]
    return {"tokenizers": rows, "prices": price_rows, "prices_as_of": prices["as_of"],
            "corpus": "FLORES-200 devtest (1012 sentences)"}


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    for f in ("index.html", "app.js", "style.css", "robots.txt", "sitemap.xml"):
        shutil.copy(SITE / f, OUT / f)
    for img in ("social-preview.png", "tokenizer-timeline.png"):
        shutil.copy(ROOT / "docs" / img, OUT / img)
    (OUT / "data.json").write_text(json.dumps(build_data(), ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (OUT / ".nojekyll").write_text("")
    print(f"built {OUT}")


if __name__ == "__main__":
    main()
