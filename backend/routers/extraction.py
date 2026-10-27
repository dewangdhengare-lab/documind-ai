"""Router for information extraction endpoints."""

from __future__ import annotations

import json
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from database import get_db
from schemas import ExtractRequest, ExtractionResponse
import services.extraction_service as ext_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["extraction"])


def _format_extraction(ext) -> ExtractionResponse:
    """Format Extraction model to ExtractionResponse with parsed result."""
    result_val = ext.result
    if isinstance(result_val, str):
        try:
            result_val = json.loads(result_val)
        except Exception:
            pass

    return ExtractionResponse(
        id=ext.id,
        document_id=ext.document_id,
        instruction=ext.instruction,
        result=result_val,
        created_at=ext.created_at,
    )


@router.post("/api/extract", response_model=ExtractionResponse, status_code=status.HTTP_201_CREATED)
@router.post("/api/extractions", response_model=ExtractionResponse, status_code=status.HTTP_201_CREATED)
def extract_information(
    req: ExtractRequest,
    db: Session = Depends(get_db),
):
    """Extract structured data from a document."""
    try:
        ext = ext_service.extract_information(
            document_id=req.document_id,
            instruction=req.instruction,
            db=db,
        )
        return _format_extraction(ext)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Extraction failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@router.get("/api/extractions", response_model=list[ExtractionResponse])
def list_extractions(
    document_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List extractions, optionally filtered by document_id."""
    items = ext_service.list_extractions(document_id=document_id, db=db)
    return [_format_extraction(item) for item in items]


@router.get("/api/extractions/{extraction_id}", response_model=ExtractionResponse)
def get_extraction(extraction_id: str, db: Session = Depends(get_db)):
    """Get single extraction by ID."""
    ext = ext_service.get_extraction(extraction_id, db)
    if not ext:
        raise HTTPException(status_code=404, detail="Extraction not found.")
    return _format_extraction(ext)


@router.delete("/api/extractions/{extraction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_extraction(extraction_id: str, db: Session = Depends(get_db)):
    """Delete an extraction by ID."""
    success = ext_service.delete_extraction(extraction_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Extraction not found.")
    return None


@router.get("/api/extractions/{extraction_id}/export")
def export_extraction(
    extraction_id: str,
    format: str = Query(default="json", pattern="^(csv|json)$"),
    db: Session = Depends(get_db),
):
    """Export extraction result as downloadable CSV or JSON."""
    ext = ext_service.get_extraction(extraction_id, db)
    if not ext:
        raise HTTPException(status_code=404, detail="Extraction not found.")

    content, media_type, filename = ext_service.export_extraction_data(ext, format=format)
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
