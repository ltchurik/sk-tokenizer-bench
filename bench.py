#!/usr/bin/env python3
"""sk-tokenizer-bench — how many tokens does Slovak cost vs English across LLM tokenizers."""
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent
CORPUS = ROOT / "corpus" / "parallel.jsonl"

# name -> (kind, id). kind: "tiktoken" | "hf"
TOKENIZERS = {
    "GPT-4o / 4.1 / 5 (o200k_base)": ("tiktoken", "o200k_base"),
    "GPT-4 / 3.5 (cl100k_base)": ("tiktoken", "cl100k_base"),
    "Llama 3.x": ("hf", "unsloth/Llama-3.1-8B"),
    "Llama 2": ("hf", "NousResearch/Llama-2-7b-hf"),
    "Mistral / Mixtral (v3)": ("hf", "mistralai/Mistral-7B-Instruct-v0.3"),
    "Mistral Nemo / Large 2 (tekken)": ("hf", "mistralai/Mistral-Nemo-Instruct-2407"),
    "Qwen 2.5 / 3": ("hf", "Qwen/Qwen2.5-7B"),
    "Gemma 2 / 3": ("hf", "unsloth/gemma-3-4b-it"),
    "DeepSeek V3 / R1": ("hf", "deepseek-ai/DeepSeek-V3"),
    "Phi-4": ("hf", "microsoft/phi-4"),
    "gpt-oss (o200k_harmony)": ("hf", "openai/gpt-oss-20b"),
    "Claude 2 (legacy, Xenova mirror)": ("hf", "Xenova/claude-tokenizer"),
    "Command R": ("hf", "Xenova/c4ai-command-r-v01-tokenizer"),
    "EuroLLM": ("hf", "utter-project/EuroLLM-1.7B"),
    "mT5": ("hf", "Xenova/mt5-base"),
    "SmolLM3": ("hf", "HuggingFaceTB/SmolLM3-3B"),
    "OLMo 2": ("hf", "allenai/OLMo-2-1124-7B"),
    "BLOOM": ("hf", "bigscience/bloom"),
    "CSTinyLlama (Czech, BUT-FIT)": ("hf", "BUT-FIT/CSTinyLlama-1.2B"),
}


def load(kind, ident):
    if kind == "tiktoken":
        import tiktoken
        enc = tiktoken.get_encoding(ident)
        return lambda s: len(enc.encode(s))
    from tokenizers import Tokenizer
    tok = Tokenizer.from_pretrained(ident)
    return lambda s: len(tok.encode(s, add_special_tokens=False).ids)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default=str(CORPUS))
    ap.add_argument("--langs", default="sk,en", help="comma-separated keys present in corpus")
    ap.add_argument("--out", default=str(ROOT / "results"))
    ap.add_argument("--only", help="substring filter on tokenizer name")
    args = ap.parse_args()

    langs = args.langs.split(",")
    base = langs[-1]  # last = baseline (en)
    rows = [json.loads(l) for l in open(args.corpus, encoding="utf-8") if l.strip()]
    domains = sorted({r["domain"] for r in rows})

    results = {}
    for name, (kind, ident) in TOKENIZERS.items():
        if args.only and args.only.lower() not in name.lower():
            continue
        try:
            count = load(kind, ident)
        except Exception as e:  # gated / offline / renamed
            print(f"SKIP {name}: {type(e).__name__}: {str(e)[:80]}", file=sys.stderr)
            continue
        tot = defaultdict(lambda: defaultdict(int))  # lang -> domain -> tokens
        chars = defaultdict(lambda: defaultdict(int))
        for r in rows:
            for lg in langs:
                n = count(r[lg])
                tot[lg][r["domain"]] += n
                tot[lg]["ALL"] += n
                chars[lg][r["domain"]] += len(r[lg])
                chars[lg]["ALL"] += len(r[lg])
        results[name] = {
            "id": ident,
            "tokens": {lg: dict(tot[lg]) for lg in langs},
            "chars_per_token": {lg: round(chars[lg]["ALL"] / tot[lg]["ALL"], 2) for lg in langs},
            "ratio_vs_" + base: {
                lg: {d: round(tot[lg][d] / tot[base][d], 2) for d in domains + ["ALL"]} for lg in langs
            },
        }
        print(f"OK   {name}: " + ", ".join(f"{lg}={tot[lg]['ALL']}" for lg in langs), file=sys.stderr)

    out = Path(args.out)
    out.mkdir(exist_ok=True)
    (out / "results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    # Markdown table
    other = [lg for lg in langs if lg != base]
    md = [f"# Results\n", f"Corpus: {len(rows)} parallel sentences, baseline = `{base}`.\n"]
    md.append("## Overall\n")
    hdr = ["Tokenizer"] + [f"{lg} tokens" for lg in langs] + [f"{lg}/{base}" for lg in other] + [f"chars/token ({lg})" for lg in langs]
    md.append("| " + " | ".join(hdr) + " |")
    md.append("|" + "---|" * len(hdr))
    for name, r in sorted(results.items(), key=lambda kv: kv[1]["ratio_vs_" + base][other[0]]["ALL"]):
        cells = [name] + [str(r["tokens"][lg]["ALL"]) for lg in langs]
        cells += [f'{r["ratio_vs_" + base][lg]["ALL"]:.2f}×' for lg in other]
        cells += [str(r["chars_per_token"][lg]) for lg in langs]
        md.append("| " + " | ".join(cells) + " |")
    for lg in other:
        md.append(f"\n## {lg}/{base} ratio by domain\n")
        hdr = ["Tokenizer"] + domains
        md.append("| " + " | ".join(hdr) + " |")
        md.append("|" + "---|" * len(hdr))
        for name, r in sorted(results.items(), key=lambda kv: kv[1]["ratio_vs_" + base][lg]["ALL"]):
            md.append("| " + " | ".join([name] + [f'{r["ratio_vs_" + base][lg][d]:.2f}×' for d in domains]) + " |")
    (out / "RESULTS.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
