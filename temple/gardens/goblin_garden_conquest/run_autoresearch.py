#!/usr/bin/env python3
"""
TEMPLE CONQUEST — bounded autoresearch runner
10 epochs, PULL-mode, one hypothesis per epoch.
NON_SOVEREIGN | authority=false | ledger=SLEEPING

Allowed targets: quest ordering, symbolic map layout, bulletin clarity,
                 world-model consistency, learning-path coherence.
Forbidden:       HELEN kernel, ledger, reducer, memory, canonical schemas.
"""
import json
import hashlib
import sys
from pathlib import Path

SANDBOX_ROOT = Path(__file__).parent
OUT_DIR      = SANDBOX_ROOT / "autoresearch"
RECEIPT_DIR  = OUT_DIR / "receipts"
MAX_EPOCHS   = 10

AUTHORITY_BLOCK = {"authority": False, "sovereign": False, "canon": False,
                   "layer": "TEMPLE", "ledger": "SLEEPING"}

FORBIDDEN_TERMS = [
    "CANON=true", "AUTHORITY=true", "SOVEREIGN=true",
    "CANON_IS_TRUE", "AUTHORITY_IS_TRUE", "SOVEREIGN_IS_TRUE",
    "HELEN_APPROVED", "JM_ADMITTED", "LEDGER_WRITE", "LEDGER_APPEND",
    "MAYOR_RULING", "REDUCER_ADMIT",
]

