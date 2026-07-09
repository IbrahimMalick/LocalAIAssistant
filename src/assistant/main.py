"""
Assistant orchestration layer.

`Assistant` ties together configuration, the personality prompt, the local LLM
client, and the local TTS client. It exposes two simple operations:

* ``respond(text)``         -> get a text reply from the local model
* ``respond_with_voice()``  -> get a text reply AND synthesize spoken audio

This is the object the demo and test scripts build on.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

from .config import AssistantConfig, load_config
from .llm_client import build_llm_client
from .prompts import build_system_prompt
from .tts_client import build_tts_client


class Assistant:
    def __init__(self, config: Optional[AssistantConfig] = None) -> None:
        self.config = config or load_config()
        self.system_prompt = build_system_prompt(self.config.name)
        self.llm = build_llm_client(self.config.llm)
        self.tts = build_tts_client(self.config.tts)

    def respond(self, text: str) -> str:
        """Return the assistant's text reply for ``text``."""
        return self.llm.chat(text, system_prompt=self.system_prompt)

    def speak(self, text: str, out_path: Optional[Path] = None) -> Path:
        """Synthesize ``text`` to a local audio file and return its path."""
        return self.tts.synthesize(text, out_path=out_path)

    def respond_with_voice(
        self, text: str, out_path: Optional[Path] = None
    ) -> Tuple[str, Path]:
        """Get a reply and speak it. Returns ``(reply_text, audio_path)``."""
        reply = self.respond(text)
        audio_path = self.speak(reply, out_path=out_path)
        return reply, audio_path
