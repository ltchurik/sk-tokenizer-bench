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
"""

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
    "Mistral Nemo / Small 3 / Large 2 (tekken)": ("hf", "mistralai/Mistral-Small-3.1-24B-Instruct-2503"),
    # --- Google -------------------------------------------------------------------------
    "Gemma 2 / 3": ("hf", "unsloth/gemma-3-4b-it"),
    "mT5": ("hf", "Xenova/mt5-base"),
    # --- Chinese labs -------------------------------------------------------------------
    "Qwen 2.5 / 3": ("hf", "Qwen/Qwen3-8B"),
    "DeepSeek V3 / V3.1 / R1": ("hf", "deepseek-ai/DeepSeek-V3.1"),
    "GLM-4.5 / 4.6": ("hf", "zai-org/GLM-4.6"),
    "Kimi K2": ("tiktoken-hf", "moonshotai/Kimi-K2-Instruct::kimi"),
    "MiniMax-M2": ("hf", "MiniMaxAI/MiniMax-M2"),
    # --- Other US / global --------------------------------------------------------------
    "Phi-4": ("hf", "microsoft/phi-4"),
    "Phi-4-mini": ("hf", "microsoft/Phi-4-mini-instruct"),
    "Command R": ("hf", "Xenova/c4ai-command-r-v01-tokenizer"),
    "Nemotron Nano 2": ("hf", "nvidia/NVIDIA-Nemotron-Nano-9B-v2"),
    "Granite 3.3": ("hf", "ibm-granite/granite-3.3-8b-instruct"),
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
