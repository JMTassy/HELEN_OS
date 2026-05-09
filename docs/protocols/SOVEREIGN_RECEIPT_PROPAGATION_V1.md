# SOVEREIGN_RECEIPT_PROPAGATION_V1

**Status:** PROPOSAL  
**Class:** PROTOCOL  
**Authority:** NON_SOVEREIGN  
**Canon:** NO_SHIP until MAYOR review  
**Depends on:** `DISTRIBUTED_SEMANTIC_CONTINUITY_V1.md`  
**Author:** JM Tassy  
**Date:** 2026-05-09

---

## Purpose

`DISTRIBUTED_SEMANTIC_CONTINUITY_V1` establishes that HELEN's semantic state should satisfy:

```
S(D_i) ≡ S(D_j)   for all compliant terminals D_i, D_j
```

This document defines the **policy layer** that makes that equation implementable. Without this layer the doctrine is rhetoric. With it, the equation becomes a testable contract.

The load-bearing function:

```
P : S → {EPHEMERAL, LOCAL_SOVEREIGN, FEDERATED_SOVEREIGN, PUBLIC_SOVEREIGN, REBUILDABLE, SEALED}
```

`P` converts semantic state from a philosophical claim into a runtime routing decision.

---

## 1. Receipt Classes

Privacy and continuity are **orthogonal axes**. Collapsing them is the failure mode that broke every "sync everything sovereign" architecture before this one.

| Class | Continuity | Federation | Description |
|---|---|---|---|
| `EPHEMERAL` | none | never | Transient runtime state. Cache, scratch, in-flight computation. Never receipted. |
| `LOCAL_SOVEREIGN` | full receipt | never | Receipted decisions that are terminal-private by policy. Example: Telegram DM metadata, private session context. Sovereign lineage, zero-propagation. |
| `FEDERATED_SOVEREIGN` | full receipt | within owner's terminals | The primary continuity class. Autoresearch verdicts, skill execution receipts, state mutations. Propagates across the operator's devices only. |
| `PUBLIC_SOVEREIGN` | full receipt | crosses trust boundaries | Doctrine documents, public ledger entries, receipts intended for external audit. Propagates beyond the operator's device boundary. |
| `REBUILDABLE` | derivable from G+L | optional | State that can be reconstructed deterministically from code truth (G) and the receipt ledger (L). Gate outputs, derived embeddings, computed summaries. |
| `SEALED` | full receipt | ciphertext only | Receipts with sovereign lineage that cross trust boundaries in encrypted form. Content private; existence and hash are public. |

**Key invariant:** A receipt's class is declared at write-time. Class cannot be promoted retroactively without a new receipt naming the original.

---

## 2. Sovereign vs Derived Continuity

Not all receipted state is `FEDERATED_SOVEREIGN`. The test is:

> **Can this receipt, if missing from terminal D_j, cause D_j to make a decision that D_i already overruled?**

If yes: `FEDERATED_SOVEREIGN`.  
If no but it was receipted: `LOCAL_SOVEREIGN` or `REBUILDABLE`.  
If the state can be recomputed from G + L: `REBUILDABLE`.

Practical examples:

| Artifact | Correct class |
|---|---|
| Autoresearch epoch verdict (KEEP/REJECT) | `FEDERATED_SOVEREIGN` |
| Autoresearch execution trace | `REBUILDABLE` |
| Telegram DM send receipt | `LOCAL_SOVEREIGN` |
| Doctrine document (pushed to repo) | `PUBLIC_SOVEREIGN` |
| K8 lint output | `REBUILDABLE` |
| MAYOR signing record | `FEDERATED_SOVEREIGN` |
| Session scratch notes | `EPHEMERAL` |
| `temple_1000_results.jsonl` (autoresearch run) | `FEDERATED_SOVEREIGN` (currently misclassified as LOCAL by `.gitignore`) |

---

## 3. Device-Local Admissibility

A terminal may admit locally without propagating. Local admission means:

- The receipt is written to the local ledger chain
- The receipt does NOT enter `oracle_town/memory/` (the shared semantic layer)
- The receipt does NOT enter any sync channel

This is valid for `EPHEMERAL` and `LOCAL_SOVEREIGN` classes.

For `FEDERATED_SOVEREIGN`: local admission is a **temporary state only**. The receipt must propagate to the shared memory layer before the next cross-terminal session begins. Failure to propagate within the session window creates `Δ_ij > 0` — measurable semantic drift.

---

## 4. Propagation Policies

### Conflict resolution: Receipt DAG

The doctrine implies a **Receipt DAG** (Git-style directed acyclic graph) rather than writer leadership or CRDTs:

- Each terminal maintains its own receipt chain with local total order
- Cross-terminal receipts have partial order only
- Explicit **merge receipts** record the convergence of two chains
- `S(D_i) ≡ S(D_j)` holds **after merge**, not continuously

Consequence: `governed_state_hash` is per-branch until merge. The claim "device-irrelevant" requires the qualifier "post-merge."

### Propagation trigger

A `FEDERATED_SOVEREIGN` receipt propagates when:
1. The terminal writes it to local ledger, AND
2. A sync window opens (git push / symlink flush / API sync)

Sync windows are not continuous — they are explicit events. This is by design: continuous sync collapses into cloud sync and loses the governed-meaning distinction.

### Propagation channel (current implementation)

```
oracle_town/memory/  ←  gitignore-exempt shared folder
                        (symlinked via setup_memory_symlink.sh)
```

`FEDERATED_SOVEREIGN` receipts land in `oracle_town/memory/receipts/` with class declaration in the envelope. `REBUILDABLE` and `EPHEMERAL` stay device-local.

---

## 5. Replay Guarantees

For `S(D_i) ≡ S(D_j)` to hold after merge:

1. Both terminals must replay from the **same G** (same git commit of code truth)
2. Both terminals must have the **same L** (identical receipt set after merge)
3. The reducer must be **deterministic** — same (G, L) always produces same S
4. Merge receipts must be **ordered** — the DAG must have a defined root for each branch

If any of these four conditions fails, `Δ_ij ≠ 0` even after apparent merge. The failure mode is **silent divergence** — both terminals believe they are synchronized but are not.

---

## 6. Privacy Boundaries

Privacy is enforced by class assignment, not by redaction. The rule:

> **The class of a receipt is set by the most restrictive axis of its content.**

A receipt that touches private context (`LOCAL_SOVEREIGN`) combined with a federated decision (`FEDERATED_SOVEREIGN`) resolves to `LOCAL_SOVEREIGN`. The decision cannot propagate because the context cannot propagate.

The correct pattern: strip the private context into a separate `LOCAL_SOVEREIGN` receipt, then emit the decision receipt as `FEDERATED_SOVEREIGN` with a reference hash (not the content) to the private context.

```
[LOCAL_SOVEREIGN receipt R-priv]  ← contains private content
[FEDERATED_SOVEREIGN receipt R-dec]  ← references hash(R-priv), not content
```

This preserves governed lineage without exposing private state.

---

## 7. Federation Routing

Future state (not current implementation):

Receipts may eventually propagate across trust boundaries (e.g., to collaborators, auditors, or MAYOR-verified external systems). Routing rules:

| Destination | Allowed classes |
|---|---|
| Operator's own terminals | `FEDERATED_SOVEREIGN`, `PUBLIC_SOVEREIGN`, `SEALED` |
| Auditor | `PUBLIC_SOVEREIGN`, `SEALED` |
| External system | `PUBLIC_SOVEREIGN` only (or `SEALED` with key exchange) |
| MAYOR | All sovereign classes; MAYOR is the trust root |

Federation routing is **not implemented** in v0.3. This section is forward declaration only.

---

## 8. Continuity Failure Modes

These are the concrete ways `S(D_i) ≡ S(D_j)` fails silently:

