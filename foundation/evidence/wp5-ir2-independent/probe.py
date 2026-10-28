import json, tempfile, hashlib
from pathlib import Path
from material_core.wp5_service import execute_journal,recover_journal,replay,prepared_inputs
from material_core.wp4_journal import recover
results=[]
with tempfile.TemporaryDirectory() as d:
    root=Path(d)
    for i,value in enumerate([0,-1,True,False,1.0,1.5,'1',None]):
        p=root/str(i)/'nested'/'journal.jsonl'
        try: execute_journal(p,budget=value)
        except ValueError as e: error=str(e)
        else: raise AssertionError('Accepted invalid budget')
        assert list(root.iterdir())==[]
        results.append(dict(value=repr(value),type=type(value).__name__,error=error,no_files_or_directories=True))
    p=root/'retry'/'journal.jsonl'
    try: execute_journal(p,budget=0)
    except ValueError: pass
    assert list(root.iterdir())==[]
    r=execute_journal(p,budget=2,cancel_requested=lambda:len(recover(p))>=1)
    assert r['stop_reason']=='cancelled' and len(recover(p))==1
    out=root/'recovered.json'
    r=recover_journal(p,out)
    assert r['accounting']['reused_candidates']==1
    assert replay(out)['status']=='passed'
    before={str(x):hashlib.sha256(x.read_bytes()).hexdigest() for x in root.rglob('*') if x.is_file()}
    try: execute_journal(p,budget=2)
    except FileExistsError: pass
    else: raise AssertionError('Overwrite accepted')
    assert before=={str(x):hashlib.sha256(x.read_bytes()).hexdigest() for x in root.rglob('*') if x.is_file()}
    results.append(dict(valid_retry=True,cancelled_after_one=True,reused_candidates=1,replay='passed',overwrite_unchanged=True))
    brief=prepared_inputs().brief.model_dump(mode='json');brief['evaluation_budget']=2
    p=root/'mismatch'/'journal.jsonl'
    before=set(root.rglob('*'))
    try: execute_journal(p,budget=1,brief=brief)
    except ValueError: pass
    else: raise AssertionError('Mismatch accepted')
    assert before==set(root.rglob('*'))
    results.append(dict(saved_brief_mismatch_no_files=True))
print(json.dumps(results,indent=2))
