from src.schema_validator import assert_requirement_schema_v2, validate_requirement_schema_v2


def test_validate_requirement_schema_v2_accepts_minimal_prompt():
    result = validate_requirement_schema_v2(
        {
            "schema_version": "v2",
            "prompt_raw": "Select a material for a hot aviation seal.",
            "coating_allowed": True,
            "lifecycle": {"evidence_maturity_floor": "B"},
        }
    )

    assert result["valid"] is True
    assert result["errors"] == []


def test_validate_requirement_schema_v2_rejects_bad_shape():
    result = validate_requirement_schema_v2(
        {
            "prompt_raw": 42,
            "coating_allowed": "yes",
            "lifecycle": {"evidence_maturity_floor": "Z"},
        }
    )

    assert result["valid"] is False
    assert "prompt_raw must be a string when provided." in result["errors"]
    assert "coating_allowed must be a boolean or None when provided." in result["errors"]
    assert "lifecycle.evidence_maturity_floor must be one of A, B, C, D, E or F." in result["errors"]


def test_assert_requirement_schema_v2_raises_for_invalid_shape():
    try:
        assert_requirement_schema_v2({"component": "not a dict"})
    except ValueError as exc:
        assert "component must be a dictionary" in str(exc)
    else:
        raise AssertionError("Expected invalid RequirementSchemaV2 to raise ValueError")
