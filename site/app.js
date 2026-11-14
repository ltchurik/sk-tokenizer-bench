// sk-tokenizer-bench web calculator. Everything runs in the browser; tokenizers are fetched
// from the Hugging Face Hub on demand and counted with tokenizers.js, which CI checks for
// exact parity with the Python benchmark on all FLORES sentences.
import { Tokenizer } from "https://cdn.jsdelivr.net/npm/@huggingface/tokenizers@0.2.0/dist/tokenizers.min.mjs";

const SAMPLE_SK =
  "Dobrý deň, chcel by som sa opýtať, či je možné zmeniť termín mojej objednávky. Pôvodne som si rezervoval doručenie na štvrtok, ale v ten deň nebudem doma. Vyhovoval by mi piatok popoludní alebo budúci pondelok. Ďakujem za odpoveď a prajem pekný deň.";
const SAMPLE_EN =
  "Hello, I would like to ask whether it is possible to change the date of my order. I originally booked delivery for Thursday, but I will not be home that day. Friday afternoon or next Monday would suit me. Thank you for your reply and have a nice day.";
const DEFAULT_EXACT = "GPT-4o / 4.1 / 5 (o200k_base)";
const VIZ_LIMIT = 600;

const T = {
  sk: {
    h1: "Koľko tokenov stojí slovenčina?",
    lead: "Jazykové modely účtujú za tokeny a tokenizéry sa učili hlavne na angličtine. Vložte slovenský text a uvidíte, koľko tokenov a peňazí stojí v jednotlivých modeloch a o koľko viac to je oproti rovnakému textu po anglicky.",
    privacy: "Všetko sa počíta vo vašom prehliadači. Text nikam neodchádza.",
    skLabel: "Slovenský text", sample: "Vložiť ukážku", clear: "Vymazať",
    enSummary: "Mám aj anglickú verziu (presné porovnanie)", enLabel: "Ten istý text po anglicky",
    enHint: "Bez anglickej verzie sa porovnanie odhaduje podľa pomeru nameraného na 1012 vetách korpusu FLORES-200.",
    costH: "Cena za 1 000 takýchto textov", resH: "Tokeny podľa tokenizéra", vizH: "Ako tokenizér delí text", vizPick: "Tokenizér",
    resNote: "Čísla s <b>≈</b> sú odhad z nameraného počtu znakov na token. Kliknutím na <b>Spočítať presne</b> sa tokenizér stiahne z Hugging Face (raz, potom ho má prehliadač uložený) a text sa spočíta presne, rovnako ako v benchmarku.",
    vizNote: "Každý farebný úsek je jeden token. Prerušovaný rámik znamená, že jeden znak (napr. ľ alebo ô) sa rozdelil do viacerých tokenov.",
    whyH: "Prečo slovenčina stojí viac?",
    stats: (c, w) => `${fmtInt(c)} znakov · ${fmtInt(w)} slov`,
    empty: "Vložte text a uvidíte, koľko tokenov stojí.",
    headline: (m, n, e, p) => `Na <b>${m}</b> má tento text <b>${n}</b> tokenov. Rovnaký obsah po anglicky by mal ${e} tokenov, teda platíte o <b>${p}</b> viac.`,
    headlineLess: (m, n, e, p) => `Na <b>${m}</b> má tento text <b>${n}</b> tokenov, po anglicky ${e}, teda o <b>${p}</b> menej.`,
    subline: (nd, p, src) => `Bez diakritiky by mal ${nd} tokenov (${p}). Porovnanie s angličtinou: ${src}.`,
    exactEn: "presne podľa vašej anglickej verzie", floresEn: "odhad podľa korpusu FLORES-200",
    costNote: (d) => `Vstupné tokeny podľa cenníkov k ${d}. Výstup (odpoveď modelu) je po slovensky dlhší v rovnakom pomere.`,
    thTok: "Tokenizér", thTokens: "Tokeny", thNd: "Bez diakritiky", thRatio: "Oproti angličtine", thStatus: "",
    thModel: "Model", thSk: "Po slovensky", thEn: "Po anglicky", thExtra: "Navyše",
    groups: { mainstream: "Bežné modely", multilingual: "Viacjazyčné modely", regional: "Regionálne (SK / CZ / PL)", api: "Cez API (namerané v benchmarku)" },
    exactBtn: (mb) => `Spočítať presne${mb ? ` · ${fmtMb(mb)}` : ""}`, loading: "Načítavam…", exact: "presne", failed: "nepodarilo sa", estOnly: "len odhad",
    loadAll: (mb) => `Spočítať presne všetky (${fmtInt(mb)} MB)`, loadAllBusy: (k, n) => `Načítavam ${k} / ${n}…`, allDone: "Všetky spočítané presne",
    vizLoadHint: "Tokenizér sa načítava…", vizTrunc: (n) => `Zobrazených prvých ${n} tokenov.`, vizCount: (n) => `${fmtInt(n)} tokenov`,
    noPrice: "Ceny sú k dispozícii pre modely, ktorých tokenizér je zmeraný.",
    also: "rovnaký ako", tokens: "tokenov",
  },
  en: {
    h1: "How many tokens does Slovak cost?",
    lead: "Language models bill per token, and tokenizers were trained mostly on English. Paste Slovak text to see how many tokens and how much money it costs in each model, and how much more that is than the same text in English.",
    privacy: "Everything runs in your browser. Your text never leaves it.",
    skLabel: "Slovak text", sample: "Insert sample", clear: "Clear",
    enSummary: "I also have the English version (exact comparison)", enLabel: "The same text in English",
    enHint: "Without an English version the comparison is estimated from the ratio measured on 1012 FLORES-200 sentences.",
    costH: "Cost per 1,000 texts like this", resH: "Tokens by tokenizer", vizH: "How the tokenizer splits your text", vizPick: "Tokenizer",
    resNote: "Numbers with <b>≈</b> are estimates from the measured characters per token. <b>Count exactly</b> downloads the tokenizer from Hugging Face (once; your browser caches it) and counts your text exactly, the same way as the benchmark.",
    vizNote: "Each coloured span is one token. A dashed outline means a single character (such as ľ or ô) was split across several tokens.",
    whyH: "Why does Slovak cost more?",
    stats: (c, w) => `${fmtInt(c)} characters · ${fmtInt(w)} words`,
    empty: "Paste some text to see what it costs.",
    headline: (m, n, e, p) => `On <b>${m}</b> this text is <b>${n}</b> tokens. The same content in English would be ${e} tokens, so you pay <b>${p}</b> more.`,
    headlineLess: (m, n, e, p) => `On <b>${m}</b> this text is <b>${n}</b> tokens and ${e} in English, so <b>${p}</b> less.`,
    subline: (nd, p, src) => `Without diacritics it would be ${nd} tokens (${p}). English comparison: ${src}.`,
    exactEn: "exact, from your English version", floresEn: "estimated from FLORES-200",
    costNote: (d) => `Input tokens at list prices as of ${d}. Output (the model's answer) is longer in Slovak by the same factor.`,
    thTok: "Tokenizer", thTokens: "Tokens", thNd: "No diacritics", thRatio: "vs English", thStatus: "",
    thModel: "Model", thSk: "In Slovak", thEn: "In English", thExtra: "Extra",
    groups: { mainstream: "Mainstream models", multilingual: "Multilingual models", regional: "Regional (SK / CZ / PL)", api: "API only (measured in the benchmark)" },
    exactBtn: (mb) => `Count exactly${mb ? ` · ${fmtMb(mb)}` : ""}`, loading: "Loading…", exact: "exact", failed: "failed", estOnly: "estimate only",
    loadAll: (mb) => `Count all exactly (${fmtInt(mb)} MB)`, loadAllBusy: (k, n) => `Loading ${k} / ${n}…`, allDone: "All counted exactly",
    vizLoadHint: "Loading tokenizer…", vizTrunc: (n) => `Showing the first ${n} tokens.`, vizCount: (n) => `${fmtInt(n)} tokens`,
    noPrice: "Prices are shown for models whose tokenizer is measured.",
    also: "same as", tokens: "tokens",
  },
};

