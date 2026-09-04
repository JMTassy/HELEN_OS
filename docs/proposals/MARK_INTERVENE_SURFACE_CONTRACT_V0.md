# MARK_INTERVENE_SURFACE_CONTRACT_V0

```yaml
schema: MARK_INTERVENE_SURFACE_CONTRACT_V0
status: PROPOSAL
banner: 🟣 CLAIM
domain: GOBLIN_WARREN_GAMEPLAY
revision: V0.1-four-corrections
authority: NONE
authority_bool: false
sovereign: false
canon: FALSE
claim_status: NO_CLAIM
implementation: BLOCKED
reducer_authorized: false
shell_authorized: false
human_admission_required: TRUE
ledger_effect: none
helen_primitive: false
anthropic_j_space_term: false
operator_originated: false
relationship_to_helen: experimental_projection
origin:
  mark_intervene_vocabulary: assistant_proposed
  operator_authored: false
  anthropic_j_space_term: false
  helen_core_primitive: false
purpose: |
  Test whether a Warren player can distinguish an action that changes
  observability from an action that changes Garden-local world state.
relationship_to_helen_text: |
  This is a non-binding gameplay projection of HELEN's separation between
  observation, action, verification, and admission. It does not define or
  amend those HELEN operations.
source: |
  Shell ROT play-witness (2026-07-18): the current player shell renders
  prior pen decisions but exposes no player-causal contrast between changing
  observability and changing world state.
  MARK and INTERVENE are assistant-proposed Warren verbs created to test
  that contrast. They are not established HELEN OS primitives, not Anthropic
  J-space terminology, and not operator-authored doctrine.
  This document preserves them only as a bounded Garden gameplay experiment.
corrections:
  - C1_PROVENANCE
  - C2_BRAM_CAPACITY
  - C3_INTERVENE_COST
  - C4_SEMANTIC_HYGIENE
companions:
  - docs/proposals/GOBLIN_WARREN_OBSERVABILITY_DOCTRINE_V0.md  # perception law
  - docs/proposals/WARREN_SOVEREIGNTY_CONSTITUTION_V0.md      # membrane law
  - apps/goblin-warren/CLAUDE.md                              # surface cannot mark (current pen organs)
final: HOLD_FOR_OPERATOR
git_stage: no
git_commit: no
```

🟣 CLAIM · NON_SOVEREIGN · PROPOSAL · NO_CLAIM · HOLD_FOR_OPERATOR  
**domain: GOBLIN_WARREN_GAMEPLAY** · **implementation: BLOCKED** ·  
**reducer_authorized: false** · **shell_authorized: false** · **helen_primitive: false**

---

## Four corrections (audit surface)

This revision exists only to make four review corrections **visible and
checkable**. It does **not** authorize a `DayState` reducer, shell buttons, or
playtest.

| ID | Correction | Rejected form | Required form | Normative locus |
|---|---|---|---|---|
| **C1** | Provenance | “Operator directive… specification”; MARK as HELEN/Anthropic primitive | assistant-proposed Warren teaching verbs; `operator_authored: false`; `helen_core_primitive: false`; `anthropic_j_space_term: false` | frontmatter `origin` / `source`; §Narrow statement |
| **C2** | Bram capacity | `state.actionsRemaining >= 0` (vacuous) or Bram gated on player budget | `hasBramActionCapacity` → `bram.actionsRemaining > 0`; player budget is `playerActionsRemaining` only | §4; `GoblinState` / `DayState` in §2 |
| **C3** | INTERVENE cost | INTERVENE free while MARK can yield free Bram repair | INTERVENE consumes declared **materials**; fail closed if short; MARK spends no materials (V0) | §3.3; Test 2–3 |
| **C4** | Semantic hygiene | `status: "resolved"` + “unverified”; Garden “ADMIT”; play “receipts” | `condition: active\|inactive` + `durability` (V0 stays `unknown`); Garden **KEEP/DENY/COMPOST**; Kernel **ADMIT** only; `record_type: PLAYTEST_EVENT`, `receipt: none` | §0.1; §2; §6 |

