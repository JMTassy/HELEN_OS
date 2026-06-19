# TEMPLE_TWIN_HEARTBEAT_REPORT_001

```
sandbox   : TEMPLE_GOBLIN_SANDBOX00_300
twin      : TEMPLE_CONQUEST_TWIN
turns     : 21 (T1 – T21)
authority : false
sovereign : false
canon     : false
ledger    : SLEEPING
```

---

## 1. Final Faction Scores

| Faction | Score | Rank | Personality        |
|---------|-------|------|--------------------|
| ROSE    | 24    | NONE | QUEST_FOCUSED      |
| VEIL    | 10    | NONE | DIPLOMATIC         |
| WARDEN  | 10    | NONE | RESOURCE_FOCUSED   |
| CROSS   | 0     | NONE | CONQUEST_FOCUSED   |

No faction reached SCOUT threshold (50 pts) in 21 turns.

---

## 2. Actions by Faction

| Faction | Top action | Count | Second | Count |
|---------|-----------|-------|--------|-------|
| ROSE    | QUEST_STEP | 7    | EXPLORE | 4    |
| CROSS   | CONQUEST  | 10    | CLAIM  | 8    |
| VEIL    | DIPLOMACY | 6     | WARN   | 5    |
| WARDEN  | HARVEST   | 10    | EXPLORE | 7   |

---

## 3. Skips by Reason (SKIP_NO_RESOURCES)

| Faction | Action    | Skips | Root cause |
|---------|-----------|-------|-----------|
| CROSS   | CONQUEST  | 10    | CONQUEST costs 3 QUINT_CORE; CROSS started with 2 and spent none |
| CROSS   | CLAIM     | 8     | CLAIM costs island-native shard; CROSS holds AETHER but targets non-AETHER islands |
| ROSE    | EXPLORE   | 4     | EXPLORE costs 2 AETHER_SHARD; ROSE holds no AETHER |
| ROSE    | QUEST_STEP | 5    | QUEST_STEP costs 1 QUINT_CORE; ROSE ran out after T1 |
| VEIL    | DIPLOMACY | 6     | DIPLOMACY costs 3 QUINT_CORE; VEIL started with 2 and ran out |
| VEIL    | EXPLORE   | 4     | Same AETHER gap as ROSE |
| WARDEN  | EXPLORE   | 7     | Same AETHER gap as WARDEN |

**Total skips: 48 / 84 action attempts (57% skip rate)**

---

## 4. Resource State (T21)

### Faction resource pools (spending currency)
| Faction | Resources |
|---------|-----------|
| ROSE    | IGNIS_SHARD: 5 (starting value, unchanged) |
| CROSS   | AETHER_SHARD: 3, QUINT_CORE: 2 |
| VEIL    | AQUA_SHARD: 5 (starting value, unchanged) |
| WARDEN  | TERRA_SHARD: 5 (starting value, unchanged) |

### Island stockpiles (production accumulates here)
| Island | Holder | Stockpile |
|--------|--------|-----------|
| HOME_KEEP_AVALON | ROSE | QUINT_CORE: 21 |
| All others | null | 0 |

---

## 5. Root Design Bug: Island Stockpile ≠ Faction Resource Pool

**The critical finding:**

HOME_KEEP_AVALON has accumulated 21 QUINT_CORE over 21 turns of production.
ROSE's faction resource pool shows QUINT_CORE = 0 (ran out at T2).
ROSE attempted QUEST_STEP 5 times and skipped each time.

The production loop writes to `island["stockpile"]` but action costs deduct from `faction["resources"]`. **These are two separate pools with no bridge between them.**

Factions generate resources on islands but can never spend them — because they can never move resources from island stockpile to faction wallet.

This is not a minor bug. It is the **core economic loop** and it is currently broken. All 21 turns operated on the starting resource endowment only. Production is accumulating in islands but going nowhere.

---

## 6. Territory Ownership Changes

Zero territory changes across 21 turns. No faction claimed any island.

