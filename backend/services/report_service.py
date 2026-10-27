"""Report generation and management service."""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any

from sqlalchemy.orm import Session

from models import Document, Report
from services.vector_store import get_chunks_by_document
from services.llm_service import call_llm

logger = logging.getLogger(__name__)


def _get_document_full_text(document_id: str) -> str:
    """Retrieve full text from stored chunks of the document."""
    chunks = get_chunks_by_document(document_id)
    if not chunks:
        return ""
    return "\n\n".join(c["text"] for c in chunks)


def generate_report(
    document_ids: list[str],
    report_type: str,
    title: str | None,
    purpose: str | None,
    audience: str | None,
    sections: list[str] | None,
    detail_level: str,
    db: Session,
) -> Report:
    """Generate a comprehensive structured report from one or multiple documents."""
    if not document_ids:
        raise ValueError("At least one document is required to generate a report.")

    docs = []
    for doc_id in document_ids:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            raise ValueError(f"Document {doc_id} not found")
        if doc.status != "ready":
            raise ValueError(f"Document '{doc.original_filename}' is not ready (status: {doc.status})")
        docs.append(doc)

    chars_per_doc = max(1500, 7000 // len(docs))
    combined_texts = []
    for doc in docs:
        text = _get_document_full_text(doc.id)
        if len(text) > chars_per_doc:
            doc_text = (
                text[: chars_per_doc * 2 // 3]
                + "\n...[middle omitted for length]...\n"
                + text[-(chars_per_doc // 3) :]
            )
        else:
            doc_text = text
        combined_texts.append(f"--- Document: {doc.original_filename} ---\n{doc_text}")

    full_context = "\n\n".join(combined_texts)

    default_title = title or f"{report_type.capitalize()} Report: {', '.join(d.original_filename for d in docs)}"
    chosen_sections = sections or [
        "Executive Summary",
        "Introduction & Objectives",
        "Key Findings & Facts",
        "Detailed Analysis",
        "Risk Assessment & Strategic Implications",
        "Recommendations & Next Steps",
        "Conclusion",
    ]

    system_prompt = (
        "You are an elite corporate and technical report author. "
        "Generate a highly professional, well-structured, comprehensive report in Markdown format.\n"
        "GUIDELINES:\n"
        "1. Follow the specified sections closely.\n"
        "2. Ground all factual assertions, figures, and dates strictly in the provided documents.\n"
        "3. Explicitly distinguish between source-derived factual findings and forward-looking strategic recommendations.\n"
        "4. Include tables, formatted metrics, and bulleted breakdowns where appropriate for clarity.\n"
        f"5. Detail Level: {detail_level.upper()} (provide rich detail and depth matching this level).\n"
        f"6. Target Audience: {audience or 'General Executive & Technical Stakeholders'}.\n"
        f"7. Report Purpose: {purpose or 'Comprehensive analytical evaluation'}.\n"
        "8. Conclude with a clear list of source documents referenced."
    )

    user_prompt = (
        f"Report Title: {default_title}\n"
        f"Report Type: {report_type}\n"
        f"Sections to include: {', '.join(chosen_sections)}\n\n"
        f"Source Documents Content:\n{full_context}"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    report_markdown = call_llm(messages, temperature=0.3, max_tokens=4096)

    config_data = {
        "title": default_title,
        "purpose": purpose or "",
        "audience": audience or "",
        "sections": chosen_sections,
        "detail_level": detail_level,
    }

    report = Report(
        id=str(uuid.uuid4()),
        document_ids=json.dumps(document_ids),
        report_type=report_type,
        config=json.dumps(config_data),
        content=report_markdown,
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return report


def get_report(report_id: str, db: Session) -> Report | None:
    """Get report by ID."""
    return db.query(Report).filter(Report.id == report_id).first()


def list_reports(db: Session) -> list[Report]:
    """List all reports."""
    return db.query(Report).order_by(Report.created_at.desc()).all()


def update_report(report_id: str, content: str, db: Session) -> Report:
    """Update report content."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise ValueError(f"Report {report_id} not found")
    report.content = content
    db.commit()
    db.refresh(report)
    return report


def delete_report(report_id: str, db: Session) -> bool:
    """Delete a report by ID."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        return False
    db.delete(report)
    db.commit()
    return True
