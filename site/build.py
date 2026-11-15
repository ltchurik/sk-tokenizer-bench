#!/usr/bin/env python3
"""Assemble the static web calculator into _site/.

    python site/build.py            # writes _site/ (index.html, en/index.html, app.js, style.css, data.json, images)
    python -m http.server -d _site  # preview at http://localhost:8000

data.json is derived from results/flores/results.json, prices.json and the registry, so the page
always shows the numbers of the last benchmark run. Tokenizer download sizes come from the
Hugging Face API (best effort; the page works without them).

The page exists in two languages with their own URLs: site/index.html is the Slovak page (/),
and the English page (/en/) is rendered from it with the texts in site/en.json, so search
engines and people without JavaScript get each language as real HTML.
"""
import gzip
import html
import json
import re
import shutil
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from skbench.registry import API_KINDS, RELEASED, TOKENIZERS, browser_repo, revision  # noqa: E402

SITE, OUT = ROOT / "site", ROOT / "_site"
BASE_URL = "https://ltchurik.github.io/sk-tokenizer-bench/"
MULTILINGUAL = {"mT5", "EuroLLM", "Apertus (Swiss AI)", "Teuken (OpenGPT-X)"}


def group(name, kind):
    if kind in API_KINDS:
        return "api"
    if "(Slovak" in name or "(Czech" in name or "(Polish" in name:
        return "regional"
    return "multilingual" if name in MULTILINGUAL else "mainstream"


def size_mb(repo):
    try:
        url = f"https://huggingface.co/api/models/{repo}?blobs=true"
        with urllib.request.urlopen(url, timeout=20) as r:
            sib = {s["rfilename"]: s.get("size") for s in json.load(r)["siblings"]}
        return round(sib["tokenizer.json"] / 1e6, 1)
    except Exception as e:  # offline build: sizes are cosmetic
        print(f"size unknown for {repo}: {type(e).__name__}", file=sys.stderr)
        return None


def build_data():
    res = json.loads((ROOT / "results" / "flores" / "results.json").read_text(encoding="utf-8"))
    prices = json.loads((ROOT / "prices.json").read_text(encoding="utf-8"))
    # The page is about Slovak: merge tokenizers whose counts match on sk, sk_nd and en,
    # even if they differ on another language (e.g. tekken vs Apertus on one Ukrainian sentence).
    counts = json.loads(gzip.decompress((ROOT / "results" / "flores" / "counts.json.gz").read_bytes()))["counts"]
    first, aliases = {}, {}
    for name in res:
        sig = tuple(tuple(counts[name][lg]) for lg in ("sk", "sk_nd", "en"))
        if sig in first:
            aliases.setdefault(first[sig], []).append(name)
        else:
            first[sig] = name
    merged = {a for v in aliases.values() for a in v}
    rows = []
    for name, r in res.items():
        if name in merged:
            continue
        kind = TOKENIZERS[name][0]
        repo = browser_repo(name)
        R, C = r["ratio_vs_en"], r["chars_per_token"]
        rows.append({
            "name": name,
            "also": aliases.get(name, []),
            "group": group(name, kind),
            "repo": repo,
            "rev": revision(repo) if repo else None,
            "size_mb": size_mb(repo) if repo else None,
            "released": RELEASED.get(name),
            "ratio": {lg: v["ALL"] for lg, v in R.items()},
            "ci": r["ci95_vs_en"]["sk"],
            "cpt": C,
        })
    rows.sort(key=lambda x: x["ratio"]["sk"])
    names = {x["name"] for x in rows} | {a for x in rows for a in x["also"]}
    canon = {a: x["name"] for x in rows for a in [x["name"], *x["also"]]}
    price_rows = [{**p, "tokenizer": canon[p["tokenizer"]]} for p in prices["models"] if p["tokenizer"] in names]
    return {"tokenizers": rows, "prices": price_rows, "prices_as_of": prices["as_of"],
            "corpus": "FLORES-200 devtest (1012 sentences)"}