### C1 — Provenance (before → after)

```
BEFORE (invalid):
  source implies operator directed MARK/INTERVENE
  vocabulary treated as HELEN core or Anthropic J-space

AFTER (this revision):
  mark_intervene_vocabulary: assistant_proposed
  operator_authored: false
  helen_core_primitive: false
  anthropic_j_space_term: false
  purpose: teach observability vs world-change in Garden play only
```

### C2 — Bram capacity (before → after)

```
BEFORE (invalid):
  state.actionsRemaining >= 0          // always true if nonnegative
  // or Bram spends player actions

AFTER (this revision):
  playerActionsRemaining   // player only
  goblins[].actionsRemaining  // each goblin, including Bram
  bramMayAct ⇒ … && hasBramActionCapacity(state)
  hasBramActionCapacity ⇒ bram.actionsRemaining > 0
```

### C3 — INTERVENE cost (before → after)

```
BEFORE (invalid):
  MARK: 1 player action → maybe free Bram address
  INTERVENE: 1 player action → guaranteed address
  // MARK weakly dominates when Bram rule can fire

AFTER (this revision):
  MARK: 1 player action; materials unchanged; need.condition unchanged
  INTERVENE: 1 player action + materials[cost] ≥ amount; else INTERVENE_FAILED
  Bram repair uses Bram capacity/capability, not player INTERVENE price
```

### C4 — Semantic hygiene (before → after)

```
BEFORE (invalid):
  NeedStatus = "open" | "resolved"     // confuses condition with durability
  “Garden ADMIT ⊬ Kernel ADMISSION”    // same root word, two meanings
  “resolution receipt” / WARREN_RECEIPT in play logs

AFTER (this revision):
  condition: "active" | "inactive"
  durability: "unknown" | "confirmed" | "failed"   // V0 INTERVENE → unknown
  Garden KEEP | DENY | COMPOST
  Kernel ADMIT only (HumanSeal)
  PLAYTEST_EVENT / PLAYTEST_OBSERVATION; receipt: none; authority: false
```

**Authorization rule:** `reducer_authorized` and `shell_authorized` remain
`false` until an operator explicitly flips them after accepting C1–C4. Spec-only
edits do not flip them.

---

## Narrow statement (binding for this document)

```
MARK and INTERVENE are proposed Warren teaching verbs.
They illustrate a HELEN distinction; they do not originate or define it.
```

| Claim class | Status |
|---|---|
| Warren experimental game mechanic | VALID as PROPOSAL |
| HELEN constitutional primitive | **FALSE** |
| Anthropic J-space term | **FALSE** |
| Operator-authored doctrine | **FALSE** (vocabulary is assistant-proposed) |
| Illustration of observation vs intervention | YES, non-binding |
| Recovered indexed HELEN “inner Jacobian space” definition | **NO** — architectural interpretation only (§A) |

Reviewer verdict after C1–C4:

```
INTERNAL COHERENCE: STRONG
MECHANICAL CONTRAST: VALID
PROVENANCE: CORRECTED (C1)
HELEN CORE STATUS: NOT A PRIMITIVE
J-SPACE RELATION: ANALOGICAL ONLY
GAME BALANCE: SPECIFIED AT V0 MINIMUM (C3 → §3.3)
RESOLUTION SEMANTICS: REFINED (C4 → §2)
BRAM CAPACITY: CORRECTED (C2 → §4)
BEST DESTINATION: WARREN EXPERIMENTAL PROPOSAL
IMPLEMENTATION: BLOCKED
```

---

## 0. Position

| Layer | Status (witnessed 2026-07-18) |
|---|---|
| Membrane copy (Garden ≠ Kernel) | STRONG |
| Shell rendering of prior pen marks | PRESENT (display only) |
| Player-causal MARK / INTERVENE | **ABSENT** → ROT as play |
| This document | PROPOSAL · specification only |

