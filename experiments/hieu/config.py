"""Hieu's isolated retrieval configuration using FixedSizeChunker."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

from ingest import chunk_document, load_documents
from src import EmbeddingStore, FixedSizeChunker

EXPERIMENT_DIR = Path(__file__).parent
CORPUS_DIR = EXPERIMENT_DIR.parents[1] / "data" / "hust_services"
OVERRIDES_PATH = EXPERIMENT_DIR / "metadata_overrides.json"

# FixedSizeChunker strategy configuration
CHUNKER = FixedSizeChunker(
    chunk_size=400,
    overlap=50,
)


def load_profile() -> dict[str, dict]:
    """Return per-document metadata overrides without modifying shared corpus."""
    if OVERRIDES_PATH.exists():
        return json.loads(OVERRIDES_PATH.read_text(encoding="utf-8"))
    return {}


def build_store(embedding_fn: Callable[[str], list[float]]) -> EmbeddingStore:
    """Create Hieu's vector store using FixedSizeChunker + metadata overrides."""
    profile = load_profile()
    chunk_docs = []
    for document in load_documents(CORPUS_DIR):
        document.metadata.update(profile.get(document.id, {}))
        chunk_docs.extend(chunk_document(document, CHUNKER))

    store = EmbeddingStore(collection_name="hust_fixed_size_hieu", embedding_fn=embedding_fn)
    store.add_documents(chunk_docs)
    return store
