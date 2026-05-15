from src.coating_vs_gradient_diagnostics import (
    DEFAULT_COATING_OPTIONS,
    build_coating_vs_gradient_diagnostic,
    get_coating_option,
    get_coating_options,
    match_coating_options,
    validate_coating_option,
    validate_default_coating_options,
)


def test_validate_default_coating_options_returns_no_errors():
    assert validate_default_coating_options() == []


def test_get_coating_options_returns_exactly_five_options():
    assert len(get_coating_options()) == 5


def test_returned_coating_options_cannot_mutate_default_coating_options():
    options = get_coating_options()

    options[0]["known_risks"].append("caller mutation")

    assert "caller mutation" not in DEFAULT_COATING_OPTIONS[0]["known_risks"]


def test_get_coating_option_returns_thermal_barrier_coating():
    option = get_coating_option("thermal_barrier_coating")

    assert option is not None
    assert option["option_id"] == "thermal_barrier_coating"


def test_get_coating_option_normalises_spaces_and_hyphens():
    option = get_coating_option("Thermal-Barrier Coating")

    assert option is not None
    assert option["option_id"] == "thermal_barrier_coating"


def test_get_coating_option_returns_none_for_unknown_id():
    assert get_coating_option("unknown_coating") is None


def test_validate_coating_option_rejects_missing_required_field():
    option = get_coating_option("thermal_barrier_coating")
    assert option is not None
    del option["option_name"]

    errors = validate_coating_option(option)

    assert "option_name is required" in errors


def test_validate_coating_option_rejects_non_list_activation_failure_modes():
    option = get_coating_option("thermal_barrier_coating")
    assert option is not None
    option["activation_failure_modes"] = "thermal_barrier"

    errors = validate_coating_option(option)

    assert "activation_failure_modes must be a list" in errors


def test_validate_coating_option_rejects_invalid_evidence_maturity_default():
    option = get_coating_option("thermal_barrier_coating")
    assert option is not None
    option["evidence_maturity_default"] = "approved"

    errors = validate_coating_option(option)

    assert any("evidence_maturity_default" in error for error in errors)


def test_match_coating_options_returns_oxidation_protection_for_hot_corrosion():
    matches = match_coating_options(
        ["hot_corrosion"],
        candidate_class="metallic",
        substrate_family="refractory_alloy",
    )

    assert [option["option_id"] for option in matches] == ["oxidation_protection_coating"]


def test_match_coating_options_filters_by_candidate_class():
    matches = match_coating_options(
        ["hot_corrosion"],
        candidate_class="ceramic",
        substrate_family="refractory_alloy",
    )

    assert matches == []


def test_match_coating_options_filters_by_substrate_family():
    matches = match_coating_options(
        ["hot_corrosion"],
        candidate_class="metallic",
        substrate_family="sic_sic_cmc",
    )

    assert matches == []


def test_build_diagnostic_returns_no_surface_driver_found_for_empty_limiting_factors():
    diagnostic = build_coating_vs_gradient_diagnostic([])

    assert diagnostic["comparison_status"] == "no_surface_driver_found"
    assert diagnostic["coating_option_count"] == 0
    assert diagnostic["gradient_template_count"] == 0


def test_build_diagnostic_returns_coating_options_only_when_no_gradient_matches():
    diagnostic = build_coating_vs_gradient_diagnostic(
        ["recession"],
        candidate_class="cmc",
        substrate_family="cmc",
        research_mode_enabled=False,
    )

    assert diagnostic["comparison_status"] == "coating_options_only"
    assert [option["option_id"] for option in diagnostic["coating_options_considered"]] == [
        "environmental_barrier_coating"
    ]
    assert diagnostic["gradient_templates_considered"] == []


def test_build_diagnostic_returns_coating_and_gradient_options_for_oxidation():
    diagnostic = build_coating_vs_gradient_diagnostic(
        ["oxidation"],
        candidate_class="metallic",
        substrate_family="nickel_alloy",
        process_routes=["DED"],
        research_mode_enabled=False,
    )

    assert diagnostic["comparison_status"] == "coating_and_gradient_options_available"
    assert [option["option_id"] for option in diagnostic["coating_options_considered"]] == [
        "oxidation_protection_coating"
    ]
    assert [template["template_id"] for template in diagnostic["gradient_templates_considered"]] == [
        "surface_oxidation_gradient"
    ]


def test_build_diagnostic_excludes_research_mode_required_gradient_when_disabled():
    diagnostic = build_coating_vs_gradient_diagnostic(
        ["thermal_barrier"],
        candidate_class="metallic",
        substrate_family="nickel_alloy",
        process_routes=["DED"],
        research_mode_enabled=False,
    )

    assert diagnostic["comparison_status"] == "coating_options_only"
    assert diagnostic["gradient_templates_considered"] == []


def test_build_diagnostic_includes_research_mode_required_gradient_when_enabled():
    diagnostic = build_coating_vs_gradient_diagnostic(
        ["thermal_barrier"],
        candidate_class="metallic",
        substrate_family="nickel_alloy",
        process_routes=["DED"],
        research_mode_enabled=True,
    )

    assert diagnostic["comparison_status"] == "coating_and_gradient_options_available"
    assert [template["template_id"] for template in diagnostic["gradient_templates_considered"]] == [
        "thermal_barrier_gradient"
    ]


def test_build_diagnostic_notes_say_it_does_not_select_winner():
    diagnostic = build_coating_vs_gradient_diagnostic(["oxidation"])

    assert any("winner" in note.lower() and "selected" in note.lower() for note in diagnostic["notes"])


def test_build_diagnostic_warns_for_coating_options_and_gradient_templates():
    diagnostic = build_coating_vs_gradient_diagnostic(
        ["oxidation"],
        candidate_class="metallic",
        substrate_family="nickel_alloy",
        process_routes=["DED"],
        research_mode_enabled=False,
    )

    assert any("Gradient alternatives require" in warning for warning in diagnostic["warnings"])
    assert any("Coating options require" in warning for warning in diagnostic["warnings"])


def test_build_diagnostic_does_not_mutate_limiting_factor_or_process_route_inputs():
    limiting_factors = ["oxidation"]
    process_routes = ["DED"]

    build_coating_vs_gradient_diagnostic(
        limiting_factors,
        candidate_class="metallic",
        substrate_family="nickel_alloy",
        process_routes=process_routes,
    )

    assert limiting_factors == ["oxidation"]
    assert process_routes == ["DED"]
