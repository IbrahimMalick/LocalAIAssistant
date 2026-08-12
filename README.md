# Local AI Assistant — Phase 1 MVP

A **local-first** AI assistant foundation that runs entirely on a Mac Mini Pro
(M4). It pairs a local LLM (via [Ollama](https://ollama.com)) with an original,
configurable personality and a local text-to-speech voice. No cloud, no API
keys — the core loop never leaves the house.

> **Phase 1 is a foundation, not the finished product.** It does text-in →
> witty reply → local spoken audio. Home control, voice input, network
> isolation, and a refined voice clone are future phases (see below).

> 🚀 **In a hurry?** The complete first-run command sequence for the client is
> in **[QUICKSTART.md](QUICKSTART.md)** — clone, configure, install Ollama,
> pull the model, and run three quick tests.

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
│   ├── voice_setup.md
│   └── knowledge_setup.md   # Phase 2: load sources, build & test the KB
├── src/
│   ├── assistant/
│   │   ├── __init__.py
│   │   ├── main.py          # Assistant orchestration
│   │   ├── config.py        # env-driven configuration
│   │   ├── prompts.py       # personality (edit me!)
│   │   ├── llm_client.py    # Ollama client
│   │   ├── tts_client.py    # TTS backends
│   │   └── knowledge/       # Phase 2: local knowledge base (RAG)
│   │       ├── loaders.py       # read txt/md/transcripts/pdf/epub
│   │       ├── chunking.py      # clean + split into chunks
│   │       ├── embeddings.py    # local embeddings (Ollama / hash fallback)
│   │       ├── vector_store.py  # on-disk cosine search
│   │       ├── ingest.py        # orchestration
│   │       └── retriever.py     # query → grounded, citable passages
│   └── scripts/
│       ├── test_llm.py
│       ├── test_tts.py
│       ├── run_demo.py
│       ├── ingest_knowledge.py  # build the knowledge index
│       ├── kb_search.py         # test retrieval
│       └── eval_knowledge.py    # per-domain accuracy metrics
├── knowledge_base/          # Phase 2: sources (git-ignored), eval banks, index
│   ├── sources/<domain>/
│   ├── eval/<domain>.json
│   └── index/               # generated (git-ignored)
├── voice_samples/           # legally provided samples (git-ignored)
│   └── README.md
├── outputs/                 # generated audio (git-ignored)
└── docs/
    ├── architecture.md
    ├── phase1_scope.md
    ├── phase2_scope.md      # KB scope, milestones, client responsibilities
    ├── knowledge_base.md    # KB architecture & evaluation methodology
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

## Phase 2 — Specialized Local Knowledge Base ("Deep Memory") · in progress

Gives the assistant deep, source-grounded recall across five curated domains
(movies & pop culture, mythology & religion, philosophy, psychology & influence,
law & penal codes) — all local, all private. It searches a curated library and
answers from it with citations, and says "I don't know" instead of guessing.

Quick start (dependency-free demo, no model or network needed):

```bash
EMBEDDING_BACKEND=hash python src/scripts/ingest_knowledge.py   # build index
EMBEDDING_BACKEND=hash python src/scripts/kb_search.py "What is the categorical imperative?"
EMBEDDING_BACKEND=hash python src/scripts/eval_knowledge.py     # accuracy metrics
```

For real semantic search, pull a local embedding model
(`ollama pull nomic-embed-text`) and drop source files into
`knowledge_base/sources/<domain>/`. Full guide:
[setup/knowledge_setup.md](setup/knowledge_setup.md) · architecture:
[docs/knowledge_base.md](docs/knowledge_base.md) · scope & milestones:
[docs/phase2_scope.md](docs/phase2_scope.md).

> **Milestone 1 (delivered):** ingestion framework, local embedding + vector-DB
> configuration, domain layout, and the evaluation methodology. Milestones 2–3
> scale ingestion over the provided corpus, wire retrieval into the assistant's
> answers with citations, and run per-domain accuracy testing.

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
