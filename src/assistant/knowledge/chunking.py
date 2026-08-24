"""
Text cleaning and chunking.

Long documents are split into overlapping, roughly paragraph-sized chunks so
that (a) each chunk fits comfortably in the embedding model's context and
(b) retrieval can point the assistant at the precise passage that answers a
question. Overlap keeps sentences that straddle a boundary retrievable.

Chunking is **heading-aware**: Markdown headings (``#`` / ``##`` / ``###``)
become a section label that is stored with each chunk and prepended to its
text. This sharpens both retrieval (the card/sign/line name travels with its
passage — e.g. "The Tower" stays attached to its meaning) and citations (a hit
can be cited as ``major_arcana.md › XVI — The Tower``). Chunks never span a
heading boundary, so each passage stays topically clean.

Chunk size is measured in words (a decent proxy for tokens) and is configurable
via ``KnowledgeConfig``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Tuple

# Collapse runs of whitespace; normalise Windows/Mac newlines first.
_WS_RE = re.compile(r"[ \t\f\v]+")
_MULTI_NL_RE = re.compile(r"\n{3,}")
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")


def clean_text(text: str) -> str:
    """Normalise whitespace without destroying paragraph structure."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [_WS_RE.sub(" ", line).strip() for line in text.split("\n")]
    text = "\n".join(lines)
    text = _MULTI_NL_RE.sub("\n\n", text)
    return text.strip()


@dataclass
class Chunk:
    """A single retrievable passage plus where it came from."""

    text: str            # clean body text, for display and prompt context
    source: str          # relative source path
    domain: str          # knowledge domain
    ordinal: int         # 0-based position within the source document
    section: str = ""     # heading path, e.g. "The Major Arcana › XVI — The Tower"

    def chunk_id(self) -> str:
        return f"{self.domain}::{self.source}::{self.ordinal}"

    def embedding_text(self) -> str:
        """
        Text used to compute the chunk's vector. The section heading is included
        with extra weight ("title boosting") so a passage stays strongly
        retrievable by its own name (e.g. a query for "The Tower" lands on the
        Tower card, not a generic passage that merely shares common words).
        """
        if self.section:
            return f"{self.section}. {self.section}. {self.text}"
        return self.text


def _split_by_heading(text: str) -> List[Tuple[str, str]]:
    """
    Split a document into (section_label, body) blocks on Markdown headings.

    The section label tracks a shallow hierarchy: the document's top heading (H1)
    plus the current sub-heading, joined with ' › '. Body text before the first
    heading is kept under an empty label.
    """
    h1 = ""
    current = ""
    blocks: List[Tuple[str, str]] = []
    buf: List[str] = []

    def label() -> str:
        parts = [p for p in (h1, current) if p]
        return " › ".join(parts)

    def flush(lbl: str) -> None:
        body = "\n".join(buf).strip()
        if body:
            blocks.append((lbl, body))
        buf.clear()

    for line in text.split("\n"):
        m = _HEADING_RE.match(line.strip())
        if m:
            flush(label())
            level = len(m.group(1))
            heading = m.group(2).strip()
            if level <= 1:
                h1 = heading
                current = ""
            else:
                current = heading
        else:
            buf.append(line)
    flush(label())
    return blocks


def _split_paragraphs(text: str) -> List[str]:
    return [p.strip() for p in text.split("\n\n") if p.strip()]


def chunk_text(
    text: str,
    source: str,
    domain: str,
    chunk_size_words: int = 220,
    overlap_words: int = 40,
) -> List[Chunk]:
    """
    Split cleaned text into overlapping, heading-scoped word-window chunks.

    Each Markdown section is chunked independently (chunks never cross a heading),
    the section label is stored on the chunk, and the label is prepended to the
    chunk text so the heading's terms are embedded and searchable with the body.
    """
    text = clean_text(text)
    if not text:
        return []

    if overlap_words >= chunk_size_words:
        overlap_words = max(0, chunk_size_words // 4)

    chunks: List[Chunk] = []
    ordinal = 0

    for section, body in _split_by_heading(text):
        current: List[str] = []

        def flush() -> None:
            nonlocal current, ordinal
            if not current:
                return
            body_text = " ".join(current).strip()
            chunks.append(
                Chunk(
                    text=body_text,
                    source=source,
                    domain=domain,
                    ordinal=ordinal,
                    section=section,
                )
            )
            ordinal += 1
            current = current[-overlap_words:] if overlap_words else []

        for para in _split_paragraphs(body):
            words = para.split()
            if len(words) > chunk_size_words:  # hard-split an oversized paragraph
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
