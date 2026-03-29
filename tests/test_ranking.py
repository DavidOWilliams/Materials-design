import pandas as pd
from src.ranking import rank_candidates

def test_rank_candidates():
    df = pd.DataFrame({"overall_score": [50, 80, 65]})
    top, near = rank_candidates(df)
    assert top.iloc[0]["overall_score"] == 80
    assert len(near) >= 1
