"""Pure, dependency-free visual data selectors. Never calculate physics or eligibility."""
from __future__ import annotations
import math
from pathlib import Path

def _value(row, objective, scope):
    key = objective if scope == "WP4" else {
        "thermal_transmission": "thermal_transmission_W_m2",
        "areal_mass": "areal_mass_kg_m2",
        "tensile_thermal_mismatch": "tensile_thermal_mismatch_Pa",
    }[objective]
    v = row.get(key)
    return float(v) if type(v) in (int,float) and math.isfinite(v) else None

def _valid(row, scope):
    return row.get("eligible") is True if scope == "WP4" else row.get("qualified_for_numerical_pareto") is True

def _pareto_ids(result):
    return {str(i) for i in result.get("pareto_ids",[])} if isinstance(result,dict) else set()

def _rows(design):
    arch=design["architecture"]
    kind=arch["kind"]
    if kind=="homogeneous":
        entries=[(0.,arch["composition"]),(1.,arch["composition"])]
    elif kind=="layered":
        entries=[(float(x["start"]),x["composition"]) for x in arch["layers"]]
        entries.append((float(arch["layers"][-1]["end"]),arch["layers"][-1]["composition"]))
    elif kind=="gradient" and arch.get("interpolation")=="piecewise_linear":
        entries=[(float(k["position"]),k["composition"]) for k in arch["knots"]]
    else:
        return kind,[],[]
    table=[]
    for i,(pos,comp) in enumerate(entries):
        for f in comp["fractions"]:
            table.append(dict(position=pos,constituent=f["material_id"],
                              fraction=float(f["fraction"]),basis=comp["basis"],sample=i))
    return kind,table,entries

def _estimated_design(record):
    e=record.get("estimated_inputs")
    if not isinstance(e,dict):
        return None
    state=e.get("estimated_state")
    if not isinstance(state,dict):
        return None
    geometry=state.get("geometry")
    return geometry if isinstance(geometry,dict) and isinstance(geometry.get("architecture"),dict) else None

def output_conflicts(path, companions=()):
    """Check destination and sidecar evidence without touching any persisted file."""
    p=Path(path)
    return [str(q) for q in (p,*(Path(str(p)+suffix) for suffix in companions)) if q.exists()]

def unused_output(path, companions=()):
    """Suggest deterministic unused name; backend still rejects a race collision."""
    p=Path(path)
    if not output_conflicts(p,companions):
        return p
    for i in range(1,10001):
        q=p.with_name(p.stem+f"-run-{i:03d}"+p.suffix)
        if not output_conflicts(q,companions):
            return q
    raise ValueError("Could not find a fresh dossier destination")
