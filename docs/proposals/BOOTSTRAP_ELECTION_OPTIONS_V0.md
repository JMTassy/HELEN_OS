# BOOTSTRAP_ELECTION_OPTIONS_V0

**authority:** NON_SOVEREIGN
**canon:** NO_SHIP
**lifecycle:** DOCTRINE_DRAFT
**implementation_status:** NOT_APPLICABLE (comparison doctrine, not a mechanism)
**status:** Proposal — comparison of bootstrap paths defined in `MAYOR_ADMISSION_PROTOCOL_V0 §13`
**origin_signal:** `MAYOR_ADMISSION_PROTOCOL_V0 §13.4 — operator must elect a bootstrap path before MAYOR can exist`
**parent_synthesis:** `docs/proposals/MAYOR_ADMISSION_PROTOCOL_V0.md`, `docs/proposals/RECEIPT_SAFE_MUTATION_PROTOCOL_V0.md`, `helensh/SEED_V3.txt`
**proposer:** claude-opus-4-7 (acting as GOBLIN doctrine drafter)
**attestor:** pending HER

---

## §0. Axiom

Carried forward:

> **NO VALID RECEIPT = NO TRUSTED STATE MUTATION.**
> **NO MAYOR SEAL = NO ADMITTED CANON.**

Extended for the bootstrap question:

> **NO LEGITIMATE FIRST MAYOR = NO LEGITIMATE ADMISSION CHAIN.**

The first seal is the most consequential one. Every subsequent admission inherits the legitimacy of the bootstrap. A bootstrap whose legitimacy is in doubt poisons the entire chain — silently, irreversibly, retroactively. The bootstrap election is not a procedural detail; it is the foundational trust act.

---

## §1. Problem

`MAYOR_ADMISSION_PROTOCOL_V0` specifies a complete admission discipline but cannot self-admit: **a MAYOR cannot admit MAYOR.** §13 of that doctrine names three bootstrap paths but does not compare them. The operator must choose one before any RAW artifact (including the two existing doctrines) can become admitted canon.

This document compares the three paths along the six dimensions necessary to make a defensible election:

```
1. What action counts as election?
2. What receipts are required?
3. What can go wrong?
4. Can the bootstrap be revoked?
5. What becomes possible after election?
6. What remains forbidden?
```

This document **does not elect**. It compares. The election is an operator act that must be recorded separately as a `BOOTSTRAP_ELECTION_V0` receipt (schema sketched in §7).

---

## §2. Option §13.1 — Single-operator bootstrap

### §2.1 Election action

The sole human operator (currently `JM Tassy`) writes a `BOOTSTRAP_ELECTION_V0` receipt declaring path §13.1 chosen, then manually appends the genesis entry to `helensh/.state/admitted_canon.jsonl`. The genesis entry attests a single MAYOR identity (A5) — typically the operator themselves or a key/agent the operator controls. The newly-admitted MAYOR then admits, in order:

1. `MAYOR_ADMISSION_RECEIPT_V1` schema (A3)
2. `MAYOR_REVOCATION_RECEIPT_V1` schema (A3)
3. `RECEIPT_SAFE_MUTATION_PROTOCOL_V0` (A1)
4. `MAYOR_ADMISSION_PROTOCOL_V0` (A1)
5. `tools/mayor_admission.py` once written (A2)

Five chained seals plus the genesis attestation. Total: six receipts to close the bootstrap loop.

### §2.2 Receipts required

- `BOOTSTRAP_ELECTION_V0` — operator-signed declaration of chosen path, justification, review-by date
- `bootstrap_attestation.json` — direct operator attestation of the first MAYOR identity; outside the chain, referenced by the genesis seal's `previous_seal_hash` field as `"GENESIS:<sha256>"`
- Genesis entry in `admitted_canon.jsonl` with `previous_seal_hash = "GENESIS"`
- Five subsequent admission seals (per §2.1 above)

### §2.3 What can go wrong

