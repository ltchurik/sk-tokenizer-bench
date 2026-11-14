#!/usr/bin/env python3
"""sk-tokenizer-bench — how many tokens does Slovak cost vs English across LLM tokenizers.

    python bench.py                      # all tokenizers, both corpora
    python bench.py --only gemma         # substring filter on tokenizer name
    python bench.py --corpus custom      # only the hand-written domain corpus
    python bench.py --no-api             # skip Claude / Gemini (API) rows entirely
    python bench.py --readme             # also regenerate the README results block
"""
import argparse
import gzip
import json
import sys

from skbench import backends, core, report
from skbench.registry import API_KINDS, TOKENIZERS

CORPUS_TITLES = {"flores": "FLORES-200 devtest", "custom": "hand-written domain corpus"}


def run_corpus(name, path, selected, n_boot, api_cache):
    rows, langs = core.load_corpus(path)
    results, counts = {}, {}
    for tname, (kind, ident) in selected.items():
        try:
            counter = backends.load(kind, ident, api_cache=api_cache)
            summary, per_sentence = core.measure(counter, rows, langs, n_boot)
        except Exception as e:  # gated / offline / renamed / no key
            print(f"SKIP {tname}: {type(e).__name__}: {str(e)[:100]}", file=sys.stderr)
            continue
        results[tname] = {"kind": kind, "id": ident, **summary}
        counts[tname] = per_sentence
        print(f"OK   [{name}] {tname}: " + ", ".join(f"{lg}={summary['tokens'][lg]['ALL']}" for lg in langs),
              file=sys.stderr)
    core.mark_identical(results, counts)
    return rows, langs, results, counts


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--corpus", default="flores,custom", help="comma-separated: flores, custom (default both)")
    ap.add_argument("--only", help="substring filter on tokenizer name")
    ap.add_argument("--no-api", action="store_true", help="skip API-counted tokenizers (Claude, Gemini)")
    ap.add_argument("--bootstrap", type=int, default=2000, help="bootstrap resamples for the CI (0 = off)")
    ap.add_argument("--out", help="results directory (default results/; a filtered --only run writes nothing unless --out is given)")
    ap.add_argument("--readme", action="store_true", help="rewrite the generated block in README.md")
    args = ap.parse_args()

    selected = {
        n: spec for n, spec in TOKENIZERS.items()
        if (not args.only or args.only.lower() in n.lower()) and not (args.no_api and spec[0] in API_KINDS)
    }
    api_cache = backends.ApiCache.load()
    prices = json.loads((core.ROOT / "prices.json").read_text(encoding="utf-8"))
    out = core.Path(args.out) if args.out else (None if args.only else core.ROOT / "results")
    all_results = {}

    for cname in args.corpus.split(","):
        rows, langs, results, counts = run_corpus(cname, core.CORPORA[cname], selected, args.bootstrap, api_cache)
        if not results:
            continue
        all_results[cname] = results
        md = report.corpus_markdown(CORPUS_TITLES[cname], results, len(rows), langs)
        print(md)
        if out is None:
            continue
        d = out / cname
        d.mkdir(parents=True, exist_ok=True)
        (d / "results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        payload = json.dumps({"ids": [r["id"] for r in rows], "counts": counts}).encode("utf-8")
        (d / "counts.json.gz").write_bytes(gzip.compress(payload, mtime=0))  # mtime=0: reproducible bytes
        (d / "RESULTS.md").write_text(md, encoding="utf-8")

    if "flores" in all_results:
        cost = report.cost_markdown(prices, all_results["flores"], "FLORES-200 devtest")
        print(cost)
        if out is not None:
            (out / "COST.md").write_text(cost, encoding="utf-8")

    if args.readme:
        if not {"flores", "custom"} <= all_results.keys() or args.only:
            sys.exit("--readme needs a full run over both corpora (no --only)")
        report.update_readme(core.ROOT / "README.md",
                             report.readme_block(all_results["flores"], all_results["custom"], prices))
        print("README.md updated", file=sys.stderr)


if __name__ == "__main__":
    main()
