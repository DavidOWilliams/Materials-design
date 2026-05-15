import pandas as pd

from src.ranking import rank_candidates


def test_rank_candidates_orders_top_by_overall_score_when_no_final_rank():
    df = pd.DataFrame({"overall_score": [50, 80, 65]})

    top, near = rank_candidates(df)

    assert top.iloc[0]["overall_score"] == 80
    assert len(top) == 3
    assert near.empty


def test_rank_candidates_returns_near_miss_from_remainder():
    df = pd.DataFrame({"overall_score": [95, 90, 85, 80, 75, 65, 40]})

    top, near = rank_candidates(df)

    assert len(top) == 5
    assert top["overall_score"].tolist() == [95, 90, 85, 80, 75]
    assert len(near) >= 1
    assert 65 in near["overall_score"].tolist()


def test_rank_candidates_prefers_final_rank_score_when_present():
    df = pd.DataFrame(
        {
            "overall_score": [90, 10, 30],
            "final_rank_score": [10, 90, 30],
        }
    )

    top, near = rank_candidates(df)

    assert top.iloc[0]["final_rank_score"] == 90
    assert top.iloc[0]["overall_score"] == 10
    assert near.empty