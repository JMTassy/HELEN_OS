# TEMPLE_RENDER_VERIFICATION_V1

**Render law for the TEMPLE UI: the interface is a function of verified ledger state, never a memory of it.**

**Status:** SPEC_DRAFT
**Authority:** NON_SOVEREIGN
**Canon:** NO_SHIP
**Layer:** 5 (TEMPLE Exploration — generative, non-sovereign)
**Proposer:** operator (Jean-Marie Tassy Simeoni)
**Origin:** `RALPH_W 15` visual meditation, epochs 1–15 (TRACE_ONLY), 2026-05-29
**Attestor:** pending HAL
**Parent invariant:** `NO RECEIPT = NO CLAIM`

---

## §1. Purpose

The TEMPLE UI renders the garden — blooms, petals, the living Merkle tree.
A rendered garden is presentation. The ledger is memory. This spec exists to
prevent the classic dashboard failure mode:

```text
pretty interface
  → stale cached state
  → operator believes it
  → false reality
```

The failure is constitutional, not cosmetic: when a cached bloom is trusted
as truth, `NO RECEIPT = NO CLAIM` collapses silently. No verdict is emitted,
no breach is logged, and the operator's belief diverges from the chain while
feeling like knowledge.

This spec converts the meditation's principle — *beauty must expose mechanism,
not hide it* — into an enforceable render law.

---

## §2. Render law

The single invariant from which everything else derives:

```text
render = verify ∘ ledger.head
```

In words:

```text
The UI is not memory.
The UI is a live rendering of verified ledger state.
```

The lock line:

> **The garden is rendered, never remembered.**

Formally, render state is a pure function of the verified ledger head:

```text
render_state = pure_fn(verify(ledger.head))
render_state ∉ canon
```

Two consequences follow immediately:

1. **Render state is non-canonical.** Nothing the UI displays is itself a
   claim. The UI may show a claim; it may never *be* one.
2. **`ledger.head` is the only source of render truth.** No render path may
   originate from UI memory, a snapshot, or a cache of validity.

---

## §3. Freshness gate

Every render passes through the gate before pixels commit:

```text
open(gate) ⟺ verify(cum_hash, ledger.head)
```

- Verification succeeds → the gate opens, the garden renders.
- Verification fails → the garden does not open. There is no degraded bloom,
  no "last known good" fallback that masquerades as current.

Freshness is **layered validation, not recency.** A petal is fresh when its
anchor receipt verifies against the current head — not merely when it was
fetched recently. A recently-cached but unverified bloom is stale by law.

```text
fresh(petal) ⟺ verify(petal.anchor, ledger.head)
```

The gate is the **only** render path. No performance bypass for cached blooms.
Latency is honest; a bypass is a silent canon-mutation path and is forbidden
(see §8).

---

## §4. Living Merkle ground

The Merkle tree is not a sidecar panel. It is the soil the garden grows from.

```text
trunk   = receipts
branches= hash chains
leaves  = payloads
root    = cum_hash
flower.root_path = merkle_path(receipt, ledger.head)
```

Growth rule:

```text
tree.root_t = sha256(tree.root_{t−1} ‖ receipt_t.payload_hash)
```

Binding requirements:

- **Every visual element has an anchor.** `∀ visual_element ∃ anchor_hash`,
  displayed adjacent to the element — never two clicks deep behind a "details"
  panel.
- **Every bloom requires its proof.** A petal opens only after its Merkle path
  is rendered: `render(bloom) ⟸ verify(merkle_path(receipt, root))`.
- **A node without lineage does not render.** Phantom growth — a branch grown
  without root verification — is a beautiful tree on a broken chain, and is
  rejected at render time.

---

## §5. Cache rules

Caching is permitted only where it cannot become ontology.

```text
ALLOWED (cache these):
  - Merkle paths
  - source text previews
  - inspection history
  - layout positions

FORBIDDEN (never cache these):
  - bloom validity
  - admitted status
  - reducer verdict as visual truth without refetch
  - any "verified" badge rendered from stale UI memory
```

The dividing line:

```text
cached path  = allowed   (it is re-verifiable against head)
cached bloom = forbidden (it asserts validity the head has not confirmed)
```

Invalidation rule: **every cache invalidates on `cum_hash` advance.** A path
cache survives only until the head moves; a bloom cache never exists at all.

---

## §6. Staleness rendering

Staleness is a first-class render target, not a hidden state.

