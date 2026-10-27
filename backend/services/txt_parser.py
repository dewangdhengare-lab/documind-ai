"""Plain text file processing."""

from pathlib import Path


def extract_text_from_txt(file_path: Path) -> tuple[list[dict], int]:
    """
    Read a TXT file and split it into sections by double newlines.

    Returns:
        A tuple of (sections, page_count_estimate).
    """
    content = file_path.read_text(encoding="utf-8", errors="replace")

    # Split on double newlines to get logical paragraphs/sections
    raw_sections = content.split("\n\n")
    sections: list[dict] = []
    for i, section_text in enumerate(raw_sections):
        text = section_text.strip()
        if text:
            sections.append({
                "section_index": i,
                "heading": None,
                "text": text,
            })

    total_chars = sum(len(s["text"]) for s in sections)
    estimated_pages = max(1, total_chars // 3000)

    return sections, estimated_pages
