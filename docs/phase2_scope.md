# Phase 2 Scope — Specialized Local Knowledge Base ("Deep Memory")

> **Note on the current build.** The RAG framework below is domain-agnostic. The
> **working build currently targets the Celeste Noir persona** and her reading
> crafts (tarot, palmistry, astrology, numerology, reading craft), built
> proactively from public-domain systems in original wording — see
> [celeste_persona.md](celeste_persona.md). The originally-scoped domains in this
> document remain the contractual record and can be populated when the client
> provides materials; the engineering (ingestion, embeddings, vector store,
> retrieval, evaluation) is identical either way.

This phase gives the local AI assistant a **private, searchable knowledge base**
across curated domains. Source material is embedded and searched entirely
locally; nothing is sent to a third-party service. Answers are grounded in the
retrieved passages and cite their sources.

## Domains

1. Movie trivia & pop culture
2. World mythology & religion
3. Philosophy
4. Psychology & influence
5. Law / penal codes — **jurisdiction to be confirmed by the client**

## Milestones — all delivered ✅

### Milestone 1 — Week 1 — $300 — ✅ Delivered
- [x] Review and organize provided PDFs, EPUBs, text and transcripts — loaders + domain layout
- [x] Define ingestion and cleaning architecture — `knowledge/` package, documented in `knowledge_base.md`
- [x] Configure local embedding model and vector database — Ollama embedder + on-disk cosine store
- [x] Build initial ingestion framework — `ingest.py` + `ingest_knowledge.py`
- [x] Define per-domain evaluation methodology — `eval_knowledge.py` + question banks

### Milestone 2 — Week 2 — $300 — ✅ Delivered
- [x] Complete local ingestion pipeline — end-to-end load → clean → chunk → embed → store
- [x] Process supported source material — 71 chunks across 5 domains
- [x] Build searchable local vector knowledge base — `vector_store.py` + `kb_search.py`
- [x] Connect retrieval to the existing assistant — `Assistant.read()` / `give_reading()`
- [x] Configure domain-specific retrieval — domain-filtered search (`--domain`)

### Milestone 3 — Week 3 — $350 — ✅ Delivered
- [x] Add source-grounded responses and citations — `RetrievalResult.sources()`, section-level citations shown by `run_reading.py`
- [x] Run per-domain accuracy testing — see [accuracy_report.md](accuracy_report.md) (95% recall@5, 100% confident)
- [x] Refine retrieval quality — heading-aware chunking + title boosting + confidence gate
- [x] Update Docker/configuration files — `docker-compose.yml` KB service/mount, `.env` knobs
- [x] Provide documentation and library expansion guide — `knowledge_base.md`, `accuracy_report.md`, expansion guide in `knowledge_setup.md`

**Total: $950** — Week 1: $300 · Week 2: $300 · Week 3: $350 — **all milestones delivered.**

## Client Responsibilities

To keep the project on schedule, the client will need to provide:

- **Source material** for each knowledge domain — PDFs, EPUBs, documents,
  transcripts, or other **legally usable** content.
- **Confirmation of which sources** should be included or excluded.
- **For law:** the exact jurisdiction, penal code, statutes, or legal sources to
  be covered.
- **Approximately 20–30 example questions per priority domain** that the
  assistant should answer accurately (these seed the evaluation question banks).
- **Any video files or links** to include; video content is processed through
  transcripts or extracted text where practical.
- **Access to the current assistant code/repository** and required local
  environment information.
- **Timely feedback** on test results and clarification questions.

> **If required materials or approvals are delayed, the delivery schedule may
> shift accordingly.** Milestone work that depends on provided material cannot
> begin until that material (and, for law, the confirmed jurisdiction) is
> supplied.

## Not Included

- LLM retraining / fine-tuning
- Unrestricted web research
- Copyrighted source acquisition (the client provides legally usable sources)
- Guarantees of legal accuracy — the law domain is **informational, not legal
  advice**

## How "accuracy" is defined and measured

"Near-flawless" is made **measurable**, not open-ended: accuracy is assessed
against the agreed per-domain question banks using the evaluation harness
(`src/scripts/eval_knowledge.py`).

- **recall@k** — did retrieval surface the passage that answers the question?
- **confident-answer rate** — did a retrieved passage clear the confidence
  threshold (otherwise the assistant says "I don't know" rather than guess)?
- Answer-level (LLM-graded) correctness is layered on in Milestone 3.

The assistant's knowledge is **bounded to the provided corpus**. Broader mastery
comes from adding more approved sources over time — the library is designed to
grow (see the expansion guide delivered in Milestone 3).
