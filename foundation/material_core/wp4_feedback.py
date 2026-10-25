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
from .wp4_balances import balances
from .wp4_registry import resolve

VERSION="wp4-feedback-v1"

def _digest(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()

def scenario(layer=0.005,feed=0.25,route="synthetic_ideal_planar_deposition"):
    p=make_wp2_fixture().provenance[0]
    return ProcessScenario(id="wp4-"+route,version=1,
        route=route,layer_resolution=quantity("length",layer),
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

def run(*,elements=4096,mass_limit=31.,layer=0.005,feed=0.25,budget=4,feedback=True,cancel_requested=None,checkpoint=None,
        route="synthetic_ideal_planar_deposition",base_inputs=None,attempt_event=None):
    if type(budget)!=int or budget<1: raise ValueError("Positive evaluation budget required")
    base=base_inputs if base_inputs is not None else starting_inputs(elements,mass_limit)
    if base_inputs is not None and (base.settings is None or base.brief is None):
        raise ValueError("Invalid supplied duty baseline")
    process=scenario(layer,feed,route)
    transformer_identity,_=resolve(process)
    # Freeze common intended/estimated contexts before selecting any result.
    records=[]
    if attempt_event is not None: attempt_event("baseline_started",None)
    try:
        intended=evaluate(base)
    except Exception as exc:
        if attempt_event is not None: attempt_event("baseline_failed",str(exc))
        raise
    if attempt_event is not None: attempt_event("baseline_completed",None)
    design=base.design
    stop="evaluation_budget_exhausted"
    for i in range(budget):
        if cancel_requested is not None and cancel_requested():
            stop="cancelled"
            break
        if attempt_event is not None: attempt_event("candidate_started",i)
        try:
            candidate=_replace_design(base,design)
            achieved=estimated_inputs(candidate,process)
            result=evaluate(achieved)
        except Exception as exc:
            if attempt_event is not None: attempt_event("candidate_failed",dict(index=i,error=str(exc)))
            raise
        if attempt_event is not None: attempt_event("candidate_completed",i)
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
            feasible=feasible,feedback=feedback_record,
            balances=balances(design,achieved.commands,achieved.estimated_state)))
        if checkpoint is not None:
            checkpoint(tuple(records))
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
        transformer_identity=transformer_identity,
        config=dict(elements=elements,mass_limit=mass_limit,layer=layer,feed=feed,
            budget=budget,feedback=feedback,route=route),
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
    if record.get("transformer_identity")!=resolve(process)[0]:
        raise ValueError("Recorded transform registry identity mismatch")
    previous=None
    previous_feedback=None
    if record["config"]["feedback"] is False and len(record["records"])>1:
        raise ValueError("Feedback-disabled campaign cannot contain revisions")
    if record["config"]["feedback"] is True and record["stop_reason"]=="feedback_disabled":
        raise ValueError("Feedback-enabled campaign cannot stop as disabled")
    if record["config"]["route"]!=process.route:
        raise ValueError("Campaign route mismatch")
    if record["config"]["layer"]!=process.layer_resolution.value or record["config"]["feed"]!=process.feed_fraction_resolution:
        raise ValueError("Campaign resolution mismatch")
    if record["proposals"]!=len(record["records"]) or record["transforms"]!=len(record["records"]) or record["evaluations"]!=len(record["records"])+1 or record["refinement_solves"]!=2*(len(record["records"])+1):
        raise ValueError("Campaign accounting mismatch")
    if not 0<=len(record["records"])<=record["config"]["budget"]:
        raise ValueError("Campaign budget mismatch")
    if record["stop_reason"] not in ("evaluation_budget_exhausted","qualified_scenario_feasible","feedback_disabled","no_supported_revision_trigger","no_improvement_possible","cancelled"):
        raise ValueError("Invalid campaign stop state")
    for i,row in enumerate(record["records"]):
        inputs=RunInputs.model_validate_json(json.dumps(row["estimated_inputs"]))
        if row["index"]!=i or inputs.process!=process or inputs.evaluation_target!="estimated":
            raise ValueError("Scenario or ordering mismatch")
        if inputs.design.content_hash!=row["intended_hash"] or inputs.design.model_dump(mode="json")!=row["intended_design"]:
            raise ValueError("Intended design artifact mismatch")
        if inputs.design.content_hash!=row["intended_hash"]:
            raise ValueError("Design lineage mismatch")
        if i and inputs.design.parent_hashes!=(previous,):
            raise ValueError("Revision parent mismatch")
        if inputs.commands.content_hash!=row["commands_hash"] or inputs.estimated_state.geometry.content_hash!=row["estimated_geometry_hash"]:
            raise ValueError("Transform artifact mismatch")
        if inputs.content_hash!=row["estimated_hash"]:
            raise ValueError("Input identity mismatch")
        result=__import__("material_core.contracts",fromlist=["Evaluation"]).Evaluation.model_validate_json(json.dumps(row["evaluation"]))
        if result.content_hash!=row["evaluation_hash"] or result.input_hash!=inputs.content_hash:
            raise ValueError("Evaluation identity mismatch")
        if row["objectives"]!=_metrics(result) or row["numerical_quality"]!=result.numerical_quality:
            raise ValueError("Persisted objective summary mismatch")
        actual=row["objectives"].get("areal_mass")
        expected_feedback=(None if actual is None or actual<=record["config"]["mass_limit"] else dict(
            metric="areal_mass",relation="le",limit=record["config"]["mass_limit"],
            actual=actual,excess=actual-record["config"]["mass_limit"],units="kg/m2",
            location="whole coupon",evidence="synthetic WP2 estimated achieved-state",
            revision_variables=["constituent volume fraction"]))
        if row["balances"]!=balances(inputs.design,inputs.commands,inputs.estimated_state):
            raise ValueError("Constituent balance mismatch")
        if row["feedback"]!=expected_feedback:
            raise ValueError("Feedback decision mismatch")
        eligible=numerical_comparison_eligible(result,inputs.brief)
        feasible=(eligible and expected_feedback is None and result.feasibility=="conditional" and result.manufacturing_feasibility=="conditional")
        if row["feasible"]!=feasible:
            raise ValueError("Persisted feasibility mismatch")
        if i and (not record["config"]["feedback"] or previous_feedback is None or record["records"][i-1]["feasible"]):
            raise ValueError("Impossible feedback continuation")
        if i and record["config"]["feedback"] and previous_feedback is not None:
            previous_design=IntendedDesign.model_validate_json(json.dumps(record["records"][i-1]["intended_design"]))
            if _revise(RunInputs.model_validate_json(json.dumps(record["baseline_intended_inputs"])),previous_design,previous_feedback).content_hash!=inputs.design.content_hash:
                raise ValueError("Revision was not generated from previous feedback")
        previous_feedback=row["feedback"]
        previous=row["intended_hash"]
    reason=record["stop_reason"]
    last=record["records"][-1] if record["records"] else None
    if reason=="qualified_scenario_feasible" and (last is None or not last["feasible"]):
        raise ValueError("False qualified completion")
    if reason=="feedback_disabled" and (record["config"]["feedback"] or last is None or len(record["records"])!=1 or last["feasible"]):
        raise ValueError("Invalid feedback-disabled terminal state")
    if reason=="no_supported_revision_trigger" and (last is None or last["feedback"] is not None or last["feasible"]):
        raise ValueError("Invalid no-trigger terminal state")
    if reason=="evaluation_budget_exhausted" and (len(record["records"])!=record["config"]["budget"] or last["feasible"]):
        raise ValueError("Invalid budget exhaustion state")
    if reason=="no_improvement_possible" and (last is None or last["feedback"] is None or last["feasible"]):
        raise ValueError("Invalid no-improvement state")
    if last is not None and last["feasible"] and reason!="qualified_scenario_feasible":
        raise ValueError("Feasible candidate with contradictory stop state")
    if reason!="cancelled" and not record["records"]:
        raise ValueError("Empty non-cancelled campaign")
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
    parser.add_argument("action",choices=("run","reopen","recompute","resume"))
    parser.add_argument("path")
    parser.add_argument("--elements",type=int,default=4096)
    parser.add_argument("--mass-limit",type=float,default=31.)
    parser.add_argument("--layer",type=float,default=.005)
    parser.add_argument("--feed",type=float,default=.25)
    parser.add_argument("--budget",type=int,default=4)
    parser.add_argument("--no-feedback",action="store_true")
    parser.add_argument("--route",default="synthetic_ideal_planar_deposition")
    parser.add_argument("--journal",default=None,help="New append-only per-candidate checkpoint journal")
    args=parser.parse_args()
    if args.action=="run":
        from .wp4_journal import Journal
        journal=Journal(args.journal) if args.journal else None
        rec=run(elements=args.elements,mass_limit=args.mass_limit,layer=args.layer,
            feed=args.feed,budget=args.budget,feedback=not args.no_feedback,
            route=args.route,
            checkpoint=journal.checkpoint if journal else None)
        save(args.path,rec)
        print(json.dumps(dict(stop_reason=rec["stop_reason"],proposals=rec["proposals"],
            feasible=[r["feasible"] for r in rec["records"]])))
    elif args.action=="resume":
        from .wp4_journal import resume
        rec=resume(args.path,elements=args.elements,mass_limit=args.mass_limit,
            layer=args.layer,feed=args.feed,budget=args.budget,
            feedback=not args.no_feedback,route=args.route)
        print(json.dumps(dict(stop_reason=rec["stop_reason"],proposals=rec["proposals"],
            resumed_journal=args.path)))
    elif args.action=="reopen":
        print(json.dumps(dict(stop_reason=reopen(args.path)["stop_reason"],status="validated")))
    else:
        print(json.dumps(recompute(args.path)))
if __name__=="__main__":main()
