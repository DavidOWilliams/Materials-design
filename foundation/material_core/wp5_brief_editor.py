"""WP5 brief editing boundary: typed validation and immutable, hash-checked snapshots.

This module contains no scientific calculations. Unsupported inputs fail closed.
"""
from __future__ import annotations

import json
from pathlib import Path
from material_core.contracts import Brief


def validate_brief(payload: dict) -> Brief:
    """Validate the complete WP1 brief; never invent omitted scientific fields."""
    if not isinstance(payload, dict):
        raise TypeError("Brief must be a JSON object")
    return Brief.model_validate(payload)


def revise_brief(original: Brief, changes: dict) -> Brief:
    """Create a new brief version, preserving every unchanged typed field."""
    if not isinstance(changes, dict):
        raise TypeError("Changes must be an object")
    if "version" in changes or "kind" in changes:
        raise ValueError("Version and kind are managed by the editor")
    if not changes:
        raise ValueError("Empty revision")
    unknown = set(changes) - set(Brief.model_fields)
    if unknown:
        raise ValueError(f"Unsupported brief fields: {sorted(unknown)}")
    raw = original.model_dump(mode="json")
    raw.update(changes)
    raw["version"] = original.version + 1
    candidate = validate_brief(raw)
    if candidate.model_dump(exclude={"version"}) == original.model_dump(exclude={"version"}):
        raise ValueError("Revision has no semantic changes")
    return candidate


def save_brief(path: str | Path, brief: Brief) -> None:
    """Create an immutable brief snapshot; no overwrite of existing evidence."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    envelope = {"schema": "wp5-brief-v1", "hash": brief.content_hash,
                "brief": brief.model_dump(mode="json")}
    with path.open("x", encoding="utf-8") as handle:
        json.dump(envelope, handle, sort_keys=True, allow_nan=False)
        handle.flush()


def open_brief(path: str | Path) -> Brief:
    envelope = json.loads(Path(path).read_text(encoding="utf-8"))
    if envelope.get("schema") != "wp5-brief-v1":
        raise ValueError("Unsupported brief snapshot schema")
    brief = validate_brief(envelope["brief"])
    if envelope.get("hash") != brief.content_hash:
        raise ValueError("Brief snapshot integrity mismatch")
    return brief
