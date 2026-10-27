"""Semantic search / retrieval service."""

from __future__ import annotations

from typing import Any

from services.vector_store import search_chunks


def retrieve_relevant_chunks(
    query: str,
    document_ids: list[str],
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """
    Retrieve the most relevant chunks for a user query across specified documents.

    Returns a list of chunk dicts sorted by relevance (lowest distance first).
    """
    results = search_chunks(
        query=query,
        document_ids=document_ids,
        top_k=top_k,
    )

    # Sort by distance (lower = more similar for cosine)
    results.sort(key=lambda r: r.get("distance", 1.0))
    return results


def format_context_for_llm(chunks: list[dict[str, Any]]) -> str:
    """
    Format retrieved chunks into a context string for the LLM prompt.

    Each chunk is labeled with its source information for citation purposes.
    """
    if not chunks:
        return "No relevant context found."

    context_parts: list[str] = []
    for i, chunk in enumerate(chunks, start=1):
        meta = chunk.get("metadata", {})
        source_parts: list[str] = []
        if meta.get("filename"):
            source_parts.append(f"File: {meta['filename']}")
        if meta.get("page_number"):
            source_parts.append(f"Page: {meta['page_number']}")
        if meta.get("heading"):
            source_parts.append(f"Section: {meta['heading']}")

        source_label = " | ".join(source_parts) if source_parts else f"Chunk {i}"
        context_parts.append(f"[Source {i}: {source_label}]\n{chunk['text']}")

    return "\n\n---\n\n".join(context_parts)
