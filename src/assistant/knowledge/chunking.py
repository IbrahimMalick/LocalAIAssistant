"""
Text cleaning and chunking.

Long documents are split into overlapping, roughly paragraph-sized chunks so
that (a) each chunk fits comfortably in the embedding model's context and
(b) retrieval can point the assistant at the precise passage that answers a
question. Overlap keeps sentences that straddle a boundary retrievable.

Chunk size is measured in words (a decent proxy for tokens) and is configurable
via ``KnowledgeConfig``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List

# Collapse runs of whitespace; normalise Windows/Mac newlines first.
_WS_RE = re.compile(r"[ \t\f\v]+")
_MULTI_NL_RE = re.compile(r"\n{3,}")


def clean_text(text: str) -> str:
    """Normalise whitespace without destroying paragraph structure."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Normalise spaces/tabs on each line, preserving newlines.
    lines = [_WS_RE.sub(" ", line).strip() for line in text.split("\n")]
    text = "\n".join(lines)
    text = _MULTI_NL_RE.sub("\n\n", text)
    return text.strip()


@dataclass
class Chunk:
    """A single retrievable passage plus where it came from."""

    text: str
    source: str          # relative source path
    domain: str          # knowledge domain
    ordinal: int         # 0-based position within the source document

    def chunk_id(self) -> str:
        return f"{self.domain}::{self.source}::{self.ordinal}"


def _split_paragraphs(text: str) -> List[str]:
    paras = [p.strip() for p in text.split("\n\n")]
    return [p for p in paras if p]


def chunk_text(
    text: str,
    source: str,
    domain: str,
    chunk_size_words: int = 220,
    overlap_words: int = 40,
) -> List[Chunk]:
    """
    Split cleaned text into overlapping word-window chunks.

    Paragraph boundaries are respected where possible: we accumulate whole
    paragraphs until adding the next one would exceed ``chunk_size_words``,
    then emit a chunk and carry ``overlap_words`` of trailing context forward.
    A single oversized paragraph is hard-split by words.
    """
    text = clean_text(text)
    if not text:
        return []

    if overlap_words >= chunk_size_words:
        overlap_words = max(0, chunk_size_words // 4)

    chunks: List[Chunk] = []
    ordinal = 0
    current: List[str] = []          # words in the in-progress chunk

    def flush() -> None:
        nonlocal current, ordinal
        if not current:
            return
        chunks.append(
            Chunk(
                text=" ".join(current).strip(),
                source=source,
                domain=domain,
                ordinal=ordinal,
            )
        )
        ordinal += 1
        # Carry the last ``overlap_words`` forward as context for the next chunk.
        current = current[-overlap_words:] if overlap_words else []

    for para in _split_paragraphs(text):
        words = para.split()
        # Hard-split a paragraph that is itself larger than a whole chunk.
        if len(words) > chunk_size_words:
            i = 0
            while i < len(words):
                room = chunk_size_words - len(current)
                if room <= 0:
                    flush()
                    room = chunk_size_words - len(current)
                current.extend(words[i : i + room])
                i += room
                if len(current) >= chunk_size_words:
                    flush()
            continue

        if len(current) + len(words) > chunk_size_words:
            flush()
        current.extend(words)

    flush()
    return chunks
