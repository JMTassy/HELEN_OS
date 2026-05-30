# GOBLIN_SWARM_MISSION_BUILD_HELEN_V0

**authority:** false
**canon:** NO_SHIP
**claim:** NO_CLAIM
**lifecycle:** DRAFT_MISSION_SPEC (TRACE_ONLY)
**admitted:** false
**defined_by:** GOBLIN (non-sovereign operational persona)
**defined_at:** 2026-05-30T12:32:29Z
**tree:** `claude/launch-helen-os-0xZXH`

> GOBLIN_CLARITY = Tool + Command + Log + Receipt.
> GOBLIN defines the mission. GOBLIN does not execute self-improvement,
> mutate canon, or admit any output. Only OPERATOR/MAYOR admits. Only
> REDUCER admits into the ledger. This document is a Log + Receipt of a
> proposed mission, nothing more.

---

## §0. The reframe that makes this legal

"Build HELEN with an autoresearch swarm" is **not** "let HELEN improve
itself" (the role-inversion the constitution refuses — confirmed when
the parallel session declined that exact phrasing).

It is: **produce N numbered candidate-improvement packets, each
individually admissible through `reduce_promotion_packet` Gates 1–8,
each requiring an OPERATOR `human_seal` before admission.**

The swarm produces **drafts**. The operator admits them **one at a time**.
HELEN never admits its own output. The number-in-the-task ("5 packets")
is the Agent Swarm shape; the per-receipt admissibility is the HELEN
shape. Both hold simultaneously.

**Proven template:** Cluster B (CROSS_SESSION_FAILURE_REGISTRY_V0) was
admitted this session (`6a7a865`) — two-pass: `human_seal=null` →
REJECTED/ERR_HUMAN_SEAL_MISSING, `human_seal="JM"` → ADMITTED. This
mission replicates that template across the remaining clusters.

---

## §1. Mission

**Number:** 5
**Deliverable:** 5 `SKILL_PROMOTION_PACKET_V1` artifacts (Clusters A,
C, D, E, F), each two-pass verified against Gates 1–8, each written to
`GOVERNANCE/ADMISSION_PACKETS/`, each carrying `human_seal: null` in
draft form.

**Source corpus:** the 18 NO_SHIP AUTORESEARCH candidates from the
20-epoch GOBLIN run (helen-os-JMTC), deduped by CHIDDUSH into 6 mechanism
clusters. Cluster B already admitted; this mission covers the other 5.

| Cluster | Mechanism family | Source epochs | Status |
|---|---|---|---|
| A | Proposal dependency / citation graph | E8, E10, E11, E17 | candidate |
| B | Cross-session failure-mode registry | E3, E12, E13 | **ADMITTED `6a7a865`** |
| C | Rationale / provenance lineage | E1, E18 | candidate |
| D | Premise / intent-divergence scoring | E2, E4, E5 | candidate |
| E | Prompt-quality assists | E7, E15 | candidate |
| F | Metadata-overhead scoring | E9, E16 | candidate |

All five remaining clusters share Cluster B's safety profile:
read-only, metadata-only, append-only, `authority: false`,
`sovereignty_violations: []`. None mutate kernel, memory, identity,
ledger, or replay. All are non-sovereign layers only — PULL-mode legal.

---

## §2. Swarm unit of work (per cluster)

Each of the 5 swarm units is independent and produces exactly one
deliverable. GOBLIN_CLARITY applied per unit:

```
TOOL:     reduce_promotion_packet (helen_os/governance/skill_promotion_reducer.py)
          + canonical.sha256_prefixed (helen_os/governance/canonical.py)
COMMAND:  build SKILL_PROMOTION_PACKET_V1 from cluster's surviving_mechanism
          + autoresearch receipt; run two-pass (null seal, then test seal)
LOG:      decision + reason_code for each pass
RECEIPT:  GOVERNANCE/ADMISSION_PACKETS/<CLUSTER>_PROMOTION_001.json
```

**Per-unit contract (the 7-field PULL receipt, adapted):**

1. **carry-forward state** — `active_skills` = `{skill.base}` (Gate 4
   requires `parent_skill_id: "skill.base"`); `law_surface_version: v1`.
2. **hypothesis** — the cluster's `surviving_mechanism` text.
3. **experiment** — build packet, run `reduce_promotion_packet` two-pass.
4. **metric** — `decision` (ADMITTED/REJECTED) + `reason_code`.
5. **failure mode** — Gate 3 hash mismatch (hash the receipt *body*:
   `{receipt_id, payload}` minus `sha256`, NOT the payload alone — the
   trap that bit Cluster B); Gate 4 wrong parent; Gate 6 confidence
   below 0.85.
