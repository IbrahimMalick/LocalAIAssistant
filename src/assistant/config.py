"""
Central configuration for the local AI assistant.

All values are read from environment variables (see `.env.example`) so that
nothing sensitive or machine-specific is hard-coded. Copy `.env.example` to
`.env`, adjust values, and the assistant will pick them up automatically.

Nothing here should ever contain a secret or an API key committed to git.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Optional .env loading
# ---------------------------------------------------------------------------
# We load .env manually (no hard dependency on python-dotenv) so the project
# stays lightweight. If python-dotenv is installed it will be used, otherwise
# we fall back to a tiny parser.
def _load_dotenv() -> None:
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return
    try:
        from dotenv import load_dotenv  # type: ignore

        load_dotenv(env_path)
        return
    except ImportError:
        pass

    # Minimal fallback parser for KEY=VALUE lines.
    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        # Do not override values already present in the real environment.
        os.environ.setdefault(key, value)


_load_dotenv()


def _get(name: str, default: str) -> str:
    return os.environ.get(name, default)


def _get_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


def _get_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUTS_DIR = PROJECT_ROOT / _get("OUTPUTS_DIR", "outputs")
VOICE_SAMPLES_DIR = PROJECT_ROOT / _get("VOICE_SAMPLES_DIR", "voice_samples")

# Knowledge base (Phase 2 — "Deep Memory") paths.
KB_DIR = PROJECT_ROOT / _get("KB_DIR", "knowledge_base")
KB_SOURCES_DIR = KB_DIR / "sources"   # raw source material (git-ignored, client-provided)
KB_INDEX_DIR = KB_DIR / "index"       # generated vector index (git-ignored)
KB_EVAL_DIR = KB_DIR / "eval"         # question banks per domain (committed templates)

# The knowledge domains that make up Celeste Noir's "Deep Memory". Each maps to
# a subfolder under KB_SOURCES_DIR and its own evaluation question bank. Editing
# this list is the single place that defines which crafts she can draw on.
#
# Content is built from traditional, public-domain reading systems, written in
# original wording (see docs/celeste_persona.md and docs/knowledge_base.md).
KB_DOMAINS = [
    "tarot",
    "palmistry",
    "astrology",
    "numerology",
    "reading_craft",
]


@dataclass
class LLMConfig:
    """Configuration for the local LLM backend (Ollama by default)."""

    backend: str = field(default_factory=lambda: _get("LLM_BACKEND", "ollama"))
    endpoint: str = field(
        default_factory=lambda: _get("LLM_ENDPOINT", "http://localhost:11434")
    )
    model: str = field(default_factory=lambda: _get("LLM_MODEL", "llama3.1:8b"))
    temperature: float = field(
        default_factory=lambda: _get_float("LLM_TEMPERATURE", 0.7)
    )
    # Max tokens the model is allowed to generate in a single response.
    max_tokens: int = field(default_factory=lambda: _get_int("LLM_MAX_TOKENS", 512))
    # Seconds before an LLM request is abandoned.
    request_timeout: int = field(
        default_factory=lambda: _get_int("LLM_REQUEST_TIMEOUT", 120)
    )


@dataclass
class TTSConfig:
    """Configuration for the local text-to-speech backend."""

    # One of: "piper", "coqui", "say" (macOS built-in), "none".
    backend: str = field(default_factory=lambda: _get("TTS_BACKEND", "piper"))

    # Piper-specific settings.
    piper_binary: str = field(default_factory=lambda: _get("PIPER_BINARY", "piper"))
    piper_model: str = field(
        default_factory=lambda: _get(
            "PIPER_MODEL", "voices/en_US-lessac-medium.onnx"
        )
    )

    # Coqui XTTS-specific settings.
    coqui_model: str = field(
        default_factory=lambda: _get(
            "COQUI_MODEL", "tts_models/multilingual/multi-dataset/xtts_v2"
        )
    )
    # Optional path to a provided voice sample used by XTTS for voice styling.
    # Leave empty to use the model's default speaker.
    coqui_speaker_wav: str = field(
        default_factory=lambda: _get("COQUI_SPEAKER_WAV", "")
    )
    coqui_language: str = field(default_factory=lambda: _get("COQUI_LANGUAGE", "en"))

    # Where generated audio is written. Always inside the (git-ignored) outputs dir.
    output_dir: Path = field(default_factory=lambda: OUTPUTS_DIR)


@dataclass
class KnowledgeConfig:
    """
    Configuration for the local knowledge base (Phase 2 — "Deep Memory").

    The whole pipeline is local-first: embeddings are produced by a local model
    (Ollama by default) and vectors are stored on disk. Nothing is sent to a
    third-party service.
    """

    # -- Embeddings --------------------------------------------------------
    # "ollama" -> local embedding model served by Ollama (default, recommended)
    # "hash"   -> deterministic dependency-free fallback for headless/CI runs
    #             and pipeline testing when no embedding model is available.
    embedding_backend: str = field(
        default_factory=lambda: _get("EMBEDDING_BACKEND", "ollama")
    )
    # Local embedding model tag. Pull it once with: `ollama pull nomic-embed-text`.
    embedding_model: str = field(
        default_factory=lambda: _get("EMBEDDING_MODEL", "nomic-embed-text")
    )
    # Vector dimension used by the "hash" fallback embedder only.
    hash_embedding_dim: int = field(
        default_factory=lambda: _get_int("HASH_EMBEDDING_DIM", 512)
    )

    # -- Chunking ----------------------------------------------------------
    # Target chunk size and overlap, measured in words (approximate tokens).
    chunk_size_words: int = field(
        default_factory=lambda: _get_int("KB_CHUNK_SIZE_WORDS", 220)
    )
    chunk_overlap_words: int = field(
        default_factory=lambda: _get_int("KB_CHUNK_OVERLAP_WORDS", 40)
    )

    # -- Retrieval ---------------------------------------------------------
    # How many chunks to retrieve for a query by default.
    top_k: int = field(default_factory=lambda: _get_int("KB_TOP_K", 5))
    # Minimum cosine similarity for a chunk to count as a real hit. Below this
    # the assistant should say "I don't know" rather than answer from noise.
    min_score: float = field(default_factory=lambda: _get_float("KB_MIN_SCORE", 0.2))

    # -- Paths -------------------------------------------------------------
    sources_dir: Path = field(default_factory=lambda: KB_SOURCES_DIR)
    index_dir: Path = field(default_factory=lambda: KB_INDEX_DIR)
    eval_dir: Path = field(default_factory=lambda: KB_EVAL_DIR)
    domains: list = field(default_factory=lambda: list(KB_DOMAINS))

    # Seconds before an embedding request is abandoned.
    request_timeout: int = field(
        default_factory=lambda: _get_int("EMBEDDING_REQUEST_TIMEOUT", 120)
    )


@dataclass
class AssistantConfig:
    """Top-level assistant configuration."""

    name: str = field(default_factory=lambda: _get("ASSISTANT_NAME", "Celeste Noir"))
    llm: LLMConfig = field(default_factory=LLMConfig)
    tts: TTSConfig = field(default_factory=TTSConfig)
    knowledge: KnowledgeConfig = field(default_factory=KnowledgeConfig)


def load_config() -> AssistantConfig:
    """Build and return the assistant configuration from the environment."""
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    KB_INDEX_DIR.mkdir(parents=True, exist_ok=True)
    return AssistantConfig()


if __name__ == "__main__":
    # Quick sanity check: `python -m assistant.config`
    cfg = load_config()
    print("Assistant name :", cfg.name)
    print("LLM backend    :", cfg.llm.backend)
    print("LLM endpoint   :", cfg.llm.endpoint)
    print("LLM model      :", cfg.llm.model)
    print("LLM temperature:", cfg.llm.temperature)
    print("TTS backend    :", cfg.tts.backend)
    print("Outputs dir    :", OUTPUTS_DIR)
