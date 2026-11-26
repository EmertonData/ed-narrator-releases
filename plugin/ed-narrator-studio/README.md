# ED Narrator studio

A Claude plugin that makes a narrated, animated demo of an app from one request: it **captures** the app, adds **motion design** in a style you choose (editorial by default for work tools, 2D, kinetic type, 3D, cinematic), **voices** it with [ED Narrator](https://github.com/EmertonData/ed-narrator-releases) and puts your **music** under it. If no voice is installed, it can install one, with your yes.

| **Who this is for:** |
| :--- |
| **Product people and founders** who need a demo video without opening four tools |
| **Teams on ED Narrator** who already voice films and want capture, motion and music in the same flow |
| **Claude Code and Cowork users** who prefer one request and a few approvals to a timeline editor |

## What it is for

- **One request, four stages.** Capture, motion, voice, music, in the order that keeps the script in sync with the picture.
- **A style you choose, approved before the render.** Claude publishes a private animated storyboard and waits, so a rejected style costs seconds, not minutes.
- **A script that fits.** It is timed to the final film, and lines too long for their slot are fixed before rendering.
- **Voices when you need them.** A Piper voice (about 65 MB) installs on your yes; the 2.4 and 3.5 GB engines only after Claude has shown you the size.
- **Narrow by design.** It reads only your input folders, writes only one output folder, and never sees the Azure key.

## What it doesn't do

- **It is not a video editor.** It composes an intro, callouts and an outro, and voices the film. It does not cut or retime your footage.
- **It keeps no original audio.** ED Narrator replaces it with the voice and the music.
- **It does not find music.** You give a file; licences are your call.
- **It is not proven end to end yet.** The manifests validate and the connector's 29 tests pass, but a full run (capture, 3D render, voice, music) has not been done, and installing from the marketplace on a clean machine has not been tried. See [what is verified](docs/reference.md#what-is-verified-and-what-is-not).
- **It needs ED Narrator running.** Nothing renders without the app. The app itself is tested on macOS Apple silicon only.

## Quick start

1. Install the plugin and open ED Narrator (below).
2. Run `/ed-narrator-studio:studio a 40 second demo of <your app>`.
3. Answer the short brief, approve the style when Claude stops, and read the result's path at the end.

Examples: `/ed-narrator-studio:studio use ~/Movies/demo.mov`, or `... 1 minute promo, 3D style, music in bed.mp3`.

Stop there; you'll know if it fits. The [tutorial](docs/tutorial-first-demo.md) walks the whole flow with what you will see at each step.

## Install

**Requirements:** Claude Code 2.1.275 or later, or Claude Cowork with plugin support; [`uv`](https://docs.astral.sh/uv/); and ED Narrator running. Node is needed only for browser capture and Remotion. The marketplace and connector source are public; no access to the private app source repository is needed.

### Claude Code

```text
/plugin marketplace add EmertonData/ed-narrator-releases
/plugin install ed-narrator-studio@ed-narrator-public
```

Or run `claude plugin marketplace add EmertonData/ed-narrator-releases` and `claude plugin install ed-narrator-studio@ed-narrator-public` in a terminal.

### Claude Cowork

Open **Customize > Plugins > Add > Add marketplace**, enter `EmertonData/ed-narrator-releases`, then add **ED Narrator Studio**. If Claude Code uses the same Claude account, the plugin syncs there too.

The public Releases page also has a plugin ZIP for direct upload and a standalone voice-over skill ZIP.

### Other assistants

The marketplace install is for Claude only. The `ed-narrator` connector works in any assistant that supports MCP, and [`AGENTS.md`](AGENTS.md) lets assistants that read it follow the same capture, motion, voice and music flow. Setup for Cursor, Codex, opencode, Gemini CLI and VS Code is in [Other assistants](docs/other-assistants.md); it has not been tested outside Claude.

Configure the connector in Claude Code's `/config` panel. Cowork uses the safe defaults below; put input files in `~/Movies` or change the folders in `/config` when using Claude Code.

| Variable | Default | What |
|---|---|---|
| `ED_NARRATOR_URL` | `http://127.0.0.1:18090` | desktop app default; set Docker to `http://127.0.0.1:8090` |
| `ED_NARRATOR_INPUT_DIRS` | `~/Movies` | folders with films, scripts and music. Never your home folder |
| `ED_NARRATOR_OUTPUT_DIR` | `~/Movies/ed-narrator-output` | where finished files are saved |

Check it works by asking Claude: `check the status of ED Narrator`. It should report the app, `ffmpeg`, and the voices available.

**Update:** `/plugin marketplace update ed-narrator-public`. **Uninstall:** see [How-to > Clean up](docs/how-to.md#clean-up-and-uninstall).

## Documentation

| You want to | Read |
|---|---|
| Make your first demo, step by step | [Tutorial](docs/tutorial-first-demo.md) |
| Do one specific thing (add music, install a voice, fix a tight line…) | [How-to](docs/how-to.md) |
| Look up a tool, a setting, a limit | [Reference](docs/reference.md) |
| Understand why it works this way | [Why a studio plugin](docs/why-studio.md) |
| Fix an error message | [Troubleshooting](docs/troubleshooting.md) |
| Use it with Codex, Cursor, opencode, Gemini CLI or VS Code | [Other assistants](docs/other-assistants.md) |
| Know what it can touch and how to report a problem | [Security](docs/security.md) |

The connector's own documentation is the [MCP server guide](https://github.com/EmertonData/ed-narrator-releases/blob/main/mcp-server/README.md). The plain voice-over skill is included in the public plugin bundle and is also available as a standalone download from Releases.

## License

MIT, copyright Emerton Data. See the [third-party notices](https://github.com/EmertonData/ed-narrator-releases/blob/main/THIRD_PARTY_NOTICES.md); voice engines the app installs keep their own licences, shown in the app under **Licences**.
