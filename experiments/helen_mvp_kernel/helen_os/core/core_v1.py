"""HELEN_CORE_V1 — the constitution spine as executable typing. 🔵 OBSERVED · authority=0.

The doctrine surface is overgrown (~78k lines measured @ 8a11fd1). This module makes the compact
spine machine-checkable: it loads HELEN_CORE_V1.json and enforces the promotion rules that keep
"status" a typed property, not prose. The core law: a claim cannot upgrade its epistemic status
without earning it — candidate ⊬ stable, reported ⊬ proven, render ⊬ admission, memory ⊬ replay.

This is a navigation spine, NOT canon and NOT a replacement for the full registry.
Determinism: pure functions over declared claim fields; no clock, no io beyond loading the JSON.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path

_SPINE_PATH = Path(__file__).resolve().parent / "HELEN_CORE_V1.json"


def load_spine(path: Path = _SPINE_PATH) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


class Status(IntEnum):
    HYPOTHESIS = 1        # written / claimed
    REPORTED = 2          # an implementation is reported, unverified here
    FIXTURE_GREEN = 3     # a falsifier suite runs green
    FRAME_BOUND_PASS = 4  # green AND bound to a witnessed frame
    TRANSPORTED = 5       # VALID_BY_TRANSPORT (C16) — distinct provenance from FRESH (I09)
    ADMITTED = 6          # routed through the ledger; replayable


class Kind(IntEnum):
    NORMAL = 0
    RENDER = 1     # a shell/projection surface — I10: render != authority
    MEMORY = 2     # a recall substrate — I10: memory != ledger
    RUNTIME = 3    # a live-state report — subject to staleness (I03)


@dataclass(frozen=True)
class Claim:
    id: str
    module: str
    status: Status
    kind: Kind
    frame_id: str
    has_witness: bool
    has_contradiction_check: bool
    evidence_ref: str = ""      # a fixture / frame proof; "" means unproven


def is_stable(c: Claim, current_frame: str) -> bool:
    """Stable = frame-bound-pass-or-higher AND in the current frame. Candidates are never stable."""
    return c.status >= Status.FRAME_BOUND_PASS and c.frame_id == current_frame


def is_live(c: Claim, current_frame: str) -> bool:
    """A RUNTIME report is live only in its own frame; a report from another frame is stale (I03)."""
    if c.kind == Kind.RUNTIME:
        return c.frame_id == current_frame
    return True


def can_promote(c: Claim, target: Status, current_frame: str):
    """The typed-status gate. Returns (allowed, reason). Fail-closed on every missing witness."""
    if target <= c.status:
        return False, "NOT_A_PROMOTION"
    # any promotion out of the candidate band (>= FIXTURE_GREEN) needs a contradiction check first
    if target >= Status.FIXTURE_GREEN and not c.has_contradiction_check:
        return False, "MISSING_CONTRADICTION_HOLD"
    # reported -> proven requires actual evidence, not a report
    if target >= Status.FIXTURE_GREEN and not c.evidence_ref:
        return False, "REPORTED_NOT_PROVEN"
    # frame-bound / transported / admitted require an independent witness
    if target >= Status.FRAME_BOUND_PASS and not c.has_witness:
        return False, "NO_WITNESS"
    # a stale-framed claim cannot be promoted to a current-frame status
    if target >= Status.FRAME_BOUND_PASS and c.frame_id != current_frame:
        return False, "STALE_FRAME"
    # admission is the ledger's alone: render and memory can never reach it
    if target == Status.ADMITTED and c.kind == Kind.RENDER:
        return False, "RENDER_NOT_ADMISSION"
    if target == Status.ADMITTED and c.kind == Kind.MEMORY:
        return False, "MEMORY_NOT_REPLAY"
    return True, "PROMOTED"


def module_names(spine: dict) -> list:
    return [m["name"] for m in spine["modules"]]


def invariant_ids(spine: dict) -> list:
    return [i["id"] for i in spine["invariants"]]
