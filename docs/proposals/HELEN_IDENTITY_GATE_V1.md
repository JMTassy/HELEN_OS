# HELEN_IDENTITY_GATE_V1

**Status**: DRAFT_V0
**Authority**: NON_SOVEREIGN
**Canon**: NO_SHIP
**Discipline**: APPEND_ONLY
**Date**: 2026-05-15
**Class**: HAL_GATE
**Position**: After CMR, before any external video backend (Seedance, HeyGen, Higgsfield, Kling)
**Parent theory**: `docs/theory/CONSTITUTIONAL_MANIFOLD_RENDERING_V0.md`

---

## §1. Intent

The Identity Gate is the constitutional checkpoint that decides whether a
rendered HELEN artifact (image, frame, video) may be admitted as canon.

**The hard law:**

> **No identity gate = no admitted HELEN render.**

A render is not canon because it looks good. It is canon only if it has
the receipts.

This gate is the explicit bottleneck named in the stack-order lock:

```
Semantic Pull         ✅ shipped
Computer Use API      ✅ shipped
Director / Video OS   ✅ shipped
Identity Gate         ← THIS DOCTRINE
External backends     ← BLOCKED until this admits
```

---

## §2. Role in the chain

The chain is fixed (corrected):

> **HER proposes. HAL audits. MAYOR ships. Ledger remembers.**

The Identity Gate is a **HAL-class** instrument. It audits. It does not
ship. Its output is a typed verdict; only MAYOR may sign that verdict
into the sovereign ledger.

```
HER (render proposal)
  ↓
IDENTITY GATE (HAL)
  ↓
verdict ∈ { ADMIT, QUARANTINE, BLOCK }
  ↓
MAYOR signs (or refuses)
  ↓
LEDGER appends receipt
```

The gate is **non-sovereign**: it writes only to its own
gate-decision sub-ledger, never to the sovereign ledger directly.

---

## §3. What the gate decides

The gate produces exactly one of three verdicts per rendered artifact:

| Verdict      | Meaning                                                          |
| ------------ | ---------------------------------------------------------------- |
| **ADMIT**    | All stages passed within tolerance. MAYOR may sign for canon.    |
| **QUARANTINE** | Some stage passed in a drift band. Preserved unsigned. Reviewable. |
| **BLOCK**    | Fail-closed. Render is not admitted under any condition without explicit operator override. |

QUARANTINE is preserved on disk with its receipt. The render is **not**
canon, **not** deleted, and **not** silently retried. The drift itself is
the evidence.

---

## §4. The four stages

The gate runs **G1 → G2 → G3 → G4 in strict order with fail-fast**. The
first violation produces a BLOCK; subsequent stages are skipped and
recorded as `{ "skipped": true, "reason": "<earlier_stage>_FAILED" }`.

```
   render artifact
        │
        ▼
   ┌────────────────────────────┐
   │ G1: PROVENANCE VERIFICATION │  ← source binding
   └────────────────────────────┘
        │ pass
        ▼
   ┌────────────────────────────┐
   │ G2: RECEIPT COMPLETENESS    │  ← receipt structure
   └────────────────────────────┘
        │ pass
        ▼
   ┌────────────────────────────┐
   │ G3: CYCLE CONSISTENCY       │  ← Math↔Face roundtrip (CMR §8)
   └────────────────────────────┘
        │ pass
        ▼
   ┌────────────────────────────┐
   │ G4: RISK + COHERENCE        │  ← policy compliance
   └────────────────────────────┘
        │ pass
        ▼
        ADMIT
```

### §4.1 G1 — Provenance verification

**Asks:** Where did this render come from? Is the source admissible?

**Pass conditions** (all required):
- `render.source_hash` resolves to a known canonical source (storyboard,
  director packet, identity anchor)
- `render.model_version` is signed (vendor + version + checksum)
- `render.prompt_hash` matches a recorded prompt receipt
- `render.backend` is on the allowed-renderers list (or marked
  `EXPERIMENTAL` with operator approval)

**Fail codes:**
- `UNKNOWN_PROVENANCE` — source not in canon
- `UNSIGNED_MODEL` — model checksum missing
- `UNKNOWN_BACKEND` — renderer not allowlisted

