# GOBLIN_5_EPOCH_AUTORESEARCH

**Classification:** NON_SOVEREIGN · NO_SHIP · GOBLIN_MODE · PROPOSAL  
**Authority:** NONE  
**World effect:** NONE  
**Ledger:** append forbidden  
**Runner:** `scripts/ralph/ralph_goblin_loop.sh`

---

## What this is

A 5-epoch bounded non-sovereign repair loop.  
GOBLIN cognition: small, stubborn, local, receipt-first.

Operating law per epoch:

```
inspect → test → isolate → patch once → verify → emit receipt → stop
```

Forbidden in every epoch:

- ledger append
- canon mutation
- MAYOR impersonation
- schema-root migration (`helen_os/schemas/` is sovereign)
- self-deploy
- SHIP without receipt linkage

---

## AUTORESEARCH GOBLIN PROMPT (inner loop)

```
[ROLE::RALPH]
[MODE::GOBLIN_MEDITATION]
[INTENT::BOUNDED_AUTORESEARCH]
[TASK::PAYLOAD_HASH_AND_RECEIPT_BINDING]
[AUTHORITY::NONE]
[WORLD_EFFECT::NONE]
[STOP::AFTER_ONE_PATCH]

Pinned invariant:
  payload_hash == SHA256(CANON_JSON_V1(payload))

CANON_JSON_V1(payload) = json.dumps(
    payload,
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False
).encode("utf-8")

Rules:
- recompute hashes; do not trust envelope hashes
- receipt binds only if it binds verdict_id + payload_hash + cum_hash
- use "type", not "etype"
- SHIP means payload["decision"]["outcome"] == "SHIP"

Allowed:
- inspect files
- run tests
- patch validators
- add tests
- emit typed receipts
- prepare review packet

Forbidden:
- ledger append
- canon mutation
- MAYOR impersonation
- kernel rewrite
- schema-root migration
- self-deploy

Output only:
1. files patched
2. tests added
3. pytest result
4. schema path drift noted
5. canon/kernel/ledger untouched
```

---

## Epoch definitions

### E1 — SILENCE / FREEZE

**Intent:** establish the meditation chamber before touching anything.

**Objective:** freeze the execution surface and confirm the exact invariant under attack:
`payload_hash == SHA256(CANON_JSON_V1(payload))`

**Actions:**
- snapshot worktree
- enumerate touched files
- classify EXISTING / CREATE / PATCH
- confirm `helen_os/schemas/` remains canonical
- mark schema-root drift as review-only, not executable

**Deliverables:**
- `scratch/TRACE_E1_FREEZE.md`
- `scratch/PATCH_SURFACE_V1.json`
- `scratch/GOBLIN_CONSTRAINTS_V1.json`

**Pass condition:**
- exact patch perimeter is known
- no sovereign file drift introduced
- canon/kernel/ledger untouched

**Failure receipt:** `FAILURE_CLUSTER_V1 { cluster: "PATCH_SURFACE_AMBIGUOUS" }`

---

### E2 — HASH MEDITATION

**Intent:** distrust all hashes, recompute all hashes.

**Objective:** patch validators so payload hash is always recomputed from payload and never trusted from the envelope.

**Patch scope:**
- `tools/validate_hash_chain.py`
- `tools/validate_receipt_linkage.py`
- tests only as needed

**Actions:**
- implement recomputation path
- replace any trust-in-envelope logic
- standardize on `type`, not `etype`
- standardize SHIP detection: `payload["decision"]["outcome"] == "SHIP"`

**Deliverables:**
- `scratch/CANDIDATE_FIX_V1_hash_semantics.json`
- `scratch/EVAL_RECEIPT_V1_hash_semantics.json`

**Pass condition:**
- mismatched payload hash fails
- no mutation of canonicalization semantics

**Failure receipt:** `FAILURE_CLUSTER_V1 { cluster: "PAYLOAD_HASH_RECOMPUTE_MISSING" }`

---

### E3 — RECEIPT BINDING TRANCE

**Intent:** bind receipt to the exact verdict, not to vibes.

**Objective:** enforce the triad — `verdict_id` + `payload_hash` + `cum_hash`.

A receipt is valid only if it binds to all three.

**Actions:** add red tests:
- event `payload_hash` mismatch → FAIL
- SHIP receipt wrong `ref_verdict_payload_hash_hex` → FAIL
- SHIP receipt right payload hash but wrong `ref_verdict_cum_hash_hex` → FAIL
- valid SHIP verdict + matching receipt → PASS

