---
schema: HELEN_PROPOSAL_V1
title: GAS V0 — Proofs Companion (Theorem 4.1, Proposition 7.1)
authority: false
sovereign: false
canon: false
ledger_effect: none
claim_status: NO_CLAIM
final: HOLD_FOR_OPERATOR
git_stage: yes  # operator commit mark 2026-07-06
origin: FABLE proof tranche 2026-07-06, companion to docs/proposals/GAS_V0.md; all Layer II verdicts run live at commit dace8b02
---

# GAS V0 — Proofs Companion

🟣 CLAIM · NON_SOVEREIGN · PROPOSAL · NO_CLAIM · HOLD_FOR_OPERATOR

Companion to `docs/proposals/GAS_V0.md`. Contains: the proof of Theorem 4.1
(Layer I), hypothesis-necessity counterexamples, the mechanization bridge to
the existing Coq layer, and the conformance argument for Proposition 7.1 —
including a **live gate verdict that currently falsifies part of it**.

Witness protocol: every Layer II verdict below was produced by running the
cited gate/test at commit `dace8b02` on 2026-07-06 and is reported verbatim.
NO RECEIPT = NO CLAIM applies to proofs about implementations too.

---

## 1. Preliminaries, and one proof-driven repair

Notation as in GAS_V0 §2: GAS `(𝒲, 𝒞, Θ, V_Θ)`; certification `𝒯`; ledger
`L ∈ Σ*`; payload projection `π : Σ → 𝒲`; admissible ledger space
`𝒞_ledger`; ledger invariant `Inv_Θ` (Def. 2.7).

**Repair record (method note).** Drafting the induction step exposed a gap
in (H3) as previously stated: it constrained `β` only *on V_Θ-passing
evidence*, leaving `β`'s behavior on non-passing (adversarial) evidence
unspecified — exactly the case an adversarial-soundness theorem must cover.
(H3) in GAS_V0 has been strengthened to **fail-closed totality**:

> **(H3, repaired)** `β` is total on `𝒞_ledger × 𝒫(E) × Θ`. For every
> evidence set `Ê ∈ 𝒫(E)` (passing or not), `β(L, Ê, Θ) = L ⊕ s` where the
> suffix `s` contains only events `e` with `V_Θ(π(e)) = 1`; in particular
> `s` may be empty — **rejection is the identity append**, never an error
> state and never an unvetted append.

