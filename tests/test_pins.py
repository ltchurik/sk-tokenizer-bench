import re

from skbench import env
from skbench.core import CORPORA
from skbench.registry import REVISIONS, TOKENIZERS, all_hf_repos


def test_every_hf_repo_is_pinned_to_a_commit():
    missing = [r for r in all_hf_repos() if r not in REVISIONS]
    assert not missing, f"run `python tools/pin_revisions.py` for {missing}"
    assert all(re.fullmatch(r"[0-9a-f]{40}", REVISIONS[r]) for r in all_hf_repos())


def test_no_stale_pins():
    assert set(REVISIONS) == set(all_hf_repos())


def test_environment_records_versions_and_revisions():
    tok = {n: TOKENIZERS[n] for n in ("GPT-4o / 4.1 / 5 (o200k_base)", "Llama 3.x")}
    info = env.environment(["--corpus", "custom"], {"custom": CORPORA["custom"]}, tok)
    assert info["packages"]["tokenizers"] and info["python"]
    assert info["machine"]["gpu_used"] is False
    assert info["tokenizers"]["Llama 3.x"]["revision"] == REVISIONS["unsloth/Llama-3.1-8B"]
    assert info["tokenizers"]["GPT-4o / 4.1 / 5 (o200k_base)"]["revision"] is None
    assert len(info["corpora_sha256"]["custom"]) == 64
