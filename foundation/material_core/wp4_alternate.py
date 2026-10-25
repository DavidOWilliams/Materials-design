"""WP4 alternate duty via the accepted WP3 adapter, unchanged numerical physics."""
from __future__ import annotations
from .wp3_adapters import resolve_provider,ALTERNATE
from .wp4_feedback import scenario
from .wp4_bridge import evaluate_estimated
from .wp4_balances import balances

def alternate_duty(*,elements=256,mass_limit=31.,layer=.005,feed=.25):
    provider=resolve_provider(ALTERNATE,17,"explore",elements,mass_limit)
    base=provider.baseline()
    process=scenario(layer,feed)
    achieved,result=evaluate_estimated(base,process)
    return dict(adapter=ALTERNATE,duty=base.brief.duty,
        original_design_hash=base.design.content_hash,
        estimated_input_hash=achieved.content_hash,
        evaluation_hash=result.content_hash,
        numerical_quality=result.numerical_quality,
        manufacturing_feasibility=result.manufacturing_feasibility,
        objectives={m.objective_id:(None if m.value is None else m.value.value) for m in result.metrics},
        balance=balances(base.design,achieved.commands,achieved.estimated_state))
