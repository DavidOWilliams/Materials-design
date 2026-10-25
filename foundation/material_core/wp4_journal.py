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

def resume(path, *, elements=4096,mass_limit=31.,layer=.005,feed=.25,budget=4,
           feedback=True,route="synthetic_ideal_planar_deposition"):
    """Deterministic full recomputation with prefix verification and append.

    This re-evaluates already completed candidates; it does not resume a solver
    kernel or skip numerical cost. It refuses any mismatched historical prefix.
    """
    from .wp4_feedback import run
    path=Path(path)
    prior=recover(path)
    if len(prior)>budget:
        raise ValueError("Journal exceeds resumed budget")
    journal=object.__new__(Journal)
    journal.path=path
    journal.previous="0"*64
    if prior:
        with path.open(encoding="utf-8") as f:
            for line in f:
                journal.previous=json.loads(line)["sha256"]
    def checkpoint(records):
        index=len(records)-1
        if index<len(prior):
            if digest(records[-1])!=digest(prior[index]):
                raise ValueError("Recomputed prefix differs from immutable journal")
        else:
            journal.checkpoint(records)
    result=run(elements=elements,mass_limit=mass_limit,layer=layer,feed=feed,
        budget=budget,feedback=feedback,route=route,checkpoint=checkpoint)
    if len(result["records"])<len(prior):
        raise ValueError("Resumed run ended before historical prefix")
    return result
