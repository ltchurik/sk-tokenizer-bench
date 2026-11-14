#!/usr/bin/env python3
"""Find tokenizers released on the Hugging Face Hub that the benchmark does not cover yet.

    python tools/watch_tokenizers.py                 # report only (last 40 days)
    python tools/watch_tokenizers.py --days 120      # look further back
    python tools/watch_tokenizers.py --open-issues   # open one GitHub issue per new tokenizer (needs gh + GH_TOKEN)

For every recent repo of the watched organisations that ships a tokenizer.json, the tokenizer
is run on a probe of the first 200 FLORES-200 sentences (Slovak + English) and compared with the
per-sentence counts of every tokenizer already in results/flores/counts.json.gz. Identical
counts mean "already covered" (a fine-tune, quantisation or re-upload); anything else is a new
tokenizer, measured on the full FLORES devtest and reported with a ready-to-paste registry line.
Issues carry the probe signature, so the same tokenizer is never reported twice.
"""
import argparse
import gzip
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from skbench.core import CORPORA, load_corpus  # noqa: E402
from skbench.registry import TOKENIZERS  # noqa: E402

ORGS = [
    "openai", "meta-llama", "mistralai", "google", "Qwen", "deepseek-ai", "zai-org", "moonshotai",
    "MiniMaxAI", "microsoft", "CohereLabs", "nvidia", "ibm-granite", "tiiuae", "allenai",
    "HuggingFaceTB", "swiss-ai", "utter-project", "openGPT-X", "BUT-FIT", "speakleash", "gerulata",
    "xai-org", "LiquidAI", "ai21labs", "tencent", "baidu",
]
SKIP = re.compile(r"(gguf|awq|gptq|fp8|nvfp4|mxfp4|int4|int8|bnb|mlx|onnx|exl2|quant|-4bit|-8bit|eagle|draft)", re.I)
# Repos whose name says they are not a text LLM: used to pick a better representative name.
NON_LLM = re.compile(r"(image|speech|asr|tts|ctc|voice|embed|rerank|ocr|parsing|vision|-vl|omni|drive|cosmos)", re.I)
MIN_VOCAB = 30_000  # character/CTC vocabularies of speech models are not LLM tokenizers
PROBE = 200
LABEL = "new-tokenizer"


def api(url):
    req = urllib.request.Request(url, headers={"User-Agent": "sk-tokenizer-bench-watch"})
    tok = os.environ.get("HF_TOKEN")
    if tok:
        req.add_header("Authorization", f"Bearer {tok}")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def candidates(days):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    covered = {ident for kind, ident in TOKENIZERS.values()}
    for org in ORGS:
        try:
            models = api(f"https://huggingface.co/api/models?author={org}&sort=createdAt&direction=-1&limit=60&full=true")
        except Exception as e:
            print(f"warn: {org}: {type(e).__name__}", file=sys.stderr)
            continue
        for m in models:
            created = datetime.fromisoformat(m["createdAt"].replace("Z", "+00:00"))
            if created < since:
                break
            files = {s["rfilename"] for s in m.get("siblings", [])}
            if "tokenizer.json" not in files or SKIP.search(m["id"]) or m["id"] in covered:
                continue
            yield {"repo": m["id"], "created": created.date().isoformat(), "gated": bool(m.get("gated"))}


def tokenizer_blob(repo):
    """Git blob id of the repo's tokenizer.json: identical files need no download."""
    try:
        sib = api(f"https://huggingface.co/api/models/{repo}?blobs=true")["siblings"]
        return next((x.get("blobId") for x in sib if x["rfilename"] == "tokenizer.json"), None)
    except Exception:
        return None


