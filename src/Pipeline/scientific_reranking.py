from typing import List, Any


def rerank_candidates(candidates: List[Any], query_ctx: Any) -> List[Any]:
    """
    Freeze-phase no-op reranker.

    Important:
    - Do not change survival here.
    - Do not add scoring logic yet.
    - This exists only to isolate baseline filtering from future reranking.
    """
    return candidates