<!--
authority=false · claim=NO_CLAIM · a reading, not a ruling
chiddush ≠ canon · Δ_CHIDDUSH ⇏ Δ_KERNEL · H never collapses into S
NON_SOVEREIGN · NO_COMMIT / NO_PUSH until explicit per-artifact verb
Extraction is DOCTRINE-ONLY: governance/architecture patterns, not operational crypto.
-->

# QUANTUM / ECDLP DISCLOSURE — CHIDDUSH V0

**Source:** Babbush, Zalcman, Gidney, Broughton, Khattar, Neven, Bergamaschi,
Drake, Boneh — *"Securing Elliptic Curve Cryptocurrencies against Quantum
Vulnerabilities: Resource Estimates and Mitigations"* (arXiv:2603.28846, 2026-03-30).

**Why for HELEN:** the paper is a responsible-disclosure whitepaper whose *method*
is HELEN's own constitution in a different domain — prove a capability exists
without releasing its mechanism, classify threats by their exploitation window,
and treat an unsubstantiated claim as itself an attack on confidence. It is a
natural stress-test of HELEN's witness / release / promotion doctrine.

---

## §1 · CORPUS STATUS (honest)

| Field | Value |
|---|---|
| status | **DOWNLOADED + WITNESSED-PARTIAL** |
| file | `~/helen_kernel/chiddush_intake/arxiv_2603_28846/paper.pdf` |
| sha256 | `1f59d951d24f360bb5fd89a25b22f28825519c65e17428f5ab204e7c2106ae99` |
| pages witnessed | **pp. 1–12 of 57** (front matter, TOC, §I intro, §II.A–C attack taxonomy + resource estimates + offensive-capability evolution, §III.A opening) |
| pages NOT read | pp. 13–57 (Bitcoin mechanics detail, Ethereum §V, other chains §VI, migration §VII, dormant assets §VIII, ZK-proof appendix) |
| crypto facts | held **REPORTED** — qubit counts (≤1200 logical / ≤90M Toffoli; ≤1450 / 70M), "9 min break", "half-million physical qubits", "2.3M vulnerable BTC" are the *authors'* estimates, ZK-validated by them, **not** independently verified here |

**Not laundered:** no quantum-resource claim is adopted as HELEN fact. The chiddush
is the *structural method*, which I witnessed directly.

EPISTEMIC_SYNTAX of the source: **VERIFIED_TEST (their ZK-validated estimate) wrapped in COMMUNICATION_ACT (policy argument).**

---

## §2 · THE SOURCE'S STRUCTURE (as witnessed)

Three doctrines the paper introduces, each with a direct HELEN twin:

1. **Attack taxonomy by execution window** (p.6): `on-spend` (break within the
   settlement window — sub-second to ~10 min), `at-rest` (days+, long-exposed
   keys), `on-setup` (compromise fixed protocol parameters once → reusable
   classical exploit; e.g. toxic-waste / trusted-setup capture).
2. **Disclosure model** (pp.3–7): publish *trustworthy resource estimates* to
   signal proximity, **withhold the circuits**; validate the estimate with a
   **zero-knowledge proof** (SP1 zkVM, SHA-256 commitment, Fiat–Shamir). Explicit
   claim: *"unsubstantiated resource estimates may themselves constitute a genuine
   or apparent attack"* (FUD).
3. **Fast-clock vs slow-clock architectures** (pp.6, 8–11): same asymptotic
   capability, wall-clock differing by 2–3 orders of magnitude → **which** threat
   class is live depends on the *substrate*, not the algorithm. Plus a **threshold
   model** (p.11): progress is discrete jumps; a 32-bit demo predicts imminent
   256-bit break; *"a public demonstration should not be seen as a wake-up call so
   much as a signal that PQC adoption has already failed."*

---

## §3 · CHIDDUSH MAPPING  (paper structure → HELEN structure)

Evidence-qualified edges `e = (source-concept, r, HELEN-concept, π, ε)`;
ε ∈ {explicit, derived, inferred, hypothesized}; π = page.