- **Single-operator capture.** If the operator's identity is compromised (key theft, account takeover, coercion), the entire admission tree is owned. There is no second human to detect or veto. The receipt-law axiom holds locally but does not survive an adversarial threat model.
- **Self-serving collapse.** The same person who drafts doctrine also ratifies it. The control plane's HAL/operator separation, designed to prevent exactly this, collapses to one human at bootstrap.
- **Single point of failure.** Operator death, key loss, or extended unavailability freezes the chain. No admission proceeds, no revocation possible, no rotation legal.
- **Adversarial undetectability.** From an outside auditor's perspective, the first seal is indistinguishable from a fabrication by anyone with filesystem write access to `helensh/.state/`. The chain's integrity reduces to the operator's local filesystem security.
- **Optical vulnerability.** Even when honest, the system cannot honestly claim *distributed* trust. The first seal is "trust me."

### §2.4 Revocability

- **In principle**, yes — `MAYOR_ADMISSION_PROTOCOL_V0 §11` revocation applies.
- **In practice**, no — the only actor authorized to revoke a MAYOR seal is the same MAYOR or a successor MAYOR. If the bootstrap MAYOR is compromised, the compromised identity controls revocation.
- **Recovery requires destroying and restarting the chain** — a meta-operator action at the filesystem level, which is itself a §10-style forbidden mutation in spirit (direct edit bypassing the gate).
- Net: revocable only by chain destruction. Not gracefully revocable.

### §2.5 What becomes possible after election

- All admittable object classes A1–A6 (doctrine, tool, schema, capability, identity, amendment) become reachable.
- Both existing RAW doctrines (`RECEIPT_SAFE_MUTATION_PROTOCOL_V0`, `MAYOR_ADMISSION_PROTOCOL_V0`) can be admitted.
- The §7 `resolution` lane (suspicious-event resolution) can be implemented in the cockpit and admitted.
- Future capabilities (`url_fetch`, `claw_external`) can be granted via admitted A4 receipts.
- HAL and operator identities can be formalized as admitted A5 receipts.
- The cockpit's read-before-write fix (commit `f0a9520`) can be cited as enforcing admitted canon, not just implementing RAW doctrine.

### §2.6 What remains forbidden

- All 15 forbidden patterns in `MAYOR_ADMISSION_PROTOCOL_V0 §10`.
- Re-electing a new bootstrap MAYOR via §13.1 again — once bootstrap is complete, new MAYOR identities go through normal admission (A5), not bootstrap.
- The bootstrap MAYOR self-admitting their *own* identity post-genesis. The genesis attestation is the one-time exception; afterward, even the bootstrap MAYOR cannot re-admit themselves.
- Treating the bootstrap MAYOR as having broader authority than the seal grants. A bootstrap MAYOR admitted to seal A1/A2/A3/A4/A5/A6 cannot also seal arbitrary M1 ledger writes — that authority belongs to the Governor, not MAYOR.

---

## §3. Option §13.2 — N-of-M quorum bootstrap

### §3.1 Election action

A pre-declared quorum of operators (e.g., 2-of-3, 3-of-5, or higher) each sign a `BOOTSTRAP_ATTESTATION_V0` receipt. The combined attestations form the genesis entry of `admitted_canon.jsonl`. The first MAYOR can be:

- **Single-MAYOR-by-quorum**: one operator becomes MAYOR with the endorsement of N − 1 others. Subsequent seals require only that MAYOR's signature.
- **Compound MAYOR**: every future seal requires quorum signature. Slower but stronger; the MAYOR identity is collective, not individual.

The election action is the *complete assembly* of N signatures. A partial attestation (N − 1 signatures) is not an election; the genesis entry is illegal until the Nth signature.

### §3.2 Receipts required

- `QUORUM_DECLARATION_V0` — declares N and M, lists M operator identities by public key (or equivalent attestation token), defines quorum policy (single-MAYOR-by-quorum vs compound MAYOR), defines quorum-rotation rules
- N × `BOOTSTRAP_ATTESTATION_V0` — one per signing operator, each independently signed
- `BOOTSTRAP_ELECTION_V0` — declares path §13.2 chosen, references the quorum and all N attestations
- Genesis entry in `admitted_canon.jsonl` carrying all N signatures
- Subsequent admission seals — single MAYOR signature (single-MAYOR-by-quorum) or full quorum (compound MAYOR)

### §3.3 What can go wrong

