---
name: studio-voice
description: Voice a film with ED Narrator and mix background music, and install voices or engines when none fits. Use when a script must be narrated onto a film, music (an mp3 or other audio file) must go under it, or no voice is installed for the language.
---

# Voice, music and model installs

Tools of the `ed-narrator` connector: `check_status`, `list_voices`, `list_installable`, `install_voice_model`, `wait_for_install`, `preview_script`, `create_voiceover`, `wait_for_job`, `get_job`, `download_result`, `list_jobs`, `delete_job`. If they are missing, tell the user to enable the plugin's connector (or open **Guide > Connect to Claude** in the app) and stop.

## 1. A voice that fits

`check_status`. Then `list_voices` for the script's language. If there is none:

1. `list_installable` (with the language). **Piper voices** are about 65 MB and need no confirmation: recommend one and, on the user's yes, `install_voice_model(name="piper", voice_id=...)`.
2. **Heavier engines** (`kokoro` 2.4 GB, `pocket` 3.5 GB) only if the user wants more quality or a language Piper lacks. Call `install_voice_model` without `confirm` first: it returns the size and memory need and installs nothing. Tell the user those numbers and **ask**. Only after a clear yes call again with `confirm=True`.
3. If an engine ever has a licence, the tool refuses and says so: send the user to **Models** in the app, where only they accept it. Never look for a way around it.
4. `wait_for_install` (repeat while it says still installing). If it fails, give the plain error. Then `list_voices` again.

Azure voices need a key typed into the app's Settings by the user. You never handle keys.

## 2. The script

Write an `.srt` in the **input folder**, timed against the **composed** film: if the intro lasts 3 s, the first cue starts after 3 s. Keep each cue to what fits its slot (about 2.5 words per second is a safe pace). `preview_script` with `film_path`. If cues are **too long**, show them and shorten only those lines (keep numbers and timings, keep the meaning, show the change), then preview again. Do not render with flagged lines unless the user says so.

## 3. Render with music

`create_voiceover(film_path, script_path, voice, music_path=<file>)`. Pass `music_path` **only** if the user gave a file (`.mp3 .wav .m4a .aac .ogg .flac`, inside the input folder). `quality="high"` only if they asked for lossless. Then `wait_for_job` until done and `download_result` (the MP4 by default; `audio`, `wav` or `script` on request). The music is mixed under the voice by the app; the exact mix (level, ducking, fades) is adjusted in the app's **Music mix** panel, not here. Say that if the user wants it louder or quieter.

## 4. Report

The voice and engine, how many lines were too long, whether music was used, and the saved path. Leave jobs alone unless asked to delete them.