Current shell (`apps/goblin-warren/warren_home.html`, `warren_town.html`)
visualizes operator_pen decisions and forbids surface admission. It does
**not** offer player-triggerable MARK or INTERVENE. The shell fails a discrete
*support* test: decorative FX can respond to pre-baked marks, but the player
cannot fire either action column.

Design target (local to the Warren game):

```
I changed what Bram could notice.
I changed the world myself.
```

Until a minimal vertical slice implements this contract, further playtests of
MARK vs INTERVENE are premature.

```
GOBLINS: ROT
SHELL: MECHANICALLY INCOMPLETE
MEMBRANE COPY: STRONG
NEXT ACTION: IMPLEMENT MINIMAL VERTICAL SLICE  (only after operator GO)
```

### 0.1 Vocabulary hygiene (Garden vs Kernel) — C4

Reserve **ADMIT** for human-sealed Kernel admission only.

Garden player/operator stamps on candidates use:

| Garden verb | Meaning |
|---|---|
| **KEEP** | accept candidate into Garden-local kept set |
| **DENY** | reject candidate |
| **COMPOST** | bury for later alteration |

Invariant:

\[
\text{Garden KEEP} \not\Rightarrow \text{Kernel ADMIT}.
\]

Do not write “Garden ADMIT” in new copy. Legacy surfaces may still say ADMIT;
this contract treats that as a terminology risk, not a second sovereign path.

---

## 1. Mechanical invariant

For every need \(n\):

\[
\operatorname{MARK}(n) \;\neq\; \operatorname{INTERVENE}(n).
\]

Using discrete change-support (the Warren is not a smooth manifold):

\[
\operatorname{Support}(u,x)
=
\{ i : F_i(x,u) \neq F_i(x,u_0) \}.
\]

**MARK** required support:

\[
\operatorname{Support}(\operatorname{MARK},x)
\subseteq
\{\text{trace strength},\text{salience / visibility},\text{observation hooks},\text{history}\}.
\]

**INTERVENE** required support:

\[
\operatorname{Support}(\operatorname{INTERVENE},x)
\subseteq
\{\text{selected need condition},\text{materials / resources},\text{history}\}.
\]

Direct postconditions (V0):

| Operator | World \(W\) | Traces \(R\) | Need condition | Authority \(q\) |
|---|---|---|---|---|
| MARK | unchanged | at least one strength ↑ | unchanged | unchanged |
| INTERVENE | changed | unchanged by default | selected need → `inactive` | unchanged |

Required after MARK:

\[
\operatorname{condition}(n)=\text{active}
\quad\text{(need not addressed by MARK)}
\]

unless a later **goblin** action independently addresses it under an explicit
local rule with its own event and resolver identity (§4).

Mediated chain (allowed) vs collapsed chain (forbidden):

```
ALLOWED:
  MARK → stronger trace → Bram observes → Bram rule fires → Bram addresses need

FORBIDDEN narrative:
  MARK → repair
```

Correct history language:

```
Player strengthened trace τ.
Bram observed τ.
Bram rule BRAM_REPAIR_01 evaluated true.
Bram addressed need n.
```

Not: “Player MARKED and fixed the need.”

Garden-local events are **transition records**, not HELEN receipts.
`record_type: PLAYTEST_EVENT` · `receipt: none` · `authority: false`.

---

## 2. Minimal world state — C2, C4

