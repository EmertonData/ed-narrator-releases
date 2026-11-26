# Why a studio plugin

The decisions behind the plugin and what they cost. Nothing here is needed to use it.

## The problem

ED Narrator voices a film well, but a demo is more than a voice. Someone must record the app, add motion so it does not look like a raw screen capture, write a script that fits the picture, and put music under it. Done by hand that is four tools and a lot of re-exporting. The first plugin idea was just a skill that voices a film (`skills/ed-narrator-voiceover`), which still exists, but it starts after the hard part is done.

## Four stages, in this order

**Capture, motion, voice, music.** The order follows what each stage depends on:

- The script is timed against the picture, so the picture must be final first. If the intro were added after the script, every cue would be off by the intro length.
- The voice replaces the film's own audio, so there is nothing to preserve: motion is rendered **silent on purpose**, and the voice and the music arrive together at the end.
- Music is last because the app mixes it under the voice and normalises the result.

## Why it stops for approval

Rendering motion (especially 3D) is the slowest, most expensive step, and style is the most subjective choice. So the plugin publishes a **private animated storyboard** first and waits. A rejected style costs seconds there and minutes after the render. This is the one place the plugin is slow on purpose.

## Why you choose the style

There is no best style for every demo: 3D suits a product launch, minimal suits an internal walkthrough, cinematic suits a story. The plugin recommends one for the audience but does not pick silently.

## Why the guards look the way they do

The connector talks to an app that has no login, and it reads and writes your files, so it is narrow on purpose:

- **Files** are read only from folders you allow, and written only to one output folder under a fixed name.
- **Installs** exist because a demo should not stall on "no voice". A Piper voice is small and installs on your yes. Kokoro, Pocket TTS and Chatterbox are gigabytes, so the tool refuses until `confirm` is set after Claude has shown you the size. Only ids the app listed ever reach a URL.
- **Licences** are never accepted through a tool. The tool that did this once (Linnet, now removed from the app) was the case that made the point: an argument filled in by a model proves nothing about what you read.
- **Nothing is published** (artifact or file) and **nothing is deleted** without your yes.

The skills tell Claude to follow these rules, but a skill is an instruction, not a lock. The locks are in the connector and the app. See [Security](security.md).

## Trade-offs

- **It depends on a running app.** Without ED Narrator open, nothing renders. This keeps your film on your machine and the voice local.
- **It is slow where it matters.** The approval pause and the render are real waiting time. Minimal style skips most of it.
- **Heavy tooling is optional but real.** Remotion and Playwright mean Node and downloads. The plugin asks before installing anything.
- **Screen capture sees everything.** A recording can include private data. The plugin warns you first, but only you can decide what is on screen.
- **Not proven end to end.** The parts are tested and validated; a full run has not been done yet. See the [reference](reference.md#what-is-verified-and-what-is-not).

## Why separate docs

The README is short so you can decide in a minute whether to install it. The [tutorial](tutorial-first-demo.md) teaches by doing, the [how-to](how-to.md) answers one task at a time, the [reference](reference.md) holds exact facts, and this page holds the reasons. Mixing them makes each worse: a tutorial with a settings table is slow to follow, and a reference with a story is slow to search.