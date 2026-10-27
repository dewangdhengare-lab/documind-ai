"""PDF text extraction using pypdf."""

from pathlib import Path
from pypdf import PdfReader


def extract_text_from_pdf(file_path: Path) -> tuple[list[dict], int]:
    """
    Extract text from a PDF file, page by page.

    Returns:
        A tuple of (pages, page_count) where pages is a list of dicts
        with keys 'page_number' and 'text'.
    """
    reader = PdfReader(str(file_path))
    pages: list[dict] = []
    total_pages = len(reader.pages)

    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = text.strip()
        if text:
            pages.append({
                "page_number": i,
                "text": text,
            })

    # Detect scanned documents where no text layer exists
    if total_pages > 0 and len(pages) == 0:
        raise ValueError(
            f"This PDF has {total_pages} page(s) consisting of scanned images without an extractable text layer. "
            "Please upload a searchable PDF (with selectable text) or run OCR to add a text layer."
        )

    return pages, total_pages