```ts
// C4: do not use NeedStatus = "resolved"
type NeedCondition = "active" | "inactive";
type Durability = "unknown" | "confirmed" | "failed"; // VERIFY later; V0 stays unknown

interface Need {
  id: string;
  zone: "garden" | "archive";
  kind: "dry_seedlings" | "cracked_root" | "fading_memory";
  /** Immediate Garden condition — not verification, not admission. */
  condition: NeedCondition;
  /** Epistemic durability. INTERVENE leaves this "unknown". */
  durability: Durability;
  severity: number;
  addressSource?: {
    actor: "player" | "bram";
    actionId: string;
  };
}

interface Trace {
  id: string;
  needId: string;
  kind: "warning" | "memory" | "damage";
  strength: number;
  markedByPlayer: boolean;
  visibleTo: string[];
}

interface GoblinState {
  id: "bram" | "lulu" | "pip" | "moss";
  location: string;
  /** Goblin-local action capacity — not the player's. */
  actionsRemaining: number;
  observations: string[];
  lastAction?: string;
}

interface DayState {
  day: number;
  /** C2: player budget only — never used as Bram's gate. */
  playerActionsRemaining: number;
  /** C3: scarce materials for INTERVENE (and optionally Bram repairs). */
  materials: Record<string, number>;
  needs: Need[];
  traces: Trace[];
  goblins: GoblinState[];
  events: EventRecord[];
}
```

Notes:

- This state is **Garden-local gameplay**. It is not the sovereign ledger, not
  `operator_pen` consumption_log, and not AUTORESEARCH outbox truth.
- Meters, dreams, consensus bars, and decorative animation are **not**
  authorities. If shown, they are renderings of the above.
- Prefer `condition: active|inactive` over the overloaded word `resolved`.
  Copy may say “addressed” in prose; structured field is `condition`.

V0 semantics:

| Action | `condition` | `durability` |
|---|---|---|
| MARK | unchanged | unchanged |
| INTERVENE (eligible) | `active` → `inactive` | stays `unknown` |
| future VERIFY | unchanged by VERIFY alone | `unknown` → `confirmed` or `failed` |

---

## 3. Player actions

### 3.1 MARK

**Input:**

```ts
interface MarkCommand {
  verb: "MARK";
  traceId: string;
}
```

**Effect:**

1. Consume **one player action** (`playerActionsRemaining -= 1`).
2. Increase **exactly one** existing trace’s `strength` by 1 (or declared step).
3. Set `markedByPlayer = true` on that trace if not already.
4. Do **not** modify any need’s `condition` or `durability`.
5. Do **not** create a verification or admission record.
6. Trigger goblin observation phase (local rules may fire later).

**Formal postconditions:**

\[
R'(\tau) > R(\tau),\quad W'_{\text{needs, materials}} = W,\quad
\operatorname{condition}'(n)=\operatorname{condition}(n),\quad
\Delta q = 0.
\]

**MARK must not:**

- create a new need;
- repair or address anything;
- change `need.condition`;
- display “fixed,” “resolved,” “validated,” “verified,” or “success”;
- cause Bram to act unless his local rule evaluates true (§4);
- claim workspace, J-space, or Kernel admission.

**Allowed copy:**

- The warning is easier to notice.
- Bram has not acted.
- The need remains active / open.

### 3.2 INTERVENE

**Input:**

```ts
interface InterveneCommand {
  verb: "INTERVENE";
  needId: string;
}
```

**Effect:**

