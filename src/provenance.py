from __future__ import annotations

import pandas as pd


def _source_provenance(row: pd.Series) -> str:
    source = str(row.get("candidate_source", "materials_project") or "materials_project")
    if source == "engineering_analogue":
        name = str(row.get("source_alloy_name", "") or row.get("matched_alloy_name", "") or "curated alloy analogue")
        refs = str(row.get("source_url_or_ref", "") or "").strip()
        text = (
            f"Curated engineering analogue candidate from the project alloy knowledge table ({name}); "
            "then evaluated using the same downstream factor, recipe, and reranking layers as retrieved candidates."
        )
        if refs:
            text += f" Source reference: {refs}."
        return text
    return (
        "Retrieved from Materials Project summary data, then filtered and labelled using prototype alloy-family rules "
        "and engineering proxy scoring."
    )


def add_provenance(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if len(out) == 0:
        out["provenance"] = []
        return out
    out["provenance"] = out.apply(_source_provenance, axis=1)
    return out
