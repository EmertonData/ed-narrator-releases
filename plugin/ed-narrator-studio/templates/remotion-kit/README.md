# Motion kit

A starter for the **motion** stage of a studio film: footage from `scripts/capture-tour.mjs` + `scripts/cut-scenes.py`, a camera rig, soft dissolves, understated lower-thirds, the app's real logo and fonts. Brand-neutral: set `theme` in `src/kit.tsx` from `scripts/extract-brand.mjs`.

```bash
cp -r templates/remotion-kit ~/scratch/film && cd ~/scratch/film     # a scratch folder, never the input folder
npm install                                                           # ask the user first; Remotion is source-available: check its licence for commercial use
cp <clips folder>/*.mp4 public/clips/ && cp <clips folder>/clips.json src/
npm run still                                                         # one frame: look at it before rendering anything
npm run render                                                        # ~0.3 s per frame; keep the film silent: ED Narrator replaces the audio
```

Edit `DEFS` in `src/Demo.tsx`: one row per beat (id = the capture mark, duration in frames, caption, camera keys). Point the camera at what the viewer must read: keep zoom at or under about 1.6 on 1080p footage, hold still between moves. `Stage` clamps the focus so the footage always covers the screen (no black bands), and never zooms out below 1.

## Gotchas (all hit for real)

- **Remotion's own Chromium may refuse to start** (`spawn Unknown system error -88`): pass any Chrome/Chromium with `--browser-executable=<path>` (Playwright's headless shell works).
- **TypeScript must be 5.x**: the newest major breaks Remotion's bundler (`Cannot read properties of undefined (reading 'readFile')`). `package.json` pins it.
- **Stop a stray render** with `pkill -f "[r]emotion render"` (the bracket stops the command from matching and killing its own shell).
- **Check every render before you hand it over:** `scripts/scan-pops.py` (single-frame pops, hard cuts), `scripts/contact-sheet.sh`, `scripts/transition-strip.sh`.