| Paper concept | → | HELEN concept | ε | π |
|---|---|---|---|---|
| ZK proof of resource cost (prove capability, withhold circuit) | ≅ | **LICENSED RELEASE (NIM V0.3):** `R=(s,t,x,p,τ,f,σ,a,w)` — release the *fact* under transform `f`=ZK, never the mechanism | derived | 4,7 |
| `CanProve(estimate) ∧ ¬Disclose(circuit)` | ≅ | `CanRead(x) ⇏ CanInfluence(x,y) ⇏ CanRelease(f(x),y)` | derived | 4 |
| "unsubstantiated estimate = FUD attack" | ≅ | **NO HASH = NO VOICE:** an unwitnessed claim is not neutral — it can be an attack on confidence | explicit→derived | 3 |
| resource estimate = *proximity signal*, not the weapon | ≅ | a WITNESS promotes ASSERTED→RESOLVED; it is not itself ADMITTED effect | derived | 3,7 |
| `on-setup` attack (capture the trusted setup / toxic waste) | ≅ | **META-CAPTURE / PROTECTION_ROOT_REBIND:** attack the parameters that govern all transitions, not one transition (`Δ Π_NIM ≠ 0 ⇒ δ_meta`) | derived | 6 |
| `on-spend` vs `at-rest` (window of exploitability) | ≅ | transition-window / seat-timing: which forbidden flow is *live* depends on latency | inferred | 6 |
| fast-clock vs slow-clock (same capability, different wall-clock) | ≅ | **capability composes, permission does not:** same computation, the *seat* decides feasibility (cf. Qwen seat-topology) | derived | 6,8 |
| threshold model (discrete jumps, no smooth metric) | ≅ | promotion lattice is **typed/discrete**, not continuous; safety can't be read off a smooth score (HAL-scorer / Goodhart lesson) | derived | 11 |
| "public demo = PQC already failed" (late witness) | ≅ | **a witness that arrives after admission has collapsed is not a gate** — receipts must precede effect, not narrate it | derived | 11 |
| dormant/abandoned assets + "digital salvage" governance | ≅ | **GHOST-CLOSURE / abandoned-state problem:** state no legitimate authority maintains but that still carries weight; salvage = *governed meta-transition* with an authority root, never self-promotion | derived | 5,36 |
| defense-in-depth intermediate mitigations before full PQC swap | ≅ | **V0.1 ships before the theorem:** bounded write-confinement (remove key-reuse / minimize exposure) earns value without the general NI proof | explicit→derived | 4,11 |
| "attacks always get better" | ≅ | adversarial monotonicity → falsifier pool must grow (loop-until-dry); a frozen suite Goodharts | explicit | 9 |

---

## §4 · LAWS CARRIED OVER (candidate, authority=false)

```
CanProve(capability)            ⇏ MustDisclose(mechanism)          # ZK ⇒ NIM V0.3 RELEASE
UnwitnessedClaim                ⇒ possible attack, not neutrality  # NO HASH = NO VOICE
Witness(proximity)             ⇏ Effect                            # estimate ≠ weapon
Attack(setup-parameters)        > Attack(single-transition)        # on-setup ⇒ meta-capture is the deeper class
SameCapability ∧ DifferentSeat  ⇒ DifferentLiveThreatClass         # fast/slow clock
LateWitness(post-admission)     = not-a-gate                       # receipts precede effect
AbandonedState                  ⇒ needs governed salvage, not self-promotion
```

The sharpest single import: **the ZK-proof-of-resource-cost is the cleanest
real-world instance of NIM V0.3 LICENSED RELEASE HELEN has yet seen** — a witness
`ω` that promotes a claim (`ECDLP-break is near`) to WITNESSED **while the
transform `f`=ZK provably blocks the forbidden flow** (mechanism → adversary).
`Λ_F(circuit → adversary) = 0`, yet `Λ_R(f(circuit)=estimate → public) = 1`.

---

