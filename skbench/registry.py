"""Tokenizer registry: display name -> how to load it.

Each entry is (kind, ident). Kinds:
  tiktoken      tiktoken encoding name (o200k_base, cl100k_base)
  hf            Hugging Face repo that ships tokenizer.json (loaded with `tokenizers`)
  hf-bpe        HF repo with vocab.json + merges.txt only (byte-level BPE, e.g. RoBERTa)
  tiktoken-hf   HF repo with a tiktoken.model file; ident = "repo::pattern-name"
  spm           HF repo with a SentencePiece tokenizer.model (needs `sentencepiece`)
  anthropic     Claude model id, counted with the Anthropic count_tokens API
  gemini        Gemini model id, counted with the Gemini countTokens API

Gated originals (Meta, Google, Cohere) are substituted with ungated mirrors that ship
byte-identical tokenizer files.

Every Hugging Face repo is pinned to a commit in revisions.json, so an upstream change to a
tokenizer file can never move the numbers silently. `python tools/pin_revisions.py` adds pins
for new repos; `--update` moves all pins to the current head (then re-run the benchmark).
"""
import json
from pathlib import Path

REVISIONS = json.loads((Path(__file__).with_name("revisions.json")).read_text(encoding="utf-8"))

TOKENIZERS = {
    # --- OpenAI -------------------------------------------------------------------------
    "GPT-4o / 4.1 / 5 (o200k_base)": ("tiktoken", "o200k_base"),
    "GPT-4 / 3.5 (cl100k_base)": ("tiktoken", "cl100k_base"),
    "gpt-oss (o200k_harmony)": ("hf", "openai/gpt-oss-20b"),
    # --- Meta ---------------------------------------------------------------------------
    "Llama 2": ("hf", "NousResearch/Llama-2-7b-hf"),
    "Llama 3.x": ("hf", "unsloth/Llama-3.1-8B"),
    "Llama 4": ("hf", "unsloth/Llama-4-Scout-17B-16E-Instruct"),
    # --- Mistral ------------------------------------------------------------------------
    "Mistral / Mixtral (v3)": ("hf", "mistralai/Mistral-7B-Instruct-v0.3"),
    "Mistral Nemo / Small 3–4 / Large 2 (tekken)": ("hf", "mistralai/Mistral-Small-3.1-24B-Instruct-2503"),
    "Mistral Large 4": ("hf", "mistralai/Mistral-Large-4-1T-A52B"),
    # --- Google -------------------------------------------------------------------------
    "Gemma 1 / 2": ("hf", "unsloth/gemma-2-9b"),
    "Gemma 3": ("hf", "unsloth/gemma-3-4b-it"),
    "mT5": ("hf", "Xenova/mt5-base"),
    # --- Chinese labs -------------------------------------------------------------------
    "Qwen 2.5 / 3": ("hf", "Qwen/Qwen3-8B"),
    "Qwen 3.8": ("hf", "Qwen/Qwen3.8-27B"),
    "DeepSeek V3 / R1 / V4": ("hf", "deepseek-ai/DeepSeek-V3.1"),
    "GLM-4.5 / 4.6 / 4.7": ("hf", "zai-org/GLM-4.6"),
    "GLM-5.3": ("hf", "zai-org/GLM-5.3"),
    "Kimi K2 / K3": ("tiktoken-hf", "moonshotai/Kimi-K2-Instruct::kimi"),
    "MiniMax M2 / M3": ("hf", "MiniMaxAI/MiniMax-M2"),
    "ERNIE 5.5": ("hf", "baidu/ERNIE-5.5-Flash-Base"),
    "Hunyuan 4 (Tencent)": ("hf", "tencent/Hy4-preview"),
    # --- Other US / global --------------------------------------------------------------
    "Phi-4": ("hf", "microsoft/phi-4"),
    "Phi-4-mini": ("hf", "microsoft/Phi-4-mini-instruct"),
    "Command R": ("hf", "Xenova/c4ai-command-r-v01-tokenizer"),
    "Cohere North": ("hf", "CohereLabs/North-Micro-Vision-Instruct"),
    "Nemotron Nano 2": ("hf", "nvidia/NVIDIA-Nemotron-Nano-9B-v2"),
    "Granite 3.3": ("hf", "ibm-granite/granite-3.3-8b-instruct"),
    "Granite 4.2": ("hf", "ibm-granite/granite-4.2-8b"),
    "LFM3 (Liquid AI)": ("hf", "LiquidAI/LFM3-1.7B"),
    "Falcon 3": ("hf", "tiiuae/Falcon3-7B-Instruct"),
    "SmolLM3": ("hf", "HuggingFaceTB/SmolLM3-3B"),
    "OLMo 2": ("hf", "allenai/OLMo-2-1124-7B"),
    "BLOOM": ("hf", "bigscience/bloom"),
    "Claude 2 (legacy, Xenova mirror)": ("hf", "Xenova/claude-tokenizer"),
    # --- European multilingual ----------------------------------------------------------
    "EuroLLM": ("hf", "utter-project/EuroLLM-1.7B"),
    "Apertus (Swiss AI)": ("hf", "swiss-ai/Apertus-8B-2509"),
    "Teuken (OpenGPT-X)": ("spm", "openGPT-X/Teuken-7B-instruct-research-v0.4"),
    # --- Regional (Slovak / Czech / Polish) ---------------------------------------------
    "SlovakBERT (Slovak, Gerulata)": ("hf-bpe", "gerulata/slovakbert"),
    "CSTinyLlama (Czech, BUT-FIT)": ("hf", "BUT-FIT/CSTinyLlama-1.2B"),
    "CSMPT (Czech, BUT-FIT)": ("hf", "BUT-FIT/csmpt7b"),
    "Bielik (Polish, SpeakLeash)": ("hf", "speakleash/Bielik-11B-v2.3-Instruct"),
    # --- Closed tokenizers, API only (skipped without a key unless cached) ---------------
    "Claude Opus 5.5 (API)": ("anthropic", "claude-opus-5-5"),
    "Claude Sonnet 5.5 (API)": ("anthropic", "claude-sonnet-5-5"),
    "Claude Haiku 5.5 (API)": ("anthropic", "claude-haiku-5-5"),
    "Claude Sonnet 4.6 (API)": ("anthropic", "claude-sonnet-4-6"),
    "Gemini 3.8 Flash (API)": ("gemini", "gemini-3.8-flash"),
    "Gemini 4 Argon (API)": ("gemini", "gemini-4-argon"),
}

