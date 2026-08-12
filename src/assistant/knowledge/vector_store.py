"""
Local vector store.

A dependency-light, file-backed store of ``(id, text, metadata, vector)``
records with cosine-similarity search. It persists to a single JSON file under
the (git-ignored) ``knowledge_base/index/`` directory, so the whole knowledge
base is self-contained, inspectable, and never leaves the machine.

This is deliberately simple and correct for the Milestone-1 framework and for
the corpus sizes in this project. The interface (``add`` / ``search`` /
``save`` / ``load``) is intentionally small so it can be swapped for Chroma,
FAISS, LanceDB, or Qdrant later without touching the rest of the pipeline.

If ``numpy`` is installed it is used to speed up search; otherwise a pure
standard-library path is used.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

try:  # optional acceleration
    import numpy as _np  # type: ignore
except ImportError:  # pragma: no cover - optional
    _np = None


@dataclass
class Record:
    id: str
    text: str
    vector: List[float]
    metadata: Dict = field(default_factory=dict)


@dataclass
class SearchHit:
    id: str
    text: str
    score: float
    metadata: Dict


class LocalVectorStore:
    """An on-disk cosine-similarity vector store."""

    DEFAULT_FILENAME = "vector_store.json"

    def __init__(self, embedder_name: str = "", dim: int = 0) -> None:
        self.embedder_name = embedder_name
        self.dim = dim
        self._records: List[Record] = []
        self._matrix = None  # cached numpy matrix of normalised vectors

    # -- mutation ----------------------------------------------------------
    def add(
        self, id: str, text: str, vector: List[float], metadata: Optional[Dict] = None
    ) -> None:
        self._records.append(Record(id=id, text=text, vector=list(vector),
                                     metadata=metadata or {}))
        self._matrix = None  # invalidate cache
        if not self.dim:
            self.dim = len(vector)

    def __len__(self) -> int:
        return len(self._records)

    def domains(self) -> Dict[str, int]:
        """Return a {domain: chunk_count} summary."""
        counts: Dict[str, int] = {}
        for rec in self._records:
            d = rec.metadata.get("domain", "unknown")
            counts[d] = counts.get(d, 0) + 1
        return counts

    # -- search ------------------------------------------------------------
    def search(
        self, query_vector: List[float], top_k: int = 5, domain: Optional[str] = None
    ) -> List[SearchHit]:
        """Return the ``top_k`` most similar records (optionally within a domain)."""
        if not self._records:
            return []

        candidates = range(len(self._records))
        if domain:
            candidates = [
                i for i in candidates
                if self._records[i].metadata.get("domain") == domain
            ]
            if not candidates:
                return []

        scores = self._cosine_scores(query_vector, list(candidates))
        ranked = sorted(scores, key=lambda t: t[1], reverse=True)[:top_k]
        return [
            SearchHit(
                id=self._records[i].id,
                text=self._records[i].text,
                score=float(s),
                metadata=self._records[i].metadata,
            )
            for i, s in ranked
        ]

    def _cosine_scores(self, query_vector, indices):
        q = _normalise(query_vector)
        if _np is not None:
            mat = _np.array([self._records[i].vector for i in indices], dtype=float)
            norms = _np.linalg.norm(mat, axis=1)
            norms[norms == 0] = 1.0
            mat = mat / norms[:, None]
            qv = _np.array(q, dtype=float)
            sims = mat @ qv
            return list(zip(indices, sims.tolist()))
        # Pure-python fallback.
        out = []
        for i in indices:
            out.append((i, _dot(q, _normalise(self._records[i].vector))))
        return out

    # -- persistence -------------------------------------------------------
    def save(self, index_dir: Path, filename: str = DEFAULT_FILENAME) -> Path:
        index_dir.mkdir(parents=True, exist_ok=True)
        path = index_dir / filename
        payload = {
            "embedder_name": self.embedder_name,
            "dim": self.dim,
            "count": len(self._records),
            "records": [asdict(r) for r in self._records],
        }
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    @classmethod
    def load(cls, index_dir: Path, filename: str = DEFAULT_FILENAME) -> "LocalVectorStore":
        path = index_dir / filename
        if not path.exists():
            raise FileNotFoundError(
                f"No vector index at {path}. Build it first with "
                "`python src/scripts/ingest_knowledge.py`."
            )
        payload = json.loads(path.read_text(encoding="utf-8"))
        store = cls(embedder_name=payload.get("embedder_name", ""),
                    dim=payload.get("dim", 0))
        store._records = [
            Record(id=r["id"], text=r["text"], vector=r["vector"],
                   metadata=r.get("metadata", {}))
            for r in payload.get("records", [])
        ]
        return store


# ---------------------------------------------------------------------------
# small vector helpers (pure-python path)
# ---------------------------------------------------------------------------
def _normalise(vec: List[float]) -> List[float]:
    norm = math.sqrt(sum(v * v for v in vec))
    if norm == 0:
        return list(vec)
    return [v / norm for v in vec]


def _dot(a: List[float], b: List[float]) -> float:
    return sum(x * y for x, y in zip(a, b))
