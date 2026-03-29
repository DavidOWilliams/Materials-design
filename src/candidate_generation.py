from __future__ import annotations
import pandas as pd
from pathlib import Path
from typing import Dict, Any

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def generate_candidates(requirements: Dict[str, Any]) -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "seed_materials.csv")

    df = df[df["material_family"].isin(requirements["allowed_material_families"])].copy()

    if requirements["am_preferred"]:
        preferred = df["am_capable"].astype(str).str.lower() == "yes"
        if preferred.any():
            df = df[preferred].copy()

    df["generated_note"] = "Seeded concept matched to inferred requirements."
    return df.reset_index(drop=True)
