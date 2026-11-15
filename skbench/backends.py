"""Load a tokenizer and turn it into `count_all(texts) -> list[int]`.

Local tokenizers count with add_special_tokens=False (no BOS/EOS, no chat template).

API tokenizers (Claude, Gemini) are counted through the vendors' token-counting
endpoints, or, without the vendor's key but with OPENROUTER_API_KEY, from the
`usage.prompt_tokens` that OpenRouter reports for a one-token completion (the provider's
own count). Every API call wraps the text in a one-message request, which adds a small
fixed overhead; we measure it once per model as count(".") - 1 and subtract it. Results
are cached in cache/api_counts.json (keyed by model and sha1 of the text, plus "__via__"
naming the route) and that file is committed, so the API rows reproduce without a key and
CI never re-bills.
"""
import hashlib
import json
import os
import random
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .registry import OPENROUTER_IDS, TIKTOKEN_PATTERNS, revision

CACHE_PATH = Path(__file__).resolve().parent.parent / "cache" / "api_counts.json"
_OVERHEAD_KEY = "__overhead__"
_VIA_KEY = "__via__"
SAVE_EVERY = 500


class Skip(Exception):
    """Tokenizer unavailable (gated, offline, missing optional dependency, no API key)."""


def load(kind, ident, *, api_cache=None, api_workers=int(os.environ.get("SKBENCH_API_WORKERS", 8))):
    if kind == "tiktoken":
        import tiktoken

        enc = tiktoken.get_encoding(ident)
        return _local(lambda s: len(enc.encode_ordinary(s)))

    if kind == "hf":
        from tokenizers import Tokenizer

        tok = Tokenizer.from_pretrained(ident, revision=revision(ident))
        return _local(lambda s: len(tok.encode(s, add_special_tokens=False).ids))

    if kind == "hf-bpe":
        from huggingface_hub import hf_hub_download
        from tokenizers import ByteLevelBPETokenizer

        rev = revision(ident)
        tok = ByteLevelBPETokenizer(hf_hub_download(ident, "vocab.json", revision=rev),
                                    hf_hub_download(ident, "merges.txt", revision=rev))
        return _local(lambda s: len(tok.encode(s).ids))

    if kind == "tiktoken-hf":
        import tiktoken
        from huggingface_hub import hf_hub_download
        from tiktoken.load import load_tiktoken_bpe

        repo, pattern = ident.split("::")
        ranks = load_tiktoken_bpe(hf_hub_download(repo, "tiktoken.model", revision=revision(repo)))
        enc = tiktoken.Encoding(name=repo, pat_str=TIKTOKEN_PATTERNS[pattern], mergeable_ranks=ranks, special_tokens={})
        return _local(lambda s: len(enc.encode_ordinary(s)))

    if kind == "spm":
        try:
            import sentencepiece as spm
        except ImportError as e:
            raise Skip("pip install sentencepiece") from e
        from huggingface_hub import hf_hub_download

        sp = spm.SentencePieceProcessor(model_file=hf_hub_download(ident, "tokenizer.model", revision=revision(ident)))
        return _local(lambda s: len(sp.encode(s)))

    if kind in ("anthropic", "gemini"):
        cache = api_cache if api_cache is not None else ApiCache.load()
        return _ApiCounter(kind, ident, cache, api_workers)

    raise ValueError(f"unknown tokenizer kind {kind!r}")


def _local(fn):
    return lambda texts: [fn(t) for t in texts]


# --------------------------------------------------------------------------------------
# API backends
# --------------------------------------------------------------------------------------


def _key(text):
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:16]


class ApiCache:
    def __init__(self, data, path):
        self.data, self.path, self.lock = data, path, threading.Lock()

    @classmethod
    def load(cls, path=CACHE_PATH):
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        return cls(data, path)

    def get(self, model, text):
        return self.data.get(model, {}).get(_key(text))

    def put(self, model, text, n):
        with self.lock:
            self.data.setdefault(model, {})[_key(text)] = n

    def save(self):
        if not self.data:
            return
        self.path.parent.mkdir(exist_ok=True)
        with self.lock:
            data = {m: dict(sorted(v.items())) for m, v in sorted(self.data.items())}
        tmp = self.path.with_suffix(".tmp")  # write-then-rename: an interrupted save never truncates the cache
        tmp.write_text(json.dumps(data, indent=0, sort_keys=True) + "\n", encoding="utf-8")
        tmp.replace(self.path)


