#!/usr/bin/env python3
"""
Build (or rebuild) the local knowledge-base index from source material.

Reads everything under ``knowledge_base/sources/<domain>/``, chunks it, embeds
it, and writes a local vector index. Run this whenever you add or change source
files.

Usage
-----
    # Real semantic embeddings (needs Ollama + an embedding model pulled):
    ollama pull nomic-embed-text
    python src/scripts/ingest_knowledge.py

    # Dependency-free pipeline test (no model/network needed):
    EMBEDDING_BACKEND=hash python src/scripts/ingest_knowledge.py
"""

import sys

import _bootstrap  # noqa: F401  (adds src/ to sys.path)

from assistant.config import load_config
from assistant.knowledge.embeddings import EmbeddingError, build_embedder
from assistant.knowledge.ingest import build_index


def main() -> int:
    config = load_config()
    kb = config.knowledge

    print(f"Embedding backend : {kb.embedding_backend}")
    if kb.embedding_backend == "ollama":
        print(f"Embedding model   : {kb.embedding_model}")
    print(f"Sources dir       : {kb.sources_dir}")
    print(f"Index dir         : {kb.index_dir}")
    print(f"Domains           : {', '.join(kb.domains)}\n")

    try:
        embedder = build_embedder(kb, config.llm.endpoint)
        store, report = build_index(kb, embedder, log=print)
    except EmbeddingError as exc:
        print(f"\nEmbedding error: {exc}", file=sys.stderr)
        return 1

    print("\nIngestion summary:")
    print(f"  files  : {report.files}")
    print(f"  chunks : {report.chunks}")
    if report.per_domain:
        for domain, count in sorted(report.per_domain.items()):
            print(f"    - {domain}: {count}")
    if len(store) == 0:
        print(
            "\nIndex is empty. Add source files under "
            f"{kb.sources_dir}/<domain>/ and run again."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
