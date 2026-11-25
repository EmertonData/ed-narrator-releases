---
name: ed-narrator-voiceover
description: Add a timed voice-over to a film with ED Narrator, through its MCP tools. Use when the user wants to narrate, voice, dub or add a voice-over to an .mp4 from an .srt, .md or .txt script, check whether script lines fit their timing before voicing, choose or compare voices, get the audio or subtitles of a voice-over, or voice several films in a row. Needs the ed-narrator MCP server connected.
---

# ED Narrator voice-over

The work is done by the `ed-narrator` MCP tools: `check_status`, `list_voices`, `preview_script`, `create_voiceover`, `wait_for_job`, `get_job`, `download_result`, `list_jobs`, `delete_job`. If they are not available, tell the user to open **Guide > Connect to Claude** in the ED Narrator app (or `docs/mcp.md`) and stop. Do not try to voice anything another way.

## Steps

1. **`check_status`.** If the app is not reachable, ask the user to open it. If no voice is installed, offer to install a Piper voice (`list_installable`, then `install_voice_model`, about 65 MB, on the user's yes) or point to the app's **Models** panel. Heavier engines (Kokoro, Pocket TTS) need the user's explicit yes before you set `confirm`.
2. **Check the script first**: `preview_script` with the script and `film_path` (or `duration_s`). It lists the lines too long for their slot; this is an estimate, and the render's own count is the final one. If any line is flagged, **stop before rendering** and ask: shorten them, or voice as they are. To shorten, edit only the flagged lines in the script file (keep cue numbers and timings, keep the meaning, show what you changed), then preview again.
3. **Choose the voice**: `list_voices` for the script's language. Use the voice the user named or described; otherwise pick one that matches the language and say which. Use only ids that `list_voices` returned.
4. **`create_voiceover`**, then `wait_for_job`, repeating while it is still running. If the job fails, give the plain-language error from `get_job`; retry at most once, and only if the cause is gone.
5. **`download_result`**: the MP4 by default; `audio`, `wav` or `script` (the timed SRT) when asked. Report the file path.

## Rules

- **Delete a job only if the user asked.** The app keeps jobs for 24 hours anyway, so leave them.
- **Several films:** one at a time, a short line per film, and stop at the first failure to ask.
- **Pass `music_path` only if the user gave a music file**, and `quality: high` only if they asked for lossless. The music mix is adjusted in the app, not here.
- **Report briefly:** the voice, how many lines were too long, the output path.
