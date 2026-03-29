from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def _load_templates() -> Dict[str, Any]:
    with open(DATA_DIR / "application_templates.json", "r", encoding="utf-8") as f:
        return json.load(f)

def infer_requirements(application_prompt: str, operating_temperature: int, am_preferred: bool) -> Dict[str, Any]:
    prompt = (application_prompt or "").lower()
    templates = _load_templates()

    weights = {
        "creep_priority": 0.25,
        "toughness_priority": 0.20,
        "temperature_priority": 0.25,
        "cost_priority": 0.15,
        "sustainability_priority": 0.15,
    }
    notes = []

    for keyword, template in templates.items():
        if keyword in prompt:
            for k in weights:
                weights[k] = max(weights[k], template.get(k, weights[k]))
            notes.extend(template.get("notes", []))

    if operating_temperature >= 800:
        weights["temperature_priority"] = max(weights["temperature_priority"], 0.30)
        weights["creep_priority"] = max(weights["creep_priority"], 0.35)
        notes.append("Operating temperature suggests elevated temperature screening.")
    elif operating_temperature < 500:
        notes.append("Operating temperature suggests a less extreme thermal regime.")

    allowed_material_families = ["Ni-based superalloy", "Co-based alloy", "Fe-Ni alloy", "Ti alloy", "Refractory alloy concept"]
    if operating_temperature >= 850:
        allowed_material_families = ["Ni-based superalloy", "Co-based alloy", "Refractory alloy concept"]

    return {
        "application_prompt": application_prompt,
        "operating_temperature": operating_temperature,
        "am_preferred": am_preferred,
        "allowed_material_families": allowed_material_families,
        "weights": weights,
        "notes": notes or ["Default engineering priorities applied."]
    }
