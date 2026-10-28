"""WP7 deterministic example evidence builder (not an acceptance determination).

Run with PYTHONPATH=foundation .venv-foundation/bin/python foundation/wp7_create_examples.py OUTPUT
Creates new output folder; never overwrites prior evidence.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from material_core.wp5_service import execute, replay
from material_core.wp7_view import summary
from material_core.wp3_search import run_search, recompute_search
from material_core.wp7_search_dossier import mixed_summary, export_mixed_zip, import_mixed_zip


def build(root, *, elements=4096, budget=9):
    root = Path(root)
    if root.exists():
        raise FileExistsError("WP7 evidence output exists; refusing overwrite")
    root.mkdir(parents=True)
    cases = []
    for name, mass in (("representative", 31.0), ("infeasible", 1.0)):
        target = root / (name + "-wp4.json")
        record = execute(target, elements=elements, mass_limit=mass, budget=4, feedback=True)
        view = summary(target)
        check = replay(target)
        assert check["status"] == "passed"
        if name == "infeasible":
            assert not any(row["eligible"] for row in view["rows"])
        cases.append(dict(case=name, path=target.name, sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                          candidates=len(view["rows"]), eligible=sum(row["eligible"] for row in view["rows"]),
                          pareto=view["pareto"], stop_reason=record["stop_reason"],
                          replay=check, measured_evidence=None))
    wp3 = root / "wp3-mixed"
    ledger_path = wp3 / "campaign.json"
    search = run_search(ledger_path, elements=elements, budget=budget, seed=17, mass_limit=31.)
    view = mixed_summary(ledger_path)
    architectures = {r["architecture"] for r in view["rows"]}
    assert {"homogeneous", "layered", "gradient"} <= architectures
    replay_result = recompute_search(ledger_path)
    assert replay_result["replay"] == "passed"
    z = export_mixed_zip(ledger_path)
    bundle = root / "wp3-mixed-portable.zip"
    bundle.write_bytes(z)
    restored = root / "wp3-restored"
    imported = import_mixed_zip(z, restored)
    assert imported["replay"] == "passed"
    # Actually execute separate Python processes, not just two calls in this process.
    wp3_command = ("import json,sys; from material_core.wp3_search import recompute_search; "
                   "print(json.dumps(recompute_search(sys.argv[1])))")
    wp4_command = ("import json,sys; from material_core.wp5_service import replay; "
                   "print(json.dumps(replay(sys.argv[1])))")
    results = []
    for command, path, key in (
        (wp3_command, restored / "campaign.json", "replay"),
        (wp4_command, root / "representative-wp4.json", "status"),
        (wp4_command, root / "infeasible-wp4.json", "status"),
    ):
        process = subprocess.run([sys.executable, "-c", command, str(path)],
                                 check=True, text=True, capture_output=True)
        decoded = json.loads(process.stdout)
        assert decoded[key] == "passed"
        results.append(dict(path=str(path.relative_to(root)), result=decoded,
                            separate_process=True))
    report = dict(schema="wp7-d1-examples-v1", provenance="synthetic WP3/WP4 and accepted numerical core",
                  measured_evidence=None, manufacturing_validation="not_established",
                  mesh_elements=elements, wp4_cases=cases,
                  wp3=dict(candidates=len(view["rows"]), architectures=sorted(architectures),
                           path="wp3-mixed/campaign.json",
                           zip="wp3-mixed-portable.zip",
                           zip_sha256=hashlib.sha256(z).hexdigest(),
                           qualified_comparison=view["pareto"], replay=replay_result),
                  separate_process_checks=results)
    (root / "example-manifest.json").write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    return report


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("output")
    parser.add_argument("--elements", type=int, default=4096)
    parser.add_argument("--budget", type=int, default=9)
    args = parser.parse_args()
    report = build(args.output, elements=args.elements, budget=args.budget)
    print(json.dumps({"status": "passed", "wp3_architectures": report["wp3"]["architectures"],
                      "wp4_cases": len(report["wp4_cases"]),
                      "separate_process_replays": len(report["separate_process_checks"])}))


if __name__ == "__main__":
    main()
