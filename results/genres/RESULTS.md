# Results — genre corpus (WMT24++ and EUR-Lex)

1260 parallel sentences, baseline = `en`. `sk_nd` = the Slovak column with diacritics stripped. 95 % CI = percentile bootstrap over sentences (2000 resamples).

## Tokens relative to en

| Tokenizer | sk/en | 95 % CI | sk_nd/en |
|---|---|---|---|
| SlovakBERT (Slovak, Gerulata) | 0.77× | 0.76–0.78 | 0.88× |
| CSTinyLlama (Czech, BUT-FIT) | 0.92× | 0.91–0.93 | 0.94× |
| CSMPT (Czech, BUT-FIT) | 0.92× | 0.91–0.93 | 0.94× |
| mT5 | 1.29× | 1.28–1.30 | 1.23× |
| EuroLLM | 1.34× | 1.33–1.35 | 1.37× |
| Teuken (OpenGPT-X) | 1.40× | 1.39–1.42 | 1.32× |
| Gemini 4 Argon (API) | 1.53× | 1.51–1.55 | 1.51× |
| Llama 4 | 1.54× | 1.53–1.56 | 1.54× |
| Gemma 1 / 2 | 1.55× | 1.53–1.56 | 1.51× |
| Gemma 3 | 1.57× | 1.55–1.59 | 1.52× |
| Gemini 3.8 Flash (API) | 1.57× | 1.55–1.59 | 1.52× |
| Claude Opus / Sonnet / Haiku 5.5 (API) | 1.60× | 1.58–1.61 | 1.59× |
| Qwen 3.8 | 1.61× | 1.60–1.63 | 1.57× |
| Command R | 1.66× | 1.64–1.67 | 1.54× |
| Cohere North | 1.66× | 1.64–1.68 | 1.58× |
| GPT-4o / 4.1 / 5 (o200k_base) | 1.66× | 1.64–1.68 | 1.58× |
| gpt-oss (o200k_harmony) | 1.66× | 1.64–1.68 | 1.58× |
| Phi-4-mini | 1.66× | 1.64–1.68 | 1.58× |
| Mistral Nemo / Small 3–4 / Large 2 (tekken) | 1.66× | 1.65–1.68 | 1.58× |
| Nemotron Nano 2 | 1.66× | 1.65–1.68 | 1.58× |
| Apertus (Swiss AI) | 1.66× | 1.65–1.68 | 1.58× |
| ERNIE 5.5 | 1.71× | 1.69–1.73 | 1.60× |
| Mistral Large 4 | 1.73× | 1.71–1.74 | 1.61× |
| Claude Sonnet 4.6 (API) | 1.78× | 1.76–1.80 | 1.64× |
| Llama 2 | 1.80× | 1.78–1.82 | 1.63× |
| Llama 3.x | 1.80× | 1.78–1.82 | 1.68× |
| SmolLM3 | 1.80× | 1.78–1.82 | 1.68× |
| LFM3 (Liquid AI) | 1.82× | 1.80–1.84 | 1.67× |
| DeepSeek V3 / R1 / V4 | 1.88× | 1.86–1.90 | 1.71× |
| GLM-5.3 | 1.90× | 1.88–1.93 | 1.72× |
| Granite 3.3 | 1.91× | 1.88–1.93 | 1.69× |
| Hunyuan 4 (Tencent) | 1.92× | 1.90–1.94 | 1.73× |
| GLM-4.5 / 4.6 / 4.7 | 1.92× | 1.90–1.95 | 1.72× |
| Mistral / Mixtral (v3) | 1.94× | 1.92–1.97 | 1.75× |
| Bielik (Polish, SpeakLeash) | 1.94× | 1.92–1.97 | 1.75× |
| BLOOM | 2.00× | 1.98–2.03 | 1.76× |
| MiniMax M2 / M3 | 2.01× | 1.98–2.03 | 1.76× |
| Kimi K2 / K3 | 2.01× | 1.99–2.04 | 1.80× |
| Qwen 2.5 / 3 | 2.06× | 2.03–2.08 | 1.78× |
| Granite 4.2 | 2.10× | 2.07–2.12 | 1.78× |
| GPT-4 / 3.5 (cl100k_base) | 2.11× | 2.09–2.14 | 1.80× |
| Phi-4 | 2.11× | 2.09–2.14 | 1.80× |
| OLMo 2 | 2.11× | 2.09–2.14 | 1.80× |
| Falcon 3 | 2.22× | 2.18–2.25 | 1.81× |
| Claude 2 (legacy, Xenova mirror) | 2.23× | 2.20–2.26 | 1.87× |

