from __future__ import annotations

from typing import Any, Callable

from .chunking import _dot
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    A vector store for text chunks.

    Tries to use ChromaDB if available; falls back to an in-memory store.
    The embedding_fn parameter allows injection of mock embeddings for tests.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._client = None
        self._collection = None
        self._next_index = 0

        try:
            import chromadb

            self._client = chromadb.Client()
            self._collection = self._client.get_or_create_collection(
                name=self._collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._client = None
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        metadata = dict(doc.metadata or {})
        metadata.setdefault("doc_id", doc.id)

        # Chroma requires unique IDs.  The suffix also lets the in-memory
        # backend accept the same Document.id more than once.
        record_id = f"{doc.id}::{self._next_index}"
        self._next_index += 1
        return {
            "id": record_id,
            "content": doc.content,
            "metadata": metadata,
            "embedding": list(self._embedding_fn(doc.content)),
        }

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        if top_k <= 0 or not records:
            return []

        query_embedding = self._embedding_fn(query)
        ranked = sorted(
            records,
            key=lambda record: _dot(query_embedding, record["embedding"]),
            reverse=True,
        )
        return [
            {
                "id": record["id"],
                "content": record["content"],
                "metadata": dict(record["metadata"]),
                "score": _dot(query_embedding, record["embedding"]),
            }
            for record in ranked[:top_k]
        ]

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        For ChromaDB: use collection.add(ids=[...], documents=[...], embeddings=[...])
        For in-memory: append dicts to self._store
        """
        if not docs:
            return

        records = [self._make_record(doc) for doc in docs]
        if self._use_chroma and self._collection is not None:
            try:
                self._collection.add(
                    ids=[record["id"] for record in records],
                    documents=[record["content"] for record in records],
                    metadatas=[record["metadata"] for record in records],
                    embeddings=[record["embedding"] for record in records],
                )
            except Exception:
                # Keep the store usable when an optional Chroma installation is
                # incompatible or rejects a metadata value.
                self._use_chroma = False
                self._collection = None

        # A small mirror makes the optional-backend fallback lossless and is
        # also the canonical store when ChromaDB is unavailable.
        self._store.extend(records)

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute dot product of query embedding vs all stored embeddings.
        """
        if top_k <= 0 or self.get_collection_size() == 0:
            return []

        if self._use_chroma and self._collection is not None:
            try:
                result = self._collection.query(
                    query_embeddings=[list(self._embedding_fn(query))],
                    n_results=min(top_k, self.get_collection_size()),
                    include=["documents", "metadatas", "distances"],
                )
                ids = (result.get("ids") or [[]])[0]
                documents = (result.get("documents") or [[]])[0]
                metadatas = (result.get("metadatas") or [[]])[0]
                distances = (result.get("distances") or [[]])[0]
                return [
                    {
                        "id": record_id,
                        "content": content,
                        "metadata": metadata or {},
                        "score": 1.0 - float(distance),
                    }
                    for record_id, content, metadata, distance in zip(
                        ids, documents, metadatas, distances
                    )
                ]
            except Exception:
                # The in-memory mirror contains everything added by this
                # instance, so a backend query failure can degrade gracefully.
                self._use_chroma = False
                self._collection = None

        return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        if self._use_chroma and self._collection is not None:
            try:
                return int(self._collection.count())
            except Exception:
                self._use_chroma = False
                self._collection = None
        return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.
        """
        if not metadata_filter:
            return self.search(query, top_k=top_k)
        if top_k <= 0:
            return []

        matching_records = [
            record
            for record in self._store
            if all(
                record["metadata"].get(key) == value
                for key, value in metadata_filter.items()
            )
        ]
        return self._search_records(query, matching_records, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        matching_ids = [
            record["id"]
            for record in self._store
            if record["metadata"].get("doc_id") == doc_id
        ]
        if not matching_ids:
            return False

        if self._use_chroma and self._collection is not None:
            try:
                self._collection.delete(ids=matching_ids)
            except Exception:
                self._use_chroma = False
                self._collection = None

        matching_id_set = set(matching_ids)
        self._store = [
            record for record in self._store if record["id"] not in matching_id_set
        ]
        return True
