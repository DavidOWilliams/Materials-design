from material_core.wp4_alternate import alternate_duty
def test_alternate_duty_through_common_transform():
    result=alternate_duty(elements=256)
    assert result["adapter"]=="wp3-alternate-duty-layered-provider-v1"
    assert result["original_design_hash"]!=result["estimated_input_hash"]
    assert result["balance"]["amount_unit"]=="m3/m2"
    assert set(result["objectives"])=={"areal_mass","thermal_transmission","tensile_thermal_mismatch"}
