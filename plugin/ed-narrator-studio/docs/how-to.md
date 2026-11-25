# How-to

Short recipes for one task each. New here? Start with the [tutorial](tutorial-first-demo.md). Exact names and limits are in the [reference](reference.md).

- [Use a film I already have](#use-a-film-i-already-have)
- [Record the app in a browser](#record-the-app-in-a-browser)
- [Record my Mac screen](#record-my-mac-screen)
- [Choose or change the motion style](#choose-or-change-the-motion-style)
- [Add background music](#add-background-music)
- [Change how loud the music is](#change-how-loud-the-music-is)
- [Install a voice](#install-a-voice)
- [Fix lines that are too long](#fix-lines-that-are-too-long)
- [Pick a different voice or language](#pick-a-different-voice-or-language)
- [Fix how a word is pronounced](#fix-how-a-word-is-pronounced)
- [Get lossless files](#get-lossless-files)
- [Voice several films](#voice-several-films)
- [Clean up and uninstall](#clean-up-and-uninstall)

## Use a film I already have

Put it (or say where it is) and ask: `/ed-narrator-studio:studio use ~/Desktop/recording/demo.mov`. Claude copies it into the input folder (the original stays), reads its length, size and a few frames, and goes on to the motion stage. `.mp4`, `.m4v` and `.mov` are accepted.

## Record the app in a browser

Say `record https://… and click through: open Models, install a voice`. Claude writes a Playwright script in a scratch folder, records at 1920 × 1080 with a visible cursor, and converts the video to an `.mp4` in your input folder. If Playwright is missing it tells you to run `npm i playwright && npx playwright install chromium` in the scratch folder; it does not install it silently.

## Record my Mac screen

Say `record my screen for 40 seconds`. Claude counts down 5 seconds, runs `screencapture -v -V 40`, and tells you when it ends. If the file is blank, give your terminal Screen Recording permission in System Settings > Privacy & Security > Screen Recording and run it again.

## Choose or change the motion style

Name the style in the request (`3D`, `cinematic`, `kinetic typography`, `2D`, `minimal`) or let Claude recommend one. To change it after seeing the storyboard, just say so: Claude updates the artifact and asks again before it renders. Aspect ratio (16:9, 9:16, 1:1), colours and intro and outro length are asked in the brief.

## Add background music

Put the file in the input folder and name it in the request (`music in bed.mp3`). Claude passes it to the render; the app mixes it under the voice (ducking) and normalises the result. Without a file, no music is used: Claude will not look for one.

## Change how loud the music is

In the ED Narrator app, open the job, then the **Music mix** panel: pick a preset (Subtle, Balanced, Radio) or set the level, the dip under the voice, the fades and where the music enters, then **Export mix**. **Remove music mix** goes back to voice only. The plugin does not change these settings.

## Install a voice

Ask: `which voices can I install?` Claude calls `list_installable`.

- **A Piper voice** (about 65 MB) installs on your yes.
- **Kokoro** (about 2.4 GB, 1.5 GB of memory) and **Pocket TTS** (about 3.5 GB, 1.1 GB of memory) install only after Claude has told you those numbers and you said yes.
- If the disk or memory cannot take it, the install is refused with the reason. Free space and ask again.

The install runs in the app; Claude waits and then lists the new voices. A voice for a language the app doesn't offer cannot be added from here.

## Fix lines that are too long

You do not need to do anything: Claude previews the script, shows the flagged lines, and shortens only those (keeping the cue numbers and timings, and the meaning). To keep a line as it is, say `voice it as it is`; the app then speeds it up or lets it overlap. To give a line more time instead, ask Claude to move the next cue's start.

## Pick a different voice or language

Say `use a French voice` or name one from the list Claude shows. Only ids that `list_voices` returned are accepted. Two voices that take turns are possible with `second_voice` (same engine): ask for `two voices, alternating`.

## Fix how a word is pronounced

Tell Claude: `say SQL as sequel`. It passes `pronunciations` with the render. The same fixes can be set in the app.

## Get lossless files

Ask for `high quality`. The render then also delivers lossless 24-bit / 48 kHz files (`flac` and `video_hires`). The engines speak at 24 kHz, so this is a lossless delivery format, not extra detail.

## Voice several films

Ask for them in one message. Claude does one film at a time, reports a line per film, and stops at the first failure to ask you.

## Clean up and uninstall

- **Jobs:** the app keeps finished jobs for 24 hours; Claude deletes one only if you ask.
- **Files:** the scratch folder, `composed.mp4` and the captures live in your folders; delete them yourself.
- **Remove the plugin:** `/plugin uninstall ed-narrator-studio`, then `/plugin marketplace remove ed-narrator-public` if you no longer want the marketplace.
- **Remove voices:** in the app, Models > the trash icon (the plugin cannot remove anything).
