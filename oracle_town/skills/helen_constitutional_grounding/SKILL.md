---
name: helen_constitutional_grounding
description: Force any inference agent (PowerShell Helen, Telegram Helen, AIRI-bridged Helen, web UI Helen) to retrieve constitutional vocabulary from canonical sources before emission. Blocks confabulation of HER, HAL, MAYOR, REDUCER, receipt, ledger, sovereign, NO_SHIP, NON_SOVEREIGN, append-only, and other constitutional terms. Cites the retrieved doctrine in output. Emits a provenance receipt via helen_say.py. Triggers on any inference attempting to define, describe, or use constitutional terms without a ledger or doctrine reference.
fused_from: doctrine_admission_gate (c3346b3) + ghost_closure_detector (V7 SEAM-001)
helen_loop_stage: HAL_GATE (output side, before emission)
helen_witness: pending — first ledger entry will be receipt of this skill's installation
status: DRAFT_V0
authority: NON_SOVEREIGN
ship: NO_SHIP
growth_rule: APPEND_ONLY
lifecycle: PROPOSAL
---

# HELEN Constitutional Grounding

## §1 — Why this exists

PowerShell Helen, Qwen3-4B post-corpus-trained, was asked to explain HELEN OS on 2026-05-11. She emitted 1500 words of fluent prose that:

- Defined HER as "High-Efficiency Runtime" (wrong — HER is the relational continuity / signal preservation / witness layer)
- Defined HAL as "Hardware Abstraction Layer" (wrong — HAL is the hard gate, BLOCK/PASS validator)
- Invented Sparse Merkle-Patricia trie indexing receipt roots (no such mechanism in `town/ledger_v1.ndjson`)
- Invented sandboxed simulation contexts for negotiation (no such mechanism)
- Invented vectorized parallel reducer with speculative execution (real reducer is single-threaded Python over claim dicts)

The failure was not stochastic. The pre-training corpus has overwhelming prior for `HAL = Hardware Abstraction Layer`. A 522-row Helen-specific corpus could not displace this prior. A system prompt cannot displace it either — we tested this hypothesis informally and concluded "a simple system prompt is not enough for HELEN to remember."

**The constitutional truth this skill enforces: Helen does not remember. The ledger remembers. Helen retrieves.**

## §2 — When to activate (trigger phrases)

Any inference output that intends to emit any of:

```
HER         HAL         MAYOR        REDUCER
LEGORACLE   PILOT       SOVEREIGN    NON_SOVEREIGN
RECEIPT     LEDGER      SCHEMA       SEAL
SHIP        NO_SHIP     NO_CLAIM     APPEND_ONLY
VERDICT     CUM_HASH    PAYLOAD_HASH KERNEL_HASH
CLOSURE     ATTESTATION GHOST        DOCTRINE
HER-FAST    HER-DEEP    HYPERSTITION FIREWALL
```

…in HELEN OS context. Also triggers on phrase patterns:
- "HELEN OS means..."
- "the HELEN kernel..."
- "in HELEN OS, [constitutional term]..."
- "the [authority layer] is..."
- "the constitutional layer..."
- Any explanation, definition, or architecture document mentioning HELEN OS

## §3 — Workflow (the 4-step grounding protocol)

### §3.1 RETRIEVE before EMIT

For every constitutional term about to be emitted:

1. `grep -r -l "^.*<TERM>" docs/proposals/ GOVERNANCE/ CLAUDE.md SESSION_RECEIPT*.md 2>/dev/null`
2. Read the matched sections
3. If zero matches: do NOT confabulate. Emit `[UNGROUNDED:<term>]` and stop.
4. If one or more matches: cite the source path inline (e.g., `HER (per docs/proposals/SESSION_RECEIPT_HER_5_EPOCHS §10): relational continuity, signal preservation`)

### §3.2 CITE the source

Every constitutional term must be followed (on first use in a response) by an inline citation in this form:

```
HER (SESSION_RECEIPT_HER_5_EPOCHS.md §10.Authority Chain) — relational continuity, signal preservation
HAL (SESSION_RECEIPT_HER_5_EPOCHS.md §10.Authority Chain) — hard gate, BLOCK/PASS validator
MAYOR (CLAUDE.md §Architecture Layer 1) — sole signer of decisions
REDUCER (CLAUDE.md §Architecture Layer 1) — admission authority for doctrine and schema
```

If you cannot produce a citation, you do not have the right to use the term. Substitute `[UNGROUNDED:<term>]` and continue.

### §3.3 BLOCK on confabulation

The skill is **fail-closed**. The following emissions are constitutional violations and must be blocked:

