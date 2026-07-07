# OVERNIGHT_SURVIVORS.md
# OVERNIGHT_BAD_IDEA_ELIMINATION_LOOP — Final Output
# authority=false | canon=false | ledger_effect=none | NO_CLAIM
# Status: HOLD_FOR_OPERATOR

Produced by: OVERNIGHT_BAD_IDEA_ELIMINATION_LOOP
Tranches run: 1 (survey + elimination)
Scanned: 8 optimization surfaces
Eliminated: 16
Hold: 5
Survivors: 15

---

## WHAT SURVIVES

### Governance kernel

| ID | Item | Why it survives |
|---|---|---|
| S-02 | `autoresearch_step_v1.py` core design | NO RECEIPT = NO CLAIM enforced at function level |
| S-03 | `autoresearch_batch_v1.py` bounded semantics | Hard cap, fail-closed, schema validation before mutation |
| S-04 | `do_next_v1.py` request validation | Defensive, thorough, complete |
| S-05 | `do_next_v1.py` state hash computation | Canonical JSON + field-exclusion before hash — correct |
| S-06 | `do_next_v1.py` atomic file save | tmp + rename — correct operational pattern |
| S-12 | `skill_admission_checker/` + `reference_drift_witness/` | Both tested, bounded scope, non-sovereign |
| S-13 | `CONSUMER_ALLOWLIST` kernel guard mechanism | Correct design; stale content (fix via MAYOR route) |
| S-15 | Gate 8 / GATE-001 capability manifest SHA | Implemented, 13/13 tests green, HOLD_FOR_OPERATOR |

### Knowledge / retrieval

| ID | Item | Why it survives |
|---|---|---|
| S-07 | `engine.py` access receipt logging + MMR-lite | authority=NONE on every access, diversity enforced |

Note: `engine.py` keyword/tag retrieval SURVIVES. `ingest.py` Gemini embedding pipeline SURVIVES as an alternative. The problem (E-03) is that neither is designated canonical. The modules themselves are not bad ideas.

### Operator UX / visual grammar

| ID | Item | Why it survives |
|---|---|---|
| S-08 | `helen2027.html` CSS variable system | One-meaning-per-color, semantic tokens, consistent |
| S-09 | Dual-track UX design (2027 + home_v1) | Deliberate modality split, not duplication |
| S-14 | Sandbox visual grammar proposals | Coherent visual language spec (ANOMALY_GRAMMAR, VISUAL_CANON_LOCK, INTERACTION_GRAMMAR) |

### Research / doctrine

| ID | Item | Why it survives |
|---|---|---|
| S-10 | Governance proposal strand | MANIFEST_GATE_V1, AUTORESEARCH_SAFE_ARCH, GAS_V0, BOUNDED_RECEIPT_WULMATH, E11/E12 RECONCILIATION — all connected to live code or active governance |
| S-11 | Transport Theory strand (9 documents) | Research substrate for GAS V0 proof obligations — non-sovereign, not connected to sovereign code paths |

### Most urgent route

| ID | Item | Required action |
|---|---|---|
| S-01 | AR-cecf4c5b553f.json (Kernel Guard risk packet) | Route via MAYOR_REVIEW_PACKET immediately. Red-gate normalization is the active risk. 3-week drift window on certification layer. |

---

## WHAT WAS ELIMINATED

| ID | Item | Elimination reason |
|---|---|---|
| E-01 | `_infer()` stub | False inference surface — passthrough echo named as inference |
| E-02 | `continuity_score` ghost field | 1.0 always, never computed, false signal in receipt and UI |
| E-03 | Dual ingestion (as a non-decision) | No canonical path = dirty state. Must resolve, not maintain |
| E-04 | `sources.py` macOS absolute paths | Dead configuration in Linux environment |
| E-05 | `skill_discovery_v1.py` dead field reads | `task_id` doesn't exist in schema; `failure_type` → `reason_code` |
| E-06 | `ingest.py` Python 3.14 hardcode | Breaks on current Python 3.11 runtime |
| E-07 | `ingest.py` zero-vector fallback | Silent wrong result for failed embeddings |
| E-08 | Self-improve loop silent INFERENCE_FAILED | 0 admissions looks like governance rejection, not infrastructure failure |
| E-09 | Hardcoded `LEDGER-0001` ID in batch | Non-unique ledger IDs break identity guarantees |
| E-10 | Quality scorer trivial gate | Any non-empty proposal passes — false selectivity |
| E-11 | `engine.py` "hybrid" mode overclaim | Identical to keyword mode with tag pre-filter |
| E-12 | Filename heuristic tags in `engine.py` | Project-specific strings baked into general module |
| E-13 | Video director version pollution (9 pilots) | No canonical version; iteration history in production code |
| E-14 | `#geo-canvas` "SACRED GEOMETRY CANVAS" | Mystically-named placeholder with no implementation |
| E-15 | `session["memory"]` unbounded growth | No cap on memory list written to disk every call |
| E-16 | `SessionStore._locks` memory leak | Lock objects never evicted, grow with unique session count |

---

## WHAT IS HELD (good idea, wrong state)

| ID | Item | Blocking dependency |
|---|---|---|
| H-01 | `/init ranking` | Blocked on E-01. No inference surface to rank against. |
| H-02 | Context ranking | Blocked on E-01 + E-03. No canonical retrieval path + no inference. |
| H-03 | Prompt compression / summarization weights | Blocked on E-03. Weights are reasonable; no canonical substrate. |
| H-04 | Epoch ceiling (HARD_REJECT) with warning | Not eliminated. Needs warning receipt at epoch 990. |
| H-05 | `skill_discovery_v1.py` module | Dead field reads (E-05) are bugs, not design flaws. Fix fields → survivor. |

---

## PRIMARY BLOCKING CHAIN

```
E-03 (no canonical ingestion)
  → H-02 (context ranking unanchored)
  → H-03 (summarization weights unanchored)

E-01 (_infer() stub)
  → H-01 (/init ranking no substrate)
  → H-02 (context ranking no inference target)
  → E-02 (continuity_score can't be computed)

E-01 + E-02 + E-03
  → XC-02 (false signal chain from API to UI)
```

Nothing in the "/init ranking / context ranking / prompt compression / skill routing / summarization weights" optimization surface should be built until E-01 and E-03 are resolved.

---

## MOST COMPRESSED VERDICT

**What is real and bounded:** governance kernel (receipts, ledger, reducer, gates), operator UX visual grammar, research/doctrine corpus, AR risk packet routing.

**What is speculative or false:** inference surface (stub), continuity signal (ghost), knowledge retrieval (dual-path without arbiter), quality gate (trivially passable), hybrid mode (overclaimed name).

**What is urgent:** Route AR-cecf4c5b553f. Fix Kernel Guard CONSUMER_ALLOWLIST. Red-gate normalization is the most dangerous form of drift: architecture holds while certification rots.

---

## INVARIANTS CONFIRMED BY ELIMINATION PASS

```
_infer() = passthrough ⊬ inference surface
continuity_score = 1.0 always ⊬ computed continuity
hybrid mode = keyword + tag ⊬ semantic retrieval
quality_score ≥ 0.5 for any 6-field packet ⊬ quality gate
macOS path ⊬ Linux resolution
```

```
NO RECEIPT = NO CLAIM                        [held]
TRACE ≠ RECEIPT                              [held]
DIRTY ROOT ⊬ SAFE TARGET                    [held — E-03 blocks H-02/H-03]
RED GATE NORMALIZATION = CERTIFICATION RISK  [active — route AR-cecf4c5b553f]
```

---

HOLD_FOR_OPERATOR
