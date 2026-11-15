#!/usr/bin/env python3
"""Pin every Hugging Face repo in the registry to a commit (skbench/revisions.json).

    python tools/pin_revisions.py            # add pins for repos that have none yet
    python tools/pin_revisions.py --update   # move every pin to the repo's current head
    python tools/pin_revisions.py --check    # report repos whose tokenizer files changed upstream

After --update, re-run `python bench.py --readme`: a moved pin may change the numbers.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from huggingface_hub import HfApi  # noqa: E402

from skbench.registry import REVISIONS, all_hf_repos  # noqa: E402

PATH = ROOT / "skbench" / "revisions.json"
TOKENIZER_FILES = {"tokenizer.json", "tokenizer_config.json", "tokenizer.model", "tiktoken.model",
                   "vocab.json", "merges.txt"}


def tokenizer_blobs(api, repo, rev):
    info = api.model_info(repo, revision=rev, files_metadata=True)
    return info.sha, {s.rfilename: s.blob_id for s in info.siblings if s.rfilename in TOKENIZER_FILES}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--update", action="store_true", help="move every pin to the current head")
    g.add_argument("--check", action="store_true", help="only report tokenizer files changed since the pin")
    args = ap.parse_args()

    api, pins, changed = HfApi(), dict(REVISIONS), []
    for repo in all_hf_repos():
        if repo in pins and not (args.update or args.check):
            continue
        head, head_blobs = tokenizer_blobs(api, repo, None)
        if repo in pins and head != pins[repo]:
            _, pinned_blobs = tokenizer_blobs(api, repo, pins[repo])
            if pinned_blobs != head_blobs:
                changed.append(repo)
        if not args.check:
            pins[repo] = head
        print(f"{repo}: {head[:12]}", file=sys.stderr)

    for repo in changed:
        print(f"tokenizer files changed upstream: {repo}")
    if not args.check:
        pins = {r: pins[r] for r in all_hf_repos()}  # drop repos no longer in the registry
        PATH.write_text(json.dumps(pins, indent=2) + "\n", encoding="utf-8")
    sys.exit(1 if args.check and changed else 0)


if __name__ == "__main__":
    main()
