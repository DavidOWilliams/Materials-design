"""User-facing terminology and display semantics for decision views."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any


TERM_GLOSSARY: dict[str, dict[str, str]] = {
    "frontier": {
        "term_id": "frontier",
        "label": "Trade-off boundary status",
        "short_definition": "Indicates whether an option is clearly outperformed by comparable alternatives.",
        "user_help": "Use this to distinguish options that remain plausible on the trade-off boundary from options that are lower priority under the current evidence.",
    },
    "validation_needs": {
        "term_id": "validation_needs",
        "label": "Evidence still needed",
        "short_definition": "Evidence actions needed before a decision can rely on the option.",
        "user_help": "These are the remaining checks, tests, reviews, or confirmations that would improve confidence in the recommendation.",
    },
    "validation_burden": {
        "term_id": "validation_burden",
        "label": "Evidence and review effort",
        "short_definition": "The expected effort required to close evidence gaps for an option.",
        "user_help": "A higher burden means the option may need more testing, specialist review, traceability, or manufacturing confirmation before adoption.",
    },
    "evidence_maturity": {
        "term_id": "evidence_maturity",
        "label": "Evidence maturity",
        "short_definition": "How established and decision-ready the supporting evidence is.",
        "user_help": "This separates mature reference evidence from exploratory assumptions, early estimates, or research-only signals.",
    },
    "recommendation_tier": {
        "term_id": "recommendation_tier",
        "label": "Recommendation category",
        "short_definition": "The decision-facing category assigned to an option.",
        "user_help": "Use this to compare mature reference options, promising options needing evidence, exploratory options, and options parked for now.",
    },
    "research_mode": {
        "term_id": "research_mode",
        "label": "Research-only mode",
        "short_definition": "A mode that may surface exploratory options or assumptions not ready for direct engineering adoption.",
        "user_help": "Research-only mode can broaden exploration, but its outputs should be treated as hypotheses until evidence gates are satisfied.",
    },
    "criterion_value": {
        "term_id": "criterion_value",
        "label": "Estimated criterion value",
        "short_definition": "A value used to compare an option against a decision criterion.",
        "user_help": "This may come from measured evidence, literature, rules, deterministic calculations, or model-supported estimates depending on provenance.",
    },
    "confidence": {
        "term_id": "confidence",
        "label": "Decision confidence",
        "short_definition": "How strongly the available evidence supports using a value, status, or recommendation.",
        "user_help": "Confidence should be interpreted alongside uncertainty, provenance, and any remaining evidence gaps.",
    },
    "uncertainty": {
        "term_id": "uncertainty",
        "label": "Uncertainty",
        "short_definition": "The expected spread, ambiguity, or incompleteness around a value or conclusion.",
        "user_help": "Uncertainty can come from sparse evidence, model limitations, process variation, measurement noise, or missing context.",
    },
    "model_supported_estimate": {
        "term_id": "model_supported_estimate",
        "label": "Model-supported estimate",
        "short_definition": "An estimate informed by a computational model or specialist adapter.",
        "user_help": "Treat this as model-informed evidence, not as a direct measurement, and review the model provenance before relying on it.",
    },
    "model_provenance": {
        "term_id": "model_provenance",
        "label": "Model provenance",
        "short_definition": "Information describing where a model-supported result came from.",
        "user_help": "Provenance may include the adapter, model version, assumptions, input data, and whether live calls or cached results were used.",
    },
    "optimisation_iteration": {
        "term_id": "optimisation_iteration",
        "label": "Optimisation step",
        "short_definition": "One step in a sequence of option refinement or trade-off search.",
        "user_help": "Use this to understand how an option changed during optimisation and which objective or constraint drove the change.",
    },
    "refinement": {
        "term_id": "refinement",
        "label": "Design refinement",
        "short_definition": "A change proposed to improve an option against objectives or constraints.",
        "user_help": "Refinements should be reviewed for intended improvements, introduced risks, and evidence needed before adoption.",
    },
    "measurement_feedback": {
        "term_id": "measurement_feedback",
        "label": "Measurement feedback",
        "short_definition": "Measured results returned to improve estimates, confidence, or future optimisation.",
        "user_help": "Measurement feedback helps update the decision record and can reduce uncertainty or reveal new constraints.",
    },
    "evidence_gap": {
        "term_id": "evidence_gap",
        "label": "Evidence gap",
        "short_definition": "A missing or weak evidence item that limits decision confidence.",
        "user_help": "Evidence gaps identify what must be measured, reviewed, or justified before the option can be treated as decision-ready.",
    },
    "validation_roadmap": {
        "term_id": "validation_roadmap",
        "label": "Evidence review roadmap",
        "short_definition": "A structured set of actions for closing evidence gaps.",
        "user_help": "Use the roadmap to plan tests, reviews, measurements, and specialist checks in an engineering sequence.",
    },
    "process_window": {
        "term_id": "process_window",
        "label": "Manufacturing process window",
        "short_definition": "The acceptable range of processing conditions for a material system.",
        "user_help": "A narrow or uncertain process window can increase manufacturing risk even when predicted material properties look attractive.",
    },
    "simulation_result": {
        "term_id": "simulation_result",
        "label": "Simulation result",
        "short_definition": "A result produced by a computational simulation.",
        "user_help": "Review the simulation setup, assumptions, boundary conditions, and validation evidence before using the result in a decision.",
    },
    "surrogate_model": {
        "term_id": "surrogate_model",
        "label": "Surrogate model",
        "short_definition": "A faster approximation model used in place of a more expensive calculation or experiment.",
        "user_help": "Surrogate model outputs are useful for exploration but should be checked against their training range and validation evidence.",
    },
    "property_prediction": {
        "term_id": "property_prediction",
        "label": "Property prediction",
        "short_definition": "A predicted material or system property value.",
        "user_help": "Property predictions should show provenance, uncertainty, and whether they are measured, calculated, or model-supported.",
    },
    "uncertainty_driver": {
        "term_id": "uncertainty_driver",
        "label": "Uncertainty driver",
        "short_definition": "A factor that contributes materially to uncertainty.",
        "user_help": "Examples include limited data, process variability, extrapolation beyond evidence, measurement noise, or model assumptions.",
    },
    "confidence_band": {
        "term_id": "confidence_band",
        "label": "Confidence band",
        "short_definition": "A displayed range communicating likely variation around an estimate.",
        "user_help": "A confidence band helps compare estimates without implying more precision than the evidence supports.",
    },
    "model_estimate": {
        "term_id": "model_estimate",
        "label": "Model estimate",
        "short_definition": "A value estimated by a computational model.",
        "user_help": "Use model estimates with their provenance, assumptions, uncertainty, and any available measurement feedback.",
    },
    "model_adapter": {
        "term_id": "model_adapter",
        "label": "Model adapter",
        "short_definition": "The integration layer that connects the assistant to a specialist model.",
        "user_help": "The adapter can affect available inputs, outputs, assumptions, provenance, and whether results are live or cached.",
    },
    "measurement_record": {
        "term_id": "measurement_record",
        "label": "Measurement record",
        "short_definition": "A structured record of a measured result and its context.",
        "user_help": "Measurement records should preserve the target, method, value, units, conditions, and source needed for later review.",
    },
    "measurement_target": {
        "term_id": "measurement_target",
        "label": "Measurement target",
        "short_definition": "The property, criterion, or risk item selected for measurement.",
        "user_help": "Measurement targets should be chosen to reduce important uncertainty or close a decision-critical evidence gap.",
    },
    "active_learning_suggestion": {
        "term_id": "active_learning_suggestion",
        "label": "Suggested next measurement",
        "short_definition": "A suggested measurement or calculation intended to improve the model or decision.",
        "user_help": "Active learning suggestions should explain which uncertainty, objective, or constraint they are expected to improve.",
    },
    "optimisation_objective": {
        "term_id": "optimisation_objective",
        "label": "Optimisation objective",
        "short_definition": "The target that an optimisation step is trying to improve.",
        "user_help": "Objectives should be interpreted alongside constraints, trade-offs, and any risks introduced by the proposed change.",
    },
    "constraint": {
        "term_id": "constraint",
        "label": "Engineering constraint",
        "short_definition": "A requirement or boundary condition that an option should satisfy.",
        "user_help": "Constraints can represent operating limits, manufacturing limits, safety limits, compatibility needs, or evidence requirements.",
    },
    "introduced_risk": {
        "term_id": "introduced_risk",
        "label": "Introduced risk",
        "short_definition": "A new or increased risk created by a proposed option or refinement.",
        "user_help": "Introduced risks should be reviewed before accepting a refinement, even when the refinement improves an objective.",
    },
    "before_after_delta": {
        "term_id": "before_after_delta",
        "label": "Before-and-after change",
        "short_definition": "The difference between a value before and after a refinement or update.",
        "user_help": "Use this to understand the practical effect of an optimisation step, evidence update, or measurement feedback.",
    },
}


STATUS_LABELS: dict[str, str] = {
    "on_frontier": "Not clearly dominated",
    "dominated": "Lower-priority trade-off option",
    "insufficient_basis": "Not enough comparable evidence",
    "validation_needs_available": "Evidence review actions available",
    "no_validation_needs_identified": "No additional evidence actions identified",
    "research_mode_validation_required": "Research-only evidence gate required",
    "mature_reference_option": "Mature reference option",
    "validation_needed_option": "Promising option needing evidence",
    "exploratory_option": "Exploratory option",
    "research_only_suggestion": "Research-only suggestion",
    "parked_not_preferred": "Parked for now",
    "tradeoff_vector_available": "Trade-off evidence available",
    "research_mode_vector_available": "Research-only trade-off evidence",
    "no_traces_available": "No optimisation trace available",
}


BOOLEAN_LABELS_BY_FIELD: dict[str, dict[bool, str]] = {
    "research_mode_enabled": {
        True: "Research-only options visible",
        False: "Research-only options hidden",
    },
    "research_mode_exposure": {
        True: "Includes research-only assumptions",
        False: "No research-mode exposure",
    },
    "live_calls_enabled": {
        True: "Live specialist-model calls enabled",
        False: "Live specialist-model calls disabled",
    },
    "generated_candidates_allowed": {
        True: "Generated candidates allowed in research mode",
        False: "Generated candidates blocked",
    },
    "mature_evidence_allowed": {
        True: "Mature evidence claims allowed",
        False: "Mature evidence claims blocked",
    },
    "follow_up_required": {
        True: "Follow-up required",
        False: "No follow-up currently required",
    },
    "registry_safe": {
        True: "Registry guardrails active",
        False: "Registry guardrails not confirmed",
    },
}

_DEFAULT_BOOLEAN_LABELS = {
    True: "Yes",
    False: "No",
}


def humanise_identifier(value: object) -> str:
    """Convert an internal identifier into readable display text."""
    if value is None:
        return "Not specified"

    text = str(value).strip()
    if not text:
        return "Not specified"

    text = text.replace("_", " ").replace("-", " ")
    words = " ".join(text.split())
    if not words:
        return "Not specified"

    return words[:1].upper() + words[1:]


def status_label(value: object) -> str:
    """Return a controlled status label, with a safe readable fallback."""
    key = str(value) if value is not None else None
    if key in STATUS_LABELS:
        return STATUS_LABELS[key]
    return humanise_identifier(value)


def term_label(term_id: str) -> str:
    """Return the controlled label for a term."""
    definition = TERM_GLOSSARY.get(term_id)
    if definition is not None:
        return definition["label"]
    return humanise_identifier(term_id)


def term_definition(term_id: str) -> dict[str, str]:
    """Return a glossary record for a term."""
    definition = TERM_GLOSSARY.get(term_id)
    if definition is not None:
        return dict(definition)

    return {
        "term_id": term_id,
        "label": humanise_identifier(term_id),
        "short_definition": "No controlled definition is available yet.",
        "user_help": "This term has not yet been added to the controlled glossary.",
    }


def tooltip_text(term_id: str) -> str:
    """Return user help text for a term."""
    return term_definition(term_id)["user_help"]


def boolean_label(field_name: str, value: object) -> str:
    """Return a context-specific display label for a boolean value."""
    if not isinstance(value, bool):
        return humanise_identifier(value)

    field_labels = BOOLEAN_LABELS_BY_FIELD.get(field_name, _DEFAULT_BOOLEAN_LABELS)
    return field_labels[value]


def display_value(field_name: str, value: object) -> str:
    """Return a user-facing display value for a field value."""
    if isinstance(value, bool):
        return boolean_label(field_name, value)
    if value is None:
        return "Not specified"
    if str(value) in STATUS_LABELS:
        return status_label(value)
    return humanise_identifier(value)


def glossary_rows(term_ids: list[str] | None = None) -> list[dict[str, str]]:
    """Return glossary rows suitable for table display."""
    selected_terms: Iterable[str]
    selected_terms = TERM_GLOSSARY.keys() if term_ids is None else term_ids

    rows = []
    for term_id in selected_terms:
        definition = term_definition(term_id)
        rows.append(
            {
                "Term": definition["label"],
                "Meaning": definition["short_definition"],
                "Help": definition["user_help"],
            }
        )
    return rows


def replace_display_values(
    record: Mapping[str, Any], *, field_names: list[str] | None = None
) -> dict[str, Any]:
    """Return a shallow copy with selected top-level values converted for display."""
    display_record = dict(record)
    selected_fields = display_record.keys() if field_names is None else field_names

    for field_name in selected_fields:
        if field_name in display_record:
            display_record[field_name] = display_value(field_name, display_record[field_name])

    return display_record