```text
when staleness > 0:  render(staleness) ≥ render(beauty)
```

- The alarm is **inline-visual, never audio.** Audio fatigues; visual
  mutilation does not. A stale petal bruises; the bruise spreads to its branch.
- Lag is displayed openly: e.g. *"anchor 3 receipts behind, last verified 4s
  ago."* When lag is present, the label is large and the bloom is small.
- Past a threshold, the bloom **collapses entirely** rather than labelling
  itself stale. Beyond N receipts of drift, render is **blocked** until a
  forced refetch — the block is the gate; the glow is only the warning.

UI-cache divergence from the live head renders as a divergence glow on the
divergent branch:

```text
|ui_cache.root − live_tree.root| > 0  ⟹  render(divergence_glow)
divergence > N receipts                ⟹  render blocked until refetch
```

---

## §7. Beauty constraint

Beauty is permitted, on one condition:

```text
beauty = proof made visible
```

- Mechanism must be visible at the **same depth** as the bloom — not behind it.
  `ux_priority(beauty) > ux_priority(verifiability)` is the failure condition.
- A proof's rendered shape must derive from the path bytes themselves. No two
  proofs render identically; a proof that becomes ornament (same silhouette
  repeated) has stopped being read and has failed the constraint.
- Aesthetic coherence can counterfeit truth. Therefore **prominence is
  constrained by verification depth**: an element may be only as visually
  prominent as its proof is deep and current.

The meditation's lock, restated as a constraint:

> The garden may bloom. The ledger must verify. Beauty must expose mechanism,
> not hide it.

---

## §8. Forbidden UI states

These states are constitutional breaches at the render layer. Each must be
unreachable by construction, not merely discouraged.

```text
1. Rendering a bloom whose anchor does not verify against ledger.head.
2. Caching bloom validity, admitted status, or reducer verdicts as visual truth.
3. A "verified" badge sourced from stale UI memory without refetch.
4. A render path that bypasses the freshness gate ("performance" fast-path).
5. Snapshot view set as the default, or persisting beyond its opt-in window.
6. Mechanism (Merkle tree, anchor hashes, proofs) hidden behind a deeper UI
   level than the bloom it backs.
7. Silent decay: staleness present but not rendered at ≥ the prominence of beauty.
8. UI state treated as ontology — the cache believed instead of the chain.
```

The governing principle behind all eight:

```text
UI state must never become ontology.
```

---

## §9. Implementation checklist

```text
[ ] render_state is a pure function of verify(ledger.head)
[ ] freshness gate is the sole render path; no bypass exists
[ ] every visual element displays its anchor hash adjacent (not nested)
[ ] every bloom renders its Merkle proof before opening
[ ] proof silhouette derives from path bytes (no two identical)
[ ] cache layer stores only: paths, source previews, inspection history, layout
[ ] cache layer cannot store: bloom validity, admitted status, verdicts
[ ] every cache invalidates on cum_hash advance
[ ] staleness renders at ≥ prominence of beauty when present
[ ] alarm is inline-visual (bruise/wilt), never audio
[ ] drift > N receipts blocks render until forced refetch
[ ] snapshot view is opt-in, time-boxed, never default
[ ] no "verified" badge renders from UI memory
```

---

## §10. Final compression

```text
The flower is presentation.
The root is proof.
The bloom is temporary.
The ledger is memory.
The UI must re-render truth, not remember it.
```

Single line:

```text
render = verify ∘ ledger.head
```

Lock:

```text
The garden is rendered, never remembered.
```

---

## §11. Halt boundary

This is a SPEC_DRAFT at Layer 5 (TEMPLE, non-sovereign). It defines render law;
it does not implement it and emits no verdict.

**Required to advance to implementation:**
- HAL attestation of the forbidden-state set (§8) as complete
- A target TEMPLE UI surface to bind the law to (`helen_simple_ui.py` is the
  current candidate render surface)
- A render-layer test harness that can assert the §9 checklist mechanically

**Not required:**
- MAYOR review of this document (spec draft, not a doctrine ratification)
- Any ledger mutation
- Any kernel change

```text
authority: false  |  claim: NO_CLAIM  |  admitted: false
ledger_mutation: false  |  layer: TEMPLE (5, non-sovereign)
```

---

*Status as of 2026-05-29: render law specified from the RALPH_W 15 visual*
*meditation. Not yet implemented. Awaiting HAL attestation and a bound render*
*surface.*
