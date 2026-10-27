"""Comprehensive automated test suite for DocuMind AI backend."""

import os
import sys
import json
import io
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from config import settings
from database import init_db, SessionLocal, engine
from models import Document, Conversation, Message, Summary, Extraction, Comparison, Quiz, QuizAttempt, Report
from main import app
import services.document_service as doc_service
from services.pdf_parser import extract_text_from_pdf
from services.docx_parser import extract_text_from_docx
from services.txt_parser import extract_text_from_txt
from services.csv_service import parse_csv, run_csv_query
from services.chunking_service import chunk_document_sections
from services.vector_store import add_chunks, search_chunks, get_chunks_by_document
from services.export_service import export_report_to_pdf, export_report_to_docx

client = TestClient(app)
test_files_dir = backend_dir.parent / "test_files"


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Ensure database tables exist."""
    init_db()
    yield


def test_health_endpoint():
    """Test the health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "DocuMind AI Backend"


def test_parsers():
    """Test all file parsers on actual generated files."""
    # 1. TXT parser
    txt_path = test_files_dir / "sample_report.txt"
    assert txt_path.exists()
    sections, pages = extract_text_from_txt(txt_path)
    assert len(sections) > 0
    assert any("TechVision Solutions" in s["text"] for s in sections)

    # 2. CSV parser
    csv_path = test_files_dir / "sales_data.csv"
    assert csv_path.exists()
    csv_sections, csv_meta = parse_csv(csv_path)
    assert len(csv_sections) > 0
    assert "columns" in csv_meta
    assert "Revenue" in csv_meta["columns"]

    # Test CSV analytics query
    csv_query_res = run_csv_query(csv_path, "total revenue and units sold")
    assert "20 rows" in csv_query_res

    # 3. DOCX parser
    docx_path = test_files_dir / "project_plan.docx"
    assert docx_path.exists()
    docx_sections, docx_pages = extract_text_from_docx(docx_path)
    assert len(docx_sections) > 0
    assert any("Project Phoenix" in s["text"] for s in docx_sections)

    # 4. PDF parser
    pdf_path = test_files_dir / "research_paper.pdf"
    assert pdf_path.exists()
    pdf_pages, pdf_page_count = extract_text_from_pdf(pdf_path)
    assert pdf_page_count >= 4
    assert len(pdf_pages) >= 4
    assert any("Artificial Intelligence" in p["text"] for p in pdf_pages)


def test_chunking_and_vector_store():
    """Test text chunking and vector storage."""
    sections = [
        {"text": "Artificial Intelligence is transforming modern healthcare systems with diagnostic improvements.", "page_number": 1, "heading": "Introduction"},
        {"text": "Project Phoenix migrated legacy systems with an operational cost reduction of 35 percent.", "page_number": 2, "heading": "Milestones"},
    ]
    chunks = chunk_document_sections(
        sections=sections,
        document_id="test-doc-123",
        filename="test.txt",
        chunk_size=200,
        chunk_overlap=20,
    )
    assert len(chunks) == 2
    assert chunks[0]["metadata"]["document_id"] == "test-doc-123"

    # Test adding to vector store
    added_count = add_chunks(chunks)
    assert added_count == 2

    # Test retrieving by document
    retrieved = get_chunks_by_document("test-doc-123")
    assert len(retrieved) == 2

    # Test semantic search
    search_res = search_chunks("healthcare diagnostic", document_ids=["test-doc-123"], top_k=2)
    assert len(search_res) > 0
    assert "healthcare" in search_res[0]["text"].lower()


def test_document_upload_and_pipeline():
    """Test uploading a file via API and running synchronous processing."""
    txt_path = test_files_dir / "sample_report.txt"
    with open(txt_path, "rb") as f:
        response = client.post(
            "/api/documents/upload",
            files={"file": ("sample_report.txt", f, "text/plain")},
        )
    assert response.status_code == 201
    doc_data = response.json()
    doc_id = doc_data["id"]
    assert doc_data["original_filename"] == "sample_report.txt"

    # Manually trigger processing to verify synchronous flow
    db = SessionLocal()
    try:
        doc_service.process_document(doc_id, db)
        updated_doc = doc_service.get_document(doc_id, db)
        assert updated_doc.status == "ready"
        assert updated_doc.chunk_count > 0
    finally:
        db.close()

    # Get document via API
    get_res = client.get(f"/api/documents/{doc_id}")
    assert get_res.status_code == 200
    assert get_res.json()["status"] == "ready"

    # Get chunks via API
    chunks_res = client.get(f"/api/documents/{doc_id}/chunks")
    assert chunks_res.status_code == 200
    assert len(chunks_res.json()) > 0


def test_export_service():
    """Test generating real PDF and DOCX exports."""
    sample_markdown = (
        "# Executive Evaluation Report\n\n"
        "## 1. Summary\n"
        "This is a **key finding** of the evaluation with *high confidence*.\n\n"
        "## 2. Key Metrics\n"
        "- Metric 1: $12.5M revenue (up 15%)\n"
        "- Metric 2: 94.2% client retention rate\n\n"
        "| Metric | Q2 2024 | Q3 2024 |\n"
        "| --- | --- | --- |\n"
        "| Revenue | $10.9M | $12.5M |\n"
        "| Margin | 16.2% | 18.4% |\n\n"
        "### Conclusion\n"
        "All targets were achieved successfully."
    )

    # Test PDF generation
    pdf_buffer = export_report_to_pdf("Test Report", sample_markdown)
    assert pdf_buffer is not None
    pdf_bytes = pdf_buffer.getvalue()
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF")

    # Test DOCX generation
    docx_buffer = export_report_to_docx("Test Report", sample_markdown)
    assert docx_buffer is not None
    docx_bytes = docx_buffer.getvalue()
    assert len(docx_bytes) > 500
    # DOCX files are zip archives starting with PK
    assert docx_bytes.startswith(b"PK")


def test_invalid_file_upload():
    """Test validation of unsupported file extensions."""
    response = client.post(
        "/api/documents/upload",
        files={"file": ("malicious.exe", b"binarycontent", "application/octet-stream")},
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


if __name__ == "__main__":
    pytest.main(["-v", __file__])
