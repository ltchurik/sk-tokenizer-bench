import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "site"))
from build import BASE_URL, render_en  # noqa: E402

SK = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
EN_TEXTS = json.loads((ROOT / "site" / "en.json").read_text(encoding="utf-8"))
EN = render_en(SK, EN_TEXTS)


def test_every_translatable_element_has_an_english_text():
    keys = set(re.findall(r'\sdata-i18n(?:-html|-alt)?="(\w+)"', SK))
    assert keys == set(EN_TEXTS["body"]), keys ^ set(EN_TEXTS["body"])


def test_english_page_is_english():
    assert '<html lang="en">' in EN and f'<link rel="canonical" href="{BASE_URL}en/">' in EN
    assert '<h1 data-i18n="h1">How many tokens does Slovak cost?</h1>' in EN
    assert f'<meta property="og:image" content="{BASE_URL}social-preview.png">' in EN
    assert f'<meta property="og:image" content="{BASE_URL}social-preview-sk.png">' in SK
    assert 'aria-current="page">EN</a>' in EN and 'src="../app.js"' in EN and 'href="../style.css"' in EN
    body = EN[EN.index("<body>"):]  # the JSON-LD in <head> describes the one app and stays shared
    for slovak in ("Koľko tokenov", "Prečo slovenčina", "Vložte slovenský", "Dáta:", "Graf:"):
        assert slovak not in body


def test_both_pages_declare_the_same_alternates():
    alternates = re.findall(r'<link rel="alternate" hreflang="[\w-]+" href="[^"]+">', SK)
    assert len(alternates) == 3
    assert alternates == re.findall(r'<link rel="alternate" hreflang="[\w-]+" href="[^"]+">', EN)
