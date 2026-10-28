from material_core.wp4_feedback import run,save,reopen
def test_cancel_before_first_transform(tmp_path):
    rec=run(elements=256,cancel_requested=lambda:True)
    assert rec["stop_reason"]=="cancelled"
    assert rec["proposals"]==0
    p=tmp_path/"cancel.json"
    save(p,rec)
    assert reopen(p)["records"]==[]

def test_cancel_after_first_evaluation(tmp_path):
    calls=[0]
    def cancelled():
        calls[0]+=1
        return calls[0]>1
    rec=run(elements=256,cancel_requested=cancelled)
    assert rec["stop_reason"]=="cancelled"
    assert rec["proposals"]==1
    p=tmp_path/"partial.json"
    save(p,rec)
    assert len(reopen(p)["records"])==1