*Byte-for-byte identical counts on this corpus: GPT-4o / 4.1 / 5 (o200k_base) = gpt-oss (o200k_harmony) = Phi-4-mini; GPT-4 / 3.5 (cl100k_base) = Phi-4 = OLMo 2; Mistral Nemo / Small 3–4 / Large 2 (tekken) = Nemotron Nano 2 = Apertus (Swiss AI); Llama 3.x = SmolLM3; CSTinyLlama (Czech, BUT-FIT) = CSMPT (Czech, BUT-FIT); Mistral / Mixtral (v3) = Bielik (Polish, SpeakLeash).*


## Total tokens

| Tokenizer | sk | sk_nd | en |
|---|---|---|---|
| SlovakBERT (Slovak, Gerulata) | 65140 | 74507 | 84605 |
| CSTinyLlama (Czech, BUT-FIT) | 89712 | 91633 | 97353 |
| CSMPT (Czech, BUT-FIT) | 89712 | 91633 | 97353 |
| mT5 | 97855 | 93324 | 75844 |
| EuroLLM | 88720 | 90861 | 66209 |
| Teuken (OpenGPT-X) | 92898 | 87909 | 66364 |
| Gemini 4 Argon (API) | 95758 | 94143 | 62513 |
| Llama 4 | 93882 | 93619 | 60808 |
| Gemma 1 / 2 | 95822 | 93532 | 61912 |
| Gemma 3 | 97451 | 94159 | 62085 |
| Gemini 3.8 Flash (API) | 97456 | 94167 | 62087 |
| Claude Opus / Sonnet / Haiku 5.5 (API) | 147294 | 146192 | 92150 |
| Qwen 3.8 | 99944 | 97300 | 61898 |
| Command R | 102376 | 95475 | 61778 |
| Cohere North | 98542 | 93747 | 59416 |
| GPT-4o / 4.1 / 5 (o200k_base) | 100151 | 95514 | 60334 |
| gpt-oss (o200k_harmony) | 100151 | 95514 | 60334 |
| Phi-4-mini | 100151 | 95514 | 60334 |
| Mistral Nemo / Small 3–4 / Large 2 (tekken) | 104745 | 99577 | 62935 |
| Nemotron Nano 2 | 104745 | 99577 | 62935 |
| Apertus (Swiss AI) | 104745 | 99577 | 62935 |
| ERNIE 5.5 | 104838 | 98200 | 61182 |
| Mistral Large 4 | 107689 | 100655 | 62402 |
| Claude Sonnet 4.6 (API) | 116432 | 107323 | 65360 |
| Llama 2 | 126039 | 114354 | 70087 |
| Llama 3.x | 110329 | 102813 | 61171 |
| SmolLM3 | 110329 | 102813 | 61171 |
| LFM3 (Liquid AI) | 113897 | 104648 | 62533 |
| DeepSeek V3 / R1 / V4 | 115450 | 105234 | 61412 |
| GLM-5.3 | 116468 | 105557 | 61219 |
| Granite 3.3 | 134192 | 119174 | 70410 |
| Hunyuan 4 (Tencent) | 118816 | 106919 | 61865 |
| GLM-4.5 / 4.6 / 4.7 | 117767 | 105557 | 61219 |
| Mistral / Mixtral (v3) | 130500 | 117256 | 67150 |
| Bielik (Polish, SpeakLeash) | 130500 | 117256 | 67150 |
| BLOOM | 123280 | 108303 | 61604 |
| MiniMax M2 / M3 | 120217 | 105524 | 59848 |
| Kimi K2 / K3 | 122232 | 109577 | 60780 |
| Qwen 2.5 / 3 | 127475 | 110630 | 61968 |
| Granite 4.2 | 129444 | 110182 | 61754 |
| GPT-4 / 3.5 (cl100k_base) | 129343 | 110084 | 61183 |
| Phi-4 | 129343 | 110084 | 61183 |
| OLMo 2 | 129343 | 110084 | 61183 |
| Falcon 3 | 138197 | 113022 | 62369 |
| Claude 2 (legacy, Xenova mirror) | 138486 | 116396 | 62149 |

## Characters per token

