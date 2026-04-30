from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from src.prompt_interpreter import interpret_prompt
from src.scope_planner import build_scope_plan

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load_templates() -> Dict[str, Any]:
    path = DATA_DIR / "application_templates.json"
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _legacy_weight_view(schema: Dict[str, Any]) -> Dict[str, float]:
    factor_importance = schema.get("soft_objectives", {}).get("factor_importance", {}) or {}
    failure = schema.get("failure_mode_priorities", {}) or {}
    lifecycle = schema.get("lifecycle_priorities", {}) or {}

    # Preserve the existing contract expected by score_candidates while making it
    # richer and schema-derived. These remain downstream weights, not survival gates.
    return {
        "creep_priority": max(float(factor_importance.get("creep", 0.25)), float(failure.get("creep", 0.0)) * 0.65),
        "toughness_priority": max(
            float(factor_importance.get("toughness", 0.20)),
            float(failure.get("fracture_toughness", 0.0)) * 0.65,
            float(failure.get("fatigue", 0.0)) * 0.30,
        ),
        "temperature_priority": float(factor_importance.get("temperature", 0.25)),
        "cost_priority": max(float(factor_importance.get("through_life_cost", 0.15)), float(lifecycle.get("through_life_cost", 0.0)) * 0.65),
        "sustainability_priority": max(float(factor_importance.get("sustainability", 0.15)), float(lifecycle.get("sustainability", 0.0)) * 0.65),
    }


def _merge_application_templates(requirements: Dict[str, Any], prompt: str) -> Dict[str, Any]:
    """Backward-compatible support for existing data/application_templates.json.

    Template hits can still lift legacy weights and notes, but the schema/scope planner
    remains the source of the richer requirement interpretation.
    """
    templates = _load_templates()
    if not templates:
        return requirements

    lower_prompt = (prompt or "").lower()
    updated = dict(requirements)
    weights = dict(updated.get("weights", {}))
    notes = list(updated.get("notes", []))

    for keyword, template in templates.items():
        if str(keyword).lower() in lower_prompt:
            for key in weights:
                weights[key] = max(float(weights.get(key, 0.0)), float(template.get(key, weights.get(key, 0.0))))
            notes.extend(template.get("notes", []))

    updated["weights"] = weights
    updated["notes"] = list(dict.fromkeys([note for note in notes if note]))
    return updated


def infer_requirements(application_prompt: str, operating_temperature: int, am_preferred: bool) -> Dict[str, Any]:
    """Return the legacy requirement dict plus the new requirement schema and scope plan.

    candidate_generation.py can continue to consume allowed_material_families, weights,
    operating_temperature, and am_preferred exactly as before. New downstream layers use
    requirement_schema and scope_plan for prompt-sensitive factor activation and reranking.
    """

    schema = interpret_prompt(application_prompt, operating_temperature, am_preferred)
    scope_plan = build_scope_plan(schema)

    weights = _legacy_weight_view(schema)
    notes = []
    notes.extend(schema.get("interpreter_trace", []))
    notes.extend(scope_plan.get("planner_trace", []))
    notes.extend(scope_plan.get("scope_warnings", []))
    if not notes:
        notes = ["Default engineering priorities applied."]

    requirements: Dict[str, Any] = {
        "application_prompt": application_prompt,
        "operating_temperature": int(operating_temperature),
        "am_preferred": bool(am_preferred),
        "allowed_material_families": list(scope_plan.get("allowed_families", [])),
        "weights": weights,
        "notes": list(dict.fromkeys(notes)),
        "requirement_schema": schema,
        "scope_plan": scope_plan,
        "active_factor_set": list(scope_plan.get("active_factor_set", [])),
        "active_factor_weights": dict(scope_plan.get("active_factor_weights", {})),
        "family_priors": dict(scope_plan.get("family_priors", {})),
    }

    # Keep these only as transparent retrieval hints. Do not force baseline changes by default.
    retrieval_hints = scope_plan.get("retrieval_hints", {}) or {}
    if retrieval_hints.get("forced_chemsys"):
        requirements["forced_chemsys"] = retrieval_hints["forced_chemsys"]

    return _merge_application_templates(requirements, application_prompt)
