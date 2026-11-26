---
name: studio-capture
description: Get the demo film for an ED Narrator studio project: scripted Playwright browser capture, macOS screen recording, or an existing .mov/.mp4, saved in the input folder.
---

# Capture the demo

Ask which mode (an existing film, a scripted capture, a scene-marked feature tour, or a screen recording) with `AskUserQuestion` (numbered text without the tool), then do only that one. Ask what the capture needs in the same batch or in follow-ups: the URL (free text), the moments to show (`multiSelect` when the app's features are known), what must be hidden, and whether the data on screen is real. The result is a film in the **input folder** (`check_status` > `input_dirs`). ED Narrator accepts `.mp4`, `.m4v` and `.mov`.

Before recording: the screen will be filmed, so ask the user to close private windows, notifications and anything with names, keys or customer data.

## 1. An existing film

Copy it into the input folder (do not move the original). `ffprobe -v error -show_entries format=duration:stream=width,height -of csv=p=0 <file>` gives its length and size. Look at a few frames (`ffmpeg -i <file> -vf fps=1/6,scale=960:-1 frame_%02d.jpg` into a scratch folder) so the script and the motion match what is on screen.

## 2. Scripted browser capture (reproducible, no screen permission)

Needs Node. Ask for the URL and the steps (what to click, in order). Work in a scratch folder, not the input folder.

Copy `scripts/capture-simple.mjs` to the scratch folder, set the URL, add one step per line (move, click, pause) and run it with `node`. It draws a cursor (the video has none) and saves a `.webm` in `out/` when the context closes.

Then convert: `ffmpeg -i out/*.webm -c:v libx264 -pix_fmt yuv420p -r 30 -an <input folder>/demo.mp4`. If Playwright is missing, tell the user to run `npm i playwright && npx playwright install chromium` in the scratch folder; do not install it silently.

## 2b. Scene-marked feature tour (best for a walkthrough of several features)

One run records the whole tour as frames and marks where each feature starts and ends, so every feature becomes its own clip that the motion stage can speed up, slow down and point a camera at. Use `scripts/capture-tour.mjs` (copy it to a scratch folder, fill the steps, `node capture-tour.mjs`) and `scripts/cut-scenes.py <out> <clips dir>`, which writes one constant-30-fps `1920x1080` clip per mark plus `clips.json` (seconds per mark).

- **Brief first:** the 3 to 5 moments to show, in order, one mark each. Ask before capturing: the screen may show private data (see below).
- **Data must look real.** A tour of constraint dialogs, charts or results on garbled data shows absurd numbers (a nutrient mean of 0.0003, a Cpk in the tens of thousands). Check the data on screen first; if it is wrong, ask the user before seeding demo data or writing to any database. Read the numbers a dialog shows and type plausible limits from them, instead of hard-coding values.
- **Hide what must never appear** (savings, before and after cost, names, keys) with `MASK="saves|was|cost impact" node capture-tour.mjs`: matching text is hidden while recording. Tell the user what you hid.
- **Selectors:** text and role names, not CSS. Custom pickers render their options as plain elements, not `role=option`. On macOS select-all is `Meta+a`. Wrap optional steps in `soft(...)` so one missing control does not lose the whole tour, and read `fail.png` when a step fails.
- A download (an Excel export) is saved next to the frames; its real file name is in `meta.json` (`downloadName`) and can be shown in the film.
- Frames are recorded at 1600x900 with a device scale of 1.2: the UI is drawn larger and stays legible when the film is shrunk.

## 3. macOS screen recording

The user performs the demo. `screencapture -v -V <seconds> "<input folder>/demo.mov"` records the screen for that many seconds (add `-R x,y,w,h` for one region). It needs Screen Recording permission for the terminal app: if the file is blank or the command fails, say so and point to System Settings > Privacy & Security > Screen Recording. Give a 5-second warning before starting and tell the user when it ends.

## After capture

Report the file, its length and size, and one line on what is on screen. Hand over to `studio-motion`.
