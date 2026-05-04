from __future__ import annotations

import csv
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from src.contracts import evidence_maturity_label
from src.material_system_schema import MaterialSystemCandidate


MATERIAL_SYSTEM_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "material_systems"

CERAMIC_REQUIRED_COLUMNS = {
    "reference_id",
    "material_name",
    "material_family",
    "system_architecture_type",
    "constituents",
    "process_route",
    "known_strengths",
    "known_watch_outs",
    "evidence_maturity",
    "source_reference",
    "applicability_guardrails",
}

CMC_REQUIRED_COLUMNS = {
    "reference_id",
    "system_name",
    "matrix",
    "fiber",
    "interphase",
    "environmental_barrier_coating",
    "process_route",
    "known_strengths",
    "known_watch_outs",
    "evidence_maturity",
    "source_reference",
    "applicability_guardrails",
}

COATING_REQUIRED_COLUMNS = {
    "reference_id",
    "coating_name",
    "coating_family",
    "substrate_family",
    "coating_role",
    "process_route",
    "known_strengths",
    "known_watch_outs",
    "evidence_maturity",
    "source_reference",
    "applicability_guardrails",
}

GRADED_AM_REQUIRED_COLUMNS = {
    "reference_id",
    "system_name",
    "substrate_family",
    "gradient_type",
    "spatial_direction",
    "zones",
    "composition_profile",
    "microstructure_profile",
    "process_route",
    "known_strengths",
    "known_watch_outs",
    "evidence_maturity",
    "source_reference",
    "applicability_guardrails",
}


def _resolve_csv_path(path_or_name: str | Path) -> Path:
    path = Path(path_or_name)
    if path.is_absolute() or path.exists():
        return path
    return MATERIAL_SYSTEM_DATA_DIR / path


def load_csv_records(
    path_or_name: str | Path,
    required_columns: set[str],
) -> list[dict[str, Any]]:
    """Load a curated material-system CSV and enforce its required columns."""
    path = _resolve_csv_path(path_or_name)
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        missing = sorted(required_columns - fieldnames)
        if missing:
            raise ValueError(f"{path.name} is missing required columns: {', '.join(missing)}")

        records: list[dict[str, Any]] = []
        for row in reader:
            records.append({key: (value.strip() if isinstance(value, str) else value) for key, value in row.items()})
    return records


def load_ceramic_references() -> list[dict[str, Any]]:
    return load_csv_records("ceramic_references.csv", CERAMIC_REQUIRED_COLUMNS)


def load_cmc_systems() -> list[dict[str, Any]]:
    return load_csv_records("cmc_systems.csv", CMC_REQUIRED_COLUMNS)


def load_coating_systems() -> list[dict[str, Any]]:
    return load_csv_records("coating_systems.csv", COATING_REQUIRED_COLUMNS)


def load_graded_am_systems() -> list[dict[str, Any]]:
    return load_csv_records("graded_am_systems.csv", GRADED_AM_REQUIRED_COLUMNS)


def load_all_material_system_reference_records() -> dict[str, list[dict[str, Any]]]:
    return {
        "ceramic_references": load_ceramic_references(),
        "cmc_systems": load_cmc_systems(),
        "coating_systems": load_coating_systems(),
        "graded_am_systems": load_graded_am_systems(),
    }


def _split_semicolon_list(value: Any) -> list[str]:
    text = str(value or "").strip()
    if not text:
        return []
    return [part.strip() for part in text.split(";") if part.strip()]


def _evidence(record: Mapping[str, Any], source_table: str) -> dict[str, Any]:
    maturity = str(record.get("evidence_maturity", "E") or "E").strip().upper()
    return {
        "maturity": maturity,
        "maturity_label": evidence_maturity_label(maturity),
        "summary": str(record.get("source_reference", "") or ""),
        "sources": [str(record.get("source_reference", "") or source_table)],
        "validation_gaps": _split_semicolon_list(record.get("known_watch_outs")),
        "assumptions": _split_semicolon_list(record.get("applicability_guardrails")),
    }


