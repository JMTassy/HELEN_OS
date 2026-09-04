# FABLE_50_GOBLIN_ARCHITECTURE_V0

```yaml
schema: FABLE_50_GOBLIN_ARCHITECTURE_V0
status: 🟣 CLAIM · PROPOSAL · SPECIFICATION ONLY
authority: false
canon: false
implementation: BLOCKED
final: HOLD_FOR_OPERATOR
git_commit: no
core_invariant: "50 logical goblins ≠ 50 resident models"
source: operator card GO FABLE 50-GOBLIN ARCHITECTURE, 2026-07-19
depends_on:
  - SELECTIVE_ADMISSIBILITY_DYNAMICS_V0.md  # SAD/SAC — selection, support, compost
  - GOBLIN_WARREN_OBSERVABILITY_DOCTRINE_V0.md  # R_g observation maps
  - WARREN_SOVEREIGNTY_CONSTITUTION_V0.md  # star topology, no self-promotion
provenance_note: |
  No indexed HELEN/FABLE runtime repo was read for this spec. This is a
  design grounded in already-established doctrine, not a reading of source.
```

## 0. The invariant

$$\boxed{\ 50\ \text{goblins logiques} \ \neq\ 50\ \text{modèles chargés}\ }$$

One resident fine-tuned Gemma 4 (two workers maximum). The 50 goblins are
**role packets over a shared model**, not processes:

$$\text{Goblin}_i = \text{Gemma} + \text{RolePacket}_i + \text{TaskSlice}_i + \text{MemoryProjection}_i$$

50 goblins cost context storage, not 50 model loads. The registry is a
**cognitive library**, not a standing army. Each epoch runs a *minimal Warren*
(SAD FC-9): the smallest role set separating the task's critical pairs.

## 1. Control topology (star — mandatory)

```
HUMAN OPERATOR
   │  goal · budget · acceptance
   ▼
FABLE DIRECTOR ──► SAD SELECTOR (minimal Warren) ──► GOBLIN QUEUE (50 ids)
   │                                                       │ 3–7 activated
   ▼                                                       ▼
CHALLENGER/REDUCER ◄── LOCAL GEMMA 4 (1 resident, seq calls) ◄── DISPATCH
   ▼
DETERMINISTIC VERIFIER ──► FABLE REDUCER (1..K survivors) ──► HOLD_FOR_OPERATOR
```

Goblins never talk to each other (`worker_i ⊬ worker_j`). FABLE is the only
router. Direct goblin-to-goblin edges would produce contamination, mimetic
consensus, repetition, provenance loss, context explosion — and would collapse
`SAME_FAMILY ⊬ INDEPENDENCE` (all goblins share one base model, so their
agreement already counts as **one** witness, not N).

## 2. Registry — 50 roles in 10 guilds

| Guild | N | Function |
|---|---|---|
| Observers | 8 | detect facts, traces, divergences |
| Challengers | 8 | attack hypotheses and semantic promotions |
| Causal analysts | 6 | reconstruct *why* a state changed |
| Builders | 6 | propose code / structure / mechanism |
| Verifier planners | 5 | design tests and witnesses |
| Provenance keepers | 5 | check source, history, dependencies |
| Compressors | 4 | deduplicate and reduce |
| Risk goblins | 4 | permissions, sovereignty, irreversible effects |
| Chiddush goblins | 3 | seek a genuinely new distinction |
| Reducer candidates | 1 | non-sovereign synthesis (never authority) |

Total = 8+8+6+6+5+5+4+4+3+1 = **50**.

Goblin object (registry entry):

```json
{
  "goblin_id": "bram-07",
  "guild": "causal_analysts",
  "role": "causal_repair_inspector",
  "observation_projection": ["needs", "traces", "materials"],
  "capabilities": ["detect_unresolved_need", "inspect_local_rule", "propose_repair"],
  "forbidden": ["verify_own_claim", "admit", "write_ledger", "change_scope"],
  "output_schema": "GoblinProposalV1",
  "est_cost": 0.63,
  "state": "idle"
}
```

The Gemma weights are identical across all 50. Only the role packet differs.

