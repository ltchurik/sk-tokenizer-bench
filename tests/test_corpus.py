import pytest

from skbench.core import BASE, CORPORA, load_corpus


@pytest.mark.parametrize("name", sorted(CORPORA))
def test_corpus_well_formed(name):
    rows, langs = load_corpus(CORPORA[name])
    assert langs[-1] == BASE and "sk" in langs
    ids = [r["id"] for r in rows]
    assert len(ids) == len(set(ids)), "duplicate ids"
    for r in rows:
        assert r["domain"]
        for lg in langs:
            assert r[lg] == r[lg].strip(), f"{r['id']}/{lg} has surrounding whitespace"


def test_flores_shape():
    rows, langs = load_corpus(CORPORA["flores"])
    assert len(rows) == 1012
    assert langs == ["sk", "cs", "pl", "hu", "de", "en"]
