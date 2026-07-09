#!/usr/bin/env python3
"""
Smoke test for the local LLM path.

Sends a single user message to the configured local model (Ollama by default)
and prints the reply. Use this to confirm Ollama is running and the model is
pulled before wiring up voice.

Usage
-----
    python src/scripts/test_llm.py
    python src/scripts/test_llm.py "What's the weather like on Mars?"
"""

import sys

import _bootstrap  # noqa: F401  (adds src/ to sys.path)

from assistant.config import load_config
from assistant.llm_client import LLMError, build_llm_client
from assistant.prompts import build_system_prompt


def main() -> int:
    config = load_config()
    user_message = (
        " ".join(sys.argv[1:]).strip()
        or "Introduce yourself in one sentence."
    )

    print(f"Backend : {config.llm.backend}")
    print(f"Endpoint: {config.llm.endpoint}")
    print(f"Model   : {config.llm.model}")
    print(f"Prompt  : {user_message}\n")

    client = build_llm_client(config.llm)

    if not client.is_available():
        print(
            "WARNING: The local LLM server does not appear to be reachable.\n"
            "Start Ollama (`ollama serve` or launch the app) and pull the "
            f"model with `ollama pull {config.llm.model}`.\n",
            file=sys.stderr,
        )

    try:
        reply = client.chat(
            user_message, system_prompt=build_system_prompt(config.name)
        )
    except LLMError as exc:
        print(f"LLM error: {exc}", file=sys.stderr)
        return 1

    print("Assistant:")
    print(reply)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