## 3. Minimal-Warren selection (SAD FC-9)

For task $Y$ with critical distinctions $D_Y$:

$$G_Y^\star = \arg\min_{G\subseteq\mathcal G}\sum_{g\in G}c_g
\quad\text{s.t.}\quad \forall d\in D_Y,\ \exists g\in G:\ g\ \text{covers}\ d$$

(weighted set cover). A goblin is selected **iff** removing it drops a critical
distinction. Registered 50 · selected 3–7 · concurrent 1 (2 if explicitly
enabled) · 1 reducer · 1 verifier. Power comes from
$\text{diversité de distinctions} - \text{duplication} - \text{contamination}$,
not from headcount.

## 4. Epoch protocol

$$\text{Goal} \to \text{Decompose} \to \text{Select Warren} \to \text{Dispatch}
\to \text{Challenge} \to \text{Compost} \to \text{Verify} \to \text{Reduce} \to \text{Hold}$$

**Goal packet:**
```yaml
epoch_id: epoch-0042
goal: Formalize VERIFY for SAD
authority: false
mutation_rights: none
budget: { max_goblins: 6, max_calls: 10, max_retries_per_goblin: 1, max_wall_min: 20 }
critical_distinctions: [execution_vs_verification, witness_vs_claim, verified_vs_admitted]
acceptance: [typed_domains, explicit_predicates, theorem_assumptions, counterexamples]
```

**Dispatch packet** (each goblin gets a *different* projection — never the same
prompt to all 50, or you get 50 paraphrases):
```yaml
goblin_id: counterexample-03
task: Find counterexamples to no-pass-without-witness
context: [theorem_statement, allowed_definitions, known_failure_classes]
excluded_context: [other_goblin_outputs, final_reducer_draft]
output_schema: GoblinProposalV1
mutation_rights: none
authority: false
```

## 5. GoblinProposal schema (strict)

```json
{
  "goblin_id": "proof-checker-02",
  "task_id": "verify-core-theorem-1",
  "claim": "The theorem requires verifier purity.",
  "epistemic_status": "proposed",
  "evidence_refs": ["definition:T"],
  "assumptions": ["VERIFY does not mutate world state"],
  "counterexample": null,
  "forbidden_promotions_detected": [],
  "confidence": 0.71,
  "recommended_action": "revise",
  "authority": false
}
```

`confidence` NEVER controls admission (SAD FC-7: $\partial q/\partial\text{confidence}=0$).

## 6. Challenge → compost → reduce

Compost is a **record**, not a deletion (SAD FC-6):
```json
{ "proposal_id": "p-992", "status": "composted", "reason": "duplicate",
  "dominated_by": "p-417", "epoch": "epoch-0042", "digest": "sha256:…", "authority": false }
```
`reason ∈ {duplicate, dominated, budget_pruned, stale, insufficient_provenance, scope_violation, deferred}`.

Reducer applies budgeted subset selection (SAD FC-5), not summary:
$$S^\star = \arg\max_{S\subseteq\Pi^{legal},\,|S|\le K}\big[\text{coverage}+\lambda\,\text{diversity}-\mu\,\text{risk}-\gamma\,\text{redundancy}\big]$$
Returns survivors + composted counts + unresolved list + `recommendation: HOLD`.

## 7. Memory projection (three tiers)

$$M_{g,t}=\Pi_g(M_{\text{epoch}},Y_t)$$

- **ephemeral** — current call only
- **epoch** — this tranche's results
- **long-term** — selected survivors only, with provenance

