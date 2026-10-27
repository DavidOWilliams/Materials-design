"""Append-only assumption versions. Scientific resolution requires recorded evidence.

Snapshots are standalone records: reopening a historic run does not consult the
latest registry. Content hashes cover every record field, including source hash.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from hashlib import sha256
from importlib.resources import files
import json
import math
import re
from typing import Mapping


# Deliberately finite canonical SI vocabulary, extend explicitly with new domains.
ASSUMPTION_UNITS = frozenset({"1", "m", "m2", "m3", "K", "Pa", "s", "kg",
                              "kg/m2", "kg/m3", "W/m2", "W/(m K)", "1/K", "J"})


def _digest(value: object) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False, allow_nan=False).encode()).hexdigest()


@dataclass(frozen=True)
class AssumptionRecord:
    assumption_id: str
    version: int
    exact_question: str
    provisional_answer: str
    value_status: str
    value: float | None
    value_range: tuple[float, float] | None
    unit: str | None
    evidence_basis: str
    affected_calculations: tuple[str, ...]
    sensitivity_consequence: str
    sensitivity_priority: str
    owner: str
    resolution_criterion: str
    status: str
    source_path: str
    source_sha256: str
    schema_version: int = 1

    def __post_init__(self):
        if self.schema_version != 1 or isinstance(self.schema_version, bool):
            raise ValueError("Unsupported assumption schema version")
        if not isinstance(self.assumption_id, str) or not re.fullmatch(r"[A-Z][0-9]{2,}", self.assumption_id):
            raise ValueError("Invalid assumption ID")
        if type(self.version) is not int or self.version < 1:
            raise ValueError("Version must be a positive integer")
        for field in ("exact_question", "provisional_answer", "evidence_basis",
                      "sensitivity_consequence", "sensitivity_priority", "owner",
                      "resolution_criterion", "source_path"):
            if not isinstance(getattr(self, field), str) or not getattr(self, field).strip():
                raise ValueError(f"{field} must be nonempty text")
        if not isinstance(self.source_sha256, str) or not re.fullmatch(r"[a-f0-9]{64}", self.source_sha256):
            raise ValueError("Source SHA256 required")
        if not isinstance(self.affected_calculations, (tuple, list)) or not self.affected_calculations:
            raise ValueError("Affected calculations required")
        if any(not isinstance(x, str) or not x.strip() for x in self.affected_calculations):
            raise ValueError("Affected calculations must be nonempty names")
        object.__setattr__(self, "affected_calculations", tuple(self.affected_calculations))
        if self.status not in ("open", "resolved", "superseded"):
            raise ValueError("Invalid scientific assumption status")
        if self.value_status not in ("unresolved", "specified", "not_applicable"):
            raise ValueError("Invalid assumption value status")
        if self.value_range is not None:
            if not isinstance(self.value_range, (tuple, list)) or len(self.value_range) != 2:
                raise ValueError("Range requires lower and upper bounds")
            object.__setattr__(self, "value_range", tuple(self.value_range))
        numbers = (() if self.value is None else (self.value,)) + (self.value_range or ())
        if any(type(x) not in (int, float) or not math.isfinite(x) for x in numbers):
            raise ValueError("Assumption values must be finite numbers")
        if self.value_status == "specified":
            if (self.value is None) == (self.value_range is None):
                raise ValueError("Specify exactly one value or range")
            if self.unit not in ASSUMPTION_UNITS:
                raise ValueError("Explicit supported SI unit required, including '1' for dimensionless")
            if self.value_range is not None and self.value_range[0] > self.value_range[1]:
                raise ValueError("Invalid range order")
        elif numbers or self.unit is not None:
            raise ValueError("Unknown or inapplicable values must remain null")

    def to_dict(self) -> dict:
        """Return a detached JSON-compatible record with its integrity hash."""
        result = json.loads(json.dumps(asdict(self), allow_nan=False))
        result["content_hash"] = _digest(result)
        return result

    @property
    def content_hash(self) -> str:
        return self.to_dict()["content_hash"]

    @classmethod
    def from_dict(cls, raw: dict) -> AssumptionRecord:
        data = dict(raw)
        supplied_hash = data.pop("content_hash", None)
        record = cls(**data)
        if supplied_hash is not None and supplied_hash != record.content_hash:
            raise ValueError("Assumption snapshot hash mismatch")
        return record


class AssumptionRegistry:
    """In-memory version ledger; serialized run snapshots preserve historical use."""

    def __init__(self, records=()):
        self._records: dict[tuple[str, int], AssumptionRecord] = {}
        for record in records:
            self.add(record)

    def add(self, record: AssumptionRecord) -> None:
        if not isinstance(record, AssumptionRecord):
            raise TypeError("Expected AssumptionRecord")
        key = (record.assumption_id, record.version)
        previous = self._records.get(key)
        if previous is not None and previous != record:
            raise ValueError("Cannot overwrite an existing assumption version")
        self._records[key] = record

    @classmethod
    def from_builtin(cls) -> AssumptionRegistry:
        path = files(__package__).joinpath("data/assumptions_v1.json")
        data = json.loads(path.read_text(encoding="utf-8"))
        if data["schema_version"] != 1:
            raise ValueError("Unsupported registry schema")
        return cls(validate_snapshot(data["assumptions"]))

    def get(self, assumption_id: str, version: int | None = None) -> AssumptionRecord:
        if version is None:
            versions = [v for ident, v in self._records if ident == assumption_id]
            if not versions:
                raise KeyError(f"Unknown assumption {assumption_id}")
            version = max(versions)
        if type(version) is not int:
            raise ValueError("Explicit integer version required")
        return self._records[(assumption_id, version)]

    def snapshot(self, refs: Mapping[str, int] | None = None) -> list[dict]:
        if refs is None:
            refs = {ident: self.get(ident).version for ident, _ in self._records}
        return [self.get(ident, refs[ident]).to_dict() for ident in sorted(refs)]

    def update(self, assumption_id: str, *, expected_version: int, **changes) -> AssumptionRecord:
        current = self.get(assumption_id)
        if type(expected_version) is not int or current.version != expected_version:
            raise ValueError("Stale assumption update; inspect current version")
        if set(changes) & {"assumption_id", "version", "schema_version"}:
            raise ValueError("Assumption identity/version cannot be edited")
        if not changes or all(getattr(current, k) == v for k, v in changes.items()):
            raise ValueError("Update must change an assumption field")
        updated = replace(current, version=current.version + 1, **changes)
        self.add(updated)
        return updated


def validate_snapshot(snapshot: list[dict]) -> tuple[AssumptionRecord, ...]:
    """Validate detached run snapshots without consulting the latest registry."""
    if not isinstance(snapshot, list):
        raise ValueError("Assumption snapshot must be a list")
    records = tuple(AssumptionRecord.from_dict(raw) for raw in snapshot)
    ids = [r.assumption_id for r in records]
    if len(set(ids)) != len(ids):
        raise ValueError("A run may reference only one version of each assumption")
    return records
