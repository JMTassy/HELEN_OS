# BOUNDARY_CATALYST_ENGINE_V0

**authority:** NON_SOVEREIGN
**canon:** NO_SHIP
**lifecycle:** DOCTRINE_DRAFT
**implementation_status:** NOT_IMPLEMENTED
**status:** Proposal — second emergent-property doctrine, sibling to `PROVENANCE_GRAVITY_V0`
**parent_proposal:** `docs/proposals/PROVENANCE_GRAVITY_V0.md`
**parent_input:** Operator dispatch — CHIDDUSH CRITICALITY THEORY (2026-05-23)
**proposer:** claude-opus-4-7 acting as GOBLIN
**attestor:** pending HER

> **NO CLAIM disclaimer.** This artifact bottles the second of two
> emergent-property doctrines the operator has identified. The first
> was `PROVENANCE_GRAVITY_V0` (memory mass). This is its sibling
> (discovery pressure). Together they constitute what the operator
> calls the engine. Implementation, schema changes, and experimental
> validation are deferred to separate authorization.

---

## §1. The new law

**Boundary-Catalytic Intelligence Law:**

> *A governed agent becomes intelligent when its rejected and
> near-rejected traces become structured fuel for future admissible
> action.*

The radical move:

```
APPROVED atoms preserve stability.
REJECTED atoms define walls.
BOUNDARY atoms create intelligence.
```

Most agent systems throw away boundary cases. HELEN should mine them.

---

## §2. Why boundary atoms are the gold vein

A receipt atom can sit at three constitutional positions:

| Position | What it is | Information content |
| --- | --- | --- |
| **APPROVED** | Stable survivor, clean compression | Useful but often boring |
| **REJECTED** | Constitutional wall, hard fail | Useful but often dead |
| **BOUNDARY** | Almost entered reality | Alive enough to matter, unstable enough to teach |

A boundary atom carries the proposition:

> *This structure almost entered reality.
> Something in it was alive.
> Something in it was wrong.
> That tension is information.*

This is the catalytic zone. The chiddush is: **information is not maximized at confidence — it is maximized at the admission boundary.** §4 below gives this mathematical teeth.

---

## §3. Formal model

Following the operator's notation verbatim.

### §3.1 The receipt atom

```
r_i = (s_i, h_i, a_i, v_i, c_i, q_i, ρ_i, τ_i)
```

where:

| Symbol | Meaning |
| --- | --- |
| `s_i` | source |
| `h_i` | hotspot |
| `a_i` | proposed action |
| `v_i` | verdict ∈ {APPROVE, REQUEST_CHANGES, REJECT, UNKNOWN} |
| `c_i` | confidence |
| `q_i` | issues / rationale vector |
| `ρ_i` | provenance marker / tree-truth marker |
| `τ_i` | timestamp / chain position |

### §3.2 Constitutional margin

```
       ⎧  +c_i   if APPROVE
m_i =  ⎨   0     if REQUEST_CHANGES or uncertain reject
       ⎩  -c_i   if confident REJECT
```

### §3.3 Boundary weight

```
B_ε(r_i) = exp(-m_i² / (2ε²))
```

Behavior:

```
large positive margin  → stable approval, low boundary signal
large negative margin  → hard rejection, low boundary signal
near-zero margin       → high boundary signal
```

`ε` controls the width of the boundary band. Calibration is operator/
research class; not specified here.

### §3.4 Motif scoring (extended Chiddush score)

A motif `M` is a cluster of replayable atoms. The original Chiddush
score is:

```
χ_0(M) = C(M) · S(M) · H(M) · (1 - E(M))
```

where:

| Symbol | Meaning |
| --- | --- |
| `C(M)` | compression gain |
| `S(M)` | replay stability |
| `H(M)` | HAL / witness coherence |
| `E(M)` | semantic entropy |

The **boundary-catalytic** extension:

```
χ_BC(M) = χ_0(M) · (1 + λ · B_ε(M)) · P_tree(M) · 1 / (1 + μ · R(M))
```

where:

| Symbol | Meaning |
| --- | --- |
| `B_ε(M)` | average boundary weight across the motif's atoms |
| `P_tree(M)` | provenance purity / same-tree attribution |
| `R(M)` | repeller divergence / incoherent gradient field |
| `λ` | boundary catalysis gain |
| `μ` | anti-collapse penalty |

