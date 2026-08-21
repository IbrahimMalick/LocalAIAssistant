# Knowledge Base — "Deep Memory" (Phase 2)

This folder holds the assistant's **local, private, searchable knowledge base**.
Everything here stays on the machine — source material is embedded locally and
searched locally.

## Layout

```
knowledge_base/
├── sources/                 # raw source material, one folder per domain
│   ├── tarot/
│   ├── palmistry/
│   ├── astrology/
│   ├── numerology/
│   └── reading_craft/
├── eval/                    # per-domain accuracy question banks (JSON)
└── index/                   # generated vector index (git-ignored, rebuildable)
```

These are the crafts **Celeste Noir** draws on. Content is written in original
wording from traditional, public-domain reading systems (see
[../docs/celeste_persona.md](../docs/celeste_persona.md)).

## What's committed vs. ignored

- **Committed:** this README, each domain's `README`, the `eval/*.json` question
  banks, and the original reference content files (`*.md`) that make up Celeste's
  base knowledge.
- **Git-ignored:** any additional provided material dropped under `sources/`
  that is potentially large or copyrighted, and the entire `index/` (regenerated
  by ingestion). The committed `*.md` files are original wording and are kept.

## Adding material

1. Drop files into the matching `sources/<domain>/` folder. Supported formats:
   `.txt`, `.md`, `.vtt`/`.srt` transcripts, `.pdf` (needs `pypdf`), `.epub`.
2. (Real embeddings) pull the local embedding model once:
   `ollama pull nomic-embed-text`
3. Build the index: `python src/scripts/ingest_knowledge.py`
4. Test retrieval: `python src/scripts/kb_search.py "your question"`
5. Measure accuracy: `python src/scripts/eval_knowledge.py`

Full guide: [../setup/knowledge_setup.md](../setup/knowledge_setup.md).
Scope, responsibilities, and milestones: [../docs/phase2_scope.md](../docs/phase2_scope.md).
