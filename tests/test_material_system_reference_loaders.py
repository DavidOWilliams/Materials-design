from pathlib import Path

import pytest

from src.reference_data.material_system_loaders import (
    CERAMIC_REQUIRED_COLUMNS,
    load_all_material_system_reference_records,
    load_ceramic_references,
    load_cmc_systems,
    load_coating_systems,
    load_csv_records,
    load_graded_am_systems,
    reference_record_to_material_system_candidate,
)


def test_every_material_system_loader_returns_records():
    assert load_ceramic_references()
    assert load_cmc_systems()
    assert load_coating_systems()
    assert load_graded_am_systems()

    all_records = load_all_material_system_reference_records()
    assert set(all_records) == {
        "ceramic_references",
        "cmc_systems",
        "coating_systems",
        "graded_am_systems",
    }
    assert all(all_records[source_table] for source_table in all_records)


def test_required_columns_are_enforced(tmp_path: Path):
    csv_path = tmp_path / "bad_ceramic.csv"
    csv_path.write_text(
        "reference_id,material_name\nmissing_columns,Incomplete reference\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="missing required columns"):
        load_csv_records(csv_path, CERAMIC_REQUIRED_COLUMNS)


def test_sic_sic_cmc_with_ebc_anchor_is_present():
    cmc_systems = load_cmc_systems()

    assert any(
        record["reference_id"] == "sic_sic_cmc_ebc_anchor"
        and "SiC/SiC" in record["system_name"]
        and record["environmental_barrier_coating"]
        for record in cmc_systems
    )


def test_graded_am_records_have_conservative_maturity():
    graded_records = load_graded_am_systems()
    maturities = {record["evidence_maturity"] for record in graded_records}

    assert maturities & {"D", "E", "F"}
    assert "A" not in maturities


def test_coating_records_preserve_role_and_substrate_family():
    coating_records = load_coating_systems()

    assert all(record["coating_role"] for record in coating_records)
    assert all(record["substrate_family"] for record in coating_records)
    assert any(record["coating_role"] == "thermal insulation" for record in coating_records)


def test_reference_record_can_convert_to_material_system_candidate_dictionary():
    record = load_coating_systems()[0]

    candidate = reference_record_to_material_system_candidate(record, "coating_systems")

    assert candidate["candidate_id"] == record["reference_id"]
    assert candidate["system_class"] == "coating_enabled"
    assert candidate["evidence_maturity"] == record["evidence_maturity"]
    assert candidate["coating_system"]["coating_type"] == record["coating_family"]
    assert candidate["constituents"][0]["material_family"] == record["substrate_family"]
    assert candidate["research_generated"] is False
