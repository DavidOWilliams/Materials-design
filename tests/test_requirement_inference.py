from src.requirement_inference import infer_requirements

def test_infer_requirements_high_temp():
    result = infer_requirements("hot aviation creep component", 850, True)
    assert "Ni-based superalloy" in result["allowed_material_families"]
    assert result["weights"]["creep_priority"] >= 0.35
