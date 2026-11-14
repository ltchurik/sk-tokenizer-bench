# Corpora

| File | Sentences | Languages | License |
|---|---|---|---|
| `parallel.jsonl` | 32 | sk, en | MIT (written for this repo) |
| `flores200_devtest.jsonl` | 1012 | sk, cs, pl, hu, de, en | CC BY-SA 4.0 |

Each line is `{"id", "domain", <lang>: <sentence>, ...}`. The last language key read by `bench.py` is always `en`, the baseline.

## FLORES-200

`flores200_devtest.jsonl` is the `devtest` split of FLORES-200
(`https://dl.fbaipublicfiles.com/nllb/flores200_dataset.tar.gz`), columns
`slk_Latn, ces_Latn, pol_Latn, hun_Latn, deu_Latn, eng_Latn`, with `domain` taken from
`metadata_devtest.tsv` (wikinews / wikivoyage / wikibooks). Sentences are unchanged apart
from stripping surrounding whitespace.

FLORES-200 © Meta Platforms, Inc., released under
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). This derived file is
distributed under the same license.

> NLLB Team et al. *No Language Left Behind: Scaling Human-Centered Machine Translation.* arXiv:2207.04672, 2022.
> Goyal et al. *The FLORES-101 Evaluation Benchmark for Low-Resource and Multilingual Machine Translation.* TACL, 2022.
