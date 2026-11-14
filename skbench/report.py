"""Markdown rendering: per-corpus RESULTS.md, COST.md and the README results block."""
import re

from .core import BASE

R = f"ratio_vs_{BASE}"
CI = f"ci95_vs_{BASE}"
README_START, README_END = "<!-- results:start -->", "<!-- results:end -->"
LANG_NAMES = {"sk": "Slovak", "cs": "Czech", "pl": "Polish", "hu": "Hungarian", "de": "German", "en": "English"}


def _table(hdr, rows):
    out = ["| " + " | ".join(hdr) + " |", "|" + "---|" * len(hdr)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def _x(v):
    return f"{v:.2f}×"


def _ci(v):
    return f"{v[0]:.2f}–{v[1]:.2f}"


def _by(results, lg):
    return sorted(results.items(), key=lambda kv: kv[1][R][lg]["ALL"])


def _identical_note(results):
    groups = {}
    for name, r in results.items():
        if r.get("same_as"):
            groups.setdefault(r["same_as"], [r["same_as"]]).append(name)
    if not groups:
        return ""
    return "\n*Byte-for-byte identical counts on this corpus: " + "; ".join(" = ".join(g) for g in groups.values()) + ".*\n"


def corpus_markdown(title, results, n_rows, langs):
    other = [lg for lg in langs if lg != BASE]
    domains = sorted(k for k in next(iter(results.values()))[R][other[0]] if k != "ALL")
    md = [f"# Results — {title}\n", f"{n_rows} parallel sentences, baseline = `{BASE}`. "
          "95 % CI = percentile bootstrap over sentences (2000 resamples).\n", "## Overall\n"]
    hdr = ["Tokenizer"] + [f"{lg} tokens" for lg in langs]
    hdr += [h for lg in other for h in (f"{lg}/{BASE}", "95 % CI")]
    hdr += [f"chars/token ({lg})" for lg in langs]
    rows = []
    for name, r in _by(results, other[0]):
        row = [name] + [r["tokens"][lg]["ALL"] for lg in langs]
        row += [c for lg in other for c in (_x(r[R][lg]["ALL"]), _ci(r[CI][lg]))]
        row += [f'{r["chars_per_token"][lg]:.2f}' for lg in langs]
        rows.append(row)
    md += [_table(hdr, rows), _identical_note(results)]
    for lg in other:
        md.append(f"\n## {lg}/{BASE} ratio by domain\n")
        md.append(_table(["Tokenizer"] + domains,
                         [[n] + [_x(r[R][lg][d]) for d in domains] for n, r in _by(results, lg)]))
    return "\n".join(md) + "\n"


def cost_rows(prices, results):
    rows = []
    for p in prices["models"]:
        r = results.get(p["tokenizer"])
        if not r:
            continue
        ratio = r[R]["sk"]["ALL"]
        rows.append({**p, "ratio": ratio, "eff_in": p["input"] * ratio, "eff_out": p["output"] * ratio})
    return sorted(rows, key=lambda x: x["eff_in"])


def cost_markdown(prices, results, corpus_label):
    rows = cost_rows(prices, results)
    md = ["# What Slovak costs, in dollars\n",
          f"List prices as of {prices['as_of']} (`prices.json`), token ratio from {corpus_label}. "
          "\"Effective\" = what the same content costs when it is written in Slovak, per 1M tokens' worth of English. "
          "The ratio applies to output too: a Slovak answer is as many times longer in tokens as a Slovak prompt.\n"]
    if not rows:
        return "\n".join(md + ["*No priced tokenizer was measured in this run.*\n"])
    md.append(_table(
        ["Vendor", "Model", "$ in / 1M", "$ out / 1M", "sk/en", "effective $ in", "effective $ out", "Slovak surcharge"],
        [[x["vendor"], f'`{x["model"]}`', f'{x["input"]:.2f}', f'{x["output"]:.2f}', _x(x["ratio"]),
          f'{x["eff_in"]:.2f}', f'{x["eff_out"]:.2f}', f'+{(x["ratio"] - 1) * 100:.0f} %'] for x in rows]))
    notes = [f'- `{x["model"]}`: {x["note"]}' for x in rows if x.get("note")]
    missing = sorted({p["tokenizer"] for p in prices["models"]} - set(results))
    if notes:
        md += ["\nNotes:\n"] + notes
    if missing:
        md.append("\n*Not measured in this run (API key not set and counts not cached): " + ", ".join(missing) + ".*")
    return "\n".join(md) + "\n"


def readme_block(flores, custom, prices):
    langs = [lg for lg in ["sk", "cs", "pl", "hu", "de"] if lg in next(iter(flores.values()))[R]]
    md = ["### Slovak vs English\n",
          "FLORES-200 devtest (1012 professionally translated sentences) with a 95 % bootstrap CI, "
          "and the hand-written 7-domain corpus for comparison.\n"]
    rows = []
    for name, r in _by(flores, "sk"):
        c = custom.get(name)
        rows.append([name, f'**{_x(r[R]["sk"]["ALL"])}**', _ci(r[CI]["sk"]),
                     _x(c[R]["sk"]["ALL"]) if c else "–",
                     f'{r["chars_per_token"]["sk"]:.2f}', f'{r["chars_per_token"]["en"]:.2f}'])
    md.append(_table(["Tokenizer", "sk/en", "95 % CI", "sk/en (domain corpus)", "chars/token sk", "chars/token en"], rows))
    md.append(_identical_note(flores))
    md += ["\n### Slovak and its neighbours\n",
           "Tokens per sentence relative to English on FLORES-200, same content in every column. "
           "Sorted by Slovak.\n"]
    md.append(_table(["Tokenizer"] + [LANG_NAMES[lg] for lg in langs],
                     [[n] + [_x(r[R][lg]["ALL"]) for lg in langs] for n, r in _by(flores, "sk")]))
    md += ["\n### In dollars\n", cost_markdown(prices, flores, "FLORES-200").split("\n", 2)[2]]
    return "\n".join(md)


def update_readme(path, block):
    text = path.read_text(encoding="utf-8")
    pat = re.compile(re.escape(README_START) + ".*?" + re.escape(README_END), re.S)
    if not pat.search(text):
        raise SystemExit(f"{path}: markers {README_START} / {README_END} not found")
    new = pat.sub(lambda _: f"{README_START}\n<!-- generated by `python bench.py --readme`; do not edit by hand -->\n\n{block}\n{README_END}", text)
    path.write_text(new, encoding="utf-8")