| Tokenizer | sk | sk_nd | en |
|---|---|---|---|
| SlovakBERT (Slovak, Gerulata) | 4.51 | 3.94 | 3.47 |
| CSTinyLlama (Czech, BUT-FIT) | 3.27 | 3.20 | 3.02 |
| CSMPT (Czech, BUT-FIT) | 3.27 | 3.20 | 3.02 |
| mT5 | 3.00 | 3.15 | 3.87 |
| EuroLLM | 3.31 | 3.23 | 4.44 |
| Teuken (OpenGPT-X) | 3.16 | 3.34 | 4.43 |
| Gemini 4 Argon (API) | 3.06 | 3.12 | 4.70 |
| Llama 4 | 3.13 | 3.13 | 4.83 |
| Gemma 1 / 2 | 3.06 | 3.14 | 4.75 |
| Gemma 3 | 3.01 | 3.12 | 4.73 |
| Gemini 3.8 Flash (API) | 3.01 | 3.12 | 4.73 |
| Claude Opus / Sonnet / Haiku 5.5 (API) | 1.99 | 2.01 | 3.19 |
| Qwen 3.8 | 2.94 | 3.02 | 4.75 |
| Command R | 2.87 | 3.07 | 4.76 |
| Cohere North | 2.98 | 3.13 | 4.95 |
| GPT-4o / 4.1 / 5 (o200k_base) | 2.93 | 3.07 | 4.87 |
| gpt-oss (o200k_harmony) | 2.93 | 3.07 | 4.87 |
| Phi-4-mini | 2.93 | 3.07 | 4.87 |
| Mistral Nemo / Small 3–4 / Large 2 (tekken) | 2.80 | 2.95 | 4.67 |
| Nemotron Nano 2 | 2.80 | 2.95 | 4.67 |
| Apertus (Swiss AI) | 2.80 | 2.95 | 4.67 |
| ERNIE 5.5 | 2.80 | 2.99 | 4.80 |
| Mistral Large 4 | 2.73 | 2.92 | 4.71 |
| Claude Sonnet 4.6 (API) | 2.52 | 2.73 | 4.50 |
| Llama 2 | 2.33 | 2.57 | 4.19 |
| Llama 3.x | 2.66 | 2.85 | 4.80 |
| SmolLM3 | 2.66 | 2.85 | 4.80 |
| LFM3 (Liquid AI) | 2.58 | 2.81 | 4.70 |
| DeepSeek V3 / R1 / V4 | 2.54 | 2.79 | 4.78 |
| GLM-5.3 | 2.52 | 2.78 | 4.80 |
| Granite 3.3 | 2.19 | 2.46 | 4.17 |
| Hunyuan 4 (Tencent) | 2.47 | 2.75 | 4.75 |
| GLM-4.5 / 4.6 / 4.7 | 2.49 | 2.78 | 4.80 |
| Mistral / Mixtral (v3) | 2.25 | 2.50 | 4.38 |
| Bielik (Polish, SpeakLeash) | 2.25 | 2.50 | 4.38 |
| BLOOM | 2.38 | 2.71 | 4.77 |
| MiniMax M2 / M3 | 2.44 | 2.78 | 4.91 |
| Kimi K2 / K3 | 2.40 | 2.68 | 4.83 |
| Qwen 2.5 / 3 | 2.30 | 2.65 | 4.74 |
| Granite 4.2 | 2.27 | 2.66 | 4.76 |
| GPT-4 / 3.5 (cl100k_base) | 2.27 | 2.67 | 4.80 |
| Phi-4 | 2.27 | 2.67 | 4.80 |
| OLMo 2 | 2.27 | 2.67 | 4.80 |
| Falcon 3 | 2.12 | 2.60 | 4.71 |
| Claude 2 (legacy, Xenova mirror) | 2.12 | 2.52 | 4.73 |

## sk/en ratio by domain

