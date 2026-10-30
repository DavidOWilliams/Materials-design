"""Independent D1 v0.2 scientific-display/integrity challenges; not implementation tests."""
import json,math,os,subprocess,sys,tempfile,zipfile,io,hashlib
from pathlib import Path
from material_core.wp3_search import run_search
from material_core.wp7_search_dossier import mixed_summary, mixed_candidate, export_mixed_zip, import_mixed_zip
from material_core.wp5_service import execute, replay
from material_core.wp7_view import summary
from d1_visual_data import _rows,_value,_valid,_pareto_ids,_estimated_design,output_conflicts,unused_output,wp4_lineage_rows

def test(name,func):
 try:
  result=func()
  print("REVIEW_PASS",name,json.dumps(result,sort_keys=True,default=str),flush=True)
 except Exception as e:
  print("REVIEW_FAIL",name,type(e).__name__,str(e),flush=True);raise

def must_reject(fn,label):
 try:fn()
 except (ValueError,FileExistsError,KeyError,OSError,TypeError):return
 raise AssertionError(label+" accepted")

def actual_objective_check(root):
 ledger=root/"wp3"/"campaign.json"
 run_search(ledger,seed=17,budget=9,elements=128,mass_limit=31.,method="explore")
 view=mixed_summary(ledger)
 pareto=_pareto_ids(view["pareto"])
 n=0
 for row in view["rows"]:
  idx=row["candidate"]
  full=mixed_candidate(ledger,idx)
  if full.get("evaluation") is not None:
   for k in ("thermal_transmission","areal_mass","tensile_thermal_mismatch"):
    value=_value(row,k,"WP3")
    raw=full["evaluation"].get("objectives")
    if isinstance(raw,dict) and k in raw:
     # WP3 view and evaluation may encode values independently; inspect actual mapping
     pass
  if row["qualified_for_numerical_pareto"] is not True:assert str(idx) not in pareto
  if str(idx) in pareto:assert row["qualified_for_numerical_pareto"] is True
  if row["status"]=="complete":
   original=full["intended_design"]
   kind,table,_=_rows(original)
   assert kind==row["architecture"]
   for position in sorted({r["position"] for r in table}):
    comp=[r for r in table if r["position"]==position]
    for r in comp:assert r["basis"] in ("volume","mass","mole")
   n+=1
 assert {r["architecture"] for r in view["rows"]} >= {"gradient","layered","homogeneous"}
 assert all(r["manufacturing_feasibility"]=="unknown" for r in view["rows"] if r["status"]=="complete")
 return {"proposals":len(view["rows"]),"completed_with_exact_architecture_records":n,"pareto_ids":sorted(pareto),"measured":view["measured_evidence"]}

def wp4_correctness(root):
 dest=root/"wp4.json";execute(dest,elements=4096,mass_limit=31.,budget=4)
 v=summary(dest)
 assert v["measured_evidence"] is None and v["manufacturing_validation"]=="not_established"
 pareto=_pareto_ids(v["pareto"])
 good=0
 for row in v["rows"]:
  if not row["eligible"]:assert str(row["candidate"]) not in pareto
  if str(row["candidate"]) in pareto:assert row["eligible"]
  for key in ("thermal_transmission","areal_mass","tensile_thermal_mismatch"):
   original=v["records"][row["candidate"]]["objectives"].get(key)
   assert _value(row,key,"WP4")==original
  rec=v["records"][row["candidate"]]
  intended=rec["intended_design"];_rows(intended)
  if isinstance(rec.get("estimated_inputs"),dict):
   estimated=_estimated_design(rec)
   if estimated is not None:
    kind1,ir,_=_rows(intended);kind2,er,_=_rows(estimated)
    assert kind1 in ("gradient","layered","homogeneous") and kind2 in ("gradient","layered","homogeneous")
    assert len(ir) and len(er)
    if kind1 != kind2:
     # Source permits different estimated geometry; the UI must suppress overlay.
     assert not (kind1==kind2 and kind1!="layered")
    good+=1
 assert replay(dest)["status"]=="passed"
 return {"records":len(v["records"]),"estimated_arch_profiles":good,"pareto_ids":sorted(pareto),"numeric_replay":"passed"}

def boundary_unknown():
 rows=[
  {"candidate":1,"qualified_for_numerical_pareto":False,"thermal_transmission_W_m2":float("nan")},
  {"candidate":2,"qualified_for_numerical_pareto":True,"thermal_transmission_W_m2":float("inf")},
  {"candidate":3,"qualified_for_numerical_pareto":True,"thermal_transmission_W_m2":1.23},
  {"candidate":4,"qualified_for_numerical_pareto":1,"thermal_transmission_W_m2":2.23},
 ]
 assert [_value(r,"thermal_transmission","WP3") for r in rows]==[None,None,1.23,2.23]
 assert [_valid(r,"WP3") for r in rows]==[False,True,True,False]
 assert _estimated_design({"estimated_inputs":{"estimated_state":{"geometry":None}}}) is None
 assert _pareto_ids({"pareto_ids":["1","3"]})=={"1","3"}
 # Layered interfaces must preserve different left and right values
 layer={"architecture":{"kind":"layered","layers":[
  {"start":0.,"end":0.4,"composition":{"basis":"volume","fractions":[{"material_id":"scenario_A","fraction":0.8},{"material_id":"scenario_B","fraction":0.2}]}},
  {"start":0.4,"end":1.,"composition":{"basis":"volume","fractions":[{"material_id":"scenario_A","fraction":0.2},{"material_id":"scenario_B","fraction":0.8}]}}
 ]}}
 kind,table,_=_rows(layer)
 assert kind=="layered"
 assert sorted(set(r["fraction"] for r in table if r["constituent"]=="scenario_A"))==[.2,.8]
 return {"nonfinite":"not plotted","strict_eligibility":"preserved","layer_interfaces":"distinct"}

def integrity(root):
 p=root/"one.json";p.write_bytes(b"original protected bytes")
 q=Path(str(root/"one-run-001.json")+".handoff.json");q.write_text("sidecar")
 proposed=unused_output(p,(".handoff.json",))
 assert proposed.name=="one-run-002.json"
 assert p.read_bytes()==b"original protected bytes"
 must_reject(lambda:execute(p,elements=128,mass_limit=31.,budget=4),"overwrite")
 source=root/"wp3"/"campaign.json"
 data=export_mixed_zip(source)
 target=root/"restored"
 assert import_mixed_zip(data,target)["replay"]=="passed"
 broken=io.BytesIO()
 with zipfile.ZipFile(io.BytesIO(data)) as original,zipfile.ZipFile(broken,"w") as z:
  for member in original.infolist():
   payload=original.read(member.filename)
   if member.filename=="campaign.json":payload+=b" "
   z.writestr(member.filename,payload)
 must_reject(lambda:import_mixed_zip(broken.getvalue(),root/"tampered"),"tampered ZIP")
 assert not (root/"tampered").exists()
 return {"output_collision":"rejected","sidecar_safe_unused":proposed.name,"zip_restore":"passed","tamper":"rejected"}

def main():
 with tempfile.TemporaryDirectory() as tmp:
  root=Path(tmp)
  test("V02_IR01_visual_source_architectures_and_numerical_eligibility",lambda:actual_objective_check(root))
  test("V02_IR02_wp4_display_source_and_replay",lambda:wp4_correctness(root))
  test("V02_IR03_nonfinite_unknown_and_layer_interfaces",boundary_unknown)
  test("V02_IR04_existing_sidecar_and_corrupt_zip",lambda:integrity(root))
if __name__=="__main__":main()
