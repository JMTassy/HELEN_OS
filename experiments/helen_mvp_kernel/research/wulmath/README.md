# WULMATH_COMPRESSION_V0

The full HELEN OS kernel constitution, compressed to its algebraic
skeleton and coloured by the sigil palette.

## What it is

`verify.py` registers 108 adversarial probes. Each probe attacks the
kernel and holds only when the attack is **refused**. The probe names
are already a prose compression of the constitution; this receipt
renders each one in WULmath — the non-entailment algebra the project
reasons in — and assigns it one of the seven sigil vibrations.

The central operator is `⊬`. Almost everything the constitution does
is refuse an entailment, which is why the compression ratio is what it
is: the kernel is mostly the enumeration of what does *not* follow.

## Census (measured, not asserted)

| quantity | value | how derived |
|---|---|---|
| kernel LOC | 39,541 | `find helen_os -name '*.py' \| xargs wc -l` |
| constitution LOC | 22,184 | same, `kernel/constitution`, excluding `test_*` |
| test LOC | 14,537 | same, `test_*.py` |
| distinct refusal codes | 649 | `grep -ohE '"E_[A-Z0-9_]+"' \| sort -u \| wc -l` |
| probes held | 108 / 108 | `python3 -m helen_os.kernel.constitution.verify` |
| compression | 366 LOC per law | 39,541 / 108 |

Gate receipt at the time of writing:
`6d2f86b8d8c775fc3c360ef138bb67d0214231aaa19c47b470b6e738c63392e4`
· `CONSTITUTION_HELD`.

## Axioms carried at the head

```
Compute ⊢ ΔRepresentation   ·   Compute ⊬ ΔReality
Witness ∘ Admit ⊢ ΔReality

Admit ⟺ PROOF ∧ SCOPE ∧ AUTHORITY ∧ REPLAY
C₅ unearned · completeness = UNKNOWN

□(¬illegal mutation) ∧ ◇(critical reachable obligation ⇒ resolution)

Retain ⊬ Admit ⊬ Authorize
```

## Colour

The palette is **not** invented for this page. It is read from
`design/skill_sigil_tokens.json`, whose own laws govern the render:

- `no_state_by_color_alone` — every coloured row carries its mono text
  label; colour is redundant encoding.
- `composed_not_decorated` — each vibration cites the kernel function
  it stands for.
- `static_sigils` — no ambient motion.
- `signature_gesture` — the hem: the plate and every stratum are
  bordered, the admission boundary made visible.
- `representation_only` — `(dP, dA, dE) = (0, 0, 0)`; the verdict word
  appears only adjacent to its receipt hash.

| vib | name | function | laws |
|---|---|---|---|
| 1 | red_oxide | stability · foundation | 15 |
| 2 | orange_earth | flow · creation | 8 |
| 3 | ochre_gold | power · transformation | 13 |
| 4 | green_deep | harmony · relationship | 13 |
| 5 | blue_slate | expression · truth | 22 |
| 6 | indigo | intuition · perception | 16 |
| 7 | violet_white | unity · human handoff | 21 |

`blue_slate` (evidence, receipts, replay, witness) is the largest
stratum at 22, and `violet_white` (admission, obligation, human
handoff) the second at 21. That distribution is a finding, not a
design choice: the constitution spends most of itself on what counts
as evidence and on who may close a decision.

## Re-deriving it

```bash
cd experiments/helen_mvp_kernel/research/wulmath
python3 gen.py          # writes helen_wulmath.html
python3 - <<'PY'        # checks the names against the live gate
import sys; sys.path[:0] = [
  "../../helen_os/kernel/constitution", "../../helen_os/gates/effect_gate"]
import verify
from wul_data import LAWS
src = {i: p["probe"] for i, p in enumerate(verify._probes(), 1)}
assert [l[1] for l in LAWS] == [src[i] for i in range(1, 109)]
print("108 names match verify._probes()")
PY
```

The assertion is the point: if a probe is renamed, added or removed and
this table is not regenerated, the check fails. A compression that
cannot be re-derived from the source is a seal without an admission.

## Standing

`authority=false · canon=false · ledger_effect=none`. This is a
**representation** of the constitution. It compresses it; it does not
hold it — the holding is done by the probes, in the gate, on each run.

## Non-deltas

The WULmath lines are a *rendering* of each probe's stated law, written
by hand; they are checked against the probe **names** automatically but
not against the probe **bodies**. A line could therefore drift from what
its probe actually asserts without the check firing. No claim is made
that the seven-vibration assignment is unique or forced — it is a
reading, and `duplicate_numbers` in the token file already concedes
that derivation, not uniqueness, is what is required.
