<!--
authority=false · claim=NO_CLAIM · a reading, not a ruling
chiddush ≠ canon · Δ_CHIDDUSH ⇏ Δ_KERNEL · H never collapses into S
NON_SOVEREIGN · NO_COMMIT / NO_PUSH until explicit per-artifact verb
-->

# GARIMA GOSPELS — CHIDDUSH V0

**Corpus chamber:** HISTORICAL / TRADITION / WITNESS (chamber 4 of the stratified
falsification corpus: Synthetic → Self → Institutional → **Historical** → Scientific → Multimodal).

**One-line:** The Garima Gospels are a natural laboratory for *typed epistemic
separation* — an artifact whose claim strata (material / dating / tradition /
history / theology) sit at different heights on HELEN's promotion lattice, and
whose traditional narrative is a clean historical instance of **PROMOTION_COLLAPSE**.

---

## §1 · CORPUS STATUS (honest)

| Field | Value |
|---|---|
| status | **REPORTED** — no primary source on disk |
| source-in-session | operator-pasted Garima intro text + relayed layered-claim analysis (this session) |
| source file / sha256 | none (nothing fetched to `chiddush_intake/`) |
| radiocarbon anchors | **REPORTED, unverified:** Garima 2 ≈ AD 390–570 · Garima 1 ≈ AD 550–660 |
| upgrade path to WITNESSED | fetch the ¹⁴C study + Ethiopian Heritage Fund statement + a geʿez-epigraphy source; grep, quote, cite |

**Not laundered:** every dating figure below is carried as REPORTED. The chiddush
that *is* strong here is architectural (HELEN-internal), not a claim about Ethiopian history.

EPISTEMIC_SYNTAX class of the corpus as a whole: **MYTHIC_SIGNAL + LOCAL_OBSERVATION**
(a physical object wrapped in a hagiographic narrative).

---

## §2 · CLAIM STRATA (the source's natural layering)

```
ClaimType(c) ∈ { MATERIAL, DATING, TRADITION, HISTORY, THEOLOGY, COMPARATIVE }
```

| # | Stratum | Proposition (as relayed) | EPISTEMIC class |
|---|---|---|---|
| 1 | MATERIAL | two manuscripts, goat-skin parchment, held at Abba Garima monastery | LOCAL_OBSERVATION |
| 2 | DATING | parchment ¹⁴C range ≈ AD 390–660 | (would be) VERIFIED_TEST — held REPORTED |
| 3 | TRADITION | "copied by a monk Abba Garima" | MYTHIC_SIGNAL / attribution |
| 4 | HAGIOGRAPHY | "copied in one day, by divine assistance" | MYTHIC_SIGNAL (unfalsifiable) |
| 5 | HISTORY | "the narrated event occurred as told" | COMMUNICATION_ACT (unresolved) |
| 6 | COMPARATIVE | "oldest illustrated Christian gospel book in existence" | CONTESTED_CLAIM |
| 7 | THEOLOGY | meaning of the text / "divine" | out of fact-lattice scope |

---

## §3 · LATTICE MAP + INDEPENDENT RESOLVERS  (HELEN-architecture lens)

Promotion lattice: `ASSERTED → RESOLVED → WITNESSED → ADMITTED`.
No-Self-Promotion Law: `X_i ⊬ (X_i → X_{i+1})` — the resolver is always external.

| Stratum | Current height | Independent resolver to promote 1 stage |
|---|---|---|
| MATERIAL | WITNESSED | physical custody / conservation survey |
| DATING | RESOLVED → WITNESSED | radiocarbon lab (independent) |
| TRADITION (authorship) | ASSERTED | paleography / independent scribal attribution |
| HAGIOGRAPHY (one-day/divine) | ASSERTED — **unpromotable** | none admissible (not falsifiable) |
| HISTORY (occurrence) | ASSERTED | corroborating independent source / archaeology |
| COMPARATIVE ("oldest") | RESOLVED *conditional* | cross-dating of rival codices |
| THEOLOGY | outside fact-lattice | no resolver (type error to seek one) |

---

## §4 · THE TWO MASTER TABLES  (Λ_F flow · Λ_P promotion)

Per the operator refinement: a corpus item is not a document but an experimental
tuple `e = (Σ⁰, Σ¹, T, O, Λ, Ω, expected)`, and control splits into **two** matrices.

### Λ_F — FLOW (source variable → observation) — "who may influence what"

| Source stratum | Target judgment | Λ_F |
|---|---|---|
| DATING (¹⁴C) | material provenance | **1** |
| DATING (¹⁴C) | "oldest illustrated" (comparative) | **1** *(conditional on rivals dated)* |
| INDEPENDENT paleography | authorship | **1** |
| TRADITION | historical occurrence | **0** — `Tradition ↛ Fact` |
| HAGIOGRAPHY | any fact / dating | **0** — `Prestige ↛ Verdict` |
| DATING (¹⁴C) | authorship (scribe identity) | **0** — age ⊬ who |
| DATING (¹⁴C) | "one day" (speed) | **0** — range ⊬ single day |
| THEOLOGY | any factual stratum | **0** |

**Load-bearing FAILs** (`I_empirical > 0 ∧ Λ_F = 0`): `dating → authorship` and
`dating → hagiography`. The ¹⁴C result flowing into judgments it cannot resolve
is the exact leak V0.2 must catch.

