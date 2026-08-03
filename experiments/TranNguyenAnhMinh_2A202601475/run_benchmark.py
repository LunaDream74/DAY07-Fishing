"""Evaluate Minh's RecursiveChunker configuration on the shared benchmark."""

from __future__ import annotations

import os
from pathlib import Path

from experiments.minh.config import CHUNKER, build_store
from scripts.benchmark import evaluate_store, generate_markdown_report
from src import LocalEmbedder, MockEmbedder

EXPERIMENT_DIR = Path(__file__).parent
REPORT_PATH = EXPERIMENT_DIR / "BENCHMARK_RECURSIVE_20260803.md"


def get_embedder():
    """Select mock or local embeddings from EMBEDDING_PROVIDER (default: mock)."""
    if os.getenv("EMBEDDING_PROVIDER", "mock").lower() == "mock":
        return MockEmbedder()
    try:
        return LocalEmbedder()
    except Exception as error:
        print(f"[WARN] LocalEmbedder unavailable: {error}. Using MockEmbedder.")
        return MockEmbedder()


def main() -> None:
    embedder = get_embedder()
    store = build_store(embedder)
    summary = evaluate_store(store, top_k=3)
    backend = getattr(embedder, "_backend_name", type(embedder).__name__)

    report = f"""---
title: "Benchmark: Minh RecursiveChunker"
date: "2026-08-03"
author: "Tran Nguyen Anh Minh"
strategy: "RecursiveChunker"
chunk_size: {CHUNKER.chunk_size}
separators: ["\\n\\n", "\\n", ". ", " ", ""]
embedding_backend: "{backend}"
total_score: {summary.total_score}
hit_rate_at_1: {summary.hit_rate_at_1}
hit_rate_at_3: {summary.hit_rate_at_3}
filter_accuracy: {summary.filter_accuracy}
---

{generate_markdown_report(summary, store_name=f"RecursiveChunker (size={CHUNKER.chunk_size})")}

## Configuration notes

- Metadata overrides are applied in memory from `metadata_overrides.json`; shared HUST source files remain unchanged.
- The benchmark's required `audience=student` filter is used for query 5.
- Results produced with `MockEmbedder` are structural-only and must not be compared as semantic-retrieval quality. Use the local multilingual backend for the final group comparison.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"Backend: {backend}")
    print(f"Chunks: {store.get_collection_size()}")
    print(f"Score: {summary.total_score:.1f}/10.0")
    print(f"Report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
