"""WP3 versioned scenario adapter boundary (software architecture, no new physics).

Orchestrator uses start/proposal/build/validate and never interprets knots,
constituent IDs or architectures. Alternate fixture tests a genuinely different
declared duty, a two-phase catalogue, and three-layer candidates using WP2.
"""
import json
import random
from .contracts import (Composition,ConstituentFraction,Homogeneous,Layer,Layered,
                        IntendedDesign,RunInputs,quantity)
from .wp2_numerical import context_for_run
from .wp2_scenarios import make_wp2_fixture
from .wp3_provider import BoundedProvider,propose,PROVIDER_ID

DEFAULT="wp3-synthetic-catalogue-provider-v1"
ALTERNATE="wp3-alternate-duty-layered-provider-v1"
SUPPORTED=(DEFAULT,ALTERNATE)


class CatalogueAdapter:
    identity=DEFAULT
    def __init__(self,seed,method,elements,mass_limit):
        self.generator=BoundedProvider(seed,method)
        self.elements=elements
        self.mass_limit=mass_limit
    def start(self):
        return dict(architecture="homogeneous",
                    pair=("scenario_A","scenario_B"),fraction=.5)
    def proposal(self,index):
        return self.generator.proposal(index)
    def build(self,spec,parent_hashes):
        return propose(**spec,elements=self.elements,mass_limit=self.mass_limit,
                       parent_hashes=parent_hashes,origin=self.identity)
    def validate(self,spec,inputs):
        # The canonical typed, versioned constructor is the scenario validator.
        try:
            reconstructed=self.build(spec,inputs.design.parent_hashes)
        except (ValueError,TypeError) as error:
            raise ValueError("Proposal validation rejected unsupported parameters") from error
        if reconstructed.content_hash!=inputs.content_hash:
            raise ValueError("Scenario proposal differs from stored typed design")
    def baseline(self):
        return self.build(self.start(),())


class AlternateDutyAdapter:
    identity=ALTERNATE
    def __init__(self,seed,method,elements,mass_limit):
        self.rng=random.Random(seed)
        self.elements=elements
        self.mass_limit=mass_limit
        self.method=method
    def start(self):
        return dict(profile="three-layer",core_fraction=.5)
    def proposal(self,index):
        # Structured fixed-profile coverage vs seeded sampling, both on a
        # distinct 380/320 K duty and actual 3-layer construction.
        fraction=(.25,.5,.75)[index%3] if self.method=="explore" else self.rng.uniform(.2,.8)
        return dict(profile="three-layer",core_fraction=round(float(fraction),8))
    def build(self,spec,parent_hashes):
        if set(spec)!={"profile","core_fraction"} or spec["profile"]!="three-layer":
            raise ValueError("Alternate provider unsupported proposal")
        f=spec["core_fraction"]
        if type(f) not in (int,float) or not .2<=f<=.8:
            raise ValueError("Invalid alternate core fraction")
        x=make_wp2_fixture("layered",elements=self.elements,mass_limit=self.mass_limit)
        def comp(frac):
            return Composition(basis="volume",fractions=(
                ConstituentFraction(material_id="scenario_A",fraction=float(frac)),
                ConstituentFraction(material_id="scenario_B",fraction=float(1-frac))))
        left=(1-f)/2
        arch=Layered(layers=(
            Layer(start=0.,end=left,composition=comp(1.)),
            Layer(start=left,end=left+f,composition=comp(.25)),
            Layer(start=left+f,end=1.,composition=comp(0.))),
            interface_condition="perfect")
        raw=x.model_dump(mode="json")
        raw["brief"]["hot_boundary"]=quantity("temperature",380.).model_dump(mode="json")
        raw["brief"]["cold_boundary"]=quantity("temperature",320.).model_dump(mode="json")
        raw["brief"]["duty"]="Alternate synthetic 380 K / 320 K three-layer duty"
        raw["brief"]["id"]="WP3-alternate-three-layer-duty"
        design=IntendedDesign(
            id="wp3-alternate-three-layer-"+str(f),parent_hashes=tuple(parent_hashes),
            thickness=x.brief.thickness,architecture=arch,
            proposal_method=self.identity,assumptions=x.brief.assumptions)
        raw["design"]=design.model_dump(mode="json")
        preliminary=RunInputs.model_validate_json(json.dumps(raw))
        raw["settings"]["evaluation_context_hash"]=context_for_run(preliminary)
        return RunInputs.model_validate_json(json.dumps(raw))
    def validate(self,spec,inputs):
        expected=self.build(spec,inputs.design.parent_hashes)
        if expected.content_hash!=inputs.content_hash:
            raise ValueError("Alternate proposal differs from typed persisted inputs")
    def baseline(self):
        return self.build(self.start(),())


def resolve_provider(identity,seed,method,elements,mass_limit):
    cls={DEFAULT:CatalogueAdapter,ALTERNATE:AlternateDutyAdapter}.get(identity)
    if cls is None:
        raise ValueError("Unavailable/unsupported versioned proposal adapter: "+str(identity))
    return cls(seed,method,elements,mass_limit)
