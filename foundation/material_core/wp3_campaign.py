"""Retired WP3 v1 campaign entry point.

Schema-1 campaign artifacts are preserved read-only but cannot meet the integrity
guarantees of schema-2 WP3 search. They are NEVER marked verified. Use
material_core.wp3_search for all new campaigns and qualified replay.
"""
from __future__ import annotations
import json
import os
from pathlib import Path


def _write_ledger(path: Path, ledger: dict):
    """Shared atomic journal writer, kept for current WP3 search."""
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix(".pending")
    with temporary.open("w",encoding="utf8") as f:
        json.dump(ledger,f,indent=2,sort_keys=True,allow_nan=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(temporary,path)


def read_legacy_unvalidated(path):
    """Historical bytes only: explicit non-validation, no numerical endorsement."""
    ledger=json.loads(Path(path).read_text(encoding="utf8"))
    if ledger.get("schema_version")!=1:
        raise ValueError("Not a historical schema-1 WP3 campaign")
    return {"validation_status":"UNVALIDATED_LEGACY_V1",
            "review_eligible":False,
            "migration":"Rerun using python -m material_core.wp3_search --ledger NEW_PATH",
            "historical_record":ledger}


def _retired(*args,**kwargs):
    raise RuntimeError(
        "WP3 schema-1 campaign interface retired: no integrity/accounting guarantee. "
        "For new work use material_core.wp3_search.run_search/open_search; "
        "for historical viewing use read_legacy_unvalidated (NOT review evidence).")


run_campaign=_retired
reopen_campaign=_retired


def main():
    import argparse
    p=argparse.ArgumentParser(description="Retired WP3 campaign; use wp3_search")
    p.add_argument("--ledger",required=True)
    p.add_argument("--legacy-read-unvalidated",action="store_true")
    args=p.parse_args()
    if not args.legacy_read_unvalidated:
        _retired()
    print(json.dumps(read_legacy_unvalidated(args.ledger),sort_keys=True))


if __name__=="__main__":
    main()
