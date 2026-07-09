# Local LLM Setup (Ollama)

The assistant uses [Ollama](https://ollama.com) as its default local LLM
backend. Ollama runs open models natively on Apple Silicon and uses the M4
GPU via Metal — no cloud, no API keys, everything stays on the Mac.

## 1. Install Ollama

**Option A — Homebrew:**
```bash
brew install ollama
```

**Option B — Official app/installer:** download from
<https://ollama.com/download> and run it.

## 2. Start the Ollama server

If you installed the app, it runs in the menu bar automatically. Otherwise:
```bash
ollama serve
```
This exposes the local API at `http://localhost:11434` (the default the
assistant expects — see `LLM_ENDPOINT` in `.env`).

## 3. Pull a local model

The suggested default is a Mac-friendly 8B model:
```bash
ollama pull llama3.1:8b
```

Good Apple-Silicon alternatives (any of these work — set `LLM_MODEL` in `.env`):

| Model            | Pull command                | Notes                          |
|------------------|-----------------------------|--------------------------------|
| Llama 3.1 8B     | `ollama pull llama3.1:8b`   | Balanced default               |
| Qwen 2.5 7B      | `ollama pull qwen2.5:7b`    | Strong, snappy                 |
| Mistral 7B       | `ollama pull mistral:7b`    | Fast, lightweight              |
| Phi-3 Mini       | `ollama pull phi3:mini`     | Very small, low memory         |

## 4. Verify from the command line

```bash
ollama run llama3.1:8b "Say hello in one short sentence."
```

## 5. Verify through the assistant

```bash
python src/scripts/test_llm.py "Introduce yourself."
```

Expected: the script prints the backend/model info and a witty one-liner reply.

## 6. Configuration reference (`.env`)

| Variable              | Meaning                                   | Default                  |
|-----------------------|-------------------------------------------|--------------------------|
| `LLM_BACKEND`         | Backend id (Phase 1: `ollama`)            | `ollama`                 |
| `LLM_ENDPOINT`        | Ollama base URL                           | `http://localhost:11434` |
| `LLM_MODEL`           | Model tag to use                          | `llama3.1:8b`            |
| `LLM_TEMPERATURE`     | Sampling temperature                      | `0.7`                    |
| `LLM_MAX_TOKENS`      | Max tokens generated per reply            | `512`                    |
| `LLM_REQUEST_TIMEOUT` | Request timeout in seconds                | `120`                    |

## Troubleshooting

- **`Could not reach Ollama`** — make sure `ollama serve` (or the app) is
  running and `LLM_ENDPOINT` matches.
- **`HTTP 404 / model not found`** — pull the model: `ollama pull <model>`.
- **Slow first response** — the model loads into memory on first use; later
  calls are faster.
- **Running the app in Docker?** set
  `LLM_ENDPOINT=http://host.docker.internal:11434` so the container can reach
  Ollama on the Mac host.