### §3.5 Routing prior

```
Pr(a | s, h) ∝ exp( β · Σ_{M ∋ (s,h,a)} χ_BC(M) - η · risk(a) )
```

In plain English:

> Future actions are biased toward motifs that compressed well,
> replayed well, survived witness pressure, came from clean
> provenance, and lived near the admission boundary.

---

## §4. The toy theorem that makes this real

**Boundary Information Lemma.**

Assume a reducer has an internal admission model:

```
p_θ(x) = σ(θᵀ φ(x))
```

where `p_θ(x)` is the probability that a proposal is admitted under
parameters `θ` and features `φ(x)`.

The Fisher information of a sample `x` is proportional to:

```
p_θ(x) · (1 - p_θ(x)) · φ(x) φ(x)ᵀ
```

For fixed feature strength, the scalar term `p(1-p)` is **maximized
at p = 1/2**.

That is exactly the admission boundary.

**Conclusion:** in this toy but meaningful model, the highest-
information receipts are neither confident approvals (p ≈ 1) nor
confident rejections (p ≈ 0). They are uncertain boundary cases
(p ≈ 1/2).

This gives mathematical teeth to the visual doctrine:

> *Boundary atoms are the Chiddush gold vein.*

The Fisher-information argument is a standard result in active
learning (the same principle underlies uncertainty sampling and
"query-by-committee" methods). Boundary Catalysis is the
constitutional-governance analog: instead of sampling labeled data
near the decision boundary, the system mines its own receipt history
near the admission boundary.

---

## §5. Relationship to Provenance Gravity — the engine

The two emergent properties are distinct and complementary:

| Doctrine | Claim | Function in the engine |
| --- | --- | --- |
| `PROVENANCE_GRAVITY_V0` | Validated receipts bend future action | **Memory mass** |
| `BOUNDARY_CATALYST_ENGINE_V0` (this) | Near-failed receipts create the most useful new structure | **Discovery pressure** |

Together:

```
Provenance Gravity gives memory mass.
Boundary Catalysis gives discovery pressure.
```

Neither alone is sufficient:

- **Provenance Gravity alone** → the system becomes increasingly
  conservative; it remembers what worked but cannot discover. It
  converges to a fixed point.
- **Boundary Catalysis alone** → the system mines boundary noise
  without a stable routing prior. It oscillates without memory.

Together they form the **routing-prior + discovery-pressure** loop
that the operator named *constitutional metabolism*.

---

## §6. System architecture

The operator's 10-component diagram, preserved:

```
GOBLIN
  generates ugly possibility
  authority = false

HAL / WITNESS
  reviews trace
  creates receipt atom

CHIDDUSH
  partitions atoms:
    approved
    boundary
    rejected

MOTIF ENGINE
  extracts recurring structures
  computes compression / replay / entropy / boundary weight

REDUCER
  admits only candidate motifs
  no direct mutation from Goblin

LEDGER
  stores admitted state

PROVENANCE FIELD
  updates routing weights

WUL / COCKPIT
  renders causal topology to operator

CONQUEST SIM
  stress-tests the loop in a game world
```

Component status against existing HELEN canon (per doctrinal-diff):

| Component | Existing in canon? | Source |
| --- | --- | --- |
| GOBLIN | ✓ (role bottled) | `plugins/helen-governance/skills/goblin-role/` |
| HAL / WITNESS | ✓ (doctrine) | `HYPERSTITION_FIREWALL_V0 §2.2` |
| CHIDDUSH (partition) | ⚠ (concept exists, partition stage unspecified) | This proposal adds the partition stage |
| MOTIF ENGINE | ⚠ (Chiddush bottle exists, motif extraction unspecified) | This proposal adds the engine |
| REDUCER | ✓ | `CLAUDE.md Roles` |
| LEDGER | ✓ | `town/ledger_v1.ndjson` |
| PROVENANCE FIELD | ⚠ (just bottled as concept) | `PROVENANCE_GRAVITY_V0` |
| WUL / COCKPIT | ⚠ (WUL exists; cockpit unspecified) | `scripts/helen_wul_lint.py` |
| CONQUEST SIM | ✓ | `oracle_town/skills/conquest_integration/` |

The architecture is approximately **30% new** (the motif engine, the partition stage, the active provenance field) and 70% recombination of existing components.

