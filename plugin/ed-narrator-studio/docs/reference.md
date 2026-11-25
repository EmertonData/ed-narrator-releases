# Reference

Exact names, settings and limits. To learn the flow, read the [tutorial](tutorial-first-demo.md); for tasks, the [how-to](how-to.md).

## The plugin

| | |
|---|---|
| Name | `ed-narrator-studio` (version 1.8.0, MIT) |
| Marketplace | `ed-narrator-public`, from `EmertonData/ed-narrator-releases` (public repository) |
| Command | `/ed-narrator-studio:studio [what to demo, or a film path]` |
| Connector | the `ed-narrator` MCP server, started by `uvx` from `mcp-server/` in the repository |
| Needs | ED Narrator running, `uv`, Claude Code 2.1.275 or later or Claude Cowork with plugin support; Node for Playwright and Remotion |

## Skills

| Skill | Your specialist | What it does |
|---|---|---|
| `ed-narrator-studio` | **Director** | Asks the brief once, runs the four stages in order, enforces the rules (input folder, consent, nothing published without a yes). |
| `studio-capture` | **Camera operator** | Gets the film: scripted browser capture (Playwright), macOS screen recording (`screencapture`), or an existing `.mp4`/`.m4v`/`.mov`. |
| `studio-motion` | **Motion designer** | Offers the styles, publishes the animated storyboard artifact, waits for approval, renders and assembles a silent `composed.mp4`. |
| `studio-voice` | **Narrator and sound** | Finds or installs a voice, writes the timed script, fixes tight lines, renders with music, downloads the result. |
| `ed-narrator-voiceover` | **Voice-over** | The standalone timed voice-over routine, also distributed separately as a skill ZIP. |

Claude loads a skill when a request matches its description; you rarely name one.

## Motion styles

| Style | How it is made | Notes |
|---|---|---|
| 2D motion graphics | Remotion renders cards and overlays | title card, rings, zoom callouts, end card |
| Kinetic typography | Remotion, one text scene per cue | timed to the script |
| 3D animation | Remotion with `@remotion/three` (Three.js) | recording on a 3D device or panel, camera moves |
| Cinematic motion picture | ffmpeg filters (`pad`, `zoompan`, `curves`, `noise`, `fade`) | letterbox 2.39:1, push-ins, grain |
| Minimal | ffmpeg `fade` | in and out only |

Defaults: 16:9 (also 9:16 and 1:1), intro and outro 3 s, the app's colour tokens (`DESIGN.md`) for ED Narrator demos. Text is drawn in Remotion because some ffmpeg builds have no `drawtext` filter.

## Connector tools

| Tool | Parameters | Returns |
|---|---|---|
| `check_status` | none | reachable, version, `ffmpeg_ok`, `voices_available`, engines, input and output folders, and a `problem` if any |
| `list_voices` | `language?`, `provider?`, `limit?` (1 to 200) | voices (id, provider, name, gender, language, licence) |
| `list_installable` | `language?` | Piper voices and the engines Kokoro and Pocket TTS with size, memory, `fits`, `installed`, `state` |
| `install_voice_model` | `name` (`piper`, `kokoro`, `pocket`), `voice_id?`, `confirm?` | `install started`, `already installed`, or `needs_confirmation` with the size |
| `wait_for_install` | `name`, `voice_id?`, `timeout_s?` (1 to 600) | `installed`, `state`, `error`, `next` |
| `preview_script` | `script_path`, `duration_s?`, `film_path?` | cues, words, `too_long_count`, the flagged cues, `advice` |
| `create_voiceover` | `film_path`, `script_path`, `voice`, `provider?`, `second_voice?`, `music_path?`, `quality?` (`standard`, `high`), `pronunciations?` | a job (`job_id`, status) |
| `get_job` | `job_id` | status, stage, progress in cues, error in plain words |
| `wait_for_job` | `job_id`, `timeout_s?` (1 to 600) | the job once finished or after the time |
| `download_result` | `job_id`, `kind?` | the saved file's path (see below) |
| `list_jobs` | `limit?` (1 to 50) | recent jobs |
| `delete_job` | `job_id` | deleted, or cancellation requested |

`download_result` kinds: `video` (voiced MP4, default), `audio` (MP3), `wav`, `script` (timed SRT), `flac` and `video_hires` (only for jobs made with `quality: high`). Files are saved as `<first 8 characters of the job id>-voiced.mp4`, `-voiceover.mp3`, `-voiceover.wav`, `-script.srt`, `-voiceover.flac`, `-voiced_hires_flac.mp4`.

## Settings

Configure these values in Claude Code's `/config` panel. Cowork uses the defaults.

| Variable | Default | Meaning |
|---|---|---|
| `ED_NARRATOR_URL` | `http://127.0.0.1:18090` | where the desktop app listens (Docker uses 8090). Only `localhost`, `127.0.0.1` and `::1` are accepted |
| `ED_NARRATOR_INPUT_DIRS` | `~/Movies` | folders (separated by the OS path separator) the connector may read. Never `/`, your home folder or a parent of it |
| `ED_NARRATOR_OUTPUT_DIR` | `~/Movies/ed-narrator-output` | where results are saved |
| `ED_NARRATOR_ALLOW_REMOTE` | unset | `1` lifts the loopback rule. Not recommended: the app has no login |

## Limits and numbers

| | |
|---|---|
| Film types | `.mp4`, `.m4v`, `.mov` |
| Script types | `.srt`, `.md`, `.markdown`, `.txt` (Markdown and text need the film length) |
| Music types | `.mp3`, `.wav`, `.m4a`, `.aac`, `.ogg`, `.flac`, up to 200 MB |
| Mixing in the browser | films up to 30 minutes |
| Loudness | normalised to -16 LUFS |
| Audio | picture copied untouched; voice as 256 kbps AAC; lossless 24-bit / 48 kHz with `high` |
| Jobs kept | 24 hours |
| Install sizes | Piper voice about 65 MB; Kokoro about 2.4 GB (1.5 GB memory); Pocket TTS about 3.5 GB (1.1 GB memory) |
| Speaking pace used for scripts | about 2.5 words per second |

## What is verified, and what is not

| | State |
|---|---|
| Plugin and marketplace manifests | pass `claude plugin validate` |
| The connector's tools and guards | covered by 27 offline tests (`cd mcp-server && uv run pytest`) |
| A complete run (capture, 3D render, voice, music) | **not done yet** |
| Installing from the marketplace on a clean machine | **not done yet** |
| Windows and Linux | **not tested**; the app itself is only tested on macOS Apple silicon |
