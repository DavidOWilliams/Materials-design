from material_core.wp4_feedback import run

def test_second_capability_runs_full_feedback_loop():
    result=run(elements=256,budget=3,layer=.01,feed=.25,
        route="synthetic_ideal_uniform_batch_deposition")
    assert result["process"]["route"]=="synthetic_ideal_uniform_batch_deposition"
    assert result["transformer_identity"]["transformer"]=="wp4-ideal-uniform-batch"
    assert result["records"][0]["feedback"] is not None
    assert result["records"][0]["balances"]["amount_unit"]=="m3/m2"
    assert result["records"][0]["estimated_inputs"]["evaluation_target"]=="estimated"
