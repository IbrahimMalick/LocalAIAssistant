#!/usr/bin/env python3
"""
End-to-end Phase 1 demo.

Flow:
  1. Take a text prompt from the terminal (argument or interactive input).
  2. Send it to the local LLM and print the response.
  3. Synthesize the response to speech with the local TTS backend.
  4. Save the audio file locally (in the git-ignored outputs/ directory).

Usage
-----
    python src/scripts/run_demo.py "Tell me a fun fact about octopuses."
    python src/scripts/run_demo.py            # then type your prompt

Optional flags:
    --no-voice     Skip TTS; just print the text reply.
"""

import sys

import _bootstrap  # noqa: F401  (adds src/ to sys.path)

from assistant.config import load_config
from assistant.llm_client import LLMError
from assistant.main import Assistant
from assistant.tts_client import TTSError


def _read_prompt(args: list) -> str:
    text = " ".join(args).strip()
    if text:
        return text
    try:
        return input("You: ").strip()
    except (EOFError, KeyboardInterrupt):
        return ""


def main() -> int:
    argv = sys.argv[1:]
    no_voice = "--no-voice" in argv
    argv = [a for a in argv if a != "--no-voice"]

    prompt = _read_prompt(argv)
    if not prompt:
        print("No prompt provided. Exiting.")
        return 0

    config = load_config()
    print(f"\n[assistant: {config.name} | model: {config.llm.model} | "
          f"tts: {config.tts.backend}]\n")

    assistant = Assistant(config)

    # Step 1-2: LLM
    try:
        reply = assistant.respond(prompt)
    except LLMError as exc:
        print(f"LLM error: {exc}", file=sys.stderr)
        return 1

    print(f"{config.name}: {reply}\n")

    if no_voice:
        return 0

    # Step 3-4: TTS
    try:
        audio_path = assistant.speak(reply)
    except TTSError as exc:
        print(f"(Voice unavailable) {exc}", file=sys.stderr)
        # The text reply already succeeded, so this is a soft failure.
        return 0

    print(f"Spoken audio saved to: {audio_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
