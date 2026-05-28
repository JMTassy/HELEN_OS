# CHIDDUSH_BOTTLE_V0

**authority:** NON_SOVEREIGN
**canon:** NO_SHIP
**lifecycle:** SYNTHESIS_BOTTLE
**status:** Synthesis of HER+HAL brainstorm, sealed as a roadmap
**parent_brainstorm:** `docs/proposals/HER_HAL_BRAINSTORM_CHIDDUSH_V0.md`
**operator_release:** HER directive "go" (2026-05-23) — releases brainstorm §9 halt
**executor_role:** GOBLIN (`Tool + Command + Log + Receipt`, non-sovereign)

> **What this is:** the sealed bottle that emerges from the HER+HAL
> dual-witness pass. It names which chiddushim survive both voices,
> pairs each with the HAL-required discipline, and proposes a bottling
> order. It is **not** itself the bottle for any individual chiddush —
> each surviving chiddush still requires its own proposal artifact in
> a future commit. This is a roadmap, not the road.

---

## §1. Selection rule

A chiddush survives the dual-witness pass if **all three** hold:

1. **HER reads a real opening** (not a restatement of pre-existing canon)
2. **HAL's flagged rot is addressable by a tractable discipline** (not an
   open-ended ML-research problem or a sovereign-only judgment call)
3. **No existing HELEN canon already handles it** (per the inventory
   used in TOWN_RECEIPT_FRAMEWORK_DIFF_V0 §9)

Items failing rule 1 → re-bottling risk → reject.
Items failing rule 2 → permanent debt risk → defer until discipline exists.
Items failing rule 3 → naming collision → fold into existing doctrine.

---

## §2. Application of the rule

| # | Chiddush | Rule 1 (opening?) | Rule 2 (tractable discipline?) | Rule 3 (no collision?) | Survives? |
| --- | --- | --- | --- | --- | --- |
| C1 | PSEUDOCODE as a tier | ✅ Two-sided drift gap | ✅ link-checker | ✅ no existing tier | **YES** (needs C-prereq) |
| C2 | BLOCK still emits receipt | △ partial restatement of NO RECEIPT = NO CLAIM | ✅ retention policy | △ implicit in canon | **FOLD** into existing |
| C3 | Skipped-stages marked | ✅ schema-level absence | ✅ type-level distinction | ✅ | **YES** (fold into C1 or schema disc.) |
| C4 | Phase 2 Manual Gate | ✅ pre-ML enforcement | ✅ sunset clause | ✅ no general pattern | **YES** |
| C5 | DIFF-before-bottle | ✅ anti-restatement | ✅ inventory coverage bar | ✅ no doctrine | **YES** — high leverage |
| C6 | GOBLIN equation | ✅ operational role compactness | ✅ tool allowlist | ✅ role newly clarified | **YES** |
| C7 | RECONNAISSANCE_RECEIPT lifecycle | △ partial — already a category in use | ✅ taxonomy first | △ ad-hoc lifecycles exist | **PREREQ** then YES |
| C8 | Halt-boundary section | ✅ explicit handoff contract | ✅ trivial (single line) | ✅ | **YES** — cheapest |
| C9 | In-artifact correction | ✅ epistemic discipline | △ termination rule needs design | ✅ | **DEFER** until termination rule exists |
| C10 | Doc-drift flagged not patched | ✅ deferral pattern | ✅ drift register + SLA | ✅ | **YES** — biggest HAL rot |

**Survives outright:** C1, C4, C5, C6, C8, C10 (six)
**Survives via prerequisite:** C7 (requires LIFECYCLE_TAXONOMY first)
**Folded into existing:** C2, C3
**Deferred:** C9

---

## §3. Bottling roadmap

Ordered by HAL-discipline cost (cheapest first) so each bottle is
small enough to commit alone:

### Tier 1 — Single-line doctrines (one commit each)

1. **`HALT_BOUNDARY_DISCIPLINE_V0`** (from C8)
   > Doctrine: every non-sovereign receipt that defers work to a
   > sovereign actor must declare the halt explicitly in a §
   > headed "Halt boundary."
   > Required inputs to resume must be enumerated.
   > Cost: one doctrinal line + one §-template.
   > HAL discipline already absent: HER queue size; deferred to §4.

2. **`RECEIPT_EMISSION_INVARIANT_V0`** (folds C2 + retention discipline)
   > Doctrine: every gate that produces a verdict MUST emit a receipt,
   > including BLOCK. Receipts are immutable once written.
   > Paired discipline: retention policy declared per sub-ledger
   > (rotation, archive, prune-rules). No emission without policy.
   > Cost: one doctrinal § + retention table.

