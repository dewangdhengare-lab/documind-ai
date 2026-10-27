"""Document upload, processing, management, and deletion service."""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from config import settings
from models import Document, Summary, Extraction, Comparison, Quiz, QuizAttempt, Conversation, Message
from services.pdf_parser import extract_text_from_pdf
from services.docx_parser import extract_text_from_docx
from services.txt_parser import extract_text_from_txt
from services.csv_service import parse_csv
from services.chunking_service import chunk_document_sections
from services.vector_store import add_chunks, delete_document_chunks

logger = logging.getLogger(__name__)


def save_upload(
    file_content: bytes,
    original_filename: str,
    file_type: str,
    file_size: int,
    db: Session,
) -> Document:
    """
    Save an uploaded file to disk and create a Document record.
    Returns the Document with status='processing'.
    """
    doc_id = str(uuid.uuid4())
    ext = Path(original_filename).suffix.lower()
    stored_filename = f"{doc_id}{ext}"
    file_path = settings.UPLOAD_DIR / stored_filename

    # Write file to disk
    file_path.write_bytes(file_content)

    # Create DB record
    doc = Document(
        id=doc_id,
        filename=stored_filename,
        original_filename=original_filename,
        file_type=file_type,
        file_size=file_size,
        status="processing",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return doc


def process_document(document_id: str, db: Session) -> None:
    """
    Process a document: extract text, chunk it, and store embeddings.
    Updates the document status to 'ready' or 'failed'.
    """
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        logger.error("Document %s not found for processing", document_id)
        return

    try:
        file_path = settings.UPLOAD_DIR / doc.filename
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = Path(doc.filename).suffix.lower()

        # Extract text based on file type
        sections: list[dict[str, Any]] = []
        page_count: int | None = None

        if ext == ".pdf":
            pages, page_count = extract_text_from_pdf(file_path)
            # Convert pages to sections format
            sections = [
                {
                    "text": p["text"],
                    "page_number": p["page_number"],
                }
                for p in pages
            ]
        elif ext == ".docx":
            sections, page_count = extract_text_from_docx(file_path)
        elif ext == ".txt":
            sections, page_count = extract_text_from_txt(file_path)
        elif ext == ".csv":
            sections, csv_meta = parse_csv(file_path)
            page_count = 1
        else:
            raise ValueError(f"Unsupported file type: {ext}")

        if not sections:
            raise ValueError("No text content could be extracted from the document.")

        # Chunk the sections
        chunks = chunk_document_sections(
            sections=sections,
            document_id=document_id,
            filename=doc.original_filename,
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )

        if not chunks:
            raise ValueError("Chunking produced no chunks.")

        # Store chunks in vector store
        chunk_count = add_chunks(chunks)

        # Update document status
        doc.status = "ready"
        doc.page_count = page_count
        doc.chunk_count = chunk_count
        doc.updated_at = datetime.now(timezone.utc)
        db.commit()

        logger.info(
            "Document %s processed: %d pages, %d chunks",
            document_id, page_count or 0, chunk_count,
        )

    except Exception as e:
        logger.exception("Failed to process document %s", document_id)
        doc.status = "failed"
        doc.error_message = str(e)
        doc.updated_at = datetime.now(timezone.utc)
        db.commit()


def delete_document(document_id: str, db: Session) -> bool:
    """
    Delete a document and all associated data.
    Returns True if the document was found and deleted.
    """
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        return False

    # Delete chunks from vector store
    delete_document_chunks(document_id)

    # Delete file from disk
    file_path = settings.UPLOAD_DIR / doc.filename
    if file_path.exists():
        try:
            file_path.unlink()
        except OSError as e:
            logger.warning("Failed to delete file %s: %s", file_path, e)

    # Delete related comparisons that reference this document
    comparisons = db.query(Comparison).all()
    for comp in comparisons:
        try:
            doc_ids = json.loads(comp.document_ids)
            if document_id in doc_ids:
                db.delete(comp)
        except (json.JSONDecodeError, TypeError):
            pass

    # Delete conversations that reference this document
    conversations = db.query(Conversation).all()
    for conv in conversations:
        try:
            doc_ids = json.loads(conv.document_ids)
            if document_id in doc_ids:
                db.delete(conv)
        except (json.JSONDecodeError, TypeError):
            pass

    # Delete the document (cascades to summaries, extractions, quizzes/attempts)
    db.delete(doc)
    db.commit()

    logger.info("Deleted document %s and all related data", document_id)
    return True


def get_document(document_id: str, db: Session) -> Document | None:
    """Get a document by ID."""
    return db.query(Document).filter(Document.id == document_id).first()


def list_documents(db: Session) -> list[Document]:
    """List all documents ordered by creation date (newest first)."""
    return db.query(Document).order_by(Document.created_at.desc()).all()
