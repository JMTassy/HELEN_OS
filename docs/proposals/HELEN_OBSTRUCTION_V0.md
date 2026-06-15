---
schema:         PROPOSAL_V1
status:         CANDIDATE
authority:      false
sovereign:      false
ledger_effect:  NONE
canon:          NO_SHIP
source:         JM_TASSY_session_2026-06-15
supersedes:     —
---

# HELEN_OBSTRUCTION_V0

## One-Line Definition

HELEN OS is an **obstruction-minimizing governance engine** — a system whose core
operating law is the monotonic reduction of a composite obstruction scalar
toward zero.

---

## The Obstruction Scalar

```
HELEN_OBSTRUCTION_N =
    determinism_error
  + provenance_gap
  + replay_failure
  + authority_drift
  + ledger_inconsistency
  + semantic_claim_debt
```

All six terms are non-negative. The system is healthy when `HELEN_OBSTRUCTION_N → 0`.
The system fails when any term grows unbounded.

---

## Component Definitions

### 1. `determinism_error`

A determinism error occurs when the same ordered event sequence produces
a different cumulative hash on two replays.

**Measured by:** K8 gate (`scripts/helen_k8_lint.py`) — mu_NDWRAP, mu_NDARTIFACT,
mu_NDLEDGER.

**Causes:** Non-deterministic output (random seeds, timestamps, UUID generation)
entering the ledger spine without hashing. `NO HASH = NO VOICE` invariant
violation.

**Reduction law:** All ND output hashed before spine entry. K8 passes
with k8=+1.000.

---

### 2. `provenance_gap`

A provenance gap occurs when a claim in the system has no traceable source
attestation — the claim appears in a display, a document, or an agent
response, but its lineage cannot be reconstructed from ledger events.

**Measured by:** K-tau gate (`scripts/helen_k_tau_lint.py`) — mu_BOUNDARY,
mu_IO, mu_SCHEMA.

**Causes:** Agent output promoted to canonical status without a
`SOURCEBOUND_OBJECT_RECEIPT_V0`; corpus ingestion without a provenance
hash; Headroom compression stripping source metadata.

**Reduction law:** Every artifact entering the corpus carries a receipt
binding its source bytes. `tools/helen_object.py` path required for any
object entering the spine.

---

### 3. `replay_failure`

A replay failure occurs when the ledger cannot reproduce the claimed final
state from its own event sequence.

**Measured by:** LEGORACLE gate (`helen_os/governance/legoracle_gate_poc.py`)
replay fixture integrity + determinism check (E12).

**Causes:** Out-of-order writes (TOCTOU seq fork); ledger mutations outside
the `ndjson_writer.py` boundary; manual ledger edits.

**Reduction law:** `fcntl.flock` exclusive lock on every write; `_handle_seq_correction()`
for anchor repair; `kernel_guard.sh` rejects unauthorized writers.
Chain status must read PASS before any claim of replay integrity.

---

### 4. `authority_drift`

Authority drift occurs when a non-sovereign agent, UI layer, or artifact
presents itself as having admission authority — issuing verdicts, certifying
claims, or speaking in the voice of the reducer without being the reducer.

**Measured by:** Ghost closure detector
(`helen_os/tests/test_no_ghost_closures.py`); WITNESS node comparison
(runtime reality vs. trust reality).

**Causes:** Agent output labeled `SHIP` without reducer pass; UI showing
`trust recovered` with no ledger receipt; demo_state promoted to canon.
Language contamination: "Zero Bugs", "Award-Winning", "Production-Ready"
without receipts.

**Reduction law:** CRITIC node intercepts unfalsifiable claims before
obligation generation. Every agent output carries `authority: false`.
WITNESS surfaces gaps; does not close them. Only the reducer emits SHIP.

---

### 5. `ledger_inconsistency`

Ledger inconsistency occurs when the on-disk `town/ledger_v1.ndjson`
contains events that fail hash-chain validation — either a broken
`cum_hash` chain or a duplicate `seq` entry.

**Measured by:** Ledger validator (`helen_os/tests/`) + duplicate seq
detector.

**Causes:** Concurrent writes without flock; manual edits; the original
TOCTOU seq=287 fork (now ANCHORED at seq=295 via `LEDGER_SEQ_CORRECTION_V1`).

**Reduction law:** NDJSONWriter atomicity: re-reads tail under flock before
each append. Seq repair via `_handle_seq_correction()` — operator-authorized
only. Ledger status must read CHAIN=PASS.

