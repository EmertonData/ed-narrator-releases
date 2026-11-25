# ed-narrator-mcp

MCP server that lets Claude and other MCP assistants add a voice-over to a film through a running ED Narrator (stdio or local streamable HTTP).

```bash
uv sync
ED_NARRATOR_URL=http://127.0.0.1:8090 ED_NARRATOR_INPUT_DIRS=$HOME/Movies uv run ed-narrator-mcp          # stdio
uv run ed-narrator-mcp --http --port 8765                                                                  # http://127.0.0.1:8765/mcp
uv run pytest                                                                                              # offline tests
```

Tools: `check_status`, `list_voices`, `preview_script`, `create_voiceover`, `get_job`, `wait_for_job`, `download_result`, `list_jobs`, `delete_job`; prompt `voice_over_a_film`.

Safety defaults: `--http` refuses non-loopback Host/Origin headers and accepts an optional `ED_NARRATOR_MCP_TOKEN` bearer token; input folders fail closed (never `/`, your home folder or a parent; hidden paths refused), so set `ED_NARRATOR_INPUT_DIRS` when started from your home folder.

For public Claude Code and Cowork marketplace installation, see the [Claude plugin guide](https://github.com/EmertonData/ed-narrator-releases/blob/main/docs/claude-plugins.md).
