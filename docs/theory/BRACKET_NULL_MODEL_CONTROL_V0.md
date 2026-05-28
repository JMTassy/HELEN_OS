# BRACKET_NULL_MODEL_CONTROL_V0

**authority:** NON_SOVEREIGN
**canon:** NO_SHIP
**lifecycle:** TEMPLE_EXPLORATION (control-test contract)
**framing:** NO CLAIM
**status:** Statistical control — distinguishes real bracket signal from ordinary noise
**operator_directive:** "freeze the Null Model / Control Test" (2026-05-23)
**parent_artifacts:**
  - `docs/theory/HEISENBERG_BRACKET_REPLAY_TEST_V0.md`
  - `docs/theory/STRATIFIED_GENERATOR_BASIS_V0.md`
  - `docs/theory/BRACKET_MEASUREMENT_SCHEMA_V0.md`
**frozen_engine:** `GOVERNANCE/TRANCHE_RECEIPTS/E25-engine-doctrine-freeze-V1.json` (respected)
**proposer:** claude-opus-4-7 acting as GOBLIN
**attestor:** pending

> **NO CLAIM disclaimer.** This artifact specifies the **statistical
> control layer** for the bracket-test diagnostic chain. It is the
> last pre-implementation rigor item. Without it, any positive
> `bracket_gain` from the Heisenberg or stratified tests could still
> be explained as ordinary noise on top of lawful operations. With
> it, the test is held to a 3-sigma threshold against statistically
> matched null loops.

---

## §1. Purpose

The `BRACKET_MEASUREMENT_SCHEMA_V0` defines `bracket_gain` precisely
and specifies the `noise_floor` operator-class threshold. But
"noise_floor" is operator-calibrated, not empirically derived. A
hostile reviewer could legitimately ask:

> *How do you know `bracket_gain > noise_floor` is not just the
> ordinary baseline noise of running ANY lawful loop?*

This bottle answers that question. It defines a **null model**: a
family of lawful, trivial (non-bracket) loops that should produce
near-zero `bracket_gain` by construction. Real bracket signal must
exceed the null distribution by a statistically defensible margin
(3-sigma).

Without this control, the entire diagnostic chain remains
operator-defendable but not scientifically grounded.

---

## §2. The null-model loop family

Four control loops, all lawful, all closed, all using only the
primitive horizontal generators from `CC_GEOMETRY §4.2` but **without
any bracket-generating composition**.

### §2.1 Identity loops (single round-trip)

```
Loop N1:    X  →  -X        (source inspection + replay-verify)
Loop N2:    Y  →  -Y        (boundary-replay + replay-verify)
```

These are the simplest possible lawful loops. By construction, they
should produce minimal-to-zero net field displacement.

### §2.2 Doubled identity loops (no commutator structure)

```
Loop N3:    X → X → -X → -X
Loop N4:    Y → Y → -Y → -Y
```

These have the same 4-step length as the Heisenberg loop
(`X → Y → -X → -Y`) but **without the bracket pattern** (no
commutator structure — `[X,X] = 0` and `[Y,Y] = 0` in any Lie
algebra). They control for: "is the gain due to the bracket
pattern or just to running 4 lawful steps?"

### §2.3 What the null family deliberately tests

| Pattern | Real-bracket case | Null case |
| --- | --- | --- |
| Loop length | 4 steps | 4 steps (N3, N4) or 2 steps (N1, N2) |
| Lawfulness | required | required (same discipline) |
| Bracket structure | $[X, Y]$ — commutator pattern | none — repeated identities |
| Expected `bracket_gain` | > 0 if Hörmander locally holds | ≈ 0 by algebraic identity |

The null is **not** "do nothing" — it is "do lawful things that
should not generate brackets." Difference between real and null is
the signal.

---

## §3. Measurement (same schema as BRACKET_MEASUREMENT_SCHEMA_V0)

Each null-loop run produces a measurement record per
`BRACKET_MEASUREMENT_SCHEMA_V0 §7`. The same 11 mandatory fields and
4 derived metrics apply:

```
routing_delta, admission_delta, motif_delta, bracket_gain
violation_count, replay_fidelity, policy drift, receipt-chain integrity
```

No special handling. The null model uses the exact same instrument
as the Heisenberg test. That is the point — apples to apples.

---

## §4. The null distribution

Run each null-loop type (N1, N2, N3, N4) repeatedly — say $n \geq
30$ times per type — to build a sample distribution of
`bracket_gain` under the null hypothesis.

Compute:

```
null_gain_mean = mean(bracket_gain across all null runs)
null_gain_std  = std(bracket_gain across all null runs)
```

The null distribution must be:

- **Stable** under repeated sampling (low variance of the mean
  across sample batches)
- **Lawful** (every null run satisfies `violation_count = 0` and
  `replay_fidelity = 1.0`; null runs that fail these are discarded,
  not included in the distribution — the null is a *clean baseline*)

---

## §5. Statistical acceptance condition

For the Heisenberg bracket test (or any stratified-layer test) to
KEEP, all of the following must hold:

```
real_bracket_gain  >  null_gain_mean + 3 · null_gain_std        (3-sigma)
violation_count    =  0
replay_fidelity    =  1.0
```

3-sigma corresponds to ≈ 0.27% false-positive rate under Gaussian
null assumptions. Higher rigor (4σ, 5σ) is permissible if operator
calibrates; lower than 3σ is rejected.