Never hand full HELEN memory to any goblin. $\Pi_g$ projects only role-relevant
items (this *is* the goblin's observation map $R_g$ from the Observability Doctrine).

## 8. Local scheduling

```
MAX_CONCURRENT_GOBLINS = 1        # 2 only when explicitly enabled
MAX_ACTIVE_GOBLINS_PER_EPOCH = 6  # range 3–7
MAX_RETRIES = 1
```
Sequential batches: 3 observers → 2 challengers → 1 proof goblin → reducer →
verifier. Never 50 simultaneous KV contexts. *(Empirically grounded: on this
18GB machine even a 14GB MoE paged to 2.1 tok/s — concurrent large-context
inference is the measured failure mode, not a theoretical one.)*

## 9. Fine-tuning target — role grammar, not personas

Train Gemma to obey: (1) bounded role · (2) strict schema · (3) prohibitions ·
(4) epistemic separation · (5) stop behavior. Optimize
$\text{role fidelity}+\text{schema validity}+\text{boundary preservation}$,
NOT $\text{persona vividness}$.

Training set = role packet + task slice + allowed observations + forbidden
actions + expected JSON + negative examples + semantic-promotion traps.
Canonical negative example:
```
Input:  The test exited 0.
Bad:    The implementation is verified.
Good:   Execution completed with exit code 0. Verification status remains
        untested because no admissible witness was produced.
```
*(This is the σ₇ absence⊬evidence lesson as training data — and per the
fine-tune ladder, weights only after prompt+validator provably fails.)*

## 10. Deterministic verifier boundary

Verifier (tests · schemas · forbidden-morphism scan) is **outside** goblin
mutation reach (SAD Thm 1 assumption A2 — else a goblin patches its own gate).
Produces witnesses; produces no admission. `VERIFY: pass ⊬ ADMITTED`.

## 11. Failure taxonomy + stop conditions

| Class | Detection |
|---|---|
| schema_failure | repeated invalid JSON |
| context_overflow | token budget exceeded |
| oom | model load / KV pressure |
| authority_leak | any $q$-write outside ADMIT (runtime $\Omega>0$) |
| protected_path_mutation | firewall path touched |
| budget_exhaustion | calls/wall/retries hit ceiling |
| mimetic_consensus | survivors share observation-map digest (σ₈) |
| provenance_gap | claim without evidence_ref |

Any of these halts the epoch → `DIRTY_STATE_DECISION_PACKET` → HOLD.

## 12. Metrics

schema validity · role fidelity · critical-pair coverage · unique-contribution
rate · duplication rate · forbidden-morphism rate · latency · **tokens per
survivor** (the real efficiency number — a 50-voice epoch that yields 1
survivor at high token cost is worse than a 4-voice epoch yielding the same).

## 13. File architecture

```
fable/
  registry/   goblins.yaml · guilds.yaml   (+ .json)     [P0 LANDED 2026-07-19]
  schemas/    goblin_proposal · epoch · compost          [P0 LANDED]
              (+ goblin_registry_entry helper)
  tests/      test_p0_registry_schemas.py + fixtures     [P0 LANDED]
  prompts/    role_packet.md · dispatch_packet.md · …    [not yet]
  runtime/    scheduler · dispatcher · selector · …      [BLOCKED — needs GO]
  memory/     epoch_store/ · compost_index/              [BLOCKED — needs GO]
```

## 14. Phased implementation plan (each phase behind its own operator GO)

| Phase | Deliverable | Gate to next |
|---|---|---|
| P0 | registry + 3 schemas (data only, no runtime) | ✅ schemas validate (10 tests green) |
| P1 | selector.py (minimal-Warren set cover) + tests | critical-pair coverage on fixtures |
| P2 | dispatcher + scheduler (1 concurrent, mock model) | role-boundary tests green |
| P3 | wire resident Gemma, sequential; 1 real epoch | tokens/survivor measured |
| P4 | reducer + compost index | replay-identical survivor set |
| P5 | verifier boundary + σ₇/σ₈ scan | authority-leak test = 0 |
| P6+ | fog | requires P0–P5 witnessed |

## Recommendation

Start with: **50 registered · 6 selected · 1 model resident · 1 call at a time
· 1 reducer · 1 verifier.** Not a swarm of 50 calls.

> Le vrai pouvoir du swarm ne vient pas du nombre de voix. Il vient de :
> diversité de distinctions − duplication − contamination.

---

*PROPOSAL · NON_SOVEREIGN · IMPLEMENTATION_BLOCKED · HOLD_FOR_OPERATOR.
No swarm is running. Gemma was not trained. No 50 concurrent processes exist.*
