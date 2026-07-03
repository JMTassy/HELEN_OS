# HARNESS DEBUG V1 — four-dimension audit against behavioral evidence

```yaml
authority: false
canon: false
ledger_effect: none
status: PROPOSED
owner: operator (JMT)
review_date: 2026-07-17
kill_criterion: superseded by applied harness edits or deleted if unreviewed
method: self-audit with declared bias (the auditor built most of this
        harness) — offset by grading against the SESSION'S BEHAVIORAL
        RECORD (what actually happened across ~30 turns) rather than
        against the files' own claims. Evidence is cited per finding.
scope: .claude/* (instructions, memory, STATE, LOOPS, commands/, agents/),
       ~/.claude/CLAUDE.md + agents + stop hook, project CLAUDE.md
```

## The goal, stated once

Nothing in the harness states it in one line, so here it is, inferred
from everything: **convert operator attention into receipted, operator-
gated improvements to HELEN OS, at minimum reasoning-cost, compounding
across sessions.** Every finding below is a place the harness pulls
against one of those five clauses.

---

## A · GOAL ORIENTATION — parts pulling against the goal

### A1 ⭐ The stop hook fights the governance model (7+ collisions this session)

`~/.claude/stop-hook-git-check.sh` ends every commit turn with "…then
push." The operator's standing law is push-on-explicit-word-only.
Result, observed: every commit turn ends in a contradiction the model
must adjudicate; early in the session the hook's instruction actually
induced an unauthorized push attempt (caught by the classifier), which
then had to be distilled into a lesson. The harness instructs violating
its own boundary once per turn.
**Edit (operator-owned file, proposed not applied):** change the hook's
final clause from "then push" to "ready to push on operator
confirmation" — or have it read a `.claude/PUSH_POLICY` line and adapt.

### A2 ⭐ Seat-blind routing: instructions demand a GPU this seat doesn't have

`instructions.md` Model Routing: "DEFAULT: ORNITH (local GPU, free)."
This cloud seat has no Ollama endpoint — the default is unexecutable
here, permanently. The barbell is right for the *system*; the file is
wrong for *this seat*. Cross-seat drift is the repo's named disease and
the harness has it internally.
**Edit (applied):** routing section now points at
`tools/model_registry.py` and declares seat-conditional behavior.

### A3 The global orchestrator is a dead letter (behavioral evidence: ~0 uses)

`~/.claude/CLAUDE.md` prescribes scout→plan→implement→review with
`PROGRESS.md` and aggressive `/clear`. Observed across the whole
session: PROGRESS.md created 0 times; the scout/implementer/reviewer
trio invoked approximately once; phase discipline never used. The
render audit — the session's biggest fan-out — used ad-hoc
general-purpose agents instead, successfully. An unfollowed
constitution trains constitution-ignoring.
**Proposed:** either (a) demote the global file to "for multi-phase
builds only, invoked by name," matching reality, or (b) delete the
PROGRESS.md machinery and keep only the maker≠grader rule, which IS
followed. Operator picks.

### A4 WULmoji-everywhere rule ≠ WULmoji-anywhere behavior

"Use WULmoji in ALL verdicts, summaries, and gate results" — observed
compliance ~60%, decaying in long analytical turns, with zero operator
corrections about its absence. The part that IS load-bearing (never
🟢🟡⚪ on non-admitted) was followed 100% and separately caught real
violations in three audits.
**Proposed:** narrow the rule to what's actually enforced and enforced-
worthy: "governance-state renderings use the palette; never 🟢🟡⚪
unadmitted." Drop the everything-else mandate.

---

## B · SELF-MODEL AUDIT — stale, aspirational, or wrong

### B1 ⭐ The harness doesn't eat its own dogfood on model routing

This session built `tools/model_registry.py` + `model_routing_registry.json`
as THE single source of truth for role→model resolution — specifically
because HAL had a 3-way drift between spec, code, and memory. Then
`instructions.md` (Model Routing, Barbell) and `memory.md` (Persona
Model Map) each keep their own hardcoded copies naming specific models
("Sonnet 5", "gemma4:e2b", "qwen3.5:9b-ud-q4"). That is the exact
disease the registry cures, reproduced inside the tool that built the
cure. Hardcoded model names in prose rot silently on every model
upgrade.
**Edit (applied):** instructions.md routing now defers to the registry.
**Proposed:** memory.md's Persona Model Map gets a `seat:` column and a
header line "resolution authority: tools/model_registry.py — this table
is a cached view, trust the registry on conflict."

### B2 Point-in-time facts stored as memory (stale on arrival)

`memory.md`: "Active Branch: 10 commits, clean" (now ~20), "last
updated 2026-07-01" (misses the roadmap, three audits, the demo
branch, the cross-seat yield event — the two densest days). Git already
stores branch state perfectly; memory storing a stale copy is negative
information.
**Edit (applied):** replaced the commit-count line with a pointer;
stamped the update.

### B3 Aspirational entities: HERMES

"Two-agent separation: HELEN=architect, HERMES=executor" — HERMES
appears in zero artifacts, zero skills, zero commits, this session or
in the repo. Either it's a local-seat concept that leaked here without
a seat tag, or it's aspiration recorded as fact.
**Proposed:** tag it `[local-seat concept, unverified here]` or delete.

