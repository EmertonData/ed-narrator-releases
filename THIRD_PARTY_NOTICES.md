# Third-party notices

ED Narrator's own code is MIT (see `LICENSE`). It can install these open-source and third-party voice engines. Each keeps its own licence; the models are downloaded at build time
(or on your machine), never committed to this repository.

| Engine | Code licence | Model / voice licence | Source |
|---|---|---|---|
| Kokoro | Apache-2.0 | Apache-2.0 | https://github.com/hexgrad/kokoro |
| Piper (`piper-tts`) | GPL-3.0-or-later | per voice (see each voice's model card) | https://github.com/OHF-Voice/piper1-gpl , https://huggingface.co/rhasspy/piper-voices |
| Pocket TTS | MIT | model CC BY 4.0 (credit Kyutai); voice samples per file | https://github.com/kyutai-labs/pocket-tts , https://huggingface.co/kyutai/pocket-tts , https://huggingface.co/kyutai/tts-voices |
| Chatterbox | MIT | MIT (weights, per the model card) | https://github.com/resemble-ai/chatterbox , https://huggingface.co/ResembleAI/chatterbox |
| Azure AI Speech | n/a (cloud service) | Microsoft terms | https://learn.microsoft.com/azure/ai-services/speech-service/ |

## Emerton Data

ED Narrator is a product of Emerton Data. The code is MIT, copyright Emerton Data (see `LICENSE`). The Emerton Data name, logo (`frontend/public/emerton-data-logo*.png`) and icons
(`frontend/public/icon-*.png`, `favicon.svg`) are Emerton Data brand assets: they identify the publisher and are not licensed for use in unrelated products.

## Pocket TTS (Kyutai)

Pocket TTS by Kyutai. The code is MIT (checked in the repository's LICENSE). The model weights are **CC BY 4.0**: credit Kyutai. Kyutai's model card adds a
prohibited-use policy: no voice impersonation or cloning without explicit and lawful consent, no deception (for example presenting generated audio as a
genuine recording of a real person), and no unlawful, harmful or abusive content.

The built-in voice samples have their own licences, as stated in Kyutai's `tts-voices` README: `alba` (CC BY 4.0), `anna`, `eve`, `jane`, `george` and `charles`
(VCTK corpus, CC BY 4.0), `estelle` (Kyutai's own recording, CC0). For `giovanni`, `lola`, `juergen` and `rafael` Kyutai documents no licence (their files sit on a
branch named `add_lang_not_documented`): check with Kyutai before using them commercially. The app marks these in the voice details.

## Chatterbox (Resemble AI)

Chatterbox by Resemble AI: the code (checked in the repository's LICENSE) and the model weights (the Hugging Face model card says `license: mit`) are **MIT**, copyright Resemble AI.
Resemble AI retired the project in August 2026: it is archived and no longer maintained. The audio it generates carries Resemble's **Perth implicit watermark** (inaudible);
the app does not remove it. Chatterbox pins its own PyTorch, transformers and numpy, so the app installs it into its own folder (`<data>/iso/chatterbox`) and runs it in a
separate process; its dependencies (PyTorch, transformers, gradio and others) keep their own licences. No voice cloning is exposed: only the model's built-in voice is used.

## Piper

Voice by voice (from each voice's MODEL_CARD in rhasspy/piper-voices): `tom` is **AGPLv3**; `northern_english_male` is
CC-BY-SA 4.0; `alba` and `siwis` are CC BY 4.0; `thorsten`, `davefx`, `paola` and `faber` are CC0; `lessac` was trained on the Blizzard 2013 data, which is under a
Research Licence Agreement (granted to a named person, not an open licence): check it before commercial use. The app shows these in each voice's details. Voices under a non-commercial licence are not offered: the Piper voice `ryan` (CC BY-NC-SA 4.0) was removed for that reason, and so were Piper's Turkish `dfki`, Korean `kss`, Japanese `hi_fi_captain`, Russian `ruslan` and Chinese `xiao_ya`.
Added voices: `pim`, `nathalie` (Dutch), `denis` (Russian), `gosia`, `darkman` (Polish) are CC0 per their model cards. `kareem` (Arabic), `irina` (Russian) and `huayan` (Chinese) have **no licence stated for their training data** and were fine-tuned from the `lessac` voice: check before commercial use (the app flags them).

The `piper-tts` package is GPL-3.0-or-later. Neither the Docker image nor the desktop installer contains it: the app installs it into the user's own data folder the first time a Piper voice is added, so the GPL applies to that user's copy. Kokoro and Pocket TTS are installed the same way, from their own releases and under their own licences.

The desktop app (Windows, macOS, Linux) bundles Python (python-build-standalone, PSF licence), the backend's dependencies under their own licences, and `ffmpeg` and `ffprobe` from the `ffmpeg-static` and `@ffprobe-installer/ffprobe` npm packages. Those ffmpeg builds are GPL-licensed: if you redistribute the installers, the GPL applies to the ffmpeg binaries inside them, and their source is available from the FFmpeg project (https://ffmpeg.org/).
