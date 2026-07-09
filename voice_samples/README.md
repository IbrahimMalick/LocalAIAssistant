# Voice Samples

This folder is where **legally provided** voice samples live locally. It exists
so the Coqui XTTS backend can do first-pass voice *styling* (see
[../setup/voice_setup.md](../setup/voice_setup.md)).

## ⚠️ Nothing in here is committed to git

Everything in this directory is **git-ignored** except this README and a
`.gitkeep`. Audio samples are private and potentially rights-restricted, so
they must never end up in the repository.

## What to put here

- Short, clean reference clips: **6–20 seconds** each is plenty for XTTS.
- **WAV** or **MP3**, mono, minimal background noise, single speaker.
- One clear speaking voice per file (no music, no overlapping talk).

Example layout (local only):
```
voice_samples/
├── README.md            <- committed
├── .gitkeep             <- committed
├── client_sample_01.wav <- git-ignored (yours)
└── client_sample_02.wav <- git-ignored (yours)
```

## Wiring a sample into the assistant

In `.env`:
```bash
TTS_BACKEND=coqui
COQUI_SPEAKER_WAV=voice_samples/client_sample_01.wav
```

## Legal & ethical requirements

- Use only audio you are **licensed / permitted** to use.
- Do **not** claim generated speech is a genuine recording of a real person.
- Do **not** market the assistant as being a specific celebrity or copyrighted
  character. Phase 1 is a first-pass voice style using provided samples only.