let lang = (navigator.language || "sk").toLowerCase().startsWith("sk") || (navigator.language || "").toLowerCase().startsWith("cs") ? "sk" : "en";
const $ = (id) => document.getElementById(id);
const t = (k) => T[lang][k];
const fmtInt = (n) => Math.round(n).toLocaleString(lang === "sk" ? "sk-SK" : "en-US");
const fmtX = (r) => r.toLocaleString(lang === "sk" ? "sk-SK" : "en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + "×";
const fmtMb = (mb) => mb.toLocaleString(lang === "sk" ? "sk-SK" : "en-US", { maximumFractionDigits: 1 }) + " MB";
const fmtPct = (r) => `${Math.round(Math.abs(r - 1) * 100)} %`;
const fmtUsd = (v) => "$" + v.toLocaleString("en-US", { minimumFractionDigits: v < 1 ? 3 : 2, maximumFractionDigits: v < 1 ? 3 : 2 });
const chars = (s) => Array.from(s).length;
const words = (s) => (s.trim().match(/\S+/g) || []).length;
const stripDiacritics = (s) => s.normalize("NFD").replace(/\p{M}/gu, "").normalize("NFC");
const shortName = (n) => n.replace(/ \((?:o200k_base|cl100k_base|legacy, Xenova mirror|tekken)\)/, "");

let DATA = null;
const tokCache = new Map(); // name -> {state: "loading"|"ready"|"error", tok, promise}

// ---------------------------------------------------------------------------------------
async function loadTokenizer(row) {
  const have = tokCache.get(row.name);
  if (have) return have.promise;
  const base = `https://huggingface.co/${row.repo}/resolve/main/`;
  const entry = { state: "loading" };
  entry.promise = (async () => {
    try {
      const [tj, tc] = await Promise.all(
        ["tokenizer.json", "tokenizer_config.json"].map((f) => fetch(base + f).then((r) => { if (!r.ok) throw new Error(r.status); return r.json(); }))
      );
      entry.tok = new Tokenizer(tj, tc);
      entry.state = "ready";
    } catch (e) {
      console.error(row.name, e);
      entry.state = "error";
    }
    render();
    return entry;
  })();
  tokCache.set(row.name, entry);
  render();
  return entry.promise;
}

const ready = (row) => tokCache.get(row.name)?.state === "ready";
const count = (row, text) => tokCache.get(row.name).tok.encode(text, { add_special_tokens: false }).ids.length;

function measure(row, sk, en) {
  const nd = stripDiacritics(sk);
  const exact = ready(row);
  const skTok = exact ? count(row, sk) : chars(sk) / row.cpt.sk;
  const ndTok = exact ? count(row, nd) : chars(nd) / row.cpt.sk_nd;
  let enTok, enExact = false;
  if (en.trim()) {
    enTok = exact ? count(row, en) : chars(en) / row.cpt.en;
    enExact = exact;
  } else {
    enTok = skTok / row.ratio.sk;
  }
  return { exact, skTok, ndTok, enTok, enExact, ratio: enTok > 0 ? skTok / enTok : row.ratio.sk };
}

// ---------------------------------------------------------------------------------------
function renderHeadline(sk, en) {
  if (!sk.trim()) { $("headline").innerHTML = t("empty"); $("subline").textContent = ""; return; }
  const row = DATA.tokenizers.find((r) => r.name === DEFAULT_EXACT);
  const m = measure(row, sk, en);
  const pre = m.exact ? "" : "≈ ";
  const preEn = m.enExact ? "" : "≈ ";
  const fn = m.ratio >= 1 ? t("headline") : t("headlineLess");
  $("headline").innerHTML = fn("GPT-4o / GPT-5", pre + fmtInt(m.skTok), preEn + fmtInt(m.enTok), fmtPct(m.ratio));
  const saved = m.ndTok / m.skTok;
  $("subline").textContent = t("subline")(pre + fmtInt(m.ndTok), (saved <= 1 ? "−" : "+") + fmtPct(saved), m.enExact ? t("exactEn") : t("floresEn"));
}

function renderCost(sk, en) {
  $("cost-note").textContent = t("costNote")(DATA.prices_as_of);
  const tbl = $("cost");
  const rows = DATA.prices.map((p) => {
    const row = DATA.tokenizers.find((r) => r.name === p.tokenizer);
    return { p, row, m: measure(row, sk, en) };
  }).sort((a, b) => a.p.input * a.m.skTok - b.p.input * b.m.skTok);
  if (!sk.trim() || !rows.length) { tbl.innerHTML = `<tr><td class="muted">${!rows.length ? t("noPrice") : t("empty")}</td></tr>`; return; }
  const head = `<thead><tr><th>${t("thModel")}</th><th class="num">${t("thSk")}</th><th class="num">${t("thEn")}</th><th class="num">${t("thExtra")}</th></tr></thead>`;
  const body = rows.map(({ p, m }) => {
    const sk$ = (m.skTok * p.input / 1e6) * 1000, en$ = (m.enTok * p.input / 1e6) * 1000;
    const est = m.exact ? "" : "≈ ";
    return `<tr><td><span class="name">${p.model}</span> <span class="also">${p.vendor}</span></td>
      <td class="num">${est}${fmtUsd(sk$)}</td><td class="num">${m.enExact ? "" : "≈ "}${fmtUsd(en$)}</td>
      <td class="num">+${fmtUsd(Math.max(0, sk$ - en$))}</td></tr>`;
  }).join("");
  tbl.innerHTML = head + `<tbody>${body}</tbody>`;
}

function renderResults(sk, en) {
  const maxR = 2.6;
  const head = `<thead><tr><th>${t("thTok")}</th><th class="num">${t("thTokens")}</th><th class="num hide-sm">${t("thNd")}</th>
    <th class="ratio-cell">${t("thRatio")}</th><th class="num">${t("thStatus")}</th></tr></thead>`;
  let body = "", lastGroup = null;
  for (const row of DATA.tokenizers) {
    if (row.group !== lastGroup) { body += `<tr class="group"><td colspan="5">${t("groups")[row.group]}</td></tr>`; lastGroup = row.group; }
    const m = measure(row, sk, en);
    const est = m.exact ? "" : `<span class="est">≈ </span>`;
    const also = row.also.length ? `<span class="also">= ${row.also.map(shortName).join(", ")}</span>` : "";
    const entry = tokCache.get(row.name);
    let status = `<span class="exact-badge">${t("estOnly")}</span>`;
    if (row.repo) {
      if (!entry) status = `<button class="btn" data-load="${encodeURIComponent(row.name)}">${t("exactBtn")(row.size_mb)}</button>`;
      else if (entry.state === "loading") status = `<span class="exact-badge">${t("loading")}</span>`;
      else if (entry.state === "ready") status = `<span class="exact-badge">✓ ${t("exact")}</span>`;
      else status = `<span class="exact-badge">${t("failed")}</span>`;
    }
    const w = Math.min(m.ratio, maxR) / maxR * 100, one = 1 / maxR * 100;
    body += `<tr><td><span class="name">${shortName(row.name)}</span>${also}</td>
      <td class="num">${sk.trim() ? est + fmtInt(m.skTok) : "–"}</td>
      <td class="num hide-sm">${sk.trim() ? est + fmtInt(m.ndTok) : "–"}</td>
      <td class="ratio-cell"><span class="bar-label">${fmtX(m.ratio)}</span>
        <div class="bar" role="img" aria-label="${fmtX(m.ratio)}"><i style="width:${w}%"></i><s style="left:${one}%"></s></div></td>
      <td class="num">${status}</td></tr>`;
  }
  $("results").innerHTML = head + `<tbody>${body}</tbody>`;

  const pending = DATA.tokenizers.filter((r) => r.repo && !tokCache.has(r.name));
  const btn = $("load-all");
  if (!pending.length) {
    const busy = DATA.tokenizers.filter((r) => tokCache.get(r.name)?.state === "loading").length;
    btn.disabled = true;
    btn.textContent = busy ? t("loadAllBusy")(DATA.tokenizers.filter((r) => ready(r)).length, DATA.tokenizers.filter((r) => r.repo).length) : t("allDone");
  } else {
    btn.disabled = false;
    btn.textContent = t("loadAll")(pending.reduce((s, r) => s + (r.size_mb || 0), 0));
  }
}

// Split the decoded text into one span per token; tokens that only decode together (a
// multi-byte character split across byte-level tokens) are merged and outlined.
function segments(tok, ids) {
  const out = [];
  let start = 0, prev = "";
  for (let i = 0; i < ids.length; i++) {
    const cur = tok.decode(ids.slice(0, i + 1), { skip_special_tokens: false, clean_up_tokenization_spaces: false });
    if (cur.endsWith("�") && i < ids.length - 1) continue;
    let k = 0;
    while (k < prev.length && k < cur.length && prev[k] === cur[k]) k++;
    out.push({ text: cur.slice(k), n: i + 1 - start });
    start = i + 1;
    prev = cur;
  }
  return out;
}

function renderViz(sk) {
  const pick = $("viz-pick");
  const row = DATA.tokenizers.find((r) => r.name === pick.value);
  const box = $("viz");
  box.textContent = "";
  if (!row || !sk.trim()) return;
  if (!ready(row)) { box.textContent = t("vizLoadHint"); loadTokenizer(row); return; }
  const entry = tokCache.get(row.name);
  const ids = entry.tok.encode(sk, { add_special_tokens: false }).ids;
  const segs = segments(entry.tok, ids.slice(0, VIZ_LIMIT));
  segs.forEach((s, i) => {
    const span = document.createElement("span");
    span.className = `k${i % 5}` + (s.n > 1 ? " split" : "");
    span.textContent = s.text;
    if (s.n > 1) span.title = `${s.n} ${t("tokens")}`;
    box.appendChild(span);
  });
  const meta = document.createElement("div");
  meta.className = "viz-meta";
  meta.textContent = t("vizCount")(ids.length) + (ids.length > VIZ_LIMIT ? " · " + t("vizTrunc")(VIZ_LIMIT) : "");
  box.after(meta);
}

let raf = 0;
function render() {
  cancelAnimationFrame(raf);
  raf = requestAnimationFrame(() => {
    const sk = $("sk").value, en = $("en").value;
    $("stats").textContent = t("stats")(chars(sk), words(sk));
    document.querySelectorAll(".viz-meta").forEach((n) => n.remove());
    renderHeadline(sk, en);
    renderCost(sk, en);
    renderResults(sk, en);
    renderViz(sk);
  });
}

// ---------------------------------------------------------------------------------------
function applyLang() {
  document.documentElement.lang = lang;
  document.querySelectorAll("[data-i18n]").forEach((n) => { const v = T[lang][n.dataset.i18n]; if (typeof v === "string") n.textContent = v; });
  document.querySelectorAll("[data-i18n-html]").forEach((n) => {
    const v = T[lang][n.dataset.i18nHtml];
    if (typeof v === "string") n.innerHTML = v;
    else if (!n.dataset.orig) n.dataset.orig = n.innerHTML; // keep the static Slovak prose for SEO
  });
  document.querySelectorAll("[data-set-lang]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.setLang === lang)));
  render();
}

async function main() {
  DATA = await fetch("data.json").then((r) => r.json());
  const GROUP_ORDER = ["mainstream", "multilingual", "regional", "api"];
  DATA.tokenizers.sort((a, b) => GROUP_ORDER.indexOf(a.group) - GROUP_ORDER.indexOf(b.group) || a.ratio.sk - b.ratio.sk);
  T.en.why = `<p>A tokenizer cuts text into pieces (tokens) using a vocabulary learned from its training data. That data is mostly English, so common English words are one token while Slovak words, with their diacritics and many forms (<i>mesto, mesta, mestu, mestom, mestách</i>), break into several pieces. Every token is billed and takes up room in the context window.</p>
<ul><li><b>Mainstream models:</b> Slovak needs 1.6× to 2.3× the tokens of English (GPT-4o / GPT-5 1.68×, Llama 4 1.56×, GPT-4 2.13×).</li>
<li><b>Diacritics are not the main problem:</b> dropping them saves only 1–5 % of tokens on modern models.</li>
<li><b>It is about training data:</b> SlovakBERT, trained on Slovak, needs fewer tokens for Slovak than for English.</li></ul>
<p>Full benchmark, methodology and results for 10 languages: <a href="https://github.com/ltchurik/sk-tokenizer-bench">github.com/ltchurik/sk-tokenizer-bench</a>.</p>`;
  T.sk.why = document.querySelector("[data-i18n-html=why]").innerHTML;
  T.en.foot = `Data: <a href="https://github.com/ltchurik/sk-tokenizer-bench">sk-tokenizer-bench</a> · FLORES-200 corpus (CC BY-SA 4.0) · official list prices · tokenizers from Hugging Face via <a href="https://github.com/huggingface/tokenizers.js">tokenizers.js</a> · <a href="https://doi.org/10.5281/zenodo.24092040">DOI 10.5281/zenodo.24092040</a> · MIT`;
  T.sk.foot = document.querySelector("[data-i18n-html=foot]").innerHTML;

  const pick = $("viz-pick");
  DATA.tokenizers.filter((r) => r.repo).forEach((r) => pick.add(new Option(shortName(r.name) + (r.size_mb ? ` (${fmtMb(r.size_mb)})` : ""), r.name)));
  pick.value = DEFAULT_EXACT;

  $("sk").value = SAMPLE_SK;
  let timer;
  for (const id of ["sk", "en"]) $(id).addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(render, 150); });
  $("sample").onclick = () => { $("sk").value = SAMPLE_SK; $("en").value = SAMPLE_EN; $("en-box").open = true; render(); };
  $("clear").onclick = () => { $("sk").value = ""; $("en").value = ""; render(); $("sk").focus(); };
  pick.onchange = render;
  $("results").addEventListener("click", (e) => {
    const b = e.target.closest("[data-load]");
    if (b) loadTokenizer(DATA.tokenizers.find((r) => r.name === decodeURIComponent(b.dataset.load)));
  });
  $("load-all").onclick = async () => {
    for (const r of DATA.tokenizers.filter((r) => r.repo && !tokCache.has(r.name))) await loadTokenizer(r);
  };
  document.querySelectorAll("[data-set-lang]").forEach((b) => (b.onclick = () => { lang = b.dataset.setLang; applyLang(); }));

  applyLang();
  loadTokenizer(DATA.tokenizers.find((r) => r.name === DEFAULT_EXACT));
}

main();