API_KINDS = {"anthropic", "gemini"}

# Month the earliest model named in each row was released (used for the timeline chart).
# Lineages draw a line through successive tokenizers of the same vendor.
RELEASED = {
    "GPT-4 / 3.5 (cl100k_base)": "2023-03",
    "GPT-4o / 4.1 / 5 (o200k_base)": "2024-05",
    "gpt-oss (o200k_harmony)": "2025-08",
    "Llama 2": "2023-07",
    "Llama 3.x": "2024-04",
    "Llama 4": "2025-04",
    "Mistral / Mixtral (v3)": "2024-04",
    "Mistral Nemo / Small 3–4 / Large 2 (tekken)": "2024-07",
    "Gemma 1 / 2": "2024-02",
    "Gemma 3": "2025-03",
    "mT5": "2020-10",
    "Qwen 2.5 / 3": "2024-09",
    "DeepSeek V3 / R1 / V4": "2024-12",
    "GLM-4.5 / 4.6 / 4.7": "2025-07",
    "Kimi K2 / K3": "2025-07",
    "MiniMax M2 / M3": "2025-10",
    "Phi-4": "2024-12",
    "Phi-4-mini": "2025-02",
    "Command R": "2024-03",
    "Nemotron Nano 2": "2025-08",
    "Granite 3.3": "2025-04",
    "Falcon 3": "2024-12",
    "SmolLM3": "2025-07",
    "OLMo 2": "2024-11",
    "BLOOM": "2022-07",
    "Claude 2 (legacy, Xenova mirror)": "2023-07",
    "EuroLLM": "2024-09",
    "Apertus (Swiss AI)": "2025-09",
    "Teuken (OpenGPT-X)": "2024-11",
    "Qwen 3.8": "2026-08",
    "Mistral Large 4": "2026-09",
    "GLM-5.3": "2026-08",
    "ERNIE 5.5": "2026-10",
    "Hunyuan 4 (Tencent)": "2026-08",
    "Cohere North": "2026-08",
    "Granite 4.2": "2026-08",
    "LFM3 (Liquid AI)": "2026-10",
}
LINEAGES = {
    "OpenAI": ["GPT-4 / 3.5 (cl100k_base)", "GPT-4o / 4.1 / 5 (o200k_base)"],
    "Meta": ["Llama 2", "Llama 3.x", "Llama 4"],
    "Mistral": ["Mistral / Mixtral (v3)", "Mistral Nemo / Small 3–4 / Large 2 (tekken)", "Mistral Large 4"],
    "Google": ["Gemma 1 / 2", "Gemma 3"],
    "Qwen": ["Qwen 2.5 / 3", "Qwen 3.8"],
}

