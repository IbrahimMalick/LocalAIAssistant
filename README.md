# Local AI Assistant — Phase 1 MVP

A **local-first** AI assistant foundation that runs entirely on a Mac Mini Pro
(M4). It pairs a local LLM (via [Ollama](https://ollama.com)) with an original,
configurable personality and a local text-to-speech voice. No cloud, no API
keys — the core loop never leaves the house.

> **Phase 1 is a foundation, not the finished product.** It does text-in →
> witty reply → local spoken audio. Home control, voice input, network
> isolation, and a refined voice clone are future phases (see below).

---

## Project overview

- **Local LLM** through Ollama (default `llama3.1:8b`).
- **Personality layer** — witty, confident, playful smart-home companion,
  editable in a single file (`src/assistant/prompts.py`).
- **Local TTS** — Piper / Coqui XTTS / macOS `say`, behind one abstraction.
- **First-pass voice styling** from **legally provided** samples via Coqui XTTS.
- **Demo flow** — one command: prompt → LLM reply → spoken audio saved locally.
- **Dockerized** app with Apple-Silicon-realistic guidance.

## Phase 1 scope (at a glance)

**Included:** local LLM + tests, editable personality, local TTS + tests,
end-to-end demo, Docker packaging, full docs.

**Excluded (later phases):** Home Assistant integration, VPN/whitelisting,
facial/emotion recognition, desktop avatar, automation control, speech-to-text,
and any guaranteed celebrity voice clone.

Full detail: [docs/phase1_scope.md](docs/phase1_scope.md).

## Hardware assumptions

- Mac Mini Pro **Apple Silicon M4** (any recent Apple Silicon Mac works).
- **16 GB unified memory minimum**, 24 GB+ recommended.
- ~15 GB free disk for a model + a voice.
- macOS 14 (Sonoma) or newer recommended.

---

## Installation

Detailed guides live in [`setup/`](setup/). Quick path:

```bash
# 1. Clone
git clone <YOUR_REPO_URL> LocalAIAssistant
cd LocalAIAssistant

# 2. (Optional) virtual environment + optional extras
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt   # core has NO required third-party deps

# 3. Configure
cp .env.example .env               # then edit as needed
```

See [setup/macos_setup.md](setup/macos_setup.md) for the full macOS bootstrap.

### How to install Ollama

```bash
brew install ollama       # or download from https://ollama.com/download
ollama serve              # (the menu-bar app starts this automatically)
```

### How to pull the local model

```bash
ollama pull llama3.1:8b   # default; alternatives in setup/model_setup.md
```

### How to configure `.env`

Copy the example and adjust. Key settings:

| Variable        | Purpose                          | Default                  |
|-----------------|----------------------------------|--------------------------|
| `ASSISTANT_NAME`| Name the assistant answers to    | `Aria`                   |
| `LLM_MODEL`     | Ollama model tag                 | `llama3.1:8b`            |
| `LLM_ENDPOINT`  | Ollama URL                       | `http://localhost:11434` |
| `LLM_TEMPERATURE`| Sampling temperature            | `0.7`                    |
| `TTS_BACKEND`   | `piper` / `coqui` / `say` / `none`| `piper`                 |

Full reference: [.env.example](.env.example) and
[setup/model_setup.md](setup/model_setup.md).

---

## How to test the LLM

```bash
python src/scripts/test_llm.py "Introduce yourself in one sentence."
```
Prints the backend/model info and the assistant's reply. If Ollama isn't
running or the model isn't pulled, the script tells you exactly what to do.

## How to test TTS

Pick a backend in `.env` (start with `say` on macOS for zero setup), then:
```bash
python src/scripts/test_tts.py "Hello from your local assistant."
```
Audio is written to the git-ignored `outputs/` folder. On macOS, play it with
`afplay outputs/assistant_reply.aiff` (or `.wav`). Backend setup:
[setup/voice_setup.md](setup/voice_setup.md).

## How to run the demo

```bash
python src/scripts/run_demo.py "Tell me a fun fact about octopuses."
# or run it and type your prompt when asked
python src/scripts/run_demo.py
# text only, skip voice:
python src/scripts/run_demo.py --no-voice "Just the text please."
```
The demo sends your prompt to the local LLM, prints the reply, speaks it with
the local TTS backend, and saves the audio under `outputs/`.

### Running in Docker

Read the header of [`docker-compose.yml`](docker-compose.yml) first — on Apple
Silicon, run **Ollama natively** and the app in Docker:
```bash
docker compose run --rm assistant python src/scripts/test_llm.py "Hi"
```

---

## Repository layout

```
├── README.md
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
├── .gitignore
├── setup/
│   ├── macos_setup.md
│   ├── model_setup.md
│   └── voice_setup.md
├── src/
│   ├── assistant/
│   │   ├── __init__.py
│   │   ├── main.py          # Assistant orchestration
│   │   ├── config.py        # env-driven configuration
│   │   ├── prompts.py       # personality (edit me!)
│   │   ├── llm_client.py    # Ollama client
│   │   └── tts_client.py    # TTS backends
│   └── scripts/
│       ├── test_llm.py
│       ├── test_tts.py
│       └── run_demo.py
├── voice_samples/           # legally provided samples (git-ignored)
│   └── README.md
├── outputs/                 # generated audio (git-ignored)
└── docs/
    ├── architecture.md
    ├── phase1_scope.md
    └── future_roadmap.md
```

---

## Known limitations

- **First-pass voice only.** Coqui XTTS styling captures general timbre/cadence
  from a short sample; it is **not** a flawless clone, and we make **no
  impersonation claims**.
- **Text input only.** No speech-to-text yet — you type, it speaks.
- **No home control.** The assistant chats and talks; it cannot operate devices.
- **Docker on Apple Silicon is CPU-bound** for models — run Ollama and neural
  TTS natively for M4 GPU acceleration.
- **Local-only core.** By design there is no cloud fallback.

## Future phases

Speech-to-text, a refined voice model, Home Assistant Assist integration,
VPN/whitelisting, multi-node/offline architecture, and (opt-in, research-stage)
facial/emotion recognition and a desktop avatar. Full plan:
[docs/future_roadmap.md](docs/future_roadmap.md).

---

## Privacy & licensing notes

- All core processing is **local**. No secrets are committed — configuration is
  via `.env` (git-ignored); only `.env.example` ships.
- `outputs/`, model binaries, and `voice_samples/` are **git-ignored**.
- Use only voice samples you are **legally permitted** to use. Do not present
  generated audio as authentic recordings of a real person or claim the
  assistant *is* any specific celebrity or copyrighted character.
