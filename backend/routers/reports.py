"""Router for report generation, editing, and document export endpoints."""

from __future__ import annotations

import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from database import get_db
from schemas import (
    ReportGenerateRequest,
    ReportUpdateRequest,
    ReportResponse,
)
import services.report_service as report_service
from services.export_service import export_report_to_pdf, export_report_to_docx

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reports", tags=["reports"])


def _format_report(report) -> ReportResponse:
    """Format Report ORM model into ReportResponse schema."""
    doc_ids = []
    try:
        doc_ids = json.loads(report.document_ids)
    except Exception:
        pass

    config_data = {}
    try:
        config_data = json.loads(report.config)
    except Exception:
        pass

    return ReportResponse(
        id=report.id,
        document_ids=doc_ids,
        report_type=report.report_type,
        config=config_data,
        content=report.content,
        created_at=report.created_at,
        updated_at=report.updated_at,
    )


@router.post("/generate", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def generate_report(
    req: ReportGenerateRequest,
    db: Session = Depends(get_db),
):
    """Generate a structured corporate/technical report from one or multiple documents."""
    try:
        rep = report_service.generate_report(
            document_ids=req.document_ids,
            report_type=req.report_type,
            title=req.title,
            purpose=req.purpose,
            audience=req.audience,
            sections=req.sections,
            detail_level=req.detail_level,
            db=db,
        )
        return _format_report(rep)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Report generation failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.get("", response_model=list[ReportResponse])
def list_reports(db: Session = Depends(get_db)):
    """List all saved reports."""
    reports = report_service.list_reports(db)
    return [_format_report(r) for r in reports]


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(report_id: str, db: Session = Depends(get_db)):
    """Get single report by ID."""
    rep = report_service.get_report(report_id, db)
    if not rep:
        raise HTTPException(status_code=404, detail="Report not found.")
    return _format_report(rep)


@router.put("/{report_id}", response_model=ReportResponse)
def update_report(
    report_id: str,
    req: ReportUpdateRequest,
    db: Session = Depends(get_db),
):
    """Update report markdown content."""
    try:
        rep = report_service.update_report(report_id, req.content, db)
        return _format_report(rep)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(report_id: str, db: Session = Depends(get_db)):
    """Delete report by ID."""
    success = report_service.delete_report(report_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Report not found.")
    return None


@router.get("/{report_id}/export")
def export_report(
    report_id: str,
    format: str = Query(default="pdf", pattern="^(pdf|docx)$"),
    db: Session = Depends(get_db),
):
    """Export report as real, styled PDF or DOCX file."""
    rep = report_service.get_report(report_id, db)
    if not rep:
        raise HTTPException(status_code=404, detail="Report not found.")

    config_data = {}
    try:
        config_data = json.loads(rep.config)
    except Exception:
        pass

    title = config_data.get("title", f"Report_{rep.id[:8]}")

    if format.lower() == "pdf":
        try:
            pdf_buffer = export_report_to_pdf(title, rep.content)
            filename = f"report_{rep.id[:8]}.pdf"
            return Response(
                content=pdf_buffer.getvalue(),
                media_type="application/pdf",
                headers={"Content-Disposition": f'attachment; filename="{filename}"'},
            )
        except Exception as e:
            logger.exception("PDF export failed: %s", e)
            raise HTTPException(status_code=500, detail=f"PDF export failed: {str(e)}")
    else:
        try:
            docx_buffer = export_report_to_docx(title, rep.content)
            filename = f"report_{rep.id[:8]}.docx"
            return Response(
                content=docx_buffer.getvalue(),
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                headers={"Content-Disposition": f'attachment; filename="{filename}"'},
            )
        except Exception as e:
            logger.exception("DOCX export failed: %s", e)
            raise HTTPException(status_code=500, detail=f"DOCX export failed: {str(e)}")