def _replace_element(page, attr, key, inner):
    """Replace the content of the one element carrying attr="key" (nested same-name tags allowed)."""
    m = re.search(rf'<(\w+)[^>]*\s{attr}="{key}"[^>]*>', page)
    if not m:
        raise KeyError(f'{attr}="{key}" not found in index.html')
    tag, pos, depth = m.group(1), m.end(), 1
    for t in re.finditer(rf"<(/?){tag}\b[^>]*>", page[pos:]):
        depth += -1 if t.group(1) else 1
        if depth == 0:
            return page[:pos] + inner + page[pos + t.start():]
    raise ValueError(f"unclosed <{tag}> for {key}")


def _sub_once(page, pattern, repl):
    new, n = re.subn(pattern, lambda _: repl, page, count=1)
    if n != 1:
        raise ValueError(f"pattern not found: {pattern}")
    return new


def render_en(page, en):
    """The English page (/en/) from the Slovak one: texts from en.json, URLs one level up."""
    head, body, attr = en["head"], en["body"], lambda v: html.escape(v, quote=True)
    page = _sub_once(page, r'<html lang="sk">', '<html lang="en">')
    page = _sub_once(page, r"<title>.*?</title>", f"<title>{html.escape(head['title'])}</title>")
    page = _sub_once(page, r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{attr(head["description"])}">')
    page = _sub_once(page, r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{attr(head["ogTitle"])}">')
    page = _sub_once(page, r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{attr(head["ogDescription"])}">')
    page = _sub_once(page, rf'<link rel="canonical" href="{BASE_URL}">', f'<link rel="canonical" href="{BASE_URL}en/">')
    page = _sub_once(page, rf'<meta property="og:url" content="{BASE_URL}">', f'<meta property="og:url" content="{BASE_URL}en/">')
    page = _sub_once(page, r'<meta property="og:locale" content="sk_SK">\n<meta property="og:locale:alternate" content="en_US">',
                     '<meta property="og:locale" content="en_US">\n<meta property="og:locale:alternate" content="sk_SK">')
    for f in ("style.css", "app.js", "tokenizer-timeline.png"):
        page = _sub_once(page, rf'(?:href|src)="{re.escape(f)}"', ('href' if f.endswith('.css') else 'src') + f'="../{f}"')
    page = _sub_once(page, r'<a href="./" hreflang="sk" lang="sk" data-lang-link aria-current="page">SK</a>',
                     '<a href="../" hreflang="sk" lang="sk" data-lang-link>SK</a>')
    page = _sub_once(page, r'<a href="en/" hreflang="en" lang="en" data-lang-link>EN</a>',
                     '<a href="./" hreflang="en" lang="en" data-lang-link aria-current="page">EN</a>')
    for key in re.findall(r'\sdata-i18n="(\w+)"', page):
        page = _replace_element(page, "data-i18n", key, html.escape(body[key], quote=False))
    for key in re.findall(r'\sdata-i18n-html="(\w+)"', page):
        page = _replace_element(page, "data-i18n-html", key, body[key])
    for key in re.findall(r'\sdata-i18n-alt="(\w+)"', page):
        page = re.sub(rf'(data-i18n-alt="{key}"[^>]*?\salt=)"[^"]*"', lambda m: m.group(1) + f'"{attr(body[key])}"', page, count=1)
    return page


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    for f in ("index.html", "app.js", "style.css", "robots.txt", "sitemap.xml"):
        shutil.copy(SITE / f, OUT / f)
    for img in ("social-preview.png", "tokenizer-timeline.png"):
        shutil.copy(ROOT / "docs" / img, OUT / img)
    en = json.loads((SITE / "en.json").read_text(encoding="utf-8"))
    (OUT / "en").mkdir()
    (OUT / "en" / "index.html").write_text(render_en((SITE / "index.html").read_text(encoding="utf-8"), en), encoding="utf-8")
    (OUT / "data.json").write_text(json.dumps(build_data(), ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (OUT / ".nojekyll").write_text("")
    print(f"built {OUT}")


if __name__ == "__main__":
    main()