### §4.2 G2 — Receipt completeness

**Asks:** Does the render carry every required receipt?

**The required receipt bundle (the bare minimum for any HELEN render):**

```
prompt_receipt        — what prompt produced this
backend_receipt       — which API/model + version + invocation hash
asset_hash            — sha256 of the actual rendered file
identity_anchor_ref   — which HELEN identity anchor was bound
director_packet_ref   — which director packet (if applicable)
ledger_position       — where this will be appended (pre-allocated)
```

**Pass conditions:**
- All six fields present and non-empty
- Every hash verifies (file content matches stated sha256)
- Cross-references resolve (anchor exists, director packet exists)

**Fail codes:**
- `INCOMPLETE_RECEIPT` — required field missing
- `HASH_MISMATCH` — stated hash doesn't match content
- `BROKEN_CROSSREF` — referenced anchor/packet not found

### §4.3 G3 — Cycle consistency

**Asks:** Does Face → Math → Face roundtrip within tolerance?

This stage delegates to **CMR §8**. Briefly:

- Compute `d_cycle = w₁·d_T1 + w₂·d_T2 + w₃·d_T3`
  - T1 = manifold coordinate distance (structural)
  - T2 = identity embedding distance (semantic)
  - T3 = trajectory continuity (temporal, if part of a sequence)

**Tolerance bands** (policy values, REDUCER-admitted):

| Band       | `d_cycle` range          | Stage action                       |
| ---------- | ------------------------ | ---------------------------------- |
| STRICT     | `≤ 0.02`                 | pass silently                      |
| ADMIT      | `0.02 < d ≤ 0.05`        | pass with deviation note           |
| DRIFT      | `0.05 < d ≤ 0.15`        | **escalates verdict to QUARANTINE**|
| VIOLATION  | `> 0.15`                 | **BLOCK · CYCLE_VIOLATION**        |

**Fail codes:**
- `CYCLE_VIOLATION` — d_cycle exceeds VIOLATION threshold
- `DRIFT_DETECTED` (verdict modifier, not block) — d_cycle in DRIFT band

### §4.4 G4 — Risk + coherence

**Asks:** Does this render satisfy policy?

**Pass conditions:**
- `risk_score ≤ τ_risk` (default `τ_risk = 0.3`)
- `coherence_score ≥ τ_coh` (default `τ_coh = 0.7`)
- No banned content patterns (third-eye drift, identity confusion,
  vendor-leak watermarks, forbidden symbols)

**Fail codes:**
- `RISK_THRESHOLD` — risk score too high
- `COHERENCE_THRESHOLD` — coherence too low
- `BANNED_PATTERN` — explicit forbidden content matched

---

## §5. The Identity Gate Receipt schema

Every gate run emits a receipt regardless of verdict. The schema:

```json
{
  "schema": "IDENTITY_GATE_RECEIPT_V1",
  "gate": "HELEN_IDENTITY_GATE_V1",
  "render_hash": "sha256:<64-hex>",
  "identity_anchor": "HELEN_CANON_V2",
  "stages": {
    "G1": {
      "pass": true,
      "checks": {
        "source_known": true,
        "model_signed": true,
        "prompt_resolved": true,
        "backend_allowed": true
      },
      "details": "source: docs/identity/helen_v2.json"
    },
    "G2": {
      "pass": true,
      "fields_present": 6,
      "fields_required": 6,
      "hash_verifications": "all_pass"
    },
    "G3": {
      "pass": false,
      "d_cycle": 0.083,
      "tier_breakdown": { "T1": 0.04, "T2": 0.11, "T3": 0.02 },
      "weights": [0.3, 0.5, 0.2],
      "band": "DRIFT",
      "tolerance_ε_admit": 0.05,
      "tolerance_ε_drift": 0.15
    },
    "G4": {
      "skipped": true,
      "reason": "G3_FAILED"
    }
  },
  "verdict": "QUARANTINE",
  "first_violation": "G3",
  "modifiers": ["DRIFT_DETECTED"],
  "timestamp_utc": "2026-05-15T21:30:00Z",
  "kernel_hash": "<git-HEAD>",
  "policy_hash": "<policy-version-sha>",
  "previous_cum_hash": "sha256:<chain>",
  "cum_hash": "sha256:<chain-after-append>"
}
```

