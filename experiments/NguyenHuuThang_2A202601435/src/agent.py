from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self.store.search(question, top_k=top_k)

        context_blocks: list[str] = []
        for index, result in enumerate(results, start=1):
            metadata = result.get("metadata") or {}
            source = (
                metadata.get("source_url")
                or metadata.get("source")
                or result.get("id")
                or "unknown"
            )
            context_blocks.append(
                f"[Chunk {index} | Source: {source}]\n{result.get('content', '')}"
            )

        context = (
            "\n\n".join(context_blocks)
            if context_blocks
            else "No relevant context was found in the knowledge base."
        )
        prompt = (
            "You are a knowledge-base assistant. Answer the question using only "
            "the supplied context. If the context does not contain enough "
            "information, say that you do not have enough information; do not "
            "invent facts.\n\n"
            f"Context:\n{context}\n\n"
            f"Question:\n{question}\n\n"
            "Answer:"
        )
        return self.llm_fn(prompt)
