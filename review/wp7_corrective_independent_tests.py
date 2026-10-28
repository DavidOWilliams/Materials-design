"""Independent WP7 correction IR01/IR04 challenges against unchanged scientific kernels."""
import json,os,subprocess,sys,tempfile
from pathlib import Path
from material_core.wp3_search import run_search
from material_core.wp7_handoff import qualified_handoff_source,execute_handoff,verify_handoff,start_checkpointed_handoff,recover_checkpointed_handoff
from material_core.wp5_service import replay
from material_core.wp4_feedback import reopen

def test(name, fn):
 try:
  value=fn();print("INDEPENDENT_PASS",name,json.dumps(value,sort_keys=True,default=str),flush=True)
 except Exception as exc:
  print("INDEPENDENT_FAIL",name,type(exc).__name__,str(exc),flush=True);raise

def rejects(fn,label):
 try:fn()
 except (ValueError,FileExistsError,KeyError,TypeError,FileNotFoundError):return
 raise AssertionError(label+" silently accepted")

def check():
 with tempfile.TemporaryDirectory() as tmp:
  root=Path(tmp)
  ledger=root/"wp3"/"campaign.json"
  run_search(ledger,seed=17,budget=4,elements=128,mass_limit=31.)
  def unsupported():
   for idx in (0,1,2):
    rejects(lambda idx=idx:qualified_handoff_source(ledger,idx,elements=128,mass_limit=31.),"unsupported architecture")
   rejects(lambda:qualified_handoff_source(ledger,3,elements=256,mass_limit=31.),"different mesh")
   rejects(lambda:qualified_handoff_source(ledger,3,elements=128,mass_limit=30.),"different mass")
   rejects(lambda:qualified_handoff_source(ledger,99,elements=128,mass_limit=31.),"invalid index")
   mapped,provenance=qualified_handoff_source(ledger,3,elements=128,mass_limit=31.)
   assert provenance["source_design_hash"]==mapped.design.content_hash
   assert provenance["measured_evidence"] is None
   return {"rejected_homogeneous_and_layered":3,"mesh_and_mass":"rejected","source_hash":provenance["source_design_hash"],"source_numerically_qualified":provenance["source_numerically_qualified"]}
  test("IR01_exact_selection_and_rejection",unsupported)
  def transfer():
   target=root/"selected.json"
   data=execute_handoff(ledger,3,target,elements=128,mass_limit=31.,budget=4)
   provenance=verify_handoff(target)
   assert provenance["verified"] and provenance["measured_evidence"] is None
   original=reopen(target)
   assert original["baseline_intended_inputs"]["design"]["architecture"]["kind"]=="gradient"
   assert replay(target)["status"]=="passed"
   cmd='import json,sys;from material_core.wp7_handoff import verify_handoff;from material_core.wp5_service import replay;print(json.dumps([verify_handoff(sys.argv[1]),replay(sys.argv[1])]))'
   env={**os.environ,"PYTHONPATH":str(Path("foundation").resolve())}
   proc=subprocess.run([sys.executable,"-c",cmd,str(target)],capture_output=True,text=True,env=env,check=True)
   results=json.loads(proc.stdout)
   assert results[0]["verified"] and results[1]["status"]=="passed"
   return {"source_ledger_hash":provenance["handoff"]["source_ledger_sha256"],"source_evaluation_hash":provenance["handoff"]["source_evaluation_hash"],"wp4_baseline":provenance["handoff"]["wp4_recontextualised_baseline_hash"],"records":len(data["records"]),"separate_process":"passed"}
  test("IR01_handoff_recompute_and_lineage",transfer)
  def binding_cancel():
   low=root/"low"/"campaign.json";run_search(low,seed=17,budget=4,elements=128,mass_limit=1.)
   journal=root/"selected.journal.jsonl"
   outcome=start_checkpointed_handoff(low,3,journal,elements=128,mass_limit=1.,budget=4,cancel_after=1)
   assert outcome["stop_reason"]=="cancelled",outcome
   assert outcome["completed"]==1,outcome
   assert journal.exists()
   assert Path(str(journal)+".attempts.jsonl").exists()
   recovered=root/"recovered.json"
   done=recover_checkpointed_handoff(journal,recovered)
   assert len(done["records"])>=1
   assert verify_handoff(recovered)["verified"] is True
   assert replay(recovered)["status"]=="passed"
   rejects(lambda:recover_checkpointed_handoff(journal,recovered),"overwrite recovered")
   return {"stop_reason":outcome["stop_reason"],"checkpoint_count":outcome["completed"],"recovered_candidates":len(done["records"]),"replay":"passed"}
  test("IR04_binding_cancel_and_recover",binding_cancel)
  def anti_tamper():
   target=root/"selected.json"
   handoff=Path(str(target)+".handoff.json")
   data=json.loads(handoff.read_text());data["provenance"]["source_design_hash"]="0"*64;handoff.write_text(json.dumps(data))
   rejects(lambda:verify_handoff(target),"forged provenance")
   return {"tampered_companion":"rejected"}
  test("IR01_companion_tamper_rejected",anti_tamper)
if __name__=="__main__":check()
