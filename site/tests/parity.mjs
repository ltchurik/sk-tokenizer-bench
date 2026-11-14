// Count tokens with tokenizers.js (the library the web page uses) for every tokenizer and
// sentence listed in the input file. Driven by parity.py.
import { Tokenizer } from "@huggingface/tokenizers";
import fs from "node:fs";

const [input, output] = process.argv.slice(2);
const inp = JSON.parse(fs.readFileSync(input, "utf8"));
const res = {};
for (const [name, [tokJson, tokConfig]] of Object.entries(inp.tok)) {
  try {
    const tok = new Tokenizer(JSON.parse(fs.readFileSync(tokJson, "utf8")), JSON.parse(fs.readFileSync(tokConfig, "utf8")));
    res[name] = Object.fromEntries(
      Object.entries(inp.texts).map(([lg, texts]) => [lg, texts.map((t) => tok.encode(t, { add_special_tokens: false }).ids.length)])
    );
  } catch (e) {
    res[name] = { error: String(e).slice(0, 200) };
  }
}
fs.writeFileSync(output, JSON.stringify(res));
