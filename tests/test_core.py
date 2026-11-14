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
