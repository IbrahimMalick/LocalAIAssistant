"""
Local knowledge base (Phase 2 — "Deep Memory").

A local-first retrieval-augmented-generation (RAG) layer that gives the
assistant deep, source-grounded recall across curated domains without sending
anything to a third-party service.

Pipeline
--------
    source files  ->  loaders  ->  cleaning + chunking  ->  embeddings  ->
    local vector store  ->  retrieval  ->  grounded answers (with citations)

Milestone 1 delivers the ingestion framework, the local embedding + vector
store configuration, the domain layout, and the evaluation methodology.
"""

from .embeddings import build_embedder
from .vector_store import LocalVectorStore
from .retriever import Retriever

__all__ = ["build_embedder", "LocalVectorStore", "Retriever"]