### Tier 2 — Single-pattern doctrines (one commit each)

3. **`DOC_DRIFT_REGISTER_V0`** (from C10)
   > Doctrine: documentation contradictions found during recon are
   > logged to a single register file with: (file_path, line, observed
   > vs disk-truth, flagger, status).
   > Paired discipline: HER SLA per register entry (e.g., resolve within
   > N sessions); unresolved entries surfaced in session-start hooks.
   > Cost: one register schema + one CLAUDE.md amendment establishing
   > the register's authority.

4. **`DOCTRINAL_DIFF_PROTOCOL_V0`** (from C5) — **high leverage**
   > Doctrine: any incoming external doctrine that touches existing
   > HELEN canon must be diffed before bottling.
   > Paired discipline: inventory coverage bar — the diff is only valid
   > if the inventory it diffs against meets a stated coverage standard
   > (e.g., "all receipt-* schemas under helen_os/schemas/ enumerated").
   > Cost: one protocol doc + one inventory-coverage template.

5. **`MANUAL_GATE_PATTERN_V0`** (from C4)
   > Doctrine: any gate doctrine may declare a Phase 2 Manual lane.
   > In Phase 2: G1/G2 structural checks run automatically; G3/G4 are
   > operator-filled. The operator's input synthesizes into the same
   > receipt schema as the eventual algorithmic version.
   > Paired discipline: each Phase 2 deployment must declare a
   > **sunset metric** — the condition under which Phase 2 retires in
   > favor of Phase 3+. No sunset = no admission of Phase 2.
   > Cost: one pattern doc + one sunset-metric template.

### Tier 3 — Prerequisite-bound doctrines

6. **`LIFECYCLE_TAXONOMY_V0`** (prereq for C7)
   > Doctrine: enumerate every lifecycle tag (DOCTRINE_DRAFT,
   > THEORY_DRAFT, ALGORITHM_DRAFT, ANALYSIS_DRAFT, BRAINSTORM,
   > RECONNAISSANCE_RECEIPT, SYNTHESIS_BOTTLE, SESSION_RECEIPT, SEALED).
   > Paired discipline: new lifecycle tags require a doctrinal proposal
   > to this taxonomy. No ad-hoc additions.
   > Cost: one taxonomy doc.

