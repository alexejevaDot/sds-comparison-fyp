import json
from pathlib import Path


class ChemicalReferenceRepository:
    """
    Repository for looking up hazard-code and substance reference data
    from a small local JSON database.
    """

    def __init__(self, json_path=None):
        if json_path is None:
            self.json_path = Path(__file__).resolve().parents[2] / "data" / "chemical_reference.json"
        else:
            self.json_path = Path(json_path)

        self.data = self._load_data()
        self.hazard_code_index = {
            item["code"].upper(): item
            for item in self.data.get("hazard_codes", [])
            if "code" in item
        }
        self.substance_name_index = {
            item["name"].strip().lower(): item
            for item in self.data.get("substances", [])
            if "name" in item
        }
        self.cas_index = {
            item["cas_number"].strip(): item
            for item in self.data.get("substances", [])
            if item.get("cas_number")
        }

    def _load_data(self):
        if not self.json_path.exists():
            return {"hazard_codes": [], "substances": []}

        with open(self.json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_hazard_code(self, code):
        if not code:
            return None
        return self.hazard_code_index.get(code.strip().upper())

    def get_hazard_codes(self, codes):
        results = []
        seen = set()

        for code in codes:
            match = self.get_hazard_code(code)
            if match and match["code"] not in seen:
                results.append(match)
                seen.add(match["code"])

        return results

    def get_substance_by_name(self, name):
        if not name:
            return None
        return self.substance_name_index.get(name.strip().lower())

    def get_substance_by_cas(self, cas_number):
        if not cas_number:
            return None
        return self.cas_index.get(cas_number.strip())