"""Minh's isolated retrieval configuration for the shared HUST corpus."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

from ingest import chunk_document, load_documents
from src import EmbeddingStore, RecursiveChunker

EXPERIMENT_DIR = Path(__file__).parent
CORPUS_DIR = EXPERIMENT_DIR.parents[1] / "data" / "hust_services"
OVERRIDES_PATH = EXPERIMENT_DIR / "metadata_overrides.json"

# Use this one strategy only for this experiment.
CHUNKER = RecursiveChunker(
    separators=["\n\n", "\n", ". ", " ", ""],
    chunk_size=450,
)


def load_profile() -> dict[str, dict]:
    """Return per-document metadata without changing the shared corpus files."""
    return json.loads(OVERRIDES_PATH.read_text(encoding="utf-8"))


def build_store(embedding_fn: Callable[[str], list[float]]) -> EmbeddingStore:
    """Create Minh's vector store from shared documents plus private metadata."""
    profile = load_profile()
    chunk_docs = []
    for document in load_documents(CORPUS_DIR):
        document.metadata.update(profile.get(document.id, {}))
        chunk_docs.extend(chunk_document(document, CHUNKER))

    store = EmbeddingStore(collection_name="hust_recursive_minh", embedding_fn=embedding_fn)
    store.add_documents(chunk_docs)
    return store
