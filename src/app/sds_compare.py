"""
Helper functions for comparing two sets of SDS sections and identifying changes.
"""

import difflib
import re
from hazard_analysis import analyse_section2_changes


def normalize_for_compare(text: str) -> str:
    text = text.replace("\r", "\n")
    text = text.lower()

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)

    text = re.sub(r"\bversion\s*[:.]?\s*[\w.\-\/]+\b", " ", text)
    text = re.sub(r"\brevision\s*[:.]?\s*[\w.\-\/]+\b", " ", text)
    text = re.sub(r"\bdate\s+of\s+issue\s*[:.]?\s*[\w.\-\/, ]+\b", " ", text)
    text = re.sub(r"\bprint\s+date\s*[:.]?\s*[\w.\-\/, ]+\b", " ", text)
    text = re.sub(r"\bissue\s+date\s*[:.]?\s*[\w.\-\/, ]+\b", " ", text)

    text = re.sub(r"\s+", " ", text)
    return text.strip()


def make_preview(text: str, length: int = 250) -> str:
    text = " ".join(text.split())
    if len(text) <= length:
        return text
    return text[:length] + "..."


def make_change_summary(old_text: str, new_text: str, max_lines: int = 6) -> list:
    old_lines = [line.strip() for line in old_text.splitlines() if line.strip()]
    new_lines = [line.strip() for line in new_text.splitlines() if line.strip()]

    diff = list(difflib.unified_diff(old_lines, new_lines, lineterm=""))
    useful = []

    for line in diff:
        if line.startswith("---") or line.startswith("+++") or line.startswith("@@"):
            continue
        if line.startswith("-") or line.startswith("+"):
            useful.append(line)

    return useful[:max_lines]


def compare_sections(old_sections: dict, new_sections: dict) -> dict:
    all_section_numbers = set(old_sections.keys()) | set(new_sections.keys())
    results = {}

    section2_old_text = old_sections.get("2", old_sections.get(2, ""))
    section2_new_text = new_sections.get("2", new_sections.get(2, ""))

    section2_analysis = analyse_section2_changes(
        section2_old_text,
        section2_new_text
    )

    for section_num in sorted(all_section_numbers, key=lambda x: int(x) if str(x).isdigit() else str(x)):
        old_text = old_sections.get(section_num, "")
        new_text = new_sections.get(section_num, "")

        old_present = section_num in old_sections
        new_present = section_num in new_sections

        old_normalized = normalize_for_compare(old_text)
        new_normalized = normalize_for_compare(new_text)

        changed = old_normalized != new_normalized

        if str(section_num) == "2":
            changed = section2_analysis["section2_changed"]

        results[section_num] = {
            "old_present": old_present,
            "new_present": new_present,
            "old_length": len(old_text),
            "new_length": len(new_text),
            "changed": changed,
            "old_preview": make_preview(old_text),
            "new_preview": make_preview(new_text),
            "change_summary": make_change_summary(old_text, new_text) if changed else [],
        }

    return {
        "sections": results,
        "section2_analysis": section2_analysis
    }

def summarize_changes(comparison_results: dict) -> dict:
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