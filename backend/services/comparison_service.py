"""Multi-document comparison service."""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any

from sqlalchemy.orm import Session

from models import Document, Comparison
from services.vector_store import get_chunks_by_document
from services.llm_service import call_llm

logger = logging.getLogger(__name__)


def _get_document_full_text(document_id: str) -> str:
    """Retrieve full text from stored chunks of the document."""
    chunks = get_chunks_by_document(document_id)
    if not chunks:
        return ""
    return "\n\n".join(c["text"] for c in chunks)


def compare_documents(
    document_ids: list[str],
    db: Session,
) -> Comparison:
    """
    Compare multiple documents and generate a structured comparison report.
    Returns a Comparison record with JSON result.
    """
    if len(document_ids) < 2:
        raise ValueError("At least 2 documents are required for comparison.")

    docs = []
    for doc_id in document_ids:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            raise ValueError(f"Document {doc_id} not found")
        if doc.status != "ready":
            raise ValueError(f"Document '{doc.original_filename}' is not ready (status: {doc.status})")
        docs.append(doc)

    # Budget total text so combined documents fit safely within LLM rate limits
    chars_per_doc = max(1500, 7000 // len(docs))
    doc_texts = {}
    for doc in docs:
        text = _get_document_full_text(doc.id)
        if len(text) > chars_per_doc:
            head_len = chars_per_doc * 2 // 3
            tail_len = chars_per_doc - head_len
            doc_texts[doc.original_filename] = (
                text[:head_len] + "\n...[middle omitted for length]...\n" + text[-tail_len:]
            )
        else:
            doc_texts[doc.original_filename] = text

    combined_input = ""
    for filename, text in doc_texts.items():
        combined_input += f"\n\n================ DOCUMENT: {filename} ================\n{text}\n"

    system_prompt = (
        "You are an expert document comparative analyst. "
        "Your task is to analyze and compare the provided documents thoroughly and objectively.\n"
        "Analyze:\n"
        "1. Common topics, themes, and shared objectives\n"
        "2. Key facts, dates, timelines, and numerical values\n"
        "3. Major similarities\n"
        "4. Key differences (divergences in scope, metrics, timeline, or focus)\n"
        "5. Contradictions or inconsistencies (differentiate true conflicts from differences in context/timing)\n"
        "6. Information unique to each document\n"
        "7. Synthesis and conclusion\n\n"
        "Output MUST be valid JSON with the exact structure:\n"
        "{\n"
        '  "summary": "High-level overview of the comparison",\n'
        '  "similarities": ["similarity 1", "similarity 2", ...],\n'
        '  "differences": ["difference 1", "difference 2", ...],\n'
        '  "contradictions": ["potential contradiction 1", ...],\n'
        '  "unique_points": {\n'
        '    "DocA_Filename": ["unique point 1", ...],\n'
        '    "DocB_Filename": ["unique point 1", ...]\n'
        "  },\n"
        '  "comparison_table": [\n'
        '    {"aspect": "Aspect name", "values": {"DocA_Filename": "value in DocA", "DocB_Filename": "value in DocB"}}\n'
        "  ],\n"
        '  "conclusion": "Comprehensive synthesis and conclusion."\n'
        "}\n"
        "Do NOT wrap in markdown formatting. Return raw JSON."
    )

    user_prompt = f"Please compare the following documents in detail:\n{combined_input}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    response_text = call_llm(messages, temperature=0.2)

    cleaned_json = response_text.strip()
    if cleaned_json.startswith("```json"):
        cleaned_json = cleaned_json[7:]
    if cleaned_json.startswith("```"):
        cleaned_json = cleaned_json[3:]
    if cleaned_json.endswith("```"):
        cleaned_json = cleaned_json[:-3]
    cleaned_json = cleaned_json.strip()

    try:
        parsed_result = json.loads(cleaned_json)
    except Exception as e:
        logger.warning("Failed to parse JSON comparison result: %s", e)
        parsed_result = {
            "summary": "Document Comparison Summary",
            "similarities": ["See detailed analysis below."],
            "differences": ["See detailed analysis below."],
            "contradictions": [],
            "unique_points": {},
            "comparison_table": [],
            "conclusion": response_text,
        }

    comp = Comparison(
        id=str(uuid.uuid4()),
        document_ids=json.dumps(document_ids),
        result=json.dumps(parsed_result),
    )
    db.add(comp)
    db.commit()
    db.refresh(comp)

    return comp


def get_comparison(comparison_id: str, db: Session) -> Comparison | None:
    """Get comparison by ID."""
    return db.query(Comparison).filter(Comparison.id == comparison_id).first()


def list_comparisons(db: Session) -> list[Comparison]:
    """List all comparisons."""
    return db.query(Comparison).order_by(Comparison.created_at.desc()).all()


def delete_comparison(comparison_id: str, db: Session) -> bool:
    """Delete a comparison by ID."""
    comp = db.query(Comparison).filter(Comparison.id == comparison_id).first()
    if not comp:
        return False
    db.delete(comp)
    db.commit()
    return True
