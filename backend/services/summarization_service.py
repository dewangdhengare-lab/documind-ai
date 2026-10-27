"""Document summarization service."""

from __future__ import annotations

import logging
import uuid
from typing import Any

from sqlalchemy.orm import Session

from models import Document, Summary
from services.vector_store import get_chunks_by_document
from services.llm_service import call_llm

logger = logging.getLogger(__name__)

SUMMARY_PROMPTS = {
    "concise": "Provide a clear, high-level concise summary (2-3 paragraphs) of the following document. Highlight the main topic, core findings/content, and key conclusion.",
    "short": "Provide a brief and clear summary (1-2 paragraphs) covering the most essential points.",
    "detailed": "Provide an in-depth, comprehensive summary of the document. Cover all major sections, arguments, findings, methodology, and conclusions thoroughly.",
    "executive": "Provide an Executive Summary formatted with: \n1. Purpose / Context\n2. Key Takeaways & Strategic Insights\n3. Critical Metrics & Findings\n4. Recommendations & Next Steps.",
    "bullet_points": "Summarize the key takeaways of the document as a structured list of bullet points organized by topic or theme.",
    "key_points": "Provide a bulleted list of the most critical key points and takeaways from the document.",
    "section_wise": "Break down the document section by section. For each section, provide a concise summary of its contents and implications.",
    "facts_and_figures": "Extract and summarize all important facts, quantitative data, percentages, dates, names, financial figures, and measurable metrics found in the document.",
}


def _get_document_full_text(document_id: str) -> str:
    """Retrieve full text from stored chunks of the document."""
    chunks = get_chunks_by_document(document_id)
    if not chunks:
        return ""
    return "\n\n".join(c["text"] for c in chunks)


def generate_summary(
    document_id: str,
    summary_type: str,
    db: Session,
) -> Summary:
    """Generate a summary for a document and persist it."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise ValueError(f"Document {document_id} not found")
    if doc.status != "ready":
        raise ValueError(f"Document '{doc.original_filename}' is not ready (status: {doc.status})")

    full_text = _get_document_full_text(document_id)
    if not full_text.strip():
        raise ValueError(f"No text content found for document '{doc.original_filename}'")

    # Limit to safe token budget for LLM
    max_chars = 8000
    if len(full_text) > max_chars:
        truncated_text = (
            full_text[:5000]
            + "\n\n[... middle content omitted to stay within token limits ...]\n\n"
            + full_text[-3000:]
        )
    else:
        truncated_text = full_text

    instruction = SUMMARY_PROMPTS.get(summary_type, SUMMARY_PROMPTS["concise"])

    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert document analyst and executive summarizer. "
                "Base your summary strictly on the actual provided document text. "
                "Do not hallucinate or extrapolate facts not present in the text. "
                "Preserve key figures, names, dates, and conclusions faithfully."
            ),
        },
        {
            "role": "user",
            "content": f"{instruction}\n\nDocument Name: {doc.original_filename}\n\nDocument Content:\n{truncated_text}",
        },
    ]

    content = call_llm(messages, temperature=0.3)

    summary = Summary(
        id=str(uuid.uuid4()),
        document_id=document_id,
        summary_type=summary_type,
        content=content,
    )
    db.add(summary)
    db.commit()
    db.refresh(summary)

    return summary


def get_summary(summary_id: str, db: Session) -> Summary | None:
    """Get a summary by ID."""
    return db.query(Summary).filter(Summary.id == summary_id).first()


def list_summaries(document_id: str | None, db: Session) -> list[Summary]:
    """List summaries, optionally filtered by document_id."""
    query = db.query(Summary)
    if document_id:
        query = query.filter(Summary.document_id == document_id)
    return query.order_by(Summary.created_at.desc()).all()


def delete_summary(summary_id: str, db: Session) -> bool:
    """Delete a summary by ID."""
    summary = db.query(Summary).filter(Summary.id == summary_id).first()
    if not summary:
        return False
    db.delete(summary)
    db.commit()
    return True