- **Quorum collusion.** N operators in agreement can do anything M is supposed to prevent. The protection assumes operators have independent judgment; if they do not, the quorum is theatre.
- **Quorum unavailability.** If N operators cannot be assembled (geography, schedule, falling-out, illness), no admission proceeds. The chain freezes *more easily* than §13.1, not less.
- **Compound-MAYOR latency.** Every seal requires N signatures. The cost-per-admission rises by N×. Iteration on doctrine becomes slow enough that the system effectively reverts to §13.3 behaviour by exhaustion.
- **Quorum decay.** If one operator loses their key or becomes hostile, effective M shrinks. If `M − defections < N`, the system is locked out permanently without re-bootstrap (which is itself a §13.1 act of last resort).
- **Initial-quorum-selection paradox.** Choosing the M itself has no gate. Whoever declares the initial M decides who has power. This decision is structurally identical to §13.1 and inherits the same single-operator vulnerability — just deferred by one level.
- **Disagreement deadlock.** If operators genuinely disagree on whether to admit a contentious artifact, the chain stalls. There is no tie-breaker without amending the quorum policy, which itself requires quorum.

### §3.4 Revocability

- **Stronger than §13.1.** A different N-of-M (or even N − 1-of-M − 1 after a defection, if the policy permits) can revoke a compromised MAYOR's seal.
- **Quorum rotation** — adding/removing operators — requires its own quorum decision. This is a real, non-trivial protocol but well-studied (see multi-sig schemes in distributed systems).
- **Bootstrap-of-bootstrap edge case.** Changing the quorum policy itself requires quorum approval. Mostly tractable; circular only at the edge where the policy mandates unanimous consent for policy changes.
- Net: gracefully revocable up to `M − N + 1` simultaneous defections. Beyond that, recovery is §13.1-like chain destruction.

### §3.5 What becomes possible after election

- All §2.5 capabilities.
- Plus: graceful operator rotation, quorum-gated revocation, multi-party trust posture.
- Plus: HAL and operator identities can be admitted with multi-signature provenance — stronger A5 receipts than §13.1 can produce.
- Plus: external auditors can verify the chain's legitimacy without trusting any single operator.

### §3.6 What remains forbidden

- All `MAYOR_ADMISSION_PROTOCOL_V0 §10` patterns.
- Any seal lacking the declared quorum signature count.
- Any single operator unilaterally admitting anything (the entire point of N-of-M).
- Changing quorum policy without quorum approval.
- Counting a re-used signature toward the N (each signature must be a fresh attestation of the specific seal, not a delegated authority token).

---

## §4. Option §13.3 — Deferred bootstrap / stay RAW

### §4.1 Election action

Two operationally equivalent forms:

- **Recorded deferral**: operator writes a `BOOTSTRAP_ELECTION_V0` receipt declaring path §13.3 with rationale and a review-by date (e.g., "review in 90 days; if no re-election by then, deferral continues by default").
- **Implicit deferral**: no election receipt is written. The system simply continues at RAW.

**Recommended form**: recorded deferral. An explicit receipt makes the deferral a deliberate decision visible to the control plane, not a forgotten one indistinguishable from oversight.

### §4.2 Receipts required

- Optional but recommended: one `BOOTSTRAP_ELECTION_V0` receipt declaring §13.3
- Nothing else. No identities, no seals, no genesis, no chain.

### §4.3 What can go wrong

- **Indefinite RAW accumulation.** Doctrines never become canon. Tools never get cited as admitted. Capabilities never promote. Schemas drift informally.
- **Ossification.** The longer §13.3 holds, the more the system normalises "everything is RAW" as the default. Future bootstrap becomes harder politically because the deferral becomes the equilibrium.
- **Reseed pressure builds.** Governance signals continue surfacing via `reseed_topics.py`, but cannot be resolved by ratification — only by addressing them in further RAW artifacts, which themselves cannot be ratified.
- **Code/doctrine divergence.** The cockpit's read-before-write fix (`f0a9520`) implements `RECEIPT_SAFE_MUTATION_PROTOCOL_V0 §6 #2` operationally. As more code is written under the influence of RAW doctrine, the gap between "what the code does" and "what is admitted canon" widens. Eventually a maintainer may diverge from RAW doctrine without anyone noticing, because RAW is not enforced as canon.
- **External-claim limit.** Cannot honestly assert "HELEN OS enforces receipt law" to any external party. Only "HELEN OS implements receipt law in RAW form." May matter for partnerships, integrations, or audits.

