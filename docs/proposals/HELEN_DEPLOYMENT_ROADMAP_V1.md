# HELEN OS — Deployment Roadmap V1 (R&D → Deployable Kernel)

```yaml
schema: ROADMAP_PROPOSAL_V1
authority: false
canon: false
ledger_effect: none
status: PROPOSED
owner: operator (JMT)
review_date: 2026-07-31
kill_criterion: superseded by an operator-chosen thesis (Phase 0 decision) or deleted if not reviewed by review_date
grounding: written against verified session findings (AR-TERMINATION-002,
           RENDER_CLARITY_AUDIT_V1, EXECUTOR/BRIDGE/LINTER proposals,
           LOOPS.md loop-3 gap, cross-seat drift in .claude/STATE.md),
           not against aspiration
```

## The core diagnosis

HELEN OS as a whole is not the product. It is a research vehicle carrying
one genuinely differentiated asset: **the governance kernel contract** —
append-only hash-chained ledger, single admitted writer, typed receipts,
deterministic replay, admission gates, proposer ≠ validator. In 2026 every
company deploying AI agents needs exactly this primitive (audit-grade
receipts for agent actions) and no framework ships it cleanly. Everything
else in this repo — surfaces, temple, video pipelines, telegram bots — is
R&D exhaust: keep it, love it, do not scale it.

**The scaling model is git, not a web service.** An append-only chain with
one sovereign writer does not scale by adding writers. It scales
hub-and-spoke: many non-sovereign seats produce receipts locally; one
sovereign ledger admits batches through the existing promotion protocol.
The doctrine already says this (`skill_local_admission ≠
operator_authorized_admission`) — the roadmap just makes it physical.

## Phase 0 — Pick the thesis (operator decision, ~1 week, no code)

Three candidate products. Everything downstream branches on this choice.

- **A. Embeddable governance kernel** ("git for agent actions"): extract
  the kernel as a library/protocol other agent stacks embed. Widest
  market, hardest positioning.
- **B. Personal sovereign AI companion**: single-tenant appliance, one
  kernel per person, HELEN as the reference personality. Emotionally
  central, niche market.
- **C. Pure research instrument**: then "scale" means reproducibility
  and publication, not deployment — the roadmap ends at Phase 2.

**Recommendation: A, with B as its reference deployment.** They compose;
A is where the differentiation is.

Exit criterion: one written sentence — "HELEN ships as ___ for ___" —
admitted to CLAUDE.md by operator decision.

## Phase 1 — Kernel extraction & hardening (~2-3 weeks)

Make the kernel a real package instead of a repo-shaped organism.

1. **Extract `helen-kernel`**: ledger writer (`ndjson_writer.py`),
   canonical schemas (`helen_os/schemas/`), gate interfaces, kernel
   daemon, replay verifier — one installable package. Today
   `pyproject.toml` declares `oracle-town` with `dependencies = []`;
   that fiction ends here.
2. **Fix the four verified reliability findings** — they all sit exactly
   at the multi-user seam and their proposals already exist with
   candidate fixes:
   - executor burn-on-failure + registry TOCTOU
     (`EXECUTOR_BURN_ON_FAILURE_AND_REGISTRY_TOCTOU_V1.md`)
   - fire-and-forget ledger bridge (`FIRE_AND_FORGET_LEDGER_BRIDGE_V1.md`)
   - linter document-global pardon
     (`LINTER_DOCUMENT_GLOBAL_RECEIPT_PARDON_V1.md`)
3. **Kill single-machine assumptions**: hardcoded `~/Documents/GitHub`
   SOT paths (status API line 14 and friends), Unix-socket-only daemon
   (add a localhost TCP transport behind the same single-writer
   discipline), one `HELEN_HOME` env var for all state.
4. **Adopt the lifecycle fields repo-wide** (owner / review_date /
   kill_criterion): AR-TERMINATION-002 measured 87.6% parking, 0 review
   dates. Governance mass that never terminates will sink any deployment;
   the stub inserter (`lifecycle_stub_inserter.py`) exists, gated on GO.

Exit criterion: `pip install helen-kernel` on a clean machine;
`helen-kernel verify` runs chain + replay checks green.

## Phase 2 — Reproducible single-node deployment (~1-2 weeks)

1. **Containerize**: `Dockerfile`, `Dockerfile.api`, `docker-compose.yml`
   already exist in-tree — make compose bring up kernel daemon + API +
   one honest surface against a fresh ledger, with the healthcheck being
   an actual replay-determinism smoke test, not a port ping.