## §5 · Λ_F / Λ_P INSTANTIATION (folds into the promotion-and-flow corpus)

| Source | → Target | Λ | class |
|---|---|---|---|
| attack circuit | adversary | **0** | forbidden flow |
| ZK-transformed estimate | public confidence | **1** | licensed release |
| unsubstantiated estimate | public confidence | **0** | forbidden (FUD) — no witness |
| 32-bit demo (WITNESSED) | "256-bit imminent" (INFERRED) | **1** | licensed promotion (threshold model) |
| resource estimate | "the system is broken now" | **0** | forbidden promotion (proximity ≠ breach) |
| lost-key dormant asset | "ownerless → free to seize" | **0** | forbidden; salvage needs authority root |

---

## §6 · FALSIFICATION — the analogy risk, named and guarded

**The live failure mode of THIS chiddush is superficial analogy** — pattern-matching
crypto vocabulary onto HELEN doctrine without structural load-bearing. Guards:

- **Where the map is FORCED (survives):** the ZK-proof ↔ LICENSED-RELEASE edge is
  structural, not lexical — both are literally "reveal `f(x)`, provably not `x`,
  under a witness." The `on-setup` ↔ meta-capture edge is structural: both attack
  the *governing parameters* once for a reusable exploit. These carry.
- **Where the map is WEAK (flag, don't ship):** "fast/slow clock ↔ seat topology"
  is *suggestive* — the crypto version is about wall-clock latency, HELEN's is about
  memory/co-residence; same shape, different physics. `inferred`, not `derived`.
- **Where it must NOT go:** none of the quantum-resource numbers enter HELEN as
  fact (REPORTED, and I read only 12/57 pages). The dormant-asset / "digital
  salvage" thread touches real legal/financial policy — it is a *structural
  inspiration* for ghost-closure governance, **not** a HELEN position on
  cryptocurrency.
- **Proposer≠validator caveat:** unlike the Garima extraction (3-lens fan-out),
  this was a single-context read. Treat every edge above as PROPOSER-ONLY until an
  independent lens validates. Seed S3 below.

---

## §7 · SEEDS (each NEEDS_OPERATOR verb — none self-promotes)

| # | Seed | Type | Route |
|---|---|---|---|
| S1 | ZK-proof-of-capability as the canonical NIM V0.3 LICENSED-RELEASE worked example | doctrine proposal | operator verb → fold into NIM V0.3 spec |
| S2 | `on-setup / trusted-setup capture` as a named member of the META_SEMANTICS_CAPTURE family | doctrine proposal | operator verb |
| S3 | Validate this extraction with a heterogeneous lens fan-out (crypto / governance / anachronism) — proposer≠validator | validation | operator verb → `chiddush arxiv --fanout` |
| S4 | "Late witness = not a gate" + threshold-model discreteness → HELEN monitoring doctrine (receipts precede effect; no smooth safety metric) | doctrine proposal | operator verb |
| S5 | Read pp.13–57 (esp. §VIII dormant assets, ZK appendix) to upgrade WITNESSED-PARTIAL → WITNESSED | intake | operator verb → `chiddush arxiv --full` |

**Firewall respected:** nothing written to kernel / governance / schemas / ledger /
GOVERNANCE. Schema-shaped seeds (a `release_witness` receipt field) are
SOVEREIGN-ADJACENT — proposed only, route to MAYOR, never through this skill.

---

## §8 · COMPRESSION

> **The paper's whole method is HELEN's central law in another domain:**
> *prove the claim, withhold the mechanism, and never let an unwitnessed estimate
> promote itself into either a fact or an effect.*
>
> `Evidence may originate with the claimant; promotion authority — and mechanism
> release — may not.`

The single best gift to HELEN: **ZK-proof-of-resource-cost is a working, deployed
instance of LICENSED RELEASE** — the exact object NIM V0.3 was specifying in the
abstract. HELEN was designing the type; this paper shipped one.

*A reading, not a ruling. authority=false · canon=false · LEDGER_EFFECT=none.*
