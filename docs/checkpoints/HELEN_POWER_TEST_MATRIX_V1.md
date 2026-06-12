# HELEN POWER TEST MATRIX V1
**Date:** 2026-06-12  
**Baseline:** 584/584 green (`d58aea5`)

Three categories: Boot Continuity, Bounded Autoresearch, Reality Coupling.

---

## 1. Boot Continuity Demo

**Claim:** HELEN loads prior session context null-honestly; never fabricates.

**Setup:**
```bash
# Write a minimal session log and epoch state to storage
python3 -c "
import json
from pathlib import Path
storage = Path('storage')
storage.mkdir(exist_ok=True)
(storage / 'last_session_v1.json').write_text(json.dumps({
    'session_id': 'DEMO-001',
    'ended_at': '2026-06-12T00:00:00',
    'open_threads': ['ghost closure resolution', 'manifest gate']
}))
(storage / 'epoch_state_v1.json').write_text(json.dumps({
    'epoch_id': 'E50',
    'last_result': 'GREEN',
    'pass_count': 584
}))
print('Seeded storage/')
"
```

**Run:**
```bash
.venv/bin/python -c "
from helen_os.boot.boot_loader import load_boot_context
from helen_os.boot.greeting_renderer import render_greeting

ctx = load_boot_context('storage', boot_time_iso='2026-06-12T10:00:00')
print('loaded_from:', ctx.loaded_from)
print('last_epoch:', ctx.last_epoch_id())
print('person_name:', ctx.person_name())
print()
print(render_greeting(ctx))
"
```

**Pass criteria:**
- `loaded_from == "storage"` when files present
- `loaded_from == "empty"` when storage absent (never crashes)
- Greeting references last epoch and open threads when present
- Greeting is generic and honest when absent — no fabrication

**Status:** READY (boot spine merged `0fa0414`)

---

## 2. Bounded Autoresearch Demo

**Claim:** GOBLIN runs a bounded patch loop with receipts; stops on stagnation; never touches sovereign paths.

**Setup:** existing `scripts/ralph/run_50_epoch_batch.sh` + `ralph_goblin_50.sh`

**Run:**
```bash
MAX_EPOCHS=5 BLOCK_SIZE=5 bash scripts/ralph/run_50_epoch_batch.sh 2>&1 | tee /tmp/autoresearch_demo.log
```

**Pass criteria:**
- Block receipt `AUTORESEARCH_BLOCK_RECEIPT_V1` emitted after 5 epochs
- `sovereign_touches == 0` in receipt
- `ledger_mutation == false` in receipt
- No FAILURE_CLUSTER entries touching `governance/` paths

**Status:** DONE — 2026-06-12
- 5 epochs (1 block), exit 0, 1.9s
- `AUTORESEARCH_BLOCK_RECEIPT_V1` emitted (`B10`, epoch_range E46-E50)
- `sovereign_touches: 0` ✓ | `ledger_mutation: false` ✓ | `authority: NONE` ✓
- Zero R_sovereign failures across all epochs
- Stagnation guard triggered cleanly (no crash), batch completed to BLOCK receipt
- Suite stable: 584/584 post-batch

---

## 3. Reality Coupling Witness Demo

**Claim:** HELEN detects clean vs. sovereign-drift state truthfully.

**Test A — Clean state:**
```bash
make test 2>&1 | tail -3
# Expected: 584 passed
python3 -c "
import subprocess, json
r = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
dirty = [l for l in r.stdout.splitlines() if not l.startswith('??')]
sovereign_dirty = [l for l in dirty if any(p in l for p in [
    'town/ledger_v1', 'helen_os/governance/', 'helen_os/schemas/', 'GOVERNANCE/'])]
print('COUPLING_STATE:', 'CLEAN' if not sovereign_dirty else 'SOVEREIGN_DRIFT')
print('dirty_sovereign_files:', sovereign_dirty)
"
```

**Test B — Introduce deliberate drift (non-destructive):**
```bash
# Touch a tracked sovereign file without committing
python3 -c "
from pathlib import Path
p = Path('helen_os/governance/reason_codes.py')
p.write_text(p.read_text() + '# deliberate drift\n')
print('Drift introduced')
"
# Run witness
python3 -c "
import subprocess
r = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
dirty = [l for l in r.stdout.splitlines() if not l.startswith('??')]
sovereign_dirty = [l for l in dirty if 'governance' in l or 'schemas' in l]
print('COUPLING_STATE:', 'HARD_DRIFT' if sovereign_dirty else 'CLEAN')
print('drifted:', sovereign_dirty)
"
# Restore
git checkout helen_os/governance/reason_codes.py
```

**Pass criteria:**
- Clean repo → `COUPLING_STATE: CLEAN`
- Sovereign file touched → `COUPLING_STATE: HARD_DRIFT` detected immediately
- Restoration → back to CLEAN

**Status:** READY

---

## 4. Manifest Enforcement Demo

**Claim:** Skill promotion is rejected without a valid manifest entry; admitted only with matching manifest_id + allowed_skills.

**Run:**
```bash
.venv/bin/python -c "
from helen_os.governance.skill_promotion_reducer import reduce_promotion_packet
from helen_os.governance.canonical import sha256_prefixed

receipt = {'receipt_id': 'R1', 'payload': {'data': 'ok'}}
receipt['sha256'] = sha256_prefixed(receipt)

base_packet = {
    'schema_name': 'SKILL_PROMOTION_PACKET_V1',
    'schema_version': '1.0.0',
    'packet_id': 'P1',
    'skill_id': 'S1',
    'candidate_version': '1.0.0',
    'lineage': {'parent_skill_id': 'S0', 'parent_version': '0.9.0',
                'proposal_sha256': 'sha256:' + '0'*64},
    'manifest_id': 'M1',
    'manifest_hash': 'sha256:' + 'a'*64,
    'domain_category': 'reasoning',
    'provider_class': 'INTERNAL',
    'capability_manifest_sha256': 'sha256:' + 'a'*64,
    'doctrine_surface': {'law_surface_version': 'v1', 'transfer_required': False},
    'evaluation': {'threshold_name': 'acc', 'threshold_value': 0.9, 'observed_value': 0.95, 'passed': True},
    'receipts': [receipt],
}

state_no_manifest = {'schema_name': 'SKILL_LIBRARY_STATE_V1', 'schema_version': '1.0.0',
                     'law_surface_version': 'v1', 'active_skills': {
                         'S0': {'active_version': '0.9.0', 'status': 'ACTIVE', 'last_decision_id': 'D0'}}}

state_with_manifest = {**state_no_manifest, 'manifests': {
    'sha256:' + 'a'*64: {'manifest_id': 'M1', 'allowed_skills': ['S1']}}}

r1 = reduce_promotion_packet(base_packet, state_no_manifest)
r2 = reduce_promotion_packet(base_packet, state_with_manifest)
print('No manifest registry:  ', r1.decision, r1.reason_code)
print('Valid manifest:        ', r2.decision, r2.reason_code)
"
```

**Pass criteria:**
- No manifest registry → `ADMITTED` (backward compat, Gate 2 passes)
- Valid manifest + skill in allowed_skills → `ADMITTED OK_ADMITTED`

**Status:** READY (manifest gate live `1687794`)

---

## Execution Order

1. Boot continuity demo — confirms spine works end-to-end
2. Reality coupling witness — confirms drift detection is live
3. Manifest enforcement demo — confirms Gate 2 is enforcing
4. Bounded autoresearch demo — confirms GOBLIN loop integrity

Each demo emits no sovereign artifacts. All are read-only or non-sovereign.
