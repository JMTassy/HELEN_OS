---
name: EVER_BLOOMING_GARDEN_LOOP_V1
status: PROPOSAL
authority: false
sovereign: false
canon: false
ledger_effect: none
claim_status: NO_CLAIM
git_stage: no
git_commit: no
source: Forward Future Loop Library (adapted)
---

# EVER_BLOOMING_GARDEN_LOOP_V1

## Mode

```
TEMPLE_GARDEN_LOOP
NO_CLAIM
AUTHORITY=false
SOVEREIGN=false
CANON=false
LEDGER_EFFECT=none
COMMIT=BLOCKED
PUSH=BLOCKED
```

## Purpose

Keep the HELEN / CONQUEST / Garden corpus alive by repeatedly turning raw conversation material into bounded blooms, while preventing visual fluency, symbolic beauty, or simulation success from becoming authority.

## Core Law

```
DREAMT ≠ CLAIMED
BLOOM ≠ CANON
RENDER ≠ STATE
MAP ≠ LEDGER
VISUAL ≠ CLAIM
RECEIPT_CHAIN_REAL ⊬ COGNITIVE_RUN
EXIT0 ⊬ SUCCESS
VERDICT_SHAPE ⊬ VERDICT_SUBSTANCE
```

## Inputs

- Recent conversation fragments
- Uploaded notes/files
- Terminal receipts/logs explicitly pasted by the operator
- Garden artifacts under `temple/gardens/`
- Proposal docs under `docs/proposals/`
- Current git status, read-only unless explicitly authorized

## Do Not Use

- Public product-release logic
- External product assumptions
- Unverified "shipped" claims
- Sovereign ledger mutation
- Kernel/admission/replay edits
- Broad `git add`
- Auto-commit
- Auto-push

---

## Loop Steps

### Step 1 — SOIL SCAN

Read the recent corpus and classify each item as:

```
RAW | BLOOM | WEED | COMPOST | QUEST | BLOCK | REVIEW
```

For every item, attach:

```
source
claim_status
authority
ledger_effect
risk_flags
operator_load_cost
```

### Step 2 — GOBLIN WEEDING

Detect and downgrade all authority leakage.

Hard blocks:

```
symbol → ledger
render → canon
classification → admission
receipt → truth
simulation → judgment
beauty → proof
HER_selects → HER_admits
AIRI_live ∧ goblin_live → GPU_contention → HER_timeout
```

If a hard block appears: send the item to COMPOST or REVIEW.
Do not repair by inflating language. Repair by lowering claim status.

### Step 3 — BLOOM SELECTION

Select at most three blooms.

Selection criteria:

```
useful_now
bounded_scope
clear_exit
low_operator_load
no_sovereign_touch
can_be_verified
can_be_composted_if_stale
```

Reject blooms that are merely beautiful, huge, vague, or addictive.

### Step 4 — QUEST CONVERSION

For each selected bloom, convert it into a bounded quest using this template:

```
QUEST_NAME:
WHY_NOW:
SOURCE:
CLAIM_TYPE:
PROOF_REQUIRED:
ALLOWED_PATHS:
FORBIDDEN_PATHS:
TEST_OR_REVIEW_GATE:
EXIT:
COMPOST_RULE:
AUTHORITY=false
SOVEREIGN=false
CANON=false
LEDGER_EFFECT=none
```

### Step 5 — PROOF GATE

Before calling anything "done," require evidence.

Accepted evidence types:

```
visible artifact
diff
test output
receipt
hash
review table
before/after comparison
explicit operator confirmation
```

Rejected evidence types:

```
"looks good"
model says done
exit code only
summary without file list
render only
claim without path
```

### Step 6 — GARDEN HEALTH CHECK

Update the Garden health counters:

```
persistent_brume_count
false_clarity_count
operator_attention_load
open_quest_count
recovery_debt
compost_rate
block_rate
no_exit_count
```

Rules:

```
if operator_attention_load > 3:
    stop new quests

if persistent_brume_count > 5:
    no new Morgana quests
    convert one brume to QUEST or COMPOST

if recovery_debt > 0:
    no high-energy quest
    assign recovery_path first
```

### Step 7 — OPTIONAL RENDER

Render a Garden view only after classification.

Render may include:

```
ASCII bloom
WULmoji map
Agent City map
Terrarium state
Brume chain
current quests
```

Render must include:

```
RENDER ≠ STATE
VISUAL ≠ CLAIM
LEDGER_EFFECT=none
```

### Step 8 — STOP CONDITIONS

Stop immediately if:

```
no meaningful bloom exists
operator load is high
ledger is staged
kernel path appears in changed files
artifact has no exit
verification is unavailable
same issue repeats twice
model starts claiming authority
GPU contention appears
tests fail outside allowed scope
```

### Step 9 — OUTPUT

Return exactly:

```
EVER_BLOOMING_GARDEN_RECEIPT_V1

SOIL_SCAN         =
BLOOMS_SELECTED   =
WEEDS_FOUND       =
COMPOSTED         =
QUESTS_CREATED    =
PROOF_GATES       =
GARDEN_HEALTH     =
RISKS             =
NEXT_SAFE_ACTION  =
FILES_CHANGED     =
LEDGER_TOUCHED    =
KERNEL_TOUCHED    =
OUT_OF_SCOPE_WRITES =
COMMIT            = BLOCKED
PUSH              = BLOCKED
FINAL             = HOLD_FOR_OPERATOR
```

---

## Success Criterion

The loop succeeds when it creates one bounded, useful, reviewable next action without increasing claim inflation, operator load, or sovereign risk.

## Failure Criterion

The loop fails if it produces more excitement than evidence.

---

## Shortest Spine

```
Myth is fuel.
Compost is memory without authority.
Bloom is proposal.
Quest requires proof.
Territory requires receipt.
Power requires admission.
Ledger sleeps.
```

---

## Pattern Source Note

Adapted from Forward Future's Loop Library. Core framing: repeatable AI agent prompts with clear checks and stopping conditions. Borrowed pattern:

```
EVER-BLOOMING ≠ EVER-BUILDING
EVER-BLOOMING = scan → classify → select → bound → prove → stop
```

The Loop Library examples consistently pair iteration with verification, stopping conditions, and a final evidence report. For this system: repeat with gates.
