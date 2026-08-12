#!/usr/bin/env python3
"""
Search the local knowledge base and print the best-matching passages.

A quick way to sanity-check retrieval quality before it is wired into the
assistant's answers (Milestone 2). Shows each hit's similarity score, domain,
and source so you can see exactly what the assistant would ground an answer on.

Usage
-----
    python src/scripts/kb_search.py "Who directed Weird Science?"
    python src/scripts/kb_search.py --domain philosophy "What is the categorical imperative?"

    # Match the backend you ingested with:
    EMBEDDING_BACKEND=hash python src/scripts/kb_search.py "your query"
"""

import sys

import _bootstrap  # noqa: F401  (adds src/ to sys.path)

from assistant.config import load_config
from assistant.knowledge.embeddings import EmbeddingError, build_embedder
from assistant.knowledge.retriever import Retriever


def main() -> int:
    argv = sys.argv[1:]
    domain = None
    if "--domain" in argv:
        i = argv.index("--domain")
        try:
            domain = argv[i + 1]
            del argv[i : i + 2]
        except IndexError:
            print("--domain requires a value", file=sys.stderr)
            return 2

    query = " ".join(argv).strip()
    if not query:
        print('Usage: kb_search.py [--domain <name>] "your question"', file=sys.stderr)
        return 2

    config = load_config()
    kb = config.knowledge

    try:
        embedder = build_embedder(kb, config.llm.endpoint)
        retriever = Retriever(kb, embedder)
    except (EmbeddingError, FileNotFoundError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    result = retriever.retrieve(query, domain=domain)
    print(f"Query   : {query}")
    if domain:
        print(f"Domain  : {domain}")
    print(f"Confident: {result.confident} "
          f"(min_score={kb.min_score}, top_k={kb.top_k})\n")

    if not result.hits:
        print("No results. Is the index built and non-empty?")
        return 0

    for i, hit in enumerate(result.hits, start=1):
        src = hit.metadata.get("source", "?")
        dom = hit.metadata.get("domain", "?")
        snippet = hit.text[:280] + ("…" if len(hit.text) > 280 else "")
        print(f"[{i}] score={hit.score:.3f}  domain={dom}  source={src}")
        print(f"    {snippet}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
