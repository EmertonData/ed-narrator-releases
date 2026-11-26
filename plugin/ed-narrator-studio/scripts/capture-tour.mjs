// Scene-marked browser capture: a feature tour recorded as frames, one marked scene per feature.
// Usage: BASE_URL=http://localhost:3000 OUT=./out node capture-tour.mjs
// Needs: npm i playwright && npx playwright install chromium (ask the user first). Set PW_EXECUTABLE to use another Chromium.
// Output: OUT/frames/*.jpg + OUT/meta.json {frames:[{t,file}], END, marks:{name:{start,end}}}; then run cut-scenes.py.
import { chromium } from "playwright";
import fs from "node:fs";
import path from "node:path";

const BASE = process.env.BASE_URL ?? "http://localhost:3000";
const OUT = path.resolve(process.env.OUT ?? "./out");
const FR = path.join(OUT, "frames");
// 1600x900 at 1.2 = 1920x1080 frames, with the UI drawn 20% larger than a 1920 layout: it stays legible when the film is shrunk.
const VIEW = { width: 1600, height: 900 }, SCALE = 1.2;
// Text that must never appear in the film (savings, names, keys): any element whose text matches is hidden while the tour runs.
const MASK = process.env.MASK ? new RegExp(process.env.MASK, "i") : null;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
fs.rmSync(OUT, { recursive: true, force: true }); fs.mkdirSync(FR, { recursive: true });

const browser = await chromium.launch({ executablePath: process.env.PW_EXECUTABLE || undefined });
const ctx = await browser.newContext({ viewport: VIEW, deviceScaleFactor: SCALE, colorScheme: process.env.SCHEME ?? "light", acceptDownloads: true });
await ctx.addInitScript((maskSrc) => {
  // The screencast has no cursor: draw one, and hide tooltips (a cursor passing over a button must not raise one).
  addEventListener("DOMContentLoaded", () => {
    const d = document.createElement("div");
    d.style.cssText = "position:fixed;z-index:2147483647;width:22px;height:22px;pointer-events:none;transform:translate(-4px,-2px);left:-50px;top:-50px;transition:transform .08s";
    d.innerHTML = '<svg viewBox="0 0 24 24"><path d="M4 2 L4 19 L8.5 15 L11.5 22 L14 21 L11 14 L17 14 Z" fill="#fff" stroke="#000" stroke-width="1.2"/></svg>';
    document.body.append(d);
    addEventListener("mousemove", (e) => { d.style.left = e.clientX + "px"; d.style.top = e.clientY + "px"; }, true);
    addEventListener("mousedown", () => (d.style.transform = "translate(-4px,-2px) scale(.85)"), true);
    addEventListener("mouseup", () => (d.style.transform = "translate(-4px,-2px)"), true);
    const st = document.createElement("style"); st.textContent = '[role="tooltip"],[data-slot="tooltip-content"]{display:none !important}'; document.head.append(st);
    if (maskSrc) { const re = new RegExp(maskSrc, "i");
      const hide = () => { const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); for (let n = w.nextNode(); n; n = w.nextNode()) if (re.test(n.textContent || "") && n.parentElement) (n.parentElement.closest("td,th") ?? n.parentElement).style.visibility = "hidden"; };
      new MutationObserver(hide).observe(document, { childList: true, subtree: true, characterData: true }); setInterval(hide, 100); }
  });
}, MASK ? MASK.source : null);

const page = await ctx.newPage();
const cdp = await ctx.newCDPSession(page);
const frames = []; const marks = {}; let T0 = 0; const now = () => (Date.now() - T0) / 1000; let n = 0;
cdp.on("Page.screencastFrame", async (f) => {
  const file = path.join(FR, `${n++}.jpg`); fs.writeFileSync(file, Buffer.from(f.data, "base64")); frames.push({ t: now(), file });
  cdp.send("Page.screencastFrameAck", { sessionId: f.sessionId }).catch(() => {});
});

let mx = VIEW.width / 2, my = VIEW.height / 2;
const ease = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
const hold = (ms) => sleep(Math.round(ms * 0.7));
const moveTo = async (x, y, dur = 700) => {   // a curved, eased glide: a straight robot line reads as fake
  const dx = x - mx, dy = y - my, d = Math.hypot(dx, dy); if (d < 3) return;
  const steps = Math.round(Math.min(800, Math.max(400, dur * Math.min(1, d / 500 + 0.4))) / 16), bow = Math.min(60, d * 0.12) * (dx > 0 ? 1 : -1);
  for (let i = 1; i <= steps; i++) { const t = ease(i / steps), c = Math.sin(Math.PI * t) * bow; await page.mouse.move(mx + dx * t - (dy / d) * c, my + dy * t + (dx / d) * c); await sleep(6); }
  mx = x; my = y;
};
const click = async (loc, pause = 700) => {
  loc = loc.first(); await loc.waitFor({ state: "visible", timeout: 15000 }); await loc.scrollIntoViewIfNeeded();
  const b = await loc.boundingBox(); await moveTo(b.x + b.width / 2, b.y + b.height / 2);
  await page.mouse.click(b.x + b.width / 2, b.y + b.height / 2); await sleep(pause * 0.6);
};
const type = async (loc, text, delay = 80) => { await click(loc, 400); await page.keyboard.type(text, { delay }); };
const soft = async (fn, label) => { try { return await fn(); } catch (e) { console.log("SOFT FAIL", label, e.message.split("\n")[0]); } };
const mark = (name) => { marks[name] = { start: now() }; console.log("MARK", name, now().toFixed(1)); };
const endMark = (name) => { if (marks[name]) marks[name].end = now(); };
let downloadName = null; page.on("download", async (d) => { downloadName = d.suggestedFilename(); await d.saveAs(path.join(OUT, downloadName)).catch(() => {}); });

T0 = Date.now();
await cdp.send("Page.startScreencast", { format: "jpeg", quality: 88, maxWidth: 1920, maxHeight: 1080, everyNthFrame: 1 });
try {
  await page.goto(BASE, { waitUntil: "networkidle" }); await hold(900);

  // ===== EDIT HERE: one mark per feature, one step per line. Prefer text selectors (getByText / getByRole name) over CSS:
  // custom pickers often render options as plain elements, not role=option. On macOS select-all is Meta+a, not Control+a.
  // Read numbers off the screen to type plausible limits (see docs/motion-design-playbook.md, "Data").
  //
  // mark("search");
  //   await type(page.getByPlaceholder("Search..."), "milk"); await hold(1500);
  // endMark("search");
  void click; void type; void soft; void mark; void endMark;

} catch (e) { console.log("FAIL", e.stack); await page.screenshot({ path: path.join(OUT, "fail.png") }).catch(() => {}); }
const END = now();
await cdp.send("Page.stopScreencast").catch(() => {});
fs.writeFileSync(path.join(OUT, "meta.json"), JSON.stringify({ frames, END, marks, downloadName }));
await browser.close(); console.log("DONE", Object.keys(marks).join(","));
