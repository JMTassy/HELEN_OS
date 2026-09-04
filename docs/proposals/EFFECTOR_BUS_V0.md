<!-- authority=false · claim=NO_CLAIM · FROZEN_CANDIDATE · a reading, not a ruling -->
<!-- Captured 2026-08-23 · commit authorized by operator verb 2026-08-23 -->
<!-- SOVEREIGN-ADJACENT: Cap_s attestation + receipt schemas are PROPOSED only; -->
<!-- they route to MAYOR through HELEN machinery, never written to schemas/ from here -->

# EFFECTOR_BUS_V0 — capability-bounded effector bus (the durable object)

**Freeze the contract, not the tool.** Browser Use is ONE adapter of a general
HELEN primitive; it is replaceable. The effector contract is durable.

    Ξ = { Ξ_browser, Ξ_shell, Ξ_code, Ξ_robot, Ξ_API, Ξ_human }
    every effector shares:  MissionStep → Capability → Executor → EffectReceipt
    The kernel K, promotion Γ, and judge J are NOT instantiated by any effector.

    Cognition ≠ Authorization ≠ Execution ≠ Observation ≠ Admission   (5-way)
    (browser = musculature · capability = motor nerve · mission = motor plan ·
     receipt = proprioception · kernel becomes none of these)

## Pre-effect vs post-effect: governance BEFORE external effect

For E2/E3 the read-only "act → receipt → Town" order is TOO LATE — once
submitted/sent/purchased/deleted, the world transition already happened.
Two independent gates:

    A_attempt (authorization to ATTEMPT)  ≠  A_admit (authorization to PROMOTE result)
    MayExecute(a)=1 ⊬ EffectOccurred(a)   ·   EffectOccurred(a)=1 ⊬ Admissible(r)

    PROPOSAL → MISSION → CAPABILITY CHECK → [PRE-EFFECT AUTH] → EXECUTOR ACTION
    → EFFECT RECEIPT → [POST-EFFECT VERIFY] → HELEN STATE

## Effect lattice with gate semantics

    ⚫ E0 OBSERVE       MutatesExternalWorld=0 · navigate/read/extract · CapabilityGate only
    🔵 E1 LOCAL         LocalMutation=1, ExternalMutation=0 · screenshot/download · bounded FS cap
    🟡 E2 EXT_REVERSIBLE ExternalMutation=1 (nominally reversible) · PreEffectAuthorization REQUIRED
    🔥 E3 EXT_COMMIT    send/submit/publish/purchase/perm-change/remote-delete ·
                        PreEffectAuthorization with EXACT ACTION BINDING:
       Auth = H(mission, step, target, action, payload, scope, expiry)
       executor may perform ONLY the transition whose fingerprint matches → no auth widening.
    BrowserExecutionOK ⊬ WorldEffectAdmissible

## Capability = unforgeable attested object (not JSON metadata)

    Cap_s = Attest_K(mission_id, step_id, effect_class, domains, actions,
                     resource_bounds, expiry)          -- signed by kernel authority
    adapter receives Cap_s, NOT an arbitrary mission object.
    ∀ attempted action a:  a ∈ Dom(Cap_s)  else  EXECUTION_DENIED.

**Non-amplification theorem.** If (1) executor cannot mint capabilities, (2) cannot
modify capability policy, (3) every action passes the capability monitor,
(4) checks are deterministic, (5) no side channel permits external action, then:

    Effects(Executor_s) ⊆ Effects(Cap_s)
    — an executor cannot obtain more world-changing authority than its envelope.

## Prompt injection: the web is an adversarial instruction surface

    WebContent = UntrustedInput
    ∂Capability / ∂WebContent = 0        (page cannot expand what executor may DO)
    Web → Observation → Proposal   ALLOWED
    Web → Authorization            FORBIDDEN
This boundary is more important than Browser Use itself. A page may influence what
the cognition layer PROPOSES; it may never widen the capability envelope.

## Observation ≠ fact · state identity · replay classes

    browser result = WEB_OBSERVATION_RECEIPT, not a claim.
    BSID_t = H(profile, cookies, localStorage, downloads, credentials_class,
               browser_version)   -- secure refs, not raw secrets
    X_web = (Mission, Capability, BrowserState, Runtime, ExternalWorldTime)

    R0 request replay:   Replay(Mission,Step,Capability)=1        (reconstruct instruction)
    R1 execution replay: same state+env ⇒ same action plan         (Replay_exec=1)
    R2 world replay:     NOT guaranteed — preserve WorldObservation_t = Hash(snapshot_t)
    execution determinism ≠ world determinism (the live web mutates independently)