This is the projection/fail-closed behavior the implementation always had
(validators return `⊥`, the daemon's gates refuse); the hypothesis now says
it. A theorem attempt that repairs its own hypotheses before proof is the
discipline working, not a defect.

**Definition 1.1 (Run, reachability).** A *run* is a sequence
`L_0, L_1, L_2, …` with `L_0 = ε` (or a designated `L_0 ∈ 𝒞_ledger` with
`Inv_Θ(L_0)`), where each `L_{n+1}` is obtained from `L_n` by applying one
morphism of the model. A ledger is *reachable* if it occurs in some run.
An *adversarial dialogue stream* is any sequence of evidence sets
`Ê_1, Ê_2, … ∈ 𝒫(E)` — no constraint whatsoever on how they were produced
(this is how "Byzantine `D`" enters the mathematics: `α` is unconstrained,
so the `Ê_n` are universally quantified).

---

## 2. Proof of Theorem 4.1 (Adversarial-proposer soundness)

**Theorem (restated).** Let `(𝒲, 𝒞, Θ, V_Θ)` with ledger as in Defs.
2.6–2.7 satisfy (H1) verifier soundness & totality, (H2) evidence
separation, (H3) reducer fail-closed totality & preservation. Then for
every adversarial dialogue stream, every reachable ledger satisfies
`L_n ∈ 𝒞_ledger` and `Inv_Θ(L_n)`.

**Proof.** By induction on the run index `n`.

*Base.* `L_0 = ε ∈ 𝒞_ledger` vacuously (no events), and `Inv_Θ(ε)` holds by
convention (empty chain is well-formed). For a designated non-empty `L_0`,
both properties hold by assumption.

*Step.* Assume `L_n ∈ 𝒞_ledger` and `Inv_Θ(L_n)`. Consider any transition
`L_n ⟶ L_{n+1}`.

1. **Only `β` moves the ledger.** By (H2), the model contains no morphism
   `D → L` and no constructor of `L` other than `β`-append (Def. 2.6 makes
   append the *only* constructor; Axiom 2.5 excludes any bypass). Hence
   `L_{n+1} = β(L_n, Ê_{n+1}, Θ)` for some evidence set `Ê_{n+1} ∈ 𝒫(E)`.

2. **The evidence is arbitrary — and it does not matter.** The adversary
   controls `Ê_{n+1}` completely. By (H3, repaired), `β` is total on all of
   `𝒫(E)` and `L_{n+1} = L_n ⊕ s` where every event `e ∈ s` satisfies
   `V_Θ(π(e)) = 1`. The case `s = ε` (all evidence rejected) gives
   `L_{n+1} = L_n`, for which both properties hold by the induction
   hypothesis. So assume `s` non-empty.

3. **Membership.** For each `e ∈ s`: `V_Θ(π(e)) = 1`, so by (H1,
   soundness) `π(e) ∈ 𝒞`. Every event of `L_{n+1}` is an event of `L_n`
   (in `𝒞` by the induction hypothesis and Def. 2.7) or an event of `s`
   (just shown). Hence `L_{n+1} ∈ 𝒞_ledger`.

4. **Invariant.** By (H1, preservation), appending events with
   `V_Θ(π(e)) = 1` to a ledger satisfying `Inv_Θ` yields a ledger
   satisfying `Inv_Θ`; applying this once per event of `s` (finite) gives
   `Inv_Θ(L_{n+1})`.

By induction, every reachable ledger satisfies both properties. Nothing in
steps 1–4 constrained the provenance, distribution, or intent of the
`Ê_n`; adversariality is absorbed by the universal quantification. ∎

**Remark 2.1 (What the theorem does and does not say).** It says the
governed layer is invariant against arbitrary generation *given* (H1)–(H3).
It does not say `V_Θ` is *correct* about the world (garbage rules give
garbage-but-governed ledgers: soundness is relative to `Θ`), and it does
not say the implementation satisfies (H2) — that is precisely
Proposition 7.1, and §5 shows why the separation matters *today*.

---

## 3. Necessity of the hypotheses (counterexamples)

Each hypothesis is used in the proof and none is redundant:

- **Drop (H1) soundness.** Take `V_Θ ≡ 1` (vacuous verifier). Every append
  passes; an adversary submits evidence for any `x ∉ 𝒞`; step 3 fails.
  *Moral:* the theorem is only as strong as the verifier — a gate that
  cannot say no protects nothing.
- **Drop (H2).** Add a single morphism `d : D → L` (one unguarded append
  path). The adversary ignores `β` entirely and appends an arbitrary event
  through `d`; step 1 fails. *Moral:* one bypass arrow defeats every gate
  on the guarded path — which is why Proposition 7.1(b) below being RED is
  treated as blocking, not cosmetic.
- **Drop (H3) fail-closed totality.** Let `β` be defined only on passing
  evidence. The adversary submits garbage `Ê`; `β(L, Ê, Θ)` is unspecified
  — the run gets stuck or, worse, an implementation "helpfully" appends
  unvetted content to make progress. Step 2 fails. *Moral:* rejection must
  be a defined, lawful outcome (the identity append), not an error state.

---

## 4. Mechanization bridge (existing Coq layer)

The repository already carries a machine-checked kernel model:
`formal/Ledger.v` (specification), `formal/LedgerProofs.v` (integration
theorems), `formal/LedgerKernel.v` — **0 `Admitted.`** at `dace8b02`.
Mapping (informal — the Coq model is not yet the GAS quadruple):

| GAS proof component | Coq artifact |
|---|---|
| Step 4 invariant preservation | `Ledger.v: inv_authority_constraint_preserved`, `system_preserves_invariants` |
| Composite safety of reachable states | `LedgerProofs.v: safety_composite` |
| Append-only constructor discipline (Def. 2.6) | `LedgerProofs.v: append_only_inductive` |
| Chain-integrity detection (Thm 4.4 side) | `LedgerProofs.v: bind_to_prev_detects_byzantine` |
| Chain well-formedness lemmas (Thm 4.2 side) | `LedgerKernel.v: seq_strict_inc_*`, `hash_chain_valid_*` |

**Mechanization goal:** formalize the GAS quadruple and (H1)–(H3) in Coq
atop `Ledger.v` and derive Theorem 4.1 from `safety_composite`. Until then,
§2 is a rigorous paper proof with mechanized *components*, not a mechanized
theorem — the distinction is stated, per layer discipline.

---

## 5. Proposition 7.1 — conformance argument and a live falsification

**Statement decomposition.** Proposition 7.1 splits:

- **7.1(a) — Architectural conformance.** No dialogue surface holds a
  ledger-write capability: every admitted write factors through the
  `NDJSONWriter` boundary (the `β`-realization), reached only via the
  admissible bridge and kernel handlers.
- **7.1(b) — Self-certification.** The implementation's *designated gate*
  (`tools/kernel_guard.sh`, wired into CI as `kernel_guard.yml`) certifies
  7.1(a) at the current commit.

**Trust boundary (stated once, honestly).** The model's morphisms are code
paths. An actor with raw filesystem access (the OS, the operator, any
process outside the repo's discipline) is outside the model; no code gate
can exclude out-of-band writes. Prop 7.1 is a claim about the *admitted
morphism surface of the SOT at a commit*, nothing more.

**Correction to GAS_V0 §7 as originally drafted.** The idealized claim
"sole path `helen_say.py → ndjson_writer.py`" is not what the gate
enforces. The gate's single source of truth is a **five-writer allowlist**:
`tools/ndjson_writer.py`, `kernel/kernel_cli.ml`, `tools/end_session.py`,
`tools/helen_add_lesson.py`, `tools/accept_payload_meta.sh` — all
kernel-boundary writers (β-family), none a dialogue surface. The paper must
state the real allowlist; a proof about an idealization is a proof about
nothing.

### Witness table (run live at `dace8b02`, 2026-07-06, verdicts verbatim)

| Witness | Checks | Verdict |
|---|---|---|
| `kernel_guard.sh` RULE 1 | direct `open(…, "a"/"w")` on ledger paths outside allowlist | **PASS** (0 violations) |
| `kernel_guard.sh` RULE 3 | shell `echo/printf >>` raw ledger writes | **PASS** (0 violations) |
| `kernel_guard.sh` RULE 2 | `NDJSONWriter` imports outside consumer allowlist | **FAIL — 3 violations** (below) |
| `test_do_next_boundary_v1.py` + `test_ndjson_writer_atomic.py` + `test_duplicate_seq_detector.py` | executor seam closed; append linearization; fork detection | **22 passed** |
| root constitutional suite `tests/test_1_*…test_9_*` | mayor-only decisions, IO allowlist, etc. | **36 passed** |
| CI `kernel_guard.yml` on `main` | same gate, GitHub runner | **failure × 3 most recent runs** (2026-07-05T20:23Z, 22:38Z, 23:24Z) |

### The three RULE 2 violations, classified

1. `helen_os/tests/test_duplicate_seq_detector.py` — test imports the
   writer to exercise it against `tmp_path` scratch ledgers. Same class as
   `tools/test_kernel_properties.py`, which *is* allowlisted. Allowlist
   staleness, not a breach.
2. `helen_os/tests/test_ndjson_writer_atomic.py` — identical class
   (these are Theorem 4.2's own witnesses).
3. `oracle_town/kernel/kernel_daemon.py` — the kernel daemon: the
   2026-06-15 admission pipeline (`_handle_promote_skill`,
   `_handle_seq_correction`) writes MAYOR-ratified entries via
   `NDJSONWriter`. Architecturally this is the β-boundary itself acting as
   a lawful writer — **not** a `D → L` arrow (dialogue reaches the daemon
   only through the socket + 6 fail-closed gates). The guard's consumer
   allowlist predates the daemon's writer role and was never updated.

### Verdict

- **7.1(a): SUPPORTED.** RULE 1 + RULE 3 pass repo-wide; the boundary and
  constitutional suites pass; the three flagged imports are β-side
  components and test scaffolding, none a dialogue-surface write path. No
  `D → L` arrow was found.
- **7.1(b): FALSE at `dace8b02`.** The designated gate returns FAIL, and
  its CI job has been red on `main` across the recent push history while
  pushes continued to land. By this program's own fail-closed discipline,
  **Proposition 7.1 is NOT PROVED while its own verifier is red** —
  supported-by-inspection is not certified-by-gate, and substituting the
  former for the latter is exactly the laundering the layer discipline
  forbids.

**Status: OPEN — blocked on an operator/MAYOR ruling**, with a precise
remediation packet:

> **Remediation packet (operator decision required; not executed by the
> drafting agent — the guard is a gate, and agents do not edit gates to
> make their own proofs pass):**
> 1. Add `helen_os/tests/test_ndjson_writer_atomic.py` and
>    `helen_os/tests/test_duplicate_seq_detector.py` to
>    `CONSUMER_ALLOWLIST` in `tools/kernel_guard.sh` (test-scope writer
>    consumers, same class as the two already-allowlisted test files).
> 2. Rule on `oracle_town/kernel/kernel_daemon.py`: if the daemon's
>    admission handlers are lawful writers (the 2026-06-15 pipeline says
>    yes), add it to `CONSUMER_ALLOWLIST`; if not, the pipeline itself
>    needs re-routing. Either way the current silence is drift.
> 3. Consider making the red gate *blocking* (branch protection on
>    `kernel_guard.yml`) — a gate that fails without stopping anything is
>    a lantern nobody watches.
> After the ruling: re-run `bash tools/kernel_guard.sh`; on PASS,
> Proposition 7.1(b) flips TRUE at that commit and 7.1 closes.

---

## 6. Method note (what this tranche demonstrated)

Writing the conformance proof did what proofs are for: it **falsified a
witness everyone believed**. The kernel-guard gate has been red since the
admission pipeline landed (allowlist last touched at `1bff42b`, pipeline at
`ccf73ae`), the CI job faithfully failed on every push, and the failure
blocked nothing and alerted no one. The architecture held (7.1(a)); the
*certification* of the architecture silently rotted (7.1(b)). That gap —
between being sound and being *verifiably* sound — is the entire subject
of this paper, exhibited in its own repository on the day its main theorem
was proved.

`Inv holds ⊬ Inv certified · gate red = claim frozen · 📜 ledger sleeps`
