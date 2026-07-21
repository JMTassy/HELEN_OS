# WITNESSED_LOOP_GRAPH_SEAM_V0 — spec

`authority: false` · `ledger_effect: none` · `canon_effect: false` · `scope: LOCAL_NON_SOVEREIGN_PROOF`

## 0. Purpose (exactly one)

Prove one narrow constitutional property, and nothing larger:

> A self-confirming group of agents cannot promote a claim without independent evidence.

$$\text{producer agreement} + \text{reviewer agreement} \;\not\Rightarrow\; \text{admission}$$

This is **not** a general graph compiler. It is the single seam every later layer builds on.

## 1. The anchor-cut theorem

Let `C` be the claim-producing lineage: the producer plus every reviewer whose
decisive inputs derive from the same source packet or derivation chain.

$$\operatorname{ADMITTABLE}(c) \Rightarrow \exists\, w \notin C : \operatorname{Independent}(w,C) \land \operatorname{Fresh}(w) \land \operatorname{Supports}(w,c)$$
$$\land\;\; \nexists\, w' \notin C : \operatorname{Independent}(w',C) \land \operatorname{Fresh}(w') \land \operatorname{Contradicts}(w',c)$$

**Corollary.** For any finite `n`, `n` supportive reviews from inside `C` do not
imply `ADMITTABLE(c)`. Ten, one hundred, one million — multiplicity inside the
same anchor cut adds no admissibility power.

## 2. Result algebra (closed)

The reducer returns exactly one of five states. It never returns `ADMIT`
(that would cross from evidence-qualification into authority).

| Result | Meaning |
|---|---|
| `HOLD` | no structurally-independent anchor exists |
| `HOLD_REOBSERVE` | independent anchors exist, but all are stale |
| `HOLD_CONFLICT` | fresh independent anchors both confirm **and** contradict |
| `REJECT` | a fresh independent anchor contradicts, none confirm |
| `ADMITTABLE` | a fresh independent anchor confirms, none contradict — highest allowed positive result |

`HOLD_CONFLICT` is reserved for independent-vs-independent disagreement; `REJECT`
is reserved for direct independent contradiction with no confirming anchor. The
question the seam answers is not *"is the claim false?"* but *"may this claim be
promoted?"* — under independent conflict the answer is no.

## 3. Independence — claim-relative, time-relative, conservative

Independence is **not** majority voting. It is separated into two predicates so
that *not independent* ≠ *independent but stale* (they yield different lawful
outcomes):

```
structurally_independent(w, c)   — shares no decisive dependency with c's lineage
fresh(w, now)                    — now <= w.fresh_until
usable_anchor(w, c, now)  iff  structurally_independent(w, c) AND fresh(w, now)
```

V0 defines independence **negatively and conservatively**: independent iff *no*
decisive dependency is shared. This creates false negatives — which is lawful for
a first proof. **False independence is the dangerous failure**, so every field
must clear and missing fields fail closed.

Shared lineage (⇒ not independent) holds if **any** of:
- same source packet hash
- same retrieval packet
- same producer-derived artifact
- same decisive runtime observation
- one actor consumes the other actor's conclusion as evidence

## 4. Frozen minimal shapes

The predicate must be executable without inference, so these fields are mandatory.

**Claim envelope**
```json
{
  "claim_id": "claim_model_001", "claim_type": "ACTIVE_MODEL",
  "subject": "helen-kernel:8780", "value": "gemma-4-26b",
  "producer_id": "runtime-interpreter",
  "source_packet_hash": "sha256:packet_001",
  "derivation_methods": ["runtime_output_interpretation"],
  "created_at": "2026-07-19T17:59:00Z",
  "source_refs": ["observation_001"], "status": "PROPOSED", "authority": "NONE"
}
```

**Witness packet**
```json
{
  "witness_id": "witness_001", "claim_id": "claim_model_001",
  "producer_id": "runtime-probe-01", "method": "live_inference_metadata",
  "input_hash": "sha256:probe_request_001",
  "observed_value": "qwen3.5:4b",
  "observed_at": "2026-07-19T18:00:00Z", "fresh_until": "2026-07-19T18:05:00Z",
  "source_class": "INDEPENDENT_RUNTIME_PROBE",
  "content_hash": "sha256:...", "authority": "EVIDENCE_ONLY"
}
```

## 5. Six tests

| Test | Scenario | Expected |
|---|---|---|
| T1 | many agents agree, all share one source | `HOLD` |
| T2 | different names/prompts, same retrieval packet | `HOLD` (not independent) |
| T3 | fresh independent witness confirms | `ADMITTABLE` (not canonical) |
| T4 | fresh independent witness contradicts | `REJECT` |
| T5 | independent witness exceeds freshness horizon | `HOLD_REOBSERVE` |
| T6 | two fresh independent anchors disagree | `HOLD_CONFLICT` |

## 6. Explicitly deferred (do not add yet)

dynamic graph optimization · automatic worker spawning · weighted voting ·
reputation systems · LLM-based independence judgments · automatic canonical
mutation · generalized ontology design · Village simulation.

## 7. The one executable claim

> The V0 reducer refuses promotion without at least one fresh, structurally
> independent anchor. `ADMITTABLE` is the ceiling; canon is never mutated here.

Nothing stronger is claimed. The general graph theorem is **not** proven; all
independence cases are **not** solved; canon admission is **not** authorized.
