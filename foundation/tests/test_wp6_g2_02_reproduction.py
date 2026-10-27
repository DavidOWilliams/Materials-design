"""Regression: original immutable WP6-G2-02 fixture independently reproduces."""
import json
import os
import subprocess
import sys
from pathlib import Path

def test_original_unresolved_reproduction(tmp_path):
    original=os.environ.get("WP6_ORIGINAL_NUMERICAL_ATTEMPTS")
    assert original, "Original archived numerical_attempts.json must be supplied"
    root=Path(__file__).resolve().parents[1]
    proc=subprocess.run([sys.executable,str(root/"wp6"/"reproduce_unresolved.py"),
                         original,str(tmp_path/"reproduced")],
                        capture_output=True,text=True)
    report_path=tmp_path/"reproduced"/"reproduction.json"
    assert report_path.exists(),proc.stdout+"\n"+proc.stderr
    report=json.loads(report_path.read_text())
    assert proc.returncode==0,(proc.stdout,proc.stderr,report.get("error"),report.get("differences"))
    assert report["original_file_sha256"]=="4c61c3459f7a5d40d22286255650fb7988233b628eb26f4d1a9a9bebd7c6ce5c"
    assert report["status"]=="pass"
    assert report["original"]["status"]==report["recomputed"]["status"]=="complete"
    assert report["original"]["numerical_quality"]==report["recomputed"]["numerical_quality"]=="unresolved"
    assert report["original"]["eligible"] is report["recomputed"]["eligible"] is False
    assert report["differences"]==[]
