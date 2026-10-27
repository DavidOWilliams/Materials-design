import pytest
from material_core.wp4_feedback import run
from material_core.wp4_journal import Journal,recover

def test_partial_failure_keeps_last_complete_checkpoint(tmp_path):
    path=tmp_path/"partial.jsonl"
    journal=Journal(path)
    def interrupt(rows):
        journal.checkpoint(rows)
        if len(rows)==2: raise RuntimeError("simulated failure after fsync")
    with pytest.raises(RuntimeError,match="simulated"):
        run(elements=256,budget=4,checkpoint=interrupt)
    assert len(recover(path))==2
    assert recover(path)[0]["index"]==0

def test_truncated_checkpoint_rejected(tmp_path):
    path=tmp_path/"partial.jsonl"
    journal=Journal(path)
    run(elements=256,budget=1,checkpoint=journal.checkpoint)
    with path.open("ab") as f:f.write(b'{"partial":')
    with pytest.raises(ValueError,match="Truncated"):
        recover(path)

def test_resealed_single_record_is_not_silent(tmp_path):
    path=tmp_path/"partial.jsonl"
    journal=Journal(path)
    run(elements=256,budget=1,checkpoint=journal.checkpoint)
    text=path.read_text()
    path.write_text(text.replace('"sequence":0','"sequence":1'))
    with pytest.raises(ValueError):
        recover(path)
