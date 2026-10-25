"""Append-only checkpoint journal for WP4 candidate artifacts.

Crash recovery is limited to last fully written record; no mid-kernel restart.
A single writer owns the file. This is not a transactional multi-writer store.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path

def digest(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()

class Journal:
    def __init__(self,path):
        self.path=Path(path)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        if self.path.exists():
            raise FileExistsError("WP4 journal is immutable; use recover")
        with self.path.open("x",encoding="utf-8") as f:
            f.flush()
            os.fsync(f.fileno())
        self.previous="0"*64

    def checkpoint(self,records):
        if len(records)!=self.count()+1:
            raise ValueError("Checkpoint must append exactly one candidate")
        record=records[-1]
        payload=dict(sequence=len(records)-1,previous=self.previous,record=record)
        envelope=dict(payload=payload,sha256=digest(payload))
        line=json.dumps(envelope,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n"
        with self.path.open("a",encoding="utf-8") as f:
            f.write(line)
            f.flush()
            os.fsync(f.fileno())
        self.previous=envelope["sha256"]

    def count(self):
        return len(recover(self.path))

def recover(path):
    path=Path(path)
    records=[]
    previous="0"*64
    with path.open("r",encoding="utf-8") as f:
        for line in f:
            if not line.endswith("\n"):
                raise ValueError("Truncated WP4 checkpoint record")
            envelope=json.loads(line)
            payload=envelope["payload"]
            if digest(payload)!=envelope["sha256"] or payload["previous"]!=previous:
                raise ValueError("Corrupt WP4 checkpoint chain")
            if payload["sequence"]!=len(records) or payload["record"]["index"]!=len(records):
                raise ValueError("WP4 checkpoint sequence mismatch")
            records.append(payload["record"])
            previous=envelope["sha256"]
    return records