---

### 6. `semantic_claim_debt`

Semantic claim debt is the accumulation of claims in circulation —
documents, agent outputs, UI labels — that have not been processed
through the full admission pipeline (classify → critic → obligations →
receipts → reducer → ledger).

**Measured by:** Manually. Every unprocessed claim in `docs/proposals/`,
unverified assertions in agent outputs, and archived-but-never-admitted
TEMPLE artifacts accumulate debt. The corpus research loop (`tools/corpus_research_loop.py`)
generates `promotion_plan_draft.json` as a debt register for image assets.

**Causes:** Sessions that generate proposals without immediately routing
them to the admission pipeline; TEMPLE sessions that surface symbolic
material without containment receipts; AUTORESEARCH epochs whose findings
are not consumed by a subsequent MAYOR ruling.

**Reduction law:** Every proposal file that reaches the operator must
declare its admission status (`NO_SHIP`, `CANDIDATE`, `SHIP_PENDING`).
Unresolved autoresearch findings block the next epoch until the prior
finding is KEEP or REJECT (one hypothesis per epoch invariant).

---

## Reduction Laws — Summary

```
TERM                     GATE            REDUCTION LAW
determinism_error      → K8             hash all ND output before spine
provenance_gap         → K-tau          sourcebound receipt on every artifact
replay_failure         → LEGORACLE      flock + seq repair + chain PASS
authority_drift        → WITNESS        CRITIC node + authority:false labels
ledger_inconsistency   → ledger-valid   NDJSONWriter atomicity + seq correction
semantic_claim_debt    → MAYOR (manual) 1-hypothesis-per-epoch + promotion discipline
```

The six gates already exist in HELEN. This document names what each gate
is minimizing. The gates do not change; the framing sharpens.

---

## Relationship to Kernel Chain

```
CLASSIFY        — semantic_claim_debt: first filter, reduces uncategorized claims
EXTRACT CLAIMS  — semantic_claim_debt: makes debt explicit and countable
CRITIC          — authority_drift: rejects unfalsifiable claims before obligation
OBLIGATIONS     — provenance_gap: forces source attestation per claim
RECEIPTS        — provenance_gap: binds evidence to obligation names
REDUCER         — authority_drift: the only node that can admit
LEDGER          — ledger_inconsistency: append-only, flock, chain integrity
REPLAY          — replay_failure: proves state from events
WITNESS         — authority_drift: compares runtime vs ledger truth
UI SHELL        — authority_drift: display only, never admit
AGENTS          — authority_drift: propose only, never decide
```

---

## OS Frame

"Obstruction-minimizing governance engine" replaces the weaker frame
"governance system." In differential geometry, an obstruction is a
cohomological invariant that prevents a local property from globalizing.
In HELEN OS:

- **Local property:** a claim is believed to be true by a single agent or session.
- **Global property:** that claim is replayable from the ledger by any observer.
- **Obstruction:** the gap between local belief and global verifiability.

HELEN's architecture is a systematic program to reduce this gap to zero.
The six components above are the six ways the gap can open.

No new mechanism is required. The gates already implement the reduction.
The contribution of this document is the **scalar formulation**: a single
number that makes system health auditable.

---

## AEON Analogy (non-binding, TEMPLE_GRADE)

The AEON bridge `𝔈_N → 0` (arithmetic entropic optimal network gap
converging to zero) surfaced in a prior session as a structural analogy
for HELEN's admission pipeline. The analogy holds at the architectural
level:

| AEON term              | HELEN term                       |
|------------------------|----------------------------------|
| φ-regularization       | sovereign firewall               |
| Λ–Δ duality            | claim ↔ receipt duality          |
| Schrödinger bridge     | admission pipeline               |
| `𝔈_N → 0`             | `HELEN_OBSTRUCTION_N → 0`       |
| Falsification certificate | K-gate PASS/FAIL verdict      |

This analogy is **TEMPLE_GRADE** — inspiring, not normative. The math
does not enter the kernel. The kernel runs on `kernel_guard.sh`.

---

## Status

```
authority:      false
sovereign:      false
ledger_effect:  NONE
status:         CANDIDATE — no code, no ledger event, no schema change
next_step:      operator countersign → MAYOR routing → DOCTRINE_ADMISSION gate
                (gate DRAFT, not yet active as of 2026-06-15)
```
