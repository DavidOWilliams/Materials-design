import json
import pytest
from material_core.wp4_feedback import run,save,_digest,reopen
from material_core.wp4_export import export

def test_export_labels_estimate_and_excludes_measurement(tmp_path):
    p=tmp_path/"evidence.json"
    save(p,run(elements=256,budget=2))
    result=export(p)
    assert result["evaluation_target"]=="estimated"
    assert result["measured_evidence"] is None
    assert result["manufacturing_validation"]=="not_established"
    assert "sintering" in result["unsupported_physics"]

def test_fabricated_measured_record_rejected_even_if_resealed(tmp_path):
    p=tmp_path/"fabricated.json"
    record=run(elements=256,budget=2)
    record["measured_evidence"]={"source":"invented"}
    p.write_text(json.dumps(dict(record=record,record_sha256=_digest(record))))
    with pytest.raises(ValueError,match="measured evidence"):
        reopen(p)
