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
        

"""
Helper functions for comparing two sets of SDS sections and identifying changes.
"""

def compare_sections(old_sections: dict, new_sections: dict) -> dict:
    """
    Compare two dictionaries of SDS sections and return comparison results.
    
    Args:
        old_sections: Dictionary mapping section numbers to text (from old SDS)
        new_sections: Dictionary mapping section numbers to text (from new SDS)
    
    Returns:
        Dictionary with section-level comparison results, keyed by section number.
        Each entry contains: old_present, new_present, old_length, new_length, changed.
    """
    all_section_numbers = set(old_sections.keys()) | set(new_sections.keys())
    
    results = {}
    
    for section_num in sorted(all_section_numbers):
        old_text = old_sections.get(section_num, "")
        new_text = new_sections.get(section_num, "")
        
        old_present = section_num in old_sections
        new_present = section_num in new_sections
        
        # Normalize whitespace for comparison
        old_normalized = " ".join(old_text.split())
        new_normalized = " ".join(new_text.split())
        
        changed = old_normalized != new_normalized
        
        results[section_num] = {
            "old_present": old_present,
            "new_present": new_present,
            "old_length": len(old_text),
            "new_length": len(new_text),
            "changed": changed,
        }
    
    return results


def summarize_changes(comparison_results: dict) -> dict:
    """
    Generate a summary of changes across all sections.
    
    Args:
        comparison_results: Output from compare_sections()
    
    Returns:
        Dictionary with summary statistics: total_sections, sections_changed, etc.
    """
    total_sections = len(comparison_results)
    sections_changed = sum(1 for r in comparison_results.values() if r["changed"])
    sections_unchanged = total_sections - sections_changed
    
    added_sections = [
        num for num, r in comparison_results.items() 
        if not r["old_present"] and r["new_present"]
    ]
    
    removed_sections = [
        num for num, r in comparison_results.items() 
        if r["old_present"] and not r["new_present"]
    ]
    
    return {
        "total_sections": total_sections,
        "sections_changed": sections_changed,
        "sections_unchanged": sections_unchanged,
        "added_sections": added_sections,
        "removed_sections": removed_sections,
    }