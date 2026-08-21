#!/usr/bin/env python3
"""
Celeste Noir — a live reading, end to end.

Flow:
  1. Take the querent's situation from the terminal (argument or prompt).
  2. Retrieve relevant knowledge from the local KB (tarot / palmistry /
     astrology / numerology / reading craft) when it's confident.
  3. Ask the local LLM to read in Celeste's voice, grounded in that knowledge.
  4. (Optional) speak the reading with the local TTS backend and save the audio.

Usage
-----
    python src/scripts/run_reading.py "Should I take the new job in Chicago?"
    python src/scripts/run_reading.py            # then type your situation
    python src/scripts/run_reading.py --no-voice "Tell me about the Tower card."
    python src/scripts/run_reading.py --no-knowledge "..."   # intuition only

Match the embedding backend you built the index with, e.g.:
    EMBEDDING_BACKEND=hash python src/scripts/run_reading.py "..."
"""

import sys

import _bootstrap  # noqa: F401  (adds src/ to sys.path)

from assistant.config import load_config
from assistant.llm_client import LLMError
from assistant.main import Assistant
from assistant.prompts import OPENING_INTRODUCTION
from assistant.tts_client import TTSError


def _read_situation(args) -> str:
    text = " ".join(args).strip()
    if text:
        return text
    try:
        return input("Your situation: ").strip()
    except (EOFError, KeyboardInterrupt):
        return ""


def main() -> int:
    argv = sys.argv[1:]
    no_voice = "--no-voice" in argv
    no_knowledge = "--no-knowledge" in argv
    argv = [a for a in argv if a not in ("--no-voice", "--no-knowledge")]

    situation = _read_situation(argv)
    if not situation:
        print("No situation provided. Exiting.")
        return 0

    config = load_config()
    assistant = Assistant(config)

    print(f"\n{config.name}:")
    print(OPENING_INTRODUCTION)
    print()

    # Show whether knowledge was pulled, for transparency.
    if not no_knowledge:
        ctx = assistant.retrieve_context(situation)
        if ctx:
            first = ctx.splitlines()[1] if len(ctx.splitlines()) > 1 else ""
            print(f"[drawing on the library... {first[:70]}]\n")
        else:
            print("[reading on intuition — no confident match in the library]\n")

    try:
        reading = assistant.give_reading(situation, use_knowledge=not no_knowledge)
    except LLMError as exc:
        print(f"LLM error: {exc}", file=sys.stderr)
        return 1

    print(f"{config.name}: {reading}\n")

    if no_voice:
        return 0

    try:
        audio_path = assistant.speak(reading)
    except TTSError as exc:
        print(f"(Voice unavailable) {exc}", file=sys.stderr)
        return 0

    print(f"Spoken reading saved to: {audio_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
