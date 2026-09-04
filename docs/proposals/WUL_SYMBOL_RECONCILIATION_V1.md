# WUL Symbol Reconciliation V1

```
banner        : 🔵 OBSERVED
zone          : GARDEN / NO_CLAIM · authority=false · admission=none · ledger_effect=none
class         : RECONCILIATION_REPORT (prerequisite to any WUL dictionary lock)
status        : PROPOSAL
date_recorded : 2026-08-09
inputs        : docs/wulmoji_ledger_spec.md (v0.2, DEPLOYED) ·
                tools/wulmoji_ledger_validator.py (DEPLOYED, validator-bound) ·
                relayed epistemic symbol-logic table (upstream, authority=DENY)
rule          : the DEPLOYED machine grammar is authoritative; later prose never overrides it
```

## 0. Purpose and non-goal

This is the reconciliation the `RECONCILE FIRST` fork required **before** any WUL
dictionary is frozen. It does exactly three things (§A, §B, §C) plus the typed
resolution (§D). It does **not** lock a dictionary, and it does **not** modify
`tools/wulmoji_ledger_validator.py` or `docs/wulmoji_ledger_spec.md`. The
validator remains the single source of truth for ledger-line glyph meaning.

Governing principle (from the relayed analysis, adopted):
```
glyph meaning is TYPED by namespace, not universal.
On any collision, the deployed ledger.* meaning WINS inside a ledger line.
```

## A. Collision table

Deployed reserved glyphs (all fields of `docs/wulmoji_ledger_spec.md`) vs the
proposed epistemic meanings:

| glyph | DEPLOYED (field · meaning) | PROPOSED epistemic | status |
|---|---|---|---|
| 🔵 | State · **Pending** | observed fact / licensed info | **COLLISION** |
| 🟢 | State · **Pass** | PASS / safe-to-continue | ALIGNED (compatible) |
| 🟣 | State · **Oracle** | diagnosis / hypothesis | **COLLISION** |
| ⚫ | State · **Alert** | blocked / denied | NEAR-COLLISION |
| 🔴 | State · **Block** | FAIL / contradiction | NEAR (compatible) |
| 📜 | Act · **Decree** (also in Ribbon exemplars) | ledger / governed memory | **COLLISION (role)** |
| 🔒📜 | Act · Sealed decree | — | no proposal conflict |
| ⚠️📜 | Act · Warning decree | — | no proposal conflict |
| 🛡️ | Act · Guard | — | no proposal conflict |
| 🔗 | Proof · link prefix `🔗#ID` | — | no proposal conflict |
| ⟂◯⟂ 🌹 🌀 ✝️ | Faction | — (🌀 was aesthetic "recursion" in Gen-0) | latent aesthetic-only |
| 🜃 🜄 🜁 🜂 🜍 | Pair · alchemy transition | — | no proposal conflict |
| ⚠️ | scoped warning (Act only) | — | no proposal conflict |

Net: **3 hard collisions** (🔵, 🟣, 📜), **2 near** (⚫, 🔴), rest clean.

## B. Namespace decision (deployed wins)

Typed namespaces:
```
WUL.ledger      deployed positional grammar · VALIDATOR-BOUND · authoritative
WUL.epistemic   SOPHIA/HER/HAL doctrine prose notation · authority=0 · prose-only
WUL.aesthetic   Gen-0 symbolic/interface use · no governance semantics
```

Resolution per collision — `⟦g⟧_τ` = meaning of glyph `g` in namespace `τ`:

| glyph | ⟦g⟧_ledger (AUTHORITATIVE) | ⟦g⟧_epistemic (prose-only) | rule |
|---|---|---|---|
| 🔵 | Pending | OBSERVED | in a ledger line 🔵 = Pending, full stop; epistemic use only in prose |
| 🟣 | Oracle | DIAGNOSIS | ledger meaning wins in-line; prose may say DIAGNOSIS |
| 🟢 | Pass | PASS | already compatible — keep both, still typed |
| ⚫ | Alert | (prefer new glyph) | keep ⚫=Alert in ledger; **epistemic "blocked" should use a distinct glyph** (see §C) |
| 🔴 | Block | FAIL | compatible; namespaced |
| 📜 | Act·Decree | ledger/governed-memory | 📜 stays the Act token in ledger lines; prose "ledger" meaning allowed but see caveat |

