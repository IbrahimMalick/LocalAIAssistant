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

## Milestones

### Milestone 1 — Week 1 — $300
- Review and organize provided PDFs, EPUBs, text and transcripts
- Define ingestion and cleaning architecture
- Configure local embedding model and vector database
- Build initial ingestion framework
- Define per-domain evaluation methodology

### Milestone 2 — Week 2 — $300
- Complete local ingestion pipeline
- Process supported source material
- Build searchable local vector knowledge base
- Connect retrieval to the existing assistant
- Configure domain-specific retrieval

### Milestone 3 — Week 3 — $350
- Add source-grounded responses and citations
- Run per-domain accuracy testing
- Refine retrieval quality
- Update Docker/configuration files
- Provide documentation and library expansion guide

**Total: $950** — Week 1: $300 · Week 2: $300 · Week 3: $350

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