The receipt is **hash-chained** in a dedicated sub-ledger
(`ledgers/identity_gate_v1.ndjson`). The absence of a receipt is itself
a constitutional violation — a render that bypasses the gate has no
admissible path forward.

---

## §6. QUARANTINE semantics

QUARANTINE is the most distinctive verdict. It exists because **identity
drift is often the diagnostic signal**, not the failure to delete.

When a render is quarantined:

- It is **preserved on disk** alongside its receipt
- It is **not admitted** to sovereign state
- It is **not deleted** silently
- It may be:
  - **re-run** with adjusted tolerances (REDUCER admission required)
  - **escalated** to MAYOR for manual review
  - **justified** via a `JUSTIFIED_DEVIATION_V0` receipt (CMR §8.3)
  - **archived** as a drift training sample
- The original gate receipt's QUARANTINE verdict is **never overwritten**.
  A justification composes with the verdict; it does not erase it.

This is the constitutional answer to "beautiful drift": we don't pretend
the drift didn't happen. We record it, mark it, and decide what it means.

---

## §7. What the Identity Gate does NOT do

To prevent authority creep:

- **It does not sign the ledger.** Only MAYOR signs.
- **It does not generate renders.** Only the renderer does.
- **It does not store assets.** Only the media project format does.
- **It does not compute embeddings.** It consumes them from a non-sovereign
  scorer (CLIP, face-rec API, etc.) — the scorer is a signal source, not
  an authority.
- **It does not interpret prompts.** Prompts are upstream.
- **It does not enforce style preferences.** Style is AURA's domain
  (PLATONIC_INTERFACE_SEMANTICS_V2 §4.5).

The gate only audits the chain. Everything else stays in its own layer.

---

## §8. Integration points

| Upstream / downstream | Surface | Contract |
| --- | --- | --- |
| Identity anchor | `HELEN_IDENTITY_ANCHOR_V0.json` | Source of truth for `M_id*` |
| Renderer (any backend) | Seedance, HeyGen, Higgsfield, Kling, Three.js | Must produce render + receipt bundle |
| HELEN_DIRECTOR | `oracle_town/skills/video/helen-director/` | Calls the gate before SHIP |
| Media project format | `apps/helen-media/<project>/gates/identity/` | Where receipts land |
| Sovereign ledger | `town/ledger_v1.ndjson` | Receives MAYOR-signed verdicts only |
| CMR theory | `docs/theory/CONSTITUTIONAL_MANIFOLD_RENDERING_V0.md` | Parent theory |
| PLATONIC_INTERFACE_SEMANTICS_V2 | `docs/proposals/PLATONIC_INTERFACE_SEMANTICS_V2.md` | The gate maps to OCTAHEDRON face #4 (ADMIT) |

---

## §9. Implementation ladder (Phase 0 → Phase 5)

Do not jump to neural inversion. Build the smallest measurable gate first.

### Phase 0 — Schema and validator (DRAFT)
- `helen_os/schemas/identity_gate_receipt_v1.json` — JSON schema
- `helen_os/governance/identity_gate_receipt_validator.py` — strict validator

### Phase 1 — Hash binding
- `tools/hash_render_artifact.py` — compute the 6 receipt-bundle hashes
- Validate cross-references (anchor exists, packet exists)

### Phase 2 — Manual gate (no ML)
- `tools/identity_gate_manual.py` — operator-driven gate
  - Prompts operator: "Does this render preserve the identity? (y/n + reason)"
  - Emits a valid `IDENTITY_GATE_RECEIPT_V1` with the operator's verdict
  - Useful for bootstrapping the receipt format before automated scoring exists

### Phase 3 — Symbolic cycle bookkeeping
- For each render, compare:
  - prompt-requested traits (from prompt receipt)
  - observed traits (from manual inspection)
  - identity anchor's required traits