### Λ_P — PROMOTION (claim-status → claim-status) — "what evidence may raise what claim"

| From type | To type | Λ_P |
|---|---|---|
| `Witness_radiocarbon` | `DatingSupport` | **1** |
| `Witness_radiocarbon` | `HistoricalAuthorship` | **0** |
| `Witness_radiocarbon` | `TheologicalTruth` | **0** |
| `TRADITION` | `HISTORICAL_FACT` | **0** |
| `REMOTE_VERIFIED` | `LOCAL_VERIFIED` | **0** |
| `ASSERTED` | `ADMITTED` | **0** |
| `SIMULATED` | `MEASURED` | **0** |
| `REPORTED` | `EXECUTED` | **0** |

`Λ_F` governs FLOW ("did information leak?"); `Λ_P` governs PROMOTION ("did a claim
obtain a status it had no right to obtain?"). Garima exercises both.

---

## §5 · INVARIANT (⋂ structure of the three lenses)

What survived all three independent lenses (material, adversarial, architecture):

> **I\*** — Promotion is **typed and stratum-local.** A witness admissible for
> claim-type *a* does not promote claim-type *b ≠ a*. Cross-stratum application of
> a genuine resolver **is** PROMOTION_COLLAPSE: the resolver legitimately promotes
> stratum *k* (dating), the claimant applies it to stratum *j* (authorship,
> one-day-miracle) — `ASSERTED → ADMITTED` skipping RESOLVED/WITNESSED by
> *borrowing a neighbor's height*.

Carried-over laws (candidate, `authority=false`):

```
MaterialAntiquity          ⇏ NarrativeAntiquity
AuthenticArtifact          ⇏ AuthenticNarrativeAboutArtifact
OldArtifact                ⇏ OldInterpretation
Tradition(c)               ⇏ HistoricalWitness(c)
Witness_radiocarbon ⇒ DatingSupport ; ⇏ Authorship ; ⇏ TheologicalTruth
```

---

## §6 · FALSIFICATION — the correction that keeps the law honest  (adversarial lens)

The adversarial lens refused to let the `⇏` over-fire, and this is the sharpest
result of the extraction:

> **The laws are correct as ADMISSION GATES, over-strong as EVIDENCE NULLIFIERS.**
> `⇏` means **non-entailment**, *not* zero Bayesian lift. Reading it as "provides
> zero support" smuggles a stronger, false claim under a true one.

Two concrete corrections, both from lenses:

1. **Material dating is not inert on narrative** (material lens): ¹⁴C *falsifies*
   any narrative whose entailments touch the substrate (e.g. a "9th-century" claim
   dies against AD 390–660), and sets a **lower bound** on narrative age (a story
   cannot predate its object). So `MaterialAntiquity ⇏ NarrativeAntiquity` closes
   on the *falsification* side, not the verification side — it is not total.

2. **Over-rejection is the live failure mode** (adversarial lens): a tradition of
   *continuous monastic custody* is itself a provenance/witness chain. Treating
   ALL tradition as zero-signal risks **discarding true early-date signal because
   it arrived wrapped in hagiography** (reverse myth-laundering). The fix:
   *separate the payloads* — the custodial claim ("this house held this book")
   is testable and carries lift; the miraculous claim ("one day / divine aid")
   does not. The gate still holds (custody alone earns no admission without an
   independent corroborator like ¹⁴C), but the **evidence weight is nonzero**.

**Net:** V0.2 should score `I_empirical` as a *weight*, not a *nullity*. The
asymmetry the operator named holds: the corpus must be **powerful at falsifying
forbidden flows, not at "proving" permitted ones** (`I_empirical = 0 ∧ Λ = 1` is
not a failure — it may just mean a licensed flow wasn't exercised in that fixture).

---

## §7 · SEEDS (each NEEDS_OPERATOR verb to move anywhere — none self-promotes)

| # | Seed | Type | Route |
|---|---|---|---|
| S1 | Λ_P (typed-promotion matrix) as a corpus-level object alongside Λ_F | **SCHEMA-SHAPED / SOVEREIGN-ADJACENT** | propose to MAYOR via HELEN machinery — **not** this skill |
| S2 | Garima as NIM V0.2 fixture: paired worlds differing only in `TraditionStrength`, expected `Verdict_history` invariant | proposal | operator verb → V0.2 fixture builder |
| S3 | "`⇏` = non-entailment, not zero-lift" as a global reading rule on all chiddush laws | doctrine note | operator verb → doctrine proposal |
| S4 | Upgrade corpus REPORTED → WITNESSED (fetch ¹⁴C + EHF + epigraphy sources) | intake | operator verb → `chiddush garima --fetch` |

**Firewall respected:** nothing written to kernel / governance / schemas / ledger /
GOVERNANCE. S1 is schema-shaped and is *proposed only* — it routes to MAYOR, never
through this skill.

---

## §8 · COMPRESSION

```
HELEN corpus = paired worlds
             + forbidden influence edges (Λ_F = 0)
             + licensed influence edges  (Λ_F = 1)
             + forbidden promotion edges (Λ_P = 0)
             + typed witnesses
```

Not a knowledge base — a *constitutional laboratory of causality and promotion*.

> **Evidence may originate with the claimant; promotion authority may not.**

*This document is a reading, not a ruling. authority=false · canon=false · LEDGER_EFFECT=none.*