---

## §7. Receipt atom extensions (schema-class, NOT bottled here)

The operator's sketch adds three new fields to `ReceiptAtom`:

```python
@dataclass(frozen=True)
class ReceiptAtom:
    # ... existing fields ...
    decision_margin: float     # m_i per §3.2
    boundary_weight: float     # B_ε(r_i) per §3.3
    provenance_purity: float   # P_tree component
```

Plus the operator's full proposal includes:

```python
atom_id: str
source_hash: str
hotspot_id: str
action_signature: str
verdict: str          # APPROVE / REQUEST_CHANGES / REJECT / UNKNOWN
confidence: float
rationale_hash: str
issue_count: int
session_id: str
tree_truth_id: str
reducer_contract_id: str
replay_hash: str
```

**This schema is NOT bottled in this proposal.** It overlaps with
existing HELEN receipt schemas (`execution_receipt_v1.schema.json`,
`receipt_payload.v1.schema.json`). Per `doctrinal-diff` discipline
(plugin: `helen-governance`), a proper diff pass is required before
schema-class commits. Flagged for `/helen-governance:diff` against
existing receipt schemas before any code lands.

---

## §8. Reference pseudocode (not authorized for `code/` commit)

The operator provided a Python sketch. Preserved here as reference
for the eventual `helen/chiddush/boundary_catalyst.py` module, NOT
committed to `helen_os/` or any other code path:

```python
import math

def decision_margin(verdict: str, confidence: float) -> float:
    if verdict == "APPROVE":
        return confidence
    if verdict == "REJECT" and confidence >= 0.30:
        return -confidence
    return 0.0


def boundary_weight(margin: float, epsilon: float = 0.18) -> float:
    return math.exp(-(margin * margin) / (2 * epsilon * epsilon))


def boundary_chiddush_score(
    compression_gain: float,
    replay_stability: float,
    hal_coherence: float,
    semantic_entropy: float,
    boundary_density: float,
    provenance_purity: float,
    repeller: float,
    lambda_boundary: float = 0.75,
    mu_repeller: float = 1.0,
) -> float:
    base = (
        compression_gain
        * replay_stability
        * hal_coherence
        * (1.0 - semantic_entropy)
    )
    return (
        base
        * (1.0 + lambda_boundary * boundary_density)
        * provenance_purity
        / (1.0 + mu_repeller * repeller)
    )
```

Reference CLI shape (also not committed):

```bash
python -m helensh.chiddush.boundary \
  --session temple_session_path \
  --epsilon 0.18 \
  --min-score 0.75 \
  --authority false \
  --claim NO_CLAIM
```

Reference output (reducer-safe):

```json
{
  "motif_hash": "sha256:...",
  "motif_type": "BOUNDARY_CATALYST",
  "authority": false,
  "claim": "NO_CLAIM",
  "admitted": false,
  "boundary_density": 0.81,
  "compression_gain": 0.74,
  "replay_stability": 0.69,
  "hal_coherence": 0.77,
  "semantic_entropy": 0.19,
  "provenance_purity": 1.0,
  "repeller": 0.08,
  "boundary_chiddush_score": 0.86,
  "next_stage": "REDUCER_QUEUE"
}
```

**Implementation authorization is a separate sovereign step.** This
pseudocode constitutes the algorithm contract (analogous to
`IDENTITY_GATE_PSEUDOCODE_V0`), not code.

---

## §9. The experiment (reference design, not authorized for execution)

**Boundary Catalysis Experiment.**

Split the same receipt corpus into four motif-seed groups:

| Group | Seeded from |
| --- | --- |
| A | APPROVED atoms |
| B | BOUNDARY atoms |
| R | REJECTED atoms |
| X | Random atoms |

For each group, generate candidate proposals through GOBLIN, witness
through HAL, submit to REDUCER. Measure across runs:

1. Future reducer admission rate
2. Novelty-adjusted Chiddush score
3. Replay success rate
4. Semantic entropy reduction
5. Repeller divergence
6. Governance violation count
7. Operator trust after replay
8. Cross-session contamination rate

