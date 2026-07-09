# Phase 1 Scope

Phase 1 delivers the **foundation** of a local-first AI assistant: a working
local LLM, an original personality, local voice output, a first-pass voice-style
test path, Docker packaging, and clear documentation.

## ✅ Included in Phase 1

| Area                | What's delivered                                                        |
|---------------------|-------------------------------------------------------------------------|
| Local LLM           | Ollama backend, configurable model/endpoint/temperature/system prompt   |
| LLM test            | `scripts/test_llm.py` sends a message and prints the reply              |
| Personality         | Editable, original witty/confident/playful persona in `prompts.py`      |
| Local TTS           | Abstraction with Piper, Coqui XTTS, macOS `say`, and `none` backends     |
| Voice styling       | First-pass XTTS styling from **legally provided** samples (experimental) |
| TTS test            | `scripts/test_tts.py` converts text to a local audio file               |
| Demo                | `scripts/run_demo.py`: prompt → LLM reply → spoken audio → saved locally |
| Docker              | `Dockerfile` + `docker-compose.yml` with macOS-realistic guidance       |
| Docs                | README, setup guides, architecture, scope, roadmap                      |
| Privacy             | Local-only core loop; secrets via `.env`; strict `.gitignore`           |

## ❌ Explicitly excluded from Phase 1

These are intentionally **not** built yet (planned for later phases):

- **Production Home Assistant integration** — no device control / HA Assist.
- **VPN / network whitelisting** — no network isolation layer.
- **Facial recognition** — none.
- **Emotion recognition** — none.
- **Desktop avatar / on-screen companion** — none.
- **Automation control** — the assistant cannot trigger home automations.
- **Speech-to-text (voice input)** — Phase 1 is text-in, voice-out.
- **Perfect / guaranteed celebrity voice clone** — first-pass styling only,
  with no impersonation claims.
- **Multi-node / offline cluster architecture** — single Mac Mini host only.

## Definition of done (Phase 1)

- [x] `test_llm.py` returns a model reply against local Ollama.
- [x] `test_tts.py` produces a local audio file from at least one backend.
- [x] `run_demo.py` runs prompt → reply → speech → saved audio end to end.
- [x] Personality is editable in one file without touching app logic.
- [x] No secrets, no copyrighted audio, no large model binaries in the repo.
- [x] README documents install, model pull, `.env`, tests, demo, and limits.

## Known limitations

- Voice styling is a **first pass**; fidelity depends on sample quality and is
  not a flawless clone.
- Neural TTS and the LLM perform best **natively on macOS**; Docker on Apple
  Silicon is CPU-bound for models.
- No voice input yet — interaction is via typed prompts.