| Tokenizer | law | literary | news | social | speech |
|---|---|---|---|---|---|
| SlovakBERT (Slovak, Gerulata) | 0.65× | 0.85× | 0.81× | 0.88× | 0.79× |
| CSTinyLlama (Czech, BUT-FIT) | 0.90× | 0.89× | 0.99× | 0.97× | 0.87× |
| CSMPT (Czech, BUT-FIT) | 0.90× | 0.89× | 0.99× | 0.97× | 0.87× |
| mT5 | 1.33× | 1.20× | 1.39× | 1.30× | 1.19× |
| EuroLLM | 1.39× | 1.28× | 1.45× | 1.33× | 1.21× |
| Teuken (OpenGPT-X) | 1.50× | 1.28× | 1.51× | 1.37× | 1.25× |
| Gemini 4 Argon (API) | 1.62× | 1.41× | 1.73× | 1.50× | 1.33× |
| Llama 4 | 1.57× | 1.45× | 1.70× | 1.55× | 1.43× |
| Gemma 1 / 2 | 1.64× | 1.45× | 1.72× | 1.50× | 1.36× |
| Gemma 3 | 1.65× | 1.47× | 1.74× | 1.53× | 1.39× |
| Gemini 3.8 Flash (API) | 1.65× | 1.47× | 1.74× | 1.53× | 1.39× |
| Claude Opus / Sonnet / Haiku 5.5 (API) | 1.64× | 1.47× | 1.70× | 1.61× | 1.51× |
| Qwen 3.8 | 1.69× | 1.51× | 1.78× | 1.58× | 1.44× |
| Command R | 1.75× | 1.52× | 1.81× | 1.63× | 1.50× |
| Cohere North | 1.73× | 1.53× | 1.82× | 1.64× | 1.50× |
| GPT-4o / 4.1 / 5 (o200k_base) | 1.74× | 1.52× | 1.83× | 1.63× | 1.50× |
| gpt-oss (o200k_harmony) | 1.74× | 1.52× | 1.83× | 1.63× | 1.50× |
| Phi-4-mini | 1.74× | 1.52× | 1.83× | 1.63× | 1.50× |
| Mistral Nemo / Small 3–4 / Large 2 (tekken) | 1.76× | 1.53× | 1.80× | 1.62× | 1.50× |
| Nemotron Nano 2 | 1.76× | 1.53× | 1.80× | 1.62× | 1.50× |
| Apertus (Swiss AI) | 1.76× | 1.53× | 1.80× | 1.62× | 1.50× |
| ERNIE 5.5 | 1.83× | 1.55× | 1.90× | 1.66× | 1.53× |
| Mistral Large 4 | 1.85× | 1.56× | 1.90× | 1.68× | 1.54× |
| Claude Sonnet 4.6 (API) | 1.89× | 1.60× | 1.95× | 1.74× | 1.64× |
| Llama 2 | 1.95× | 1.61× | 1.93× | 1.74× | 1.62× |
| Llama 3.x | 1.94× | 1.63× | 1.99× | 1.74× | 1.60× |
| SmolLM3 | 1.94× | 1.63× | 1.99× | 1.74× | 1.60× |
| LFM3 (Liquid AI) | 1.99× | 1.61× | 2.01× | 1.74× | 1.61× |
| DeepSeek V3 / R1 / V4 | 2.05× | 1.67× | 2.08× | 1.80× | 1.66× |
| GLM-5.3 | 2.07× | 1.70× | 2.12× | 1.81× | 1.68× |
| Granite 3.3 | 2.10× | 1.68× | 2.01× | 1.85× | 1.70× |
| Hunyuan 4 (Tencent) | 2.11× | 1.68× | 2.13× | 1.83× | 1.71× |
| GLM-4.5 / 4.6 / 4.7 | 2.10× | 1.72× | 2.13× | 1.82× | 1.69× |
| Mistral / Mixtral (v3) | 2.12× | 1.73× | 2.12× | 1.86× | 1.72× |
| Bielik (Polish, SpeakLeash) | 2.12× | 1.73× | 2.12× | 1.86× | 1.72× |
| BLOOM | 2.20× | 1.73× | 2.22× | 1.91× | 1.79× |
| MiniMax M2 / M3 | 2.18× | 1.77× | 2.22× | 1.92× | 1.79× |
| Kimi K2 / K3 | 2.19× | 1.76× | 2.21× | 1.93× | 1.80× |
| Qwen 2.5 / 3 | 2.25× | 1.81× | 2.29× | 1.94× | 1.81× |
| Granite 4.2 | 2.31× | 1.83× | 2.34× | 1.97× | 1.84× |
| GPT-4 / 3.5 (cl100k_base) | 2.33× | 1.86× | 2.36× | 1.99× | 1.85× |
| Phi-4 | 2.33× | 1.86× | 2.36× | 1.99× | 1.85× |
| OLMo 2 | 2.33× | 1.86× | 2.36× | 1.99× | 1.85× |
| Falcon 3 | 2.46× | 1.94× | 2.50× | 2.06× | 1.92× |
| Claude 2 (legacy, Xenova mirror) | 2.46× | 1.93× | 2.49× | 2.10× | 1.97× |

## sk_nd/en ratio by domain

