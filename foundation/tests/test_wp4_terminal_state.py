import json
import pytest
from material_core.wp4_feedback import run,reopen,_digest

def test_resealed_false_terminal_reason_rejected(tmp_path):
    record=run(elements=256,budget=3)
    assert record["stop_reason"]!="qualified_scenario_feasible"
    record["stop_reason"]="qualified_scenario_feasible"
    p=tmp_path/"forged-stop.json"
    p.write_text(json.dumps({"record":record,"record_sha256":_digest(record)}))
    with pytest.raises(ValueError,match="False qualified"):
        reopen(p)
