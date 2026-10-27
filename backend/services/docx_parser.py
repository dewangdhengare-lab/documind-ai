"""DOCX text extraction using python-docx."""

from pathlib import Path

from docx import Document as DocxDocument


def extract_text_from_docx(file_path: Path) -> tuple[list[dict], int]:
    """
    Extract text from a DOCX file, preserving heading structure.

    Returns:
        A tuple of (sections, page_count_estimate) where sections is a list of
        dicts with keys 'text', 'heading', and 'section_index'.
        page_count is estimated as total_chars / 3000 (rough approximation).
    """
    doc = DocxDocument(str(file_path))
    sections: list[dict] = []
    current_heading: str | None = None
    current_text_parts: list[str] = []
    section_index = 0

    def _flush():
        nonlocal section_index
        text = "\n".join(current_text_parts).strip()
        if text:
            sections.append({
                "section_index": section_index,
                "heading": current_heading,
                "text": text,
            })
            section_index += 1

    for para in doc.paragraphs:
        style_name = para.style.name if para.style else ""
        if style_name.startswith("Heading"):
            _flush()
            current_heading = para.text.strip() or None
            current_text_parts = []
        else:
            if para.text.strip():
                current_text_parts.append(para.text.strip())

    # Flush last section
    _flush()

    # Estimate page count
    total_chars = sum(len(s["text"]) for s in sections)
    estimated_pages = max(1, total_chars // 3000)

    return sections, estimated_pages
