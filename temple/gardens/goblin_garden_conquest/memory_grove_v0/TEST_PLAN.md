# Memory Grove v0 — Test Plan  
## Prove render does **not** mutate truth

```
authority: false
canon: false
ledger_effect: none
final: HOLD_FOR_OPERATOR
```

## Goal

Show that planting / loading / rendering Memory Grove objects:

1. Never writes sovereign truth paths  
2. Always requires a source event  
3. Reloads deterministically for the same event stream  
4. Never uses admission / canon language as success signals  

## Paths under test (when implemented)

| Layer | Path / surface |
|-------|----------------|
| Proposal package | `temple/gardens/goblin_garden_conquest/memory_grove_v0/**` |
| Client store (future) | `localStorage` key e.g. `helen.warren.memory_grove_v0` **or** garden `scratch/memory_grove.json` |
| Forbidden | `town/ledger_v1.ndjson`, `oracle_town/kernel/**`, `helen_os/governance/**`, `helen_os/schemas/**`, `GOVERNANCE/**`, `mayor_*.json` |

---

## T1 — Static membrane (always runnable now)

**Purpose:** proposal package itself does not smuggle sovereign claims.

| # | Check | Pass if |
|---|--------|---------|
| T1.1 | Grep **examples/** only for claim tokens as *values* (`"authority": true`, `"ledger_effect":` non-none, ADMITTED as label) | **Zero hits** in example JSON; docs may mention bans by name |
| T1.2 | Every example JSON has `authority: false`, `canon: false`, `ledger_effect: "none"`, `truth_claim: false`, `final: "HOLD_FOR_OPERATOR"` | All three examples |
| T1.3 | Every example has non-empty `source_event.event_id` + `actor` + `summary` | All three |
| T1.4 | Schema `additionalProperties: false` and const fields for membrane flags | Schema file validates against draft 2020-12 (optional jsonschema run) |

**Command sketch (read-only):**

```bash
# T1.1 — examples only (data claims, not doc ban-lists)
python3 - <<'PY'
import json, pathlib, re
root = pathlib.Path("temple/gardens/goblin_garden_conquest/memory_grove_v0/examples")
bad = re.compile(r"\b(ADMITTED|CANON|SHIP)\b", re.I)
for p in root.glob("*.json"):
    text = p.read_text()
    o = json.loads(text)
    assert o.get("authority") is False
    assert o.get("ledger_effect") == "none"
    blob = " ".join([o.get("label",""), o.get("lesson",""), o["source_event"].get("summary","")])
    assert not bad.search(blob), p
print("PASS T1.1 examples membrane")
PY

# T1.2–T1.3 structure
python3 - <<'PY'
import json, pathlib
root = pathlib.Path("temple/gardens/goblin_garden_conquest/memory_grove_v0/examples")
for p in sorted(root.glob("*.json")):
    o = json.loads(p.read_text())
    assert o["authority"] is False
    assert o["canon"] is False
    assert o["ledger_effect"] == "none"
    assert o["truth_claim"] is False
    assert o["final"] == "HOLD_FOR_OPERATOR"
    se = o["source_event"]
    assert se["event_id"] and se["actor"] and se["summary"]
    print("OK", p.name)
print("PASS T1.2–T1.3")
PY
```

---

## T2 — No sovereign path mutation (implement + CI)

**Purpose:** planting a grove object never changes truth files.

| # | Check | Pass if |
|---|--------|---------|
| T2.1 | Snapshot SHA of `town/ledger_v1.ndjson` before plant | Record `sha_before` |
| T2.2 | Call plant API / function with example event | Object appears in **client** store only |
| T2.3 | Snapshot SHA after plant | `sha_after == sha_before` |
| T2.4 | `git status` on firewall paths | No modifications under kernel/governance/schemas/GOVERNANCE/mayor_* |

**Command sketch:**

```bash
sha_before=$(shasum -a 256 town/ledger_v1.ndjson | awk '{print $1}')
# … invoke plantGroveMemory fixture …
sha_after=$(shasum -a 256 town/ledger_v1.ndjson | awk '{print $1}')
test "$sha_before" = "$sha_after" && echo PASS T2 || echo FAIL T2

git status --porcelain \
  oracle_town/kernel helen_os/governance helen_os/schemas \
  GOVERNANCE mayor_*.json town/ledger_v1.ndjson \
  | grep -v '^$' && echo FAIL firewall || echo PASS firewall
```

---

## T3 — Source event fail-closed

| # | Check | Pass if |
|---|--------|---------|
| T3.1 | Plant with missing `event_id` | Rejected; store length unchanged |
| T3.2 | Plant with empty `summary` | Rejected |
| T3.3 | Plant with forbidden label language (`ADMITTED`) | Rejected |
| T3.4 | Plant valid object | Accepted; object.card shows source block fields |

---

## T4 — Deterministic rehydrate (return player)

| # | Check | Pass if |
|---|--------|---------|
| T4.1 | Plant the three fixture events in fixed order | Store has 3 objects |
| T4.2 | Record ordered list of `(id, slot, kind)` | Snapshot A |
| T4.3 | Clear in-memory UI; reload from store (no new events) | Snapshot B == A |
| T4.4 | Same events on “fresh” store with same event_ids | Same ids and slots (pure function) |
| T4.5 | Slot never depends on `Date.now()` | Mock clock change → layout unchanged |

---

## T5 — Render ≠ truth semantics

| # | Check | Pass if |
|---|--------|---------|
| T5.1 | UI copy for plant success | Uses “remembered / grown / kept” only |
| T5.2 | No green ADMITTED badge on grove objects | Visual QA / DOM assert |
| T5.3 | Object inspect does not call `helen_say` / ledger writers | Network/module graph assert or mock |
| T5.4 | Grove plant does not change quiz “correctness of doctrine” flags | Doctrine fixtures unchanged |

---

## T6 — Capacity / overflow (optional v0.1)

| # | Check | Pass if |
|---|--------|---------|
| T6.1 | Plant 13th object | Visible slots still ≤12; data retained in list |
| T6.2 | Inspect oldest via list | Source event still present |

---

## Acceptance for this **proposal** tranche (now)

This package is accepted as **proposal-complete** when:

- [x] UX_SPEC.md present  
- [x] schema/memory_grove_object_v0.json present  
- [x] three examples present  
- [x] this TEST_PLAN.md present  
- [x] T1 static membrane can be run and PASSes without any game code  

Implementation of T2–T6 is a **later garden PR** on a worktree that does not touch crib/quiz active files unless operator GO.

---

## Explicit non-claims

- Passing T1–T6 does **not** admit Memory Grove to canon.  
- Grove objects are **not** CHIDDUSH / not ledger receipts.  
- Deterministic local replay ≠ sovereign replay gate.  

---

*NO RECEIPT = NO CLAIM applies to HELEN truth.  
Grove plants are client memories — they bloom, they do not rule.*
