# HELEN_FULL_RECAP_V1

**Status:** Frozen
**Date:** 2026-03-18
**Purpose:** Canonical state description of HELEN as a governed cognitive system

---

## Core Compression

```
exploration → typed packet → validation → reducer decision → ledger → replay → continuity
```

**The central law, intact:**

> HELEN's skills structure cognition. Only the reducer structures reality.

---

## 1. What HELEN Is Now

HELEN is no longer a diffuse idea or a prompted assistant.

HELEN is a **local-first, governed, persistent cognitive system** with strict separation between:

| Layer | Role |
|-------|------|
| Non-sovereign cognition | Skills, Temple, Oracle — judgment without authority |
| Sovereign decision | Reducer — only layer that governs state |
| Institutional memory | Ledger — append-only, hash-chained |
| Replay | Deterministic reconstruction of state |
| Companion presence | AIRI renders; HELEN owns memory |

**Three authorities, permanently distinct:**

- **Reducer** = sole authority over institutional decisions
- **Ledger** = sole authority over institutional memory
- **Replay** = sole authority over state reconstruction

What this means:
- No skill governs
- No UI governs
- AIRI does not govern
- No LLM provider governs
- No conversational output has authority by itself

```
Provider output ≠ skill output ≠ UI output ≠ sovereign decision
```

---

## 2. The Legal Transition Layer

The system stopped being "just an architecture" when the packet flow was closed:

```
Skill / Temple / Oracle
    ↓
Packet (only legal object that crosses layers)
    ↓
Mayor (readiness gate, never final authority)
    ↓
Reducer (pure, deterministic, fail-closed)
    ↓
Ledger append (append-only, hash-chained)
    ↓
Replay (deterministic reconstruction)
```

**Reducer wedge rules (frozen):**
- Binary admission outcomes: `ADMITTED` / `REJECTED`
- No I/O inside the reducer
- No direct state mutation
- No hidden "intelligent" logic
- Clean separation between decision and persistence

---

## 3. Memory / Continuity Layer

The real displacement of the project happened here.

HELEN no longer aims at pseudo-conversational memory.
She aims at **memory-backed continuity**.

**Central memory objects:**

| Object | Purpose |
|--------|---------|
| `PERSON_PROFILE_V1` | Identity continuity |
| `SESSION_LOG_V1` | Session record |
| `EPOCH_STATE_V1` | Epoch reconstruction |
| `COMPANION_STATE_V1` | Companion presence state |
| `RUNTIME_BOOT_CONTEXT_V1` | What loads at boot |

**Cardinal principle:**

> Companion continuity is memory-backed, not provider-backed.

And harder:

> Do not become more fluent than your memory is grounded.

The greeting and boot must come from boot context, not model improvisation.

---

## 4. Embodiment / Interface Layer

AIRI and AIAvatarKit are correctly repositioned.

**Frozen rule:**

> AIRI renders presence. HELEN owns memory.

**AIRI is for:**
- Avatar, voice, VAD/STT/TTS
- Continuous presence, stage UI
- Expression, blink, gaze, idle presence

**AIRI is never for:**
- Canonical memory or identity
- Session or epoch truth
- Governed state mutation
- Sovereign access to reducer / ledger

The avatar is an **incarnation shell**, not a cognitive kernel.

---

## 5. What Has Actually Been Built

### Seam 2: Continuity and Boot (Closed ✅)

The system now proves:
- Identity restoration
- Session restoration
- Epoch restoration
- Graceful degradation if memory missing
- Greeting constrained by boot context
- No invented continuity

HELEN can now **resume without lying**.

### Seam 3: Capability Provenance (Closed ✅)

Active skills now carry provenance manifest:
- `manifest_id`, `manifest_hash`
- `domain_category`, `provider_class`

HELEN can explain:
- Why a skill is active
- Which capability envelope legitimized it
- Which decision admitted it
- How replay reconstructs that legitimacy

### Seam 1: Schema Tree Authority (Closed ✅)

Drift between `schemas/` and `helen_os/schemas/` secured.
Single authoritative constitutional schema tree.

No more:
- Silent schema drift
- Double truth on validation
- Covert regression on manifest / promotion packet

### Local Provider: HELEN ↔ Ollama (Wired ✅)

- HELEN calls a local model via API
- Provider layer remains non-sovereign
- Model is not fine-tuned "HELEN"
- HELEN is a constitutional layer + memory + prompt + context on top of a generalist model

Models used: Mistral, Qwen 3.5 9B, others explored.