**Deliverables:**
- `tests/test_hash_chain_payload_hash.py`
- `tests/test_receipt_linkage.py`
- `scratch/RECEIPT_BINDING_MATRIX_V1.json`

**Pass condition:** receipt linkage proves exact verdict binding, not approximate binding.

**Failure receipt:** `FAILURE_CLUSTER_V1 { cluster: "RECEIPT_BINDING_WEAK" }`

---

### E4 — AUTORESEARCH MIRROR

**Intent:** let HELEN inspect its own failure surface without gaining authority.

**Objective:** run one bounded Ralph-style autoresearch loop on the patched surface.

**Loop:**
1. run focused tests
2. run full tests
3. cluster failures
4. generate one candidate fix
5. apply one bounded patch
6. rerun targeted tests
7. emit eval receipt
8. stop

**Allowed outputs:**
- `FAILURE_CLUSTER_V1`
- `CANDIDATE_FIX_V1`
- `EVAL_RECEIPT_V1`
- `REVIEW_PACKET_DRAFT_V1`

**Forbidden:**
- direct state mutation
- direct skill activation
- direct ledger append
- sovereign config rewrite
- self-upgrade

**Deliverables:**
- `scratch/AUTORESEARCH_EPOCH_4_REPORT.md`
- `scratch/FAILURE_CLUSTER_V1.ndjson`
- `scratch/REVIEW_PACKET_DRAFT_V1.json`

**Pass condition:** autoresearch produces lawful review-ready artifacts only.

**Failure receipt:** `FAILURE_CLUSTER_V1 { cluster: "AUTORESEARCH_AUTHORITY_LEAK" }`

---

### E5 — GOBLIN SEAL WITHOUT SEALING

**Intent:** compress everything into a referee-clean terminal state.

**Objective:** produce the smallest trustworthy report.

**Final report must contain only:**
- files patched
- tests added
- pytest result
- schema path drift noted
- canon/kernel/ledger untouched

**No extra claims.** No "done." No "shipped." No "sealed." No metaphysics.

**Deliverables:**
- `scratch/GOBLIN_FINAL_REPORT_V1.md`
- `scratch/PATCH_MANIFEST_V1.json`
- `scratch/TEST_RESULTS_V1.json`

**Pass condition:** the run ends with a bounded, typed, audit-ready packet.

**Failure receipt:** `FAILURE_CLUSTER_V1 { cluster: "FINAL_REPORT_SCOPE_DRIFT" }`

---

## Tree map

```
E1 FREEZE
└── define patch perimeter
    ├── files
    ├── constraints
    └── no-root-drift
E2 HASH
└── recompute payload_hash
    ├── validate_hash_chain.py
    └── validate_receipt_linkage.py
E3 BIND
└── enforce verdict binding
    ├── verdict_id
    ├── payload_hash
    └── cum_hash
E4 MIRROR
└── bounded autoresearch
    ├── run tests
    ├── cluster failures
    ├── patch once
    └── emit receipts
E5 COMPRESS
└── final review packet
    ├── patched files
    ├── tests added
    ├── pytest
    └── untouched sovereign core
```

---

## Key factors of success

1. **Patch the validator, not the story.**  
   If semantics stay ambiguous, no amount of prompting saves you.

2. **One patch per epoch.**  
   Multiple conceptual moves in one pass destroy attribution.

3. **Red tests first.**  
   A silent invariant is not an invariant.

4. **Schema-root discipline.**  
   Do not "clean up" structure during hardening.

5. **Autoresearch stays non-sovereign.**  
   The moment it writes reality directly, HELEN collapses back into agent theater.

---

## Ultra-compressed WUL slab

```
[ROLE::RALPH]
[MODE::GOBLIN]
[TASK::5_EPOCH_AUTORESEARCH]
[AUTHORITY::NONE]
[WORLD_EFFECT::NONE]
E1 freeze
E2 recompute hash
E3 bind receipt
E4 patch once
E5 compress report
LAW:
  do not trust hashes
  recompute hashes
  then trust the match
TRIAD:
  verdict_id + payload_hash + cum_hash
BAN:
  ledger append
  canon mutation
  MAYOR impersonation
  schema-root drift
  self-deploy
END:
  typed receipts only
  no receipt -> no ship
```

---

## Emergent property

```
more consequence → less improvisation

lawful self-narrowing under epistemic pressure
```

Not "autonomy." The inverse of autonomy at the mutation boundary.
