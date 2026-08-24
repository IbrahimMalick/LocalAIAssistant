# Accuracy Report — Knowledge Base (Milestone 3)

Per-domain retrieval accuracy for Celeste's knowledge base, measured against the
committed question banks in `knowledge_base/eval/`.

## Metrics

- **recall@k** — the share of questions whose answering passage appears in the
  top-`k` retrieved chunks (did retrieval fetch the right passage?).
- **confident** — the share of questions where the top hit clears the confidence
  threshold (`KB_MIN_SCORE`), i.e. the assistant would answer rather than say
  "I don't know."

## Latest results

Configuration: `top_k=5`, `min_score=0.2`, **71 chunks** across 5 domains.

| Domain | Questions | recall@5 | confident |
|--------|-----------|----------|-----------|
| tarot | 5 | 80% | 100% |
| palmistry | 4 | 100% | 100% |
| astrology | 5 | 100% | 100% |
| numerology | 4 | 100% | 100% |
| reading_craft | 4 | 100% | 100% |
| **Overall** | **22** | **95%** | **100%** |

Chunk counts: tarot 36 · palmistry 9 · astrology 7 · numerology 6 · reading_craft 13.

## How these were produced

```bash
EMBEDDING_BACKEND=hash python src/scripts/ingest_knowledge.py
EMBEDDING_BACKEND=hash python src/scripts/eval_knowledge.py
```

> **Important — this is the floor, not the ceiling.** These numbers use the
> dependency-free `hash` embedding backend (keyword overlap only), so they run
> anywhere with no model or network. The production configuration uses a local
> semantic embedding model (`EMBEDDING_BACKEND=ollama`,
> `ollama pull nomic-embed-text`), which understands meaning rather than shared
> words and scores higher — especially on the one tarot question that currently
> misses top-5 under keyword matching. Re-run the two commands above with
> `EMBEDDING_BACKEND=ollama` on the Mac Mini to measure the real figure.

## Retrieval-quality refinements applied (Milestone 3)

- **Heading-aware chunking** — chunks never cross a Markdown heading, so each
  passage stays topically clean (each tarot card, each sign, each line is its
  own chunk).
- **Title boosting** — each chunk's section heading is weighted in its
  embedding, so a passage stays strongly retrievable by its own name (a query
  for "The Tower" lands on the Tower card, not a passage that merely shares
  common words).
- **Section-level citations** — every hit carries its heading path, so answers
  can be cited as e.g. `major_arcana.md › XVI — The Tower`.
- **Confidence gate** — weak matches below `KB_MIN_SCORE` are treated as "no
  confident match" so Celeste reads on intuition instead of grounding on noise.

## Growing accuracy over time

Accuracy is bounded by the corpus. To raise it in a domain: add more source
material to `knowledge_base/sources/<domain>/`, expand that domain's question
bank in `knowledge_base/eval/<domain>.json`, rebuild the index, and re-run the
eval. See [knowledge_base.md](knowledge_base.md) and
[../setup/knowledge_setup.md](../setup/knowledge_setup.md).
