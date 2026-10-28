"""Versioned evaluator selection for bounded WP3 campaigns."""
from .wp2_numerical import evaluate

STANDARD = "wp2-bounded-2"
DELEGATE = "wp2-delegate-test-v1"

def delegate(inputs):
    return evaluate(inputs)

IMPLEMENTATIONS = {STANDARD: evaluate, DELEGATE: delegate}

def for_run(adapter, identity):
    if adapter is None:
        if identity is None:
            return STANDARD, evaluate
        if identity not in IMPLEMENTATIONS:
            raise ValueError("Unavailable evaluator implementation: " + str(identity))
        return identity, IMPLEMENTATIONS[identity]
    if not callable(adapter):
        raise ValueError("evaluation_adapter must be callable")
    if not isinstance(identity, str) or not identity.strip():
        raise ValueError("Custom evaluation_adapter requires explicit evaluator_identity")
    if identity in IMPLEMENTATIONS and adapter is not IMPLEMENTATIONS[identity]:
        raise ValueError("Evaluator identity reserved for registered implementation: " + identity)
    return identity, adapter

def for_replay(identity):
    if identity not in IMPLEMENTATIONS:
        raise ValueError("Unavailable evaluator for numerical recomputation: " + str(identity))
    return IMPLEMENTATIONS[identity]
