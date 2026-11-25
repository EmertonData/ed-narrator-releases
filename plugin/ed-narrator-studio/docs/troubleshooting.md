# Troubleshooting

Find the message Claude showed you, then follow its fix. If your message is not here, ask Claude to run `check_status` first: it names the usual causes.

| You see | Why | Do this |
|---|---|---|
| `ED Narrator is not reachable at …` | the app is closed, or `ED_NARRATOR_URL` points to the wrong port | Open the app. Docker serves on `http://127.0.0.1:8090`; the desktop app shows its port in **Guide > Connect to Claude**. Change `ED_NARRATOR_URL` in Claude Code's `/config` panel |
| `No voice is available` | nothing is installed in the app | Ask `which voices can I install?`, or open **Models** in the app. See [Install a voice](how-to.md#install-a-voice) |
| `The film file is outside the folders this server may read` | the file is not in an allowed folder | Move it into your input folder, or add its folder to `ED_NARRATOR_INPUT_DIRS` |
| `No input folder is allowed` | no safe input folder is configured | Set `ED_NARRATOR_INPUT_DIRS` in Claude Code's `/config` panel to a dedicated folder such as `~/Movies/demo` |
| `ED_NARRATOR_INPUT_DIRS may not contain …` | the setting names `/`, your home folder or a parent of it | Use a dedicated folder |
| `Refusing <host>: ED Narrator has no login …` | `ED_NARRATOR_URL` is not a loopback address | Use `127.0.0.1` or `localhost` |
| `… cannot be installed on this machine: …` | not enough free disk or memory for that engine | Free space or memory, or pick a Piper voice (about 65 MB) |
| `Give a voice_id returned by list_installable` | the voice id is not one the app listed | Ask for the list again and choose from it |
| `Unknown voice …` | the voice id is not one `list_voices` returned | Use an id from `list_voices`; both voices of a pair must use the same engine |
| `Give duration_s (the film length in seconds)` | a Markdown or text script needs the film length | Pass the film path, or the length |
| `too_long_count` is above 0 | some lines do not fit their slot | See [Fix lines that are too long](how-to.md#fix-lines-that-are-too-long) |
| The job ends in `error` | the render failed; Claude gives the app's plain-language reason | Read the reason; retry once if the cause is gone (disk space, the app restarted). **Help > Open the log** in the desktop app has details |
| `has a licence only you can accept` | an engine that needs a licence | Open the app, **Models**, and install it there |
| The screen recording is blank | Screen Recording permission is missing | System Settings > Privacy & Security > Screen Recording: allow your terminal, then record again |
| Playwright is missing | not installed in the scratch folder | `npm i playwright && npx playwright install chromium` there, then retry |
| Text does not appear on the title card | this ffmpeg has no `drawtext` filter | Expected: Claude draws text in Remotion instead. Ask it to render the card there |
| The connector does not start | `uv` is missing, or you cannot reach the public repository | Install `uv`; check you can open `github.com/EmertonData/ed-narrator-releases`. The connector is fetched with `uvx` |
| The plugin does not install | Claude Code is older than 2.1.275, or the public marketplace cannot be reached | Update Claude Code; check marketplace access |
| The artifact would show private data | the film shows customer data | Say so: Claude redacts or skips the artifact. Nothing is published without your yes |

Still stuck? Run `claude plugin validate plugin/ed-narrator-studio` in a checkout of the repository, and `cd mcp-server && uv run pytest`. A failure there points to the plugin or the connector; a pass points to the app or your setup.
