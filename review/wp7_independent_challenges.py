"""Separately authored WP7 reviewer challenge probes. Not implementation tests."""
from __future__ import annotations
import hashlib, io, json, os, subprocess, sys, tempfile, zipfile
from pathlib import Path
from material_core.wp5_service import execute, inspect, replay, portable_import
from material_core.wp7_view import summary, selected_candidate
from material_core.wp3_search import run_search
from material_core.wp7_search_dossier import mixed_summary, export_mixed_zip, import_mixed_zip

def check(name, fn):
    try:
        data=fn()
        print("REVIEW_PASS",name,json.dumps(data,sort_keys=True,default=str),flush=True)
    except Exception as e:
        print("REVIEW_FAIL",name,repr(e),flush=True)
        raise

def main():
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp)
        def positive():
            p=root/"positive.json"; r=execute(p,elements=4096,mass_limit=31.,budget=4,feedback=True)
            v=summary(p)
            assert r["stop_reason"]=="qualified_scenario_feasible",r["stop_reason"]
            assert any(row["eligible"] for row in v["rows"]),v["rows"]
            assert len(v["directions"])==3
            assert all(row["pareto"] is False for row in v["rows"] if not row["eligible"])
            assert selected_candidate(p,0)["evaluation_hash"]
            assert v["measured_evidence"] is None and v["manufacturing_validation"]=="not_established"
            return {"stop":r["stop_reason"],"eligible":sum(x["eligible"] for x in v["rows"]),"pareto":v["pareto"]["pareto_ids"],"bytes_sha":hashlib.sha256(p.read_bytes()).hexdigest()}
        check("IR01_feasible_eligible_pareto",positive)
        def negative():
            p=root/"infeasible.json";r=execute(p,elements=4096,mass_limit=1.,budget=4)
            v=summary(p)
            assert not any(x["eligible"] for x in v["rows"])
            assert not v["pareto"]["pareto_ids"]
            assert all(x["reason"] for x in v["rows"])
            return {"stop":r["stop_reason"],"reasons":[x["reason"] for x in v["rows"]]}
        check("IR02_infeasible_with_reasons",negative)
        def boundary():
            outcomes={}
            for mass in (30.0,31.0,31.000001):
                p=root/f"mass-{mass}.json"
                r=execute(p,elements=4096,mass_limit=mass,budget=4,feedback=True)
                v=summary(p)
                outcomes[str(mass)]={"eligible":sum(x["eligible"] for x in v["rows"]),"stop":r["stop_reason"]}
                assert all(x["numerical_quality"] != "qualified" or isinstance(x["eligible"],bool) for x in v["rows"])
            return outcomes
        check("IR03_mass_boundary_sweep",boundary)
        def invalid():
            p=root/"invalid.json"
            try:execute(p,elements=4096,budget=0)
            except ValueError:pass
            else:raise AssertionError("zero budget accepted")
            assert not p.exists()
            try:execute(root/"positive.json",elements=4096,budget=4)
            except FileExistsError:pass
            else:raise AssertionError("overwrite accepted")
            try:summary(root/"missing.json")
            except (ValueError,FileNotFoundError,OSError,KeyError):pass
            else:raise AssertionError("missing dossier accepted")
            corrupted=json.loads((root/"positive.json").read_text())
            corrupted["record"]["config"]["mass_limit"]=999
            p=root/"corrupted.json";p.write_text(json.dumps(corrupted))
            try:summary(p)
            except (ValueError,KeyError):pass
            else:raise AssertionError("mutated dossier accepted")
            return {"zero_budget":"rejected","overwrite":"rejected","missing":"rejected","corruption":"rejected"}
        check("IR04_invalid_missing_corrupt",invalid)
        def replay_check():
            p=root/"positive.json";target=root/"copy.json"
            portable_import(p,target)
            assert target.read_bytes()==p.read_bytes()
            code="import json,sys;from material_core.wp5_service import replay;print(json.dumps(replay(sys.argv[1])))"
            env={**os.environ,"PYTHONPATH":str(Path("foundation").resolve())}
            result=subprocess.run([sys.executable,"-c",code,str(target)],env=env,capture_output=True,text=True,check=True)
            status=json.loads(result.stdout)
            assert status["status"]=="passed",status
            return {"status":status["status"],"recomputed":status.get("recomputed")}
        check("IR05_independent_process_replay",replay_check)
        def deterministic():
            p=root/"repeat.json";execute(p,elements=4096,mass_limit=31.,budget=4,feedback=True)
            assert p.read_bytes()==(root/"positive.json").read_bytes()
            return {"byte_equal":True}
        check("IR06_deterministic",deterministic)
        def mixed():
            ledger=root/"mixed"/"campaign.json"
            run_search(ledger,seed=17,budget=4,elements=4096,mass_limit=31.,method="explore")
            v=mixed_summary(ledger)
            architectures={r["architecture"] for r in v["rows"]}
            assert {"homogeneous","layered","gradient"} <= architectures
            assert all(r["manufacturing_feasibility"]=="unknown" for r in v["rows"] if r["status"]=="complete")
            bundle=export_mixed_zip(ledger)
            restored=root/"restored"
            output=import_mixed_zip(bundle,restored)
            assert output["replay"]=="passed"
            broken=io.BytesIO()
            with zipfile.ZipFile(io.BytesIO(bundle)) as z,zipfile.ZipFile(broken,"w") as out:
                for info in z.infolist():
                    raw=z.read(info.filename)
                    if info.filename=="campaign.json":raw+=b" "
                    out.writestr(info.filename,raw)
            dest=root/"tampered"
            try:import_mixed_zip(broken.getvalue(),dest)
            except (ValueError,KeyError):pass
            else:raise AssertionError("tampered ZIP accepted")
            assert not dest.exists()
            return {"architectures":sorted(architectures),"zip_sha":hashlib.sha256(bundle).hexdigest(),"tamper":"rejected","restored_replay":output["replay"]}
        check("IR07_mixed_arch_zip_integrity",mixed)
if __name__=="__main__":main()
