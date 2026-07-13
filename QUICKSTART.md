# Quick Start — Commands the client runs on the Mac Mini

The complete "first run" sequence to prove the assistant works on the client's
own machine. **One** command to get the code, **one** to configure it, **two**
to install/start the AI engine, and **three** quick tests (brain, voice, full
demo) to confirm everything works before real use.

> Run these in **Terminal** on the Mac Mini Pro (M4), in order.

| # | Command | What it does |
|---|---------|--------------|
| 1 | `git clone <repo-url> LocalAIAssistant && cd LocalAIAssistant` | Downloads the project from GitHub onto the Mac Mini and moves into that folder. |
| 2 | `cp .env.example .env` | Creates the local configuration file from the template. This is where you set the assistant's name, model choice, etc. **No secrets involved.** |
| 3 | `brew install ollama && ollama serve` | Installs Ollama (the tool that runs the local AI model) and starts its background service so it's ready to answer requests. |
| 4 | `ollama pull llama3.1:8b` | Downloads the actual AI model (~4.7 GB) that powers the assistant's brain — this is the one-time model download. |
| 5 | `python src/scripts/test_llm.py "Introduce yourself in one sentence."` | Quick test that sends a message to the local model and prints its reply — confirms the **"thinking"** part works. |
| 6 | `python src/scripts/test_tts.py "Hello from your local assistant."` | Quick test that converts text to spoken audio — confirms the **"voice"** part works. See the note below about `TTS_BACKEND=say`. |
| 7 | `python src/scripts/run_demo.py "Tell me a fun fact about octopuses."` | The full demo — sends a prompt, gets a reply from the local AI, and speaks it out loud. This is the one command that shows the whole thing working end-to-end. |

## Notes

- **Step 3 — leave Ollama running.** `ollama serve` runs in the foreground. If
  you installed the Ollama menu-bar app, it already runs the service for you and
  you can skip `ollama serve`. Otherwise, open a **second Terminal tab** for
  steps 4–7 so Ollama keeps running.
- **Step 6 — instant voice with zero installs.** On a Mac, set `TTS_BACKEND=say`
  in your `.env` first. This uses macOS's built-in voice, so the voice test
  works immediately with nothing else to install. To upgrade to a nicer neural
  voice (Piper) or sample-based voice styling (Coqui XTTS) later, see
  [setup/voice_setup.md](setup/voice_setup.md).
- **Where the audio goes.** Generated audio is saved in the `outputs/` folder
  (git-ignored). Play it on macOS with, e.g.,
  `afplay outputs/assistant_reply.aiff`.
- **Python.** These commands assume Python 3.10+ (`python` may be `python3` on
  your system). The core has no required third-party packages. Full macOS
  bootstrap: [setup/macos_setup.md](setup/macos_setup.md).

## If something doesn't work

| Symptom | Fix |
|---------|-----|
| `Could not reach Ollama` | Make sure `ollama serve` (or the menu-bar app) is running. |
| `model not found` / HTTP 404 | Run `ollama pull llama3.1:8b` (step 4). |
| Voice test errors about Piper | Set `TTS_BACKEND=say` in `.env` for the instant macOS voice. |
| `python: command not found` | Use `python3` instead of `python`. |

For deeper setup and troubleshooting, see the guides in [`setup/`](setup/) and
the main [README](README.md).
