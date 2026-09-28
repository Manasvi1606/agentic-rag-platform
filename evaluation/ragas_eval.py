"""RAGAS evaluation harness — turns "seems to work" into numbers.

This is the module that makes the project read as engineering research rather
than a demo. The dataset loading + RAGAS call are provided as glue; the piece
you own is generating the predictions to score and interpreting the results.

Metrics you'll produce (know what each means for interviews):
  - faithfulness:      is the answer grounded in the retrieved context? (hallucination)
  - answer_relevancy:  does the answer address the question?
  - context_precision: are the retrieved chunks relevant / well-ranked?
  - context_recall:    did retrieval find everything needed vs. ground truth?
"""
from __future__ import annotations

import json
from pathlib import Path

DATASET = Path(__file__).parent / "dataset" / "qa.jsonl"


def load_dataset() -> list[dict]:
    """Load the gold Q/A set. (Glue.)"""
    if not DATASET.exists():
        raise FileNotFoundError(
            f"No dataset at {DATASET}. Create qa.jsonl — see dataset/README.md."
        )
    return [json.loads(line) for line in DATASET.read_text().splitlines() if line.strip()]


def generate_predictions(dataset: list[dict]) -> list[dict]:
    """Run YOUR pipeline over each question to collect (answer, contexts).

    TODO(you): for each row, call the retrieval/agent pipeline and record the
    generated answer and the retrieved contexts. This is the bridge between your
    system and the scorer — keep it swappable so you can eval baseline vs.
    hybrid vs. hybrid+rerank vs. +self-rag and fill the README table.
    """
    raise NotImplementedError("Run the pipeline to produce predictions for scoring.")


def evaluate() -> dict:
    """Score predictions with RAGAS and return the metric dict. (Glue.)"""
    from datasets import Dataset
    from ragas import evaluate as ragas_evaluate
    from ragas.metrics import (
        answer_relevancy,
        context_precision,
        context_recall,
        faithfulness,
    )

    rows = generate_predictions(load_dataset())
    ds = Dataset.from_list(rows)
    result = ragas_evaluate(
        ds,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
    )
    print(result)
    return dict(result)


if __name__ == "__main__":
    evaluate()
