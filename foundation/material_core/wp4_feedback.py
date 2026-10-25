"""Bounded synthetic manufacturing-feedback campaign.

A design revision is derived from the violated achieved-state material budget.
This is not a general optimiser or an empirical manufacturing model.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from .contracts import (RunInputs, IntendedDesign, Gradient, Homogeneous, Layered,
    Knot, Layer, Composition, ConstituentFraction, ProcessScenario, Provenance, quantity)
from .wp2_scenarios import make_wp2_fixture
from .wp2_numerical import evaluate, numerical_comparison_eligible, context_for_run
from .wp4_bridge import estimated_inputs
from .wp4_resolution import TRANSFORM_ID, TRANSFORM_VERSION

VERSION="wp4-feedback-v1"

def _digest(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()

def scenario(layer=0.005,feed=0.25):
    p=make_wp2_fixture().provenance[0]
    return ProcessScenario(id="wp4-ideal-resolution",version=1,
        route="synthetic_ideal_planar_deposition",layer_resolution=quantity("length",layer),
        feed_fraction_resolution=feed,status="assumed",provenance=p,assumptions=(),
        excluded_mechanisms=("mixing lag","shrinkage","porosity","sintering","CFD","manufacturing residual stress"))

def _composition(f, ids):
    return Composition(basis="volume",fractions=(
        ConstituentFraction(material_id=ids[0],fraction=float(f)),
        ConstituentFraction(material_id=ids[1],fraction=float(1-f))))

def starting_inputs(elements=4096,mass_limit=31.):
    base=make_wp2_fixture("gradient",elements=elements,mass_limit=mass_limit)
    ids=("scenario_A","scenario_B")
    arch=Gradient(knots=(Knot(position=0.,composition=_composition(.25,ids)),
                         Knot(position=1.,composition=_composition(.05,ids))))
    d=IntendedDesign(id="wp4-binding-gradient",thickness=base.design.thickness,
        architecture=arch,proposal_method="declared synthetic binding-constraint example",
        assumptions=base.design.assumptions)
    raw=base.model_dump(mode="json")
    raw["design"]=d.model_dump(mode="json")
    raw["settings"]["evaluation_context_hash"]=context_for_run(RunInputs.model_validate_json(json.dumps(raw)))
    return RunInputs.model_validate_json(json.dumps(raw))

def _density(inputs):
    densities={}
    for material in inputs.materials:
        match=[p.quantity.value for p in material.properties if p.name=="density"]
        if len(match)!=1: raise ValueError("Missing unique density for feedback")
        densities[material.id]=match[0]
    return densities

def _fraction(comp, material):
    return next(f.fraction for f in comp.fractions if f.material_id==material)

def _revise(base, parent, feedback, step=0.25):
    if feedback["metric"]!="areal_mass" or feedback["relation"]!="le":
        raise ValueError("Unsupported feedback for this bounded revision policy")
    densities=_density(base)
    light=min(densities,key=lambda x:(densities[x],x))
    if len(densities)!=2 or len(set(densities.values()))!=2:
        raise ValueError("Revision requires exactly two constituents with distinct density")
    arch=parent.architecture
    compositions=([arch.composition] if isinstance(arch,Homogeneous)
        else [l.composition for l in arch.layers] if isinstance(arch,Layered)
        else [k.composition for k in arch.knots])
    if any(c.basis!="volume" or {f.material_id for f in c.fractions}!=set(densities) for c in compositions):
        raise ValueError("Unsupported revision composition basis")
    def revise(c):
        old=_fraction(c,light)
        new=min(1.,old+step)
        return _composition(new,(light,next(x for x in sorted(densities) if x!=light)))
    if isinstance(arch,Homogeneous):
        updated=Homogeneous(composition=revise(arch.composition))
    elif isinstance(arch,Layered):
        updated=Layered(layers=tuple(Layer(start=l.start,end=l.end,composition=revise(l.composition))
            for l in arch.layers),interface_condition=arch.interface_condition)
    elif isinstance(arch,Gradient):
        updated=Gradient(knots=tuple(Knot(position=k.position,composition=revise(k.composition))
            for k in arch.knots))
    else: raise ValueError("Unsupported architecture")
    return IntendedDesign(id=parent.id+"-feedback-"+parent.content_hash[:10],
        parent_hashes=(parent.content_hash,),thickness=parent.thickness,
        architecture=updated,proposal_method="wp4 density-guided composition revision from "+feedback["metric"],
        assumptions=parent.assumptions)

def _replace_design(base,design):
    raw=base.model_dump(mode="json")
    raw["design"]=design.model_dump(mode="json")
    raw["settings"]["evaluation_context_hash"]=context_for_run(RunInputs.model_validate_json(json.dumps(raw)))
    return RunInputs.model_validate_json(json.dumps(raw))

def _metrics(e):
    return {m.objective_id:(None if m.value is None else m.value.value) for m in e.metrics}

def run(*,elements=4096,mass_limit=31.,layer=0.005,feed=0.25,budget=4,feedback=True):
    if type(budget)!=int or budget<1: raise ValueError("Positive evaluation budget required")
    base=starting_inputs(elements,mass_limit)
    process=scenario(layer,feed)
    # Freeze common intended/estimated contexts before selecting any result.
    records=[]
    intended=evaluate(base)
    design=base.design
    stop="evaluation_budget_exhausted"
    for i in range(budget):
        candidate=_replace_design(base,design)
        achieved=estimated_inputs(candidate,process)
        result=evaluate(achieved)
        limit=mass_limit
        actual=next((m.value.value for m in result.metrics
                     if m.objective_id=="areal_mass" and m.value is not None),None)
        feedback_record=None
        if actual is not None and actual>limit:
            feedback_record=dict(metric="areal_mass",relation="le",limit=limit,
                actual=actual,excess=actual-limit,units="kg/m2",
                location="whole coupon",evidence="synthetic WP2 estimated achieved-state",
                revision_variables=["constituent volume fraction"])
        qualified=numerical_comparison_eligible(result,achieved.brief)
        feasible=(qualified and feedback_record is None and
                  result.feasibility=="conditional" and
                  result.manufacturing_feasibility=="conditional")
        records.append(dict(index=i,intended_design=design.model_dump(mode="json"),
            intended_hash=design.content_hash,estimated_inputs=achieved.model_dump(mode="json"),
            estimated_hash=achieved.content_hash,commands_hash=achieved.commands.content_hash,
            estimated_geometry_hash=achieved.estimated_state.geometry.content_hash,
            evaluation=result.model_dump(mode="json"),evaluation_hash=result.content_hash,
            objectives=_metrics(result),numerical_quality=result.numerical_quality,
            feasible=feasible,feedback=feedback_record))
        if feasible:
            stop="qualified_scenario_feasible"
            break
        if not feedback:
            stop="feedback_disabled"
            break
        if feedback_record is None:
            stop="no_supported_revision_trigger"
            break
        if i+1>=budget:
            break
        new_design=_revise(base,design,feedback_record)
        if new_design.architecture==design.architecture:
            stop="no_improvement_possible"
            break
        design=new_design
    return dict(schema_version=1,algorithm=VERSION,
        baseline_intended_inputs=base.model_dump(mode="json"),
        baseline_intended_evaluation=intended.model_dump(mode="json"),
        process=process.model_dump(mode="json"),
        config=dict(elements=elements,mass_limit=mass_limit,layer=layer,feed=feed,
            budget=budget,feedback=feedback),
        records=records,stop_reason=stop,proposals=len(records),
        transforms=len(records),evaluations=len(records)+1,
        refinement_solves=2*(len(records)+1),measured_evidence=None)

def save(path,record):
    path=Path(path)
    if path.exists(): raise FileExistsError("Immutable WP4 dossier exists")
    path.parent.mkdir(parents=True,exist_ok=True)
    payload=dict(record=record,record_sha256=_digest(record))
    path.write_text(json.dumps(payload,sort_keys=True,indent=2,allow_nan=False)+"\n")
    return payload["record_sha256"]

def reopen(path):
    payload=json.loads(Path(path).read_text())
    record=payload["record"]
    if _digest(record)!=payload["record_sha256"]:
        raise ValueError("Dossier checksum mismatch")
    if record.get("algorithm")!=VERSION or record.get("measured_evidence") is not None:
        raise ValueError("Unsupported dossier or invented measured evidence")
    process=ProcessScenario.model_validate_json(json.dumps(record["process"]))
    previous=None
    for i,row in enumerate(record["records"]):
        inputs=RunInputs.model_validate_json(json.dumps(row["estimated_inputs"]))
        if row["index"]!=i or inputs.process!=process:
            raise ValueError("Scenario or ordering mismatch")
        if inputs.design.content_hash!=row["intended_hash"]:
            raise ValueError("Design lineage mismatch")
        if i and inputs.design.parent_hashes!=(previous,):
            raise ValueError("Revision parent mismatch")
        if inputs.commands.content_hash!=row["commands_hash"] or inputs.estimated_state.geometry.content_hash!=row["estimated_geometry_hash"]:
            raise ValueError("Transform artifact mismatch")
        if inputs.content_hash!=row["estimated_hash"]:
            raise ValueError("Input identity mismatch")
        previous=row["intended_hash"]
    return record

def recompute(path):
    record=reopen(path)
    base=RunInputs.model_validate_json(json.dumps(record["baseline_intended_inputs"]))
    process=ProcessScenario.model_validate_json(json.dumps(record["process"]))
    if evaluate(base).content_hash!=__import__("material_core.contracts",fromlist=["Evaluation"]).Evaluation.model_validate_json(json.dumps(record["baseline_intended_evaluation"])).content_hash:
        raise ValueError("Baseline numerical recomputation mismatch")
    for row in record["records"]:
        design=IntendedDesign.model_validate_json(json.dumps(row["intended_design"]))
        inputs=estimated_inputs(_replace_design(base,design),process)
        if inputs.content_hash!=row["estimated_hash"]:
            raise ValueError("Transform recomputation mismatch")
        if evaluate(inputs).content_hash!=row["evaluation_hash"]:
            raise ValueError("WP2 numerical recomputation mismatch")
    return dict(recomputed=len(record["records"]),status="passed")

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("action",choices=("run","reopen","recompute"))
    parser.add_argument("path")
    parser.add_argument("--elements",type=int,default=4096)
    parser.add_argument("--mass-limit",type=float,default=31.)
    parser.add_argument("--layer",type=float,default=.005)
    parser.add_argument("--feed",type=float,default=.25)
    parser.add_argument("--budget",type=int,default=4)
    parser.add_argument("--no-feedback",action="store_true")
    args=parser.parse_args()
    if args.action=="run":
        rec=run(elements=args.elements,mass_limit=args.mass_limit,layer=args.layer,
            feed=args.feed,budget=args.budget,feedback=not args.no_feedback)
        save(args.path,rec)
        print(json.dumps(dict(stop_reason=rec["stop_reason"],proposals=rec["proposals"],
            feasible=[r["feasible"] for r in rec["records"]])))
    elif args.action=="reopen":
        print(json.dumps(dict(stop_reason=reopen(args.path)["stop_reason"],status="validated")))
    else:
        print(json.dumps(recompute(args.path)))
if __name__=="__main__":main()
