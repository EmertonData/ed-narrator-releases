---
name: studio-motion
description: Add motion design to a demo film for an ED Narrator studio project, in a style the user chooses (2D motion graphics, kinetic typography, 3D animation, cinematic motion picture, minimal), and publish an animated storyboard artifact for approval. Use after capture and before voicing.
---

# Motion design and the motion artifact

The user **chooses the style**. Offer these and recommend one for the audience; do not pick silently.

| Style | What the viewer sees | How it is made |
|---|---|---|
| **2D motion graphics** | animated title card, highlight rings and zoom callouts on the UI, lower-thirds, end card | Remotion (React) renders the overlays and cards |
| **Kinetic typography** | the key lines of the script animate as type, timed to the cues | Remotion; one text scene per cue |
| **3D animation** | the recording playing on a 3D device or floating panel, camera moves, depth of field, a 3D logo reveal | Remotion with `@remotion/three` (Three.js or react-three-fiber) |
| **Cinematic motion picture** | letterbox 2.39:1, slow push-ins, fades, film grain, graded colour, a title sequence | ffmpeg filters (`pad`, `zoompan`, `curves`, `noise`, `fade`) on the film; cards from Remotion |
| **Minimal** | a short fade in and out only | ffmpeg `fade` |

Also ask: aspect ratio (16:9, 9:16 or 1:1), the colours and fonts (for ED Narrator use the tokens in `DESIGN.md`, never invented hex values), and the intro and outro length (default 3 s each).

If other motion skills are installed (`motion-design`, `remotion-video-creation`, `3dviz-pro-max`, `threejs-webgl`, `manim-video`), use them for the craft: timing, easing, composition. This skill only decides the flow.

## 1. Storyboard

Look at the film first (frames every few seconds). Write a shot list: timecode, what is on screen, the motion applied (title, zoom on the Models panel, callout, outro), and the on-screen text. Keep it to what the demo needs.

## 2. The motion artifact (animated storyboard)

Publish it so the user can approve the style before the heavy render. Call the Artifact tool's `quickstart` once, load the `artifact-design` skill, then publish one self-contained HTML page: the shots as a timeline with play and pause, the chosen style animated in CSS, SVG or canvas (a 3D style may use a small inline canvas scene), the palette and the text. It starts **private**; say so, and share nothing without a yes. Do not put private details from the film into it unless the user agreed.

**Stop here and wait for approval or changes.** A rejected style costs seconds now and minutes after rendering.

## 3. Render

Work in a scratch folder. Render each piece at the film's resolution, frame rate (`ffprobe` it) and `yuv420p`:

- Remotion: `npx create-video@latest` into the scratch folder (ask before installing anything), compositions for intro, callouts and outro, `npx remotion render <id> intro.mp4`. For 3D add `@remotion/three` and `three`.
- Cinematic: apply the filters to the film with ffmpeg, for example `-vf "scale=1920:-2,pad=1920:1080:0:(oh-ih)/2,zoompan=z='min(zoom+0.0004,1.08)':d=1,fade=in:0:20,fade=out:st=<end-1>:d=1"`.
- Check which filters this ffmpeg has before using one (`ffmpeg -filters | grep drawtext`): some builds have no `drawtext`, so draw text in Remotion instead.

Assemble: `ffmpeg -f concat -safe 0 -i list.txt -c:v libx264 -pix_fmt yuv420p -an composed.mp4` (intro, demo with overlays, outro; all the same size, fps and codec so concat is safe). Save `composed.mp4` in the ED Narrator **input folder**. The result is **silent on purpose**: ED Narrator replaces the film's audio.

## Hand over

Tell `studio-voice` the intro length in seconds (script times start after it) and the composed film's path. Say which part you checked (for example "played frames at 0, 5 and the end") and what you did not.
