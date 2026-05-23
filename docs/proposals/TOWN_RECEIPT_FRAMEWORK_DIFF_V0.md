# TOWN_RECEIPT_FRAMEWORK_DIFF_V0

**authority:** NON_SOVEREIGN
**canon:** NO_SHIP
**lifecycle:** ANALYSIS_DRAFT
**implementation_status:** N/A (comparison artifact)
**status:** Diff against existing HELEN doctrine
**parent_input:** TOWN_RECEIPT_FRAMEWORK v0.1 (conversation dump, 2026-05-23)

---

## §1. Purpose

This document maps every claim in the **TOWN RECEIPT FRAMEWORK v0.1**
dump against HELEN's existing on-disk doctrine.

It exists to answer one question:

> What in the Town Receipt Framework is **already canonical in HELEN**,
> what is **genuinely new**, and what is **out of scope**?

This is **not a proposal**. It produces no doctrine, no schemas, no
gates. It is an audit so we don't accidentally bottle a restatement
under a new name and call it progress.

---

## §2. Layer-by-layer mapping

| Town Framework Layer | HELEN Equivalent | File / Source | Status |
| --- | --- | --- | --- |
| **SIGNAL** — detect what matters (cost spikes, latency, prompt waste, governance friction) | `HELEN_PRESSURE_SIGNAL_V1` — composite operational stress signal | `helen_pressure_signal_v1.py` (lines 77-81) | **Partial overlap.** HELEN tracks pressure/ambiguity/coercion/constraint-conflict. Cost/latency/prompt-waste signals are absent. |
| **ATTRIBUTION** — actor + workflow + model + prompt + context | Proposer ≠ validator + ledger meta fields | `oracle_kernel_v1.py:176`, `decision_ledger_v1.json` entry `meta` | **Restated.** Attribution exists but is binary (proposer vs validator); per-call actor/model/prompt attribution is not separately structured. |
| **GOVERNANCE** — rules layer | K8 + K-τ + K-ρ + K-wul + LEGORACLE + kernel_guard | `scripts/helen_*_lint.py`, `helen_os/governance/legoracle_gate_poc.py`, `tools/kernel_guard.sh` | **Restated.** HELEN has 6 active gates today. Framework's 4 governance rules are a subset of what HELEN already enforces. |
| **OPTIMIZATION** — prompt compression, semantic cache, model routing, duplicate suppression | **None** | n/a | **Genuinely new.** No cost-reduction layer exists in HELEN. (Q6: zero token/spend/economic tracking on disk.) |
| **RECEIPT** — proof of governed execution | 6 canonical receipt schemas | `helen_os/schemas/{autoresearch_eval,batch,closure,execution,plugin}_receipt_v1.{json,schema.json}` + `receipt_payload.v1.schema.json` | **Restated, with one new field cluster.** Existing receipts cover decision/execution/closure/batch/plugin lineage. **Cost/saving fields are net-new.** |
| **REPLAY** — full, sparse, checkpoint, cost | `replay_proof_v1.py`, `ledger_replay_v1.py`, E12 LEGORACLE replay gate | `helen_os/replay_proof_v1.py`, `helen_os/state/ledger_replay_v1.py`, `GOVERNANCE/TRANCHE_RECEIPTS/E12-*.json` | **Mostly restated, taxonomy refinement is new.** HELEN has replay machinery; framework's full/sparse/checkpoint/cost taxonomy by purpose is a refinement. |
| **TPI** — composite 0-100 stress score | None (HELEN_PRESSURE_SIGNAL_V1 is posture-only, not 0-100 composite governance score) | n/a | **Genuinely new.** No constitutional construct combining governance + economic + drift + coherence into a single index. |

---

## §3. Invariants

### §3.1 Restated

| Framework | HELEN | Note |
| --- | --- | --- |
| `NO RECEIPT = NO SHIP` | `NO RECEIPT = NO CLAIM` (`CLAUDE.md` Key Invariants) | **SHIP** is a verdict subset of **CLAIM**. HELEN's invariant is broader: any action without a receipt is constitutionally void, not just shipping. The framework restatement narrows scope. |
| `proposer ≠ validator` (attribution rule) | K2 / Rule 3, peer_review enforces | `oracle_kernel_v1.py:176`, `AUTORESEARCH_CONTRACT_V1.json:120` | Identical. |
| Each ledger entry hash-chained | `prev_cum_hash` + `cum_hash` chain | `town/ledger_v1.ndjson`, `decision_ledger_v1.json` | Identical. |

### §3.2 Genuinely new

| Invariant | Status |
| --- | --- |
| `No critical action without checkpoint` | New if "checkpoint" ≠ "receipt". The framework distinguishes checkpoints (lightweight state snapshots) from receipts (cryptographic proofs). HELEN conflates these today. |
| `No optimization without measurable baseline` | New. HELEN has no concept of optimization-with-baseline; this is a precondition that doesn't exist in current doctrine. |
| `No autonomy increase without replayability` | Partial. HELEN's halt discipline + 7-field tranche receipt approximate this for autoresearch; not generalized to arbitrary autonomy expansion. |

---

## §4. The 9-field RECEIPT format

