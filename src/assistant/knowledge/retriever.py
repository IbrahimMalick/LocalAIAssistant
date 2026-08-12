"""
Retrieval interface.

Wraps an embedder + a loaded vector store and answers the core question:
"which passages best match this query, and are any of them good enough to
trust?" The ``min_score`` gate is what lets the assistant say *"I don't know"*
instead of answering from weak matches — a key Milestone-3 behaviour that is
defined here in Milestone 1.

Milestone 2 connects this retriever to the assistant's LLM prompt so answers
are grounded in, and cited from, the retrieved passages. Milestone 1 ships the
retriever and a CLI to exercise it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from ..config import KnowledgeConfig
from .embeddings import BaseEmbedder
from .vector_store import LocalVectorStore, SearchHit


@dataclass
class RetrievalResult:
    query: str
    hits: List[SearchHit]
    confident: bool  # True if the top hit clears config.min_score

    def context_block(self) -> str:
        """Format hits as a numbered, citable context block for an LLM prompt."""
        lines = []
        for i, hit in enumerate(self.hits, start=1):
            src = hit.metadata.get("source", "?")
            lines.append(f"[{i}] (source: {src})\n{hit.text}")
        return "\n\n".join(lines)


class Retriever:
    def __init__(
        self,
        config: KnowledgeConfig,
        embedder: BaseEmbedder,
        store: Optional[LocalVectorStore] = None,
    ) -> None:
        self.config = config
        self.embedder = embedder
        self.store = store or LocalVectorStore.load(config.index_dir)

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        domain: Optional[str] = None,
    ) -> RetrievalResult:
        k = top_k or self.config.top_k
        query_vec = self.embedder.embed_one(query)
        hits = self.store.search(query_vec, top_k=k, domain=domain)
        confident = bool(hits) and hits[0].score >= self.config.min_score
        return RetrievalResult(query=query, hits=hits, confident=confident)
