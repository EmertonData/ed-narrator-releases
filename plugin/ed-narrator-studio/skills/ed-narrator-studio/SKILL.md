---
name: ed-narrator-studio
description: Make a narrated, animated demo of an app from start to finish with ED Narrator. Use when the user wants a product demo, walkthrough or promo video that is recorded (or already recorded), given motion design (2D, 3D or cinematic), narrated by a voice and mixed with background music. Orchestrates the studio-capture, studio-motion and studio-voice skills.
---

# ED Narrator studio

One film, four stages: **capture, motion, voice, music**. Each stage has its own skill; this one decides the order, asks the right questions once and keeps the files in the right folder.

## Before anything: one short brief

Ask these together, in one message, and use defaults for what the user skips:

1. **What** is the demo about, for **whom**, how long (default 30 to 60 s)?
2. **Capture:** record the app in a browser (scripted), record the Mac screen, or use a film they already have?
3. **Motion style:** 2D motion graphics, kinetic typography, 3D animation, cinematic motion picture, or minimal (see `studio-motion`). Also the aspect ratio (default 16:9) and colours (default: the app's own palette).
4. **Voice:** language and a voice (or "you choose"). Music: the path of an audio file, or none. Never fetch music yourself: licences are the user's call.

## Order of work

1. **`check_status`.** Not reachable: ask the user to open ED Narrator. No voice for the language: follow the install steps in `studio-voice`.
2. **Capture** (`studio-capture`). Result: one film in the input folder.
3. **Storyboard and approval** (`studio-motion`): list the shots, publish the animated storyboard artifact, and **wait for the user to approve the style** before rendering anything heavy.
4. **Motion render** (`studio-motion`): intro, callouts, outro, assembled into one silent film. Note the intro length: every script time is shifted by it.
5. **Script and voice** (`studio-voice`): write the `.srt` against the *composed* film, `preview_script`, fix tight lines, `create_voiceover` with `music_path` when the user gave a track, `wait_for_job`, `download_result`.
6. **Report** in a few lines: the style, the voice, the number of tight lines, the music used, and the output path.

## Rules

- Every input file (film, script, music) must sit inside the ED Narrator input folder (`check_status` shows `input_dirs`). Put captures and renders there, not in the home folder.
- Install a voice or engine only as `studio-voice` says: sizes and licences are shown to the user first, `confirm` is set only after the user's yes, and a licence is only ever accepted by the user in the app, never by you.
- ED Narrator replaces the film's original audio. Do not promise to keep it.
- The film may show private data (an internal tool, real recipes, names). Tell the user before capturing, and publish nothing (artifact or file) without their yes. Artifacts start private.
- Delete jobs only when asked. One film at a time; stop at the first failure and ask.
- Say what you did not verify (for example a render you did not watch back).
