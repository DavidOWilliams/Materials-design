"""WP7 presentation and portable packaging for the accepted WP3 mixed-space ledger.

No scientific calculations, eligibility overrides or WP3 search policies added.
WP3 intended-state numerical search is a different evidence context from WP4
estimated achieved-state manufacturing feedback.
"""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import shutil
import zipfile

from .store import RunStore
from .wp3_search import open_search, recompute_search

MAX_BUNDLE_FILES = 10000
MAX_BUNDLE_BYTES = 100 * 1024 * 1024


def mixed_summary(path):
    """Strictly reopen WP3 durable ledger and related immutable store."""
    path = Path(path)
    ledger = open_search(path)
    rows = []
    for p in ledger["proposals"]:
        values = p.get("objectives", {})
        selection = p.get("proposal") or {}
        rows.append({
            "candidate": p["index"],
            "status": p["status"],
            "architecture": selection.get("architecture", "unavailable"),
            "materials": ", ".join(selection.get("pair", [])),
            "fraction": selection.get("fraction"),
            "thermal_transmission_W_m2": values.get("thermal_transmission"),
            "areal_mass_kg_m2": values.get("areal_mass"),
            "tensile_thermal_mismatch_Pa": values.get("tensile_thermal_mismatch"),
            "numerical_quality": p.get("numerical_quality", "unknown"),
            "qualified_for_numerical_pareto": p.get("qualified") is True,
            "hard_constraint_feasibility": p.get("hard_constraint_feasibility", "unknown"),
            "manufacturing_feasibility": p.get("manufacturing_feasibility", "unknown"),
            "evidence_maturity": p.get("evidence_maturity", "unknown"),
            "reason": p.get("reason") or (
                "Qualified numerically, NOT manufacturing-validated"
                if p.get("qualified") is True else
                "Incomplete, unqualified, infeasible or unresolved numerical evidence"),
        })
    return {
        "ledger": str(path), "rows": rows,
        "pareto": ledger.get("qualified_comparison"),
        "config": ledger["config"], "stop_reason": ledger["stop_reason"],
        "candidate_count": len(rows),
        "scientific_boundary": "Intended-state WP3 numerical qualification only; manufacturing feasibility unknown; not WP4 achieved-state comparison",
        "measured_evidence": None,
    }


def mixed_candidate(path, index):
    ledger = open_search(path)
    if type(index) is not int or not 0 <= index < len(ledger["proposals"]):
        raise ValueError("Invalid candidate index")
    row = ledger["proposals"][index]
    if row["index"] != index:
        raise ValueError("Index mismatch")
    if row["status"] != "complete":
        return {"proposal": row, "evaluation": None, "reason": "Candidate not complete"}
    run = RunStore(Path(path).parent / "run-store").load(row["run_id"])
    if run.evaluation is None:
        raise ValueError("Completed run lost evaluation")
    return {"proposal": row, "intended_design": run.inputs.design.model_dump(mode="json"),
            "brief": run.inputs.brief.model_dump(mode="json"),
            "evaluation": run.evaluation.model_dump(mode="json"),
            "numerical_quality": run.evaluation.numerical_quality,
            "manufacturing_validation": "not_established",
            "measured_evidence": None}


def _source_files(path):
    """Only ledger and actual referenced run store files, not arbitrary neighbours."""
    path = Path(path)
    if path.name != "campaign.json":
        raise ValueError("WP3 portable path must be named campaign.json")
    mixed_summary(path)  # validate evidence and identities before archive
    root = path.parent
    files = [path] + sorted((root / "run-store").rglob("*"))
    files = [p for p in files if p.is_file()]
    if len(files) > MAX_BUNDLE_FILES or any(p.is_symlink() for p in files):
        raise ValueError("Unsupported archive size or symbolic link")
    total = sum(p.stat().st_size for p in files)
    if total > MAX_BUNDLE_BYTES:
        raise ValueError("Archive exceeds 100 MB bounded demo limit")
    return root, files


def export_mixed_zip(path):
    """Return verified portable bytes, including SQLite and hash-addressed artifacts."""
    root, files = _source_files(path)
    payloads = {}
    for p in files:
        rel = p.relative_to(root).as_posix()
        data = p.read_bytes()
        payloads[rel] = data
    hashes = {k: hashlib.sha256(v).hexdigest() for k, v in payloads.items()}
    manifest = {
        "schema": "wp7-wp3-portable-v1",
        "files": hashes,
        "source_type": "WP3 intended-state synthetic numerical ledger",
        "manufacturing_validation": "not_established",
        "measured_evidence": None,
    }
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("SHA256SUMS.json", json.dumps(manifest, sort_keys=True, indent=2))
        for name, content in sorted(payloads.items()):
            z.writestr(name, content)
    return buffer.getvalue()


def import_mixed_zip(contents, destination):
    """Closed-world ZIP import and verification. Never overwrite destination."""
    destination = Path(destination)
    if destination.exists():
        raise FileExistsError("WP3 destination already exists")
    if not isinstance(contents, bytes) or len(contents) > MAX_BUNDLE_BYTES:
        raise ValueError("Invalid or oversized WP3 evidence archive")
    payloads = {}
    with zipfile.ZipFile(io.BytesIO(contents)) as z:
        members = z.infolist()
        names = [x.filename for x in members]
        if len(names) != len(set(names)) or len(names) > MAX_BUNDLE_FILES + 1:
            raise ValueError("Duplicate or excessive archive members")
        if "SHA256SUMS.json" not in names:
            raise ValueError("Missing WP7 archive manifest")
        manifest = json.loads(z.read("SHA256SUMS.json"))
        if manifest.get("schema") != "wp7-wp3-portable-v1" or not isinstance(manifest.get("files"), dict):
            raise ValueError("Unsupported archive manifest")
        if set(names) != set(manifest["files"]) | {"SHA256SUMS.json"}:
            raise ValueError("Archive membership inconsistent with manifest")
        if "campaign.json" not in manifest["files"] or "run-store/runs.sqlite3" not in manifest["files"]:
            raise ValueError("Missing compulsory WP3 dossier evidence")
        total = 0
        for entry in members:
            if entry.filename == "SHA256SUMS.json":
                continue
            parts = PurePosixPath(entry.filename)
            if parts.is_absolute() or ".." in parts.parts or (
                entry.filename != "campaign.json" and parts.parts[0] != "run-store"):
                raise ValueError("Unsafe archive path")
            total += entry.file_size
            if total > MAX_BUNDLE_BYTES:
                raise ValueError("Expanded archive exceeds limit")
            data = z.read(entry)
            if hashlib.sha256(data).hexdigest() != manifest["files"][entry.filename]:
                raise ValueError("Archive checksum mismatch")
            payloads[entry.filename] = data
    destination.mkdir(parents=True)
    try:
        for name, data in payloads.items():
            p = destination / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
        mixed_summary(destination / "campaign.json")
        result = recompute_search(destination / "campaign.json")
        if result["replay"] != "passed":
            raise ValueError("Numerical archive recomputation failed")
        return result
    except BaseException:
        shutil.rmtree(destination)
        raise
