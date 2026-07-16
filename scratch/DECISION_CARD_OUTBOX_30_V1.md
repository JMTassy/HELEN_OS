# DECISION CARD — OUTBOX 30 · V1 (2026-07-06)

NON_SOVEREIGN · authority=false · ledger_effect=none · card proposes, PEN decides
30 unconsumed packets → 4 decisions. Estimated pen time: ~10 minutes.

---

## BATCH A — 26× scanner lexical noise → propose **rejected**

One finding, 26 masks: the scanner flags `proposal_marker` / `risk_marker` /
`gap_marker` **keywords inside proposal docs** — which contain those words by
definition. No crossing analysis, no unique content per packet. (This is the
known lexical over-trigger failure mode: flag the crossing, not the glyph.)

The real signal is preserved as a next-step: **upgrade the scanner from
keyword-match to crossing-detection before any rescan.**

Packets: AR-137a79dbae09 · AR-1c394e006626 · AR-3521ec730fd4 · AR-39307ac76191 ·
AR-3b7799cb88a0 · AR-4eedf96f7ace · AR-5602a344e0d6 · AR-5832a927028e ·
AR-603402e9d1c4 · AR-622d76f69257 · AR-671223d898a2 · AR-83d2c37481c7 ·
AR-842e7f4922cf · AR-941d3bbb6333 · AR-944b83d2fa9e · AR-9598791758a5 ·
AR-a657ef5764d8 · AR-b634eae985b4 · AR-c1f03861ffdc · AR-c73a8b88fb8d ·
AR-c8121dc0789e · AR-cfad921197fc · AR-d30a1396bd93 · AR-ea91f2b2230c ·
AR-ed9bd849fb7e · AR-eec73bbbf239

**Pen command (one paste):**
```bash
for id in AR-137a79dbae09 AR-1c394e006626 AR-3521ec730fd4 AR-39307ac76191 \
  AR-3b7799cb88a0 AR-4eedf96f7ace AR-5602a344e0d6 AR-5832a927028e \
  AR-603402e9d1c4 AR-622d76f69257 AR-671223d898a2 AR-83d2c37481c7 \
  AR-842e7f4922cf AR-941d3bbb6333 AR-944b83d2fa9e AR-9598791758a5 \
  AR-a657ef5764d8 AR-b634eae985b4 AR-c1f03861ffdc AR-c73a8b88fb8d \
  AR-c8121dc0789e AR-cfad921197fc AR-d30a1396bd93 AR-ea91f2b2230c \
  AR-ed9bd849fb7e AR-eec73bbbf239; do
  python3 temple/autoresearch/operator_pen.py --mark "$id" --decision rejected \
    --note "lexical marker noise: keyword flags in proposal docs, no crossing analysis; upgrade scanner to crossing-detection before rescan" \
    --operator JM
done
```

---

## SINGLES — 4 substantive packets

### 1. AR-332110575215 — meta: "no triage workflow exists" → propose **acted**
The packet's complaint is now false: the consumption organ exists
(triage=eye · pen=hand · guard=immune, 30/30 tests green, this card is the
workflow it asked for).
```bash
python3 temple/autoresearch/operator_pen.py --mark AR-332110575215 --decision acted \
  --note "consumption organ built+tested (triage/pen/guard, 30 tests); this card is the requested workflow" --operator JM
```

### 2. AR-eee30b74e78d — 4 garden validators fail-closed but not in CI → propose **acted** (bounded task queued)
Real regression risk with a documented past incident (300-epoch sibling broke
validate_avalon.py, caught manually days later). Fix is small: one CI job
running the four validators.
```bash
python3 temple/autoresearch/operator_pen.py --mark AR-eee30b74e78d --decision acted \
  --note "bounded task queued: wire 4 garden validators into CI workflow" --operator JM
```

### 3. AR-e8d1841c6d2f — VERIFY_ALL.sh steps 3-4 structurally cannot pass (missing oracle_town/runs/ fixtures) → propose **deferred**
"Verification theater" claim is serious but the remedy needs YOUR ruling:
regenerate frozen adversarial-run fixtures (provenance question) vs. descope
steps 3-4. Not decidable by an agent.
```bash
python3 temple/autoresearch/operator_pen.py --mark AR-e8d1841c6d2f --decision deferred \
  --note "needs operator ruling: regenerate runs/ fixtures vs descope VERIFY_ALL steps 3-4" --operator JM
```

### 4. AR-1f936d1bda4b — sandbox agent adapter has no tests → propose **deferred**
True and worth doing, but below the validators-in-CI task in yield. Resurface
after it.
```bash
python3 temple/autoresearch/operator_pen.py --mark AR-1f936d1bda4b --decision deferred \
  --note "queue after garden-validators-CI: unit tests for helen_sandbox_agent_adapter" --operator JM
```

---

## After the session

```bash
python3 temple/autoresearch/ci_outbox_guard.py     # expect: 0 unconsumed, gate green
```
Marks on log: 31 ≥ 20 → **GATE 0 of the /init ranking loop unlocks** (gold set
buildable from operator truth).

Emergent finding for the loop's receipt: **26/30 of outbox volume was one
scanner defect** — generation didn't outpace consumption; noise did. Scanner
crossing-detection upgrade is the highest-yield generation-side fix.

card proposes ⊬ pen decides · 📜 ledger sleeps