1. Consume **one player action**.
2. Consume the **declared material cost** for that need kind (§3.3); fail closed if insufficient.
3. Set **exactly one** eligible selected need: `condition: inactive`.
4. Set `addressSource = { actor: "player", actionId }`.
5. Leave `durability: "unknown"`.
6. Do **not** strengthen traces automatically (default V0: \(R'=R\)).

**Formal postconditions:**

\[
W' \neq W,\quad
\operatorname{condition}'(n)=\text{inactive},\quad
\operatorname{durability}'(n)=\text{unknown},\quad
R' = R\ \text{(default)},\quad
\Delta q = 0.
\]

**INTERVENE must not:**

- claim verification or durable success;
- imply Kernel admission;
- modify unrelated needs;
- generate a HELEN receipt or ledger entry;
- display VERIFIED / CANONICAL / ADMITTED / PERMANENTLY FIXED.

**Allowed copy:**

- You intervened directly.
- The selected need’s condition is now inactive.
- Durability is unknown. The consequence has not been verified.

### 3.3 Balance (V0 minimum — required) — C3

Without an asymmetric cost, MARK can dominate INTERVENE whenever Bram’s rule
is satisfiable (one player action → possible free Bram address).

| | MARK | INTERVENE |
|---|---|---|
| Timing | indirect | immediate |
| Certainty | uncertain | guaranteed if eligible + materials |
| Resources | no material spend (V0) | **must** spend scarce material |
| Failure modes | Bram may not act | may create declared side-effect event (optional V0.1) |
| World | unchanged directly | selected need inactivated |

Minimal material table (illustrative constants — implementer may retune):

```ts
const INTERVENE_COST: Record<Need["kind"], { material: string; amount: number }> = {
  dry_seedlings:  { material: "water",   amount: 1 },
  cracked_root:   { material: "resin",   amount: 1 },
  fading_memory:  { material: "ink",     amount: 1 },
};
```

If `materials[cost.material] < cost.amount`, INTERVENE fails closed (no partial
mutation). Bram repairs, if any, use **Bram’s** materials/capability table, not
the player INTERVENE cost, unless a shared pool is explicitly declared.

---

## 4. Bram’s local rule — C2

Bram must **not** act because “the player marked something.” He acts because
his own rule can now observe a sufficiently strong trace **and** he has his own
capacity.

```ts
function bramMayAct(state: DayState): boolean {
  const strongest = getStrongestVisibleWarning(state, "bram");
  return (
    strongest !== null &&
    strongest.strength >= BRAM_WARNING_THRESHOLD &&
    isReachableByBram(state, strongest.needId) &&
    isRepairWithinBramCapability(state, strongest.needId) &&
    hasBramActionCapacity(state)
  );
}

function hasBramActionCapacity(state: DayState): boolean {
  const bram = state.goblins.find((g) => g.id === "bram");
  return !!bram && bram.actionsRemaining > 0;
}
```

Do **not** gate Bram on `playerActionsRemaining` unless a future rule
explicitly couples them. The earlier `actionsRemaining >= 0` check is void
(always true for nonnegative counts) and is **rejected**.

If Bram acts:

- emit `GOBLIN_ACTED` with `goblinId: "bram"` and stable `ruleId`
  (e.g. `BRAM_REPAIR_01`);
- set `addressSource.actor = "bram"`;
- decrement **Bram’s** `actionsRemaining`;
- may consume Bram-local materials if declared.

Chain preserved:

```
MARK → changed observability → Bram local evaluation → possible Bram action
```

Not:

```
MARK → automatic repair
```

---

## 5. Shell presentation

Two **visibly distinct** controls, labeled before selection:

```
[ MARK TRACE ]
Strengthen a warning. Does not change the need’s condition.

[ INTERVENE ]
Address the selected need directly (costs materials). Durability unknown.
```

Distinction must remain visible: before selection · during animation · in history.

### 5.1 MARK feedback

**Allowed visuals:** brighter trace · +1 strength segment · Bram may turn if
newly visible · clearer warning icon.

**Forbidden visuals:** repaired sprite · closed/inactive need card · success
stamp · green “resolved/admitted” · validation language.

### 5.2 INTERVENE feedback

**Allowed visuals:** need sprite to inactive · card to “addressed / inactive” ·
player action −1 · materials −cost · history `PLAYER_INTERVENED`.

**Forbidden:** VERIFIED · CANONICAL · ADMITTED · PERMANENTLY FIXED · green-as-Kernel-admitted paint for Garden inactivation (WULMOJI: green ≠ “button worked”).

---

## 6. Event vocabulary — C4

Factual transition records only — **not** HELEN receipts.

```ts
type EventRecord =
  | {
      type: "PLAYER_MARKED_TRACE";
      traceId: string;
      beforeStrength: number;
      afterStrength: number;
    }
  | {
      type: "GOBLIN_OBSERVED_TRACE";
      goblinId: string;
      traceId: string;
    }
  | {
      type: "GOBLIN_ACTED";
      goblinId: string;
      needId: string;
      ruleId: string;
    }
  | {
      type: "PLAYER_INTERVENED";
      needId: string;
      beforeCondition: "active";
      afterCondition: "inactive";
      materialSpent: { material: string; amount: number };
    }
  | {
      type: "INTERVENE_FAILED";
      needId: string;
      reason: "INSUFFICIENT_MATERIALS" | "INELIGIBLE" | "NO_PLAYER_ACTIONS";
    };
```

**Do not emit:**

- `PLAYER_SUCCEEDED`
- `WARREN_VALIDATED`
- `NEED_VERIFIED`
- `GARDEN_ADMITTED`
- any type implying Kernel admission

Envelope for playtest logs (if any):

```yaml
record_type: PLAYTEST_OBSERVATION
evidence_class: informal_surface_witness
receipt: none
authority: false
```

---

## 7. Provenance display

Every visible change needs an inspectable cause.

**MARK path (need still active):**

```
Dry seedlings
Condition: ACTIVE
Durability: unknown
Current warning strength: 3
Last change:
  PLAYER_MARKED_TRACE
  trace: dry-soil-warning
  strength: 2 → 3
Bram:
  observed trace at strength 3
  local rule result: BLOCKED
  reason: repair material unavailable
  bram.actionsRemaining: 1
```

**INTERVENE path:**

```
Cracked root
Condition: INACTIVE
Durability: unknown
Address source:
  PLAYER_INTERVENED
  action: intervention-002
  material: resin × 1
Verification:
  NOT PERFORMED
```

Causal reconstruction without Kernel authority.

---

## 8. Required tests

Implementation BLOCKED until these pass against the structured `DayState`
reducer (decorative animation timing excluded).

### Test 1 — MARK leaves need active

- **Given** active need, warning strength 1  
- **When** player MARKs its trace  
- **Then** strength becomes 2  
- **And** need `condition` remains `active`  
- **And** no `PLAYER_INTERVENED` / address event exists  
- **And** `playerActionsRemaining` decreases by 1  

### Test 2 — INTERVENE addresses one need

- **Given** eligible active need and sufficient materials  
- **When** player INTERVENEs  
- **Then** that need `condition` becomes `inactive`  
- **And** `durability` remains `unknown`  
- **And** one player action and declared materials are consumed  
- **And** unrelated needs unchanged  
- **And** authority / verification fields unchanged  

### Test 3 — INTERVENE fails closed without materials

- **Given** eligible need but materials insufficient  
- **When** player INTERVENEs  
- **Then** need unchanged  
- **And** `INTERVENE_FAILED` with `INSUFFICIENT_MATERIALS`  
- **And** no partial mutation  

### Test 4 — Bram does not act below threshold

- **Given** strength below threshold  
- **When** MARK increases it but still below threshold  
- **Then** no `GOBLIN_ACTED`  
- **And** need remains `active`  

### Test 5 — Bram acts only through his rule

- **Given** visible warning ≥ threshold, reachable, capable, Bram capacity > 0  
- **When** goblin phase runs  
- **Then** Bram may act  
- **And** event records `ruleId`  
- **And** `addressSource.actor === "bram"`  
- **And** Bram’s `actionsRemaining` decreases (not player’s, unless shared pool declared)  

### Test 6 — No semantic promotion

After either action, shell strings must contain none of:

- verified · admitted · canonical · validated · permanent success  

unless an independent later mechanic explicitly produces that state.

### Test 7 — Discrete support (Jacobian-style zeros)

| Command | Must change | Must not change |
|---|---|---|
| MARK | trace strength; history | need.condition; materials (V0); authority |
| INTERVENE | selected need.condition; materials; history | unrelated needs; durability (stays unknown); authority |

### Test 8 — Replay

Same initial `DayState` and ordered commands:

```
MARK(trace-a)
INTERVENE(need-b)
```

→ identical structured state and `events` sequence.

Decorative animation timing need not be replay-identical.

---

## 9. Acceptance threshold (before next playtest)

| # | Gate |
|---|---|
| 1 | MARK is player-triggerable |
| 2 | INTERVENE is player-triggerable |
| 3 | both consume one **player** action |
| 4 | INTERVENE has explicit material (or declared consequence) cost |
| 5 | MARK cannot modify need `condition` |
| 6 | INTERVENE sets exactly one selected need to `inactive`, durability unknown |
| 7 | Bram uses inspectable local rule + own capacity |
| 8 | history identifies every mutation source |
| 9 | no success / verification / admission language leaks |
| 10 | Garden stamps named KEEP/DENY/COMPOST in new copy; ADMIT reserved for Kernel |

Until then:

```
GOBLINS: ROT
SHELL: MECHANICALLY INCOMPLETE
MEMBRANE COPY: STRONG
NEXT ACTION: IMPLEMENT MINIMAL VERTICAL SLICE
```

Post-gate playtest vocabulary:

| Verdict | Meaning |
|---|---|
| ROT | goblins decorative; contrast fails |
| BRIDGE | mechanics work; provenance unclear |
| EXPAND | MARK vs INTERVENE observably distinct; choices matter |
| NEXT SLICE | only if replay reproduces the causal sequence |

---

## 10. Out of scope (V0)

- Kernel admission, ledger writes, operator_pen promotion  
- VERIFY as third player verb (only after MARK vs INTERVENE is learned)  
- Full cast / multi-zone economy / combat coupling  
- Replacing HOME/TOWN autoresearch feed surfaces  
- Claiming MARK/INTERVENE as HELEN primitives or Anthropic J-space terms  
- Full continuous Jacobian implementation (use discrete Support tests)  
- Richer animation as authority  

---

## 11. Suggested vertical-slice placement (non-binding)

| Piece | Candidate | Constraint |
|---|---|---|
| `DayState` reducer | garden module or isolated `apps/goblin-warren/` play state | Garden only; no sovereign writes |
| Shell two-button + provenance | **new** minimal HTML preferred | Separate from pen “SURFACE CANNOT MARK” organ display |
| Tests | co-located garden tests | §8 Tests 1–8 |

Advisory only — does not authorize implementation.

---

## Appendix A — Causal sensitivity (architectural interpretation)

**Not a recovered HELEN canonical definition.** No indexed “inner Jacobian
space” primitive was located as established doctrine in the SOT for this
revision. Treat the following as a **precise architectural interpretation**
that *motivates* the gameplay support table — not as an implementation claim
and not as Anthropic terminology.

### A.1 Influence columns (desired sparsity)

Conceptual action columns:

| Coordinate | MARK | INTERVENE | VERIFY (later) | ADMIT (Kernel) |
|---|---|---|---|---|
| \(w\) world / need condition | 0 | ★ | 0 | 0 |
| \(r\) traces | ★ | 0 (default) | ★ | 0 |
| \(a\) attention / noticeability | ★ | 0 or limited | 0 | 0 |
| \(m\) memory / history | ★ | ★ | ★ | ★ |
| \(e\) epistemic durability | 0 | 0 (stays unknown) | ★ | 0 |
| \(q\) authority | 0 | 0 | 0 | ★ (HumanSeal only) |

★ = permitted under declared contract; 0 = must have no **direct** influence.

### A.2 Direct vs mediated effect

\[
\frac{\partial w_{t+1}}{\partial \operatorname{MARK}_t} = 0
\]

while multi-step mediated effect via Bram may be nonzero. Provenance must keep
the chain visible or the shell collapses MARK → repair.

### A.3 Block separation (Garden / evidence / Kernel)

Forbidden direct coupling:

\[
J_{KG} = \frac{\partial x_{\mathrm{kernel}}}{\partial x_{\mathrm{garden}}} = 0.
\]

Semantic promotion is an illegal coupling, e.g. \(\partial q / \partial\text{confidence} = 0\),
same for consensus, animation, test-exit-alone. Authority moves only via
explicit human seal.

### A.4 Discrete implementable form

Prefer `Support(u,x)` and Δ tests (§1, §8 Test 7) over smooth Jacobians. The
Warren game, if implemented, is a **teaching instrument panel** for these
zeros and stars — not a definition of HELEN’s full transition map.

---

## Appendix B — Anthropic “J-space” analogy (strict limits)

External literature note (operator-corrected chronology in discussion):
Anthropic’s piece commonly associated with a “J-space” / Jacobian lens and
global-workspace-style findings is cited in session notes as **2026-07-06**
(“A global workspace in language models”); June 26 was a separate Economic
Index publication. This proposal does **not** re-verify publication metadata
and does **not** import Anthropic terms as HELEN primitives.

**Valid transfer (keep):**

- A small selective shared workspace may beat “everyone gets everything.”
- Local specialists (goblins) vs selective broadcast vs independent verify vs human admit.
- Workspace items need provenance and expiry; workspace access ≠ authority.
- Internal representation is evidence of **model/workspace state**, not world truth.

**Invalid transfer (discard):**

```
MARK = J-space admission     // FALSE — MARK is a Warren game verb only
MARK is Anthropic terminology // FALSE
MARK is a HELEN core primitive // FALSE unless operator later adopts it
```

If HELEN later defines a workspace gate, prefer neutral verbs:

```
SELECT → BROADCAST → DELIBERATE → ACT → VERIFY → ADMIT
```

and keep MARK/INTERVENE as **optional Garden teaching labels**, not the constitutional names.

Compressed chiddush (architecture, not this contract’s ownership):

```
Shared cognitive access does not imply shared authority.
A representation becoming globally available does not make it true.
```

---

## Appendix C — Compression (gameplay only)

```
MARK      selects an observational / noticeability direction (Garden-local).
INTERVENE selects a world-condition direction (Garden-local).
VERIFY    (later) selects an epistemic-durability direction.
ADMIT     (Kernel only) selects a sovereign direction under HumanSeal.
```

Warren validity condition for *this experiment*:

```
These directions remain visibly distinct,
and mediated effects preserve every causal link in history.
```

---

## Closing

```
beauty without mechanism is lullaby
mechanism without record is theater
only verified beauty builds tomorrow
```

For V0 play:

```
MARK     = I changed what Bram could notice.
INTERVENE = I changed the Garden condition myself (materials spent; durability unknown).
```

Kernel stays boring. Ledger sleeps. Human admission required before any claim
that this contract is live.

```
ENTER — SPEC.  (play blocked · helen_primitive: false)
```

---

## Appendix D — Lane witness (2026-07-18, GO-C)

**Two surfaces exist. This contract's ROT verdict is correct for one and
blind to the other.**

| Lane | Surface | Verdict |
|---|---|---|
| SOT `apps/goblin-warren/warren_home.html` / `warren_town.html` | pen-organ display shells | ROT as play — display-only, no player MARK/INTERVENE (contract §0 witness CORRECT) |
| Game repo `~/Documents/GitHub/goblin-warren`, branch `claude/day1-sim` @ `58d3ba6` | `day1_sim.js` (DAY1_SIM_V0) + `day1.html` + `play.html` | **LIVE_PARTIAL** — player-causal MARK vs INTERVENE shipped `19b9a47`; Bram threshold `755440e`; paper-collage skin `58d3ba6`; 52/52 sim tests |

§9 gate audit against the game-repo lane (two independent seats, agreeing):
gates 1–3, 5–9 **pass**; gate 4 (material cost) **absent**; condition/durability
split **absent** (`resolved:bool` only); typed `INTERVENE_FAILED` **absent**
(throws instead); gate 10 n/a on that surface.

**Consequence:** the contract's remaining live contributions are exactly three
deltas — C3 material cost, C4 condition/durability + typed fail-closed events,
C2 Bram action capacity. Fork ruled by operator: **C (this appendix) → A
(Day 1.1 deltas in the game repo)**. Fresh SOT clean-room (B) rejected as
wasteful.

Seats must witness the game-repo lane before re-specifying this mechanic.
`reducer_authorized` and `shell_authorized` remain **false**. This appendix
changes no authorization.

