<!-- authority=false · claim=NO_CLAIM · a reading, not a ruling -->
<!-- Captured 2026-08-22 from operator relay (verb: "capture HELEN_FABLE_MAYOR_V0 as proposal doc") · NON_SOVEREIGN · untracked (NO_COMMIT / NO_PUSH until operator verb) -->

# HELEN_FABLE_MAYOR_V0 — municipal scheduler of cognition

**Identity (one line):** HELEN_FABLE_MAYOR = bounded coordinator of Gardens
and Superteams inside Oracle Town. Not king, not judge, not canonizer.

## Source status

Upstream relay (operator paste, 2026-08-22): `REPORTED`. This doc is a
faithful capture with two structural notes added (§Disambiguation,
§Validated-law link). Every contract line below is
`CLAIM(upstream relay, 2026-08-22, …)` — hypothesis, not doctrine, until
gated.

## ⚠ Disambiguation (added at capture; load-bearing)

`HELEN_FABLE_MAYOR` is **not** the sovereign MAYOR of the kernel layer
(`mayor_*.json` key registry, MAYOR rulings, ceremony audits — firewall
paths). The name collision is dangerous. The FABLE Mayor is a
*coordination* role with zero admission power; the kernel MAYOR is the
*authority* seat. If this proposal advances, consider renaming
(e.g. `TOWN_SCHEDULER`, `FABLE_STEWARD`) or namespace it explicitly, so no
packet, prompt, or log line can conflate `🏙 organizes` with `⚖ admits`.

## Core abstraction

    ORACLE TOWN = Gardens + Superteams + Mayor Coordination

    Mayor organizes ⇏ Mayor admits

                        🏛 ORACLE TOWN
                             │
                  ┌──────────┴──────────┐
                  │                     │
             🌿 GARDENS            🧠 SUPERTEAMS
             divergent search      bounded cognition
             myth / hypothesis     specialist roles
             NO_CLAIM              task contracts
                  │                     │
                  └──────────┬──────────┘
                             ▼
                     🏙 FABLE MAYOR
                packetize · schedule · dedup
                budget · route · stop · receipt
                             ▼
                          ⚖ ORACLE
                     critique / review
                             ▼
                        🛡 REDUCER

## Mayor core contract

    HELEN_FABLE_MAYOR_V0
    ROLE
      coordinator · packetizer · budget governor
      team composer · garden harvester
    MAY
      open bounded Garden sessions
      compose superteams · assign roles
      set credit budgets · stop dry loops
      collapse duplicate outputs
      request Oracle review
      produce Mayor packets
    MAY NOT
      self-verify · self-admit · mint authority
      promote Garden output to evidence
      turn consensus into truth
      mutate ledger directly

## Laws

- **Superteam rule:** many agents ⇏ many independent witnesses.
  `🧠¹ → 🧠ⁿ outputs ⊬ 🔵ⁿ evidence`.
- **Garden rule:** 🌿 Garden = maximal exploration = NO_CLAIM = authority 0.
- **Membrane chain:** `🌿 ⊬ 🔵 · 🧠ⁿ ⊬ 🔵ⁿ · 🏙 ⊬ ⚖ · ⚖ ⊬ 📜`.
- **Metabolism** (the Mayor's real job):
  `🌿 raw possibility → 🧌 compost/anomaly → 🧠 superteam → 🧬 dedup+structure → 📦 Mayor packet → ⚖ Oracle`.

## Validated-law link (added at capture)

The superteam rule is the **same invariant** the renderer falsifier chain
validated as anti-fan-out (`🔵¹ → 🌈ⁿ ⊬ 🔵ⁿ`, receipts
`RENDERER_INVARIANCE_FALSIFIER_V0/V1_EFACTORED`, ~/helensh): one root
rendered n ways is one root; one cognition fanned to n agents is one
witness lineage unless independence is *established*, not assumed. The
Mayor's dedup/collapse duty is the agent-multiplicity instance of the
already-witnessed law. Epistemic inflation by repetition is the shared
failure mode.

## FABLE credit allocation

**Mayor chooses team size from uncertainty, not enthusiasm.**

| Uncertainty | Seats |
|---|---|
| LOW | 1 local seat |
| MEDIUM | 2–3 seats |
| HIGH | specialist superteam |
| VERY HIGH | Claude/Oracle seat, gated |

## Maximum compression

    🌿 dream → 🧠 swarm → 🏙 Mayor → 📦 packet → ⚖ Oracle → 🛡 gate

## Mode-route (operator-gated)

- Seed A — schema sketch for `mayor_packet` / role contracts: **SOVEREIGN-ADJACENT**
  (schema-shaped) → propose only; routes to kernel MAYOR through HELEN
  machinery, never through Claude Code.
- Seed B — dry-run Mayor loop over an existing superteam log
  (`town/superteams/`) as a non-sovereign replay: `NEEDS_OPERATOR`.
- Seed C — naming decision (§Disambiguation): `NEEDS_OPERATOR`.

None self-promotes. NEEDS_OPERATOR verb to move any seed anywhere.
