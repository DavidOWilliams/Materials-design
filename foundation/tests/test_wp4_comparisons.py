from material_core.wp4_comparisons import paired,sensitivity,PREREGISTERED

def test_paired_equal_declared_budget_and_same_initial_state():
    result=paired(elements=256,budget=4)
    assert result["common_budget"]==4
    assert result["feedback_on"]["records"][0]["intended_hash"]==result["feedback_off"]["records"][0]["intended_hash"]
    assert result["feedback_on"]["process"]==result["feedback_off"]["process"]
    assert result["unused_on"]>=0 and result["unused_off"]>=0

def test_fixed_grid_retains_all_cases():
    result=sensitivity(elements=256,budget=3)
    assert len(result["records"])==len(PREREGISTERED)
    assert [(r["layer_m"],r["feed_step"]) for r in result["records"]]==list(PREREGISTERED)