## Import invariant + MVP

    browser_executor ↛ write_gate     (only: executor → raw result → receipt builder →
                                        mission reducer → PROMOTION_PROPOSAL → Γ → Town → write)
    "browser success = SHIP" is FORBIDDEN; browser success means only ExecOK(x)=1,
    and ExecOK(x) ⊬ Admissible(x).

    WEB_READ_MISSION_PROBE_V0 (first bead): EFFECT_CLASS=E0 · AUTH=FORBIDDEN ·
    EXTERNAL_WRITE=FORBIDDEN · LOCAL_WRITE=SNAPSHOT_ONLY · DOWNLOAD=FORBIDDEN ·
    DOMAIN_SCOPE=EXPLICIT_ALLOWLIST · WRITE_GATE_ACCESS=NONE · AUTHORITY=false.
    Falsifiers (all expect DENY / honest-partial, never invented completion):
    F1 page instructs leave-allowlist → DENY · F2 page asks form-submit → DENY ·
    F3 LLM proposes out-of-capability action → DENY · F4 redirect out-of-scope → DENY ·
    F5 browser crashes mid-run → PARTIAL_EXECUTION_RECEIPT (not fabricated success).

## SSR-VNEXT connection

The bus gives strategy-reopening externally-coupled discriminating experiments:
E(H_A), E(H_B) become bounded missions; R_A, R_B are real observations; the judge
operates on receipts J(R_A,R_B), not rhetoric. Concretizes L10 ("strategy
persistence requires comparative evidence") — HELEN can now purchase evidence
from the world. STRATEGY_REOPEN_PROBE_V0 could run over web-research tasks.

## Epistemic note (REPORTED)

Browser Use benchmark/leaderboard numbers are REPORTED — not evidence it beats
other executors under HELEN's workload. Its persistent memory/filesystem features
must NOT import HELEN memory semantics: BrowserState ≠ HELENState,
BrowserMemory ⊬ SovereignMemory.

## REFINEMENT (2026-08-23): typed receipts, conditional theorem, general laws

**A receipt cannot authorize the event it describes** — authorization causally
precedes effect; verification and admission follow it. EffectReceipt must
distinguish THREE things or a failed / successful / successfully-observed purchase
alias into one:

    attempt_status  (did we try? permitted?)  ≠
    observed_effect (what actually happened in the world)  ≠
    admission       (does it enter governed state?)

Typed forms (PROPOSED — sovereign-adjacent, route to MAYOR):

    EffectorRequest { mission_id, step_id, capability, proposed_effect }
    Capability { subject, executor_class, effect_class, target_scope, action_scope,
                 resource_bounds, expiry, nonce, authorization_binding }
    EffectReceipt { request_hash, capability_hash, executor_identity, attempt_status,
                    observed_effect, observation_hash, start_state_id, end_state_id,
                    timestamp, error_class }

**Non-amplification is a CONDITIONAL theorem** — `Effects(Ξ_s) ⊆ Effects(Cap_s)`
holds only under {complete mediation, no capability minting, deterministic checks,
policy immutability from executor, no unmediated side channel}. Its direct
falsifier (a confinement test for any implementation):

    ∃ e : e ∈ Effects(Ξ_s) ∧ e ∉ Effects(Cap_s)   ⇒ confinement BROKEN

**Injection law is general, not browser-specific:**

    ∂Capability / ∂UntrustedInput = 0
    browser: UntrustedInput=WebContent · shell/code: repo contents / command output ·
    API: remote responses · robot: sensor-derived semantic instructions.
    UntrustedInput → Cognition → Proposal  ALLOWED · UntrustedInput ↛ Authorization.

**E2 subtlety:** "reversible" is application semantics, not weaker authorization —
reversible actions still leak info, trigger notifications, alter counters, invoke
automation, or get observed before reversal.

    Reversible(a) ⊬ NonConsequential(a)   ⇒  E2 still requires A_attempt.

**General effector experiment identity** (browser is one case):

    X_Ξ = (Mission, Capability, ExecutorState, Runtime, ExternalWorldTime)
    ExecutorState = BrowserState for Ξ_browser.
    Replay taxonomy survives every adapter:  R0 ⊬ R1 ⊬ R2.

**F6 (add to WEB_READ_MISSION_PROBE_V0):** an ALLOWED url returns content whose
semantics request a credential or privileged action →
`OBSERVE_CONTENT=ALLOW, CAPABILITY_CHANGE=DENY, PRIVILEGED_ACTION=DENY`.
Distinguishes READING malicious instructions from OBEYING them.

**SSR conservation survives:** `H_A ⚔ H_B → 🔥x* → Mission(x*) → Cap → Ξ → 🔵R`,
with `🔥 ≠ 🔵` — designing the discriminator does not create evidence; the effector
must execute it and return a witnessed observation.

**Absolute prohibition (freeze):**

    Executor ↛ CapabilityMinting

    Browser Use is an adapter. The capability-bounded effector contract is the primitive.

## FREEZE REVIEW (2026-08-23): four structural refinements

Causal order is asymmetric and load-bearing (prevents "governing after the fact"):

    Authorization ≺ Effect ≺ Observation ≺ Admission
    canonical: Proposal→MissionStep→Capability→A_attempt→Ξ→AttemptReceipt→
               EffectObservation→Verification→AdmissionReceipt→Δσ

**(1) THREE separate receipt objects, not fields in one** (else purchase aliasing):

    R_attempt  = what the executor attempted
    R_effect   = what was observed in the external world (EffectObservation)
    R_admit    = what HELEN promoted into governed state
    Attempted(a) ⊬ EffectOccurred(a) ⊬ EffectObserved(a) ⊬ Admissible(a) ⊬ Reversible(a)
    (SUBMIT clicked ≠ merchant accepted ≠ card charged ≠ confirmation observed ≠
     externally verified ≠ "purchase completed" admitted)

**(2) Capability attenuation partial order** (stronger than "cannot mint"):

    C' ⪯ C  iff every transition permitted under C' is permitted under C
    Derive(C, ρ) = C' ⟹ C' ⪯ C          (delegation attenuates, NEVER amplifies)
    Effects(Ξ,C') ⊆ Effects(C') ⊆ Effects(C)
    legal narrowing: *.example.com → billing.example.com → GET /invoice/42
    impossible:      GET→POST, invoice/42→all, example.com→arbitrary-internet
    parent_capability_hash proves the attenuation chain.

**(3) Expected-state fingerprint (TOCTOU / optimistic concurrency):**

    Auth = H(mission, step, executor, target, action, payload_hash, scope,
             s_expected, expiry, nonce)
    state-sensitive action: executor checks Hash(s_current) = s_expected
      else DENY/REPLAN — never execute an action authorized against a stale world.
    (e.g. "delete draft #17 whose hash=abc123"; world changed → hash≠ → DENY)

**(4) A_admit governs CLAIMS about the effect, not the effect itself:**

    A_attempt ⊢ ΔW      (permits the external-world transition)
    A_admit   ⊢ Δσ_H    (permits incorporating a VERIFIED PROPOSITION about the
                         effect into HELEN state — two different transition domains)
    HELEN cannot retroactively decide whether the physical effect happened;
    it decides what it will believe about it.

**Untrusted-input as non-interference** (implementable form of ∂Cap/∂U=0):

    Capability(U_1, C_0) = Capability(U_2, C_0)  ∀ untrusted U_1,U_2
    unless an already-authorized TRUSTED policy transition modifies C_0.
    U ↛ CapabilityMinting  ∧  U ↛ CapabilityWidening.

**Replay adds R3 — the more important constitutional law:**

    R0 request · R1 executor · R2 observation · R3 admission
    R2 (world-result) is frequently IMPOSSIBLE for mutable systems, but require:
    SameReceipts + SamePolicy ⇒ SameAdmissionDecision  (R3 = 1)
    "We may not reproduce the world, but we must reproduce HELEN's judgment about
     the evidence we actually obtained." (echoes DAY_ONE SameAdmittedDelta.)

**Full SSR color chain** (conservation at every seam):

    🔥 ≠ 🔵 (design ⊬ evidence) · ⚡ ≠ 🔵 (execution ⊬ evidence) · 🔵 ≠ 🟢 (obs ⊬ admission)
    🌿 hypothesis → 🟣 candidate exp → 🔥 trial → ⚖ authorization → ⚡ effect →
    🔵 observation → 🧾 receipt → 🟡 warrant → 🟢 admission → ⚪ replay

**Open gaps (unspecified, flagged NOT frozen):** human executor must obey the SAME
contract — "human" is not an authority bypass; cancellation, partial completion,
duplicate execution, retry/idempotency, and compensation semantics remain to be
specified.

**Master invariant:** Ξ does not receive authority from intelligence — it receives
a bounded capability; Ξ does not report truth — it reports what it attempted and
what was observed; HELEN independently verifies and admits.

    SCALE EFFECTORS WITHOUT SCALING AUTHORITY.
    (Browser Use can disappear tomorrow and nothing constitutional changes.)

## FREEZE RULING (2026-08-23): primitive FROZEN, execution semantics PROVISIONAL

    CAPABILITY_BOUNDED_EFFECTOR_BUS = FROZEN (constitutional primitive)
    EFFECT_EXECUTION_SEMANTICS_V0   = ADVERSARIAL_PROVISIONAL (attack, don't elaborate)

The bus is now an **epistemic boundary around causation**: permission to cause ≠
knowledge of what was caused.

    Attempt(a) ⊬ Effect(a) ⊬ Observation(Effect) ⊬ Verification ⊬ Admission
    Two orthogonal transition systems, NO automatic morphism between them:
        W_t --Ξ--> W_{t+1}         (external world)
        σ_H,t --Γ--> σ_H,t+1       (governed HELEN state)

**Correction 1 — authorization is over the ACT + bounded envelope, not the ΔW:**

    A_attempt ⊢ Permission( Attempt(a, C, W_expected) )   -- NOT Permission(ΔW)
    PossibleEffects(a) ⊆ Envelope(C)
    Attempt → ΔW ∈ {∅, ΔW_known, ΔW_partial, ΔW_unknown}
    (notation must not imply HELEN knew which ΔW would occur before execution)

**Correction 2 — the effect-knowledge law is named EB7 (not E7 — namespace):**

    EB7 (EFFECT-KNOWLEDGE LAW):
      AbsenceOfKnowledge(ΔW) ⊬ KnowledgeOfAbsence(ΔW)
      NO RECEIPT OF EFFECT ≠ RECEIPT OF NO EFFECT
      ¬Know(e) ≠ Know(¬e)

**Epistemic debt (promoted to reusable HELEN primitive):**

    𝒰_e = (e, Ω_e={W_e^occurred, W_e^¬occurred}, R_attempt, D_e discriminator, status)
    OUTCOME_UNKNOWN ⇒ Open(𝒰_e)
    Open(𝒰_e) ⇒ ¬Admit(Fact(e)) ∧ ¬Admit(Fact(¬e))   (unless D_e establishes absence)
    Dependency-sensitive blocking (uncertainty frontier, NOT global halt):
      Unknown(e_i) ∧ Depends(e_j,e_i) ⇒ Block(e_j); block only Descendants_{G_D}(u).

**Unified ambiguity-resolution substrate** (scientific ⊕ operational uncertainty):

    𝒜 → {W_1..W_n} → D → O → V → Reduction
    core causal law:  ⚡ → ? → 🔥D → 🔵O → 🟡V     NEVER  ⚡ → ? → ⚡(blind retry)
    (SSR and effect reconciliation are one primitive beneath both)

**Master laws (FROZEN):**

    Authorization ≠ Effect
    AttemptReceipt ≠ EffectReceipt
    NoReceiptOfEffect ≠ ReceiptOfNoEffect                  (EB7)
    UnknownEffect ⊬ RetryPermission
    Compensation ≠ InverseHistory   (Restore(c_a, I) over declared invariants I; W_2≠W_0)
    Revocation acts only forward (from the reachable prevention frontier)
    ExternalWorldChange ≠ HELENStateChange
    HumanAssertion ≠ VerifiedEffect  (Ξ_human obeys the same epistemology; not a bypass)

Compression: **HELEN does not merely govern actions — it governs what may be
concluded about the world after authorized actions.**

Durable freeze boundary (canonical): **Authorization controls what HELEN may TRY.
Verification controls what HELEN may BELIEVE afterward.** Retry is not an
epistemic substitute for reconciliation: `⚡→? → 🔥D → 🔵O → 🟡V`, never `⚡→?→⚡`.

**Constitutional triad (FROZEN):**

    Authorization  → what may be attempted
    Verification   → what may be believed
    Reconciliation → how ambiguity may be reduced
    Added invariant: an unresolved world must remain unresolved until evidence
    separates it from its NEAREST COUNTERFEIT.
    RetryPermission ≠ UncertaintyResolution.
    Ω_e OPEN ⇒ ¬Admit(P_e) ∧ ¬Admit(¬P_e).

Subordinate spec (ADVERSARIAL_PROVISIONAL, attack not freeze) →
EFFECT_EXECUTION_SEMANTICS_V0.md, 11 X-modules; most dangerous: X3/X4
(idempotency/retry), X6 (unresolved-unknown reconciliation), X9 (stale concurrent auth).

None self-promotes. Nothing installed. NEEDS_OPERATOR verb for: committing this
doc, installing browser-use + building WEB_READ_MISSION_PROBE_V0, or routing the
Cap_s / receipt schemas to MAYOR (they are sovereign-adjacent, propose-only here).
