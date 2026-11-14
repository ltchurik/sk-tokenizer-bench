"""Third-party corpora: fetched from their publishers at run time, never stored in this repo.

The repo links to the sources and publishes only token counts. Each corpus is downloaded once into
cache/corpora/ (git-ignored), from a pinned file checked against a SHA-256, and converted into the
JSONL format the benchmark reads ({"id", "domain", <lang>: <text>, ...}). The converted files are
checked against a SHA-256 too, so every run measures exactly the same text.

- FLORES-200 devtest (Meta, CC BY-SA 4.0), 1012 sentences in 10 languages
- genres: WMT24++ en-sk_SK (Google; third-party sources offered for research use) for social media,
  speech, literary and news, plus 300 paragraphs of EU legislation from the EU Publications Office

See corpus/README.md for sources, licences and the exact conversion.
"""
import hashlib
import html
import io
import json
import re
import sys
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "cache" / "corpora"

FLORES_URL = "https://dl.fbaipublicfiles.com/nllb/flores200_dataset.tar.gz"
FLORES_SHA256 = "b8b0b76783024b85797e5cc75064eb83fc5288b41e9654dabc7be6ae944011f6"
FLORES_LANGS = {"sk": "slk_Latn", "cs": "ces_Latn", "pl": "pol_Latn", "hu": "hun_Latn", "sl": "slv_Latn",
                "hr": "hrv_Latn", "ro": "ron_Latn", "uk": "ukr_Cyrl", "de": "deu_Latn", "en": "eng_Latn"}
FLORES_OUT_SHA256 = "ae6e24ec8cb125d707339012da3319e510c1d189a515d08d37e09f48b08a573f"

WMT_REV = "fd7405c06494bc66a57b25f55d217a72f96e60dc"
WMT_URL = f"https://huggingface.co/datasets/google/wmt24pp/resolve/{WMT_REV}/en-sk_SK.jsonl"
WMT_SHA256 = "dc4b5e84e7bbb3a0ddd31846c83be2214456f5f3637a3301b1d762396a9bb98f"
WMT_DOMAINS = ["social", "speech", "literary", "news"]

EU_ACTS = {"32016R0679": "GDPR", "32024R1689": "AI Act", "32011L0083": "Consumer Rights Directive"}  # CELEX
EU_PER_ACT = 100  # paragraphs per act, evenly spaced
EU_MIN_CHARS = 60  # skip numbering, headings and one-liners
EU_SHA256 = "3d27efeb82490031c6c3b8376f15e0cf026da3dccdadf43948b7cb1ef8a13ec4"

FLORES = CACHE / "flores200_devtest.jsonl"
GENRES = CACHE / "genres.jsonl"


def _get(url, headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": "sk-tokenizer-bench", **(headers or {})})
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read()


def _download(url, sha256, name):
    """Pinned download, cached under cache/corpora/."""
    path = CACHE / name
    if not path.exists():
        print(f"downloading {url}", file=sys.stderr)
        data = _get(url)
        if hashlib.sha256(data).hexdigest() != sha256:
            raise RuntimeError(f"{url}: content does not match the pinned SHA-256")
        CACHE.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    return path


def _write(rows, path, sha256, what, strict=True):
    data = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows).encode("utf-8")
    if hashlib.sha256(data).hexdigest() != sha256:
        msg = f"{what}: converted text differs from the version the published results were measured on"
        if strict:
            raise RuntimeError(msg)
        print(f"warning: {msg}", file=sys.stderr)
    CACHE.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


# --- FLORES-200 -----------------------------------------------------------------------------------

def _unescape_csv(s):
    """53 Croatian lines carry CSV quote escaping upstream: the outer quotes go and "" becomes \"."""
    if s.startswith('"') and s.endswith('"') and '""' in s:
        return s[1:-1].replace('""', '"')
    return s


