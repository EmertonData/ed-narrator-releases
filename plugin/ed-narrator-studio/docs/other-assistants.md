# Use it with another assistant

The plugin package (marketplace install, the `/studio` command, the skills) is for Claude Code and Claude Cowork. The parts underneath are open, so other assistants can use most of it.

| Part | In another assistant |
|---|---|
| **Voice-over connector** (`ed-narrator`, 12 tools) | Works in any assistant that supports MCP over stdio. Setup below. |
| **The guided flow** (brief, capture, motion, approval, voice, music) | Works through [`AGENTS.md`](../AGENTS.md) in assistants that read it (Codex, opencode, Cursor and others). It points to the same skill files and maps Claude-only tools to plain steps. |
| **Marketplace install and `/studio`** | Claude only. Ask in plain words instead: "make a narrated demo of my app". |

**Not tested.** This was written from each tool's documented config shape; nothing outside Claude has been run end to end. Check your tool's current docs if a snippet is rejected.

## 1. Connect the voice-over connector

You need [`uv`](https://docs.astral.sh/uv/) and ED Narrator running (desktop app at `http://127.0.0.1:18090`, Docker at `http://127.0.0.1:8090`). Use real folder paths, not `~`. The input folder must not be your home folder.

The command is the same everywhere:

```text
uvx --from "git+https://github.com/EmertonData/ed-narrator-releases#subdirectory=mcp-server" ed-narrator-mcp
```

with these environment variables:

```text
ED_NARRATOR_URL=http://127.0.0.1:18090
ED_NARRATOR_INPUT_DIRS=/Users/me/Movies
ED_NARRATOR_OUTPUT_DIR=/Users/me/Movies/ed-narrator-output
```

**Cursor** (`~/.cursor/mcp.json` or `.cursor/mcp.json`) and **Gemini CLI** (`~/.gemini/settings.json`):

```json
{ "mcpServers": { "ed-narrator": {
  "command": "uvx",
  "args": ["--from", "git+https://github.com/EmertonData/ed-narrator-releases#subdirectory=mcp-server", "ed-narrator-mcp"],
  "env": { "ED_NARRATOR_URL": "http://127.0.0.1:18090", "ED_NARRATOR_INPUT_DIRS": "/Users/me/Movies", "ED_NARRATOR_OUTPUT_DIR": "/Users/me/Movies/ed-narrator-output" }
} } }
```

**VS Code** (`.vscode/mcp.json`): the same, with `"servers"` instead of `"mcpServers"` and `"type": "stdio"` next to `"command"`.

**Codex** (`~/.codex/config.toml`):

```toml
[mcp_servers.ed-narrator]
command = "uvx"
args = ["--from", "git+https://github.com/EmertonData/ed-narrator-releases#subdirectory=mcp-server", "ed-narrator-mcp"]
env = { ED_NARRATOR_URL = "http://127.0.0.1:18090", ED_NARRATOR_INPUT_DIRS = "/Users/me/Movies", ED_NARRATOR_OUTPUT_DIR = "/Users/me/Movies/ed-narrator-output" }
```

**opencode** (`opencode.json` or `opencode.jsonc`):

```json
{ "mcp": { "ed-narrator": {
  "type": "local",
  "command": ["uvx", "--from", "git+https://github.com/EmertonData/ed-narrator-releases#subdirectory=mcp-server", "ed-narrator-mcp"],
  "environment": { "ED_NARRATOR_URL": "http://127.0.0.1:18090", "ED_NARRATOR_INPUT_DIRS": "/Users/me/Movies", "ED_NARRATOR_OUTPUT_DIR": "/Users/me/Movies/ed-narrator-output" },
  "enabled": true
} } }
```

Cline, Continue and Windsurf use the Cursor shape. Other options (a local checkout, streamable HTTP) are in [docs/mcp.md](https://github.com/EmertonData/ed-narrator-releases/blob/main/docs/mcp.md).

Check it works: ask `check the status of ED Narrator`. It should report the app, `ffmpeg` and the voices.

## 2. Add the guided flow (optional)

For the full capture, motion, voice and music flow:

1. Clone `EmertonData/ed-narrator-releases` and open the `plugin/ed-narrator-studio` folder as your project, or copy its contents (`AGENTS.md`, `skills/`, `scripts/`, `docs/`, `templates/`) into your own project.
2. Keep `AGENTS.md` at the project root. If your assistant reads another file name (for example `GEMINI.md`), copy or link `AGENTS.md` under that name.
3. Ask: `make a narrated 40 second demo of <your app>`.

The assistant reads the stage files only when it reaches each stage, so the always-loaded part stays small.

## What changes outside Claude

- **Questions.** Claude's multiple-choice question tool is replaced by a numbered list in one message. Reply with numbers or your own words.
- **Storyboard.** Claude publishes a private artifact. Elsewhere the assistant saves one HTML file in a scratch folder and gives you its path; open it, then approve or change the style.
- **Parallel work.** The assistant runs steps one after another if it has no background tasks.
- **Same rules.** Files only from your input folder, a stop for style approval, installs and publishing only after your yes. The connector enforces the file and loopback limits itself; see [Security](security.md).
- **Tools you still need.** Node for browser capture and Remotion, `ffmpeg`, and Python for the check scripts.
