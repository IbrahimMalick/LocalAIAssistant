# macOS Setup — Mac Mini Pro (M4)

This guide gets the base environment ready on the client's Mac Mini before
installing the model and voice pieces.

## 1. Hardware assumptions

- **Mac Mini Pro, Apple Silicon M4** (works on any recent Apple Silicon Mac).
- **16 GB unified memory minimum**; 24 GB+ recommended for comfortable
  headroom when running an 8B model alongside a TTS engine.
- ~15 GB free disk for a local model + a voice model.
- macOS 14 (Sonoma) or newer recommended.

## 2. Install the developer basics

### Xcode Command Line Tools
```bash
xcode-select --install
```

### Homebrew (package manager)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Python 3.11+
Python 3 ships with macOS, but installing via Homebrew keeps it current:
```bash
brew install python@3.11
python3 --version   # expect 3.11+ (3.10+ is fine)
```

## 3. Get the project

```bash
git clone <YOUR_REPO_URL> LocalAIAssistant
cd LocalAIAssistant
```

## 4. Create a virtual environment (optional but recommended)

The Phase 1 core has no required third-party packages, but a venv keeps any
optional extras (python-dotenv, Coqui TTS) isolated.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 5. Configure environment variables

```bash
cp .env.example .env
# edit .env to taste (model name, TTS backend, etc.)
```

## 6. Next steps

- **[model_setup.md](model_setup.md)** — install Ollama and pull a local model.
- **[voice_setup.md](voice_setup.md)** — set up local TTS and add voice samples.

## 7. (Optional) Docker Desktop

If you want to run the assistant container:
```bash
brew install --cask docker
```
Then read the notes at the top of `docker-compose.yml`. On Apple Silicon,
prefer running **Ollama natively** (M4 GPU acceleration) and only the Python
app in Docker.
