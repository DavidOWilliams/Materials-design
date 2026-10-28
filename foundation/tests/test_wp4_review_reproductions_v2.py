"""Reviewer reproductions for strict WP4 validation and reusable recovery."""
import copy,json
import pytest
from material_core.wp4_feedback import run,save,reopen,_digest
from material_core.wp4_journal import initialize,resume,read_attempts,recover
from material_core.wp3_adapters import resolve_provider,ALTERNATE
from material_core.wp4_export import export

def reseal(path,record):
    path.write_text(json.dumps({"record":record,"record_sha256":_digest(record)}))
    return path

@pytest.mark.parametrize("mutation,match",[
    (lambda r:r.update(schema_version=999),"schema_version"),
    (lambda r:r.update(stop_reason="no_improvement_possible"),"no-improvement"),
    (lambda r:r["baseline_intended_evaluation"].update(input_hash="0"*64),"Baseline evaluation"),
    (lambda r:r["config"].update(elements=128),"mesh mismatch"),
    (lambda r:r["records"][0].update(intended_hash="0"*64),"design artifact"),
])
def test_r1_reviewer_reproductions(tmp_path,mutation,match):
    record=run(elements=256,budget=4)
    mutation(record)
    with pytest.raises(ValueError,match=match):
        reopen(reseal(tmp_path/"bad.json",record))

def test_r2_reject_missing_historical_events(tmp_path):
    path=tmp_path/"journal.jsonl"
    journal,base=initialize(path,elements=256,budget=4)
    def interrupt(rows):
        journal.checkpoint(rows)
        raise RuntimeError("stop")
    with pytest.raises(RuntimeError):
        run(elements=256,budget=4,base_inputs=base,checkpoint=interrupt,attempt_event=journal.event)
    sidecar=path.with_suffix(path.suffix+".attempts.jsonl")
    sidecar.unlink()
    with pytest.raises(ValueError,match="Missing durable attempt"):
        resume(path,elements=256,budget=4)

def test_r2_reject_tampered_counters(tmp_path):
    path=tmp_path/"journal.jsonl"
    journal,base=initialize(path,elements=256,budget=4)
    def interrupt(rows):
        journal.checkpoint(rows)
        raise RuntimeError("stop")
    with pytest.raises(RuntimeError):
        run(elements=256,budget=4,base_inputs=base,checkpoint=interrupt,attempt_event=journal.event)
    out=tmp_path/"resumed.json"
    record=resume(path,elements=256,budget=4,output=out)
    record["cumulative_evaluations"]=999
    with pytest.raises(ValueError,match="accounting"):
        reopen(reseal(tmp_path/"forged.json",record))
    record.pop("attempt_events")
    with pytest.raises(ValueError,match="missing durable"):
        reopen(reseal(tmp_path/"forged.json",record))

def test_r4_alternate_resume_preserves_duty_and_context(tmp_path):
    path=tmp_path/"alternate.jsonl"
    base=resolve_provider(ALTERNATE,17,"explore",256,31.).baseline()
    journal,base=initialize(path,elements=256,budget=4,base_inputs=base)
    def interrupt(rows):
        journal.checkpoint(rows)
        raise RuntimeError("stop")
    with pytest.raises(RuntimeError):
        run(elements=256,budget=4,base_inputs=base,checkpoint=interrupt,attempt_event=journal.event)
    result=resume(path,elements=256,budget=4,output=tmp_path/"alternate.json")
    assert result["baseline_intended_inputs"]["brief"]["duty"]==base.brief.duty
    assert result["baseline_intended_inputs"]["materials"]==base.model_dump(mode="json")["materials"]
    assert result["accounting"]["reused_candidates"]==1
    assert reopen(tmp_path/"alternate.json")["algorithm"]==result["algorithm"]

def test_r3_hash_changes_when_design_content_changes_but_id_same(tmp_path):
    first=run(elements=256,budget=1)
    save(tmp_path/"first.json",first)
    h1=export(tmp_path/"first.json")["intended_baseline_hash"]
    second=run(elements=256,budget=1)
    second["baseline_intended_inputs"]["design"]["architecture"]["knots"][0]["composition"]["fractions"][0]["fraction"]=.35
    second["baseline_intended_inputs"]["design"]["architecture"]["knots"][0]["composition"]["fractions"][1]["fraction"]=.65
    # Hash sensitivity is a contract property; mutated baseline is not an authentic dossier.
    from material_core.contracts import IntendedDesign
    original=IntendedDesign.model_validate_json(json.dumps(first["baseline_intended_inputs"]["design"]))
    changed=IntendedDesign.model_validate_json(json.dumps(second["baseline_intended_inputs"]["design"]))
    assert original.id==changed.id
    assert original.content_hash!=changed.content_hash
    assert h1==original.content_hash