def build_flores():
    tgz = _download(FLORES_URL, FLORES_SHA256, "flores200_dataset.tar.gz")
    with tarfile.open(tgz) as tar:
        def read(member):
            return tar.extractfile(f"./flores200_dataset/{member}").read().decode("utf-8")
        cols = {lg: read(f"devtest/{code}.devtest").split("\n")[:1012] for lg, code in FLORES_LANGS.items()}
        meta = list(csv_rows(read("metadata_devtest.tsv")))
    rows = []
    for i in range(1012):
        domain = meta[i]["domain"]
        row = {"id": f"flores-devtest-{i:04d}", "domain": domain}
        for lg, col in cols.items():
            text = col[i].strip()  # str.strip() also removes U+3000 ideographic spaces
            row[lg] = _unescape_csv(text).strip() if lg == "hr" else text
        rows.append(row)
    _write(rows, FLORES, FLORES_OUT_SHA256, "FLORES-200")


def csv_rows(tsv):
    lines = tsv.rstrip("\n").split("\n")
    head = lines[0].split("\t")
    for line in lines[1:]:
        yield dict(zip(head, line.split("\t")))


# --- genres: WMT24++ + EU legislation ---------------------------------------------------------------

def wmt_rows():
    path = _download(WMT_URL, WMT_SHA256, f"wmt24pp-en-sk_SK.{WMT_REV[:12]}.jsonl")
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        if r["domain"] not in WMT_DOMAINS or r["is_bad_source"]:
            continue  # drops the canary line and the segments the authors recommend excluding
        sk, en = r["target"].strip(), r["source"].strip()
        if sk and en:
            rows.append({"id": f"wmt24pp-{r['segment_id']}", "domain": r["domain"], "sk": sk, "en": en})
    return rows


def _act_paragraphs(celex, lang):
    path = CACHE / f"eurlex-{celex}-{lang}.xhtml"
    if not path.exists():
        print(f"downloading CELEX {celex} ({lang}) from the EU Publications Office", file=sys.stderr)
        CACHE.mkdir(parents=True, exist_ok=True)
        path.write_bytes(_get(f"http://publications.europa.eu/resource/celex/{celex}",
                              {"Accept": "application/xhtml+xml", "Accept-Language": lang}))
    out = []
    for cls, body in re.findall(r'<p[^>]*class="([^"]*)"[^>]*>(.*?)</p>', path.read_text(encoding="utf-8"), re.S):
        out.append((cls, re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", body))).strip()))
    return out


def eu_rows():
    rows = []
    for celex, name in EU_ACTS.items():
        sk, en = _act_paragraphs(celex, "slk"), _act_paragraphs(celex, "eng")
        if [c for c, _ in sk] != [c for c, _ in en]:
            raise RuntimeError(f"{name}: Slovak and English paragraph structure differ, cannot align")
        pairs = [(i, s, e) for i, ((c, s), (_, e)) in enumerate(zip(sk, en))
                 if c == "oj-normal" and len(s) >= EU_MIN_CHARS and len(e) >= EU_MIN_CHARS]
        step = len(pairs) / EU_PER_ACT
        for k in range(min(EU_PER_ACT, len(pairs))):
            i, s, e = pairs[int(k * step)]
            rows.append({"id": f"eurlex-{celex}-{i}", "domain": "law", "sk": s, "en": e})
    return rows


def build_genres():
    law = eu_rows()
    data = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in law).encode("utf-8")
    if hashlib.sha256(data).hexdigest() != EU_SHA256:  # the EU may re-render its pages; not fatal
        print("warning: EU legislation text differs from the version the published results were measured on",
              file=sys.stderr)
    rows = wmt_rows() + law
    CACHE.mkdir(parents=True, exist_ok=True)
    GENRES.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


BUILDERS = {FLORES: build_flores, GENRES: build_genres}


def ensure(path):
    """Build a third-party corpus on first use. Other paths are returned unchanged."""
    if path in BUILDERS and not path.exists():
        BUILDERS[path]()
    return path
