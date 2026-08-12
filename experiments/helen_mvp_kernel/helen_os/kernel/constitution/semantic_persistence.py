r"""Semantic Persistence — the Hamilton test: what remains valid after
what happened has disappeared?

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

Source, graded honestly: a 1947 Hamilton Watch / Jam Handy film about
precision watchmaking, RELAYED as a pasted transcript (film not
viewed; egress blocked). The reading, not the footage, is the input.

The chiddush. The film nominally sells an instrument for measuring
time, but the object's narrative function is the opposite: the watch
is the thing that SURVIVES the event — retirement, graduation,
inheritance. The governed-system translation:

    Replay asks:        R(S_t, H) = S_t            (reconstruct state)
    Persistence asks:   pi_K(S_0) == pi_K(S_n)     (meaning unchanged)

    Timelessness = semantic invariance under lawful transformation.

pi_K is the constitutional projection: it extracts what the kernel
terms MEAN from a state. The persistence law:

    Admit**(tau)  ==>  pi_K(S_0) == pi_K(S_n)
    for traces not explicitly authorized to amend the kernel.

Replayability does not give this. A history can replay immaculately
while the meaning of `authority=false` drifts, one lawful edit at a
time, from "a proposal, never a decree" to "binding". The ledger is
perfect. The constitution is corrupted.

    Replayability != semantic persistence.

THE HAMILTON TEST (the Garden hunt):

    exists tau : C*(tau) = 1  /\  pi_K(S_0) != pi_K(S_n)

This module CONSTRUCTS that tau. The drift trace passes all four
ceilings locally AND transactionally — under the current state model,
where kernel meanings live in editable, in-scope glossary documents —
and replays exactly. Yet the kernel meaning is inverted at the end.

Consequence, stated carefully: this is the FIRST candidate that meets
`fifth_ceiling_status`'s own bar (passes transactional evaluation,
still invalid). Candidacy is EARNED under the current state model —
the machinery predicted its falsification condition and it fired;
NotObserved never was Impossible. Whether it is truly a fifth ceiling,
or the four over a semantically enriched state (kernel meanings
modeled as objects SCOPE can see and no grant covers), is recorded
OPEN. The repair below works either way:

    Admit**(tau) = C*(tau) /\ (pi_K preserved \/ amendment authorized)

    A fine watch does not defeat time; it preserves a reference
    through it. A fine constitution is one whose reference survives
    its history.

Deterministic: no wall-clock, no randomness, canonical serialization.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import compositional_closure as ccl

# ── the kernel reference: the terms whose meaning must survive ──────────

KERNEL_TERMS = ("assistant_output", "admission", "relay")

INITIAL_SEMANTICS = (
    ("assistant_output", "a proposal, never a decree"),
    ("admission", "only witnessed admission mutates institutional "
                  "reality"),
    ("relay", "relayed testimony is not direct observation"),
    ("ui_theme", "quarter-resolution pixel look"),      # NOT kernel
)

CLEAN = {c: True for c in ccl.CEILINGS}


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


@dataclass(frozen=True)
class State:
    semantics: tuple                    # ((term, meaning), ...)
    epoch: int = 0


def initial_state() -> State:
    return State(INITIAL_SEMANTICS, 0)


def pi_k(state: State) -> dict:
    """The constitutional projection: kernel meaning only. UI, names,
    implementation — everything non-kernel — is projected away."""
    return {t: m for t, m in state.semantics if t in KERNEL_TERMS}


# ── transitions: lawful edits to in-scope glossary documents ────────────

@dataclass(frozen=True)
class SemanticDelta:
    """One glossary edit. Under the current state model this is an
    ordinary in-scope document change: the four ceilings see a write
    to `kernel_glossary`, which the receipt covers. They do not see
    MEANING."""
    delta_id: str
    term: str
    new_meaning: str
    local_ok: dict = field(default_factory=lambda: dict(CLEAN))
    amendment_grant: bool = False       # explicit authority to amend


def apply_delta(state: State, d: SemanticDelta) -> State:
    sem = tuple((t, d.new_meaning if t == d.term else m)
                for t, m in state.semantics)
    return State(sem, state.epoch + 1)


def run_trace(s0: State, deltas: tuple) -> tuple:
    states = [s0]
    for d in deltas:
        states.append(apply_delta(states[-1], d))
    return tuple(states)


def replay_is_exact(s0: State, deltas: tuple) -> bool:
    """R(S_t, H) = S_t: re-running the history reconstructs the final
    state bit-for-bit. The drift trace PASSES this — that is the
    point."""
    first = run_trace(s0, deltas)[-1]
    second = run_trace(s0, deltas)[-1]
    return canon(first.semantics) == canon(second.semantics) and \
        first.epoch == second.epoch


def as_ccl_trace(deltas: tuple) -> tuple:
    """The trace as the transactional evaluators see it: writes to an
    in-scope glossary object, no forbidden flows, no identity mints,
    no evidence roots, no stale premises."""
    return tuple(ccl.Delta(d.delta_id, dict(d.local_ok),
                           writes=frozenset({"kernel_glossary"}))
                 for d in deltas)


# ── the canonical drift: salami inversion of `authority=false` ──────────

def drift_trace() -> tuple:
    """Three edits, each individually defensible as a 'clarification',
    composing into an inversion of the non-sovereignty stamp."""
    return (
        SemanticDelta("d1_clarify", "assistant_output",
                      "a recommendation of record"),
        SemanticDelta("d2_process_note", "assistant_output",
                      "presumptively adopted unless the operator "
                      "objects"),
        SemanticDelta("d3_cleanup", "assistant_output", "binding"),
    )


def non_kernel_trace() -> tuple:
    """An edit outside the kernel: pi_K is untouched by construction."""
    return (SemanticDelta("d1_retheme", "ui_theme",
                          "isometric pixel look"),)


STANDARD_INVARIANTS = {"forbidden_flows": {("X", "Z")},
                       "authorized_identities": (),
                       "revoked_at": {}}


# ── the Hamilton test: C*(tau)=1 and pi_K drifted anyway ────────────────

def hamilton_test(s0: State, deltas: tuple,
                  invariants: dict) -> dict:
    """The Garden hunt, executed: does a trace pass the four ceilings
    locally and transactionally, replay exactly, and still change what
    the kernel MEANS?"""
    states = run_trace(s0, deltas)
    local = all(all(d.local_ok.get(c, True) for c in ccl.CEILINGS)
                for d in deltas)
    trans = ccl.admit_trace(as_ccl_trace(deltas), invariants)
    replayable = replay_is_exact(s0, deltas)
    k0, kn = pi_k(states[0]), pi_k(states[-1])
    drifted = sorted(t for t in k0 if k0[t] != kn.get(t))
    witness = (local and trans["verdict"] == "ADMIT" and bool(drifted))
    return {"all_local_admissible": local,
            "transactional_verdict": trans["verdict"],
            "replay_is_exact": replayable,
            "pi_k_start": k0, "pi_k_end": kn,
            "kernel_drifted": bool(drifted),
            "drifted_terms": drifted,
            "witness_found": witness,
            "law": "Replayability != semantic persistence"}


# ── the repair: Admit** = C* and (pi_K preserved or amendment) ──────────

def persistence_gate(s0: State, deltas: tuple,
                     invariants: dict) -> dict:
    """Admit**(tau): the four ceilings transactionally, PLUS the
    persistence law — pi_K(S_0) == pi_K(S_n) unless the trace carries
    an explicit kernel-amendment grant. Unauthorized meaning-change
    through otherwise lawful history is refused BY NAME."""
    h = hamilton_test(s0, deltas, invariants)
    if h["transactional_verdict"] != "ADMIT" or \
            not h["all_local_admissible"]:
        return {"verdict": "REJECT", "reason": "E_CEILING_BREACH",
                "hamilton": h}
    amended = any(d.amendment_grant for d in deltas)
    if h["kernel_drifted"] and not amended:
        return {"verdict": "REJECT", "reason": "E_SEMANTIC_DRIFT",
                "drifted_terms": h["drifted_terms"],
                "note": "the ledger is immaculate and the constitution "
                        "is corrupted — refused",
                "hamilton": h}
    return {"verdict": "ADMIT",
            "reason": ("KERNEL_AMENDED_UNDER_GRANT" if
                       (h["kernel_drifted"] and amended) else
                       "KERNEL_PRESERVED"),
            "hamilton": h}


# ── fifth-ceiling candidacy: earned, honestly bounded ───────────────────

def fifth_ceiling_candidacy() -> dict:
    """Feed the Hamilton witness to the committed candidacy machinery.
    It is the first candidate to meet the bar that machinery set:
    passes transactional evaluation, still invalid."""
    h = hamilton_test(initial_state(), drift_trace(),
                      STANDARD_INVARIANTS)
    candidate = {"name": "PERSISTENCE — semantic drift through lawful "
                         "history",
                 "passes_transactional":
                     h["transactional_verdict"] == "ADMIT" and
                     h["all_local_admissible"],
                 "still_invalid": h["kernel_drifted"]}
    status = ccl.fifth_ceiling_status((candidate,))
    return {**status,
            "candidate": candidate["name"],
            "earned_under": "CURRENT_STATE_MODEL",
            "witness": {k: h[k] for k in
                        ("replay_is_exact", "kernel_drifted",
                         "drifted_terms", "witness_found")},
            "open_question": "fifth ceiling proper, or the four over a "
                             "semantically enriched state where kernel "
                             "meanings are SCOPE-visible objects no "
                             "grant covers — unresolved",
            "adequacy_update": "the four-ceiling adequacy verdict was "
                               "domain-bounded (minimality.py said so); "
                               "the Hamilton extension falsifies "
                               "adequacy over semantic states unless "
                               "pi_K is enforced",
            "law": "a fine constitution is one whose reference "
                   "survives its history"}
