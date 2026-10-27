"""Router for summarization endpoints."""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from schemas import SummarizeRequest, SummaryResponse
import services.summarization_service as sum_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["summarization"])


@router.post("/api/summarize", response_model=SummaryResponse, status_code=status.HTTP_201_CREATED)
@router.post("/api/summaries", response_model=SummaryResponse, status_code=status.HTTP_201_CREATED)
def generate_summary(
    req: SummarizeRequest,
    db: Session = Depends(get_db),
):
    """Generate a structured summary for a ready document."""
    try:
        return sum_service.generate_summary(
            document_id=req.document_id,
            summary_type=req.summary_type,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Failed to generate summary: %s", e)
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")


@router.get("/api/summaries", response_model=list[SummaryResponse])
def list_summaries(
    document_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List summaries, optionally filtered by document_id."""
    return sum_service.list_summaries(document_id=document_id, db=db)


@router.get("/api/summaries/{summary_id}", response_model=SummaryResponse)
def get_summary(summary_id: str, db: Session = Depends(get_db)):
    """Get single summary by ID."""
    summary = sum_service.get_summary(summary_id, db)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found.")
    return summary


@router.delete("/api/summaries/{summary_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_summary(summary_id: str, db: Session = Depends(get_db)):
    """Delete a summary by ID."""
    success = sum_service.delete_summary(summary_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Summary not found.")
    return None
