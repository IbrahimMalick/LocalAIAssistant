#!/usr/bin/env python3
"""
Evaluate retrieval quality against per-domain question banks.

This is the Milestone-1 *evaluation methodology*, made runnable. It measures
how well the knowledge base can surface the passage that answers each question,
using two standard retrieval metrics:

* recall@k  - fraction of questions whose expected source/keywords appear in
              the top-k retrieved chunks (did we fetch the right passage?).
* hit-rate  - fraction of questions where at least one retrieved chunk clears
              the confidence threshold (would the assistant attempt an answer?).

Each domain has a question bank at ``knowledge_base/eval/<domain>.json``:

    {
      "domain": "philosophy",
      "questions": [
        {
          "question": "What is Kant's categorical imperative?",
          "expected_keywords": ["categorical imperative", "universal law"],
          "expected_source": "kant_groundwork.txt"   // optional
        }
      ]
    }

A question counts as a retrieval hit when a top-k chunk either comes from
``expected_source`` or contains any ``expected_keywords`` (case-insensitive).
Answer-level grading (LLM-graded correctness) is layered on in Milestone 3;
this harness establishes the methodology and the metrics now.

Usage
-----
    EMBEDDING_BACKEND=hash python src/scripts/eval_knowledge.py
    python src/scripts/eval_knowledge.py --domain philosophy
"""

import json
import sys

import _bootstrap  # noqa: F401  (adds src/ to sys.path)

from assistant.config import load_config
from assistant.knowledge.embeddings import EmbeddingError, build_embedder
from assistant.knowledge.retriever import Retriever


def _load_bank(eval_dir, domain):
    path = eval_dir / f"{domain}.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"  ! {domain}: invalid JSON ({exc})", file=sys.stderr)
        return None
    return data.get("questions", [])


def _question_hit(result, expected_source, expected_keywords):
    keywords = [k.lower() for k in (expected_keywords or [])]
    for hit in result.hits:
        if expected_source and hit.metadata.get("source", "").endswith(expected_source):
            return True
        text = hit.text.lower()
        if keywords and any(k in text for k in keywords):
            return True
    return False


def main() -> int:
    argv = sys.argv[1:]
    only_domain = None
    if "--domain" in argv:
        i = argv.index("--domain")
        only_domain = argv[i + 1] if i + 1 < len(argv) else None

    config = load_config()
    kb = config.knowledge

    try:
        embedder = build_embedder(kb, config.llm.endpoint)
        retriever = Retriever(kb, embedder)
    except (EmbeddingError, FileNotFoundError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    domains = [only_domain] if only_domain else kb.domains
    grand_total = grand_recall = grand_conf = 0

    print(f"Evaluating with backend={kb.embedding_backend}, top_k={kb.top_k}, "
          f"min_score={kb.min_score}\n")

    for domain in domains:
        questions = _load_bank(kb.eval_dir, domain)
        if not questions:
            print(f"[{domain}] no question bank yet "
                  f"(add {kb.eval_dir}/{domain}.json)")
            continue

        total = len(questions)
        recall = conf = 0
        for q in questions:
            result = retriever.retrieve(q["question"], domain=domain)
            if _question_hit(result, q.get("expected_source"),
                             q.get("expected_keywords")):
                recall += 1
            if result.confident:
                conf += 1

        grand_total += total
        grand_recall += recall
        grand_conf += conf
        r_pct = 100 * recall / total if total else 0
        c_pct = 100 * conf / total if total else 0
        print(f"[{domain}] questions={total}  "
              f"recall@{kb.top_k}={r_pct:.0f}%  confident={c_pct:.0f}%")

    if grand_total:
        print(f"\nOVERALL  questions={grand_total}  "
              f"recall@{kb.top_k}={100*grand_recall/grand_total:.0f}%  "
              f"confident={100*grand_conf/grand_total:.0f}%")
        print(
            "\nNote: with EMBEDDING_BACKEND=hash these numbers reflect keyword "
            "overlap only. Real semantic accuracy is measured with the Ollama "
            "embedder on the full provided corpus (Milestones 2-3)."
        )
    else:
        print("\nNo question banks found. Add banks under "
              f"{kb.eval_dir}/<domain>.json (templates are provided).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
