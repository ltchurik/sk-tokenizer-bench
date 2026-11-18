import json

from skbench import backends, report
from skbench.core import mark_identical, measure, ratio_ci

ROWS = [
    {"id": "a", "domain": "x", "sk": "aaaa", "en": "aa"},
    {"id": "b", "domain": "y", "sk": "bbbbbb", "en": "bbb"},
]


def char_counter(texts):
    return [len(t) for t in texts]


def test_ratio_of_sums_not_mean_of_ratios():
    summary, per = measure(char_counter, ROWS, ["sk", "en"], n_boot=0)
    assert per == {"sk": [4, 6], "en": [2, 3]}
    assert summary["ratio_vs_en"]["sk"] == {"x": 2.0, "y": 2.0, "ALL": 2.0}
    assert summary["chars_per_token"] == {"sk": 1.0, "en": 1.0}


def test_bootstrap_ci_is_deterministic_and_brackets_point_estimate():
    num, den = [3, 5, 2, 8, 4, 6] * 20, [2, 2, 1, 4, 3, 3] * 20
    lo, hi = ratio_ci(num, den, n_boot=500)
    assert (lo, hi) == ratio_ci(num, den, n_boot=500)
    assert lo < sum(num) / sum(den) < hi


def test_mark_identical():
    res = {"A": {}, "B": {}, "C": {}}
    counts = {"A": {"sk": [1, 2]}, "B": {"sk": [1, 3]}, "C": {"sk": [1, 2]}}
    mark_identical(res, counts)
    assert [res[n]["same_as"] for n in "ABC"] == [None, None, "A"]


def test_api_counter_uses_cache_without_network(tmp_path):
    path = tmp_path / "c.json"
    path.write_text(json.dumps({"m": {backends._key("ahoj"): 3, backends._key("hi"): 1}}))
    counter = backends.load("anthropic", "m", api_cache=backends.ApiCache.load(path))
    assert counter(["ahoj", "hi", "ahoj"]) == [3, 1, 3]


def test_readme_block_replacement(tmp_path):
    p = tmp_path / "README.md"
    p.write_text(f"intro\n{report.README_START}\nold\n{report.README_END}\noutro\n")
    report.update_readme(p, "NEW")
    text = p.read_text()
    assert "old" not in text and "NEW" in text and text.startswith("intro") and text.endswith("outro\n")


def test_openrouter_route_reads_prompt_tokens_and_retries_without_usage(monkeypatch, tmp_path):
    import io

    replies = iter([{"usage": None}, {"usage": {"prompt_tokens": 9}},   # "." -> overhead 8
                    {"usage": {"prompt_tokens": 12}}])                   # "ahoj" -> 4
    sent = []

    def fake_urlopen(req, timeout):
        sent.append(json.loads(req.data))
        return io.BytesIO(json.dumps(next(replies)).encode())

    monkeypatch.setattr(backends.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test")
    cache = backends.ApiCache.load(tmp_path / "c.json")
    counter = backends.load("anthropic", "claude-haiku-5-5", api_cache=cache)
    assert counter(["ahoj"]) == [4]
    assert sent[0]["model"] == "anthropic/claude-haiku-5.5" and [s["max_tokens"] for s in sent] == [1, 16, 1]
    assert cache.data["claude-haiku-5-5"]["__via__"] == "openrouter"
    assert "test" not in (tmp_path / "c.json").read_text()


def test_openrouter_refusal_is_recounted_on_vertex(monkeypatch):
    import io

    refusal = {"usage": None, "choices": [{"finish_reason": "content_filter", "message": {"content": None}}]}
    replies = iter([refusal, {"usage": {"prompt_tokens": 20}}])
    sent = []

    def fake_urlopen(req, timeout):
        sent.append(json.loads(req.data))
        return io.BytesIO(json.dumps(next(replies)).encode())

    monkeypatch.setattr(backends.urllib.request, "urlopen", fake_urlopen)
    raw = backends._openrouter("anthropic/claude-sonnet-4.6", "test", rpm=0)
    assert raw("text") == 20
    assert "provider" not in sent[0] and sent[1]["provider"] == {"order": ["google-vertex"], "allow_fallbacks": False}
    assert sent[1]["max_tokens"] == 1