The framework specifies a receipt containing:
`WHO / WHAT / WHY / MODEL / COST / RISK / OUTCOME / SAVING / REPLAY_LINK`

Mapping to existing HELEN receipts:

| Framework field | HELEN equivalent | Source |
| --- | --- | --- |
| WHO | `executor` / `proposer` / `meta.actor` | `execution_receipt_v1.schema.json` |
| WHAT | `decision` / `command_ref` | `decision_ledger_v1.json`, `execution_receipt_v1.schema.json` |
| WHY | `claims` / `obligations` | `closure_receipt_v1.json` |
| MODEL | **partial** — `helen_multimodel_dispatcher_v1.py` references model but doesn't record per-call | Gap |
| **COST** | **none** | **Net-new** |
| RISK | `verdict` (BLOCK/NO_SHIP) implies risk-derived, but no separate risk field | Partial gap |
| OUTCOME | `status` / `result` / `verdict` | `execution_receipt_v1.schema.json`, `verdict_v1.schema.json` |
| **SAVING** | **none** | **Net-new** |
| REPLAY_LINK | `ledger_replay_proof` / `execution_replay_proof` | `batch_receipt_packet_v1.json` |

**Gap analysis:** 7/9 fields already in HELEN. **COST and SAVING are the net-new contribution.**

---

## §5. The 7-field tranche receipt vs. the 9-field RECEIPT

HELEN already has a 7-field receipt per epoch:

```
carry-forward state | hypothesis | experiment | metric |
failure mode | keep/reject rule | upgrade path
```

Source: `CLAUDE.md` PULL-Mode Tranche Discipline; example
`GOVERNANCE/TRANCHE_RECEIPTS/E12-legoracle-replay-gate-V1.json`.

The framework's 9-field RECEIPT is **operational** (per-call); HELEN's
7-field is **epistemic** (per-epoch). These are **complementary, not
competing**. A clean adoption path would treat them as two receipt
*classes* at different temporal scales:

- 9-field RECEIPT — bounded executor / per-call
- 7-field tranche receipt — autoresearch / per-epoch

---

## §6. Town Pressure Index (TPI) vs HELEN_PRESSURE_SIGNAL_V1

The framework's TPI:
```
TPI = f(governance_pressure, economic_pressure,
        attribution_confidence, drift_risk, signal_coherence)
```
- Range: 0-100
- Current modeled value: 82-84
- Purpose: synthetic stress score for "governance + interpretability tension"

HELEN's existing pressure signal:
```
HELEN_PRESSURE_SIGNAL_V1 = {
    pressure_score, ambiguity_score, coercion_score,
    constraint_conflict_score
} → stability_state ∈ {STABLE, STRAINED, UNSTABLE, BLOCKED}
   → routing_effect ∈ {NORMAL, CLARIFY_BEFORE_ACTION, DEFER, REFUSE}
```
- Range: each dim [0-1]
- Purpose: **routing posture for HELEN's own cognition**, not town-wide governance metric

