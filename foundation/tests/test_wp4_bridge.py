from material_core.wp3_adapters import resolve_provider,DEFAULT
from material_core.wp4_bridge import evaluate_estimated
from material_core.contracts import ProcessScenario,quantity,Provenance

def test_estimated_target_reaches_wp2():
    base=resolve_provider(DEFAULT,17,"explore",32,31).baseline()
    process=ProcessScenario(id="wp4-test",version=1,route="synthetic_ideal_planar_deposition",
        layer_resolution=quantity("length",base.brief.thickness.value/2),
        feed_fraction_resolution=0.25,status="assumed",
        provenance=Provenance(source_id="test",source_version="1",source_hash="0"*64,
            location="test fixture",reuse_terms="test only",
            evidence_kind="synthetic_scenario",conditions="ideal",extraction="test"),
        assumptions=(),excluded_mechanisms=("porosity","shrinkage"))
    inputs,result=evaluate_estimated(base,process)
    assert inputs.evaluation_target=="estimated"
    assert inputs.design.content_hash==base.design.content_hash
    assert inputs.estimated_state.geometry is not None
    assert result.input_hash==inputs.content_hash
    assert result.comparison_context_hash is not None
    assert result.evidence_status=="synthetic"