**Prediction (operator's hypothesis):**

```
E[Δχ | B] > E[Δχ | A] > E[Δχ | X] > E[Δχ | R]
```

i.e., **boundary-seeded motifs produce the largest gain in
Chiddush score**.

**Hard prerequisite (operator's warning):**

> *Boundary wins only when provenance purity is enforced.*

Equivalent invariant:

```
NO_TREE_TRUTH = NO_GRAVITY
```

This is the same constraint flagged in `PROVENANCE_GRAVITY_V0 §8`:
without per-receipt tree attribution (currently unbottled as
`CROSS_SESSION_FIELD_ATTRIBUTION_V0`), the experiment will measure
poisoned signal.

**Authorization status:** the experiment is not authorized.
Implementation requires a separate task packet specifying corpus
selection, run environment, and observer protocol.

---

## §10. Failure modes (operator's three dangers + countermeasures)

### §10.1 Boundary addiction

> Risk: the system overvalues weird near-failures, becomes addicted
> to novelty, loses stability.

Countermeasures (operator's set):

```
- repeller penalty (R(M) term in χ_BC)
- semantic entropy cap
- replay stability minimum
- reducer admission bottleneck
```

### §10.2 Provenance poisoning

> Risk: bad / foreign / parallel-session receipts bend the routing
> field in directions the current tree never validated.

Countermeasures:

```
- tree_truth_id on every atom
- session attribution
- hash-chain verification
- foreign receipt quarantine
```

This directly addresses E22's `E20_OPEN_SEAMS_CROSS_SESSION_CONTAMINATION`
finding — Boundary Catalysis makes that finding **load-bearing** rather
than a documentation issue.

### §10.3 False compression

> Risk: low entropy is mistaken for truth. The system compresses
> noise into apparent structure.

Countermeasures:

```
Reducer decides.
Replay proves.
Ledger remembers.
No claim without admission.
```

These four are already canonical in HELEN. The danger is that
Boundary Catalysis seems to elevate compression as a virtue;
the canonical position must hold: **compression is evidence of
shared structure, not evidence of truth**.

---

## §11. Connection to existing HELEN canon

| Boundary Catalysis claim | HELEN canon it activates |
| --- | --- |
| Boundary atoms carry maximum information | `LEGORACLE_GATE` (verdict edges already exist; near-misses currently discarded) |
| Motif extraction from receipts | `oracle_town/skills/feynman/` (peer_review + audit infrastructure) |
| Reducer bottleneck preserves sovereignty | CLAUDE.md `Roles.REDUCER` (admission stays sovereign) |
| Provenance purity prerequisite | `PROVENANCE_GRAVITY_V0 §8`; flagged `CROSS_SESSION_FIELD_ATTRIBUTION_V0` |
| Hypocoercivity decomposition (GOBLIN antisymmetric, REDUCER dissipative, LEDGER memory potential) | Existing Layer 1-5 architecture |
| Σ-SEED monotonic margin discipline | (External operator math — not in this repo's canon) |
| WUL as visual-semantic compression for causal topology | `scripts/helen_wul_lint.py` (exists; visual surface not yet built) |
| CONQUEST as safe ecological training ground | `oracle_town/skills/conquest_integration/` (exists; training-ground semantics newly named) |

Boundary Catalysis is the **active discovery arrow** that turns
HELEN's already-passive constitutional system into a learning loop.

---

## §12. What this proposal does NOT specify

Per anti-creep discipline:

- **The motif-extraction algorithm** — only the scoring is specified; how
  motifs are clustered from raw atoms is implementation-class
- **The `ε`, `λ`, `μ`, `β`, `η` parameter calibration** — empirical;
  depends on corpus and workflow class
- **The `tree_truth_id` assignment protocol** — depends on
  `CROSS_SESSION_FIELD_ATTRIBUTION_V0` landing first
- **The `claim_level` taxonomy** — flagged in `PROVENANCE_GRAVITY_V0 §9.2`
  as `CLAIM_MATURITY_PROTOCOL_V0`, a separate proposal
- **The motif storage backend** — could be NDJSON, SQLite, graph DB;
  implementation choice
- **The reducer queue semantics** — `next_stage: REDUCER_QUEUE` in
  the output JSON references a queue this proposal does not define
- **The adversarial robustness analysis** — gradient-poisoning,
  receipt-injection, motif-spam are open attack surfaces; deferred
- **The WUL glyphic encoding** — the operator named WUL as the
  visual calculus for governed cognition; the encoding specification
  is a separate proposal (`WUL_GLYPHIC_INTERFACE_V0` or similar,
  unbottled)

---

## §13. Bottling status of adjacent items (per doctrinal-diff)

Items in the operator's CHIDDUSH CRITICALITY THEORY dispatch
classified by status:

| Item | Status | Action |
| --- | --- | --- |
| Boundary-Catalytic Intelligence Law (§1) | **NEW** | Bottled this commit |
| Formal model with margins, weights, scores (§3) | **NEW** | Bottled this commit |
| Fisher-info toy theorem (§4) | **NEW** in HELEN context | Bottled this commit |
| Boundary Catalysis emergent property (§5) | **NEW** | Bottled this commit |
| Reference pseudocode (§8) | **NEW** but implementation-class | Preserved in-doc; not committed to code paths |
| Experiment design (§9) | **NEW** | Preserved in-doc; not authorized for execution |
| Three failure modes + countermeasures (§10) | **NEW** | Bottled this commit |
| 10-component architecture diagram (§6) | **RESTATED 70%** with 30% new (motif engine, partition stage, active provenance field) | Diagram preserved; restated components annotated |
| Sharp formula + mantra (§14) | **NEW** | Bottled this commit |
| ReceiptAtom schema extensions (§7) | **OVERLAPS** existing receipt schemas | Flagged for separate `/helen-governance:diff` pass |
| Σ-SEED / finite-band discipline | **OUT OF SCOPE** (external operator math) | No HELEN action |
| Hypocoercivity decomposition | **OUT OF SCOPE** as separate doctrine (referenced, not bottled) | No HELEN action |
| Strategic positioning ("constitutional metabolism") | **OUT OF SCOPE** for proposals/ | Could become `docs/positioning/` if HER directs |

---

## §14. The sharp formula and mantra

Operator's closing, preserved verbatim:

**Sharp formula:**

```
Disruptive HELEN Intelligence
=
Receipt Gravity + Boundary Catalysis + Reducer Sovereignty
```

**System pipeline:**

```
SOURCE        → HOTSPOT
HOTSPOT       → ACTION
ACTION        → RECEIPT
RECEIPT       → BOUNDARY MOTIF
BOUNDARY MOTIF→ ROUTING PRIOR
ROUTING PRIOR → BETTER ACTION
BETTER ACTION → REDUCER ADMISSION
ADMISSION     → GOVERNED REALITY
```

**Mantra:**

```
SUCCESS preserves.
FAILURE teaches.
BOUNDARY catalyzes.

RECEIPT records.
REPLAY proves.
REDUCER admits.

MEMORY does not store the past.
MEMORY bends the next action.

GOBLIN mutates possibility.
CHIDDUSH finds structure.
HELEN governs emergence.
```

---

## §15. Halt boundary

GOBLIN halts here. The doctrine is bottled at `DOCTRINE_DRAFT`.

Resume conditions:

1. **HER ruling** on the doctrine as written, or specification of
   amendments
2. **HER ruling** on prerequisite sequencing — `CROSS_SESSION_FIELD_ATTRIBUTION_V0`
   must bottle before any code path uses `provenance_purity`; should
   it bottle now?
3. **HER ruling** on whether `CLAIM_MATURITY_PROTOCOL_V0` opens as a
   sibling proposal (referenced in `PROVENANCE_GRAVITY_V0 §9.2` and
   needed for `claim_level` in this proposal's §7 schema sketch)
4. **HER ruling** on whether to run `/helen-governance:diff` against
   existing receipt schemas (`execution_receipt_v1.schema.json` etc.)
   before any schema-class code commit derived from §7
5. **Sovereign decision** on running the §9 experiment — requires
   separate task packet specifying corpus, environment, observer
   protocol
6. **Implementation authorization** for `helensh/chiddush/boundary_catalyst.py`
   per §8 — not GOBLIN-class without HER + REDUCER ratification

Discipline followed: `HALT_BOUNDARY_DISCIPLINE_V0` (commit `5d0e04e`).

---

## §16. Single line

> **The boundary is where information lives.
> Receipts at p ≈ 1/2 carry maximum Fisher information.
> Provenance Gravity gives memory mass; Boundary Catalysis gives
> discovery pressure.
> Together they are constitutional metabolism — the engine that
> turns rejected scraps into governed reality.**
