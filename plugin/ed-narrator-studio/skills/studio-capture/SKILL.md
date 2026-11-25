---
name: studio-capture
description: Get the demo film for an ED Narrator studio project. Use when a recording of an app is needed: scripted browser capture with Playwright, macOS screen recording, or an existing .mov/.mp4. Produces one .mp4 or .mov in the ED Narrator input folder.
---

# Capture the demo

Ask which of the three modes, then do only that one. The result is a film in the **input folder** (`check_status` > `input_dirs`). ED Narrator accepts `.mp4`, `.m4v` and `.mov`.

Before recording: the screen will be filmed, so ask the user to close private windows, notifications and anything with names, keys or customer data.

## 1. An existing film

Copy it into the input folder (do not move the original). `ffprobe -v error -show_entries format=duration:stream=width,height -of csv=p=0 <file>` gives its length and size. Look at a few frames (`ffmpeg -i <file> -vf fps=1/6,scale=960:-1 frame_%02d.jpg` into a scratch folder) so the script and the motion match what is on screen.

## 2. Scripted browser capture (reproducible, no screen permission)

Needs Node. Ask for the URL and the steps (what to click, in order). Write a small script in a scratch folder (not the input folder) and run it with `node`:

```js
// capture.mjs: node capture.mjs
import { chromium } from "playwright";
const b = await chromium.launch();
const ctx = await b.newContext({ viewport: { width: 1920, height: 1080 }, recordVideo: { dir: "out", size: { width: 1920, height: 1080 } } });
const page = await ctx.newPage();
await page.addInitScript(() => {            // the video has no cursor: draw one
  addEventListener("DOMContentLoaded", () => { const d = document.createElement("div");
    d.style.cssText = "position:fixed;z-index:99999;width:18px;height:18px;border-radius:50%;background:#52b3e8;opacity:.8;pointer-events:none;transform:translate(-50%,-50%)";
    document.body.append(d); addEventListener("mousemove", e => { d.style.left = e.clientX + "px"; d.style.top = e.clientY + "px"; }); }); });
await page.goto("URL");
await page.waitForTimeout(1500);
// one step per line, with a pause so it reads on screen:
//   await page.mouse.move(x, y, { steps: 25 }); await page.click("selector"); await page.waitForTimeout(1200);
await ctx.close(); await b.close();          // closing the context saves the .webm in out/
```

Then convert: `ffmpeg -i out/*.webm -c:v libx264 -pix_fmt yuv420p -r 30 -an <input folder>/demo.mp4`. If Playwright is missing, tell the user to run `npm i playwright && npx playwright install chromium` in the scratch folder; do not install it silently.

## 3. macOS screen recording

The user performs the demo. `screencapture -v -V <seconds> "<input folder>/demo.mov"` records the screen for that many seconds (add `-R x,y,w,h` for one region). It needs Screen Recording permission for the terminal app: if the file is blank or the command fails, say so and point to System Settings > Privacy & Security > Screen Recording. Give a 5-second warning before starting and tell the user when it ends.

## After capture

Report the file, its length and size, and one line on what is on screen. Hand over to `studio-motion`.
