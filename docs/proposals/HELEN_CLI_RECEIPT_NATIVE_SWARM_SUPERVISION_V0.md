# HELEN CLI: Receipt-Native Swarm Supervision

```
AUTHORITY      = false
CANON          = false
STATE_MUTATION = none
LEDGER_EFFECT  = NONE
STATUS         = proposal / non-sovereign
VERSION        = V0
ROUTE          = docs/proposals
PROMOTION      = FORBIDDEN_WITHOUT_PEER_REVIEW_AND_REDUCER
```

> **One-line abstract.** HELEN CLI is a receipt-first command membrane for supervising
> sandboxed autonomous agents: agents may move, receipts may speak, and only explicit
> human ALLOW may admit reality.

---

## 0. What this freezes (and what it does not)

This proposal freezes the **interface law** for the HELEN command line. It is doctrine
*about* the interface, not the interface itself. It is **not** kernel law, **not** canon,
**not** an admitted ledger object. It may be peer-reviewed, revised, or rejected. It may
not self-promote.

---

## 1. Refined definition

The CLI is not a "command shell that runs things," and not merely a "supervisory
interface." It is a **verification membrane between autonomous agent motion and
human-authorized reality.**

```
HELEN_CLI =
    swarm observability
  + receipt verification
  + symbolic compression
  + zero-trust action gating
  + human ALLOW
  + fail-closed repo hygiene
```

**Grounding.** A CLI is the right substrate because it is compact, scriptable, replayable,
and history-preserving — the same properties a receipt trail and a deterministic operator
workflow require. Zero-trust ("never trust, always verify"; treat the network as
compromised; least-privilege per request) is not aesthetic here — it is the security
model. "Every command is suspect" is the literal posture, not a slogan.

---

## 2. The emergent property

> A symbolic CLI where agents may act,
> but only receipts may report,
> and only the human may admit.

Hard kernel form:

```
AGENT_MOTION ≠ REALITY
RECEIPT      = SPEAKABLE_STATE
ALLOW        = ADMISSION_GATE
SCOPE        = COMMIT_GATE
HASH         = TRUST_HANDLE
```

WUL form:

```
🌐 swarm + 🧾 receipt + ⚖️ validation + 🛡️ membrane + 👁️ ALLOW  =  HELEN CLI
```

The interface must make one thing obvious:

```
nothing is real     until receipted
nothing is admitted until ALLOW
nothing is committed until scoped
```

---

## 3. Interface primitive — the EVENT_CARD (not the command)

The architectural move: the unit of the interface is not a command, it is an **event
card**. Every CLI line reduces to this shape.

```
EVENT_CARD = {
  route,
  mode,
  authority,
  canon,
  ledger_effect,
  files_touched,
  staged,
  committed,
  pushed,
  receipt_hash,
  next_safe_action
}
```

Rendered lines:

```
[🌱 GARDEN ][AUTH=false][LEDGER=NONE ][FILES=∅       ] swarm.render.day0 → 🧾#a19c
[🛠 OPERATE][AUTH=local][LEDGER=NONE ][FILES=1       ] datetime.patch    → 🧾#9f22
[⚠ HOLD    ][AUTH=?    ][LEDGER=dirty][FILES=CLAUDE.md] commit.target     → NONE
```

This gives HELEN a command line with an **audit-native state model** — not a chat
transcript pretending to be operational control. An unreceipted line (`→ NONE`) is a
non-event: it may be shown, but it may not be reported as having happened.

---

## 4. Four-pane CLI law

The CLI always shows four simultaneous layers — repo/authority state on top, swarm in the
middle, the gate at the bottom:

```
╔════════════════ HELEN CLI ════════════════╗
║ MODE        OPERATE / GARDEN / HOLD        ║
║ AUTHORITY   false / pending / allowed      ║
║ LEDGER      sleep / read-only / mutation   ║
║ REPO        clean / dirty / staged / ahead ║
╠════════════════ SWARM FIELD ══════════════╣
║ 🧠 agents    12   ⚠ noisy 1   ╬ critical 2 ║
║ 🧾 receipts  34   ⚖ pass 31   ⛧ contest 3  ║
╠════════════════ ACTION GATE ══════════════╣
║ NEXT SAFE ACTION: HOLD                     ║
║ ALLOW REQUIRED: yes                        ║
╚════════════════════════════════════════════╝
```

**Honesty rule for the SWARM FIELD.** The agent/receipt counts must be backed by real
receipts. If no instrumented swarm exists, the cells render `UNRECEIPTED` — they are never
populated with fabricated telemetry. A blank-by-honesty pane is the law working; a
confident fake count is the law failing. (Observed failure mode: a sibling runtime prints
`agents 12 / receipts 34` and hallucinated git status with no receipt behind either.)

---

## 5. Non-negotiable laws

```
NO_RECEIPT → NO_VOICE     a result with no receipt may not be reported as real
NO_ALLOW   → NO_ADMIT     threshold/validation ≠ operator consent
NO_SCOPE   → NO_COMMIT     a commit must name its exact target set
NO_HASH    → NO_TRUST      unverifiable provenance is treated as untrusted
NO_DIFF    → NO_STAGE      nothing is staged that was not diff-inspected
NO_STATUS  → NO_PUSH       no push without a clean, reviewed status read
```

These are fail-closed. Any uncertainty halts the action and surfaces it; it does not
proceed under ambiguity.

---

## 6. DASA → HELEN translation

DASA's reusable elements, stripped of military framing, become a civilian interface
pattern:

| DASA element | HELEN CLI translation |
|---|---|
| adaptive swarm autonomy | many sandboxed agents move without per-step human approval |
| human-machine synergy | human monitors the overview, intervenes via ALLOW |
| ethical governance | every admission gated; contest is data, not failure |
| resilience under noisy agents | Byzantine/noisy nodes quarantined, not trusted, not exiled |

Result: a **swarm-control tower**, not a chat, not a dashboard, not a raw terminal — a
receipt-first command membrane.

---

## 7. Supervisory-control alignment

This matches the supervisory-control model directly: the system continues autonomously
while the human monitors the overall process and intervenes when necessary. The CLI's
compactness, scriptability, replayability, and preserved history are exactly the
affordances that make supervisory control auditable rather than merely observable.

```
many semi-autonomous nodes
  → local state
  → shared signals
  → human-readable overview
  → explicit human override / ALLOW
  → receipt trail
```

---

## 8. Admission path (when ready)

This is a frozen **proposal**, not kernel law. To advance:

1. Peer-review (proposer ≠ validator — K2 / Rule 3)
2. Reconcile EVENT_CARD fields with existing receipt schemas (`helen_os/schemas/`)
3. Prototype the four-pane renderer against real `git` + real receipt sources only
4. MAYOR routing via `tools/helen_say.py`; enforce only after ratification

Until then: `AUTHORITY = false`, `CANON = false`, `STATE_MUTATION = none`.

```
🌐 agents may move · 🧾 only receipts may speak · 👁️ only the human may admit
NO_RECEIPT→NO_VOICE · NO_ALLOW→NO_ADMIT · NO_SCOPE→NO_COMMIT · NO_HASH→NO_TRUST
🏁
```