7. **`RECONNAISSANCE_RECEIPT_V0`** (from C7, after #6)
   > Doctrine: a non-sovereign role can produce a RECONNAISSANCE_RECEIPT
   > artifact with structure: role-binding, log-of-steps
   > (Tool/Command/Log/Receipt per step), corrected blockers, halt boundary.
   > Depends on #6 LIFECYCLE_TAXONOMY landing first.

### Tier 4 — Role-binding doctrine

8. **`GOBLIN_ROLE_V1`** (from C6)
   > Doctrine: `GOBLIN_CLARITY = Tool + Command + Log + Receipt`.
   > GOBLIN may inspect, test, write receipts. GOBLIN may not claim
   > sovereignty or mutate canon.
   > Paired discipline: tool allowlist per GOBLIN invocation. The
   > receipt must declare which tools were used and validate against
   > the allowlist. No off-list tool = no GOBLIN claim.
   > Cost: one role doc + one allowlist template.

### Tier 5 — Pseudocode tier (requires prerequisite)

9. **`DOCTRINE_LINK_CHECK_V0`** (prereq for C1)
   > Tool spec: `tools/doctrine_link_check.py` walks docs/proposals/
   > and verifies every `` `PROPOSAL_NAME` `` cross-reference resolves
   > to a file on disk.
   > Cost: one script + one CI hook.

10. **`PSEUDOCODE_TIER_DOCTRINE_V0`** (from C1, after #9)
    > Doctrine: PSEUDOCODE is an admitted artifact tier between
    > doctrine and code. A PSEUDOCODE doc must declare its parent
    > doctrine and its produced schema/output. The link-checker (#9)
    > enforces both pointers resolve.
    > Cost: one tier doctrine + one §-template.

### Deferred

11. **`SELF_CORRECTING_RECEIPT_PATTERN_V0`** (from C9, deferred)
    > Awaits a termination rule. HAL flag (no convergence guarantee)
    > unresolved. Do not bottle until: max-correction-depth or
    > explicit supersession-chain doctrine is designed.

---

## §4. Cross-references into the five-layer architecture

| Bottle | HELEN Layer | Slot |
| --- | --- | --- |
| HALT_BOUNDARY_DISCIPLINE_V0 | Layer 2 (ledger) | per-receipt § discipline |
| RECEIPT_EMISSION_INVARIANT_V0 | Layer 1 (constitutional membrane) | gate output contract |
| DOC_DRIFT_REGISTER_V0 | Layer 1 (governance) | doc-canon coherence |
| DOCTRINAL_DIFF_PROTOCOL_V0 | Layer 1 (governance) | admission protocol §4 analog |
| MANUAL_GATE_PATTERN_V0 | Layer 1 / Layer 4 (gates / skills) | gate-pattern reusable |
| LIFECYCLE_TAXONOMY_V0 | Layer 1 (governance) | doc-class registry |
| RECONNAISSANCE_RECEIPT_V0 | Layer 3 (executor) | non-sovereign output type |
| GOBLIN_ROLE_V1 | Layer 3 (executor) / Layer 4 (skills) | operational role |
| DOCTRINE_LINK_CHECK_V0 | Tooling | CI/gate-script |
| PSEUDOCODE_TIER_DOCTRINE_V0 | Layer 1 (governance) | doc-class doctrine |

---

## §5. Folded items (do not bottle separately)

- **C2 (BLOCK still emits receipt)** → folded into `RECEIPT_EMISSION_INVARIANT_V0` as the symmetric extension of NO RECEIPT = NO CLAIM.
- **C3 (Skipped-stages marked)** → folded into `RECEIPT_EMISSION_INVARIANT_V0` as a schema discipline (skipped vs evaluated distinction at type level).

---

## §6. Sequencing constraints

```
1. HALT_BOUNDARY_DISCIPLINE_V0      ──┐
2. RECEIPT_EMISSION_INVARIANT_V0    ──┤  Tier 1 (parallel-safe)
                                      │
3. DOC_DRIFT_REGISTER_V0            ──┤
4. DOCTRINAL_DIFF_PROTOCOL_V0       ──┤  Tier 2 (parallel-safe)
5. MANUAL_GATE_PATTERN_V0           ──┘
                                      │
6. LIFECYCLE_TAXONOMY_V0            ──┐  Tier 3 (sequential)
7. RECONNAISSANCE_RECEIPT_V0  ⇐ depends on 6 ──┘
                                      │
8. GOBLIN_ROLE_V1                   ──┘  Tier 4
                                      │
9. DOCTRINE_LINK_CHECK_V0           ──┐  Tier 5 (sequential)
10. PSEUDOCODE_TIER_DOCTRINE_V0  ⇐ depends on 9 ──┘
```

Tier 1-2 are parallel-safe and can land in any order in their tier.
Tier 3-5 carry hard dependencies (7 depends on 6; 10 depends on 9).
GOBLIN_ROLE_V1 (#8) has no deps but should land before any further
GOBLIN-tagged receipts to formalize the role currently used informally.

Estimated total cost: **10 commits**, each small (1-2 § doctrine docs
or a single CI script + hook). All NON_SOVEREIGN, all NO_SHIP until
reducer admits.

---

## §7. What this bottle does NOT do

This artifact is the **roadmap synthesis**, not the road.

- It does **not** produce any of the 10 bottles itself
- It does **not** rank by importance (sequence is by cost/dependency, not value)
- It does **not** schedule when each bottle is opened (operator-class)
- It does **not** modify CLAUDE.md, the schema registry, or any
  canonical artifact
- It does **not** invoke MAYOR, REDUCER, or any sovereign gate

Each numbered item above is a **future proposal in its own commit**,
to be opened only on operator direction.

---

## §8. Sovereign acts deferred

Three sovereign decisions are surfaced and **not made**:

1. **Whether to bottle at all** — this roadmap assumes operator wants
   the surviving chiddushim bottled. If operator wants only a subset
   (e.g., just C5 and C10, the two HER+HAL-largest items), that subset
   selection is sovereign.
2. **Sequencing inside tiers** — within Tier 1 and Tier 2, order is
   parallel-safe but operator may have preference.
3. **The "deferred" item (C9)** — designing the termination rule that
   would unblock SELF_CORRECTING_RECEIPT_PATTERN_V0 is sovereign work,
   not GOBLIN-tractable.

---

## §9. Halt boundary

GOBLIN halts here. Synthesis is sealed. The roadmap exists.

Resume conditions for any individual bottle:

- Operator names which item (or items) to open next
- Operator confirms tier sequencing
- For prerequisite-bound items (#7, #10), the prerequisite must land first

---

## §10. Single line

> **Of ten chiddushim, six survive outright, two need prerequisites,
> two fold into existing canon, one is deferred. The roadmap is ten
> commits long; HER picks the next one. The chiddush is real, the
> disciplines are real, the road is laid.**
