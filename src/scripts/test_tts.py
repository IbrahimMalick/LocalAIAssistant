#!/usr/bin/env python3
"""
Smoke test for the local TTS path.

Converts a line of text into a local audio file using the configured TTS
backend and prints where the file was saved. This does NOT require the LLM,
so you can verify voice output independently.

Usage
-----
    python src/scripts/test_tts.py
    python src/scripts/test_tts.py "Testing, testing, one two three."
"""

import sys

import _bootstrap  # noqa: F401  (adds src/ to sys.path)

from assistant.config import load_config
from assistant.tts_client import TTSError, build_tts_client


def main() -> int:
    config = load_config()
    text = (
        " ".join(sys.argv[1:]).strip()
        or "Hi! This is a local text to speech test running on your Mac Mini."
    )

    print(f"TTS backend: {config.tts.backend}")
    print(f"Text       : {text}\n")

    client = build_tts_client(config.tts)
    try:
        out_path = client.synthesize(text)
    except TTSError as exc:
        print(f"TTS error: {exc}", file=sys.stderr)
        return 1

    print(f"Saved audio to: {out_path}")
    print("Open it to listen (on macOS: `afplay` the file, or double-click it).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