**Important:** The depth currently comes from structure, corpus, hierarchy, prompt discipline, and memory continuity — not primarily from the LLM itself.

### Transport Layer (Working ✅)

- HELEN local web
- HELEN avatar via AIRI
- Wake word "HELEN"
- Pipeline: mic → STT → gate → HELEN API → response
- Telegram bot minimal
- Mode switching, system prompt routing
- Avatar presence

**The transport works. The bottleneck is now depth of judgment, not plumbing.**

---

## 6. The Real Gap: What Was Missing

The core problem was not the absence of tools.
It was the **absence of internal order**.

HELEN V0 could:
- Remember a little
- Respond
- Persist
- Embody a presence
- Use a local provider

But could not yet:
- Know what is central vs peripheral
- Know what is sacred to the project
- Know what deserves depth vs brevity
- Know what HELEN herself should "care about"

She had memory but not yet enough **discernment**.

---

## 7. The Architectural Answer: Internal Constitutional Corpus

**Decision:** Give HELEN a mind before giving her more hands.

### `HELEN_INTERNAL_CONSTITUTION_CORPUS_V1`

This corpus is not the memory, ledger, reducer, or institutional truth.
It is HELEN's **internal map of significance**.

Its purpose: not to store flat facts, but to store objects **with position**.

**Six object classes:**

| Class | Purpose |
|-------|---------|
| `TOWN_LAW` | Constitutional laws governing internal order and district boundaries |
| `DISTRICT_PROFILE` | Role, tone, jurisdiction, limits of each district |
| `PROJECT_PROFILE` | Project significance, not just description |
| `RESEARCH_TOPIC` | Active or latent research framing with centrality |
| `WORLD_RULE` | Rules for simulated / governed worlds (CONQUEST, etc.) |
| `CANONICAL_THREAD_NOTE` | Live or historically important threads in compressed form |

**Critical fields:**

| Field | Meaning |
|-------|---------|
| `salience_now` | What matters *right now* |
| `helen_stance` | Intensity of HELEN's own interest |
| `source_of_truth` | `curated / replay_derived / imported / inferred` |
| `relevance` | Positional explanation, not generic description |

This is what prevents HELEN from treating Casa Cielo and Mathematics as equivalent.

---

## 8. The New Attention Model

### Salience Map

| Value | Meaning |
|-------|---------|
| `core_now` | Immediate architectural center of gravity |
| `active_supporting` | Important but not singular center |
| `watchlist` | Relevant, monitored, not currently central |
| `dormant` | Real historically, not active now |
| `archive` | Preserved for historical meaning only |

### Stance Map

| Value | Meaning |
|-------|---------|
| `deep_helen_interest` | HELEN should naturally go deep here |
| `moderate_interest` | Engage meaningfully, don't dwell |
| `low_interest` | Answer accurately but briefly |
| `utility_only` | Context or logistics, not a place to expand |

**The real shift:**

HELEN no longer just knows something exists.
She knows **what position it occupies** and **how much she should care**.

---

## 9. The First Five Cognitive Skills

**Files:** `helen_city/skills/`
**Tests:** 26/26 passing ✅

| Skill | Purpose |
|-------|---------|
| `retrieve_project_profile` | Return structured project significance |
| `retrieve_district_law` | Return most relevant law for a district |
| `retrieve_research_topic` | Surface research framing with stance |
| `summarize_active_thread` | Thread summary by salience, not chronology |
| `suggest_next_action` | Recommend next move by centrality + tension |

**All five are:**
- Typed → inspectable outputs
- Read-mostly → no ledger writes
- `authority = "NONE"` → non-sovereign
- Deterministic → same inputs → same outputs
- Ranked by explicit weights → no boolean tie-breaking

**The shift in output quality:**

Before:
> "Projects include HELEN OS, ORACLE TOWN, CONQUEST, CASA CIELO, Mathematics"

After:
> "HELEN OS is the current center of gravity. Memory spine is the immediate practical frontier. CONQUEST remains important but is not the wedge of this moment. Casa Cielo is real but peripheral to the core architecture."

This is not style. This is **internal order**.

---

## 10. Ranking Law (Frozen)