**Hard rules (invariants of this reconciliation):**
1. This report does **not** touch the validator or spec. `WUL.ledger` is frozen as-is.
2. Any glyph appearing in a validator-parsed ledger line takes its `WUL.ledger`
   meaning — no exceptions, no epistemic override.
3. `WUL.epistemic` and `WUL.aesthetic` glyphs are **prose-only**. Never emit an
   epistemic-meaning glyph into a line that will be fed to
   `wulmoji_ledger_validator.py`.
4. WULmoji core law preserved: `glyph ⇏ state · glyph ⇏ authority · glyph ⇏ claim`.
5. `📜` caveat: it is heavily overloaded (Act token AND doctrine "ledger"). In
   doctrine prose, prefer writing "ledger" or a namespaced `WUL.ledger::📜`
   token when precision matters, to avoid readers mistaking prose for a Decree act.

## C. New clean symbols (no conflict — free for WUL.epistemic)

These proposed glyphs are **absent** from the deployed grammar and may be used
in epistemic doctrine prose without collision:
```
👁️ observe/witness   🟡 UNKNOWN/HOLD/obligation   🟠 candidate/Garden seed
🩵 SOPHIA nutrient    🟨 admitted/governed state    ⚖️ HAL/adjudication
Γ  admission seam     🧾 receipt                    👑 authority/sovereign effect
🌿 Garden             🍂 failure material           🌰 seed/reusable nutrient
🧪 experiment         🧠 memory/context
```
Operators (not Unicode-cluster glyphs; no grammar conflict):
```
⊬ does-not-imply   ↛ forbidden-transition   → allowed-transformation
≠ distinction      ⊥ authority-zero          Δ change   ∅ absent   ? unknown
```

**Recommendation for the two near-collisions:** to keep the epistemic layer
readable *and* collision-free, use the clean glyphs instead of overloading:
- epistemic "blocked/denied" → **⚫ carries Alert in ledger**, so in doctrine
  prefer the operator form `↛` / `∅ effect` or reserve a distinct mark rather
  than reusing ⚫.
- epistemic "admitted" → **🟨** (clean, no ledger-State conflict) — do NOT reuse
  a State-field color for admission.

## D. What a future dictionary may safely contain

A subsequent `WUL_DOCTRINE_SYMBOLS_V1` (separate verb) may lock **only**:
- the `WUL.epistemic` clean glyphs from §C, and
- the collision glyphs **explicitly namespaced** per §B (`⟦🔵⟧_epistemic`, etc.),

and must carry the standing rule "deployed `WUL.ledger` grammar is authoritative;
this layer is prose-only." The firewall renderings from the relayed table are
consistent with existing SOT doctrine and may be reused verbatim:
```
🌿 ↛ 📜      Garden never writes ledger
SOPHIA ↛ 📜  reflection never writes ledger
🟢 ⊬ 🟨      HAL PASS does not imply admission
🟣 ⊬ 🔵      diagnosis does not imply licensed fact
🔴 ⊬ ¬h      failure does not imply hypothesis false
(🌿 ∪ SOPHIA)* ↛ 👑   authority never bootstraps upstream
```
These match `ETA_CALCULUS_V0_1.md §9` and the persona docs' non-promotion laws.

## E. Verdict

```
RECONCILED     : yes — 3 collisions + 2 near resolved by typed namespaces
DEPLOYED SPEC  : untouched · validator untouched
DICTIONARY     : NOT locked (this is the prerequisite report, per RECONCILE FIRST)
NEXT VERB      : WRITE DOCTRINE DICT (epistemic layer, §C + §B namespacing) | HOLD
authority=0 · canon=FALSE · ledger_effect=NONE
```