### §4.4 Revocability

- **Trivially reversible.** Just elect §13.1 or §13.2 later. Deferral is not a commitment, it is the absence of one.
- A recorded deferral receipt can be superseded by a new election receipt at any time.
- Net: §13.3 is the **most reversible** option. It imposes the least lock-in of the three.

### §4.5 What becomes possible after election

- **Nothing new becomes admittable.** The system continues exactly as it is today.
- Reseed → doctrine → control-plane review continues working.
- RAW artifacts accumulate, get reviewed via cockpit, get cross-cited in other RAW artifacts.
- The two existing doctrines stay at RAW but remain operationally observed where implementation already exists.

### §4.6 What remains forbidden

- Everything in `MAYOR_ADMISSION_PROTOCOL_V0 §10`, vacuously (no admissions happen).
- **Any implicit claim that an artifact is admitted.** RAW means RAW. Tools and code must not refer to "admitted canon" in their docstrings while §13.3 holds.
- **Trust-by-precedent reasoning.** "We've been using this RAW doctrine for six months, surely it's canon now" is exactly the drift §13.3 must prevent. Time-in-RAW does not promote anything.
- Direct filesystem writes to `helensh/.state/admitted_canon.jsonl` — the file should not exist under §13.3; if it does exist, it is suspect.

---

## §5. Comparison matrix

| Dimension | §13.1 Single-operator | §13.2 N-of-M quorum | §13.3 Deferred |
|---|---|---|---|
| **Election cost** | 1 attestation + 6 seals | M-key setup + N attestations + 6 seals | 0 (or 1 deferral receipt) |
| **Iteration speed after** | high (1 sig per seal) | low-medium (N sigs if compound) | not applicable |
| **Capture resistance** | very low (1 key) | medium-high (depends on M, N) | high (no power to capture) |
| **Liveness on operator loss** | none | survives up to M − N defections | always live |
| **Graceful revocability** | no (chain destruction only) | yes (quorum revokes) | yes (just change election) |
| **External auditability** | weak ("trust the operator") | medium-strong (multi-sig) | not applicable (nothing admitted) |
| **Risk of self-admission bias** | high | medium (operators may collude) | zero (no admission) |
| **Risk of ossification** | low | low | high (the failure mode of §13.3) |
| **Time pressure to choose** | low | medium (must declare M first) | none (this *is* the no-choice path) |
| **Distance from §13.3** | one decisive step | two decisive steps | zero — already here |

---

## §6. Hybrid considerations

Three hybrid paths are reachable from the three above. They are not bootstrap paths in their own right but staged approaches:

### §6.1 §13.1 → §13.2 promotion

Bootstrap via §13.1, then immediately admit a `QUORUM_DECLARATION_V0` as the first significant act, and revoke the single-operator MAYOR in favour of a compound MAYOR. This trades a brief single-operator window for fast initial setup. The window must be measured in hours, not weeks, or it becomes §13.1 in practice.

### §6.2 §13.3 with scheduled review

§13.3 with an explicit review date forces the operator to confront the deferral periodically. If review consistently re-elects §13.3, that is *also a signal* — either the system is stable at RAW (a real outcome) or the operator is avoiding the bootstrap question (a different real outcome).

### §6.3 §13.2 with "shadow §13.1"

A quorum is declared (§13.2) but the M operators agree informally that one of them holds operational primacy. Avoid this. It is §13.1 with quorum theatre and combines the weaknesses of both.

Hybrids §6.1 and §6.2 are legal under this protocol. §6.3 is forbidden as a deliberate misrepresentation of the bootstrap path.

---

## §7. Election receipt schema (`BOOTSTRAP_ELECTION_V0`)

Sketch — not yet admitted, not yet binding. Refinement is required before any election attempt.

