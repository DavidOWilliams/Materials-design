"""SQLite run metadata with immutable, SHA-256 addressed JSON artifacts.

Every boundary revalidates serialized contracts (including model_copy outputs).
Artifacts are installed before the metadata transaction commits. A crash may leave
an unreferenced artifact, but never an acknowledged row pointing at an unwritten
file. Created, failed and incomplete runs are retained. This is a local prototype
store, not a multi-user access-control or archival authenticity service.
"""
from __future__ import annotations
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import re
import sqlite3
import tempfile
import uuid

from pydantic import ValidationError
from .contracts import DecisionRecord, Evaluation, RunInputs


class StoreError(RuntimeError):
    """Run store operation failed without manufacturing a successful result."""


class ArtifactIntegrityError(StoreError):
    """Missing, corrupted or invalid immutable artifact."""


class StateTransitionError(StoreError):
    """Attempt to replace a terminal result or otherwise violate run state."""


class UnsupportedStoreVersion(StoreError):
    """Future store schemas must be migrated explicitly, never silently reset."""


@dataclass(frozen=True)
class StoredRun:
    run_id: str
    input_hash: str
    inputs: RunInputs
    evaluation: Evaluation | None
    status: str
    parent_run_id: str | None
    failure_reason: str | None
    created_at: str
    finished_at: str | None


def _now():
    return datetime.now(timezone.utc).isoformat()


