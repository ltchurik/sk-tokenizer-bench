#!/usr/bin/env python3
"""Check that tokenizers.js (used by the web page) counts exactly like the Python benchmark.

    cd site && npm ci && cd ..
    python site/tests/parity.py

Runs every browser-loadable tokenizer over the FLORES sk, sk_nd and en columns in Node and
compares the per-sentence counts with results/flores/counts.json.gz. Exits non-zero on any
difference, so the page can never silently disagree with the published numbers.
"""
import gzip
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from huggingface_hub import hf_hub_download  # noqa: E402

from skbench.core import CORPORA, load_corpus  # noqa: E402
from skbench.registry import TOKENIZERS, browser_repo  # noqa: E402

LANGS = ("sk", "sk_nd", "en")


def main():
    rows, _ = load_corpus(CORPORA["flores"])
    py = json.loads(gzip.decompress((ROOT / "results" / "flores" / "counts.json.gz").read_bytes()))["counts"]
    tok = {}
    for name in TOKENIZERS:
        repo = browser_repo(name)
        if repo and name in py:
            tok[name] = [hf_hub_download(repo, "tokenizer.json"), hf_hub_download(repo, "tokenizer_config.json")]
    with tempfile.TemporaryDirectory() as d:
        inp, out = Path(d) / "in.json", Path(d) / "out.json"
        inp.write_text(json.dumps({"texts": {lg: [r[lg] for r in rows] for lg in LANGS}, "tok": tok}))
        subprocess.run(["node", str(ROOT / "site" / "tests" / "parity.mjs"), str(inp), str(out)],
                       cwd=ROOT / "site", check=True)
        js = json.loads(out.read_text())
    bad = 0
    for name, v in js.items():
        if "error" in v:
            print(f"ERROR {name}: {v['error']}")
            bad += 1
            continue
        diffs = {lg: sum(a != b for a, b in zip(v[lg], py[name][lg])) for lg in LANGS}
        if any(diffs.values()):
            print(f"DIFF  {name}: sentences differing per language {diffs}")
            bad += 1
        else:
            print(f"OK    {name}")
    print(f"{len(js) - bad}/{len(js)} tokenizers match the Python benchmark on {len(rows)} sentences x {len(LANGS)}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