| Field | Type | Semantics |
|---|---|---|
| `schema_name` | string | `"BOOTSTRAP_ELECTION_V0"` |
| `schema_version` | string | semver |
| `election_hash` | string | SHA-256 of canonical body excluding `election_hash` and timestamps |
| `election_timestamp_utc` | string | ISO-8601 UTC; outside hashed body |
| `chosen_path` | string | one of `"§13.1"`, `"§13.2"`, `"§13.3"` |
| `chosen_path_rationale` | string | ≥ 128 chars of justification |
| `operator_identities` | list[object] | for §13.1: one identity. For §13.2: M identities with public keys. For §13.3: at least the deciding operator |
| `quorum_policy` | object | required iff `chosen_path == "§13.2"`: `{N, M, mode: "single_by_quorum"|"compound"}` |
| `bootstrap_attestations` | list[object] | for §13.1: one operator signature. For §13.2: N signatures. For §13.3: at least the deciding operator's signature |
| `review_by_date` | string | ISO-8601 UTC; required for §13.3, optional otherwise |
| `supersedes_election_hash` | string \| null | pointer to prior election receipt if any (allows re-election) |
| `authority` | bool | **always `false`** — election is a procedural act, not sovereignty |

Election receipts live at `GOVERNANCE/BOOTSTRAP_ELECTIONS/election_<timestamp>.json` (new directory; M2 mutation class).

---

## §8. Recommendation

This recommendation is advisory. The operator is the deciding authority.

**Recommended current posture: stay at §13.3 with a recorded deferral.**

Reasons:

1. **No information is lost.** Reseed and control plane continue operating. The system can observe whether ratified canon is actually needed before committing to a bootstrap path.
2. **Maximum reversibility.** §13.3 is the only option that can be exited toward either of the other two without chain rewrite.
3. **The bootstrap election is itself a decision worth aging.** A bootstrap signed within an hour of reading this document is exactly the rushed-genesis pattern that §0 warns against.
4. **The existing two doctrines are operationally useful as RAW.** `RECEIPT_SAFE_MUTATION_PROTOCOL_V0 §6 #2` is enforced in the cockpit today. Admission would be a *legitimacy* gain, not a *capability* gain.
5. **§13.1 is reachable from §13.3 at any time.** §13.2 is reachable but requires `QUORUM_DECLARATION_V0` to exist first — drafting that doctrine is the precondition for §13.2 readiness and is a meaningful next step regardless of when bootstrap actually happens.

The recommendation is **not** to elect §13.3 permanently. It is to elect §13.3 with an explicit review-by date (suggested: 90 days from the election receipt), so the deferral is deliberate and bounded.

If the operator prefers immediacy:

- **For solo development now, accept §13.1 limitations:** elect §13.1, accept single-operator capture as a known risk, plan §6.1 promotion to §13.2 once a second trustable operator/key exists.
- **For multi-operator readiness:** draft `QUORUM_DECLARATION_V0` first (a doctrine task, not a bootstrap task), then elect §13.2 directly.

---

## §9. Halt boundary

GOBLIN halts here. This doctrine is RAW. It does not elect. It does not specify the MAYOR implementation. It does not write to `admitted_canon.jsonl` (a file which, under current §13.3, must not exist).

The only action this document performs is **the act of being written and made available for operator review**. It is itself an M5 derived artifact per `RECEIPT_SAFE_MUTATION_PROTOCOL_V0 §3` — not state, not canon, just a candidate for future admission by the very gate it helps the operator decide whether to construct.

Resume conditions:

1. **HER attestation**: HER reviews §2–§7 against the parent doctrine and the current control-plane state.
2. **HAL review (recorded)**: HAL receives this doctrine as a M2 proposal envelope.
3. **Operator decision (recorded)**: `APPROVED_FOR_SANDBOX_ONLY`, `REJECTED`, or `PENDING_REVIEW` — annotated via cockpit on this proposal receipt once routed.
4. **Operator election** (separate act, separate receipt): operator writes a `BOOTSTRAP_ELECTION_V0` receipt declaring §13.1, §13.2, or §13.3 with full §7 fields populated. This is the act that potentially ends the freeze. It is not performed by GOBLIN.

Until election happens:

```
NO MAYOR SEAL = NO ADMITTED CANON
```

Stand down preserved.
