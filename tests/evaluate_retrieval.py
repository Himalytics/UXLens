"""Small evaluation harness for UXLens retrieval quality."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from rag_engine import UXLensEngine  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--semantic",
        action="store_true",
        help="Load Hugging Face models and evaluate semantic retrieval. Without this flag, use the offline fallback retriever.",
    )
    args = parser.parse_args()

    engine = UXLensEngine(enable_models=args.semantic, top_k=3)
    dataset = Path(__file__).with_name("evaluation_questions.csv")

    top1_correct = 0
    top3_correct = 0
    total = 0

    print("mode:", "semantic" if engine.embedding_model is not None else "fallback")
    if args.semantic and engine.embedding_model is None:
        print("model load warning:", engine.model_error)

    with dataset.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            total += 1
            results = engine.retrieve(row["scenario"], top_k=3)
            titles = [result.chunk.title for result in results]
            expected = row["expected_primary_principle"]
            hit1 = bool(titles and titles[0] == expected)
            hit3 = expected in titles
            top1_correct += int(hit1)
            top3_correct += int(hit3)
            print(
                f"{row['id']:>2}. {'PASS' if hit3 else 'MISS'} | expected: {expected} | top-3: {', '.join(titles)}"
            )

    print("\nSummary")
    print(f"Top-1 expected-principle match: {top1_correct}/{total} ({top1_correct / total:.0%})")
    print(f"Top-3 expected-principle match: {top3_correct}/{total} ({top3_correct / total:.0%})")


if __name__ == "__main__":
    main()
