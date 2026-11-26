// node capture-simple.mjs  (edit URL and the step lines first)
import { chromium } from "playwright";
import fs from "node:fs";
fs.rmSync("out", { recursive: true, force: true });   // a re-run must leave exactly one .webm
const b = await chromium.launch();
const ctx = await b.newContext({ viewport: { width: 1920, height: 1080 }, recordVideo: { dir: "out", size: { width: 1920, height: 1080 } } });
const page = await ctx.newPage();
await page.addInitScript(() => {            // the video has no cursor: draw one (#52b3e8 is the ED Narrator accent: use your app's)
  addEventListener("DOMContentLoaded", () => { const d = document.createElement("div");
    d.style.cssText = "position:fixed;z-index:99999;width:18px;height:18px;border-radius:50%;background:#52b3e8;opacity:.8;pointer-events:none;transform:translate(-50%,-50%)";
    document.body.append(d); addEventListener("mousemove", e => { d.style.left = e.clientX + "px"; d.style.top = e.clientY + "px"; }); }); });
await page.goto("URL");
await page.waitForTimeout(1500);
// one step per line, with a pause so it reads on screen:
//   await page.mouse.move(x, y, { steps: 25 }); await page.click("selector"); await page.waitForTimeout(1200);
await ctx.close(); await b.close();          // closing the context saves the .webm in out/