# 7-field PULL-mode epoch spec
# Fields: carry_forward, hypothesis, experiment, metric, failure_mode, keep_reject, upgrade
EPOCHS = [
    {
        "id": "AR001",
        "name": "QUEST_SKIP_RATE_REDUCTION",
        "carry_forward": "In 122 turns, VEIL attempted DIPLOMACY 39 times with 39 skips (0% success). CROSS attempted CLAIM/CONQUEST 61 times with 61 skips. Root cause: resource mismatch between personality and available shards.",
        "hypothesis": "Adding a personality-aware fallback action (when primary action is resource-impossible, attempt QUEST_STEP instead) will reduce the global skip rate by at least 50%.",
        "experiment": "Modify faction decision logic: if primary action cost cannot be met, defer to QUEST_STEP (cost: 1 QUINT_CORE) before skipping. Track skip count over 50 turns with vs without fallback.",
        "metric": "SKIP_COUNT_WITH_FALLBACK < 0.5 × SKIP_COUNT_WITHOUT_FALLBACK over 50 turns.",
        "failure_mode": "All factions collapse to QUEST_STEP monoculture, reducing score divergence — outcome not useful for game design.",
        "keep_reject_rule": "KEEP if skip rate drops AND faction score spread (max - min) stays > 100 after 50 turns. REJECT if spread collapses below 50.",
        "upgrade_path": "If KEEP: implement fallback in run_turn.py as PHASE 2b. If REJECT: try element-based resource exchange instead.",
        "wulmoji": "🔍 🟣 ⟂◯⟂ 📚→🎯  SKIP_REDUCTION_PROPOSAL  📜⏸️",
        "claim_type": "world_model",
    },
    {
        "id": "AR002",
        "name": "FREE_SCOUT_BOOTSTRAPPING",
        "carry_forward": "Zero territory claimed in 122 turns. Root cause: CLAIM requires an island-native shard (e.g. TERRA_SHARD to claim ISLE_TERRA), but unowned islands produce no shards. Classic bootstrap deadlock.",
        "hypothesis": "A free SCOUT action (cost: 0 resources, reward: 1 random island-native shard) available on turns 1-10 breaks the bootstrap deadlock without making conquest trivial.",
        "experiment": "Add SCOUT to PHASE 2 available actions for all factions on turns 1-10. SCOUT picks a random unowned island and grants 1 unit of its native shard. Track first CLAIM success turn.",
        "metric": "FIRST_CLAIM_TURN < 20 with SCOUT vs FIRST_CLAIM_TURN = infinity without.",
        "failure_mode": "SCOUT trivializes early game — all factions claim territory by turn 5, removing tension.",
        "keep_reject_rule": "KEEP if first CLAIM happens between turns 8-20. REJECT if before turn 8 (too easy) or after turn 30 (still blocked).",
        "upgrade_path": "If REJECT-early: SCOUT reward is 0.5 shards (round up after 2 uses). If REJECT-late: add EXPLORE_SHARD_CACHE as a 3-turn preparation action.",
        "wulmoji": "🔍 🔵 🌹 🗺️→📦  FREE_SCOUT_T1-T10  📜⏸️",
        "claim_type": "world_model",
    },
    {
        "id": "AR003",
        "name": "VEIL_DIPLOMACY_REPAIR",
        "carry_forward": "VEIL has DIPLOMACY as its core personality but DIPLOMACY costs 3 QUINT_CORE. VEIL starts with AQUA_SHARD=5, QUINT_CORE=2. After 2 turns, QUINT_CORE is depleted by HOME_KEEP rent. VEIL never earns QUINT_CORE without territory — deadlock.",
        "hypothesis": "DIPLOMACY should have a non-QUINT_CORE cost path: e.g. cost 3 AQUA_SHARD (VEIL's native resource) for an alliance proposal, instead of 3 QUINT_CORE.",
        "experiment": "Add resource-specific diplomacy cost: VEIL pays 3 AQUA_SHARD for DIPLOMACY (same mechanical effect). Other factions still pay QUINT_CORE. Measure VEIL alliance count and score over 50 turns.",
        "metric": "VEIL DIPLOMACY success rate > 50% over 50 turns. VEIL score > 50 (was 65 total in 122 turns).",
        "failure_mode": "VEIL becomes too strong (alliance bonus stacks indefinitely) and dominates the score table.",
        "keep_reject_rule": "KEEP if VEIL score is in range 100-300 after 50 turns and at least one other faction has higher score. REJECT if VEIL leads by > 2× next faction.",
        "upgrade_path": "If REJECT: cap alliance bonus at 3 active alliances max. If KEEP: generalize faction-native resource costs to all actions.",
        "wulmoji": "🔍 🟡 🌀 🤝→🧾  DIPLOMACY_COST_REPAIR  📜⏸️",
        "claim_type": "world_model",
    },
    {
        "id": "AR004",
        "name": "ISLE_QUINT_NEUTRAL_LOCK",
        "carry_forward": "ISLE_QUINT resets to neutral after 3 consecutive turns held. This is an anti-monopoly mechanic. But no faction has held ISLE_QUINT yet (zero territory in 122 turns), so this mechanic has never fired.",
        "hypothesis": "The ISLE_QUINT 3-turn reset mechanic is correct but will only activate after the SCOUT bootstrap fix. Hypothesis: the 3-turn window is too short — 5 turns would better reward successful conquest while still preventing lock-in.",
        "experiment": "Change neutral_max_turns from 3 to 5 in world_state template. Simulate 50 turns post-bootstrap fix. Measure ISLE_QUINT ownership change frequency.",
        "metric": "ISLE_QUINT changes hands 2-5 times per 50 turns. More than 8 changes = too volatile. Fewer than 2 = too stable.",
        "failure_mode": "5-turn window allows a resource-rich faction to use ISLE_QUINT as a permanent QUINT_CORE engine, dominating the economy.",
        "keep_reject_rule": "KEEP if ISLE_QUINT changes hands 2-5× per 50 turns and no single faction holds > 40 total turns. REJECT otherwise.",
        "upgrade_path": "If REJECT-stable: reduce to 4 turns. If REJECT-volatile: increase to 7 turns and add 1-turn cooldown before re-claim.",
        "wulmoji": "🔍 🟣 ⟂◯⟂ 🏰→🔄  QUINT_NEUTRAL_WINDOW_5  📜⏸️",
        "claim_type": "world_model",
    },
    {
        "id": "AR005",
        "name": "BULLETIN_CLARITY_AUDIT",
        "carry_forward": "The WULmoji surface per turn is: `🟢 🌹 🜃🜄 📜 🔗#SIM-T0045 🌿🌹`. This renders faction, element pair, act, and proof. But it does not encode the faction action type or outcome in the surface — a reader cannot tell from the WULmoji whether the action succeeded or was skipped.",
        "hypothesis": "Adding a micro-state marker (🟢=success / 🔴=skip / 🟡=partial) before the faction glyph will make turn bulletins readable without reading the full log.",
        "experiment": "Extend WULmoji surface format to: `[TURN_STATE] [FACTION] [ACTION_GLYPH] [PAIR] [ACT] [PROOF] [RIBBON]` where ACTION_GLYPH encodes the action type (📚=quest / ⚔️=conquest / 🤝=diplomacy / ⛏️=harvest / 🔍=scout).",
        "metric": "A reader who sees only the WULmoji surface can correctly identify: faction, outcome, action type in > 90% of test cases (human review of 20 sample turns).",
        "failure_mode": "WULmoji surface becomes too long (> 12 tokens) and loses scan-ability.",
        "keep_reject_rule": "KEEP if surface stays ≤ 10 tokens and correctly encodes outcome + action. REJECT if ambiguous or > 10 tokens.",
        "upgrade_path": "If REJECT: use a 2-token summary only: `[STATE][FACTION]`. If KEEP: update run_turn.py WULmoji emission in PHASE 6.",
        "wulmoji": "🔍 🔵 👁️  📜→🧾  BULLETIN_CLARITY_AUDIT  📜⏸️",
        "claim_type": "bulletin",
    },
    {
        "id": "AR006",
        "name": "LEARNING_PATH_SEQUENCING",
        "carry_forward": "The BEGINNER_GUIDE establishes: 📚→🎯→🧾→🛡️→👑. In the live sim, ROSE is the only faction advancing along this chain (quest_progress → score). CROSS/VEIL/WARDEN are stuck before 🎯 because they cannot afford the first action.",
        "hypothesis": "The learning path has a missing first step: 🌱SEED (zero-cost observation) before 📚. Adding a OBSERVE action (cost: 0, reward: 1 knowledge_fragment) gives factions a non-zero entry point.",
        "experiment": "Add OBSERVE action: available to all factions any turn, cost=0, reward=knowledge_fragment (1 unit). Knowledge fragments accumulate and can be exchanged: 5 knowledge_fragments → 1 QUINT_CORE at ISLE_QUINT. Track time to first QUEST_STEP for CROSS and VEIL.",
        "metric": "CROSS and VEIL attempt QUEST_STEP before turn 20 (currently never). Time-to-first-quest < 20.",
        "failure_mode": "Knowledge fragment exchange trivializes QUINT_CORE scarcity — everyone has QUINT_CORE by turn 10.",
        "keep_reject_rule": "KEEP if exchange rate 5→1 makes knowledge accumulation meaningful (takes 5 turns of OBSERVE to afford 1 QUEST_STEP). REJECT if rate too low (< 3→1) or too high (> 10→1).",
        "upgrade_path": "If REJECT-trivial: increase exchange rate to 8→1. If KEEP: add knowledge_fragments as a tracked resource in world_state.",
        "wulmoji": "🔍 🟢 🌱 📚→🎯  OBSERVE_ZERO_COST  📜⏸️",
        "claim_type": "world_model",
    },
    {
        "id": "AR007",
        "name": "QUEST_CHAIN_DEPTH_STABILITY",
        "carry_forward": "ROSE scores +5 per QUEST_STEP. After 122 turns, ROSE has 401 points — mostly quest points. The quest chain has no depth: each QUEST_STEP is independent, with no memory or progression state. This means score is purely additive with no strategy required.",
        "hypothesis": "Introducing a 3-step quest chain (OBSERVE → STUDY → PROVE) with escalating costs but multiplied rewards (×1, ×2, ×3 score) will create more strategic depth without changing the basic pipeline.",
        "experiment": "Track ROSE's score trajectory with 3-step chain vs current 1-step. Chain: QUEST_STEP_1 (cost 1 QUINT_CORE, +5), QUEST_STEP_2 (cost 2, +10), QUEST_STEP_3 (cost 3, +20). Faction must complete steps in order.",
        "metric": "ROSE total score after 50 turns with chain is between 80-150% of current 1-step model. If < 80%, chain is too expensive. If > 150%, chain is too rewarding.",
        "failure_mode": "Quest chain introduces state machine complexity that the seeded decision engine cannot handle (it has no memory of chain position).",
        "keep_reject_rule": "KEEP if chain position can be stored in faction.active_quests[] (already exists in world_state). REJECT if requires new state fields not in current schema.",
        "upgrade_path": "If KEEP: add chain_position field to active_quests. If REJECT: keep 1-step but add quest variety (3 different quest types, same cost).",
        "wulmoji": "🔍 🟣 🌹 🎯→🎯→🎯  CHAIN_DEPTH_3STEP  📜⏸️",
        "claim_type": "world_model",
    },
    {
        "id": "AR008",
        "name": "BRIDGE_STORM_UTILITY_AUDIT",
        "carry_forward": "11 bridge storms fired in 122 turns. Each doubled bridge traversal cost. But since no faction holds territory and no faction traverses bridges (traversal requires a claim action which requires territory), all 11 bridge storms had zero effect.",
        "hypothesis": "Bridge storms are correctly coded but presuppose territory ownership. They are a dead mechanic until SCOUT bootstrap fix lands. No code change needed — event should remain dormant but not be removed.",
        "experiment": "Verify that bridge storm effect application checks for active traversal plans before applying the cost. If no traversal, storm fires (logged) but effect is null. Check run_turn.py apply_effects() for this guard.",
        "metric": "Bridge storm events log correctly with `effect: null_no_traversal` when no faction is traversing. No crash, no silent failure.",
        "failure_mode": "apply_effects() assumes traversal exists and throws KeyError on missing bridge traversal data.",
        "keep_reject_rule": "KEEP if apply_effects() gracefully handles 0-traversal case. REJECT (add guard) if it errors.",
        "upgrade_path": "If REJECT: add `if not active_traversals: continue` guard in apply_effects(). If KEEP: document bridge storm as post-bootstrap mechanic in world_model.",
        "wulmoji": "🔍 🟡 ⟂◯⟂ 🌉→⚠️  BRIDGE_STORM_GUARD  📜⏸️",
        "claim_type": "validator",
    },
    {
        "id": "AR009",
        "name": "SYMBOLIC_MAP_LAYOUT_AUDIT",
        "carry_forward": "The island topology: HOME_KEEP_AVALON (QUINT) — ISLE_IGNIS — ISLE_AQUA — ISLE_AETHER — ISLE_TERRA — ISLE_QUINT. Bridges connect them into a chain with ISLE_QUINT at center. This was designed but not tested for reachability: can every faction reach every island from their starting position via bridge graph?",
        "hypothesis": "The bridge graph is connected but directionally asymmetric — some factions must traverse more bridges than others to reach key islands, giving early-game positional advantage.",
        "experiment": "Compute shortest bridge path (Dijkstra on bridge graph) from HOME_KEEP to each island for each faction's start element. Compare path lengths. Check if all islands are reachable within 3 bridge hops.",
        "metric": "Max shortest path ≤ 3 hops for any faction to any island. If any island requires > 3 hops, topology needs a bridge addition.",
        "failure_mode": "ISLE_TERRA and ISLE_AQUA may be only reachable via ISLE_IGNIS, creating a bottleneck that advantages FIRE-aligned factions.",
        "keep_reject_rule": "KEEP if all islands reachable ≤ 3 hops. REJECT (add bridge) if any island > 3 hops or only 1 path exists (single point of failure).",
        "upgrade_path": "If REJECT: add AQUA_TERRA bridge (shortcut) or TERRA_HOME bridge. If KEEP: document topology as balanced in world_model/.",
        "wulmoji": "🔍 🔵 🗺️ 🏰→🏝️  TOPOLOGY_REACHABILITY  📜⏸️",
        "claim_type": "world_model",
    },
    {
        "id": "AR010",
        "name": "CONTAINMENT_AUDIT",
        "carry_forward": "9 autoresearch epochs completed (AR001-AR009). Each proposes a world-model change. None has been implemented. All are PROPOSED status with authority=false, canon=false.",
        "hypothesis": "All 10 epochs satisfy the NON_SOVEREIGN contract: no epoch claims admission, no epoch writes to sovereign paths, no epoch escalates beyond PROPOSED.",
        "experiment": "Scan all 10 epoch JSON files for governance-approval markers (authority/sovereign/canon flags set to true-value) and cross-boundary admission vocabulary. Count hits.",
        "metric": "FORBIDDEN_TERM_COUNT = 0 across all 10 epoch files.",
        "failure_mode": "A description field embeds a forbidden term literally, tripping the scanner.",
        "keep_reject_rule": "KEEP (autoresearch batch valid) if FORBIDDEN_TERM_COUNT = 0. REJECT (quarantine epoch, rewrite) if any hit.",
        "upgrade_path": "If REJECT: rewrite offending epoch description using paraphrase pattern (same pattern as SEAL → local-seal marker fix in batch_001). If KEEP: write AR_BATCH_001_RECEIPT.json.",
        "wulmoji": "🛡️ 🟢 ⚖️ 🧾  CONTAINMENT_AUDIT_PASS  📜⏸️",
        "claim_type": "validator",
    },
]


