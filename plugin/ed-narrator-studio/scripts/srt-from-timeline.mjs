// A script skeleton timed to the composed film, with a pacing check, from a scene timeline.
// Usage: node srt-from-timeline.mjs <timeline.json> <out.srt> [lead=1.0] [tail=0.8]
// timeline.json: [{"id":"intro","start":0,"end":5.6,"text":"..."}, ...] in seconds, the scene boundaries of the COMPOSED film
// (a scene text is spoken from start+lead to end-tail; no text = silent scene). Warns above 2.5 words per second.
import fs from "node:fs";
const [tl, out, lead = "1.0", tail = "0.8"] = process.argv.slice(2);
if (!tl || !out) { console.error("usage: srt-from-timeline.mjs <timeline.json> <out.srt> [lead] [tail]"); process.exit(2); }
const t = (s) => { const ms = Math.round(s * 1000), p = (n, w = 2) => String(n).padStart(w, "0"); return `${p(Math.floor(ms / 3600000))}:${p(Math.floor(ms / 60000) % 60)}:${p(Math.floor(ms / 1000) % 60)},${p(ms % 1000, 3)}`; };
const cues = JSON.parse(fs.readFileSync(tl, "utf8")).filter((s) => s.text);
let bad = 0;
const srt = cues.map((s, i) => {
  const a = s.start + Number(lead), b = s.end - Number(tail), words = s.text.trim().split(/\s+/).length, wps = words / (b - a);
  if (wps > 2.5) { bad++; console.warn(`cue ${i + 1} (${s.id}): ${wps.toFixed(1)} words/s over ${(b - a).toFixed(1)} s: shorten it`); }
  return `${i + 1}\n${t(a)} --> ${t(b)}\n${s.text.trim()}\n`;
}).join("\n");
fs.writeFileSync(out, srt); console.log(`${out}: ${cues.length} cues, ${bad} too fast`);