def reference_record_to_material_system_candidate(
    record: Mapping[str, Any],
    source_table: str,
) -> MaterialSystemCandidate:
    """Mechanically wrap one curated reference row in the MaterialSystemCandidate shape."""
    evidence = _evidence(record, source_table)
    maturity = evidence["maturity"]
    reference_id = str(record.get("reference_id", "") or "").strip()

    if source_table == "ceramic_references":
        name = str(record.get("material_name", reference_id) or reference_id)
        system_class = "monolithic_ceramic"
        base_family = str(record.get("material_family", "") or "")
        constituents = [
            {
                "name": str(record.get("constituents", name) or name),
                "role": "substrate",
                "material_family": base_family,
                "composition": {"description": str(record.get("constituents", "") or "")},
            }
        ]
        coating_system = None
        gradient_architecture = None
    elif source_table == "cmc_systems":
        name = str(record.get("system_name", reference_id) or reference_id)
        system_class = "ceramic_matrix_composite"
        base_family = "ceramic matrix composite"
        constituents = [
            {"name": str(record.get("matrix", "") or ""), "role": "matrix", "material_family": "ceramic"},
            {"name": str(record.get("fiber", "") or ""), "role": "fiber", "material_family": "ceramic"},
            {"name": str(record.get("interphase", "") or ""), "role": "interphase", "material_family": "ceramic"},
        ]
        coating_system = {
            "coating_type": str(record.get("environmental_barrier_coating", "") or ""),
            "layers": [],
            "substrate_compatibility": "CMC substrate",
            "deposition_routes": [str(record.get("process_route", "") or "")],
            "failure_modes": _split_semicolon_list(record.get("known_watch_outs")),
            "evidence": evidence,
        }
        gradient_architecture = None
    elif source_table == "coating_systems":
        name = str(record.get("coating_name", reference_id) or reference_id)
        system_class = "coating_enabled"
        base_family = str(record.get("substrate_family", "") or "")
        constituents = [
            {"name": base_family, "role": "substrate", "material_family": base_family},
            {
                "name": name,
                "role": "coating",
                "material_family": str(record.get("coating_family", "") or ""),
            },
        ]
        coating_system = {
            "coating_type": str(record.get("coating_family", "") or ""),
            "layers": [constituents[1]],
            "substrate_compatibility": base_family,
            "deposition_routes": [str(record.get("process_route", "") or "")],
            "failure_modes": _split_semicolon_list(record.get("known_watch_outs")),
            "evidence": evidence,
        }
        gradient_architecture = None
    elif source_table == "graded_am_systems":
        name = str(record.get("system_name", reference_id) or reference_id)
        system_class = "spatially_graded_am"
        base_family = str(record.get("substrate_family", "") or "")
        constituents = [{"name": base_family, "role": "substrate", "material_family": base_family}]
        coating_system = None
        gradient_architecture = {
            "gradient_types": [str(record.get("gradient_type", "") or "")],
            "composition_gradients": [
                {
                    "location": str(record.get("spatial_direction", "") or ""),
                    "from_value": str(record.get("zones", "") or ""),
                    "to_value": str(record.get("composition_profile", "") or ""),
                    "rationale": str(record.get("known_strengths", "") or ""),
                }
            ],
            "microstructure_gradients": [
                {
                    "location": str(record.get("spatial_direction", "") or ""),
                    "from_value": str(record.get("zones", "") or ""),
                    "to_value": str(record.get("microstructure_profile", "") or ""),
                    "rationale": str(record.get("known_strengths", "") or ""),
                }
            ],
            "manufacturing_route": str(record.get("process_route", "") or ""),
            "transition_risks": _split_semicolon_list(record.get("known_watch_outs")),
            "notes": str(record.get("applicability_guardrails", "") or ""),
        }
    else:
        raise ValueError(f"Unsupported material-system reference table: {source_table}")

    candidate: MaterialSystemCandidate = {
        "candidate_id": reference_id,
        "name": name,
        "system_class": system_class,
        "system_classes": [system_class],
        "summary": str(record.get("known_strengths", "") or ""),
        "base_material_family": base_family,
        "constituents": constituents,
        "coating_system": coating_system,
        "gradient_architecture": gradient_architecture,
        "processing_routes": [{"route_name": str(record.get("process_route", "") or "")}],
        "property_estimates": {},
        "factor_scores": [],
        "evidence": evidence,
        "evidence_maturity": maturity,
        "maturity_rationale": evidence_maturity_label(maturity),
        "generated_by_adapter": None,
        "research_generated": False,
        "assumptions": _split_semicolon_list(record.get("applicability_guardrails")),
        "risks": _split_semicolon_list(record.get("known_watch_outs")),
        "validation_plan": [],
        "provenance": {"source_table": source_table, "reference_id": reference_id},
    }
    return candidate
