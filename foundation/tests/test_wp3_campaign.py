"""Retired v1 API cannot be used to launder historical campaign evidence."""
import json
import subprocess
import sys
from pathlib import Path
import pytest
from material_core.wp3_campaign import run_campaign,reopen_campaign,read_legacy_unvalidated


def test_legacy_public_execution_and_reopen_fail_closed(tmp_path):
    path=tmp_path/"v1.json"
    with pytest.raises(RuntimeError,match="retired"):
        run_campaign(path,seed=17,evaluation_budget=1)
    with pytest.raises(RuntimeError,match="retired"):
        reopen_campaign(path)
    raw=dict(schema_version=1,unique_evaluations=999,
             qualified_comparison={"pareto_ids":["invented"]},proposals=[])
    path.write_text(json.dumps(raw))
    with pytest.raises(RuntimeError,match="retired"):
        reopen_campaign(path)
    result=read_legacy_unvalidated(path)
    assert result["validation_status"]=="UNVALIDATED_LEGACY_V1"
    assert not result["review_eligible"]
    assert result["historical_record"]==raw


def test_legacy_cli_refuses_normal_replay_and_labels_historical_read(tmp_path):
    path=tmp_path/"legacy.json"
    path.write_text(json.dumps({"schema_version":1,"unique_evaluations":999,
                                 "qualified_comparison":{"pareto_ids":["invented"]}}))
    module=[sys.executable,"-m","material_core.wp3_campaign","--ledger",str(path)]
    import os
    env=dict(os.environ)
    env["PYTHONPATH"]=str(Path(__file__).resolve().parents[1])
    denied=subprocess.run(module,capture_output=True,text=True,env=env)
    assert denied.returncode!=0 and "retired" in denied.stderr
    historical=subprocess.run(module+["--legacy-read-unvalidated"],
                              capture_output=True,text=True,env=env,check=True)
    assert json.loads(historical.stdout)["review_eligible"] is False
