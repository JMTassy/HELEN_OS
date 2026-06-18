# HELEN_OSAURUS_ADMISSION_SEAM_V0

```
STATUS    = PROPOSAL / design note
AUTHORITY = false
CANON     = false
LAYER     = NON_SOVEREIGN
LEDGER_EFFECT = none · KERNEL_EFFECT = none
```

> Consolidates THREE independent derivations that converged on the same architecture in one night
> (2026-06-17→18): (a) this session's "Admission Seam" frontier formalization, (b) the `~/.helen/`
> runtime's "Membrane Protocol / HELENVerifier" render, (c) a third session's "ComplianceScore / Veto"
> render. **Convergence across independent contexts is the confidence signal.** This doc is the single
> place that derivation should live — not re-derived in N chats forever.

---

## 0. The problem (the seam)

Each piece is proven **in isolation**, but the **join is not load-bearing**:
- **LAW** — the WUL reducer `Admit(c)` refuses self-asserted predicates (BED 02/03). Proven in *sandbox*,
  with *stub* evidence (`ReplayContext` faked), not wired to the live kernel.
- **BODY** — Osaurus agents produce proposals, live. Nothing routes their output through the reducer.
- **BRIDGE** — the only admitted ledger writer is `tools/helen_say.py`. No agent path reaches it.

**The gap:** there is no *running, enforced, self-deriving* edge `AGENT → helen_say.py → reducer → ledger`.
The membrane is proven on paper; it is not yet mechanical across the body→law boundary.

## 1. The convergent design — the Membrane

```
[User / trigger]
      │
      ▼
[Osaurus Agent (local, M3 Pro)]
      │  proposes an action (e.g. "write local DB", "send", "promote")
      ▼
[HELEN MEMBRANE  — the verifier, sits BETWEEN agent loop and execution]
      │  checks: receipt? · within constraints? · matches reducer logic? · predicates DERIVED?
      ├──(ADMIT)──▶ Osaurus sandbox executes · receipt appended via helen_say.py
      ├──(DENY) ──▶ HELEN ledger records the refusal (audit) · agent told the lawful path
      └──(WAIT) ──▶ action held · operator notified · pending-receipt with TIMEOUT
```

All three derivations agree on this shape: **Osaurus proposes; the Membrane decides; the ledger records.**
The arrow only points up. Invert it (agent → state directly) and authority moves into the expression —
the one thing the reducer forbids.

## 2. Memory vs Ledger (the anti-drift separation)

```
Osaurus Memory   = mutable contextual CACHE (agent state, tool outputs, transient). NOT truth.
HELEN Ledger     = immutable RECEIPTS (permissions, decisions, admissions). The only truth.
```
- A conversational "I will do X" is recorded as a **PENDING receipt** — and **expires on timeout**.
- This kills *drift*: the agent cannot act on a decision the user made 5 minutes (or 5 days) ago whose
  receipt has expired. `MEMORY ⊬ CANON` · `AUTHENTICATED ⊬ ADMITTED`.

## 3. ONE correction (verify, don't absorb): admission is BINARY, not a score

The third derivation proposed a `ComplianceScore (0–100)`, proceed if `> 80`. **This is off-doctrine for
the sovereign boundary** and must NOT be adopted as the admission rule:
- HELEN admission is a **conjunctive gate** — `Typed ∧ Hashed ∧ GateGreen ∧ ReviewedExternally ∧ HumanSeal`.
  It is **all-or-nothing**, not a fuzzy threshold. A 79/100 "almost admissible" claim is **NO_SHIP**, full stop.
- A `ComplianceScore` is acceptable ONLY as a *soft Osaurus-side pre-filter / UX hint* (which proposals to
  even surface) — never as the gate. The gate stays the binary reducer. `SCORE ⊬ ADMISSION`.

## 4. The formal problematic (what must be proven)

```
Let A = agent outputs · S = sovereign state (ledger) · R = Admit : A × Evidence × Replay → {ADMIT, REJECT}
PROVE:  ∀ a ∈ A :  a ∈ S  ⟺  R(a, derive(a), replay(a)) = ADMIT  ∧  self_asserted(a) ⇒ REJECT,
        with both outcomes emitting REPLAYABLE receipts.
Sub-frontiers:
  Q1 DERIVATION   — minimal real artifact set so R computes gate_green/seal WITHOUT trusting the agent
                    (= BED 03 closed in PRODUCTION, not sandbox stub)
  Q2 EXCLUSIVITY  — prove ∄ edge A→S except via helen_say.py (ENFORCED, not disciplined →
                    the PreToolUse firewall hook, tranche A3, still planned/non-enforceable)
  Q3 REPLAYABILITY— admission reconstructable from the ledger alone, under real inputs
  Q4 LIVENESS×SAFETY — HER's good proposals get admitted (usable) while no crossing passes (safe);
                    the over-flag failure mode, now at the seam
```

## 5. Phased roadmap (clean route — use Osaurus, add HELEN, fork last)

```
Phase 0  Osaurus↔Ollama bridge ........................ DONE (live, supervised)
Phase 1  HELEN agents (HER/HAL via prompts+routing) ... config-only
Phase 2  HELEN model fine-tune (LoRA → register HER) .. operator GPU (in flight)
Phase 3  Membrane Verifier as MCP/library between agent loop and execution
Phase 4  reducer/ledger bridge: agent → helen_say.py → reducer → ledger (the L4 join)
Phase 5  EXCLUSIVITY enforcement (Q2): activate the PreToolUse firewall hook  ← SOVEREIGN, MAYOR-routed
```

## 6. Boundaries (unchanged)

- The Membrane Verifier and the reducer that backs it are **sovereign** (`helen_os/governance/**`) —
  MAYOR-routed, NOT written by the non-sovereign shell.
- HELEN runs **read-heavy, write-only-for-authority** — it never mutates app data; it only admits/denies/records.
- This doc is a *design note*: `authority=false · canon=false`. It decides nothing; it maps the seam.

```
🦖 body proposes · ⚖️ membrane decides · 📜 ledger records · 🔁 replay reconstructs
AUTHORITY IS IN THE VERIFIED POSITION, NOT THE OBJECT · SCORE ⊬ ADMISSION · 👑🚫
```