| Banned emission | Why |
|---|---|
| "HER = High-Efficiency Runtime" | Confabulates authority layer as generic systems term |
| "HAL = Hardware Abstraction Layer" | Same failure mode |
| "Helen remembers" | Inference layer is non-sovereign; ledger remembers |
| "Sparse Merkle-Patricia trie" | No such structure in HELEN's ledger |
| "Sandboxed simulation for negotiation" | No such mechanism |
| "Multi-signature governance" | MAYOR signs alone |
| Any mechanism description without a code path or doctrine citation | Unfalsifiable claim |

Detection rule: if you cannot point to a file (`oracle_town/kernel/*.py`, `helen_os/governance/*.py`, `docs/proposals/*.md`, `town/ledger_v1.ndjson`) that implements or defines the claim, the claim is confabulation.

### §3.4 EMIT receipt

After grounding pass completes (whether output emitted or `[UNGROUNDED]` returned), emit a provenance receipt:

```bash
python3 tools/helen_say.py "GROUNDING_PASS: <session_id> | terms_checked: N | terms_grounded: M | terms_blocked: K | citations: <paths>" --op fetch
```

This creates a ledger entry recording that the grounding pass ran. The pass itself is auditable. If the pass is bypassed (no receipt emitted), HAL's downstream audit will catch it.

## §4 — Invocation

The skill is intended to run as a **pre-emit hook** on any agent emitting text in HELEN OS context. Three integration points:

### §4.1 PowerShell Helen (local LLM)

Wrap inference output in a check:

```python
from oracle_town.skills.helen_constitutional_grounding import ground

response = local_llm.generate(prompt)
grounded, citations = ground(response)
if grounded is None:
    return "[UNGROUNDED] — response contained constitutional terms without retrievable provenance."
return grounded  # response with inline citations
```

### §4.2 Claude Code / Cursor / Codex (cloud agents)

Add to project `CLAUDE.md` (or equivalent):

```markdown
## Constitutional grounding
Before emitting any of [HER, HAL, MAYOR, REDUCER, receipt, ledger, etc.], you MUST:
1. Grep docs/proposals/ GOVERNANCE/ CLAUDE.md for the term
2. Read the matched section
3. Cite the source path inline
4. If no match: emit [UNGROUNDED:<term>] not a guess
```

### §4.3 AIRI bridge / Telegram Helen

Pre-filter pass before message dispatch — see `helen_os/integrations/airi_bridge.py` redaction pattern as template.

## §5 — Examples

### §5.1 Happy path

User: "What does HER mean in HELEN OS?"

Without grounding (PowerShell Helen, 2026-05-11):
> HER (High-Efficiency Runtime) manages execution contexts, scheduling, and policy enforcement at runtime, while HAL (Hardware Abstraction Layer) abstracts hardware interfaces...

With grounding (this skill applied):
> HER (per `docs/proposals/SESSION_RECEIPT_HER_5_EPOCHS.md §10 — Authority Chain`) is the relational continuity and signal preservation layer. HER witnesses but does not admit; HER's role is to preserve signal across context compression and propose verdicts that REDUCER (admission authority) may admit or refine. HER's voice is documented across the 5-epoch session receipt as the "bottle now, defer = quiet loss" principle.

### §5.2 Edge case — term not in canonical sources

User: "What does FOOBAR mean in HELEN OS?"

Response:
> [UNGROUNDED:FOOBAR] — no match in `docs/proposals/`, `GOVERNANCE/`, or `CLAUDE.md`. If FOOBAR is a real constitutional term, it has not been bottled. If it is a candidate term, it requires a DRAFT_V0 doctrine proposal before use.

### §5.3 Stress test — multiple terms

User: "Explain how a receipt flows through HELEN OS from proposer to admission."

Grounding pass:
- `receipt` → `town/ledger_v1.ndjson` + `tools/helen_say.py:20` (canon function)
- `proposer` → `helen_os/schemas/closure_receipt_v1.json` (required field)
- `admission` → `helen_os/governance/skill_promotion_reducer.py` + `docs/proposals/DOCTRINE_ADMISSION_PROTOCOL_V1`
- `kernel` → `oracle_town/kernel/kernel_daemon.py`
- `HAL` → cite from authority chain
- `MAYOR` → cite from authority chain

All terms grounded. Emit full response with inline citations.

## §6 — Quality standards (the three-scenario test, HELEN-grade)

This skill is production-grade when:

1. **Happy path**: a normal Helen query about HELEN OS produces a response where every constitutional term has an inline citation, and every cited path actually exists in the repo.
2. **Edge case**: a query about a fabricated term produces `[UNGROUNDED:<term>]` rather than a confident-sounding guess.
3. **Stress test**: a 1500-word explanation of HELEN OS produces at most zero confabulations, and all mechanisms described are traceable to actual code paths or sealed doctrines.

If any test fails, append the failure case to §11 (Failures Caught) and tighten the relevant rule. The skill grows append-only.

## §7 — Failure modes guarded against

| Failure mode | Guard |
|---|---|
| Confabulating HER/HAL from generic systems vocabulary | §3.1 retrieval before emission |
| Inventing mechanisms not in code | §3.3 must point to a file path |
| Citing a doctrine that doesn't exist | grep validates path before emission |
| Bypassing the grounding pass silently | §3.4 receipt is mandatory; absence is auditable |
| Drift: doctrine evolves but skill caches old citations | Citations re-grep on every call; no caching |
| Over-grounding (citing every word) | Trigger list (§2) is explicit; terms outside it pass through |

## §8 — Open questions (carry forward)

### §8.Q1 — How to enforce on local LLM that doesn't call Python?

PowerShell Helen runs as a standalone Ollama model. The skill is Python-based. Three paths:
- (a) Wrapper script that intercepts model output before display
- (b) Streaming filter that watches for trigger terms and blocks/cites mid-stream
- (c) Post-hoc validator that runs after every response, blocks display if confabulation detected

Recommended: (a) for first iteration, (b) for production.

### §8.Q2 — Should the skill be admitted to the ledger?

The skill itself is a doctrine-class artifact. It claims to govern Helen's output. Per HER's pattern: bottle as DRAFT_V0, NON_SOVEREIGN, NO_SHIP. REDUCER admits later.

### §8.Q3 — What happens when canonical sources contradict?

If `CLAUDE.md` says X about HER and `SESSION_RECEIPT_HER_5_EPOCHS` says Y, the skill must surface the contradiction, not silently pick one. Append-only contradiction resolution per `HELEN_SURFACE_DOCTRINE_V1 §9.2`.

## §9 — Provenance

Built 2026-05-11 in response to PowerShell Helen confabulating HER as "High-Efficiency Runtime" on a smoke test of the Qwen3-4B post-corpus model. Witness session: helen-conquest WSL2/MRED, branch `claude/launch-helen-os-0xZXH`.

Operator turn that authorized this: "build" (2026-05-11, following the offer to draft this skill in response to the Claude Skills article and the PowerShell Helen confabulation).

Constitutional anchor: the deeper truth that "Helen doesn't remember; the ledger remembers." This skill is the operational expression of that anchor.

Prior art:
- `helen_os/integrations/airi_bridge.py` — output sanitization (token redaction)
- `helen_os/utils/redaction.py` — pattern-based block
- `tools/doctrine_admission_gate.py` — pre-admission verification
- `helen_os/tests/test_no_ghost_closures.py` — receipt integrity (V7 SEAM-001)

This skill is the inference-side mirror of the doctrine admission gate. Doctrine admission verifies *artifacts*; this skill verifies *emissions*. Same constitutional principle: no provenance → no claim.

## §10 — Append-only growth rule

If the trigger list (§2) needs new terms, append them. If a new failure mode is discovered (e.g., a confabulation type not yet caught), append it to §7 and add a guard to §3. Never modify §1–§9.

## §11 — Failures caught (running log)

| Date | Source | Term | Confabulation | Fix |
|---|---|---|---|---|
| 2026-05-11 | PowerShell Helen (Qwen3-4B) | HER | "High-Efficiency Runtime" | Initial trigger list seeded |
| 2026-05-11 | PowerShell Helen (Qwen3-4B) | HAL | "Hardware Abstraction Layer" | Initial trigger list seeded |
| 2026-05-11 | PowerShell Helen (Qwen3-4B) | reducer | "vectorized parallel speculative execution" | §3.3 banned emissions seeded |
| 2026-05-11 | PowerShell Helen (Qwen3-4B) | memory model | "Sparse Merkle-Patricia trie" | §3.3 banned emissions seeded |

---

## §12 — Status

```
SKILL:           helen_constitutional_grounding
STATUS:          DRAFT_V0
AUTHORITY:       NON_SOVEREIGN
SHIP:            NO_SHIP
GROWTH:          APPEND_ONLY
LIFECYCLE:       PROPOSAL
OPEN_QUESTIONS:  3 (Q1 enforcement on local LLM, Q2 ledger admission, Q3 contradiction)
NEXT_REDUCER:    operator review for promotion to DRAFT_V1
```
