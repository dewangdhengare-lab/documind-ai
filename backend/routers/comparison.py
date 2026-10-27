"""Router for multi-document comparison endpoints."""

from __future__ import annotations

import json
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from schemas import CompareRequest, ComparisonResponse
import services.comparison_service as comp_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["comparison"])


def _format_comparison(comp) -> ComparisonResponse:
    """Format Comparison ORM model to ComparisonResponse schema."""
    doc_ids = []
    try:
        doc_ids = json.loads(comp.document_ids)
    except Exception:
        pass

    result_val = comp.result
    if isinstance(result_val, str):
        try:
            result_val = json.loads(result_val)
        except Exception:
            pass

    return ComparisonResponse(
        id=comp.id,
        document_ids=doc_ids,
        result=result_val,
        created_at=comp.created_at,
    )


@router.post("/api/compare", response_model=ComparisonResponse, status_code=status.HTTP_201_CREATED)
@router.post("/api/comparisons", response_model=ComparisonResponse, status_code=status.HTTP_201_CREATED)
def compare_documents(
    req: CompareRequest,
    db: Session = Depends(get_db),
):
    """Compare 2 to 5 uploaded documents."""
    try:
        comp = comp_service.compare_documents(
            document_ids=req.document_ids,
            db=db,
        )
        return _format_comparison(comp)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Comparison failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


@router.get("/api/comparisons", response_model=list[ComparisonResponse])
def list_comparisons(db: Session = Depends(get_db)):
    """List all saved comparisons."""
    comps = comp_service.list_comparisons(db)
    return [_format_comparison(c) for c in comps]


@router.get("/api/comparisons/{comparison_id}", response_model=ComparisonResponse)
def get_comparison(comparison_id: str, db: Session = Depends(get_db)):
    """Get single comparison by ID."""
    comp = comp_service.get_comparison(comparison_id, db)
    if not comp:
        raise HTTPException(status_code=404, detail="Comparison not found.")
    return _format_comparison(comp)


@router.delete("/api/comparisons/{comparison_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comparison(comparison_id: str, db: Session = Depends(get_db)):
    """Delete comparison by ID."""
    success = comp_service.delete_comparison(comparison_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Comparison not found.")
    return None
