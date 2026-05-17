from pathlib import Path

from src.decision_language import (
    TERM_GLOSSARY,
    display_value,
    glossary_rows,
    humanise_identifier,
    status_label,
    term_definition,
    tooltip_text,
    boolean_label,
    replace_display_values,
)


def test_humanise_identifier_converts_snake_case_into_readable_text():
    assert humanise_identifier("validation_needs_available") == "Validation needs available"
    assert humanise_identifier("on_frontier") == "On frontier"
    assert humanise_identifier(None) == "Not specified"


def test_status_label_maps_frontier_status():
    assert status_label("on_frontier") == "Not clearly dominated"


def test_status_label_maps_validation_needs_available():
    assert status_label("validation_needs_available") == "Evidence review actions available"


def test_unknown_status_falls_back_safely():
    assert status_label("new_internal_status") == "New internal status"


def test_term_definition_returns_glossary_entry_for_frontier():
    definition = term_definition("frontier")

    assert definition["term_id"] == "frontier"
    assert definition["label"] == "Trade-off boundary status"
    assert definition["short_definition"]
    assert definition["user_help"]


def test_tooltip_text_returns_non_empty_help_text_for_validation_burden():
    assert tooltip_text("validation_burden")


def test_boolean_label_maps_research_mode_enabled_false():
    assert boolean_label("research_mode_enabled", False) == "Research-only options hidden"


def test_boolean_label_maps_live_calls_enabled_false():
    assert boolean_label("live_calls_enabled", False) == "Live specialist-model calls disabled"


def test_display_value_does_not_return_raw_true_or_false_for_booleans():
    assert display_value("unknown_field", True) == "Yes"
    assert display_value("unknown_field", False) == "No"
    assert display_value("research_mode_exposure", True) != "True"
    assert display_value("research_mode_exposure", False) != "False"


def test_display_value_returns_not_specified_for_none():
    assert display_value("criterion_value", None) == "Not specified"


def test_glossary_rows_returns_table_display_rows():
    rows = glossary_rows(["frontier"])

    assert rows == [
        {
            "Term": "Trade-off boundary status",
            "Meaning": TERM_GLOSSARY["frontier"]["short_definition"],
            "Help": TERM_GLOSSARY["frontier"]["user_help"],
        }
    ]


def test_replace_display_values_does_not_mutate_original_record():
    record = {
        "frontier_status": "on_frontier",
        "research_mode_enabled": False,
        "untouched": "raw_value",
    }

    converted = replace_display_values(
        record, field_names=["frontier_status", "research_mode_enabled"]
    )

    assert record["frontier_status"] == "on_frontier"
    assert record["research_mode_enabled"] is False
    assert converted["frontier_status"] == "Not clearly dominated"
    assert converted["research_mode_enabled"] == "Research-only options hidden"
    assert converted["untouched"] == "raw_value"


def test_forward_compatible_terms_exist():
    assert term_definition("model_estimate")["label"] == "Model estimate"
    assert term_definition("measurement_record")["label"] == "Measurement record"
    assert term_definition("optimisation_objective")["label"] == "Optimisation objective"


def test_controlled_glossary_labels_do_not_expose_raw_snake_case():
    for definition in TERM_GLOSSARY.values():
        label = definition["label"]
        assert "_" not in label
        assert label
        assert label != definition["term_id"]


def test_decision_language_does_not_import_forbidden_modules():
    source = Path("src/decision_language.py").read_text(encoding="utf-8")

    forbidden_imports = [
        "import app",
        "from app",
        "import streamlit",
        "from streamlit",
        "import phase6_decision_cockpit_prototype",
        "from phase6_decision_cockpit_prototype",
        "import phase5_",
        "from phase5_",
        "import src.phase5_",
        "from src.phase5_",
    ]

    for forbidden_import in forbidden_imports:
        assert forbidden_import not in source
