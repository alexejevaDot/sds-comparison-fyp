"""
Helper functions for working with SDS PDF files, including text
extraction and section detection.
"""

import fitz  # PyMuPDF

def extract_text_from_pdf(path: str) -> str:
    
    """Extract all text from a PDF file using PyMuPDF."""
    text_chunks = []
    with fitz.open(path) as doc:
        for page in doc:
            text_chunks.append(page.get_text())
    return "\n".join(text_chunks)