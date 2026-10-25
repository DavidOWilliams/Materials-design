"""Alternate WP3 duty through the identical WP4 feedback campaign lifecycle."""
from __future__ import annotations
from .wp3_adapters import resolve_provider,ALTERNATE
from .wp4_feedback import run

def alternate_duty(*,elements=256,mass_limit=31.,layer=.005,feed=.25,budget=4,feedback=True):
    provider=resolve_provider(ALTERNATE,17,"explore",elements,mass_limit)
    base=provider.baseline()
    campaign=run(elements=elements,mass_limit=mass_limit,layer=layer,feed=feed,
        budget=budget,feedback=feedback,base_inputs=base)
    return dict(adapter=ALTERNATE,duty=base.brief.duty,
        original_design_hash=base.design.content_hash,
        estimated_input_hash=campaign["records"][0]["estimated_hash"],
        evaluation_hash=campaign["records"][0]["evaluation_hash"],
        numerical_quality=campaign["records"][0]["numerical_quality"],
        manufacturing_feasibility=campaign["records"][0]["evaluation"]["manufacturing_feasibility"],
        objectives=campaign["records"][0]["objectives"],
        balance=campaign["records"][0]["balances"],
        campaign=campaign)
