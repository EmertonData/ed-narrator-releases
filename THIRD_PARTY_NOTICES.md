# Third-party notices

ED Narrator's own code is MIT (see `LICENSE`). It can install these open-source and third-party voice engines. Each keeps its own licence; the models are downloaded at build time
(or on your machine), never committed to this repository.

| Engine | Code licence | Model / voice licence | Source |
|---|---|---|---|
| Kokoro | Apache-2.0 | Apache-2.0 | https://github.com/hexgrad/kokoro |
| Piper (`piper-tts`) | GPL-3.0-or-later | per voice (see each voice's model card) | https://github.com/OHF-Voice/piper1-gpl , https://huggingface.co/rhasspy/piper-voices |
| Pocket TTS | MIT | model CC BY 4.0 (credit Kyutai); voice samples per file | https://github.com/kyutai-labs/pocket-tts , https://huggingface.co/kyutai/pocket-tts , https://huggingface.co/kyutai/tts-voices |
| Supertonic 3 | MIT | BigScience OpenRAIL-M (weights, with use restrictions) | https://github.com/supertone-inc/supertonic , https://huggingface.co/Supertone/supertonic-3 |
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

## Supertonic 3 (Supertone)

Supertonic 3 by Supertone Inc. The code and SDK are MIT. The model weights are under the **BigScience OpenRAIL-M** licence (the `LICENSE` file of
https://huggingface.co/Supertone/supertonic-3, dated August 18, 2022). It allows use, including commercial use, but it is not an open-source licence: it carries
use-based restrictions that you must also put in any agreement with your own users. The app installs the weights only after you accept them (Models, Supertonic 3).

Section 5 of the licence: "You cannot use the Model and the Derivatives of the Model for the specified restricted uses." and "You shall require all of Your users who use the
Model or a Derivative of the Model to comply with the terms of this paragraph". Section 6: "You are accountable for the Output you generate and its subsequent uses."
Section 7: the licensor "reserves the right to restrict (remotely or otherwise) usage of the Model in violation of this License".

Attachment A, "You agree not to use the Model or Derivatives of the Model" for these purposes (quoted from the licence, the examples in (e) and (m) shortened):
in any way that violates any applicable law or regulation; to exploit or harm minors; to generate or disseminate verifiably false information with the purpose of harming others;
to generate or disseminate personal identifiable information that can be used to harm an individual; to generate or disseminate content without expressly and intelligibly
disclaiming that it is machine generated; to defame, disparage or harass others; to impersonate or attempt to impersonate (e.g. deepfakes) others without their consent;
for fully automated decision making that adversely impacts an individual's legal rights or creates or modifies a binding, enforceable obligation; for any use intended to or
having the effect of discriminating against individuals or groups based on online or offline social behavior or known or predicted personal or personality characteristics;
to exploit the vulnerabilities of a specific group of persons based on their age, social, physical or mental characteristics in order to materially distort their behavior in a
manner that causes or is likely to cause physical or psychological harm; for any use intended to or having the effect of discriminating based on legally protected characteristics;
to provide medical advice and medical results interpretation; to generate or disseminate information for administration of justice, law enforcement, immigration or asylum
processes. Read the full text before relying on this summary. The app uses only the ten built-in voice styles (M1 to M5, F1 to F5): no voice cloning.

## Chatterbox (Resemble AI)

Chatterbox by Resemble AI: the code (checked in the repository's LICENSE) and the model weights (the Hugging Face model card says `license: mit`) are **MIT**, copyright Resemble AI.
Resemble AI retired the project in August 2026: it is archived and no longer maintained. The audio it generates carries Resemble's **Perth implicit watermark** (inaudible);
the app does not remove it. Chatterbox pins its own PyTorch, transformers and numpy, so the app installs it into its own folder (`<data>/iso/chatterbox`) and runs it in a
separate process; its dependencies (PyTorch, transformers, gradio and others) keep their own licences. No voice cloning is exposed: only the model's built-in voice is used.

## Piper

Voice by voice (from each voice's MODEL_CARD in rhasspy/piper-voices): `tom` is **AGPLv3**; `northern_english_male` is
CC-BY-SA 4.0; `alba` and `siwis` are CC BY 4.0; `thorsten`, `davefx`, `paola` and `faber` are CC0; `lessac` was trained on the Blizzard 2013 data, which is under a
Research Licence Agreement (granted to a named person, not an open licence): check it before commercial use. The app shows these in each voice's details. Voices under a non-commercial licence are not offered: the Piper voice `ryan` (CC BY-NC-SA 4.0) was removed for that reason, and so were Piper's Turkish `dfki`, Korean `kss`, Japanese `hi_fi_captain`, Russian `ruslan` and Chinese `xiao_ya`.
Added voices: `pim`, `nathalie` (Dutch), `denis` (Russian), `gosia`, `darkman` (Polish) are CC0 per their model cards. `kareem` (Arabic) has **no licence stated for its training data** (its model card says "See URL" and the linked repository has no licence file) and was fine-tuned from the `lessac` voice: check before commercial use (the app flags it). Russian `irina` and Chinese `huayan` had the same gap, could not be verified (no licence on the linked sources) and were **removed**.

Voices added for more languages, each checked at the source its model card links (none is fine-tuned from `lessac`): `dimitar` (Bulgarian), `anna`, `imre` (Hungarian), `chitwan` (Nepali), `mihai` (Romanian) and `lili` (Slovak) come from the Nabu Casa / Open Home Foundation voice datasets, **CC0** (https://github.com/OHF-Voice/voice-datasets); `rapunzelina` (Greek) and `harri` (Finnish) from the CSS10 datasets on Kaggle, **CC0** (kaggle.com/datasets/bryanpark); `aivars` (Latvian) is **CC0** per its Hugging Face page (huggingface.co/RaivisDejus/Piper-lv_LV-Aivars-medium); `talesyntese` (Norwegian, Språkbanken sbr-15) and `nst` (Swedish, Språkbanken sbr-17) are **CC0** per the National Library of Norway's resource catalogue (nb.no/sprakbanken). `anna` and `lili` (like the earlier `gosia`) were fine-tuned from a base model trained on the Hi-Fi TTS dataset, which is **CC BY 4.0** (https://www.openslr.org/109/, Bakhturina et al.): credit it if you redistribute those voices. The app shows this in each voice's details.

The `piper-tts` package is GPL-3.0-or-later. Neither the Docker image nor the desktop installer contains it: the app installs it into the user's own data folder the first time a Piper voice is added, so the GPL applies to that user's copy. Kokoro and Pocket TTS are installed the same way, from their own releases and under their own licences.

The desktop app (Windows, macOS, Linux) bundles Python (python-build-standalone, PSF licence), the backend's dependencies under their own licences, and `ffmpeg` and `ffprobe` from the `ffmpeg-static` and `@ffprobe-installer/ffprobe` npm packages. Those ffmpeg builds are GPL-licensed: if you redistribute the installers, the GPL applies to the ffmpeg binaries inside them, and their source is available from the FFmpeg project (https://ffmpeg.org/).
