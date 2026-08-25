"""
Local LLM client abstraction.

The default backend is Ollama (https://ollama.com), which runs local models
extremely well on Apple Silicon. The client speaks Ollama's HTTP API directly
using the standard library, so there is no heavy SDK dependency.

The abstraction is deliberately small — `chat()` takes a user message and an
optional system prompt and returns the assistant's text reply. Swapping in a
different local backend (e.g. an LM Studio OpenAI-compatible endpoint) only
requires implementing the same `chat()` signature.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import List, Optional

from .config import LLMConfig


class LLMError(RuntimeError):
    """Raised when the local LLM cannot be reached or returns an error."""


class OllamaClient:
    """A minimal client for a local Ollama server."""

    def __init__(self, config: LLMConfig) -> None:
        self.config = config

    # -- public API --------------------------------------------------------
    def chat(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        history: Optional[List[dict]] = None,
    ) -> str:
        """
        Send a chat message to the local model and return the reply text.

        Parameters
        ----------
        user_message:
            The user's message.
        system_prompt:
            Optional system prompt that steers the assistant personality.
        history:
            Optional prior turns as a list of ``{"role", "content"}`` dicts.
        """
        messages: List[dict] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_message})

        payload = {
            "model": self.config.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens,
            },
        }

        url = f"{self.config.endpoint.rstrip('/')}/api/chat"
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            url, data=data, headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(
                request, timeout=self.config.request_timeout
            ) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:  # pragma: no cover - network path
            detail = exc.read().decode("utf-8", errors="replace")
            raise LLMError(
                f"Ollama returned HTTP {exc.code}. Is the model '{self.config.model}' "
                f"pulled? Try: ollama pull {self.config.model}\nDetails: {detail}"
            ) from exc
        except urllib.error.URLError as exc:  # pragma: no cover - network path
            raise LLMError(
                f"Could not reach Ollama at {self.config.endpoint}. "
                "Is Ollama running? Start it with `ollama serve` (or the app), "
                f"then pull the model with `ollama pull {self.config.model}`.\n"
                f"Underlying error: {exc.reason}"
            ) from exc
        except TimeoutError as exc:  # pragma: no cover - network path
            # A read (not connect) timeout raises a bare TimeoutError from the
            # socket layer, which urllib does not wrap in URLError.
            raise LLMError(
                f"Ollama at {self.config.endpoint} did not respond within "
                f"{self.config.request_timeout}s. The model may be slow on this "
                "machine — try a smaller model or raise LLM_REQUEST_TIMEOUT in .env."
            ) from exc

        message = body.get("message", {})
        content = message.get("content", "").strip()
        if not content:
            raise LLMError(f"Ollama returned an empty response: {body!r}")
        return content

    def is_available(self) -> bool:
        """Return True if the Ollama server responds to a version check."""
        url = f"{self.config.endpoint.rstrip('/')}/api/version"
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                return response.status == 200
        except Exception:  # pragma: no cover - network path
            return False


def build_llm_client(config: LLMConfig) -> OllamaClient:
    """
    Factory that returns an LLM client for the configured backend.

    Currently only Ollama is implemented. LM Studio exposes an
    OpenAI-compatible endpoint and can be added here in a future phase.
    """
    backend = config.backend.lower()
    if backend == "ollama":
        return OllamaClient(config)
    raise LLMError(
        f"Unsupported LLM backend '{config.backend}'. "
        "Supported in Phase 1: 'ollama'."
    )
