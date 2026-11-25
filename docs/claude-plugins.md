# ED Narrator plugins for Claude Code and Cowork

The public [ED Narrator releases repository](https://github.com/EmertonData/ed-narrator-releases) also hosts the Claude plugin marketplace and its connector source. You do not need access to the private app source repository.

## Install in Claude Code

Run these commands in a terminal:

```bash
claude plugin marketplace add EmertonData/ed-narrator-releases
claude plugin install ed-narrator-studio@ed-narrator-public
```

Or, from a Claude Code session:

```text
/plugin marketplace add EmertonData/ed-narrator-releases
/plugin install ed-narrator-studio@ed-narrator-public
```

To update later, run `claude plugin marketplace update ed-narrator-public` and `claude plugin update ed-narrator-studio@ed-narrator-public`.

## Install in Claude Cowork

In Cowork, open **Customize > Plugins > Add > Add marketplace**, enter `EmertonData/ed-narrator-releases`, then add **ED Narrator Studio**. Plugins added to your Claude account are also available in Claude Code when it uses the same Claude account and plugin sync is enabled.

The plugin includes the studio workflow and the standalone `ed-narrator-voiceover` skill. The public Releases page also offers a plugin ZIP for direct upload under **Customize > Plugins** and a standalone skill ZIP under **Customize > Skills**. If you upload only the skill ZIP, configure the MCP connector separately; the skill needs the connector's tools.

## Requirements

- A running ED Narrator app and at least one installed voice.
- `uv` available to Claude so the plugin can launch the public `ed-narrator-mcp` package.
- The MCP process must be able to reach the app. The plugin defaults to the desktop app at `http://127.0.0.1:18090`; Docker uses `http://127.0.0.1:8090`. Configure `ED_NARRATOR_URL` in Claude Code's `/config` panel when the default differs.
- The safe defaults allow reads from `~/Movies` and save results to `~/Movies/ed-narrator-output`. Claude Code users can change `ED_NARRATOR_INPUT_DIRS` and `ED_NARRATOR_OUTPUT_DIR` in `/config`.

In Claude Cowork, local MCP access depends on the Cowork runtime being able to reach the running app on the same machine. Use the desktop app's default port and keep the media files in `~/Movies`. If `127.0.0.1` is not reachable there, use Claude Code on the machine running ED Narrator.

For the workflow, safety rules, and troubleshooting, see the [studio plugin guide](../plugin/ed-narrator-studio/README.md) and [MCP server guide](../mcp-server/README.md).