class _ApiCounter:
    def __init__(self, kind, model, cache, workers):
        self.kind, self.model, self.cache, self.workers = kind, model, cache, workers
        self._raw, self.via = None, None

    def _client(self):
        if self._raw:
            return self._raw
        native_key = os.environ.get("ANTHROPIC_API_KEY") if self.kind == "anthropic" else (
            os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
        if not native_key and os.environ.get("OPENROUTER_API_KEY") and self.model in OPENROUTER_IDS:
            self._raw, self.via = _openrouter(OPENROUTER_IDS[self.model], os.environ["OPENROUTER_API_KEY"]), "openrouter"
            return self._raw
        self.via = self.kind
        if self.kind == "anthropic":
            try:
                import anthropic
            except ImportError as e:
                raise Skip("pip install anthropic") from e
            client = anthropic.Anthropic()

            def raw(text):
                return client.messages.count_tokens(
                    model=self.model, messages=[{"role": "user", "content": text}]
                ).input_tokens

        else:
            if not (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")):
                raise Skip("GEMINI_API_KEY not set and counts not cached")
            try:
                from google import genai
            except ImportError as e:
                raise Skip("pip install google-genai") from e
            client = genai.Client()

            def raw(text):
                return client.models.count_tokens(model=self.model, contents=text).total_tokens

        self._raw = raw
        return raw

    def _overhead(self):
        cached = self.cache.data.get(self.model, {}).get(_OVERHEAD_KEY)
        if cached is None:
            cached = self._client()(".") - 1
            with self.cache.lock:
                self.cache.data.setdefault(self.model, {})[_OVERHEAD_KEY] = cached
        return cached

    def __call__(self, texts):
        missing = sorted({t for t in texts if self.cache.get(self.model, t) is None})
        if missing:
            try:
                raw = self._client()
                overhead = self._overhead()
                with self.cache.lock:
                    self.cache.data[self.model][_VIA_KEY] = self.via

                done = [0]

                def one(t):
                    self.cache.put(self.model, t, raw(t) - overhead)
                    with self.cache.lock:
                        done[0] += 1
                        n = done[0]
                    if n % SAVE_EVERY == 0:  # a long run can be stopped and resumed without losing counts
                        self.cache.save()
                        print(f"     {self.model}: {n}/{len(missing)} counted", file=sys.stderr, flush=True)

                with ThreadPoolExecutor(self.workers) as ex:
                    list(ex.map(one, missing))
            except Skip:
                raise
            except Exception as e:  # auth, rate limit, unknown model ...
                raise Skip(f"{type(e).__name__}: {str(e)[:120]}") from e
            finally:
                self.cache.save()
        return [self.cache.get(self.model, t) for t in texts]


def _openrouter(model, key, attempts=12):
    """Count a text's tokens from OpenRouter's usage report on a minimal completion.

    Reasoning models (Gemini) may report no usage when the answer is cut at one token, so the
    limit grows until usage comes back. Rate limits, timeouts and 5xx errors are retried with
    backoff (honouring Retry-After), so a shared, busy key slows the run down instead of
    failing it.
    """
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    def wait(attempt, retry_after=None):
        try:
            delay = float(retry_after)
        except (TypeError, ValueError):
            delay = min(60.0, 2.0 ** attempt)
        time.sleep(delay + random.uniform(0, 1))

    def raw(text):
        max_tokens, last = 1, None
        for attempt in range(attempts):
            body = json.dumps({"model": model, "max_tokens": max_tokens,
                               "messages": [{"role": "user", "content": text}]}).encode("utf-8")
            try:
                with urllib.request.urlopen(urllib.request.Request(url, body, headers), timeout=120) as r:
                    data = json.load(r)
            except urllib.error.HTTPError as e:
                last = f"HTTP {e.code}"
                if e.code in (408, 429) or e.code >= 500:
                    wait(attempt, e.headers.get("Retry-After"))
                    continue
                raise RuntimeError(f"OpenRouter {last} for {model}") from None
            except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
                last = type(e).__name__
                wait(attempt)
                continue
            if data.get("error"):  # provider errors can arrive with HTTP 200
                last = f"error {str(data['error'].get('code', ''))[:20]}"
                wait(attempt)
                continue
            n = (data.get("usage") or {}).get("prompt_tokens")
            if n is not None:
                return n
            last = "no usage"
            max_tokens = min(max_tokens * 16, 256)
        raise RuntimeError(f"OpenRouter gave no token count for {model} after {attempts} attempts (last: {last})")

    return raw
