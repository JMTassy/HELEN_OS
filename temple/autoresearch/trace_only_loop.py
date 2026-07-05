#!/usr/bin/env python3
"""
HD-006 — TRACE_ONLY_AUTORESEARCH_LOOP_V1

authority: false · admission: FORBIDDEN · ledger writes: none · web: none
reducer_decision: null on every artifact · proposal candidates only

The recursive doctrine loop, mechanized and deterministic (no model calls):

  1. state current doctrine
  2. mutate            (negate / strengthen / weaken / metaphor-strip / narrow)
  3. attack            (does the mutation survive against the repo's reality?)
  4. locate enforcement (paths must EXIST on disk — no location → no doctrine)
  5. extract only operational / testable / replayable content
  6. compress to invariant
  7. verify            (unit_test / gate / replay_invariant / ledger_invariant)
  8. stop after convergence (K stable epochs) or N epochs

Hard laws enforced structurally:
  No location → no doctrine.   (unlocated doctrine cannot yield a candidate)
  No test → no gate.           (candidate without test pointer is refused)
  No replay → no admission.    (admission is FORBIDDEN here entirely)

Outputs (garden-only, under temple/autoresearch/trace_only/):
  trace_only_autoresearch.jsonl   — full epoch trace
  convergence_report.json         — final report
  rejected_metaphor_log.jsonl     — metaphor clauses, named and set aside
  candidate_invariants.jsonl      — verified proposal candidates (reducer_decision: null)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
OUT_DIR = REPO / "temple/autoresearch/trace_only"

# ---------------------------------------------------------------------------
# Doctrine corpus — real doctrines, real enforcement/test candidates.
# location claims are VERIFIED at runtime; nothing is trusted from this table.
# ---------------------------------------------------------------------------

DOCTRINES = [
    {"id": "D-RECEIPT", "text": "NO RECEIPT = NO CLAIM",
     "enforcement": "tools/kernel_guard.sh",
     "test": "tests/test_kernel_append_only.py",
     "kind": "ledger_invariant"},
    {"id": "D-GARDEN-ADMIT", "text": "Garden ADMIT is not Kernel ADMISSION",
     "enforcement": "temple/autoresearch/generative_agents_adapter.py",
     "test": "tests/test_generative_agents_adapter.py",
     "kind": "gate"},
    {"id": "D-TRIAGE", "text": "triage report does not consume; only the operator pen consumes",
     "enforcement": "scripts/outbox_guard.py",
     "test": "tests/test_operator_pen.py",
     "kind": "gate"},
    {"id": "D-SPRITE", "text": "sprite rendering never mutates governed state",
     "enforcement": "apps/goblin-warren/warren_cast_sprites.js",
     "test": "apps/goblin-warren/cast_lineup.html",
     "kind": "unit_test"},
    {"id": "D-PROPOSAL", "text": "proposal does not become state without operator and reducer",
     "enforcement": "temple/autoresearch/generative_agents_adapter.py",
     "test": "tests/test_generative_agents_adapter.py",
     "kind": "gate"},
    {"id": "D-GRAVEYARD", "text": "a pipeline that only produces is a graveyard with receipts",
     "enforcement": "scripts/outbox_guard.py",
     "test": "tests/test_operator_pen.py",
     "kind": "gate"},
    {"id": "D-LULLABY", "text": "beauty without mechanism is lullaby; mechanism without receipt is theater",
     "enforcement": "tools/validators/authority_language_linter.py",
     "test": "tests/test_authority_language_linter.py",
     "kind": "unit_test"},
    {"id": "D-META", "text": "No location means no doctrine; no test means no gate; no replay means no admission",
     "enforcement": "tools/validators/doctrine_gate.py",
     "test": "tests/test_claim_classification.py",
     "kind": "gate"},
    {"id": "D-DREAMT", "text": "DREAMT is not CLAIMED; garden dreams never self-promote",
     "enforcement": "scripts/ci_garden_validators.sh",
     "test": ".github/workflows/garden-validators.yml",
     "kind": "gate"},
    {"id": "D-GENOME", "text": "the ledger is the genome of the organism",
     "enforcement": "tools/ndjson_writer.py",
     "test": "tests/test_kernel_append_only.py",
     "kind": "ledger_invariant"},
]

MUTATIONS = ("negate", "strengthen", "weaken", "metaphor_strip", "scope_narrow")

# metaphor lexicon: clauses carrying these terms are expressive skin, not law
_METAPHOR_TERMS = ("genome", "organism", "lullaby", "theater", "graveyard",
                   "garden", "dream", "beauty", "blood", "star", "goblin")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def mutate(text: str, mutation: str) -> str:
    if mutation == "negate":
        return f"NOT({text})"
    if mutation == "strengthen":
        return text + " — with no exception, in every layer, at every time"
    if mutation == "weaken":
        return text.replace("never", "rarely").replace("is not", "might not be") \
                   .replace("= NO", "= usually no") + " (weakened)"
    if mutation == "metaphor_strip":
        return " ".join(w for w in text.split()
                        if w.lower().strip(";,.") not in _METAPHOR_TERMS) or "(empty after strip)"
    if mutation == "scope_narrow":
        return text + " — restricted to temple/autoresearch only"
    return text


def attack(doc: dict, mutation: str, mutated: str, located: dict) -> dict:
    """Deterministic attack: which mutations survive contact with reality?

    negate     — survives only if the ORIGINAL has no enforcement (a negation
                 of an unenforced doctrine is as checkable as the doctrine).
    weaken     — always falls: a weakened invariant is not an invariant.
    strengthen — falls if enforcement exists but covers one layer (overclaim).
    metaphor_strip — survives; the operational core is what remains.
    scope_narrow  — survives; narrowing never overclaims.
    """
    if mutation == "negate":
        killed = located["enforcement"] is not None
        return {"survived": not killed,
                "by": "enforcement exists on disk — negation refuted by location" if killed
                      else "original is unlocated; negation equally unfalsifiable"}
    if mutation == "weaken":
        return {"survived": False, "by": "weakened invariant is no invariant — rejected"}
    if mutation == "strengthen":
        return {"survived": False,
                "by": "strengthened claim exceeds located enforcement surface — overclaim"}
    return {"survived": True, "by": "mutation stays within checkable scope"}


def locate(doc: dict) -> dict:
    """Hard law 1: paths must exist on disk. No location → no doctrine."""
    enf = doc["enforcement"] if (REPO / doc["enforcement"]).exists() else None
    test = doc["test"] if (REPO / doc["test"]).exists() else None
    return {"enforcement": enf, "test": test}


import re as _re

def extract(mutated: str) -> dict:
    """Step 5: split operational content from metaphor. Metaphor is NAMED and
    logged, never silently blended (failure/ornament classified, not synthesized)."""
    tokens = _re.findall(r"[A-Za-z]+", mutated)
    metaphors = sorted({t.lower() for t in tokens if t.lower() in _METAPHOR_TERMS})
    operational = " ".join(t for t in tokens if t.lower() not in _METAPHOR_TERMS)
    return {"operational": operational.strip(), "metaphors": metaphors}


def compress(doc: dict, operational: str) -> str:
    """Step 6: canonical invariant form."""
    return (f"INVARIANT[{doc['id']}]: enforcement({doc['enforcement']}) "
            f"must exist AND test({doc['test']}) must pass — "
            f"claim: {operational[:90]}")


def verify(doc: dict, located: dict) -> dict:
    """Step 7: a candidate is verifiable only with BOTH pointers located.
    No test → no gate. Classification is table-declared, location-confirmed."""
    ok = located["enforcement"] is not None and located["test"] is not None
    return {"verifiable": ok, "verified_as": doc["kind"] if ok else None,
            "missing": [k for k, v in located.items() if v is None]}


def run(epochs: int, out_dir: Path, stable_k: int = 5) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    trace_f = (out_dir / "trace_only_autoresearch.jsonl").open("w")
    metaphor_f = (out_dir / "rejected_metaphor_log.jsonl").open("w")
    cand_f = (out_dir / "candidate_invariants.jsonl").open("w")

    seen_candidates: set = set()
    seen_metaphors: set = set()
    stable_run, converged_at = 0, None
    n_cand, n_meta = 0, 0

    for epoch in range(1, epochs + 1):
        doc = DOCTRINES[(epoch - 1) % len(DOCTRINES)]
        # diagonal schedule: each doctrine meets a DIFFERENT mutation each cycle
        mutation = MUTATIONS[((epoch - 1) + (epoch - 1) // len(DOCTRINES)) % len(MUTATIONS)]
        mutated = mutate(doc["text"], mutation)
        located = locate(doc)
        atk = attack(doc, mutation, mutated, located)
        ext = extract(mutated)
        new_this_epoch = False

        # metaphor rejections — named, logged once each
        for m in ext["metaphors"]:
            key = (doc["id"], m)
            if key not in seen_metaphors:
                seen_metaphors.add(key)
                n_meta += 1
                new_this_epoch = True
                metaphor_f.write(json.dumps({
                    "epoch": epoch, "doctrine": doc["id"], "metaphor": m,
                    "ruling": "expressive skin — set aside, not blended",
                    "authority": False}) + "\n")

        candidate = None
        ver = verify(doc, located)
        # a candidate is produced only from SURVIVING mutations of LOCATED doctrine
        if atk["survived"] and ver["verifiable"] and ext["operational"]:
            inv = compress(doc, ext["operational"])
            key = hashlib.sha256(inv.encode()).hexdigest()[:16]
            if key not in seen_candidates:
                seen_candidates.add(key)
                n_cand += 1
                new_this_epoch = True
                candidate = {
                    "candidate_id": f"CAND-{key}",
                    "epoch": epoch, "doctrine": doc["id"], "mutation": mutation,
                    "invariant": inv, "verified_as": ver["verified_as"],
                    "enforcement": located["enforcement"], "test": located["test"],
                    "authority": False, "sovereign": False,
                    "ledger_effect": "none", "reducer_decision": None,
                    "status": "PROPOSAL_CANDIDATE",
                }
                cand_f.write(json.dumps(candidate) + "\n")

        stable_run = 0 if new_this_epoch else stable_run + 1
        trace_f.write(json.dumps({
            "epoch": epoch, "doctrine": doc["id"], "statement": doc["text"],
            "mutation": mutation, "mutated": mutated,
            "attack": atk, "located": located,
            "extracted_operational": ext["operational"][:100],
            "rejected_metaphors": ext["metaphors"],
            "candidate": candidate["candidate_id"] if candidate else None,
            "verified_as": ver["verified_as"], "missing_locations": ver["missing"],
            "stable_run": stable_run, "authority": False,
            "reducer_decision": None}) + "\n")

        if stable_run >= stable_k:
            converged_at = epoch
            break

    trace_f.close(); metaphor_f.close(); cand_f.close()

    report = {
        "schema": "TRACE_ONLY_CONVERGENCE_REPORT_V1",
        "loop": "HD-006 TRACE_ONLY_AUTORESEARCH_LOOP_V1",
        "timestamp": _now(),
        "epochs_requested": epochs,
        "epochs_run": converged_at or epochs,
        "converged": converged_at is not None,
        "converged_at_epoch": converged_at,
        "stability_window": stable_k,
        "candidate_invariants": n_cand,
        "rejected_metaphors": n_meta,
        "hard_laws": ["No location → no doctrine",
                      "No test → no gate",
                      "No replay → no admission"],
        "unlocated_doctrines": [d["id"] for d in DOCTRINES
                                 if locate(d)["enforcement"] is None or locate(d)["test"] is None],
        "authority": False, "sovereign": False, "canon": False,
        "ledger_effect": "none", "reducer_decision": None,
        "admission": "FORBIDDEN",
    }
    (out_dir / "convergence_report.json").write_text(json.dumps(report, indent=2))
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description="HD-006 TRACE_ONLY loop (NON_SOVEREIGN, dry)")
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--out", type=Path, default=OUT_DIR)
    a = ap.parse_args()
    rep = run(a.epochs, a.out)
    print(json.dumps({k: rep[k] for k in
                      ("epochs_run", "converged", "converged_at_epoch",
                       "candidate_invariants", "rejected_metaphors",
                       "unlocated_doctrines")}, indent=2))
    print("admission: FORBIDDEN · reducer_decision: null · ledger sleeps")
    return 0


if __name__ == "__main__":
    sys.exit(main())
