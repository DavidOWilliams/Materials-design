"""Independent process reproduction of archived WP6-G2-02 numerical result.

Reads ONLY the original immutable Actions artifact's gate2/numerical_attempts.json.
No modification of WP2 scientific algorithms, fixtures or tolerances.
"""
from __future__ import annotations
import hashlib
import json
import math
import sys
from pathlib import Path
from material_core.contracts import RunInputs, Evaluation
from material_core.wp2_numerical import evaluate, numerical_comparison_eligible

def _compare(a,b,path,differences):
    if isinstance(a,dict) and isinstance(b,dict):
        if a.keys()!=b.keys():
            differences.append(dict(path=path,kind="keys",original=sorted(a),recomputed=sorted(b)))
            return
        for k in sorted(a): _compare(a[k],b[k],path+"."+k,differences)
    elif isinstance(a,list) and isinstance(b,list):
        if len(a)!=len(b):
            differences.append(dict(path=path,kind="length",original=len(a),recomputed=len(b)))
            return
        for i,(x,y) in enumerate(zip(a,b)): _compare(x,y,path+f"[{i}]",differences)
    elif type(a) in (int,float) and type(b) in (int,float) and type(a) is not bool and type(b) is not bool:
        if not math.isfinite(a) or not math.isfinite(b) or not math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-10):
            differences.append(dict(path=path,kind="numeric",original=a,recomputed=b,
                relative_tolerance=1e-12,absolute_tolerance=1e-10))
    elif a!=b:
        differences.append(dict(path=path,kind="value",original=a,recomputed=b))

def main(original_path,output_dir):
    original_path=Path(original_path)
    output_dir=Path(output_dir)
    output_dir.mkdir(parents=True,exist_ok=False)
    raw=original_path.read_bytes()
    report=dict(source_archive_run=40386166153,source_archive_artifact=12681955393,
        original_path="gate2/numerical_attempts.json",
        original_file_sha256=hashlib.sha256(raw).hexdigest(),
        command="PYTHONPATH=foundation .venv-foundation/bin/python foundation/wp6/reproduce_unresolved.py ORIGINAL_JSON OUTPUT_DIR",
        comparison_tolerance=dict(relative=1e-12,absolute=1e-10),
        status="inconclusive")
    try:
        attempts=json.loads(raw)
        matched=[a for a in attempts if a["elements"]==2]
        if len(matched)!=1: raise ValueError("Exactly one original two-element case required")
        saved=matched[0]
        if not (saved["status"]=="complete" and saved["numerical_quality"]=="unresolved" and saved["eligible"] is False):
            raise ValueError("Original two-element case is not the required unresolved challenge")
        inputs=RunInputs.model_validate(saved["input"])
        original=Evaluation.model_validate(saved["evaluation"])
        result=evaluate(inputs)
        eligible=numerical_comparison_eligible(result,inputs.brief)
        differences=[]
        _compare(saved["evaluation"],result.model_dump(mode="json"),"evaluation",differences)
        original_input_hash=inputs.content_hash
        report.update(input_hash=original_input_hash,
            serialized_input_sha256=hashlib.sha256(json.dumps(saved["input"],sort_keys=True,separators=(",",":")).encode()).hexdigest(),
            original=dict(status=original.status,numerical_quality=original.numerical_quality,eligible=saved["eligible"],
                          evaluation=saved["evaluation"]),
            recomputed=dict(status=result.status,numerical_quality=result.numerical_quality,eligible=eligible,
                            evaluation=result.model_dump(mode="json")),
            differences=differences)
        valid=(result.status=="complete" and result.numerical_quality=="unresolved"
               and eligible is False and not differences
               and original.input_hash==original_input_hash
               and result.input_hash==original_input_hash)
        report["status"]="pass" if valid else "fail"
    except Exception as exc:
        report["error"]=repr(exc)
        report["status"]="fail"
    (output_dir/"reproduction.json").write_text(json.dumps(report,sort_keys=True,indent=2,default=str)+"\n")
    print(json.dumps({k:report.get(k) for k in ("status","input_hash","original_file_sha256","differences","error")},default=str))
    if report["status"]!="pass": raise SystemExit(1)

if __name__=="__main__":
    if len(sys.argv)!=3: raise SystemExit("Usage: reproduce_unresolved.py ORIGINAL_JSON OUTPUT_DIR")
    main(sys.argv[1],sys.argv[2])