class RunStore:
    SCHEMA_VERSION = 1
    TERMINAL = {'complete', 'incomplete', 'unsupported', 'failed'}

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)
        self.artifacts = self.path / 'artifacts'
        self.artifacts.mkdir(exist_ok=True)
        self.database = self.path / 'runs.sqlite3'
        with self._connection() as db:
            version = db.execute('PRAGMA user_version').fetchone()[0]
            tables = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            if version == 0 and tables:
                raise UnsupportedStoreVersion('Unversioned nonempty database; refusing initialization')
            if version not in (0, self.SCHEMA_VERSION):
                raise UnsupportedStoreVersion(f'Unsupported store schema {version}')
            if version == 0:
                db.executescript('''
                    BEGIN IMMEDIATE;
                    CREATE TABLE runs (
                        run_id TEXT PRIMARY KEY,
                        input_hash TEXT NOT NULL,
                        result_hash TEXT,
                        status TEXT NOT NULL CHECK(status IN
                            ('created','complete','incomplete','unsupported','failed')),
                        parent_run_id TEXT REFERENCES runs(run_id),
                        failure_reason TEXT,
                        created_at TEXT NOT NULL,
                        finished_at TEXT,
                        record_version INTEGER NOT NULL CHECK(record_version=1)
                    );
                    CREATE INDEX runs_by_input ON runs(input_hash);
                    CREATE TABLE decisions (
                        decision_id TEXT PRIMARY KEY,
                        artifact_hash TEXT NOT NULL,
                        record_version INTEGER NOT NULL CHECK(record_version=1)
                    );
                    PRAGMA user_version=1;
                    COMMIT;
                ''')

    @contextmanager
    def _connection(self):
        db = sqlite3.connect(self.database, timeout=30)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        db.execute('PRAGMA synchronous=FULL')
        try:
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    def artifact_path(self, digest: str) -> Path:
        if not isinstance(digest, str) or re.fullmatch(r'[a-f0-9]{64}', digest) is None:
            raise ArtifactIntegrityError('Invalid artifact digest in metadata')
        return self.artifacts / (digest + '.json')

    def _write_artifact(self, model):
        data = model.canonical_json().encode('utf-8')
        digest = hashlib.sha256(data).hexdigest()
        target = self.artifact_path(digest)
        if target.exists():
            if target.read_bytes() != data:
                raise ArtifactIntegrityError(f'Existing artifact corrupted: {digest}')
            return digest
        # A hard link atomically installs without overwriting another writer.
        fd, temporary = tempfile.mkstemp(prefix='.pending-', dir=self.artifacts)
        try:
            with os.fdopen(fd, 'wb') as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            try:
                os.link(temporary, target)
            except FileExistsError:
                if target.read_bytes() != data:
                    raise ArtifactIntegrityError(f'Concurrent artifact mismatch: {digest}')
            directory = os.open(self.artifacts, os.O_RDONLY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        finally:
            os.unlink(temporary)
        return digest

    def _read_artifact(self, digest, model_type):
        path = self.artifact_path(digest)
        try:
            raw = path.read_bytes()
        except OSError as error:
            raise ArtifactIntegrityError(f'Missing or unreadable artifact: {digest}') from error
        if hashlib.sha256(raw).hexdigest() != digest:
            raise ArtifactIntegrityError(f'Artifact checksum mismatch: {digest}')
        try:
            model = model_type.model_validate_json(raw)
        except (ValueError, TypeError, ValidationError) as error:
            raise ArtifactIntegrityError(f'Invalid or unsupported artifact schema: {digest}') from error
        if model.content_hash != digest:
            raise ArtifactIntegrityError(f'Noncanonical artifact: {digest}')
        return model

    def create(self, inputs: RunInputs, parent_run_id: str | None = None) -> str:
        if not isinstance(inputs, RunInputs):
            raise TypeError('Expected RunInputs')
        inputs = RunInputs.model_validate_json(inputs.canonical_json())
        if parent_run_id is not None:
            parent = self.load(parent_run_id)
            if (inputs.design.content_hash != parent.inputs.design.content_hash
                    and parent.inputs.design.content_hash not in inputs.design.parent_hashes):
                raise ValueError('Changed design must retain parent design hash')
        digest = self._write_artifact(inputs)
        run_id = uuid.uuid4().hex
        with self._connection() as db:
            db.execute('''INSERT INTO runs
                (run_id,input_hash,status,parent_run_id,created_at,record_version)
                VALUES (?,?,'created',?,?,1)''', (run_id,digest,parent_run_id,_now()))
        return run_id

    @staticmethod
    def _validate_result(inputs, evaluation):
        if evaluation.input_hash != inputs.content_hash:
            raise ValueError('Evaluation input identity does not match run')
        if evaluation.brief_hash != inputs.brief.content_hash:
            raise ValueError('Evaluation brief identity does not match run')
        if evaluation.solver != inputs.solver:
            raise ValueError('Evaluation solver identity does not match run')
        objectives = {o.id:o for o in inputs.brief.objectives}
        metrics = {m.objective_id:m for m in evaluation.metrics}
        if set(metrics) - set(objectives):
            raise ValueError('Result contains an unrequested objective')
        if evaluation.status == 'complete' and set(metrics) != set(objectives):
            raise ValueError('Complete result must contain every requested objective')
        for key, metric in metrics.items():
            objective = objectives[key]
            if metric.value is not None and (metric.value.dimension,metric.value.unit) != (objective.dimension,objective.unit):
                raise ValueError('Result units differ from requested objective')

    def finish(self, run_id: str, evaluation: Evaluation) -> None:
        if not isinstance(evaluation, Evaluation):
            raise TypeError('Expected Evaluation')
        evaluation = Evaluation.model_validate_json(evaluation.canonical_json())
        run = self.load(run_id)
        self._validate_result(run.inputs, evaluation)
        digest = self._write_artifact(evaluation)
        with self._connection() as db:
            cursor = db.execute('''UPDATE runs SET result_hash=?,status=?,finished_at=?
                WHERE run_id=? AND status='created' ''',
                (digest,evaluation.status,_now(),run_id))
            if cursor.rowcount != 1:
                raise StateTransitionError('Only a created run can receive one terminal evaluation')

    def fail(self, run_id: str, reason: str) -> None:
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError('Failure reason is required')
        self.load(run_id)  # Fail clearly if the input artifact is no longer readable.
        with self._connection() as db:
            cursor = db.execute('''UPDATE runs SET status='failed',failure_reason=?,finished_at=?
                WHERE run_id=? AND status='created' ''', (reason,_now(),run_id))
            if cursor.rowcount != 1:
                raise StateTransitionError('Only a created run can be marked failed')

    def load(self, run_id: str) -> StoredRun:
        with self._connection() as db:
            row = db.execute('SELECT * FROM runs WHERE run_id=?',(run_id,)).fetchone()
        if row is None:
            raise KeyError(f'Unknown run {run_id}')
        if row['record_version'] != 1:
            raise UnsupportedStoreVersion('Unsupported run record version')
        status = row['status']
        if status not in self.TERMINAL | {'created'}:
            raise ArtifactIntegrityError('Invalid run state metadata')
        inputs = self._read_artifact(row['input_hash'], RunInputs)
        evaluation = None
        if row['result_hash'] is not None:
            evaluation = self._read_artifact(row['result_hash'], Evaluation)
            try:
                self._validate_result(inputs, evaluation)
            except ValueError as error:
                raise ArtifactIntegrityError('Result/input identity mismatch') from error
            if evaluation.status != status:
                raise ArtifactIntegrityError('Result/run status mismatch')
        if status == 'created':
            if evaluation is not None or row['finished_at'] is not None or row['failure_reason'] is not None:
                raise ArtifactIntegrityError('Created run has terminal metadata')
        elif row['finished_at'] is None:
            raise ArtifactIntegrityError('Terminal run lacks completion timestamp')
        elif evaluation is None and (status != 'failed' or not row['failure_reason']):
            raise ArtifactIntegrityError('Terminal run lacks result or explicit failure')
        return StoredRun(run_id,row['input_hash'],inputs,evaluation,status,
                         row['parent_run_id'],row['failure_reason'],row['created_at'],row['finished_at'])

    def find_complete(self, input_hash: str) -> tuple[StoredRun,...]:
        """Integrity-checked cache candidates; stale assumptions create other keys."""
        self.artifact_path(input_hash)
        with self._connection() as db:
            rows = db.execute("SELECT run_id FROM runs WHERE input_hash=? AND status='complete' ORDER BY created_at,run_id",(input_hash,)).fetchall()
        return tuple(self.load(row['run_id']) for row in rows)

    def save_decision(self, record: DecisionRecord) -> str:
        record = DecisionRecord.model_validate_json(record.canonical_json())
        for run_id in record.compared_run_ids:
            self.load(run_id)
        digest = self._write_artifact(record)
        with self._connection() as db:
            existing = db.execute('SELECT artifact_hash FROM decisions WHERE decision_id=?',(record.id,)).fetchone()
            if existing is not None:
                if existing['artifact_hash'] != digest:
                    raise StateTransitionError('Decision records are immutable; use a new decision ID')
                return digest
            db.execute('INSERT INTO decisions VALUES (?,?,1)',(record.id,digest))
        return digest

    def load_decision(self, decision_id: str) -> DecisionRecord:
        with self._connection() as db:
            row = db.execute('SELECT * FROM decisions WHERE decision_id=?',(decision_id,)).fetchone()
        if row is None:
            raise KeyError(f'Unknown decision {decision_id}')
        if row['record_version'] != 1:
            raise UnsupportedStoreVersion('Unsupported decision record version')
        record = self._read_artifact(row['artifact_hash'], DecisionRecord)
        if record.id != decision_id:
            raise ArtifactIntegrityError('Decision identity mismatch')
        return record
