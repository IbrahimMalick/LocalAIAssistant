# Knowledge Base Architecture ("Deep Memory")

The knowledge base is a **local-first retrieval-augmented generation (RAG)**
layer. Instead of relying only on what the LLM memorized during training, the
assistant searches a curated local library and answers grounded in it — citing
the passages it used, and declining when it has no good match.

## Pipeline

```
 source files                 knowledge_base/sources/<domain>/*.{txt,md,vtt,srt,pdf,epub}
      │
      ▼   loaders.py           read → plain text (transcripts de-timestamped)
      │
      ▼   chunking.py          clean + split into overlapping word-window chunks
      │
      ▼   embeddings.py        each chunk → vector (local: Ollama, or hash fallback)
      │
      ▼   vector_store.py      persisted to knowledge_base/index/vector_store.json
      │
      ▼   retriever.py         query → embed → cosine search → top-k passages
      │                        (min_score gate → "I don't know" when weak)
      ▼
   assistant answer            grounded + cited   (LLM wiring lands in Milestone 2)
```

## Components (Milestone 1)

| Module | Responsibility |
|--------|----------------|
| `knowledge/loaders.py` | Read `.txt/.md`, `.vtt/.srt` transcripts, `.pdf` (via `pypdf`), `.epub` into clean text |
| `knowledge/chunking.py` | Normalize whitespace; split into overlapping, paragraph-aware chunks |
| `knowledge/embeddings.py` | Local embeddings — `OllamaEmbedder` (default) or dependency-free `HashingEmbedder` |
| `knowledge/vector_store.py` | On-disk cosine-similarity store; small interface, swappable for Chroma/FAISS/Qdrant later |
| `knowledge/ingest.py` | Orchestrates load → chunk → embed → store, per domain |
| `knowledge/retriever.py` | Query → ranked passages + confidence gate + citable context block |

## Local by design

- **Embeddings** are produced by a local model served by Ollama
  (`nomic-embed-text` by default) over `localhost` — the same offline posture as
  the LLM and TTS. Pull it once: `ollama pull nomic-embed-text`.
- **Vectors** live in a single JSON file under `knowledge_base/index/`
  (git-ignored, rebuildable). No external database, no cloud.
- **The `hash` embedding backend** is a deterministic, dependency-free fallback
  so the entire pipeline can be built, tested, and demoed with no model and no
  network (used for CI and for the demo `sample_*.md` files). It does
  keyword-overlap matching only — real semantic quality comes from the Ollama
  embedder on the full corpus.

## Why a custom vector store (for now)

For this project's corpus sizes, a transparent JSON-backed cosine store is
correct, inspectable, and dependency-light — matching the repo's local-first,
minimal-dependency philosophy. The `LocalVectorStore` interface
(`add`/`search`/`save`/`load`) is deliberately tiny so it can be swapped for
Chroma, FAISS, LanceDB, or Qdrant if corpus growth ever demands it, without
touching loaders, chunking, embeddings, or retrieval.

## Evaluation methodology

Accuracy is measured against per-domain question banks in
`knowledge_base/eval/<domain>.json`. Each question declares
`expected_keywords` and an optional `expected_source`. A question is a
retrieval hit when a top-k chunk comes from the expected source or contains an
expected keyword. `src/scripts/eval_knowledge.py` reports **recall@k** and the
**confident-answer rate** per domain and overall. This turns "near-flawless"
into a number tied to an agreed corpus and question set (see
[phase2_scope.md](phase2_scope.md)).

## Configuration

All knobs are environment-driven (see `.env.example`): `EMBEDDING_BACKEND`,
`EMBEDDING_MODEL`, `KB_CHUNK_SIZE_WORDS`, `KB_CHUNK_OVERLAP_WORDS`, `KB_TOP_K`,
`KB_MIN_SCORE`. Defaults live in `KnowledgeConfig` in `assistant/config.py`.

## What's next

- **Milestone 2:** scale ingestion over the full provided corpus; wire the
  retriever into the assistant's LLM prompt for grounded answers; tune
  domain-specific retrieval.
- **Milestone 3:** source citations in responses, per-domain accuracy testing
  with the real embedder, retrieval-quality refinement, Docker/config updates,
  and the library-expansion guide.
