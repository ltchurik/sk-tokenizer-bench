# What Slovak costs, in dollars

List prices as of 2026-11-14 (`prices.json`), token ratio from FLORES-200 devtest. "Effective" = what the same content costs when it is written in Slovak, per 1M tokens' worth of English. The ratio applies to output too: a Slovak answer is as many times longer in tokens as a Slovak prompt.

| Vendor | Model | $ in / 1M | $ out / 1M | sk/en | effective $ in | effective $ out | Slovak surcharge |
|---|---|---|---|---|---|---|---|
| OpenAI | `gpt-4o-mini` | 0.15 | 0.60 | 1.68× | 0.25 | 1.01 | +68 % |
| OpenAI | `gpt-5-mini` | 0.25 | 2.00 | 1.68× | 0.42 | 3.35 | +68 % |
| OpenAI | `gpt-5` | 1.25 | 10.00 | 1.68× | 2.10 | 16.77 | +68 % |
| OpenAI | `gpt-4.1` | 2.00 | 8.00 | 1.68× | 3.35 | 13.42 | +68 % |
| OpenAI | `gpt-4o` | 2.50 | 10.00 | 1.68× | 4.19 | 16.77 | +68 % |

*Not measured in this run (API key not set and counts not cached): Claude Haiku 5.5 (API), Claude Opus 5.5 (API), Claude Sonnet 4.6 (API), Claude Sonnet 5.5 (API), Gemini 3.8 Flash (API), Gemini 4 Argon (API).*