2. **Ledger operations doctrine**: backup/restore, seal/rotate (sealed
   epochs already exist as a concept — `storage/ledger_epoch*_work.ndjson`),
   documented recovery from a mid-write crash.
3. **CI cold-boot job**: clean container → init ledger → run the four
   `make demo-*` targets → verify chain. Reproducibility becomes a gate,
   not a hope.
4. **Fix render-audit T1** (ralph.sh verdict laundering) — the automation
   loop must be trustworthy before anything runs unattended in a
   container.

Exit criterion: a person who is not the operator boots HELEN from the
README on a machine that has never seen it, in under 30 minutes, and the
chain verifies.

## Phase 3 — Multi-seat, single sovereign (~3-4 weeks)

The actual scaling architecture. Not more writers — more seats.

1. **SEAT_LEDGER_V1**: same NDJSON chain format, permanently
   `authority=false`. Every machine/agent/seat runs its own local chain
   freely (this is what the cloud seat and the Windows/WSL seat already
   do de facto).
2. **Sync tool**: seat ledger → proposal bundle → MAYOR admission queue →
   sovereign ledger, through the existing 6-gate `_handle_promote_skill`
   / promotion-protocol machinery. Batched, operator-ratified, seq-fork
   impossible because only the sovereign writer ever writes the sovereign
   chain.
3. **Drift as a first-class metric**: the cross-seat skill-convention
   drift (`.claude/STATE.md`, helen-conquest vs helen-os-JMTC) was the
   first real multi-seat bug. `transport/drift.py` Δ already formalizes
   doc↔guard drift — extend it to seat↔sovereign convention drift and
   report it in the session digest.
4. **Model routing registry becomes deployment config**: the HAL 3-way
   drift showed what happens when role→model resolution lives in three
   places. `docs/spec/model_routing_registry.json` + `tools/model_registry.py`
   become the only source, per seat.

Exit criterion: two physical machines, one sovereign chain, a full
propose→admit→replay round-trip with zero seq forks and measured Δ.

## Phase 4 — External witness (Loop 3) (~4-8 weeks)

`LOOPS.md` finding: HELEN has an agentic loop (minutes) and a developer
loop (hours) but **no external feedback loop at all**. R&D without Loop 3
cannot tell if it's building value.

1. **Precondition — stop the glass from lying**: render-audit tranches
   T2-T3 (client-side receipt minting, fabricated PASS panels). You
   cannot show a governance product whose own demo counterfeits receipts.
2. **2-3 design partners** run `helen-kernel` against their own agent
   stacks (thesis A) or a hosted companion instance (thesis B). Their
   typed failure receipts are the first external evidence stream.
3. **Governance Yield goes live**: failures_prevented /
   governance_objects_added (`governance_yield_report.py` exists,
   seeded). External users finally supply the numerator. If yield stays
   ~0 after two months of partner use, that is Phase 0's kill signal —
   honor it; termination is sacred.

Exit criterion: one external failure that a HELEN gate caught before it
shipped, receipted, cited by a person who is not the operator.

## Phase 5 — Scale-out decision (only after Phase 4 evidence)

- **Hosted** (SaaS): per-tenant sovereign chains. Scales horizontally
  trivially *because* tenants share nothing — the single-writer
  constraint is per-chain, and chains don't touch.
- **Protocol/OSS**: publish the ledger + receipt + admission spec with
  `helen-kernel` as reference implementation; others host themselves.
- Or both (open core). Decided by what Phase 4 partners actually pay
  attention to.

## Anti-goals (explicitly not scaled)

- `temple/gardens/`, `temple/subsandbox/` — NO_CLAIM zones stay local
  forever; that locational safety is load-bearing.
- The 10 operator surfaces — one honest surface (temple.html's
  LIVE/FALLBACK pattern) ships; the rest remain lab instruments.
- Video/TTS/Telegram pipelines — demos, not deployables.
- Multi-writer sovereign ledger — never. Scaling pressure on the writer
  is always answered with more seats, not more writers.

## Sequencing summary

```
P0 thesis (1w) → P1 extract+harden (2-3w) → P2 reproducible node (1-2w)
             → P3 multi-seat (3-4w) → P4 external witness (4-8w) → P5 decide
```

Roughly one quarter of solo-operator R&D pace to reach external evidence.
Each phase has a receipt-shaped exit criterion; no phase starts on an
unreviewed prior one.

---
authority=false · canon=false · ledger_effect=none · PROPOSED
owner: operator (JMT) · review_date: 2026-07-31
kill_criterion: superseded by Phase 0 thesis decision or deleted if unreviewed
