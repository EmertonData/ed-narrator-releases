# ED Narrator studio

Use this when the user wants a narrated, animated demo of an app (capture, motion design, voice, music), or a voice-over on a film they have. It needs the `ed-narrator` MCP server and a running ED Narrator app (`check_status` tells you).

## How to work

Read the stage files in `skills/` only when you reach that stage, in this order, and follow them:

1. `skills/ed-narrator-studio/SKILL.md`: the brief, the order of work and the rules. Read it first.
2. `skills/studio-capture/SKILL.md`: get the film.
3. `skills/studio-motion/SKILL.md`: motion design, the storyboard, the approval stop.
4. `skills/studio-voice/SKILL.md`: script, voice, music, installs.

Paths in those files (`scripts/`, `docs/`, `templates/`) are relative to this folder. Skip the YAML header of each file.

## Claude tools, in plain terms

The stage files name a few Claude-only tools. Use these equivalents:

| The file says | Do this |
|---|---|
| `AskUserQuestion` | Ask your multiple-choice question tool if you have one. Otherwise number the options in one message (several answers allowed where they combine, an open answer always allowed), put your recommendation first, and wait. |
| the Artifact tool, "publish the storyboard" | Save the animated storyboard as one self-contained HTML file in a scratch folder, give its path, and wait for the user's approval. Nothing is published online. |
| a subagent, `run_in_background` | Use your own background tasks. If you have none, run the steps one after another. |
| "load the `artifact-design` skill", other named skills | Ignore; they are optional extras. |

The rules in `ed-narrator-studio/SKILL.md` still apply: files only in the allowed folders, a stop for style approval, installs and publishing only after a clear yes.
