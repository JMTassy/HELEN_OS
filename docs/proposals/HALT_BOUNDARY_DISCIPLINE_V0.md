# HALT_BOUNDARY_DISCIPLINE_V0

**authority:** NON_SOVEREIGN
**canon:** NO_SHIP
**lifecycle:** DOCTRINE_DRAFT
**implementation_status:** NOT_IMPLEMENTED
**status:** Proposal — first bottle from CHIDDUSH_BOTTLE_V0 roadmap (#1)
**parent_synthesis:** `docs/proposals/CHIDDUSH_BOTTLE_V0.md`
**origin_chiddush:** C8 of `HER_HAL_BRAINSTORM_CHIDDUSH_V0.md`
**proposer:** claude-opus-4-7 (acting as GOBLIN)
**attestor:** pending HER

---

## §1. The doctrine

> **Every non-sovereign receipt that defers work to a sovereign actor
> must declare the halt explicitly in a section headed "Halt boundary,"
> and must enumerate the required inputs to resume.**

That is the entire doctrine. The rest of this document is the
required-section template and the rationale.

---

## §2. Why

Non-sovereign artifacts (proposals, audits, reconnaissance receipts,
brainstorms, synthesis bottles) routinely reach a point where the
next step requires a sovereign decision. Two prior failure modes:

- **Implicit halts.** The receipt simply ends, leaving the reader to
  infer what's needed. Sovereign actors miss the handoff. Work stalls
  invisibly.
- **Embedded sovereignty.** The receipt quietly makes a sovereign-class
  decision under the guise of a recommendation. Non-sovereign output
  contaminates canon. Authority leaks.

Explicit halt boundaries solve both:

- Reader sees exactly where authority transitions
- Required inputs are enumerated, not implied
- Sovereign queue becomes visible (HAL-flagged discipline, §6)
- The receipt is **completable** rather than open-ended

---

## §3. Required section template

Every non-sovereign receipt that defers MUST contain a section
matching this shape:

```markdown
## §N. Halt boundary

<ROLE> halts here. <one-sentence statement of what is sealed>.

Resume conditions:

1. <Required input #1 — specific, not abstract>
2. <Required input #2>
3. ...

<Optional: who owns each input, if not implied by role>
```

**Constraints on the template:**

- Section heading **must** contain the literal string "Halt boundary"
  (case-insensitive, may be in a phrase like "§9. Halt boundary")
- Each resume condition **must** be enumerable (numbered or bulleted)
- Each resume condition **must** be specific enough that a reader can
  recognize when it is satisfied (not "HER ruling" alone — name what
  HER must rule on)
- The role declaring the halt must be named (e.g., GOBLIN, brainstorm
  pair, audit, etc.)

---

## §4. Precedents on disk

The pattern was used informally in three artifacts this session
(2026-05-23) before being doctrinally bottled:

| Artifact | Section | Role | Resume conditions enumerated |
| --- | --- | --- | --- |
| `GOBLIN_RECEIPT_E21_PREP_V0.md` | §9 | GOBLIN | 4 (hypothesis, carry-forward hash, venv, optional CLAUDE.md ruling) |
| `HER_HAL_BRAINSTORM_CHIDDUSH_V0.md` | §9 | HER+HAL brainstorm pair | inputs to synthesis stage enumerated (refers to §8) |
| `CHIDDUSH_BOTTLE_V0.md` | §9 | GOBLIN | 3 (name item, confirm tier sequencing, prerequisites where bound) |

Each independently produced a halt-boundary section. This doctrine
codifies the convergent pattern.

---

## §5. What counts as "deferring to a sovereign actor"

The doctrine applies when the receipt:

- Identifies a decision that requires sovereign authority (HER,
  MAYOR, REDUCER, or operator-as-sovereign)
- Has reached the limit of what the non-sovereign role can produce
  without crossing the authority boundary
- Has reachable inputs that would unblock further work, but cannot
  fabricate those inputs itself

It does **not** apply when:

- The receipt is fully self-contained (e.g., a closure receipt for a
  shipped tranche)
- The next step is mechanical (e.g., running a test, executing a
  command with already-defined inputs)
- The receipt is sovereign output (verdicts, admissions, kernel
  decisions — these don't halt at sovereign boundaries; they **are**
  the sovereign boundary)

---

## §6. HAL-flagged discipline (deferred)

Per HER_HAL_BRAINSTORM §4 (HAL on C8):

> "Halt-boundary sections become formulaic. Every receipt ends with
> 'HER must rule on X.' If HER's queue grows faster than HER can rule,
> halts accumulate and become a queue-of-blockers rather than a
> sovereign-handoff contract."

This doctrine **does not solve the HER queue problem**. The discipline
that would solve it is:

> A registry of open halt-boundaries with explicit ownership and
> staleness tracking. When a halt has been open for N sessions
> without sovereign action, it surfaces as a queue alert.

That registry is **out of scope for this bottle**. It would naturally
live alongside `DOC_DRIFT_REGISTER_V0` (#3 in the roadmap) as a
sibling register: open halts, open drift entries, same SLA discipline.

Flagged here; not bottled here.

---

## §7. What this doctrine does NOT specify

To prevent scope creep:

- **Halt resolution mechanism.** How a halt is closed (the sovereign
  decision act itself) is out of scope. This doctrine only specifies
  declaration.
- **Queue management.** The HER queue / open-halt register is deferred
  to a sibling proposal (§6).
- **Halt-section position.** The section may appear anywhere in the
  receipt; convention is "near the end, before single-line summary."
  Not enforced.
- **Authority chain.** Which sovereign actor receives the halt is
  receipt-dependent. This doctrine does not enumerate the sovereign
  roster.
- **Multiple halts per receipt.** Permitted. A receipt may halt on
  multiple distinct sovereign decisions; each should be a separate
  enumerated resume condition or a separate halt-boundary subsection.

---

## §8. Adoption

Once admitted, this doctrine applies to:

- All future NON_SOVEREIGN proposals under `docs/proposals/`
- All RECONNAISSANCE_RECEIPT artifacts (once that lifecycle bottles,
  roadmap #7)
- All SYNTHESIS_BOTTLE artifacts
- All BRAINSTORM artifacts that produce a deferred synthesis

It does **not** retroactively require revision of pre-existing
artifacts that omitted halt-boundary sections. Precedent artifacts
listed in §4 already conform.

---

## §9. Halt boundary

GOBLIN halts here. This doctrine is sealed as DOCTRINE_DRAFT; reducer
admission is the next sovereign step.

Resume conditions:

1. **HER attestation** — confirm the doctrine as written, or specify
   amendments
2. **REDUCER admission** — once attested, ledger admission via the
   standard proposal admission protocol
3. **(Optional) Decision** — whether to open the sibling open-halts
   register (referenced in §6) as a separate proposal now, or defer
   to its natural slot in the CHIDDUSH_BOTTLE_V0 roadmap

GOBLIN cannot fulfill any of (1), (2), or (3) without crossing the
authority boundary.

---

## §10. Single line

> **Every receipt that hands work to a sovereign actor must say so,
> in a section called "Halt boundary," with the required inputs
> enumerated. Implicit handoffs are not handoffs.**