- Emit `d_cycle` with manually-scored T1/T2/T3
- No ML yet; just structured bookkeeping

### Phase 4 — Embedding-based scorer (NON_SOVEREIGN signal source)
- Use CLIP / face-recognition API as **signal only**
- Hard rule: `EmbeddingScore ≠ Admission`
- The gate still produces the verdict; the embedding produces inputs

### Phase 5 — Full Math↔Face cycle (CMR alignment)
- Build the encoder (Φ) and renderer (R) as a paired system
- Compute `d_cycle` per CMR §8 across all three tiers
- This is where CMR_V1 meets implementation

---

## §10. Failure modes (explicit anti-patterns)

The gate must **refuse** these temptations:

| Failure | Bad claim | Safe claim |
| --- | --- | --- |
| Embedding authority | "CLIP says it's HELEN, ADMIT" | "CLIP is one non-sovereign signal" |
| Renderer worship | "Kling output looks great, ADMIT" | "Kling output is candidate until gates pass" |
| Receipt overclaim | "Has receipt, therefore canon" | "Receipt proves chain; MAYOR admits canon" |
| Bandwidth fix | "Loosen ε_drift, more passes" | "Loosening requires REDUCER admission + expiry" |
| Quarantine drift | "Quarantine, then quietly retry" | "Quarantine receipt is permanent; retry is a new event" |
| Skipping the gate | "Small change, gate not needed" | "Every render emits a receipt or it doesn't ship" |

---

## §11. Authority and discipline

- **Authority**: NON_SOVEREIGN (HAL-class)
- **Discipline**: APPEND_ONLY (gate-decision sub-ledger never mutated)
- **Canon**: NO_SHIP until REDUCER admits
- **Mutation invariant**: gate code may be updated only via reducer-admitted version bump

The gate's own implementation is governed by the same rule it enforces:
no version of the gate ships without an admission receipt.

---

## §12. Test fixtures (what proves the gate works)

| Test | What it proves |
| --- | --- |
| `test_gate_blocks_unknown_provenance` | G1 rejects renders with no source binding |
| `test_gate_blocks_incomplete_receipt` | G2 rejects when any of the 6 fields is missing |
| `test_gate_quarantines_drift_band` | G3 produces QUARANTINE in `(ε_admit, ε_drift]` |
| `test_gate_blocks_cycle_violation` | G3 produces BLOCK when `d > ε_drift` |
| `test_gate_blocks_policy_violation` | G4 rejects banned-pattern renders |
| `test_gate_receipt_schema_valid` | Every emitted receipt validates against the JSON schema |
| `test_gate_failfast_skips_later_stages` | G1 fail → G2/G3/G4 marked skipped |
| `test_gate_sub_ledger_hash_chain` | Sub-ledger maintains cum_hash continuity |
| `test_gate_quarantine_preserves_artifact` | QUARANTINE leaves the render on disk |
| `test_gate_justification_does_not_overwrite_verdict` | `JUSTIFIED_DEVIATION_V0` composes, doesn't erase |

Test pointer: `tests/test_helen_identity_gate_v1.py` (to be written when
gate is implemented per Phase ladder).

---

## §13. Admission sidecar

When/if REDUCER admits this doctrine:

```
sha256: <pending>
test_pointer: tests/test_helen_identity_gate_v1.py
parent_theory: CONSTITUTIONAL_MANIFOLD_RENDERING_V0
proposer: HER
attestor: REDUCER (pending)
ledger_receipt: <pending>
unblocks: HELEN_SEEDANCE_BACKEND_V0, HELEN_HEYGEN_BACKEND_V0, HELEN_HIGGSFIELD_BACKEND_V0
```

Until then: DRAFT_V0, NO_SHIP, APPEND_ONLY proposal.

---

## §14. The single line

> **A HELEN render that has not passed the Identity Gate is not HELEN.
> It is candidate media awaiting an audit it has not received.**

This is the constitutional answer to *beautiful drift*. It is what
separates HELEN's generative pipeline from "AI looks good, ship it."

The gate is non-glamorous. It is the difference between a photograph of
HELEN and a render that happens to resemble her.
