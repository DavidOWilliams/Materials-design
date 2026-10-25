import json
import pytest
from material_core.wp4_feedback import run,save,reopen,_digest

@pytest.mark.parametrize("key,mutate",[
 ("summary",lambda d:d["records"][0].update(objectives={"areal_mass":0})),
 ("feedback",lambda d:d["records"][0].update(feedback=None)),
 ("feasibility",lambda d:d["records"][0].update(feasible=True)),
 ("counter",lambda d:d.update(evaluations=999)),
 ("stop",lambda d:d.update(stop_reason="unrecognized")),
 ("lineage",lambda d:d["records"][0].update(intended_hash="0"*64)),
])
def test_recomputed_checks_reject_resealed_forgery(tmp_path,key,mutate):
    dossier=run(elements=256,budget=3)
    mutate(dossier)
    path=tmp_path/"forged.json"
    path.write_text(json.dumps({"record":dossier,"record_sha256":_digest(dossier)}))
    with pytest.raises(ValueError):
        reopen(path)

def test_checksum_detects_accidental_corruption(tmp_path):
    p=tmp_path/"corrupt.json"
    save(p,run(elements=256,budget=2))
    d=json.loads(p.read_text())
    d["record"]["config"]["budget"]=999
    p.write_text(json.dumps(d))
    with pytest.raises(ValueError,match="checksum"):
        reopen(p)
