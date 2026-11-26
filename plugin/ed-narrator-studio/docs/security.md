# Security

The plugin runs on your machine with your files, through a connector to an app that has no login. This page says what it can and cannot do, and how to report a problem.

## What the connector can do

- **Talk only to your own machine.** `ED_NARRATOR_URL` must be `localhost`, `127.0.0.1` or `::1`. It never follows redirects and sends no `Origin` header, so a web page cannot ride on it.
- **Read films, scripts and music only from folders you list** in `ED_NARRATOR_INPUT_DIRS`. Paths are resolved first (symlinks and `..` included) and refused if the real file is outside, if any part is a hidden (dot) name, or if the extension is wrong. `/`, your home folder and its parents are refused.
- **Write only into `ED_NARRATOR_OUTPUT_DIR`**, under a fixed name that starts with the first 8 characters of the job id (hexadecimal only, so no path pieces).
- **Use only voices the app listed.** A voice id must have been returned by the app a moment earlier for the engine you name.
- **Start installs of catalog voices and engines**, and nothing else: a Piper voice by id; Kokoro or Pocket TTS only with `confirm`, after the size has been shown. The app refuses an install the disk or memory cannot take.

## What it cannot do

- It never calls the app's settings, so it never sees or sets the Azure key.
- It cannot remove voices or engines.
- It cannot accept a licence for you: an engine that needs one is refused and sent to the app.
- It cannot read outside your input folders or write outside the output folder.

## What the skills add, and their limit

The skills tell Claude to ask before installing, publishing or deleting, to keep artifacts private, and to warn you before filming. These are instructions. A tool call is not proof that you agreed, so if you auto-approve this server, an engine download can start without a second look. Keep tool approvals on if you want that check.

## What Claude shows before you add it

The plugin page in Claude's directory lists two notices: it **can send data to other services** and it **can run code without asking**. They come from the plugin having a connector and a command. The limits above say what that means in practice: the connector talks only to your own machine, and the skills ask before installing, publishing or deleting.

## Things to watch

- **What is on screen.** A recording or an artifact can contain private data. Close windows before capturing, and say so if the film must not be shared.
- **Artifacts start private.** Publishing one to others is your decision, not the plugin's.
- **Installing Remotion or Playwright** downloads packages. Claude asks first; read what it proposes.
- **The marketplace is public.** The connector is fetched from `EmertonData/ed-narrator-releases` with `uvx`; no access to the private app source is needed.

## Reporting a problem

Report vulnerabilities privately to the Emerton Data maintainers, not in a public issue. Say which tool or skill, the plugin version (from `plugin.json`), the steps and the impact you saw. Problems in third-party tools the plugin drives (Claude Code, Remotion, Playwright, ffmpeg) belong with those projects.

More on the connector and its tests: [MCP server guide](https://github.com/EmertonData/ed-narrator-releases/blob/main/mcp-server/README.md).