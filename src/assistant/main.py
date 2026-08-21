"""
Assistant orchestration layer.

`Assistant` ties together configuration, the personality prompt, the local LLM
client, the local knowledge base (RAG), and the local TTS client.

Operations:
* ``respond(text)``         -> text reply from the local model
* ``give_reading(text)``    -> a knowledge-grounded reading (retrieval + LLM)
* ``respond_with_voice()``  -> reply AND synthesized spoken audio

This is the object the demo and test scripts build on.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple

from .config import AssistantConfig, load_config
from .llm_client import build_llm_client
from .prompts import build_reading_prompt, build_system_prompt
from .tts_client import build_tts_client


class Assistant:
    def __init__(self, config: Optional[AssistantConfig] = None) -> None:
        self.config = config or load_config()
        self.system_prompt = build_system_prompt(self.config.name)
        self.llm = build_llm_client(self.config.llm)
        self.tts = build_tts_client(self.config.tts)
        self._retriever = None  # built lazily; the KB is optional

    # -- knowledge base (lazy, optional) -----------------------------------
    def _get_retriever(self):
        """
        Build the retriever on first use. Returns None (rather than raising) if
        the index or embedder isn't available, so a reading still works on
        intuition alone when the knowledge base hasn't been built yet.
        """
        if self._retriever is not None:
            return self._retriever
        try:
            from .knowledge.embeddings import build_embedder
            from .knowledge.retriever import Retriever

            embedder = build_embedder(self.config.knowledge, self.config.llm.endpoint)
            self._retriever = Retriever(self.config.knowledge, embedder)
        except Exception:
            self._retriever = None
        return self._retriever

    def retrieve_context(self, query: str) -> str:
        """Return a citable context block of relevant knowledge, or ''."""
        retriever = self._get_retriever()
        if retriever is None:
            return ""
        try:
            result = retriever.retrieve(query)
        except Exception:
            return ""
        if not result.hits or not result.confident:
            return ""
        return result.context_block()

    # -- generation --------------------------------------------------------
    def respond(self, text: str) -> str:
        """Return the assistant's text reply for ``text``."""
        return self.llm.chat(text, system_prompt=self.system_prompt)

    def give_reading(self, situation: str, use_knowledge: bool = True) -> str:
        """
        Give a reading grounded in the local knowledge base when relevant.

        Retrieves matching passages (tarot, palmistry, astrology, numerology,
        or reading craft), injects them into the prompt, and asks the model to
        read in Celeste's voice. Falls back to intuition-only if no confident
        knowledge is found or the KB isn't built.
        """
        context = self.retrieve_context(situation) if use_knowledge else ""
        prompt = build_reading_prompt(situation, context)
        return self.llm.chat(prompt, system_prompt=self.system_prompt)

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
