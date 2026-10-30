"""Independent chart-encoding review: compare chart data with actual source records."""
import json,tempfile
from pathlib import Path
from contextlib import nullcontext
from types import SimpleNamespace
from unittest.mock import patch
from material_core.wp3_search import run_search
from material_core.wp7_search_dossier import mixed_summary,mixed_candidate
from material_core.wp5_service import execute
from material_core.wp7_view import summary
from d1_visual_data import _rows, _value, _pareto_ids,_estimated_design
import d1_visuals

class Stub:
 def __init__(self):
  self.charts=[];self.messages=[]
 def altair_chart(self,chart,**kw):self.charts.append(chart)
 def selectbox(self,label,options,**kw):
  if label=="Horizontal objective":return "areal_mass"
  if label=="Vertical objective":return "thermal_transmission"
  return options[0]
 def expander(self,*a,**kw):return nullcontext()
 def info(self,v,*a,**kw):self.messages.append(str(v))
 def __getattr__(self,key):
  return lambda *args,**kwargs:None

def compare_campaign(view,scope):
 fake=Stub()
 with patch.object(d1_visuals,"st",fake):
  d1_visuals.campaign_view(view,scope=scope,key="audit")
 assert fake.charts
 chart=fake.charts[0]; plotted=chart.data.to_dict("records")
 pareto=_pareto_ids(view["pareto"])
 expected=[]
 for r in view["rows"]:
  a=_value(r,"areal_mass","WP4" if "WP4" in scope else "WP3")
  b=_value(r,"thermal_transmission","WP4" if "WP4" in scope else "WP3")
  if a is None or b is None:continue
  eligible=r.get("eligible") is True if "WP4" in scope else r.get("qualified_for_numerical_pareto") is True
  classification=("Pareto eligible" if eligible and str(r["candidate"]) in pareto else
                  "Eligible, dominated" if eligible else "Excluded or unresolved")
  expected.append(dict(candidate=str(r["candidate"]),x=a,y=b,classification=classification))
 assert sorted(plotted,key=lambda x:int(x["candidate"]))==sorted(expected,key=lambda x:int(x["candidate"])),(plotted,expected)
 return {"plotted":len(plotted),"exact_coordinates":True,"classes":sorted({r["classification"] for r in plotted})}

def compare_architecture(design):
 fake=Stub()
 with patch.object(d1_visuals,"st",fake):
  d1_visuals.architecture_view(design)
 kind,records,_=_rows(design)
 assert len(fake.charts)>=2
 source_samples=fake.charts[1].data.to_dict("records")
 if kind=="layered":
  expected=[]
  for i,layer in enumerate(design["architecture"]["layers"]):
   for f in layer["composition"]["fractions"]:
    for pos in (layer["start"],layer["end"]):
     expected.append({"position":float(pos),"constituent":f["material_id"],"fraction":float(f["fraction"]),"basis":layer["composition"]["basis"],"layer_id":str(i+1)})
 else:
  expected=[dict(r,layer_id="continuous") for r in records]
  # Source sample index is intentionally retained in chart data.
 assert sorted(source_samples,key=str)==sorted(expected,key=str),(kind,source_samples,expected)
 return kind,len(source_samples)

def main():
 with tempfile.TemporaryDirectory() as temp:
  root=Path(temp)
  wp3=root/"wp3"/"campaign.json"
  run_search(wp3,seed=17,budget=9,elements=128,mass_limit=31.,method="explore")
  view=mixed_summary(wp3)
  print("CHART_REVIEW_PASS WP3",json.dumps(compare_campaign(view,"WP3 intended state")),flush=True)
  counts={}
  for row in view["rows"]:
   if row["status"]!="complete":continue
   kind,count=compare_architecture(mixed_candidate(wp3,row["candidate"])["intended_design"])
   counts[kind]=counts.get(kind,0)+1
  assert set(counts)>={"gradient","layered","homogeneous"},counts
  print("CHART_REVIEW_PASS architecture_source_samples",json.dumps(counts),flush=True)
  target=root/"wp4.json"
  execute(target,elements=4096,mass_limit=31.,budget=4)
  wp4=summary(target)
  print("CHART_REVIEW_PASS WP4",json.dumps(compare_campaign(wp4,"WP4 estimated achieved state")),flush=True)
  no_overlay=0
  for rec in wp4["records"]:
   fake=Stub()
   with patch.object(d1_visuals,"st",fake):d1_visuals.feedback_view(rec)
   achieved=_estimated_design(rec)
   intended=rec.get("intended_design")
   if achieved and intended:
    kind1,_,_=_rows(intended)
    kind2,_,_=_rows(achieved)
    if kind1!=kind2 or kind1=="layered":
     assert any("No unsupported overlay" in message for message in fake.messages)
     no_overlay+=1
  print("CHART_REVIEW_PASS incompatible_state_overlay_suppression",no_overlay,flush=True)
if __name__=="__main__":main()
