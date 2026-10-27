"""Text chunking service with overlap and metadata preservation."""

from __future__ import annotations

from typing import Any


def _estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 characters per token for English text."""
    return len(text) // 4


def chunk_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    metadata: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """
    Split text into chunks of approximately chunk_size tokens with overlap.

    Args:
        text: The text to chunk.
        chunk_size: Target number of tokens per chunk.
        chunk_overlap: Number of overlapping tokens between consecutive chunks.
        metadata: Metadata dict to attach to each chunk (e.g. filename, page).

    Returns:
        List of chunk dicts with 'text' and 'metadata' keys.
    """
    if not text or not text.strip():
        return []

    metadata = metadata or {}

    # Convert token targets to character targets
    char_chunk_size = chunk_size * 4
    char_overlap = chunk_overlap * 4

    # Split by sentences to avoid cutting mid-sentence
    sentences = _split_sentences(text)

    chunks: list[dict[str, Any]] = []
    current_chunk: list[str] = []
    current_length = 0
    chunk_index = 0

    for sentence in sentences:
        sentence_len = len(sentence)

        if current_length + sentence_len > char_chunk_size and current_chunk:
            # Emit the current chunk
            chunk_text_str = " ".join(current_chunk)
            chunks.append({
                "text": chunk_text_str,
                "metadata": {
                    **metadata,
                    "chunk_index": chunk_index,
                },
            })
            chunk_index += 1

            # Create overlap by keeping trailing sentences
            overlap_text: list[str] = []
            overlap_length = 0
            for s in reversed(current_chunk):
                if overlap_length + len(s) > char_overlap:
                    break
                overlap_text.insert(0, s)
                overlap_length += len(s)

            current_chunk = overlap_text
            current_length = overlap_length

        current_chunk.append(sentence)
        current_length += sentence_len

    # Emit remaining text
    if current_chunk:
        chunk_text_str = " ".join(current_chunk)
        chunks.append({
            "text": chunk_text_str,
            "metadata": {
                **metadata,
                "chunk_index": chunk_index,
            },
        })

    return chunks


def _split_sentences(text: str) -> list[str]:
    """
    Split text into sentences using a simple heuristic.
    Splits on '.', '!', '?' followed by a space or newline.
    """
    import re

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Split on sentence-ending punctuation followed by space
    raw_sentences = re.split(r"(?<=[.!?])\s+", text)
    sentences = [s.strip() for s in raw_sentences if s.strip()]
    return sentences


def chunk_document_sections(
    sections: list[dict],
    document_id: str,
    filename: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> list[dict[str, Any]]:
    """
    Chunk all sections of a document, preserving per-section metadata.

    Each section dict should have 'text' and optionally 'page_number',
    'heading', 'section_index'.
    """
    all_chunks: list[dict[str, Any]] = []

    for section in sections:
        meta: dict[str, Any] = {
            "document_id": document_id,
            "filename": filename,
        }
        if "page_number" in section:
            meta["page_number"] = section["page_number"]
        if "heading" in section and section["heading"]:
            meta["heading"] = section["heading"]
        if "section_index" in section:
            meta["section_index"] = section["section_index"]

        section_chunks = chunk_text(
            text=section["text"],
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            metadata=meta,
        )
        all_chunks.extend(section_chunks)

    # Re-index globally
    for i, chunk in enumerate(all_chunks):
        chunk["metadata"]["chunk_index"] = i

    return all_chunks