| Tokenizer | law | literary | news | social | speech |
|---|---|---|---|---|---|
| SlovakBERT (Slovak, Gerulata) | 0.81× | 0.91× | 0.94× | 0.94× | 0.87× |
| CSTinyLlama (Czech, BUT-FIT) | 0.94× | 0.89× | 1.01× | 0.97× | 0.89× |
| CSMPT (Czech, BUT-FIT) | 0.94× | 0.89× | 1.01× | 0.97× | 0.89× |
| mT5 | 1.28× | 1.13× | 1.33× | 1.23× | 1.12× |
| Teuken (OpenGPT-X) | 1.43× | 1.20× | 1.43× | 1.29× | 1.18× |
| EuroLLM | 1.47× | 1.27× | 1.49× | 1.33× | 1.22× |
| Gemini 4 Argon (API) | 1.61× | 1.43× | 1.69× | 1.45× | 1.28× |
| Gemma 1 / 2 | 1.62× | 1.39× | 1.69× | 1.45× | 1.32× |
| Gemma 3 | 1.61× | 1.41× | 1.69× | 1.46× | 1.33× |
| Gemini 3.8 Flash (API) | 1.61× | 1.41× | 1.69× | 1.46× | 1.33× |
| Llama 4 | 1.62× | 1.40× | 1.70× | 1.50× | 1.40× |
| Command R | 1.65× | 1.40× | 1.70× | 1.49× | 1.38× |
| Qwen 3.8 | 1.68× | 1.45× | 1.74× | 1.51× | 1.39× |
| Cohere North | 1.67× | 1.43× | 1.75× | 1.54× | 1.41× |
| Mistral Nemo / Small 3–4 / Large 2 (tekken) | 1.69× | 1.45× | 1.73× | 1.53× | 1.41× |
| Nemotron Nano 2 | 1.69× | 1.45× | 1.73× | 1.53× | 1.41× |
| Apertus (Swiss AI) | 1.69× | 1.45× | 1.73× | 1.53× | 1.41× |
| GPT-4o / 4.1 / 5 (o200k_base) | 1.68× | 1.44× | 1.75× | 1.54× | 1.42× |
| gpt-oss (o200k_harmony) | 1.68× | 1.44× | 1.75× | 1.54× | 1.42× |
| Phi-4-mini | 1.68× | 1.44× | 1.75× | 1.54× | 1.42× |
| Claude Opus / Sonnet / Haiku 5.5 (API) | 1.64× | 1.45× | 1.70× | 1.58× | 1.50× |
| ERNIE 5.5 | 1.73× | 1.44× | 1.79× | 1.54× | 1.42× |
| Mistral Large 4 | 1.74× | 1.45× | 1.78× | 1.55× | 1.43× |
| Llama 2 | 1.77× | 1.48× | 1.75× | 1.57× | 1.46× |
| Claude Sonnet 4.6 (API) | 1.75× | 1.48× | 1.79× | 1.59× | 1.50× |
| LFM3 (Liquid AI) | 1.83× | 1.49× | 1.84× | 1.59× | 1.48× |
| Llama 3.x | 1.82× | 1.51× | 1.86× | 1.60× | 1.48× |
| SmolLM3 | 1.82× | 1.51× | 1.86× | 1.60× | 1.48× |
| Granite 3.3 | 1.85× | 1.51× | 1.80× | 1.64× | 1.52× |
| DeepSeek V3 / R1 / V4 | 1.87× | 1.52× | 1.90× | 1.62× | 1.51× |
| GLM-4.5 / 4.6 / 4.7 | 1.87× | 1.55× | 1.92× | 1.63× | 1.52× |
| GLM-5.3 | 1.87× | 1.55× | 1.92× | 1.63× | 1.52× |
| Hunyuan 4 (Tencent) | 1.89× | 1.52× | 1.92× | 1.65× | 1.54× |
| Mistral / Mixtral (v3) | 1.90× | 1.57× | 1.90× | 1.67× | 1.54× |
| Bielik (Polish, SpeakLeash) | 1.90× | 1.57× | 1.90× | 1.67× | 1.54× |
| BLOOM | 1.94× | 1.53× | 1.94× | 1.67× | 1.56× |
| MiniMax M2 / M3 | 1.90× | 1.57× | 1.95× | 1.69× | 1.57× |
| Granite 4.2 | 1.95× | 1.58× | 1.99× | 1.69× | 1.57× |
| Qwen 2.5 / 3 | 1.94× | 1.60× | 1.98× | 1.69× | 1.57× |
| GPT-4 / 3.5 (cl100k_base) | 1.96× | 1.60× | 2.01× | 1.70× | 1.58× |
| Phi-4 | 1.96× | 1.60× | 2.01× | 1.70× | 1.58× |
| OLMo 2 | 1.96× | 1.60× | 2.01× | 1.70× | 1.58× |
| Kimi K2 / K3 | 1.96× | 1.58× | 1.99× | 1.73× | 1.61× |
| Falcon 3 | 2.00× | 1.61× | 2.03× | 1.70× | 1.56× |
| Claude 2 (legacy, Xenova mirror) | 2.06× | 1.64× | 2.10× | 1.76× | 1.65× |
