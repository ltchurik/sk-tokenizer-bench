# Methodology

How sk-tokenizer-bench measures the Slovak token tax, why it is measured this way, how the
numbers were checked, and what they do not tell you. The short version is in the
[README](../README.md#methodology); this document is the full one.

## 1. The question

LLM APIs bill per token, and the context window is measured in tokens too. Tokenizers are
learned mostly from English text, so the same content written in Slovak splits into more
tokens. The benchmark answers one question: **for the same content, how many tokens does
Slovak need compared with English, in each tokenizer, and what does that do to the price?**

It measures tokenizers only. Model quality in Slovak, latency and throughput are out of scope.

## 2. What is measured

For every tokenizer *T*, corpus *C* and language *L*:

- **tokens(T, C, L)**: the sum of token counts over all segments of *C* in language *L*.
- **ratio(T, C, L) = tokens(T, C, L) / tokens(T, C, en)**: a ratio of sums over the whole
  corpus, not a mean of per-sentence ratios. A mean of ratios lets short sentences dominate;
  the ratio of sums is what you pay for a real document. `tests/test_core.py` pins this choice.
- **95 % confidence interval**: percentile bootstrap over segments, with 2000 resamples and
  seed 0, so the interval is identical on every run. Each resample draws segments with
  replacement and recomputes the ratio of sums.
- **chars/token**: Unicode code points per token. A letter with a diacritic (*ľ, ô, ä*) counts
  as one character.
- **Slovak without diacritics (`sk_nd`)**: the same Slovak segments after Unicode NFD
  decomposition with combining marks removed (*ľ → l, ô → o, ä → a*), and nothing else changed.
  This separates the cost of diacritics from the cost of morphology and vocabulary.
- **Effective price** = list price per 1M tokens × ratio, i.e. what the same content costs in
  Slovak per 1M English tokens' worth. It applies to output as well: a Slovak answer is as many
  times longer in tokens as a Slovak prompt.

Counting rules:

- Local tokenizers count with `add_special_tokens=False`: no BOS/EOS and no chat template, so
  only the text itself is counted. tiktoken uses `encode_ordinary`.
- API tokenizers (Claude, Gemini) are counted with the vendors' token-counting endpoints. Each
  request wraps the text in one user message, which adds a fixed overhead. It is measured once
  per model as `count(".") − 1` and subtracted from every count.

## 3. Corpora

Three corpora, chosen to cover different failure modes:

| Corpus | Size | Why it is here |
|---|---|---|
| FLORES-200 devtest (NLLB Team, 2022) | 1012 sentences × 10 languages | Professionally translated from the same English source into every language, so the columns carry the same content. This is the standard multilingual MT benchmark and the main corpus of every table. |
| Genre corpus | 1260 segments, sk/en | FLORES is encyclopedic and translated. Real text varies: social-media posts (494), speech transcripts (111), literary prose (206) and news (149) from WMT24++ (Deutsch et al., 2025, human-translated and post-edited), plus 300 paragraphs of the GDPR, the AI Act and the Consumer Rights Directive in their official Slovak and English versions (EUR-Lex). |
| Domain corpus | 32 sk/en pairs | Written by hand, not machine-translated, covering news, tech, legal, chat, wiki, diacritics-heavy text and system prompts, i.e. what people actually send to an API. Small, so it is a sanity check, not a headline number. |

English is the baseline in every corpus. The neighbour languages (cs, pl, hu, sl, hr, ro, uk,
de) exist only in FLORES.

Integrity: third-party corpora are not stored in the repo. `skbench/corpora.py` downloads
them from their publishers, checks each download against a pinned SHA-256, converts it and checks
the converted text against a second SHA-256. Every run therefore measures exactly the text behind
the published numbers. The only exception is the EU acts: EUR-Lex may re-render its pages, so a
hash mismatch there is a warning rather than an error, and `results/env.json` records the hash of
the text that was actually measured. Conversion details (for example 53 Croatian FLORES lines with
upstream CSV quote escaping) are in [corpus/README.md](../corpus/README.md).

## 4. Tokenizers

**Selection.** The aim is every tokenizer a Slovak user is likely to pay for or run: all
current OpenAI encodings, the Llama, Mistral, Gemma, Qwen, DeepSeek, GLM, Kimi and MiniMax
families, models built for European languages (EuroLLM, Teuken, Apertus, Bielik, SlovakBERT,
CSTinyLlama) as reference points, and closed models through their counting APIs. New
tokenizers are found by a monthly watch (`tools/watch_tokenizers.py`), which scans recent
Hugging Face repos of about 25 vendors, skips fine-tunes and re-uploads whose tokenizer is
already covered, and opens an issue for anything new.

**Loading.** Each entry in [`skbench/registry.py`](../skbench/registry.py) names how to load
the tokenizer: a tiktoken encoding, a Hugging Face repo with `tokenizer.json`, a byte-level BPE
`vocab.json` + `merges.txt`, a SentencePiece model, a tiktoken file hosted on the Hub, or an API
model id. Gated originals (Meta, Google, Cohere) are replaced by ungated mirrors that ship
byte-identical tokenizer files, so anyone can reproduce the run without accepting a licence.

**Pinning.** Every Hugging Face repo is pinned to a commit in
[`skbench/revisions.json`](../skbench/revisions.json). Without that, a vendor updating its
`tokenizer.json` would change the numbers silently. `python tools/pin_revisions.py` pins new
repos; the monthly watch runs `--check` and reports any pinned tokenizer whose files changed
upstream, so a move to the new version is a deliberate, visible commit. tiktoken encodings are
downloaded by tiktoken itself, which checks them against built-in SHA-256 hashes.

**Duplicates.** Many models reuse another vendor's tokenizer. Two tokenizers whose per-segment
counts are identical in every language are marked as the same and listed once under each table.

## 5. How the numbers were checked

- **Unit tests** (`pytest`): ratio of sums instead of a mean of ratios, a deterministic
  bootstrap whose interval brackets the point estimate, duplicate detection, API counts served
  from the cache without network access, well-formed corpora (expected size and languages, no
  duplicate ids, no stray whitespace, no leaked CSV escaping), diacritic stripping, and a pin for
  every Hugging Face repo.
- **Full re-run in CI on every push and pull request.** GitHub Actions (x86_64, Ubuntu) runs the
  whole benchmark from scratch and diffs the regenerated README and `results/` against the
  committed ones. The committed results were produced on a different architecture (aarch64, see
  below), and the CI run reproduces them exactly, confidence intervals included.
- **Browser parity.** The web calculator uses tokenizers.js instead of the Python libraries.
  `site/tests/parity.py` runs every browser-loadable tokenizer over all FLORES sentences (sk,
  sk_nd, en) in Node and requires the per-sentence counts to match the Python ones exactly. CI
  runs it on every push.
- **Cross-corpus consistency.** On the genre corpus every tokenizer's overall ratio stays within
  ±0.07× of its FLORES ratio and the ranking barely moves (Spearman 0.98); the hand-written domain
  corpus lands within ±0.08×. A result that held on only one corpus would be suspect.
- **Prices** come from each vendor's official pricing page, linked per entry in
  [`prices.json`](../prices.json) with the date they were read.

## 6. Environment and hardware

Token counts are **deterministic**: the same tokenizer files, the same library versions and the
same text give the same numbers on any machine. No GPU is used, and runtime does not enter any
result. The hardware is recorded for completeness, not because it changes the results; the
x86_64 CI run in section 5 confirms that.

Every run writes `results/env.json`: date, command, Python and library versions, OS, CPU and
memory, the SHA-256 of each corpus as measured, and the pinned revision of every tokenizer. The
committed results were produced with:

| | |
|---|---|
| Machine | NVIDIA GB10 system, 20-core ARM CPU (10× Cortex-X925 + 10× Cortex-A725), 128 GB unified memory (GPU not used) |
| OS | Ubuntu 24.04.5 LTS, Linux 7.0, aarch64 |
| Python | CPython 3.12.3 |
| Libraries | tiktoken 0.14.0, tokenizers 0.23.3, sentencepiece 0.2.3, huggingface_hub 2.4.0, numpy 2.5.4 |
| Web calculator | tokenizers.js, version pinned in `site/package-lock.json` |
| Full run | about 1.5 minutes for 41 tokenizers × 3 corpora once corpora and tokenizers are downloaded (CPU, single process) |

CI cross-check: GitHub Actions `ubuntu-latest`, x86_64, CPython 3.12.

## 7. Reproducing

```bash
git clone https://github.com/ltchurik/sk-tokenizer-bench && cd sk-tokenizer-bench
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python bench.py --readme          # downloads corpora and tokenizers, rewrites results/ and README tables
git diff --stat -- README.md results/ ':!results/env.json'   # empty = reproduced
```

`results/*/counts.json.gz` holds every per-segment count, so any other statistic can be
computed without re-running the tokenizers. API rows reproduce without a key from the committed
`cache/api_counts.json` once it contains them.

## 8. Limitations

- **FLORES is translated text.** Translations into Slovak can be longer or more formal than text
  written in Slovak from scratch. The genre corpus (post-edited human translations and official
  EU language versions) and the hand-written corpus narrow this gap, but no corpus here consists
  of original Slovak text with an independent English equivalent.
- **Tokens are not the whole bill.** System prompts, tool definitions and chat templates add
  tokens that are partly language-independent, so the surcharge on a real request can be smaller
  than the ratio. Reasoning tokens are generated by the model and are not measured here at all.
- **List prices only.** Batch discounts, prompt caching, long-context tiers and regional pricing
  are ignored, and prices change; `prices.json` is dated.
- **Closed tokenizers are black boxes.** API counts depend on how the vendor counts a request
  today; the cache freezes them, but a vendor may count differently later.
- **Same tokenizer, different model.** A model can share a tokenizer with another and still
  answer more or less verbosely in Slovak. That is model behaviour, not tokenization, and is not
  measured here.

## 9. How the benchmark got here

| Version | Date | What changed in the method |
|---|---|---|
| v0.1.0 | 2026-11-09 | Hand-written sk/en corpus, first tokenizers. |
| v0.2.0 | 2026-11-14 | FLORES-200 devtest as the main corpus, neighbour languages, 30+ tokenizers, bootstrap CIs, cost table. |
| v0.2.2 | 2026-11-14 | Slovak without diacritics, tokenizer timeline. |
| v0.3.0 | 2026-11-14 | Web calculator with exact browser/Python parity checked in CI. |
| v0.3.2 | 2026-11-14 | 2026 tokenizers, automatic monthly tokenizer watch. |
| v0.3.3 | 2026-11-14 | Official prices for more vendors. |
| v0.3.4 | 2026-11-14 | Genre corpus (WMT24++, EU law); third-party corpora downloaded at run time with pinned hashes instead of stored in the repo. |
| v0.3.5 | 2026-11 | Tokenizer revisions pinned, `results/env.json`, this document. |

## References

- NLLB Team et al. *No Language Left Behind: Scaling Human-Centered Machine Translation.* arXiv:2207.04672, 2022.
- Goyal et al. *The FLORES-101 Evaluation Benchmark for Low-Resource and Multilingual Machine Translation.* TACL, 2022.
- Deutsch et al. *WMT24++: Expanding the Language Coverage of WMT24 to 55 Languages & Dialects.* 2025.
