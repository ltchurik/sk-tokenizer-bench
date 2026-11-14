# What Slovak costs, in dollars

List prices as of 2026-11-14 (`prices.json`), token ratio from FLORES-200 devtest. "Effective" = what the same content costs when it is written in Slovak, per 1M tokens' worth of English. The ratio applies to output too: a Slovak answer is as many times longer in tokens as a Slovak prompt.

| Vendor | Model | $ in / 1M | $ out / 1M | sk/en | effective $ in | effective $ out | Slovak surcharge |
|---|---|---|---|---|---|---|---|
| Alibaba | `qwen3.8-flash` | 0.15 | 0.47 | 1.64× | 0.25 | 0.77 | +64 % |
| Mistral | `mistral-small-4-0-26-03` | 0.15 | 0.60 | 1.67× | 0.25 | 1.00 | +67 % |
| OpenAI | `gpt-4o-mini` | 0.15 | 0.60 | 1.68× | 0.25 | 1.01 | +68 % |
| DeepSeek | `deepseek-flash` | 0.15 | 0.60 | 1.91× | 0.29 | 1.14 | +90 % |
| Z.ai | `glm-5.3-flash` | 0.15 | 0.50 | 1.93× | 0.29 | 0.96 | +93 % |
| MiniMax | `MiniMax-M3.1-Flash` | 0.15 | 0.60 | 2.01× | 0.30 | 1.20 | +101 % |
| OpenAI | `gpt-5-mini` | 0.25 | 2.00 | 1.68× | 0.42 | 3.35 | +68 % |
| MiniMax | `MiniMax-M3` | 0.30 | 1.20 | 2.01× | 0.60 | 2.41 | +101 % |
| Alibaba | `qwen3.8-27b` | 0.50 | 3.00 | 1.64× | 0.82 | 4.92 | +64 % |
| Z.ai | `glm-4.7` | 0.60 | 2.20 | 1.95× | 1.17 | 4.28 | +95 % |
| Mistral | `mistral-large-4-0` | 0.70 | 2.10 | 1.74× | 1.22 | 3.65 | +74 % |
| DeepSeek | `deepseek-v4-pro` | 0.66 | 1.98 | 1.91× | 1.26 | 3.77 | +90 % |
| OpenAI | `gpt-5` | 1.25 | 10.00 | 1.68× | 2.10 | 16.77 | +68 % |
| Z.ai | `glm-5.3` | 1.40 | 4.40 | 1.93× | 2.70 | 8.49 | +93 % |
| Alibaba | `qwen3.8-max` | 2.00 | 6.00 | 1.64× | 3.28 | 9.83 | +64 % |
| OpenAI | `gpt-4.1` | 2.00 | 8.00 | 1.68× | 3.35 | 13.42 | +68 % |
| Moonshot AI | `kimi-k3.1-pro` | 2.00 | 10.00 | 2.01× | 4.02 | 20.10 | +101 % |
| OpenAI | `gpt-4o` | 2.50 | 10.00 | 1.68× | 4.19 | 16.77 | +68 % |
| Moonshot AI | `kimi-k3` | 3.00 | 15.00 | 2.01× | 6.03 | 30.15 | +101 % |

Notes:

- `qwen3.8-flash`: international (Singapore) rate
- `deepseek-flash`: DeepSeek-V4.1-Flash; off-peak price; $0.30 / $1.20 during peak hours (01–04 and 06–10 UTC on weekdays)
- `MiniMax-M3`: standard tier, up to 512k input tokens (marked as a permanent 50 % discount)
- `qwen3.8-27b`: international (Singapore) rate
- `deepseek-v4-pro`: off-peak price; $1.32 / $3.96 during peak hours (01–04 and 06–10 UTC on weekdays)
- `qwen3.8-max`: international (Singapore) rate; closed model, assumes the tokenizer shared by all open Qwen 3.8 models

*Not measured in this run (API key not set and counts not cached): Claude Haiku 5.5 (API), Claude Opus 5.5 (API), Claude Sonnet 4.6 (API), Claude Sonnet 5.5 (API), Gemini 3.8 Flash (API), Gemini 4 Argon (API).*
