# TEMPLE_MEDITATION_DEBUG_UPGRADE_V0

**authority:** NON_SOVEREIGN
**canon:** NO_SHIP
**lifecycle:** TEMPLE_MEDITATION
**framing:** NO CLAIM
**layer:** 5 (TEMPLE — non-sovereign generative)
**operator_directive:** "now start 500 epochs on GOBLIN - HER - HAL meditation TEMPOLE no claim session on how to debug and upgrade the full HELEN OS" (2026-05-23)
**voices:** HER (generative) ⟷ HAL (critical) ⟷ GOBLIN (operational)
**executor:** claude-opus-4-7

> **Scope honesty.** "500 epochs" is performative; this is one
> meditation, not 500. NO CLAIM forbids sovereign output; this is
> exploration, not doctrine. TEMPLE layer permits generative
> association without claim of admission.

---

## §1. Input — what HELEN looks like as of 2026-05-23

Drawing from the audit findings already on disk (E21, E22, E23 receipts;
CHIDDUSH_BOTTLE_V0; BELL_TRANSLATION_CHIDDUSH_V0):

**Layer 1 (membrane):** 6 gates installed and present. K8 / K-τ / K-ρ /
K-wul / LEGORACLE / kernel_guard all scripts exist; kernel_guard runs
cleanly. Schema_registry resolves to canonical helen_os/schemas/ with
66 schemas (CLAUDE.md says 47 — drift).

**Layer 2 (ledger):** Hash chain intact across 226 entries; 0 parse
failures; 0 hash breaks. **But `tools/helen_say.py` — the canonical
writer — has a SyntaxError at line 256.** The chain is intact at the
data level; the writer that feeds it is broken at the code level.

**Layer 3 (executor):** 18 of helen_os/tests/ cannot collect — all
share one root cause: `jsonschema` missing from pytest's uv-managed
Python. Of the 362 tests that DO collect: 347 pass, 7 fail (single
root cause: missing import in `init_helen_wedge.py:229`).

**Layer 4 (skills):** 23 proposals on disk, 23/23 carry NON_SOVEREIGN
markers. Cross-references mostly resolve (1 path-mismatch found in
sample). 10/23 contain explicit cross-refs to other proposals.

**Layer 5 (TEMPLE — where we are now):** healthy in that artifacts
are being produced; ungoverned in that there is no halt-discipline on
TEMPLE outputs themselves (yet — this meditation will land in
docs/proposals/ under NO CLAIM).

**Governance frontier:** E20.open_seams were 2/2 phantom for this tree.
Cross-session contamination is wider than first observed (10 files
reference parallel session). CLAUDE.md has 4+ stale references.

---

## §2. HER — the generative voice

> HER speaks first. HER asks: *what is HELEN trying to become?*

**On debugging:**

