# TRANCHE 01 — BAD IDEA ELIMINATION
# authority=false | canon=false | ledger_effect=none | NO_CLAIM

Epoch: 1
Loop: OVERNIGHT_BAD_IDEA_ELIMINATION_LOOP
Scanned surfaces: do_next_v1, autonomy/*, knowledge/*, apps/helen-surface/*, oracle_town/skills/, temple/autoresearch/outbox/, docs/proposals/
Method: read-only repo survey → elimination by dirty-state / false-signal / unbounded-growth / overclaim criteria

---

## ELIMINATED — do not carry forward

### E-01 `_infer()` stub in `helen_os/api/do_next_v1.py`
**What it is:** `reply = user_input; return reply, []` — named inference, is a passthrough echo.
**Why eliminated:** Receipt log records `context_count=len(context_items)` but context_items is always []. False signal in every response. Proposals for "context ranking" and "retrieval-augmented inference" downstream of this stub are speculative — the surface doesn't exist yet.
**Rule:** visibility ≠ validity. Stub ≠ inference surface.

### E-02 `continuity_score` ghost field
**What it is:** Initialized to 1.0, never updated, written to every API response, displayed in `home_v1.html #session-delta`.
**Why eliminated:** 3-layer false signal chain: API emits 1.0 always → receipt stamps 1.0 always → UI displays "session continuity: 1.0" always. This is not a feature gap; it is a lie in the receipt.
**Rule:** carried_value ⊬ computed_value. Ghost field in receipt = ERR_RECEIPT_HASH_MISMATCH analog for semantics.

### E-03 Dual ingestion pipelines (`engine.py`/corpus.json vs `ingest.py`/index.json)
**What it is:** Two incompatible ingestion systems for the knowledge base. `engine.py` uses hashtag-keyed keyword retrieval; `ingest.py` uses Gemini embedding cosine similarity. Different index formats, no shared API, no arbitration.
**Why eliminated:** There is no canonical path. Either one is active or neither is. Proposals for "summarization weights" and "retrieval weighting" are unanchored until one path is designated sovereign.
**Rule:** two paths to the same surface = dirty state. Dirty root ⊬ safe target.

### E-04 `sources.py` hardcoded macOS absolute paths
**What it is:** `/Users/jean-marietassy/...` paths in a module that runs on Linux (`/home/user/helen-conquest`). `apple_notes` source points to `/tmp/helen_notes_export` — ephemeral across reboots.
**Why eliminated:** These paths will never resolve in the deployment environment. `KnowledgeEngine` will ingest zero documents from two of its three sources silently.
**Rule:** dead configuration path = ERR_ARTIFACT_MISSING silent variant.

### E-05 `skill_discovery_v1.py` dead field reads
**What it is:** Reads `entry.get("task_id", "unknown")` — field doesn't exist in batch schema (always returns "unknown"). Reads `"failure_type"` — schema uses `"reason_code"`. Both are silent wrong reads.
**Why eliminated:** All task clusters collapse to one cluster named "unknown". All common-context extraction returns empty. The discovery output is structurally meaningless for any real batch.
**Rule:** field mismatch = silent wrong result. Not a minor bug — it breaks the primary function of the module.

### E-06 `ingest.py` Python 3.14 hardcoded path
**What it is:** `sys.path.insert(0, ... "python3.14" ...)` — breaks on Python 3.11 (current runtime) and any other version.
**Why eliminated:** The module cannot run as-written in the current environment. Dead code.

### E-07 `ingest.py` zero-vector fallback on embedding failure
**What it is:** Failed embedding batches fill with `[0.0] * 3072`. Zero vectors have undefined cosine similarity direction — they score as equidistant from all query vectors.
**Why eliminated:** Silent failure masquerades as a retrievable chunk. Chunks that failed to embed will be returned as retrieval results with unpredictable ranking. No error is surfaced.
**Rule:** silent wrong result = worse than explicit error.

### E-08 Self-improve loop silent INFERENCE_FAILED
**What it is:** If Ollama is unavailable or `helen-chat:latest` is missing, all 5 cycles complete with INFERENCE_FAILED. Caller receives `admitted_count=0` with no error flag.
**Why eliminated:** From outside the loop, 0 admissions looks like "nothing qualified" not "infrastructure is down." This hides operational failures behind normal-looking governance rejection.

### E-09 `ledger_id` hardcoded `"LEDGER-0001"` in batch
**What it is:** `autoresearch_batch_v1.py` creates new ledgers with a fixed ID. Concurrent calls share the same ID.
**Why eliminated:** Non-unique IDs break ledger identity guarantees downstream. Small but real.

### E-10 Quality scorer trivial gate in `self_improve_loop_v1.py`
**What it is:** Any proposal with 6 non-empty fields scores 0.5 and passes the quality threshold. There is no content quality check — "observable effects" is a prompt instruction, not verified.
**Why eliminated:** The gate exists but passes trivially. Any proposal with non-empty strings is "quality-gated." This is a false gate — it adds ceremony without selectivity.

### E-11 `engine.py` "hybrid" mode overclaim
**What it is:** `retrieve(mode="hybrid")` is identical to keyword mode with a tag pre-filter. Named "hybrid" to imply combined semantic+lexical retrieval.
**Why eliminated:** Name overclaims the implementation. Downstream proposals that rely on "hybrid semantic retrieval" are speculative until this actually differs from keyword mode.

### E-12 Hardcoded project-specific heuristics in `engine.py`
**What it is:** Tag extraction checks filenames for "helen", "riemann", "swarm", "oracle", "conquest", "agi", "legoracle" (lines ~208-215). These are project-specific strings baked into a general knowledge module.
**Why eliminated:** Makes the module non-reusable and the tags non-principled. Tags should come from content, not filename-pattern matching.

### E-13 Video director version pollution
**What it is:** `oracle_town/skills/video/helen-director/` contains 9 versioned pilot files: v2, v5, v8a through v8g.
**Why eliminated:** No version arbitration, no canonical path, no cleanup. The active version is unknowable from the file listing. The iteration history is living in production code.

### E-14 `#geo-canvas` "SACRED GEOMETRY CANVAS" placeholder
**What it is:** `helen2027.html` declares `#geo-canvas` with `opacity:.72` and the comment "SACRED GEOMETRY CANVAS." No rendering logic visible in the file.
**Why eliminated:** Named mystically but does nothing. Either implement geometry rendering or remove the element. Placeholder with mystical naming is low information.

### E-15 `session["memory"]` unbounded growth
**What it is:** `do_next_v1.py` appends every turn to `session["memory"]` without a cap. Written to disk on every call. `recent_receipts` has a 50-item cap; the full `receipts` list and `memory` do not.
**Why eliminated:** Memory leak in the session file. Long-running sessions grow without bound.

### E-16 `SessionStore._locks` leaked per-session Lock objects
**What it is:** Threading locks created on first session access, never evicted. A process handling many unique session IDs leaks memory proportional to session count.
**Why eliminated:** Operational leak in a server context.

---

## HOLD — good idea, wrong state

### H-01 `/init ranking` surface
**Status:** Dependent on E-01 (`_infer()` stub). The ranking surface has no live inference to rank.
**Correct next step:** Fix `_infer()` first. The ranking idea itself (prioritize recent receipts, high-continuity sessions) is sound — just has no substrate.

### H-02 Context ranking
**Status:** Dependent on both E-01 and E-03 (dual ingestion). Until one knowledge path is canonical, context ranking is unanchored.
**Correct next step:** Resolve E-03 (designate canonical ingestion path), then wire retrieval into `_infer()`.

### H-03 `prompt compression` / `summarization weights`
**Status:** Dependent on E-03. The weighting system in `engine.py` (epistemic priority by source) is a reasonable design. The weights themselves (1.0/0.9/0.8) are editorial but not wrong in principle.
**Correct next step:** Designate canonical path, run experiments, receipt the weights.

### H-04 `HARD_REJECT_EPOCH = 1000` with no warning
**Status:** Not eliminated — epoch ceiling is a legitimate governance bound. But no warning at epoch 999, no reset path, no grace is operationally harsh.
**Correct next step:** Add warning receipt at epoch 990. Not a bad idea; incomplete implementation.

### H-05 `skill_discovery_v1.py` as a module
**Status:** Structurally sound (non-sovereign, deterministic IDs, proposals only). Dead field reads (E-05) are bugs in the implementation, not flaws in the design.
**Correct next step:** Fix field reads (`reason_code` not `failure_type`, `decision_type` not `task_id`), then this module is a survivor.

---

## SURVIVORS — bounded, receipt-backed, retain

### S-01 AR-cecf4c5b553f.json (most recent autoresearch packet)
Well-formed risk packet. authority=false, sovereign=false, reducer_required=true. Specific evidence (commit hashes, timestamps, run dates). Correctly identifies red-gate normalization as the active risk. Should be routed to MAYOR immediately.
**Action needed:** Route via MAYOR_REVIEW_PACKET. Not a code change — a governance routing.

### S-02 `autoresearch_step_v1.py` core design
NO RECEIPT = NO CLAIM enforced at the function level. Ledger append only on ADMITTED. State mutation only on ADMITTED. The placeholder hashes are implementation debt, not design debt.

### S-03 `autoresearch_batch_v1.py` bounded semantics
Hard batch cap, fail-closed on unknown decision types, schema validation before state application. O(N²) replay is a performance note for large batches, not a design defect.

### S-04 `do_next_v1.py` request validation
Input length cap, session_id format validation, type checking, range enforcement. Defensive and complete.

### S-05 `do_next_v1.py` state hash computation
Canonical JSON before hashing, strips hash field before computing. Correct tamper-detection approach.

### S-06 `do_next_v1.py` atomic file save
tmp-file + rename prevents torn writes. Correct operational pattern.

### S-07 `engine.py` access receipt logging
Consistently stamps `authority: "NONE"`, every retrieval logged. MMR-lite diversity prevents file flooding.

### S-08 `helen2027.html` CSS variable system
Clean semantic tokens, consistent color system with one-meaning-per-color discipline (--ok, --warn, --blocked, --helen, --gold). The visual grammar is well-specified.

### S-09 Operator UX dual-track design
`helen2027.html` (document aesthetic) and `home_v1.html` (terminal aesthetic) are deliberate parallel design tracks, not accidental duplication. Both are valid interface modalities for different operator contexts.

### S-10 Proposal corpus governance strand
`MANIFEST_GATE_V1.md`, `HELEN_AUTORESEARCH_SAFE_ARCHITECTURE_V1.md`, `GAS_V0.md`, `GAS_V0_PROOFS.md`, `BOUNDED_RECEIPT_WULMATH_V0.md`, `AUTORESEARCH_E11_E12_RECONCILIATION.md` — all directly connected to implemented code or active governance. Retain.

### S-11 Transport Theory strand (9 documents)
Research layer, not implementation. Correctly not connected to sovereign code paths. Retain as research substrate — it is the mathematical foundation for GAS V0 proof obligations.

### S-12 `skill_admission_checker/` and `reference_drift_witness/`
Both have tests. Bounded function, clear scope, non-sovereign.

### S-13 `CONSUMER_ALLOWLIST` kernel guard mechanism
The guard itself is correct. The allowlist is stale (AR-cecf4c5b553f correctly identifies this). Route AR packet; fix allowlist.

### S-14 Sandbox visual grammar
`HELEN_ANOMALY_GRAMMAR_V1.md`, `HELEN_OS_V2_VISUAL_CANON_LOCK.md`, `HELEN_OS_V2_INTERACTION_GRAMMAR.md` — these define a coherent visual language. Retain.

### S-15 Gate 8 / Capability manifest SHA verification (GATE-001)
Implemented this session. 13/13 tests green. HOLD_FOR_OPERATOR. Correctly contained.

---

## CROSS-CUTTING FINDINGS

### XC-01 Inference-retrieval gap is the primary blocking dependency
`_infer()` stub blocks: context ranking, summarization weights, retrieval-augmented responses, continuity scoring. Before any of these ideas can be evaluated, the inference surface must exist. All downstream optimization proposals are HOLD until E-01 is resolved.

### XC-02 False signal chain from API to UI
E-01 + E-02 + E-03 create a 3-layer false signal chain:
- `context_items = []` always → `context_count=0` in receipt → misleading receipt
- `continuity_score = 1.0` always → ghost field in receipt + ghost in UI
- Dual ingestion with no canonical path → knowledge retrieval status unknowable

This chain means the UX currently displays false operational state. Should be documented as active technical debt, not aspirational features.

### XC-03 Red-gate normalization is the most urgent risk
AR-cecf4c5b553f is the most correctly-formed, most urgent finding in the corpus. Kernel Guard CI has been red for 3 consecutive main pushes over 3 weeks. The architecture holds (22 boundary + 36 constitutional tests green) but the certification layer has drifted. This is the exact risk the AR outbox was built to surface. Route immediately.

### XC-04 Goblin/operative doc registers mixed in proposals/
`PROTO_SENTIENT_GOBLIN_MANIFESTO_V0.md` (narrative) and `GOBLIN_5_EPOCH_AUTORESEARCH.md` (operational spec) live in the same directory as formal governance proposals. Not a bad idea — but a clarity gap. The manifesto belongs in `temple/subsandbox/` (narrative layer), not in `docs/proposals/` (governance layer).

---

Tranche 01 seal: 16 eliminations, 5 HOLDs, 15 survivors
Next: write OVERNIGHT_SURVIVORS.md