def signature(counts):
    return hashlib.sha1(json.dumps(counts, separators=(",", ":")).encode()).hexdigest()[:16]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--days", type=int, default=40)
    ap.add_argument("--open-issues", action="store_true")
    args = ap.parse_args()

    from tokenizers import Tokenizer

    rows, _ = load_corpus(CORPORA["flores"])
    probe = {lg: [r[lg] for r in rows[:PROBE]] for lg in ("sk", "en")}
    known_counts = json.loads(gzip.decompress((ROOT / "results" / "flores" / "counts.json.gz").read_bytes()))["counts"]
    known = {}
    for name, c in known_counts.items():  # first (canonical) name wins for shared tokenizers
        known.setdefault(signature({lg: c[lg][:PROBE] for lg in ("sk", "en")}), name)

    from skbench.registry import browser_repo

    known_blobs = {}
    for name in known_counts:
        repo = browser_repo(name) if name in TOKENIZERS else None
        if repo:
            known_blobs.setdefault(tokenizer_blob(repo), name)
    known_blobs.pop(None, None)

    new, same, gated, failed, seen, seen_blobs = [], [], [], [], {}, {}
    for c in candidates(args.days):
        if c["gated"]:
            gated.append(c)
            continue
        blob = tokenizer_blob(c["repo"])
        if blob in known_blobs:
            same.append({**c, "same_as": known_blobs[blob]})
            continue
        if blob in seen_blobs:  # identical tokenizer.json already checked in this run
            prev = seen_blobs[blob]
            if "sig" in prev:
                prev["also"].append(c["repo"])
            else:
                same.append({**c, "same_as": prev["same_as"]})
            continue
        try:
            tok = Tokenizer.from_pretrained(c["repo"])
        except Exception as e:
            failed.append({**c, "error": f"{type(e).__name__}: {str(e)[:80]}"})
            continue
        if tok.get_vocab_size() < MIN_VOCAB:
            failed.append({**c, "error": f"vocabulary {tok.get_vocab_size():,} < {MIN_VOCAB:,}, not an LLM tokenizer"})
            continue
        n = lambda s: len(tok.encode(s, add_special_tokens=False).ids)  # noqa: E731
        sig = signature({lg: [n(s) for s in texts] for lg, texts in probe.items()})
        if sig in known:
            item = {**c, "same_as": known[sig]}
            same.append(item)
        elif sig in seen:
            item = seen[sig]
            item["also"].append(c["repo"])
        else:
            sk, en = sum(n(r["sk"]) for r in rows), sum(n(r["en"]) for r in rows)
            item = {**c, "sig": sig, "ratio": round(sk / en, 3), "vocab": tok.get_vocab_size(), "also": []}
            seen[sig] = item
            new.append(item)
        if blob:
            seen_blobs[blob] = item
        print(f"checked {c['repo']}", file=sys.stderr)

    for x in new:  # name the tokenizer after its most LLM-looking repo
        repos = sorted([x["repo"], *x["also"]], key=lambda r: (bool(NON_LLM.search(r)), len(r)))
        x["repo"], x["also"] = repos[0], repos[1:]
    lines = [f"## Tokenizer watch ({args.days} days)\n"]
    lines += [f"- **NEW** `{x['repo']}` ({x['created']}): sk/en {x['ratio']:.2f}×, vocab {x['vocab']:,}"
              + (f"; same tokenizer in {', '.join(x['also'])}" if x["also"] else "") for x in new] or ["- no new tokenizers"]
    if same:
        lines.append("\nAlready covered:\n")
        lines += [f"- `{x['repo']}` = {x['same_as']}" for x in same]
    if gated:
        lines.append("\nGated (needs an ungated mirror or HF_TOKEN):\n")
        lines += [f"- `{x['repo']}` ({x['created']})" for x in gated]
    if failed:
        lines.append("\nSkipped:\n")
        lines += [f"- `{x['repo']}`: {x['error']}" for x in failed]
    report = "\n".join(lines) + "\n"
    print(report)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        Path(os.environ["GITHUB_STEP_SUMMARY"]).write_text(report, encoding="utf-8")

    if args.open_issues:
        open_issues(new)


def open_issues(new):
    subprocess.run(["gh", "label", "create", LABEL, "--color", "2a78d6", "--description",
                    "Tokenizer found by the monthly watch", "--force"], check=True, capture_output=True)
    for x in new:
        existing = subprocess.run(["gh", "issue", "list", "--label", LABEL, "--state", "all", "--search", x["sig"],
                                   "--json", "number"], check=True, capture_output=True, text=True).stdout
        if json.loads(existing):
            print(f"issue exists for {x['repo']}", file=sys.stderr)
            continue
        name = x["repo"].split("/")[1]
        body = f"""The monthly tokenizer watch found a tokenizer that is not in the benchmark yet.

| | |
|---|---|
| Repo | [`{x['repo']}`](https://huggingface.co/{x['repo']}) |
| Created | {x['created']} |
| Vocabulary | {x['vocab']:,} |
| sk/en on FLORES-200 devtest | **{x['ratio']:.2f}×** |
| Same tokenizer also in | {', '.join(f'`{a}`' for a in x['also']) or '–'} |

To add it, put this line into `TOKENIZERS` in `skbench/registry.py` (and a release month into `RELEASED`), then run `python bench.py --readme`:

```python
    "{name}": ("hf", "{x['repo']}"),
```

<sub>probe signature: {x['sig']}</sub>
"""
        subprocess.run(["gh", "issue", "create", "--title", f"New tokenizer: {x['repo']} (sk/en {x['ratio']:.2f}×)",
                        "--label", LABEL, "--body", body], check=True)


if __name__ == "__main__":
    main()
