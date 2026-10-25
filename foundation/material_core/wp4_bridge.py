"""WP4 bridge: estimated geometry into the existing WP2 numerical target.

This is a callable service, not a completed feedback campaign or validation.
"""
from __future__ import annotations
import json
from .contracts import RunInputs
from .wp2_numerical import context_for_run, evaluate
from .wp4_resolution import transform

def estimated_inputs(base: RunInputs, process):
    """Retain original intended design and replace only estimated-target inputs."""
    commands, state=transform(base.design,process)
    raw=base.model_dump(mode="json")
    raw["process"]=process.model_dump(mode="json")
    raw["commands"]=commands.model_dump(mode="json")
    raw["estimated_state"]=state.model_dump(mode="json")
    raw["measured_state"]=None
    raw["evaluation_target"]="estimated"
    # A process may add assumption refs; RunInputs validates complete snapshots.
    preliminary=RunInputs.model_validate_json(json.dumps(raw))
    raw["settings"]["evaluation_context_hash"]=context_for_run(preliminary)
    inputs=RunInputs.model_validate_json(json.dumps(raw))
    return inputs

def evaluate_estimated(base: RunInputs, process):
    inputs=estimated_inputs(base,process)
    return inputs,evaluate(inputs)
