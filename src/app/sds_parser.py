"""
Helper functions for working with SDS PDF files, including text
extraction and section detection.
"""

import re
import fitz  # PyMuPDF


def extract_text_from_pdf(path: str) -> str:
    """Extract all text from a PDF file using PyMuPDF."""
    text_chunks = []

    with fitz.open(path) as doc:
        for page in doc:
            text_chunks.append(page.get_text("text"))

    return "\n".join(text_chunks)


def normalize_text(text: str) -> str:
    """Clean extracted PDF text to make section detection easier."""
    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()


SECTION_PATTERNS = {
    1: r"(section\s*)?\b1[\.\:\)]?\s*(identification)",
    2: r"(section\s*)?\b2[\.\:\)]?\s*(hazard[s]?\s+identification)",
    3: r"(section\s*)?\b3[\.\:\)]?\s*(composition|information on ingredients)",
    4: r"(section\s*)?\b4[\.\:\)]?\s*(first[\s-]?aid)",
    5: r"(section\s*)?\b5[\.\:\)]?\s*(fire[\s-]?fighting)",
    6: r"(section\s*)?\b6[\.\:\)]?\s*(accidental release)",
    7: r"(section\s*)?\b7[\.\:\)]?\s*(handling and storage)",
    8: r"(section\s*)?\b8[\.\:\)]?\s*(exposure controls|personal protection)",
    9: r"(section\s*)?\b9[\.\:\)]?\s*(physical and chemical properties)",
    10: r"(section\s*)?\b10[\.\:\)]?\s*(stability and reactivity)",
    11: r"(section\s*)?\b11[\.\:\)]?\s*(toxicological information)",
    12: r"(section\s*)?\b12[\.\:\)]?\s*(ecological information)",
    13: r"(section\s*)?\b13[\.\:\)]?\s*(disposal considerations)",
    14: r"(section\s*)?\b14[\.\:\)]?\s*(transport information)",
    15: r"(section\s*)?\b15[\.\:\)]?\s*(regulatory information)",
    16: r"(section\s*)?\b16[\.\:\)]?\s*(other information)",
}


def split_into_sections(text: str) -> dict:
    """Split extracted SDS text into numbered sections."""
    text = normalize_text(text)
    matches = []

    for section_number, pattern in SECTION_PATTERNS.items():
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            matches.append((section_number, match.start(), match.group(0)))

    matches.sort(key=lambda item: item[1])

    sections = {}

    for i, (section_number, start_pos, matched_heading) in enumerate(matches):
        if i + 1 < len(matches):
            end_pos = matches[i + 1][1]
        else:
            end_pos = len(text)

        sections[section_number] = text[start_pos:end_pos].strip()

    return sections
        