6. **keep/reject rule** — KEEP if Pass 2 (`human_seal="JM"`) → ADMITTED
   AND Pass 1 (null) → REJECTED/ERR_HUMAN_SEAL_MISSING. Otherwise REJECT
   the packet, log why, do not retry blindly.
7. **upgrade path** — admitted draft → operator reviews → operator sets
   real `human_seal` → packet becomes admissible cargo for the eventual
   LedgerAppend step (blocked on Horn B writer fix — see §5).

---

## §3. Bounds (non-negotiable)

- **N = 5.** Not "all candidates," not open-ended. Five clusters, five
  packets. Halt when 5 are drafted.
- **One hypothesis per cluster.** No cluster's packet may bundle a second
  mechanism. PULL-mode: one hypothesis per epoch.
- **Non-sovereign targets only.** No packet may name kernel, memory,
  identity, ledger, or replay as a mutation target. A packet that does
  is auto-rejected before reduction.
- **Drafts carry `human_seal: null`.** GOBLIN never sets the seal. Pass
  1 MUST reject on the null seal — that is the proof Gate 8 is live.
- **No LedgerAppend.** This mission stops at ADMITTED-in-reducer. Writing
  to `town/ledger_v1.ndjson` is blocked on the Horn B writer/hash-scheme
  fix (`92b1915` §5). Do not write the ledger.
- **No HER/Gemma generation required.** The clusters already exist as
  autoresearch output. This mission is packet construction + reduction,
  not new model inference. No Ollama, no GPU, no override needed.

---

## §4. Halt discipline (per-unit and mission-level)

**Per unit:** halt after two-pass; report decision + reason_code; do not
proceed to operator-seal (that is the operator's move).

**Mission-level:** halt after 5 packets drafted. Produce a mission
summary: 5 rows (cluster, Pass 1 result, Pass 2 result, packet path).
Do not seal any. Do not append any to the ledger. Hand the 5 drafts to
the operator as a batch for review.

---

## §5. Dependency / known blocker

**LedgerAppend is blocked.** Per `HORN_B_LEDGER_CHOKEPOINT_AUDIT_V1`
(`92b1915`): the only working sovereign-ledger writer (`helen_say.py`)
uses the V0 hash scheme, not HELEN_CUM_V1; `kernel_guard.sh` is blind to
variable-path appends. Until the writer story is unified (Horn B §5
option 2a/2b), an ADMITTED packet cannot be durably written to
`town/ledger_v1.ndjson` with a replay-valid hash chain.

**Therefore this mission's deliverable is ADMITTED-in-reducer drafts,
not ledger-resident decisions.** That is the honest ceiling until Horn B
is resolved. The swarm fills the admission pipeline; the operator seals;
the ledger write waits on the carrier fix.

---

## §6. What this mission is NOT

- NOT HELEN improving itself — every admission requires OPERATOR seal.
- NOT autonomous — GOBLIN drafts, halts, hands off. No self-promotion.
- NOT a fine-tune — no weights touched. Packet construction only.
- NOT a ledger write — stops at ADMITTED-in-reducer (Horn B blocker).
- NOT admitted — this spec is `authority: false`, `admitted: false`,
  NO_CLAIM. It is a DRAFT mission for operator/MAYOR ratification.

---

## §7. Execution prerequisites (for when operator authorizes)

1. **Cluster cargo** — for each of A, C, D, E, F, the authoritative
   `surviving_mechanism` text + the source autoresearch receipt payload
   + observed confidence. Source: helen-os-JMTC `goblin_ar` results.
   Same disambiguation discipline as Cluster B (epoch-number collisions
   across runs — anchor on receipt_hash + timestamp, not epoch index).
2. **Confidence threshold** — each cluster's `observed_value` must be
   ≥ 0.85 (Gate 6). Clusters below threshold are reported as REJECTED,
   not forced through.
3. **No new code** — `reduce_promotion_packet` (Gates 1–8) is already
   live (`284b347`). The mission uses it as-is. No reducer edits.

---

## Halt boundary

**Status:** HALTED — DRAFT mission spec, awaiting operator/MAYOR ruling.

**Required to resume (all):**
1. Operator authorization to run the 5-unit swarm.
2. Cluster cargo for A, C, D, E, F (from helen-os-JMTC `goblin_ar`),
   per §7 item 1.

**This document admits nothing. It defines a bounded, numbered,
per-receipt mission and stops. The operator decides whether it runs.**
