import re
from chemical_reference_repository import ChemicalReferenceRepository


SIGNAL_WORD_PATTERN = re.compile(r'\b(Danger|Warning)\b', re.IGNORECASE)
H_CODE_PATTERN = re.compile(r'H\d{3}[A-Z]?(?=\b|;|,|\s)', re.IGNORECASE)
P_CODE_PATTERN = re.compile(r'P\d{3}(?:\+\w+)?(?=\b|;|,|\s)', re.IGNORECASE)

repo = ChemicalReferenceRepository()


def extract_section2_hazards(section_text: str) -> dict:
    if not section_text:
        return {
            "signal_words": [],
            "h_codes": [],
            "p_codes": []
        }

    signal_words = sorted({
        match.group(1).capitalize()
        for match in SIGNAL_WORD_PATTERN.finditer(section_text)
    })

    h_codes = sorted({
        match.group(0).upper()
        for match in H_CODE_PATTERN.finditer(section_text)
    })

    p_codes = sorted({
        match.group(0).upper()
        for match in P_CODE_PATTERN.finditer(section_text)
    })

    return {
        "signal_words": signal_words,
        "h_codes": h_codes,
        "p_codes": p_codes
    }


def compare_lists(old_list, new_list) -> dict:
    old_set = set(old_list)
    new_set = set(new_list)

    return {
        "added": sorted(new_set - old_set),
        "removed": sorted(old_set - new_set),
        "unchanged": sorted(old_set & new_set)
    }


def build_guidance_block(code_diff: dict) -> dict:
    return {
        "added": repo.get_hazard_codes(code_diff["added"]),
        "removed": repo.get_hazard_codes(code_diff["removed"]),
        "unchanged": repo.get_hazard_codes(code_diff["unchanged"])
    }


def analyse_section2_changes(old_text: str, new_text: str) -> dict:
    old_data = extract_section2_hazards(old_text)
    new_data = extract_section2_hazards(new_text)

    signal_word_diff = compare_lists(old_data["signal_words"], new_data["signal_words"])
    h_code_diff = compare_lists(old_data["h_codes"], new_data["h_codes"])
    p_code_diff = compare_lists(old_data["p_codes"], new_data["p_codes"])

    section2_changed = any([
        signal_word_diff["added"],
        signal_word_diff["removed"],
        h_code_diff["added"],
        h_code_diff["removed"],
        p_code_diff["added"],
        p_code_diff["removed"]
    ])


    return {
        "old": old_data,
        "new": new_data,
        "signal_words": signal_word_diff,
        "h_codes": h_code_diff,
        "p_codes": p_code_diff,
        "h_code_guidance": build_guidance_block(h_code_diff),
        "section2_changed": section2_changed
    }