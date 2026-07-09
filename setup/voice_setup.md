# Local Voice / TTS Setup

Phase 1 delivers a **working local voice path**. The goal is real spoken
output running entirely on the Mac — *not* a perfect celebrity clone. Voice
*styling* from legally provided samples is a first-pass capability via Coqui
XTTS; treat it as experimental.

Pick ONE backend to start. All are selected with `TTS_BACKEND` in `.env`.

---

## Option A — macOS `say` (fastest, zero install)

Great for confirming the end-to-end demo before installing anything.

```bash
# .env
TTS_BACKEND=say
```
```bash
python src/scripts/test_tts.py "Hello from your local assistant."
# -> outputs/assistant_reply.aiff  (play with: afplay outputs/assistant_reply.aiff)
```

---

## Option B — Piper (recommended local neural TTS)

[Piper](https://github.com/rhasspy/piper) is fast, fully local, and sounds
far better than `say`.

### 1. Install the Piper binary
```bash
# Homebrew (if available):
brew install piper-tts
# …or download a release binary from:
#   https://github.com/rhasspy/piper/releases
# Ensure the `piper` command is on your PATH.
```

### 2. Download a voice model
Piper voices are two files: `NAME.onnx` and `NAME.onnx.json`. Browse voices at
<https://rhasspy.github.io/piper-samples/> and place both files under a local
`voices/` folder (git-ignored):
```bash
mkdir -p voices
# example: download en_US-lessac-medium.onnx and .onnx.json into voices/
```

### 3. Point `.env` at it
```bash
TTS_BACKEND=piper
PIPER_BINARY=piper
PIPER_MODEL=voices/en_US-lessac-medium.onnx
```

### 4. Test
```bash
python src/scripts/test_tts.py "This is Piper speaking, fully offline."
# -> outputs/assistant_reply.wav
```

---

## Option C — Coqui XTTS v2 (voice styling from a sample)

[Coqui XTTS v2](https://github.com/coqui-ai/TTS) can imitate the *style* of a
short reference clip. This is the path for the **client-provided voice
samples**. It is heavier (pulls in PyTorch and downloads a model on first run).

### 1. Install
```bash
pip install TTS
```

### 2. Add a legally provided sample
Place a clean 6–20 second clip in `voice_samples/` (see
[voice_samples/README.md](../voice_samples/README.md) for guidance). These
files are **git-ignored and never committed**.

### 3. Configure `.env`
```bash
TTS_BACKEND=coqui
COQUI_MODEL=tts_models/multilingual/multi-dataset/xtts_v2
COQUI_LANGUAGE=en
COQUI_SPEAKER_WAV=voice_samples/client_sample_01.wav
```
Leave `COQUI_SPEAKER_WAV` blank to use the model's default speaker.

### 4. Test
```bash
python src/scripts/test_tts.py "Testing a first-pass voice style."
# -> outputs/assistant_reply.wav
```

> **First-pass expectations:** XTTS captures general timbre and cadence from a
> short sample. Quality depends heavily on sample cleanliness. It will not be a
> flawless clone, and we make no impersonation claims. A refined voice model is
> a Phase 2 item.

---

## Option D — `none` (headless / CI / Docker)

Writes a `.txt` transcript instead of audio so the demo still completes where
no audio engine is configured.
```bash
TTS_BACKEND=none
```

---

## Where audio goes

All generated audio is written to `outputs/` (default), which is **git-ignored**.
Nothing you synthesize will be committed.

## Legal & ethical note

Only use voice samples you are **legally permitted** to use. Do not represent
generated audio as authentic recordings of a real person, and do not claim the
assistant *is* any specific celebrity or copyrighted character.
