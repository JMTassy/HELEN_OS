# Model Routing V1 — Per-Agent Model Assignment

**Status:** spec (binding on `helensh/agents/` + `helensh/egregor/mesh.py`)
**Adopted:** 2026-05-15
**Companion to:** `docs/architecture/separation_thesis.md`, `docs/spec/HELEN_KERNEL_AXIOMS.md`

---

## 1. Principle

```
bigger ≠ better for governance roles
bigger = better for generation roles
```

INTELLIGENCE-layer agents (proposers) want generation surface. AUTHORITY-layer
agents (reviewers, gates) want compliance surface. Different layers → different
models. Same hardware, different role-fits.

This is the operational consequence of the separation thesis:

> intelligence ≠ memory ≠ truth ≠ authority ≠ execution

A single model cannot serve all five layers optimally. Routing by role makes
that explicit.

---

## 2. Dispatch paths

HELEN has three distinct LLM dispatch paths today. Each has its own model
selection point.

```
PATH 1   helensh/egregor/mesh.py STREETS        →  /api/chat traffic
PATH 2   helensh/agents/her_coder.py            →  HER.propose()
PATH 3   helensh/agents/hal_reviewer.py         →  HAL.review()
```

CLAW (`helensh/agents/claw.py`) has no model — it is a deterministic tool
dispatcher. That is correct: EXECUTION layer should not be an LLM.

---

## 3. Per-agent assignment matrix

| Path                    | Layer        | Role               | Model                  | Why |
|-------------------------|--------------|--------------------|------------------------|-----|
| mesh CONVERSATION       | INTELLIGENCE | direct chat        | `qwen3.5:9b-ud-q4`     | conversational, fast, 32K ctx; current swap baseline |
| mesh REASONING          | INTELLIGENCE | depth, logic, math | `deepseek-r1:14b`      | R1-distill specialized for reasoning; 8.99 GB fits |
| HER (proposer)          | INTELLIGENCE | creative cognition | `qwen3.5:9b-ud-q4`     | generation diversity > strict compliance |
| HAL (reviewer)          | AUTHORITY    | strict gate        | `mistral:latest`       | small, fast, rule-following; **creative models second-guess strict rules** |
| CLAW (skills)           | EXECUTION    | tool dispatch      | n/a (deterministic)    | by design |

The non-obvious assignment is **HAL → mistral**. A larger more creative model
produces worse HAL outputs because it tries to reason its way around the rules
instead of just applying them. The reviewer should be small, fast, directive.
The proposer should be bigger and creative.

---

## 4. Observation cadence

Per-step reassignment, not parallel. Each reassignment is preceded by ~20
metrics rows of baseline observation on the previous configuration. The
`model` field on `truth_metrics.jsonl` (added 2026-05-15) makes per-step
attribution falsifiable.

```
Step 1   mesh CONVERSATION  qwen3:14b           → qwen3.5:9b-ud-q4    ✓ shipped 9a94c2f
Step 2   HAL review         (hal-reviewer→mistral fallback)
                            → mistral:latest    (explicit, this commit)
Step 3   mesh REASONING     qwen3.5:9b-ud-q4    → deepseek-r1:14b      (this commit)
Step 4   HER propose        (her-coder→mistral fallback)
                            → qwen3.5:9b-ud-q4  (this commit)
```

Steps 2-4 land together by operator override of the per-step cadence. The
discipline note: this consolidates what HER would have phased. Rollback path
is per-file (one constant edit per agent) and ~30 seconds total.

---

## 5. Why explicit assignments matter

Today HER and HAL both effectively run on `mistral:latest` — not by intent,
but because their `MODEL_PRIMARY` constants point to custom Modelfiles
(`her-coder`, `hal-reviewer`) that don't exist in the current Ollama
registry, so they silently fall back.

Silent fallback hides routing intent. After this spec:

- HER's `MODEL_PRIMARY` is `qwen3.5:9b-ud-q4` (intentional, big-creative)
- HAL's `MODEL_PRIMARY` is `mistral:latest` (intentional, small-strict)
- Fallback chains are explicit rollback paths, not silent defaults

---

## 6. Hardware constraint (RTX 5070, 12 GB VRAM)

Only one model is fully resident at a time. Cold-load penalty per swap is
~30 s (Qwen3.5-9B observed). The current dispatch pattern means a single
`/api/chat` call can chain: mesh → HER → HAL. If each uses a different
model and none is resident, the cold-load cost compounds.

**Mitigation:** Ollama keeps recently-used models in a soft cache. Under
steady-state traffic the working set stabilizes. Cold-start is a first-call
cost, not a per-call cost. If empirical observation shows thrash, the
mitigation is to consolidate HER + mesh CONVERSATION on the same model
(they already are in this V1).

---

## 7. Forbidden patterns

These violate the routing spec:

| Forbidden                                                  | Violates                  | Why bad                                            |
|------------------------------------------------------------|---------------------------|----------------------------------------------------|
| HAL routed to a generative reasoning model (e.g., deepseek-r1) | §1 (governance role)  | Reviewer tries to reason around the rules          |
| CLAW given an LLM                                          | §2 (EXECUTION layer)      | Tool dispatch ≠ cognition                          |
| HER and HAL routed to the same model                       | §1 (layer collapse)       | INTELLIGENCE ≡ AUTHORITY: separation thesis fail   |
| `MODEL_PRIMARY` pointing to a non-existent Modelfile       | §5 (silent fallback)      | Hides routing intent                               |

---

## 8. Falsification

Each agent's model assignment is testable by reading `MODEL_PRIMARY` /
`STREETS` from the source. Routing claims that don't match the source are
the violation. PR review checks both files against this spec.

---

## 9. What this document is not

- Not a benchmark. Doesn't claim qwen3.5 > qwen3 or mistral > gemma in
  absolute terms. Only role-fit claims.
- Not a permanent assignment. Each row is rebindable as observation
  produces evidence.
- Not a model recommendation for the wider community. Specific to HELEN's
  hardware + layer architecture.

## 10. What this document is

- The canonical per-agent model map.
- Binding on `helensh/agents/` and `helensh/egregor/mesh.py`.
- A pre-registered prediction the metrics will test:
  *each agent should produce its expected behavior shape under its
  assigned model.* When the data disagrees, the matrix updates, not the
  data.

---

**Reference points:**
- `docs/architecture/separation_thesis.md` — layer invariant
- `docs/spec/HELEN_KERNEL_AXIOMS.md` — formal kernel equations
- `helensh/egregor/mesh.py` — STREETS routing
- `helensh/agents/her_coder.py`, `helensh/agents/hal_reviewer.py` — per-agent constants
- `helensh/.state/truth_metrics.jsonl` — per-call `model` tag (observation surface)