**Key difference:**
- HELEN_PRESSURE_SIGNAL_V1 is **introspective** (one agent's posture)
- TPI is **systemic** (whole town's governance stress)

These are different objects. TPI would be a new construct if adopted.
It would not replace HELEN_PRESSURE_SIGNAL_V1.

---

## §7. Economic / cost dimension

This is the framework's clearest net-new contribution.

**Finding from Q6 of inventory:** HELEN has **zero on-disk economic tracking**:

- No token-spend counters
- No latency receipts
- No model-cost attribution
- No optimization-saving claims
- No CFO/investor reporting surface

Existing references are comments only (`helen_multimodel_dispatcher_v1.py`
mentions "latency/cost tradeoff" but does not implement it).

If HELEN ever runs at scale or under the EU AI Act / RGPD pressure the
framework names, this gap becomes operationally hot. The framework's
TokenLens framing is **commercially driven** (real product, real
clients) but the **governance pattern** maps cleanly onto HELEN's
existing receipt discipline.

**This is the only layer where adoption would be net-additive rather
than restating what's already on disk.**

---

## §8. Drift report mapping

The framework's drift vectors:

| Framework drift | Already happening in HELEN? | Evidence |
| --- | --- | --- |
| `continuous monitoring → sparse checkpoint governance` | **Yes, partially.** | E12 replay gate uses sparse checkpoints; tranche discipline = sparse per-epoch receipts. |
| `full transparency → selective intelligibility` | **No explicit doctrine, but emergent.** | HELEN does not have a privacy/selective-disclosure layer; receipts are full-transparency today. This would be net-new. |
| `execution-first → governance-first` | **Yes, complete.** | Entire constitutional architecture (5 layers, kernel sovereignty, NO RECEIPT = NO CLAIM) embodies this. |
| `observability as visibility → observability as guaranteed savings` | **Out of scope.** | HELEN's observability is for governance, not financial guarantee. The framework's "paid only on savings" is a commercial model, not a governance pattern. |

---

## §9. What's already canonical (do not re-bottle)

The following framework claims would be **doctrinal duplicates** if
bottled as new HELEN proposals:

- Receipt-based execution discipline → existing
- Hash-chained ledger → existing
- Proposer ≠ validator → existing
- Replay machinery → existing (E12, ledger_replay_v1, replay_proof_v1)
- Governance gates → existing (K8, K-τ, K-ρ, K-wul, LEGORACLE, kernel_guard)
- Sparse checkpoint governance → existing (tranche discipline)
- Pressure / stress signaling → existing (HELEN_PRESSURE_SIGNAL_V1)

Bottling these under TOWN_RECEIPT_FRAMEWORK names would be a **naming
collision attack** on the existing canon. Resist.

---

## §10. What's genuinely new (potentially adoptable)

| New construct | Cost to adopt | Value if adopted |
| --- | --- | --- |
| **Cost/saving fields in RECEIPT** | Low — 2 new optional fields in `execution_receipt_v1.schema.json` | High once HELEN runs at scale or under AI Act |
| **Per-call model attribution** | Low — `model` field in receipt | Medium — enables routing audits |
| **Replay taxonomy** (full / sparse / checkpoint / cost) | Low — typed enum on replay_proof | Medium — clarifies replay intent |
| **TPI as composite governance score** | Medium — new schema + computation | Uncertain — needs a consumer; without one it's dashboard furniture |
| **`No optimization without measurable baseline`** invariant | Low — one new doctrinal line | High **if** optimization layer is built |
| **`No autonomy increase without replayability`** invariant | Low — one new doctrinal line | High — generalizes halt discipline |
| **Selective-intelligibility doctrine** (drift vector B) | High — privacy layer is a substantial design space | Unknown — no current pressure for it |

---

## §11. What's out of scope for HELEN

- **TokenLens as a product** — commercial entity, not a HELEN component
- **CFO/investor reporting surface** — downstream consumer of receipts, not a constitutional layer
- **"Paid only on savings" commercial model** — business arrangement, not doctrine
- **AI Act compliance positioning as market differentiator** — regulatory posture, not governance architecture
- **Composite TPI score as marketing artifact** — even if adopted internally, the framework's 82-84 number is not constitutionally meaningful

These belong in the TokenLens deck, not in `docs/proposals/`.

---

## §12. Open questions

1. **Is TOKEN_LENS adjacent or upstream of HELEN?** The deck names HER's
   commercial work. If TokenLens consumes HELEN receipts as a downstream
   audit/cost product, that's a clean separation. If TokenLens *is*
   HELEN under a different name, the diff matters more.

2. **Is the OPTIMIZATION layer inside the kernel or downstream?**
   HELEN's kernel is sovereign-but-narrow. An optimization layer that
   rewrites prompts, routes models, or compresses payloads is
   non-sovereign by construction. If adopted, it belongs in
   `helen_os/executor/` or as a new `helen_os/optimization/` skill —
   not in the kernel.

3. **Should TPI be a HELEN object or a Town object?** The framework
   uses "Town" as the unit, but HELEN's Town (oracle_town/) is its
   internal civic structure. External "Town discourse" (HER's social
   signal aggregation) is a different Town. Naming collision needs
   resolution before adoption.

4. **Receipt-cost coupling.** If COST fields land in every receipt,
   does every existing receipt schema need a migration? If so, what's
   the backward-compatibility story? (Probably: COST is optional and
   defaults to null on legacy entries.)

5. **NO RECEIPT = NO SHIP vs NO RECEIPT = NO CLAIM.** Framework's
   "SHIP" narrows scope. Should HELEN adopt the narrower form anywhere,
   or insist on the broader CLAIM form? Recommendation: keep CLAIM as
   canonical; SHIP is a usable subset for media/render pipelines.

---

## §13. Recommendation

**Do not bottle TOWN_RECEIPT_FRAMEWORK_V0 as a unified doctrinal artifact.**

The framework is ~80% restatement of existing HELEN doctrine wrapped in
new terminology. Bottling it whole would create a parallel naming
system that competes with the canonical one.

**Instead, extract three small targeted proposals:**

1. **`COST_RECEIPT_FIELDS_V0`** — add optional `cost` and `saving`
   fields to `execution_receipt_v1.schema.json`. One commit, low risk,
   forward-compatible.

2. **`REPLAY_TAXONOMY_V0`** — typed enum (`FULL | SPARSE | CHECKPOINT |
   COST`) on existing replay-proof artifacts. Refinement, not new
   doctrine.

3. **`AUTONOMY_REPLAY_INVARIANT_V0`** — single doctrinal line: *"No
   autonomy increase without replayability."* Generalizes halt
   discipline. Cheap and high-leverage.

**Defer:**

- TPI as a HELEN object — needs a consumer first
- Selective-intelligibility doctrine — no current pressure
- Optimization layer architecture — premature without operator demand

**Reject as out-of-scope for HELEN proposals/:**

- TokenLens commercial framing
- CFO/investor reporting surfaces
- "Paid only on savings" business model

---

## §14. The single line

> **The Town Receipt Framework is mostly HELEN restated.
> The genuinely new contribution is the economic dimension — COST and
> SAVING fields in receipts. Bottle that one piece; resist the temptation
> to re-bottle the rest under new names.**
