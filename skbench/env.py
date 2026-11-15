"""Record the environment a run used (results/env.json).

Token counts are deterministic: the same tokenizer files, library versions and corpus give the
same numbers on any machine. The hardware is recorded for completeness, not because it matters;
no GPU is used.
"""
import datetime
import hashlib
import os
import platform
import subprocess
import sys
from importlib import metadata

from .registry import hf_repo, revision

PACKAGES = ["tiktoken", "tokenizers", "sentencepiece", "huggingface_hub", "numpy", "anthropic", "google-genai"]


def _version(pkg):
    try:
        return metadata.version(pkg)
    except metadata.PackageNotFoundError:
        return None


def _cpu():
    try:
        out = subprocess.run(["lscpu"], capture_output=True, text=True, timeout=10).stdout
        names = [ln.split(":", 1)[1].strip() for ln in out.splitlines() if ln.startswith("Model name:")]
        if names:
            return " + ".join(dict.fromkeys(names))
    except (OSError, subprocess.SubprocessError):
        pass
    return platform.processor() or None


def _memory_gb():
    try:
        return round(os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 2**30)
    except (ValueError, OSError, AttributeError):
        return None


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def environment(argv, corpora, tokenizers):
    """corpora: {name: Path}; tokenizers: {name: (kind, ident)} that were measured."""
    return {
        "date_utc": datetime.datetime.now(datetime.timezone.utc).date().isoformat(),
        "command": " ".join(["python", "bench.py", *argv]),
        "python": f"{platform.python_implementation()} {platform.python_version()}",
        "packages": {p: _version(p) for p in PACKAGES},
        "machine": {
            "os": platform.platform(),
            "arch": platform.machine(),
            "cpu": _cpu(),
            "cpu_count": os.cpu_count(),
            "memory_gb": _memory_gb(),
            "gpu_used": False,
        },
        "corpora_sha256": {name: _sha256(path) for name, path in corpora.items()},
        "tokenizers": {
            name: {"kind": kind, "id": ident, "revision": revision(hf_repo(kind, ident)) if hf_repo(kind, ident) else None}
            for name, (kind, ident) in tokenizers.items()
        },
        "byteorder": sys.byteorder,
    }