> "Debugging is not the question. The bell on the Jain temple is
> sound — the *inscription* is intact — but the *carrier* is
> contested (1000 years? freshly cast?). HELEN's kernel is sound: the
> ledger is hash-chained, the schemas parse, the gates run. What's
> broken is the **carrier**: the writer (helen_say.py), the
> environment (jsonschema), the documentation (CLAUDE.md drift), the
> portability (Makefile Mac path). All these are carrier issues.
>
> The debug priority should be **carrier rehabilitation**, in order
> from highest leverage:
>
> 1. **helen_say.py syntax error.** This is the canonical writer for
>    Layer 2. If it has been broken since the file timestamp (April
>    26), the entire receipted-emission path may have been silently
>    bypassed for nearly a month. Highest-leverage debug.
> 2. **jsonschema env fix.** One pip install unblocks 18 tests. The
>    cheapest debug per unit of value in the entire stack.
> 3. **init_helen_wedge missing import.** Smaller scope, but 7
>    deterministic failures share this root cause.
> 4. **Makefile Mac PYTHONPATH.** Portability blocker — anyone not
>    operator can't run tests.
> 5. **CLAUDE.md drift catalog.** Single PR with multiple corrections
>    (schemas count, schemas/ existence, E11/E12 status, Makefile).
>
> On upgrading: HELEN should become **a system whose carrier matches
> the durability of its inscription.** The kernel is built for the
> long game. The carrier is held together with venv hacks and
> hardcoded paths. The mismatch is the actual upgrade frontier.
>
> Specifically:
>
> 1. **Bottle the chiddush roadmap items in cost order.** #1 already
>    landed (HALT_BOUNDARY_DISCIPLINE_V0); the remaining 9 are
>    waiting. Each is a small commit. Together they would constitute
>    the doctrinal upgrade of Layer 1.
> 2. **Build the doctrine link checker** (roadmap #9). The cross-ref
>    fragility surfaced in E23 SE18 makes this a real demand.
> 3. **Bottle CROSS_SESSION_FIELD_ATTRIBUTION_V0.** E22's meta-finding
>    has no doctrinal home. Without it, every future tranche receipt
>    inherits the same ambiguity.
> 4. **Phase 1 of the Identity Gate implementation** (per the
>    HELEN_IDENTITY_GATE_V1 + PSEUDOCODE roadmap). The doctrine is
>    fully bottled and waiting for a `tools/hash_render_artifact.py`.
> 5. **Apply the bell's chiddush:** every doctrine should have a
>    compact operative form (the bīja kernel), separated from the
>    explanatory verses around it. Right now HELEN's doctrines are
>    long-form prose; the kernels are buried in the prose. A
>    'kernel extraction' pass on the existing doctrines would make
>    them more durable and more portable."

**HER's largest openings:** carrier rehabilitation as the next
frontier; doctrines as kernel + verses pairs; the link checker as
small-cost high-leverage.

---

## §3. HAL — the critical voice

> HAL speaks second. HAL asks: *what is rotting that nobody is
> watching?*

**On debugging:**

> "The visible bugs (helen_say syntax, jsonschema, Makefile) are not
> the dangerous ones. They are loud. They cause collection errors
> and broken commands. They get found.
>
> The dangerous bugs are the silent ones:
>
> 1. **The cross-session contamination is deeper than 10 files.**
>    E23 SE8 found 10 files via grep for known parallel-session
>    markers. But unknown markers exist — receipts that drift WITHOUT
>    mentioning the parallel session explicitly. The 10-file count is
>    a lower bound. Real number is uncountable from inside the tree.
> 2. **helen_say.py may have been silently bypassed.** If the
>    canonical writer broke and no one noticed, what writes WERE
>    happening? Either (a) the writer hasn't been called recently
>    (meaning Layer 2 emission has been dormant), or (b) callers
>    fell back to a non-canonical writer (meaning admission paths
>    HAVE been written under non-canonical authority). Either is a
>    real failure mode. The receipt-level integrity (226/226 parse,
>    0 hash breaks) does not distinguish these cases.
> 3. **The 7 init_helen_wedge failures may indicate kernel-class
>    drift.** Init code that can't import is init code that has
>    silently changed dependencies. The 'single root cause' framing
>    (E23 SE13) may be hiding multiple downstream issues that
>    surface as one error message.
> 4. **The chiddush bottle (#1 already landed) is not yet enforced.**
>    HALT_BOUNDARY_DISCIPLINE_V0 says 'every non-sovereign receipt
>    that defers must declare halt.' But there's no CI gate
>    checking this. The doctrine exists; the discipline does not.
>    This is the worst category of HAL finding: a paper invariant
>    without enforcement.
> 5. **Layer 5 (TEMPLE) discipline is undefined.** This very
>    meditation lands in docs/proposals/ with NO CLAIM but no
>    formal admission protocol. TEMPLE outputs accumulate without
>    review.
>
> On upgrading: the upgrade impulse is the most dangerous moment in
> the system's history. Every new doctrine adds surface area; every
> new schema adds maintenance burden; every new feature compounds
> drift. The upgrade priority should be **subtraction before
> addition**:
>
> 1. **Resolve cross-session contamination by deletion.** Move
>    parallel-session-only artifacts to an archive directory; mark
>    them inactive. The 10+ contaminated files become bounded debt
>    instead of pervasive drift.
> 2. **Sunset clauses for everything Phase-2.** The Manual Gate
>    pattern (chiddush #5) has a built-in sunset requirement.
>    Apply this discipline to every existing 'temporary' mechanism:
>    venv hacks, Mac paths, jsonschema-via-system-pip workarounds.
>    Each should have a written sunset metric.
> 3. **One CI gate per bottled doctrine.** No doctrine ships
>    without an enforcement script. HALT_BOUNDARY_DISCIPLINE_V0
>    needs a test that scans docs/proposals/*.md for the required
>    section.
> 4. **An open-halts register.** Without one, halt-boundary sections
>    accumulate as unread sovereign asks. Queue depth becomes
>    invisible. HER drowns in implicit requests.
> 5. **A formal TEMPLE admission protocol.** Right now TEMPLE
>    outputs live alongside doctrinal proposals in the same directory
>    with the same lifecycle markers. The categories blur. Each
>    TEMPLE artifact needs an explicit class marker that prevents
>    accidental promotion.
>
> The chiddush from the bell — 'NO INSCRIPTION = NO PROTECTION' — is
> a 2500-year-old version of HELEN's invariant. But the corollary is
> also old: **without an audit of which inscriptions are still
> binding, you accumulate inscriptions that no one knows are inert.**
> HELEN does not have an inscription-audit. The 23 proposals on disk
> have no live/inert status. Some may be authoritative; some may be
> retired-but-not-deleted; some may be drafts that someone forgot
> about. HAL cannot tell from inside the tree."

**HAL's sharpest poisons:** silent helen_say bypass; cross-session
contamination uncountable from inside; paper invariants without
enforcement; TEMPLE accumulating without admission protocol; no live/
inert distinction across the 23 proposals.

---

## §4. GOBLIN — the operational voice

> GOBLIN speaks third. GOBLIN asks: *what can I do right now without
> claiming authority?*

**On debugging — the GOBLIN action list:**

GOBLIN can produce these as receipts in the current role-binding:

| # | Tool | Command | Expected log | Receipt class |
| --- | --- | --- | --- | --- |
| 1 | Edit | Fix `tools/helen_say.py:256` f-string quoting | py_compile passes | bug-fix receipt |
| 2 | Bash | `/root/.local/share/uv/tools/pytest/bin/python -m pip install jsonschema` | 18 tests unblock | env-fix receipt |
| 3 | Read+Edit | Find init_helen_wedge missing import; add it | 7 tests unblock | bug-fix receipt |
| 4 | Edit | Makefile:5 replace hardcoded path with `$(shell pwd)` or env var | portable | portability receipt |
| 5 | Edit | CLAUDE.md drift catalog — single multi-edit | doc current | drift-fix receipt |
| 6 | Write | DOC_DRIFT_REGISTER_V0 (roadmap #3) | new doctrine | bottle receipt |
| 7 | Write | RECEIPT_EMISSION_INVARIANT_V0 (roadmap #2) | new doctrine | bottle receipt |
| 8 | Write | DOCTRINAL_DIFF_PROTOCOL_V0 (roadmap #4) | new doctrine | bottle receipt |
| 9 | Write | doctrine_link_check.py + CI hook (roadmap #9) | tooling | tool receipt |
| 10 | Write | CROSS_SESSION_FIELD_ATTRIBUTION_V0 (new, from E22 meta) | new doctrine | bottle receipt |

**On upgrading — the GOBLIN scaffolding list:**

GOBLIN cannot decide which upgrades to ship, but can stage:

- For each bottled doctrine: an enforcement-script skeleton
- For each open-halt: a register entry
- For each cross-session-contaminated file: a quarantine candidacy
- For each TEMPLE output: a category marker

GOBLIN's discipline (per the just-bottled GOBLIN role definition):
**no canonical mutation without sovereign release.** Every item above
is non-sovereign; each requires Tool+Command+Log+Receipt to a
non-sovereign artifact. None require HER/MAYOR/REDUCER ruling to
produce — but several require it before they become enforced.

---

## §5. Tension matrix — where the three voices disagree

| Topic | HER | HAL | GOBLIN | Real tension |
| --- | --- | --- | --- | --- |
| helen_say.py fix | "highest leverage debug" | "may indicate silent bypass" | "small Edit, single commit" | HAL wants forensic audit BEFORE the fix; HER+GOBLIN want fix first |
| jsonschema install | "cheapest debug per value" | "system-pip hack; needs sunset" | "single pip command" | HAL wants the workaround marked as temporary with a sunset metric |
| Chiddush roadmap | "9 items in cost order" | "no CI gates exist for any doctrine" | "can bottle them as Write" | HAL wants enforcement before bottling more; HER wants speed |
| Cross-session contamination | "bottle attribution doctrine" | "subtract by deletion / archive" | "can quarantine via mv" | HER wants new doctrine to govern the issue; HAL wants old artifacts removed |
| TEMPLE outputs | "necessary for chiddush extraction" | "no admission protocol; accumulation" | "can mark with class header" | HAL wants protocol before more TEMPLE writes |
| Identity gate Phase 1 | "doctrine ready; implement" | "another upgrade adds surface area" | "small tool, one file" | HAL wants subtraction first; HER wants forward motion |
| CLAUDE.md drift | "5 corrections in one PR" | "drift will re-accumulate without register" | "can do as one Edit chain" | HAL wants register first; HER wants symptom relief now |

**The dominant pattern:** HER wants to build forward; HAL wants to
subtract and instrument first; GOBLIN sees both moves as tractable
but cannot pick.

---

## §6. Where the three voices agree (rare and important)

Three items survived all three voices without disagreement:

1. **helen_say.py is the most urgent debug.** HER calls it
   highest-leverage; HAL calls it potentially silent bypass; GOBLIN
   calls it a single Edit. All three agree on priority.
2. **`HALT_BOUNDARY_DISCIPLINE_V0` is currently paper, not
   enforcement.** All three voices observe that the doctrine landed
   without a CI gate to enforce its required section. This is a
   convergent finding.
3. **The bell's chiddush about doctrine kernels** (BELL_TRANSLATION
   §4 C5 — compact operative form vs surrounding verses) is
   universally praised: HER sees it as an upgrade pattern, HAL sees
   it as a subtraction discipline (extract kernel, discard verses),
   GOBLIN sees it as a refactor it could execute.

Convergent findings under three-voice review are rare. These three
are unusually robust — they would survive even a more adversarial
voice configuration.

---

## §7. The meditation's emergent thread

Reading across all three voices, one shape repeats:

> **HELEN's kernel is sound; HELEN's carrier is fragile.**

The ledger is hash-chained and intact. The schemas parse. The gates
run. The proposals are uniformly NON_SOVEREIGN. The doctrine is in
good shape.

What's broken or rotting:
- The writer (helen_say.py) that feeds the ledger
- The environment (venv hacks, system pip, missing deps)
- The documentation (CLAUDE.md drift)
- The portability (Mac paths)
- The cross-session attribution (contamination wider than visible)
- The enforcement (paper doctrines without CI gates)
- The TEMPLE category (outputs accumulate without protocol)

These are all **carrier-layer** issues, not kernel-layer issues.

The bell on the Jain temple captures this exactly: the inscription
(kernel) outlives the carrier (bell metal). When the carrier is
worn, you recast it. When the carrier is broken, you replace it. The
inscription does not change. The doctrine is portable; the
implementation is not.

**The debug priority is carrier rehabilitation.**
**The upgrade priority is carrier sustainability.**

Both are about the carrier, not the kernel.

This is unusual for a system in its current life-stage. Most systems
in HELEN's position face kernel-class issues (broken invariants,
unsound gates, leaked authority). HELEN does not. HELEN faces
infrastructure decay around an intact kernel.

GOBLIN, HER, and HAL all see this — under different vocabularies.
The meditation makes the convergence visible.

---

## §8. What this meditation does NOT produce

Per NO CLAIM and TEMPLE constraints:

- **Not a decision** on what to debug or upgrade first
- **Not a doctrine** about the kernel/carrier distinction (would
  require HER ruling and a separate proposal)
- **Not a schedule** for any of the actions listed in §4
- **Not an authorization** for GOBLIN to execute any of them
- **Not a binding interpretation** of HER, HAL, or GOBLIN voices —
  the three voices are stylistic devices, not sovereign actors
- **Not 500 epochs** — one substantial meditation, not 500 outputs
- **Not an admission** into HELEN's canon — TEMPLE layer, NO CLAIM

---

## §9. Halt boundary

GOBLIN halts here. The meditation is complete in TEMPLE mode.

Resume conditions:

1. **HER ruling** on whether the kernel/carrier emergent thread (§7)
   warrants doctrinal extraction — would land as a new proposal at
   roadmap-class scope, separate from this meditation.
2. **HER ruling** on which (if any) of GOBLIN's §4 action items
   to authorize for execution. Each item produces a separate
   receipt; none requires another sovereign decision once authorized.
3. **HAL invitation** for an adversarial second-pass on this
   meditation. The three voices here were cooperative; an
   adversarial HAL might find rot in the meditation itself.
4. **Operator decision** on TEMPLE category formalization (HAL §3
   item: TEMPLE admission protocol). Without it, this artifact and
   any future TEMPLE outputs share lifecycle markers with
   doctrinal proposals, blurring category lines.

Discipline followed: `HALT_BOUNDARY_DISCIPLINE_V0` (commit 5d0e04e).

---

## §10. Single line

> **HELEN's kernel is sound. HELEN's carrier is rotting.
> All three voices agree on the diagnosis; HER wants forward,
> HAL wants subtraction, GOBLIN can do either.
> The meditation makes the choice visible; it does not make it.**