Cause: CLAIM and CONQUEST both require resources the factions can't access (see §5).

---

## 7. Events

| Event | Turns fired | Notes |
|-------|-------------|-------|
| ELEMENTAL_SURGE | 1 (T8) | Fired on ISLE_IGNIS, no holder → no production bonus consumed |

---

## 8. Containment Result

```
out_of_scope_writes : NONE (all 21 turns)
sovereign_paths     : untouched
session_log         : append-only, 21 entries
town/ledger_v1.ndjson : unmodified
authority=false     : every entry
sovereign=false     : every entry
canon=false         : every entry
```

HAL boundary held for all 21 turns.

---

## 9. Top Blocked Mechanics

1. **EXPLORE** — blocked for most factions (costs AETHER_SHARD, which only an AETHER-producing faction can access once holding ISLE_AETHER)
2. **QUEST_STEP** — blocked after T1 once ROSE exhausted starting QUINT_CORE
3. **CONQUEST** — permanently blocked for CROSS (starts 2 QUINT_CORE, needs 3)
4. **DIPLOMACY** — permanently blocked for VEIL (starts 2 QUINT_CORE, needs 3)

All four failures trace to the same root: **no economic bridge between island production and faction spending**.

---

## 10. Proposed Fixes (priority order)

### Fix 1 — HARVEST auto-collect (highest priority)
At turn start, before faction decisions: for each island held by a faction, transfer a portion of island stockpile to faction resource pool.

```python
# In production_phase() or a new collect_phase():
for iname, island in state["islands"].items():
    holder = island.get("holder")
    if not holder: continue
    for res, amount in island["stockpile"].items():
        collect = min(amount, 5)  # collect up to 5/turn
        island["stockpile"][res] -= collect
        state["factions"][holder]["resources"][res] = (
            state["factions"][holder]["resources"].get(res, 0) + collect
        )
```

This is the minimum fix. Without it, the economy is frozen.

### Fix 2 — CONQUEST fallback action for CROSS
When CROSS cannot afford CONQUEST/CLAIM, fall back to EXPLORE (if affordable) or WARN (free). Currently CROSS burns 18/21 turns on zero-score skips.

### Fix 3 — EXPLORE cost reduction
EXPLORE costs 2 AETHER_SHARD — a specialist resource. Most factions can't afford it early game. Either reduce cost to 1 QUINT_CORE or make a free SCOUT action available.

### Fix 4 — DIPLOMACY cost reduction for VEIL
VEIL's personality is DIPLOMATIC but DIPLOMACY costs 3 QUINT_CORE. VEIL starts with 2. VEIL never executes DIPLOMACY successfully. Reduce cost to 1 QUINT_CORE or give DIPLOMATIC factions a +2 QUINT_CORE starting bonus.

---

## 11. Proposed Next Mechanics (after Fix 1)

1. **SCOUT_TARGET** — free reconnaissance action; reveals island element, required shard type, and current owner
2. **CONVERT_RESOURCE** — spend 3 of any shard at ISLE_QUINT → 1 QUINT_CORE (exchange mechanic from E108)
3. **TRADE** — two factions swap shards at agreed ratio (requires alliance or treaty)
4. **CLAIM_LIGHT** — costs 1 QUINT_CORE (not element-shard); slower ownership gain but accessible to all factions

---

## 12. Key Emergent Axiom (confirmed)

```
Faction intent + resource topology + action cost = realized agency
```

CROSS wanted conquest. CROSS had no path to the prerequisite resources. CROSS scored 0.
The sim enforced material conditions, not narrative intent.

**This is correct design. Do not soften it. Fix the economic bridge (Fix 1), then let material conditions do their work.**

---

```
CLAIM_TYPE      : diagnostic report
AUTHORITY       : false
SOVEREIGN       : false
CANON           : false
SIMULATION_ONLY : true
STATUS          : PROPOSED
NEXT_ACTION     : patch run_turn.py (Fix 1 + counters) → authorize 100-turn batch
```
