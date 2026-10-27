"""Information extraction service."""

from __future__ import annotations

import csv
import io
import json
import logging
import uuid
from typing import Any

from sqlalchemy.orm import Session

from models import Document, Extraction
from services.vector_store import get_chunks_by_document
from services.llm_service import call_llm
from services.csv_service import parse_csv

logger = logging.getLogger(__name__)


def _get_document_full_text(document_id: str) -> str:
    """Retrieve full text from stored chunks of the document."""
    chunks = get_chunks_by_document(document_id)
    if not chunks:
        return ""
    return "\n\n".join(c["text"] for c in chunks)


def extract_information(
    document_id: str,
    instruction: str,
    db: Session,
) -> Extraction:
    """
    Extract structured information from a document based on instructions.
    Returns an Extraction record with JSON-serialized result.
    """
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise ValueError(f"Document {document_id} not found")
    if doc.status != "ready":
        raise ValueError(f"Document '{doc.original_filename}' is not ready (status: {doc.status})")

    full_text = _get_document_full_text(document_id)
    if not full_text.strip():
        raise ValueError(f"No text content found for document '{doc.original_filename}'")

    max_chars = 8000
    if len(full_text) > max_chars:
        truncated_text = (
            full_text[:5000]
            + "\n\n[... content truncated to fit token limits ...]\n\n"
            + full_text[-3000:]
        )
    else:
        truncated_text = full_text

    system_prompt = (
        "You are an expert data extraction assistant. "
        "Extract structured information from the document according to the user's instructions.\n"
        "RULES:\n"
        "1. Extract ONLY facts explicitly stated in the document.\n"
        "2. If an item or attribute is missing from the document, indicate it as 'Not Specified' or null.\n"
        "3. Output MUST be a valid JSON object with the following structure:\n"
        "{\n"
        '  "title": "Title of the extraction",\n'
        '  "headers": ["Field 1", "Field 2", ...],\n'
        '  "rows": [\n'
        '    {"Field 1": "value", "Field 2": "value"},\n'
        '    ...\n'
        "  ],\n"
        '  "summary": "Brief 1-2 sentence overview of extracted entities",\n'
        '  "source_notes": "Specific references or page/section locations if available"\n'
        "}\n"
        "Do NOT include markdown formatting or backticks around the JSON. Output raw JSON only."
    )

    user_prompt = f"Instruction: {instruction}\n\nDocument ({doc.original_filename}):\n{truncated_text}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    response_text = call_llm(messages, temperature=0.1)

    # Clean response in case of markdown formatting
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
        logger.warning("Failed to parse JSON directly from LLM, attempting fallback structure: %s", e)
        parsed_result = {
            "title": "Extraction Result",
            "headers": ["Information", "Details"],
            "rows": [{"Information": "Extracted Content", "Details": response_text}],
            "summary": "Extracted text content from document.",
            "source_notes": f"Extracted from {doc.original_filename}",
        }

    extraction = Extraction(
        id=str(uuid.uuid4()),
        document_id=document_id,
        instruction=instruction,
        result=json.dumps(parsed_result),
    )
    db.add(extraction)
    db.commit()
    db.refresh(extraction)

    return extraction


def get_extraction(extraction_id: str, db: Session) -> Extraction | None:
    """Get an extraction by ID."""
    return db.query(Extraction).filter(Extraction.id == extraction_id).first()


def list_extractions(document_id: str | None, db: Session) -> list[Extraction]:
    """List extractions, optionally filtered by document_id."""
    query = db.query(Extraction)
    if document_id:
        query = query.filter(Extraction.document_id == document_id)
    return query.order_by(Extraction.created_at.desc()).all()


def delete_extraction(extraction_id: str, db: Session) -> bool:
    """Delete an extraction by ID."""
    extraction = db.query(Extraction).filter(Extraction.id == extraction_id).first()
    if not extraction:
        return False
    db.delete(extraction)
    db.commit()
    return True


def export_extraction_data(extraction: Extraction, format: str = "json") -> tuple[str, str, str]:
    """
    Export extraction result.
    Returns (content_string, media_type, filename).
    """
    data = json.loads(extraction.result) if isinstance(extraction.result, str) else extraction.result
    
    if format.lower() == "csv":
        output = io.StringIO()
        headers = data.get("headers", [])
        rows = data.get("rows", [])
        
        if not headers and rows and isinstance(rows, list) and isinstance(rows[0], dict):
            headers = list(rows[0].keys())

        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            if isinstance(row, dict):
                writer.writerow(row)
        
        return output.getvalue(), "text/csv", f"extraction_{extraction.id[:8]}.csv"
    
    # JSON default
    return json.dumps(data, indent=2), "application/json", f"extraction_{extraction.id[:8]}.json"
