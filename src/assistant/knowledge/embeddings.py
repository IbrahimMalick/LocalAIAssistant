"""
Local embedding backends.

Embeddings turn text into vectors so we can search by meaning. Everything here
runs locally:

* ``OllamaEmbedder`` (default) calls a local embedding model served by Ollama
  (e.g. ``nomic-embed-text``) over its HTTP API using only the standard
  library — the same dependency-free approach as ``llm_client.py``.

* ``HashingEmbedder`` is a deterministic, dependency-free fallback. It does not
  understand language the way a neural model does, but it produces stable
  vectors so the whole ingestion/retrieval pipeline can be built, tested, and
  demonstrated on any machine (headless, CI, or before the embedding model is
  pulled). Set ``EMBEDDING_BACKEND=hash`` to use it.

The two share one tiny interface: ``embed(texts) -> list[list[float]]``.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import urllib.error
import urllib.request
from typing import List

from ..config import KnowledgeConfig


class EmbeddingError(RuntimeError):
    """Raised when embeddings cannot be produced."""


class BaseEmbedder:
    """Common interface for embedding backends."""

    #: Vector dimension produced by this embedder (set by subclasses).
    dim: int = 0
    #: Short identifier stored alongside vectors so a mismatched index can be
    #: detected (you must re-index if you change embedder).
    name: str = "base"

    def embed(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError

    def embed_one(self, text: str) -> List[float]:
        return self.embed([text])[0]


class OllamaEmbedder(BaseEmbedder):
    """Embeddings from a local Ollama embedding model."""

    def __init__(self, config: KnowledgeConfig, endpoint: str) -> None:
        self.config = config
        self.endpoint = endpoint.rstrip("/")
        self.name = f"ollama:{config.embedding_model}"
        # dim is discovered lazily on first embed (model-dependent).
        self.dim = 0

    def embed(self, texts: List[str]) -> List[List[float]]:
        vectors: List[List[float]] = []
        for text in texts:
            vectors.append(self._embed_single(text))
        if vectors:
            self.dim = len(vectors[0])
        return vectors

    def _embed_single(self, text: str) -> List[float]:
        payload = {"model": self.config.embedding_model, "prompt": text}
        url = f"{self.endpoint}/api/embeddings"
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
            raise EmbeddingError(
                f"Ollama returned HTTP {exc.code} for embeddings. Is the model "
                f"'{self.config.embedding_model}' pulled? Try: "
                f"ollama pull {self.config.embedding_model}\nDetails: {detail}"
            ) from exc
        except urllib.error.URLError as exc:  # pragma: no cover - network path
            raise EmbeddingError(
                "Could not reach Ollama for embeddings. Start it with "
                "`ollama serve`, then pull the embedding model with "
                f"`ollama pull {self.config.embedding_model}`. You can also set "
                "EMBEDDING_BACKEND=hash to build/test the pipeline without a "
                f"model.\nUnderlying error: {exc.reason}"
            ) from exc

        embedding = body.get("embedding")
        if not embedding:
            raise EmbeddingError(f"Ollama returned no embedding: {body!r}")
        return [float(x) for x in embedding]


_TOKEN_RE = re.compile(r"[a-z0-9]+")


class HashingEmbedder(BaseEmbedder):
    """
    Deterministic bag-of-words hashing embedder (no dependencies, no model).

    Each token is hashed into one of ``dim`` buckets with a signed weight; the
    resulting vector is L2-normalised. Overlapping vocabulary between a query
    and a chunk yields a positive cosine similarity, so retrieval returns
    sensible (if unsophisticated) results — enough to validate the pipeline
    end-to-end. Swap in ``OllamaEmbedder`` for real semantic search.
    """

    def __init__(self, dim: int = 512) -> None:
        self.dim = dim
        self.name = f"hash:{dim}"

    def embed(self, texts: List[str]) -> List[List[float]]:
        return [self._embed_single(t) for t in texts]

    def _embed_single(self, text: str) -> List[float]:
        vec = [0.0] * self.dim
        for token in _TOKEN_RE.findall(text.lower()):
            digest = hashlib.md5(token.encode("utf-8")).digest()
            bucket = int.from_bytes(digest[:4], "big") % self.dim
            sign = 1.0 if digest[4] & 1 else -1.0
            vec[bucket] += sign
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec


def build_embedder(config: KnowledgeConfig, llm_endpoint: str) -> BaseEmbedder:
    """Return the embedding backend selected by ``EMBEDDING_BACKEND``."""
    backend = config.embedding_backend.lower()
    if backend == "ollama":
        return OllamaEmbedder(config, llm_endpoint)
    if backend == "hash":
        return HashingEmbedder(config.hash_embedding_dim)
    raise EmbeddingError(
        f"Unsupported EMBEDDING_BACKEND '{config.embedding_backend}'. "
        "Choose 'ollama' (local model) or 'hash' (dependency-free fallback)."
    )
