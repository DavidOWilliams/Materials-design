"""Portable regression for WP6-G2-02, plus exact archived fixture in WP6 CI.

No network or artifact environment variable is required for general foundation tests.
The dedicated WP6 workflow additionally supplies the original archived fixture.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ORIGINAL_SHA256="4c61c3459f7a5d40d22286255650fb7988233b628eb26f4d1a9a9bebd7c6ce5c"
EXPECTED_INPUT_HASH="bb255bef4c643887e71a80639b1b6b49790d43bd4c92fd077017b4961cbe0bb2"

def test_original_unresolved_reproduction(tmp_path):
    root=Path(__file__).resolve().parents[1]
    original=os.environ.get("WP6_ORIGINAL_NUMERICAL_ATTEMPTS")
    if original is None:
        # Reconstruct the registered two-element scientific case from the
        # unchanged WP4 fixture builder, without requiring GitHub credentials.
        from material_core.wp4_feedback import starting_inputs
        from material_core.wp2_numerical import evaluate, numerical_comparison_eligible
        inputs=starting_inputs(elements=2,mass_limit=31.0)
        result=evaluate(inputs)
        eligible=numerical_comparison_eligible(result,inputs.brief)
        assert result.status=="complete"
        assert result.numerical_quality=="unresolved"
        assert eligible is False
        original=tmp_path/"local_numerical_attempts.json"
        original.write_text(json.dumps([dict(elements=2,input=inputs.model_dump(mode="json"),
            evaluation=result.model_dump(mode="json"),status=result.status,
            numerical_quality=result.numerical_quality,eligible=eligible)],sort_keys=True))
    proc=subprocess.run([sys.executable,str(root/"wp6"/"reproduce_unresolved.py"),
                         str(original),str(tmp_path/"reproduced")],
                        capture_output=True,text=True)
    report_path=tmp_path/"reproduced"/"reproduction.json"
    assert report_path.exists(),proc.stdout+"\\n"+proc.stderr
    report=json.loads(report_path.read_text())
    assert proc.returncode==0,(proc.stdout,proc.stderr,report.get("error"),report.get("differences"))
    if os.environ.get("WP6_ORIGINAL_NUMERICAL_ATTEMPTS"):
        assert report["original_file_sha256"]==ORIGINAL_SHA256
    assert report["input_hash"]==EXPECTED_INPUT_HASH
    assert report["status"]=="pass"
    assert report["original"]["status"]==report["recomputed"]["status"]=="complete"
    assert report["original"]["numerical_quality"]==report["recomputed"]["numerical_quality"]=="unresolved"
    assert report["original"]["eligible"] is report["recomputed"]["eligible"] is False
    assert report["differences"]==[]