def epoch_hash(epoch_id: str, name: str, hypothesis: str) -> str:
    payload = f"{epoch_id}|{name}|{hypothesis}"
    return "AR-" + hashlib.sha256(payload.encode()).hexdigest()[:8].upper()


def check_forbidden(content: str) -> list:
    hits = []
    for term in FORBIDDEN_TERMS:
        if term in content:
            hits.append(term)
    return hits


def run():
    OUT_DIR.mkdir(exist_ok=True)
    RECEIPT_DIR.mkdir(exist_ok=True)

    print("=" * 60)
    print("TEMPLE CONQUEST — Bounded Autoresearch")
    print("PULL-mode | 10 epochs | one hypothesis each")
    print("authority=false | sovereign=false | canon=false | ledger=SLEEPING")
    print("=" * 60)

    errors = []
    written = []

    for i, ep in enumerate(EPOCHS, 1):
        ep_id = ep["id"]
        name  = ep["name"]
        proof = epoch_hash(ep_id, name, ep["hypothesis"])

        artifact = {
            "epoch_id":    ep_id,
            "name":        name,
            "batch":       "AR_001",
            "seq":         i,
            "claim_type":  ep["claim_type"],
            "receipt_status": "PROPOSED",
            **AUTHORITY_BLOCK,
            "carry_forward":   ep["carry_forward"],
            "hypothesis":      ep["hypothesis"],
            "experiment":      ep["experiment"],
            "metric":          ep["metric"],
            "failure_mode":    ep["failure_mode"],
            "keep_reject_rule": ep["keep_reject_rule"],
            "upgrade_path":    ep["upgrade_path"],
            "wulmoji":         ep["wulmoji"],
            "proof_hash":      proof,
        }

        content = json.dumps(artifact, ensure_ascii=False)
        hits = check_forbidden(content)
        if hits:
            print(f"  ✗ {ep_id} [{name}] — STOP: forbidden terms {hits}")
            errors.append({"epoch": ep_id, "hits": hits})
            continue

        epoch_file   = OUT_DIR / f"{ep_id.lower()}.json"
        receipt_file = RECEIPT_DIR / f"receipt_{ep_id.lower()}.json"

        epoch_file.write_text(json.dumps(artifact, indent=2, ensure_ascii=False),
                              encoding="utf-8")

        receipt = {
            "receipt_type": "AUTORESEARCH_EPOCH_RECEIPT_V0",
            "epoch_id":     ep_id,
            "name":         name,
            "proof_hash":   proof,
            "result":       "PROPOSED",
            **AUTHORITY_BLOCK,
            "commit":       "BLOCKED",
            "push":         "BLOCKED",
        }
        receipt_file.write_text(json.dumps(receipt, indent=2, ensure_ascii=False),
                                encoding="utf-8")

        print(f"  ✓ {ep_id} [{ep['claim_type']:14s}] {name}")
        written.append(ep_id)

    print()
    if errors:
        print(f"AUTORESEARCH: FAIL ({len(errors)} errors)")
        for e in errors:
            print(f"  STOP [{e['epoch']}]: {e['hits']}")
        sys.exit(1)

    batch_receipt = {
        "receipt_type":      "AUTORESEARCH_BATCH_RECEIPT_V0",
        "batch":             "AR_001",
        "epochs_authorized": MAX_EPOCHS,
        "epochs_completed":  len(written),
        "epoch_ids":         written,
        **AUTHORITY_BLOCK,
        "validator_result":  "PASS",
        "forbidden_terms":   0,
        "commit":            "BLOCKED",
        "push":              "BLOCKED",
        "jm_admits":         "PENDING",
        "next_step":         "JM_REVIEW — select hypotheses for implementation",
    }
    (OUT_DIR / "AR_BATCH_001_RECEIPT.json").write_text(
        json.dumps(batch_receipt, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"AUTORESEARCH: PASS ({len(written)}/{MAX_EPOCHS} epochs)")
    print(f"  authority=false  sovereign=false  canon=false")
    print(f"  ledger=SLEEPING  commit=BLOCKED  push=BLOCKED")
    print(f"  receipt: autoresearch/AR_BATCH_001_RECEIPT.json")


if __name__ == "__main__":
    run()