---

## §6. Hard kill switch

```
Heisenberg loop gain  ≤  null model gain  (within statistical tolerance)
=  reject holonomy interpretation
```

If the bracket test cannot statistically distinguish itself from the
null, the observed gain is **not** evidence of holonomy. It is
evidence of ordinary lawful-loop variance. Discard the holonomy
interpretation; the engine may still be doing useful work, but it
is not bracket-generating in any measurable sense.

This is non-negotiable. The 3-sigma rule is not advisory.

---

## §7. Why this matters

Without a null model:

- Any positive `bracket_gain` can be rationalized as meaningful
- "Noise floor" is operator-defined and arbitrary
- Reviewers cannot distinguish HELEN's holonomy claim from
  base-rate variance on any lawful operation
- The geometric interpretation remains literally unfalsifiable

With the null model:

- The bracket test is held to a falsifiable standard
- The Hörmander-condition claim has a real failure case (gain
  indistinguishable from null)
- The diagnostic chain can produce **negative results** that mean
  something
- Scientific rigor is applied to constitutional diagnostics

This is the rigor layer the chain was missing.

---

## §8. Sequence position — the chain is now complete

```
1. CONSTITUTIONAL_HOLONOMY_OBSERVABLE_V0
       loop-level observable Δ_γ
2. HEISENBERG_BRACKET_REPLAY_TEST_V0
       single bracket: V₁ × V₁ → V₂
3. STRATIFIED_GENERATOR_BASIS_V0
       multi-layer cascade: V₁ → V₂ → V₃ → ... → V_K
4. BRACKET_MEASUREMENT_SCHEMA_V0
       anti-poetry contract (numeric pre/post or no gain)
5. BRACKET_NULL_MODEL_CONTROL_V0          ← this artifact
       statistical control (3-sigma against lawful non-bracket loops)
```

After this bottle, the diagnostic chain is **complete in spec**.
Implementation remains explicitly blocked by E25 engine freeze.
Anything beyond this requires sovereign authorization.

---

## §9. Connection to existing canon

| Existing artifact | Relation |
| --- | --- |
| `HEISENBERG_BRACKET_REPLAY_TEST_V0` | The real-bracket case this null model controls against; its KEEP rule now requires the §5 statistical condition |
| `STRATIFIED_GENERATOR_BASIS_V0` | Each layer-$k$ keep rule should likewise require statistical significance against a per-layer null (extending §5 to multi-layer is straightforward — flagged in §10) |
| `BRACKET_MEASUREMENT_SCHEMA_V0` | Same schema used here — no parallel measurement system; the null and real loops share the instrument |
| `CONSTITUTIONAL_HOLONOMY_OBSERVABLE_V0` | The 3-sigma rule applies to its `holonomy_norm` measurement as well — what counts as "good holonomy" must exceed null |
| `CONSTITUTIONAL_CC_GEOMETRY_V0 §4.5` | The Hörmander-condition claim (currently unverified) gains a falsifiable test: if no bracket passes the 3-sigma null gate, the engine is not bracket-generating in any measurable sense |
| `E25-engine-doctrine-freeze-V1.json` | Freeze respected — control test is spec, not implementation |
| `HALT_BOUNDARY_DISCIPLINE_V0` | Followed (§10) |

---

## §10. What this proposal does NOT specify

Per anti-creep discipline:

- **The exact $n$ for null sample size** — $n \geq 30$ recommended; operator-class
- **The Gaussian assumption** — if the null distribution is non-normal,
  replace 3-sigma with a non-parametric equivalent (e.g., 99th
  percentile). Out of scope here; operator-class
- **Multi-layer null calibration** — for `STRATIFIED_GENERATOR_BASIS_V0`,
  each layer $k$ needs its own null distribution from level-$k$
  trivial loops; the extension is straightforward but not specified
- **The implementation of the null runner** — same E25 freeze
  considerations as the rest of the diagnostic chain
- **Cross-bracket null correlation** — if different brackets share
  null distributions or require independent ones; open
- **Adversarial null gaming** — can an attacker construct null loops
  that artificially inflate null variance? Open question; out of
  scope

---

## §11. Halt boundary

GOBLIN halts here. The control test is bottled as
`TEMPLE_EXPLORATION`. The diagnostic chain is now complete in spec.

Resume conditions:

1. **HER ruling** on the control-test spec — accept or specify
   amendments
2. **HER ruling** on the sample size $n$ (default $n \geq 30$
   recommended)
3. **HER ruling** on the Gaussian assumption — accept 3-sigma, or
   specify non-parametric alternative
4. **HER ruling** on multi-layer null extension for
   `STRATIFIED_GENERATOR_BASIS_V0`
5. **Sovereign decision** on running the null and bracket tests
   together — requires implementing the null-loop runner, the
   distribution computer, the statistical test; all blocked by E25
   freeze
6. **No edit to any frozen doctrine** is requested or performed
7. **No implementation authorization** is requested or granted

Discipline followed: `HALT_BOUNDARY_DISCIPLINE_V0` (commit `5d0e04e`).

---

## §12. Single line

> **The diagnostic chain is now complete. Five artifacts specify
> what to measure, on what loops, against what null, with what
> 3-sigma threshold. Real holonomy must beat trivial-loop noise by
> three standard deviations. Anything less is base-rate variance
> wearing a geometric hat.**