### Replay forking
A `FEDERATED_SOVEREIGN` receipt exists on D_i but never propagates to D_j. D_j replays without it. Both terminals produce valid local chains but diverge semantically. Neither terminal detects the fork without an explicit cross-check.

**Mitigation:** Require `governed_state_hash` comparison at session start. Hash mismatch = fork detected before work begins.

### Stale-G replay
Terminal D_j replays sovereign receipts (L) against an old version of code truth (G). The reducer may produce different output for the same input if G changed. `S(D_j)` is self-consistent but not equivalent to `S(D_i)` running current G.

**Mitigation:** Each receipt envelope records the G-commit hash at write-time. Replay must match G-commit or explicitly declare upgrade.

### Conflicting writer claims
Both D_i and D_j emit `FEDERATED_SOVEREIGN` receipts for the same semantic object during the same session window (before merge). Merge creates ambiguity about which receipt is canonical.

**Mitigation:** Receipt DAG requires explicit merge receipts. No implicit last-write-wins. Unresolved conflicts surface as open merge nodes visible to MAYOR.

### Receipt spoofing
A receipt claims `FEDERATED_SOVEREIGN` class without a canonical witness (no MAYOR signature, no gate passage, no hash chain). Propagated across terminals, it poisons the shared semantic state.

**Mitigation:** Gate check on class assignment. `FEDERATED_SOVEREIGN` receipts require: `authority ≠ NONE`, `receipt_hash` present, chain predecessor present. Unsigned receipts are demoted to `LOCAL_SOVEREIGN` at propagation time.

---

## 9. Ledger Convergence Conditions

For the receipt DAG to converge (i.e., for `Δ_ij → 0` to be achievable):

1. **Termination:** Every branch eventually produces a merge receipt. No perpetually-open branches.
2. **Determinism:** Reducers are pure functions of (G, L). No side effects that escape the receipt system.
3. **Completeness:** All `FEDERATED_SOVEREIGN` receipts from all terminals are present in the merged L before a convergence claim is made.
4. **Integrity:** No receipt in the merged L has a broken hash chain.

When all four hold: `Δ_ij = 0` and the first passing test of the doctrine is achieved.

---

## Live Falsification Test (v0.3)

The autoresearch run currently executing on the iMac (PID 38251, ~1000 epochs of KEEP/REJECT verdicts on HELEN's future) produces receipts in:

```
helensh/.state/temple_1000_results.jsonl
```

This artifact is currently:
- **Actual class:** `EPHEMERAL` (gitignored, never propagates)
- **Correct class by this doctrine:** `FEDERATED_SOVEREIGN` (receipted KEEP/REJECT decisions about HELEN's evolution)

The minimum passing test of this protocol:

1. Declare `temple_1000_results.jsonl` receipts as `class: FEDERATED_SOVEREIGN`
2. Add `class` field to the receipt envelope schema
3. Move the output path to `oracle_town/memory/autoresearch/` (symlinked, shared)
4. Replay on the MacBook → `governed_state_hash` matches iMac

If the replay produces matching state: `Δ_ij = 0` for this class. First passing test.  
If not: the specific failure mode identifies which of the 9 convergence conditions broke.

---

## The OS-Level Claim

```
Traditional OS:  storage policy = filesystem policy (path, extension, size)
HELEN:           storage policy = semantic governance policy (meaning, class, continuity)
```

This is the inversion. Filesystems route by location. HELEN routes by meaning. The class function `P` is what makes that routing deterministic rather than aspirational.

---

## Next Steps (non-binding)

1. Add `class` field to receipt envelope schema in `helen_os/schemas/`
2. Implement class-check at propagation time in the sync layer
3. Move autoresearch epoch verdicts to `oracle_town/memory/autoresearch/`
4. Write `governed_state_hash` comparison to `sync_preflight.sh`
5. First replay test across iMac + MacBook on completed autoresearch run

---

*HELEN OS — created by JM Tassy.*
