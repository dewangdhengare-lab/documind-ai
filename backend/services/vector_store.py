"""ChromaDB vector storage for document chunks."""

from __future__ import annotations

import logging
import threading
from typing import Any

import chromadb

from config import settings
from services.embedding_service import generate_embeddings, generate_single_embedding

logger = logging.getLogger(__name__)

# Module-level client cache & lock
_client: chromadb.PersistentClient | None = None
_COLLECTION_NAME = "documind_chunks"
_chroma_lock = threading.RLock()


def _get_client() -> chromadb.PersistentClient:
    """Lazy-load the ChromaDB persistent client."""
    global _client
    with _chroma_lock:
        if _client is None:
            logger.info("Initializing ChromaDB at %s", settings.CHROMA_DB_DIR)
            _client = chromadb.PersistentClient(path=str(settings.CHROMA_DB_DIR))
        return _client


def _get_collection() -> chromadb.Collection:
    """Get or create the main chunks collection."""
    with _chroma_lock:
        client = _get_client()
        return client.get_or_create_collection(
            name=_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )


def add_chunks(chunks: list[dict[str, Any]]) -> int:
    """
    Add document chunks to the vector store.

    Each chunk dict should have 'text' and 'metadata' keys.
    The metadata must include 'document_id'.

    Returns the number of chunks added.
    """
    if not chunks:
        return 0

    texts = [c["text"] for c in chunks]
    metadatas = []
    ids = []

    for i, chunk in enumerate(chunks):
        doc_id = chunk["metadata"]["document_id"]
        chunk_id = f"{doc_id}_chunk_{i}"
        ids.append(chunk_id)

        # ChromaDB metadata values must be str, int, float, or bool
        meta: dict[str, Any] = {}
        for k, v in chunk["metadata"].items():
            if v is None:
                continue
            if isinstance(v, (str, int, float, bool)):
                meta[k] = v
            else:
                meta[k] = str(v)
        metadatas.append(meta)

    # Generate embeddings
    embeddings = generate_embeddings(texts)

    with _chroma_lock:
        collection = _get_collection()
        batch_size = 500
        for start in range(0, len(ids), batch_size):
            end = min(start + batch_size, len(ids))
            collection.add(
                ids=ids[start:end],
                embeddings=embeddings[start:end],
                documents=texts[start:end],
                metadatas=metadatas[start:end],
            )

    logger.info("Added %d chunks for document %s", len(ids), chunks[0]["metadata"].get("document_id"))
    return len(ids)


def search_chunks(
    query: str,
    document_ids: list[str] | None = None,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """
    Search for chunks relevant to a query.

    Args:
        query: The search query text.
        document_ids: Optional list of document IDs to filter by.
        top_k: Number of results to return.

    Returns:
        List of result dicts with 'id', 'text', 'metadata', 'distance'.
    """
    query_embedding = generate_single_embedding(query)
    if not query_embedding:
        return []

    where_filter = None
    if document_ids:
        if len(document_ids) == 1:
            where_filter = {"document_id": document_ids[0]}
        else:
            where_filter = {"document_id": {"$in": document_ids}}

    with _chroma_lock:
        collection = _get_collection()
        try:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_filter,
                include=["documents", "metadatas", "distances"],
            )
        except Exception as e:
            logger.error("ChromaDB query failed: %s", e)
            return []

    # Flatten results
    chunks: list[dict[str, Any]] = []
    if results and results["ids"] and results["ids"][0]:
        for i, chunk_id in enumerate(results["ids"][0]):
            chunks.append({
                "id": chunk_id,
                "text": results["documents"][0][i] if results["documents"] else "",
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                "distance": results["distances"][0][i] if results["distances"] else 0.0,
            })

    return chunks


def get_chunks_by_document(document_id: str, limit: int = 1000) -> list[dict[str, Any]]:
    """Get all chunks belonging to a document."""
    with _chroma_lock:
        collection = _get_collection()
        try:
            results = collection.get(
                where={"document_id": document_id},
                include=["documents", "metadatas"],
                limit=limit,
            )
        except Exception as e:
            logger.error("Failed to get chunks for document %s: %s", document_id, e)
            return []

    chunks: list[dict[str, Any]] = []
    if results and results["ids"]:
        for i, chunk_id in enumerate(results["ids"]):
            chunks.append({
                "id": chunk_id,
                "text": results["documents"][i] if results["documents"] else "",
                "metadata": results["metadatas"][i] if results["metadatas"] else {},
            })

    return chunks


def delete_document_chunks(document_id: str) -> int:
    """Delete all chunks belonging to a document. Returns count deleted."""
    with _chroma_lock:
        collection = _get_collection()
        try:
            results = collection.get(
                where={"document_id": document_id},
                include=[],
            )
            if results and results["ids"]:
                collection.delete(ids=results["ids"])
                count = len(results["ids"])
                logger.info("Deleted %d chunks for document %s", count, document_id)
                return count
        except Exception as e:
            logger.error("Failed to delete chunks for document %s: %s", document_id, e)

    return 0