# Pre-tokenization patterns for tiktoken-format vocabularies shipped on the HF Hub.
# Copied verbatim from the model repo's tokenization_*.py.
TIKTOKEN_PATTERNS = {
    "kimi": "|".join(
        [
            r"""[\p{Han}]+""",
            r"""[^\r\n\p{L}\p{N}]?[\p{Lu}\p{Lt}\p{Lm}\p{Lo}\p{M}&&[^\p{Han}]]*[\p{Ll}\p{Lm}\p{Lo}\p{M}&&[^\p{Han}]]+(?i:'s|'t|'re|'ve|'m|'ll|'d)?""",
            r"""[^\r\n\p{L}\p{N}]?[\p{Lu}\p{Lt}\p{Lm}\p{Lo}\p{M}&&[^\p{Han}]]+[\p{Ll}\p{Lm}\p{Lo}\p{M}&&[^\p{Han}]]*(?i:'s|'t|'re|'ve|'m|'ll|'d)?""",
            r"""\p{N}{1,3}""",
            r""" ?[^\s\p{L}\p{N}]+[\r\n]*""",
            r"""\s*[\r\n]+""",
            r"""\s+(?!\S)""",
            r"""\s+""",
        ]
    ),
}

# Repo the web calculator loads in the browser (tokenizers.js needs tokenizer.json +
# tokenizer_config.json). Defaults to the registry repo for kind "hf"; tiktoken encodings
# use Xenova's byte-identical tokenizer.json exports (parity-tested in CI).
BROWSER_REPO = {
    "GPT-4o / 4.1 / 5 (o200k_base)": "Xenova/gpt-4o",
    "GPT-4 / 3.5 (cl100k_base)": "Xenova/gpt-4",
}


def browser_repo(name):
    kind, ident = TOKENIZERS[name]
    return BROWSER_REPO.get(name) or (ident if kind == "hf" else None)


def hf_repo(kind, ident):
    """The Hugging Face repo a registry entry downloads from, or None (tiktoken, API)."""
    if kind in ("hf", "hf-bpe", "spm"):
        return ident
    if kind == "tiktoken-hf":
        return ident.split("::")[0]
    return None


def all_hf_repos():
    repos = {hf_repo(*spec) for spec in TOKENIZERS.values()} | set(BROWSER_REPO.values())
    return sorted(r for r in repos if r)


def revision(repo):
    """Pinned commit of `repo`; a KeyError means `python tools/pin_revisions.py` was not run."""
    return REVISIONS[repo]
