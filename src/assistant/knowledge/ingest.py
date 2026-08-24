"""
Ingestion orchestration.

Ties the pieces together:

    source dirs (per domain)  ->  load  ->  clean + chunk  ->  embed  ->
    local vector store on disk

This is the Milestone-1 ingestion framework. It already runs end-to-end on any
material you drop into ``knowledge_base/sources/<domain>/`` and, with
``EMBEDDING_BACKEND=hash``, needs no model or network — so the pipeline is
testable today. Milestone 2 scales this up over the full provided corpus and
wires retrieval into the assistant.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional

from ..config import KnowledgeConfig
from .chunking import Chunk, chunk_text
from .embeddings import BaseEmbedder
from .loaders import iter_source_files, load_document
from .vector_store import LocalVectorStore


@dataclass
class IngestReport:
    """Summary of an ingestion run, for logging and evaluation."""

    files: int = 0
    chunks: int = 0
    skipped: int = 0
    per_domain: dict = None  # type: ignore

    def __post_init__(self) -> None:
        if self.per_domain is None:
            self.per_domain = {}


def _collect_chunks(config: KnowledgeConfig, log: Callable[[str], None]) -> List[Chunk]:
    """Load and chunk every supported file across all configured domains."""
    all_chunks: List[Chunk] = []
    for domain in config.domains:
        domain_dir = config.sources_dir / domain
        files = iter_source_files(domain_dir)
        if not files:
            log(f"  [{domain}] no source files yet")
            continue
        domain_chunks = 0
        for path in files:
            rel = str(path.relative_to(config.sources_dir))
            try:
                text = load_document(path)
            except Exception as exc:  # keep going; report the bad file
                log(f"  [{domain}] SKIP {path.name}: {exc}")
                continue
            chunks = chunk_text(
                text,
                source=rel,
                domain=domain,
                chunk_size_words=config.chunk_size_words,
                overlap_words=config.chunk_overlap_words,
            )
            all_chunks.extend(chunks)
            domain_chunks += len(chunks)
        log(f"  [{domain}] {len(files)} file(s) -> {domain_chunks} chunk(s)")
    return all_chunks


def build_index(
    config: KnowledgeConfig,
    embedder: BaseEmbedder,
    log: Optional[Callable[[str], None]] = None,
) -> tuple:
    """
    Run the full ingestion pipeline and persist the vector index.

    Returns ``(store, report)``.
    """
    log = log or (lambda _m: None)

    log("Scanning source material...")
    chunks = _collect_chunks(config, log)
    report = IngestReport(chunks=len(chunks))
    for c in chunks:
        report.per_domain[c.domain] = report.per_domain.get(c.domain, 0) + 1

    if not chunks:
        log(
            "No chunks produced. Drop source files into "
            f"{config.sources_dir}/<domain>/ and re-run."
        )
        store = LocalVectorStore(embedder_name=embedder.name, dim=embedder.dim)
        store.save(config.index_dir)
        return store, report

    log(f"Embedding {len(chunks)} chunk(s) with {embedder.name}...")
    vectors = embedder.embed([c.embedding_text() for c in chunks])

    store = LocalVectorStore(embedder_name=embedder.name, dim=embedder.dim or len(vectors[0]))
    for chunk, vector in zip(chunks, vectors):
        store.add(
            id=chunk.chunk_id(),
            text=chunk.text,
            vector=vector,
            metadata={
                "domain": chunk.domain,
                "source": chunk.source,
                "ordinal": chunk.ordinal,
                "section": chunk.section,
            },
        )

    path = store.save(config.index_dir)
    report.files = len({c.source for c in chunks})
    log(f"Saved index with {len(store)} chunk(s) to {path}")
    return store, report
