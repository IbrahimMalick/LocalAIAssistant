# Architecture — Phase 1

## Overview

The Local AI Assistant is a **local-first** smart-home companion that runs
entirely on the client's Mac Mini Pro (M4). No cloud services are required for
its core loop: a local LLM produces text, and a local TTS engine speaks it.

```
                         ┌──────────────────────────────────────────┐
                         │            Mac Mini Pro (M4)             │
                         │            local AI host                 │
                         │                                          │
  User text prompt ─────▶│  ┌────────────┐     ┌─────────────────┐  │
                         │  │ Assistant  │     │  Ollama (native)│  │
                         │  │  app       │────▶│  local LLM      │  │
                         │  │ (Python)   │◀────│  llama3.1:8b …  │  │
                         │  │            │     └─────────────────┘  │
                         │  │  main.py   │                          │
                         │  │  config    │     ┌─────────────────┐  │
                         │  │  prompts   │────▶│  Local TTS      │  │
                         │  │  llm/tts   │◀────│  Piper / Coqui  │  │
                         │  └────────────┘     │  / macOS say    │  │
                         │        │            └─────────────────┘  │
                         │        ▼                                 │
                         │   outputs/*.wav  (spoken reply, local)   │
                         └──────────────────────────────────────────┘
```

## Components

### 1. Mac Mini as the local AI host
Everything runs on the household's own hardware. The M4's unified memory and
Metal GPU acceleration make an 8B-class model and a neural voice practical
without a cloud dependency. This is the privacy foundation of the whole system.

### 2. Local LLM (Ollama)
- Ollama runs the model natively and exposes an HTTP API at
  `http://localhost:11434`.
- `assistant/llm_client.py` implements a thin `OllamaClient.chat()` over the
  standard library — no heavy SDK.
- The backend is abstracted behind `build_llm_client()`, so an LM Studio
  (OpenAI-compatible) endpoint can be slotted in later without touching the
  rest of the app.

### 3. Personality layer
- `assistant/prompts.py` builds the system prompt from editable trait and
  behaviour lists.
- Personality is **original** — witty, confident, playful — and deliberately
  avoids copyrighted character text or impersonation claims.

### 4. Local TTS service
- `assistant/tts_client.py` defines a `BaseTTS` interface with four backends:
  `piper`, `coqui`, `say` (macOS), and `none`.
- Coqui XTTS is the path for first-pass **voice styling** from legally provided
  samples; Piper is the recommended everyday neural voice; `say` is a
  zero-install smoke test.
- Output audio is written to the git-ignored `outputs/` directory.

### 5. Orchestration & entry points
- `assistant/main.py` (`Assistant`) wires config → prompt → LLM → TTS.
- `scripts/test_llm.py`, `scripts/test_tts.py`, and `scripts/run_demo.py` are
  the operator-facing entry points.

### 6. Deployment
- The Python app is containerized (`Dockerfile`, `docker-compose.yml`).
- On Apple Silicon, **Ollama and neural TTS run best natively** (Metal GPU),
  while the app itself can run in Docker and reach the host via
  `host.docker.internal`. A `full` compose profile can also run Ollama in
  Docker (CPU-only) for a self-contained demo.

## Data flow (demo)

1. Operator runs `run_demo.py "…prompt…"`.
2. `Assistant.respond()` sends the prompt + system prompt to Ollama.
3. The text reply is printed.
4. `Assistant.speak()` synthesizes the reply with the configured TTS backend.
5. Audio is saved locally under `outputs/`.

All five steps happen on-device.

## Future integration points (not built in Phase 1)

These are **design placeholders** — see `future_roadmap.md` for detail.

### Future Home Assistant integration
The assistant will connect to **Home Assistant Assist** to control devices.
Envisioned shape: the assistant app becomes (or calls) a Home Assistant
*conversation agent*, translating intents into HA service calls. Keeping the
LLM/TTS layer modular now means HA can be added as another client of the same
`Assistant` core later.

### Future VPN / network isolation
Because everything is local, the natural next security step is to place the Mac
Mini on an isolated network segment (VLAN) reachable only over a VPN
(e.g. WireGuard/Tailscale) with device whitelisting. Phase 1 makes no outbound
calls in its core loop, which keeps that future lockdown straightforward.

### Future STT (voice input)
A local speech-to-text stage (e.g. whisper.cpp) would sit in front of the LLM
to close the loop into a true voice assistant. The `Assistant` core is designed
to accept text from any source, so STT plugs in cleanly ahead of it.
