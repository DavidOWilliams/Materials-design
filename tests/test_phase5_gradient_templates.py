from src.gradient_templates import (
    DEFAULT_GRADIENT_TEMPLATES,
    get_gradient_template,
    get_gradient_templates,
    match_gradient_templates,
    validate_default_gradient_templates,
    validate_gradient_template,
)


def test_validate_default_gradient_templates_returns_no_errors():
    assert validate_default_gradient_templates() == []


def test_get_gradient_templates_returns_exactly_five_templates():
    assert len(get_gradient_templates()) == 5


def test_returned_templates_cannot_mutate_default_gradient_templates():
    templates = get_gradient_templates()

    templates[0]["known_risks"].append("caller mutation")
    templates[0]["property_targets_by_zone"]["surface"].append("caller mutation")

    assert "caller mutation" not in DEFAULT_GRADIENT_TEMPLATES[0]["known_risks"]
    assert (
        "caller mutation"
        not in DEFAULT_GRADIENT_TEMPLATES[0]["property_targets_by_zone"]["surface"]
    )


def test_get_gradient_template_returns_surface_oxidation_gradient():
    template = get_gradient_template("surface_oxidation_gradient")

    assert template is not None
    assert template["template_id"] == "surface_oxidation_gradient"


def test_get_gradient_template_returns_none_for_unknown_id():
    assert get_gradient_template("unknown_gradient") is None


def test_validate_gradient_template_rejects_missing_required_field():
    template = get_gradient_template("surface_oxidation_gradient")
    assert template is not None
    del template["template_name"]

    errors = validate_gradient_template(template)

    assert "template_name is required" in errors


def test_validate_gradient_template_rejects_invalid_maturity_level():
    template = get_gradient_template("surface_oxidation_gradient")
    assert template is not None
    template["minimum_evidence_maturity_default"] = "qualified"

    errors = validate_gradient_template(template)

    assert any("minimum_evidence_maturity_default" in error for error in errors)


def test_validate_gradient_template_rejects_non_list_activation_failure_modes():
    template = get_gradient_template("surface_oxidation_gradient")
    assert template is not None
    template["activation_failure_modes"] = "oxidation"

    errors = validate_gradient_template(template)

    assert "activation_failure_modes must be a list" in errors


def test_match_gradient_templates_returns_surface_oxidation_gradient_for_oxidation():
    matches = match_gradient_templates(
        ["oxidation"],
        candidate_class="metallic",
        substrate_family="nickel_alloy",
        research_mode_enabled=False,
    )

    assert [template["template_id"] for template in matches] == ["surface_oxidation_gradient"]


def test_match_gradient_templates_excludes_thermal_barrier_gradient_without_research_mode():
    matches = match_gradient_templates(
        ["thermal_barrier"],
        candidate_class="metallic",
        substrate_family="nickel_alloy",
        process_routes=["DED"],
        research_mode_enabled=False,
    )

    assert "thermal_barrier_gradient" not in [template["template_id"] for template in matches]


def test_match_gradient_templates_includes_thermal_barrier_gradient_with_research_mode():
    matches = match_gradient_templates(
        ["thermal_barrier"],
        candidate_class="metallic",
        substrate_family="nickel_alloy",
        process_routes=["DED"],
        research_mode_enabled=True,
    )

    assert [template["template_id"] for template in matches] == ["thermal_barrier_gradient"]


def test_match_gradient_templates_returns_default_template_order():
    matches = match_gradient_templates(
        ["wear", "coating_spallation"],
        research_mode_enabled=True,
    )

    assert [template["template_id"] for template in matches] == [
        "surface_wear_gradient",
        "thermal_barrier_gradient",
        "tough_core_hard_surface",
        "metal_to_ceramic_transition",
    ]


def test_match_gradient_templates_normalises_spaces_and_hyphens():
    matches = match_gradient_templates(
        ["hot corrosion"],
        candidate_class="metallic",
        substrate_family="nickel-alloy",
        process_routes=["directed energy deposition"],
    )

    assert [template["template_id"] for template in matches] == ["surface_oxidation_gradient"]


def test_match_gradient_templates_filters_by_candidate_class():
    matches = match_gradient_templates(
        ["oxidation"],
        candidate_class="ceramic",
        substrate_family="nickel_alloy",
        research_mode_enabled=False,
    )

    assert matches == []


def test_match_gradient_templates_filters_by_process_routes():
    matches = match_gradient_templates(
        ["wear"],
        candidate_class="metallic",
        process_routes=["forging"],
        research_mode_enabled=False,
    )

    assert matches == []