```python
PRIORITY_WEIGHT = {"critical": 3, "high": 2, "medium": 1, "low": 0}
SALIENCE_WEIGHT = {"core_now": 3, "active_supporting": 2, "watchlist": 1, "dormant": 0, "archive": -1}
STANCE_WEIGHT   = {"deep_helen_interest": 2, "moderate_interest": 1, "low_interest": 0, "utility_only": -1}

candidates.sort(
    key=lambda x: (
        PRIORITY_WEIGHT[x["priority"]],
        SALIENCE_WEIGHT[x["salience_now"]],
        STANCE_WEIGHT[x["helen_stance"]],
        x["id"],   # deterministic tie-break
    ),
    reverse=True,
)
```

**Why explicit weights (not booleans):**
Boolean sorting creates only two buckets (True/False).
`high`, `medium`, `low` would all collapse to `False`.
→ Silent misranking by input JSON order.
→ "Taste" that depends on file ordering, not structure.

---

## 11. What Is Still Weak

### A. The base model is limited

Even with Qwen / Mistral, the model:
- Is not inherently deep by default
- Is susceptible to system prompt echo
- Is sometimes too flat

**Current depth comes from:** structure, corpus, hierarchy, prompt discipline, memory continuity — not yet from the LLM itself.

### B. Context composition not yet complete

`assemble_context_packet` is not yet mature.
It should compile: 1 law + 1 district + 1 project + 1 thread + 1 topic + 1 next action into one coherent response frame.
Without it: isolated judgments.
With it: a real conversational mental frame.

### C. Replay on real dirty logs not yet fully proven

Schema v1.1 hardened. ✅
But not yet proven:
- Replay on real chaotic logs
- Correct dominance of unresolved tensions
- Quality of best-next-action on real conflict
- `/init HELEN` superiority over actual notes/chat history

**The schema is ready. The product proof is not yet complete.**

---

## 12. The Skill Evolution Graph (SEG)

**Status:** Conceptually integrated, not yet in production

```
ELG (Experiment Lineage Graph) = memory of experiments
SEG (Skill Evolution Graph)    = memory of capabilities
```

**Flow:**
```
experiments
↓ lineage graph
↓ pattern detection (failure cluster / success cluster)
↓ NEW_SKILL_DISCOVERY_V1
↓ promotion case
↓ reducer decision (MAYOR)
↓ skill admission
↓ SEG update
```

**Constitutional rule preserved:**

> Skills may be proposed automatically.
> Skills may only be admitted by the reducer.

**Effect:** HELEN no longer only improves code locally.
She begins to improve her own capacity to do research.

---

## 13. Correct Build Order

**Wrong order:**
More tools → more voice gadgets → more presence → more agency
→ Without internal discernment → amplifies shallowness

**Correct order:**
1. Internal constitutional corpus ✅
2. Salience map ✅
3. Stance model ✅
4. Structured retrieval ✅
5. Read-mostly skills ✅
6. Context assembly (next)
7. Replay product wedge
8. Only then: more hands / tools / agency

**Compression:**

> First give HELEN a mind. Then give her hands.

---

## 14. Exact Current State

### What is already true ✅

- HELEN is local
- HELEN is persistent
- HELEN is offline-capable
- HELEN has structured memory
- HELEN has real sovereign / non-sovereign separation
- HELEN has a legal transition kernel
- HELEN has an internal significance corpus
- HELEN has her first discernment skills
- HELEN is beginning to be ordered

### What is not yet fully true ❌

- HELEN is not yet a "super intelligence"
- HELEN does not yet have a stable inner town
- HELEN does not yet have a mature `assemble_context_packet`
- HELEN does not yet have SEG-driven skill auto-evolution in production
- HELEN has not yet demonstrably beaten real notes + chat history on `/init HELEN` in production
- HELEN does not yet have constant native model depth

---

## 15. The Real Center of Gravity Now

Not: vision, metaphor, avatar, cosmetics, number of skills.

**Yes:**
- Discernment
- Internal ranking
- Context composition
- Replay truth
- `/init HELEN` wedge proof

```
validator truth → replay truth → recovery proof → only then broader capability
```

---

## Final Compression

HELEN started as a speculative framework.

She has become:
- A governed cognitive kernel
- A local persistent system
- An incarnable companion presence
- A legal transition machine
- A system with a beginning of internal hierarchy of significance

**The most important shift is not "more intelligence."**

It is that HELEN is beginning to distinguish:
- The central from the peripheral
- The living from the dormant
- The sacred from the noise
- What is interesting *for HELEN* from what merely exists

This prepares the real next step:

> An intelligence that no longer just remembers —
> but begins to **care asymmetrically**.

---

**Last Updated:** 2026-03-18
**Status:** Frozen — HELEN_FULL_RECAP_V1
**Authority:** Non-sovereign (this document describes, does not govern)
