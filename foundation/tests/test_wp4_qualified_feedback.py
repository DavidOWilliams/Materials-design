from material_core.wp4_feedback import run,save,reopen,recompute

def test_high_resolution_binding_feedback_produces_qualified_scenario_feasible_revision(tmp_path):
    result=run(elements=4096,budget=4,mass_limit=31.,layer=.005,feed=.25)
    assert result["stop_reason"]=="qualified_scenario_feasible"
    assert len(result["records"])==3
    assert [row["numerical_quality"] for row in result["records"]]==["qualified"]*3
    assert [row["feasible"] for row in result["records"]]==[False,False,True]
    assert result["records"][0]["feedback"]["actual"]==37.5
    assert result["records"][1]["feedback"]["actual"]==32.5
    assert result["records"][2]["feedback"] is None
    assert result["records"][2]["intended_design"]["parent_hashes"]==[result["records"][1]["intended_hash"]]
    path=tmp_path/"qualified.json"
    save(path,result)
    assert reopen(path)["stop_reason"]=="qualified_scenario_feasible"
    assert recompute(path)["recomputed"]==3
