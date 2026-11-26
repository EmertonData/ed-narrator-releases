---
name: studio-voice
description: Voice a film with ED Narrator (one or two voices), mix background music, check the voice-to-music balance, and install voices or engines when none fits.
---

# Voice, music and model installs

If the `ed-narrator` connector tools are missing, tell the user to enable the plugin's connector (or open **Guide > Connect to Claude** in the app) and stop.

## 1. A voice that fits

`check_status`. Then `list_voices` for the script's language (filter by `provider` and `language`; the list is long). If there is none:

1. `list_installable` (with the language). **Piper voices** are about 65 MB and need no confirmation: recommend one and, on the user's yes, `install_voice_model(name="piper", voice_id=...)`.
2. **Heavier engines** (`kokoro` 2.4 GB, `pocket` 3.5 GB) only if the user wants more quality or a language Piper lacks. Call `install_voice_model` without `confirm` first: it returns the size and memory need and installs nothing. Tell the user those numbers and **ask** with `AskUserQuestion` (options: install, pick a lighter voice, cancel; numbered text without the tool). Only after a clear yes call again with `confirm=True`.
3. If an engine ever has a licence, the tool refuses and says so: send the user to **Models** in the app, where only they accept it. Never look for a way around it.
4. `wait_for_install` (repeat while it says still installing). If it fails, give the plain error. Then `list_voices` again.

Azure voices need a key typed into the app's Settings by the user. You never handle keys.

**Choose by context, and say which and why**, then let the user confirm or swap with `AskUserQuestion` (your pick first as "(Recommended)", two alternatives, "Other" for a voice id they know). Ask what else the voice needs in the same batch: one or two voices, the pace, words to pronounce a certain way, the music level; `multiSelect` for the pronunciations to fix. A calm, authoritative voice for scientific, enterprise or internal-tool films; a brighter, closer one for consumer launches; the accent the audience expects. Prefer the highest tier the engine offers (for Azure, the HD "Dragon" voices). Use only ids that `list_voices` returned.

**Two voices:** pass `second_voice` (same engine). The cues alternate voice by voice, starting with `voice`: write the script so each turn is one topic. A male and a female voice make the change obvious. One voice per cue is not configurable: reorder or merge cues instead.

## 2. The script

Write an `.srt` in the **input folder**, timed against the **composed** film: if the intro lasts 3 s, the first cue starts after 3 s. A safe pace is 2.5 words per second at most. `scripts/srt-from-timeline.mjs` builds the skeleton from the scene timeline and warns on fast cues. `preview_script` with `film_path`. If cues are **too long**, show them and shorten only those lines (keep numbers and timings, keep the meaning, show the change), then preview again. Do not render with flagged lines unless the user says so. Say acronyms the way they are spoken with `pronunciations` (for example `{"CPK": "C P K"}`).

## 3. Render, then check the mix

`create_voiceover(film_path, script_path, voice, second_voice?, provider?, music_path?, pronunciations?)`. Pass `music_path` **only** if the user gave a file (or you generated one with `scripts/make-bed.py` and the user agreed), inside the input folder. `quality="high"` only if they asked for lossless. `wait_for_job` until done, then `download_result` (the MP4 by default; `wav` is the narration alone).

**The app replaces the film's original audio** with the narration. With `music_path` the job reports `music: true` and the app stores the track, but the mix itself is computed in the app's browser (the **Music mix** panel), so a job driven only through the connector downloads narration-only audio, with silence between cues. Check what you got: run `scripts/check-mix.py <voiced film> <script.srt>`: it measures the voice against the music in every cue (5 dB or more is fine, under 3 dB is hard to follow). If the music is missing or too loud, download the narration `wav` and mix it yourself:

`scripts/mix-narration.sh <silent film> <narration.wav> <music> <out.mp4> [music_gain=0.26]` ducks the music under the voice and copies the video untouched. Lower the gain (0.2) and re-check until the worst margin is comfortable. Tell the user the mix is made outside the app when it is, and that opening the job in the app's **Music mix** panel is the other way to get a mix they can adjust.

## 4. Report

The voices and engine and why they were chosen, how many lines were too long, whether music was used and how it was mixed, the worst voice-to-music margin, and the saved path. Leave jobs alone unless asked to delete them.
