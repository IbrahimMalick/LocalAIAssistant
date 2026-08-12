# Knowledge Base Setup ("Deep Memory")

How to load source material into the assistant's local knowledge base, build the
index, and test it. Everything runs locally.

## 1. (Recommended) Pull the local embedding model

Real semantic search uses a local embedding model served by Ollama:

```bash
ollama pull nomic-embed-text
```

Set in `.env`:
```bash
EMBEDDING_BACKEND=ollama
EMBEDDING_MODEL=nomic-embed-text
```

> **No model yet? / testing headless?** Set `EMBEDDING_BACKEND=hash` to run the
> full pipeline with zero dependencies and no network. It does keyword-overlap
> matching only — fine for verifying the plumbing, not for judging accuracy.

## 2. Add source material

Drop files into the matching domain folder under `knowledge_base/sources/`:

```
knowledge_base/sources/
├── movies_pop_culture/
├── mythology_religion/
├── philosophy/
├── psychology_influence/
└── law_penal_codes/
```

Supported formats:

| Format | Extension | Notes |
|--------|-----------|-------|
| Plain text / Markdown | `.txt` `.md` | Works with no extra dependencies |
| Transcripts | `.vtt` `.srt` | Timestamps and cue numbers stripped automatically |
| PDF | `.pdf` | Requires `pip install pypdf` |
| EPUB | `.epub` | Uses `ebooklib`+`beautifulsoup4` if installed; otherwise a stdlib fallback |

Provided source files are **git-ignored** (except the small committed
`sample_*.md` demo files) so private/copyrighted material is never committed.

**Video content:** export a transcript (`.vtt`/`.srt`) or plain text and drop
that in — video files themselves are not ingested directly.

## 3. Build the index

```bash
python src/scripts/ingest_knowledge.py
```

Re-run this any time you add or change source files. The index is written to
`knowledge_base/index/` (git-ignored, rebuildable).

## 4. Test retrieval

```bash
python src/scripts/kb_search.py "Who directed Weird Science?"
python src/scripts/kb_search.py --domain philosophy "What is the categorical imperative?"
```

Each hit shows a similarity score, domain, and source so you can see exactly
what the assistant would ground an answer on.

## 5. Measure accuracy

Question banks live in `knowledge_base/eval/<domain>.json`. Add ~20–30
"must nail these" questions per domain (the client provides these — see
[../docs/phase2_scope.md](../docs/phase2_scope.md)), then:

```bash
python src/scripts/eval_knowledge.py
python src/scripts/eval_knowledge.py --domain law_penal_codes
```

This reports **recall@k** and the **confident-answer rate** per domain.

### Question-bank format

```json
{
  "domain": "philosophy",
  "questions": [
    {
      "question": "What is Kant's categorical imperative?",
      "expected_keywords": ["categorical imperative", "universal law"],
      "expected_source": "kant_groundwork.txt"
    }
  ]
}
```

`expected_source` is optional; `expected_keywords` should list distinctive terms
that a correct passage would contain.

## Tuning

Adjust in `.env` (no code changes needed):

| Variable | Meaning | Default |
|----------|---------|---------|
| `KB_CHUNK_SIZE_WORDS` | Target chunk size (words) | `220` |
| `KB_CHUNK_OVERLAP_WORDS` | Overlap between chunks | `40` |
| `KB_TOP_K` | Passages retrieved per query | `5` |
| `KB_MIN_SCORE` | Confidence threshold for a trusted hit | `0.2` |

After changing chunking or the embedding model, **rebuild the index** (step 3).
