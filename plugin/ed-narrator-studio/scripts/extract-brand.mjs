// Take the REAL brand from a running app instead of redrawing it: logo geometry, colour tokens and font files.
// Usage: node extract-brand.mjs <url> <logo svg selector> <out.json> [--dark]
// Writes {viewBox, shapes:[{d, fillRule, transform}], tokens:{"--primary":"#2525d4",...}, fonts:[{family,weight,src}]}.
// Render the logo with the shapes (kit: <Logo shapes viewBox fill/>); never trace it by eye or invent a lookalike.
import { chromium } from "playwright";
import fs from "node:fs";

const [url, selector, out] = process.argv.slice(2);
if (!url || !selector || !out) { console.error("usage: extract-brand.mjs <url> <svg selector> <out.json> [--dark]"); process.exit(2); }
if (!/^https?:\/\//i.test(url)) { console.error("url must be http(s)"); process.exit(2); }
const dark = process.argv.includes("--dark");
const browser = await chromium.launch({ executablePath: process.env.PW_EXECUTABLE || undefined });
const ctx = await browser.newContext({ viewport: { width: 1600, height: 900 }, colorScheme: dark ? "dark" : "light" });
const page = await ctx.newPage();
await page.goto(url, { waitUntil: "networkidle" }); await page.waitForTimeout(2000);
const data = await page.evaluate((sel) => {
  const svg = document.querySelector(sel);
  const shapes = svg ? [...svg.querySelectorAll("path")].map((p) => {
    const tf = []; for (let e = p; e && e !== svg; e = e.parentElement) if (e.getAttribute("transform")) tf.unshift(e.getAttribute("transform"));
    return { d: p.getAttribute("d"), fillRule: p.getAttribute("fill-rule") || undefined, transform: tf.join(" ") || undefined };
  }) : [];
  const tokens = {}, fonts = [];
  for (const sheet of document.styleSheets) { let rules; try { rules = sheet.cssRules; } catch { continue; }
    const walk = (list) => { for (const r of list) {
      if (r.type === CSSRule.STYLE_RULE && /^(:root|html|\.dark)\b/.test(r.selectorText || "")) for (const name of r.style) if (name.startsWith("--") && !(name in tokens)) tokens[name] = r.style.getPropertyValue(name).trim();
      else if (r.type === CSSRule.FONT_FACE_RULE) fonts.push({ family: r.style.getPropertyValue("font-family").replace(/["']/g, ""), weight: r.style.getPropertyValue("font-weight") || "400", src: r.style.getPropertyValue("src") });
      else if (r.cssRules) walk(r.cssRules); } };
    walk(rules); }
  // Vite and friends inject @font-face where the walker above cannot see it: the loaded faces are the reliable list.
  if (!fonts.length) for (const f of document.fonts) fonts.push({ family: f.family.replace(/["']/g, ""), weight: f.weight, src: null, status: f.status });
  return { viewBox: svg?.getAttribute("viewBox") ?? null, label: svg?.getAttribute("aria-label") ?? null, shapes, tokens, fonts };
}, selector);
await browser.close();
if (!data.shapes.length) { console.error(`no <path> found under "${selector}": check the selector`); process.exit(1); }
fs.writeFileSync(out, JSON.stringify(data, null, 1));
console.log(`${out}: ${data.shapes.length} shapes, ${Object.keys(data.tokens).length} tokens, ${data.fonts.length} font faces, viewBox ${data.viewBox}`);