### B4 The memory-update trigger is miscalibrated

Protocol: update memory.md "every time the operator shares major
context." Observed: the session's most durable knowledge (parking rate,
verdict-laundering pattern, yield-event pipeline, unrelated-histories
finding) came from WORK, not operator dumps — and none of it reached
memory.md, only STATE.md. The trigger misses the main knowledge stream.
**Proposed:** trigger becomes "any stage-4 distillation" regardless of
source; memory.md gets the distillations, STATE.md keeps the raw log.

---

## C · MEMORY THAT COMPOUNDS — where knowledge goes to die

### C1 ⭐ The harness has the repo's own 87.6%-parking disease

Three overlapping stores (memory.md Decisions Log, STATE.md Last
Session, LOOPS.md commentary), no promotion rules, no decay rules, no
kill criteria on entries. STATE.md's "Last session" section is
append-only and grew ~5x this session. Nothing ever promotes to
Verified Facts by rule, nothing ever composts. AR-TERMINATION-002
measured this exact pattern in the repo's governance objects; the
harness memory reproduces it.
**Proposed retention rules (the design the prompt asked for):**
- *Promotion:* an Open Failure or observation confirmed twice
  independently → moves UP to Verified Facts / General Rules; one
  contradiction → moves back down with the contradicting receipt cited.
- *Decay:* Last-Session entries older than 2 sessions get distilled to
  one line each; the raw text is composted per q50 fingerprint-retention
  (hash recorded in the distill line, prose deleted). STATE.md stays
  under ~120 lines forever.
- *Cap:* Decisions Log keeps the latest 15 rows; older rows survive as
  git history, which is what git is for.

### C2 ⭐ Resurfacing exists but nothing triggers it

`tools/session_digest.py` was built to be the session-start brain-load
(open failures, routing drift, governance overdue). Observed: it is
invoked by nothing — no hook, no instruction strong enough. It ran once
at build time, never again. Knowledge captured + never resurfaced =
dead.
**Proposed (single highest-leverage memory fix):** a SessionStart hook
that runs `python3 tools/session_digest.py` — its output lands in the
first context window automatically. The `session-start-hook` skill
exists for exactly this; one operator GO wires it.

### C3 "Distill into the skill" is written but not walked

Rule (instructions.md line 15): after any non-trivial failure, write
the lesson into the skill itself. Observed this session: 5+ lessons
written to STATE.md; skills actually amended with a lesson: 1
(provenance-trace v0.2). The push-boundary lesson, the collect-only
lesson, the listener-order lesson — all live in STATE/chat only.
**Proposed:** session_digest.py prints a nag line: lessons added to
STATE.md since the newest mtime under `.claude/commands/` — makes the
gap visible at session start instead of invisible forever.

---

## D · BITTER LESSON — where structure will become ballast

Sutton's claim: general methods that leverage compute beat hand-encoded
human knowledge, and the hand-encoding becomes the ceiling. Audit of
this harness against it:

### Aligned (keep, these scale WITH better models)
- **Barbell routing** — routes work to the cheapest sufficient compute;
  more compute/better models = same law, better output.
- **Verifier-gated generate-and-test** (the cross-seat survival-rate
  pipeline) — literally search + evaluation; the bitter lesson's
  favorite shape. 3050→2→1 is the receipt.
- **Maker ≠ grader** — evaluation over introspection.
- **Receipts/gates as invariants** — these constrain GOALS, not
  methods; the lesson never argued against knowing what you want.

### Violations (today's model-quirk workarounds written as timeless law)
- `think:false` for deepseek, heredoc-in-subshell rules, "never say
  'show your reasoning'", two-daemon inventory rules, WULmoji output
  mandates, council's 5-persona × N-round choreography — every one is
  a patch for a 2026-model weakness, written in the same permanent
  voice as the sovereign firewall. When models improve, these become
  ballast that no one dares delete because they're indistinguishable
  from law.

### The structural fix (the "comprehensive plan", one move)
Split every harness rule into two declared classes:
- **INVARIANT** — survives any model swap (firewall, receipts,
  maker≠grader, push-on-word, garden locality). No expiry.
- **SCAFFOLD** — encodes a model assumption. Gets two fields:
  `model_assumption: <what must stay true>` and `review_date:`.
  `session_digest.py` flags scaffolds whose named model no longer
  matches the registry — so upgrading a model automatically surfaces
  which crutches to re-test and delete.

One pass through `.claude/commands/*.md` + instructions.md adding the
class marker is ~30 minutes of work and makes the whole harness
future-model-proof by construction: doctrine stays, crutches decay on
schedule.

---

## Applied this pass (pure staleness corrections only)
1. instructions.md — Model Routing/Barbell now defer to
   `tools/model_registry.py`, seat-conditional (B1/A2).
2. memory.md — stale branch counts replaced with pointers; update
   stamped (B2).

## Held for operator GO (structural)
- A1 stop-hook wording (operator-owned file)
- A3 global-orchestrator demote-or-delete decision
- A4 WULmoji rule narrowing
- C1 retention rules into STATE.md header
- C2 SessionStart hook wiring (session-start-hook skill, one GO)
- C3 digest nag line
- D scaffold/invariant classification pass

---
authority=false · canon=false · PROPOSED · the auditor built the thing
it audited — findings are graded against behavior, but weigh them
accordingly
