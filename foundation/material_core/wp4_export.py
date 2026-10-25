"""Conservative WP4 evidence export, with explicit absence of measurements."""
from __future__ import annotations
from .wp4_feedback import reopen

def export(path):
    record=reopen(path)
    return dict(schema_version=1,source_algorithm=record["algorithm"],
        process_identity=record["transformer_identity"],
        process_scenario=record["process"],
        intended_baseline_hash=record["baseline_intended_inputs"]["design"]["id"],
        evaluation_target="estimated",
        measured_evidence=None,
        measured_evidence_status="not_available",
        manufacturing_validation="not_established",
        unsupported_physics=record["process"]["excluded_mechanisms"],
        budget=dict(maximum=record["config"]["budget"],evaluations=record["evaluations"],
                    transforms=record["transforms"],refinement_solves=record["refinement_solves"]),
        stop_reason=record["stop_reason"],
        candidates=[dict(index=row["index"],intended_hash=row["intended_hash"],
            estimated_hash=row["estimated_hash"],evaluation_hash=row["evaluation_hash"],
            objectives=row["objectives"],feedback=row["feedback"],
            balances=row["balances"],numerical_quality=row["numerical_quality"],
            scenario_feasible=row["feasible"]) for row in record["records"]])
