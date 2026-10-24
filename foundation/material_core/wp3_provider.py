"""WP3 bounded mixed architecture / constituent proposal provider.

All records are explicitly synthetic; the third catalogue constituent is an
invented numerical test record, NOT a ceramic reference. No process feasibility
is inferred. The entire pack remains fixed as candidates select constituents.
"""
from __future__ import annotations
import hashlib
import json
import random

from .contracts import (
    Composition, ConstituentFraction, Gradient, Homogeneous, IntendedDesign,
    Knot, Layer, Layered, MaterialRecord, Property, Provenance, RunInputs,
    quantity,
)
from .wp2_numerical import context_for_run, property_pack_hash
from .wp2_scenarios import make_wp2_fixture

PROVIDER_ID = "wp3-synthetic-catalogue-provider-v1"
CATALOGUE_ID = "wp3-neutral-A-B-C"
CATALOGUE_VERSION = "1"


def _composition(pair, fraction):
    return Composition(basis="volume", fractions=(
        ConstituentFraction(material_id=pair[0], fraction=float(fraction)),
        ConstituentFraction(material_id=pair[1], fraction=float(1-fraction)),
    ))


def make_catalogue_base(*, elements=4096, mass_limit=31.):
    """One versioned pack shared across all candidate constituent subsets."""
    original = make_wp2_fixture("gradient", elements=elements, mass_limit=mass_limit)
    prior = original.materials[0]
    manifest = "WP3 synthetic third constituent: k=5,rho=2500,Q=125e9,alpha=7e-6,domain=290..410 K"
    provenance = Provenance(
        source_id="wp3-neutral-synthetic-catalogue",
        source_version=CATALOGUE_VERSION,
        source_hash=hashlib.sha256(manifest.encode()).hexdigest(),
        location="foundation/material_core/wp3_provider.py:make_catalogue_base",
        reuse_terms="Project generated test values only; not measured materials",
        evidence_kind="synthetic_scenario",
        conditions=prior.provenance.conditions,
        extraction="Hypothetical numerical test record without experimental basis",
    )
    vals={"conductivity":quantity("conductivity",5.),
          "density":quantity("density",2500.),
          "biaxial_modulus":quantity("stress",125e9),
          "expansion":quantity("expansion",7e-6)}
    props=tuple(Property(
        name=p.name, quantity=vals[p.name],
        convention=p.convention, conditions=p.conditions, uncertainty=None,
        provenance=provenance, temperature_min=p.temperature_min,
        temperature_max=p.temperature_max,
    ) for p in prior.properties)
    third=MaterialRecord(
        id="scenario_C", version=1, label="Hypothetical scenario_C",
        state=prior.state, chemistry="synthetic numerical test; no actual composition",
        properties=props, provenance=provenance,
    )
    raw=original.model_dump(mode="json")
    materials=tuple(original.materials)+(third,)
    raw["materials"]=[m.model_dump(mode="json") for m in materials]
    raw["settings"]["property_pack_id"]=CATALOGUE_ID
    raw["settings"]["property_pack_version"]=CATALOGUE_VERSION
    raw["settings"]["property_pack_hash"]=property_pack_hash(materials)
    raw["provenance"].append(provenance.model_dump(mode="json"))
    preliminary=RunInputs.model_validate_json(json.dumps(raw))
    raw["settings"]["evaluation_context_hash"]=context_for_run(preliminary)
    return RunInputs.model_validate_json(json.dumps(raw))


def propose(*, architecture, pair, fraction, knot_position=.5, elements=4096, mass_limit=31.,
            parent_hashes=(), origin=PROVIDER_ID):
    """Bounded candidate; pair is ordered, two distinct members from A/B/C."""
    if architecture not in ("homogeneous","layered","gradient"):
        raise ValueError("Unsupported architecture")
    if len(pair)!=2 or pair[0]==pair[1] or any(
            m not in ("scenario_A","scenario_B","scenario_C") for m in pair):
        raise ValueError("Unsupported constituent selection")
    if type(fraction) not in (int,float) or not 0.05<=fraction<=0.95:
        raise ValueError("Fraction outside declared [0.05,0.95]")
    if type(knot_position) not in (int,float) or not 0.05<=knot_position<=0.95:
        raise ValueError("Gradient knot position outside [0.05,0.95]")
    base=make_catalogue_base(elements=elements,mass_limit=mass_limit)
    if architecture=="homogeneous":
        arch=Homogeneous(composition=_composition(pair,fraction))
    elif architecture=="layered":
        arch=Layered(layers=(
            Layer(start=0.,end=float(fraction),composition=_composition(pair,1.)),
            Layer(start=float(fraction),end=1.,composition=_composition(pair,0.)),
        ),interface_condition="perfect")
    else:
        arch=Gradient(knots=(
            Knot(position=0.,composition=_composition(pair,1.)),
            Knot(position=float(knot_position),composition=_composition(pair,fraction)),
            Knot(position=1.,composition=_composition(pair,0.)),
        ))
    design=IntendedDesign(
        id="wp3-"+architecture+"-"+pair[0]+"-"+pair[1]+"-"+str(fraction),
        parent_hashes=tuple(parent_hashes),thickness=base.brief.thickness,
        architecture=arch,proposal_method=origin,
        assumptions=base.brief.assumptions,
    )
    raw=base.model_dump(mode="json")
    raw["design"]=design.model_dump(mode="json")
    preliminary=RunInputs.model_validate_json(json.dumps(raw))
    raw["settings"]["evaluation_context_hash"]=context_for_run(preliminary)
    return RunInputs.model_validate_json(json.dumps(raw))


class BoundedProvider:
    """Replaceable proposal generator. Random and exploratory policies share a space."""
    def __init__(self, seed, method="explore"):
        if type(seed) is not int or method not in ("explore","sampling"):
            raise ValueError("Invalid seed or provider method")
        self.rng=random.Random(seed)
        self.method=method
        self.pairs=(("scenario_A","scenario_B"),
                    ("scenario_A","scenario_C"),
                    ("scenario_C","scenario_B"))
        self.architectures=("homogeneous","layered","gradient")

    def proposal(self, index):
        if self.method=="explore":
            # Structured coverage of all architecture and pair combinations
            # with seeded bounded parameter variation; no claim of optimality.
            pair=self.pairs[(index//3)%len(self.pairs)]
            architecture=self.architectures[index%3]
            fraction=(0.35 if index==0 else 0.65 if index==1
                      else round(self.rng.uniform(.1,.9),8))
        else:
            pair=self.rng.choice(self.pairs)
            architecture=self.rng.choice(self.architectures)
            fraction=round(self.rng.uniform(.1,.9),8)
        return dict(pair=pair,architecture=architecture,fraction=fraction,
                    knot_position=round(self.rng.uniform(.3,.7),8) if architecture=="gradient" else .5)
