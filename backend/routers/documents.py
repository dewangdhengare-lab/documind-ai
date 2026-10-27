"""Router for document management endpoints."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, status
from sqlalchemy.orm import Session

from config import settings
from database import get_db, SessionLocal
from schemas import DocumentResponse, ChunkResponse
import services.document_service as doc_service
from services.vector_store import get_chunks_by_document

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents", tags=["documents"])


def _process_in_background(document_id: str):
    """Background task function that opens its own DB session."""
    db = SessionLocal()
    try:
        doc_service.process_document(document_id, db)
    finally:
        db.close()


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload a document (PDF, DOCX, TXT, CSV) and trigger background ingestion."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    ext = Path(file.filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed types: {', '.join(sorted(settings.ALLOWED_EXTENSIONS))}",
        )

    # Read content and check size
    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum size of {settings.MAX_FILE_SIZE_MB}MB.",
        )

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    doc = doc_service.save_upload(
        file_content=content,
        original_filename=file.filename,
        file_type=ext,
        file_size=len(content),
        db=db,
    )

    # Launch background processing
    background_tasks.add_task(_process_in_background, doc.id)

    return doc


@router.get("", response_model=list[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    """List all uploaded documents."""
    return doc_service.list_documents(db)


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: str, db: Session = Depends(get_db)):
    """Get single document metadata and processing status."""
    doc = doc_service.get_document(document_id, db)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return doc


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: str, db: Session = Depends(get_db)):
    """Delete a document, its stored file, its vector embeddings, and related data."""
    success = doc_service.delete_document(document_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found.")
    return None


@router.post("/{document_id}/retry", response_model=DocumentResponse)
def retry_document_processing(
    document_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Retry processing a failed document."""
    doc = doc_service.get_document(document_id, db)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    doc.status = "processing"
    doc.error_message = None
    db.commit()
    db.refresh(doc)

    background_tasks.add_task(_process_in_background, document_id)
    return doc


@router.get("/{document_id}/chunks", response_model=list[ChunkResponse])
def get_document_chunks(document_id: str, db: Session = Depends(get_db)):
    """Get chunks generated for a document."""
    doc = doc_service.get_document(document_id, db)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    raw_chunks = get_chunks_by_document(document_id)
    return [
        ChunkResponse(
            id=c["id"],
            content=c["text"],
            metadata=c.get("metadata", {}),
        )
        for c in raw_chunks
    ]
