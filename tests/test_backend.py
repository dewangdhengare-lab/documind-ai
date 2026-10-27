"""Root test runner for DocuMind AI backend tests."""

import sys
from pathlib import Path

# Ensure backend directory is in sys.path
root_dir = Path(__file__).resolve().parent.parent
backend_dir = root_dir / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Import all tests from backend/tests/test_backend.py
from backend.tests.test_backend import (
    setup_database,
    test_health_endpoint,
    test_parsers,
    test_chunking_and_vector_store,
    test_document_upload_and_pipeline,
    test_export_service,
    test_invalid_file_upload,
)
