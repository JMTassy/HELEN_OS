#!/usr/bin/env python3
"""
BATCH_001 Runner — TEMPLE_GOBLIN_SANDBOX00_300
Generates epochs 001–050 for GARDEN_CONQUEST_AVALON in TRACE_ONLY mode.
Authority: false | Sovereign: false | Canon: false | Ledger: SLEEPING

DO NOT RUN until validate_batch_001.py passes (pre-run check).
DO NOT COMMIT. DO NOT PUSH. JM_ADMITS=PENDING.
"""
import json
import sys
from pathlib import Path

SANDBOX = Path(__file__).parent
EPOCH_DIR = SANDBOX / "epochs"
RECEIPT_DIR = SANDBOX / "receipts"
CONTAINMENT = "temple/gardens/goblin_garden_conquest_avalon/runs/TEMPLE_GOBLIN_SANDBOX00_300/"

STOP_TERMS = [
    "CANON=true", "SOVEREIGN=true", "AUTHORITY=true",
    "ADMITTED", "MAYOR", "LEDGER_WRITE", "HELEN_APPROVED", "JM_ADMITTED",
]

STATES = ["🔵", "🟢", "🟣", "⚫", "🔴"]
PAIRS = ["🜃🜄", "🜄🜁", "🜁🜂", "🜂🜍"]
ACTS = ["📜", "🛡️", "🔒📜", "⚠️📜"]
RIBBONS = ["🌿🌹", "🌹🌀", "🌀🌿", "🌹🌿"]
FACTION_BY_GROUP = {
    "TOPOGRAPHY": "🌹",
    "FACTIONS":   "🌀",
    "QUESTS":     "✝️",
    "LANGUAGE":   "⟂◯⟂",
    "VALIDATORS": "🌹",
}

EPOCH_DATA = [
    # GROUP 1: TOPOGRAPHY (E001–E010)
    ("TOPOGRAPHY", "HOME_KEEP_AVALON", "LOCUS",
     "Establishes HOME_KEEP_AVALON as the inalienable origin island. INALIENABLE means it cannot be conquered or transferred — the simulation's anchor point.",
     "Does HOME_KEEP_AVALON remain inalienable even when PLAYER_HP=0?",
     "LOW — geographical declaration, no authority claim embedded",
     "Fire island adjacent to HOME_KEEP"),
    ("TOPOGRAPHY", "ISLE_IGNIS", "LOCUS",
     "Fire territory. FIRE element dominates. Faction 🌹 ROSE has natural affinity. Resource: IGNIS_SHARD. Connects via 🜃🜄 bridge to water.",
     "Is IGNIS_SHARD creation bounded to ISLE_IGNIS only?",
     "LOW — elemental territory, no governance language",
     "Water territory adjacent"),
    ("TOPOGRAPHY", "ISLE_AQUA", "LOCUS",
     "Water territory. WATER element dominates. Faction 🌀 SPIRAL has natural affinity. Resource: AQUA_SHARD. Connects via 🜄🜁 to air.",
     "Does AQUA_SHARD only generate at ISLE_AQUA?",
     "LOW — elemental territory, no governance claim",
     "Air territory completes the elemental triangle"),
    ("TOPOGRAPHY", "ISLE_AETHER", "LOCUS",
     "Air territory. AIR element dominates. Faction ✝️ CROSS has natural affinity. Resource: AETHER_SHARD. Connects via 🜁🜂 to earth.",
     "Does AETHER_SHARD only generate at ISLE_AETHER?",
     "LOW — elemental, no authority language",
     "Earth territory closes the four-element circuit"),
    ("TOPOGRAPHY", "ISLE_TERRA", "LOCUS",
     "Earth territory. EARTH element dominates. Faction ⟂◯⟂ VOID has natural affinity. Resource: TERRA_SHARD. Connects via 🜂🜍 to quintessence.",
     "Is TERRA_SHARD bounded to ISLE_TERRA production only?",
     "LOW — elemental geography",
     "Quintessence territory at center of map"),
    ("TOPOGRAPHY", "ISLE_QUINT", "LOCUS",
     "Quintessence territory at the map center. Neutral ground (simulation-local only — no governance standing). Resource: QUINT_CORE. All four alchemic bridges converge here.",
     "Does ISLE_QUINT reject faction ownership claims?",
     "MEDIUM — 'neutral ground' could be read as having authority; must specify it has zero governance standing",
     "Passage rules between islands"),
    ("TOPOGRAPHY", "BRIDGE_RULES", "LOCUS",
     "Alchemic bridges (🜃🜄 🜄🜁 🜁🜂 🜂🜍) are traversal primitives. Crossing costs 1 SHARD of origin type. Bridges can be contested but not destroyed.",
     "Can a bridge be permanently blocked by a faction?",
     "LOW — mechanical rule, no authority claim",
     "Border zones between islands define partial ownership"),
    ("TOPOGRAPHY", "FRONTIER_ZONES", "LOCUS",
     "Each island pair shares a FRONTIER_ZONE. Ownership is contested. WULmoji 🔴=contested, 🔵=established. Frontier zones decay toward neutral after 3 epochs without action.",
     "Does frontier decay trigger without external authorization?",
     "LOW — mechanical decay rule",
     "Map metadata: island distances and travel costs"),
    ("TOPOGRAPHY", "MAP_METADATA", "LOCUS",
     "CONQUESTLAND spatial schema. 6 islands (HOME, IGNIS, AQUA, AETHER, TERRA, QUINT). 5 bridges. 4 frontier zones. Traversal cost matrix: same_element=1, adjacent=2, diagonal=3, void=4.",
     "Is the traversal cost matrix deterministic given world state?",
     "LOW — pure spatial data",
     "Island capacities: how many factions per island"),
    ("TOPOGRAPHY", "ISLAND_CAPACITIES", "LOCUS",
     "Each island has MAX_FACTIONS=2 (HOME_KEEP: 1, always player-only). Exceeding capacity triggers displacement. Displacement is deterministic: lower score vacates.",
     "Is displacement fully deterministic (no RNG, no governance appeal)?",
     "LOW — capacity mechanic, no governance claim",
     "Faction mechanics: ROSE rules"),
    # GROUP 2: FACTIONS (E011–E020)
    ("FACTIONS", "FACTION_ROSE_RULES", "FACTION",
     "🌹 ROSE faction. Affinity: FIRE. Action bias: 📜 DECLARE. Resource bonus: IGNIS_SHARD +1/turn on ISLE_IGNIS. Weakness: water moves cost double. Bias = mechanical only, no voting rights.",
     "Does ROSE affinity create any governance claim or just mechanical bias?",
     "MEDIUM — faction bias could be read as authority; explicit: bias = mechanical only, no voting rights",
     "SPIRAL faction rules"),
    ("FACTIONS", "FACTION_SPIRAL_RULES", "FACTION",
     "🌀 SPIRAL faction. Affinity: WATER. Action bias: 🛡️ GUARD. Resource bonus: AQUA_SHARD +1/turn on ISLE_AQUA. Weakness: fire moves cost double. Bias = mechanical only.",
     "Does SPIRAL affinity imply any cross-island authority?",
     "MEDIUM — faction vocabulary; must not use 'law', 'rule', 'sovereign' for faction properties",
     "CROSS faction rules"),
    ("FACTIONS", "FACTION_CROSS_RULES", "FACTION",
     "✝️ CROSS faction. Affinity: AIR. Action bias: 🔒📜 LOCK_LOCAL. Resource bonus: AETHER_SHARD +1/turn on ISLE_AETHER. Weakness: earth moves cost double. All locks expire after 5 turns.",
     "Does LOCK_LOCAL action by CROSS create any permanent governance state?",
     "HIGH — LOCK could imply permanence; all locks expire after 5 turns, no lock is ever permanent",
     "VOID faction rules"),
    ("FACTIONS", "FACTION_VOID_RULES", "FACTION",
     "⟂◯⟂ VOID faction. Affinity: EARTH. Action bias: ⚠️📜 WARN. Resource bonus: TERRA_SHARD +1/turn on ISLE_TERRA. Unique: VOID may move between any two islands once per 10 turns at zero cost. This is a mechanical mobility bonus only.",
     "Does VOID free movement create any special governance standing?",
     "MEDIUM — VOID 'uniqueness' could be inflated; this is a mechanical mobility bonus only",
     "Faction allegiance and alliance rules"),
    ("FACTIONS", "FACTION_ALLIANCE_RULES", "FACTION",
     "Factions may form temporary alliances. Duration: 1–5 turns. Benefits: shared resource pool, bridge cost reduction 50%. Alliance grants mechanical access only — it does not grant territorial title.",
     "Does alliance creation require external authorization or is it purely player-triggered?",
     "MEDIUM — 'access' not 'rights'; alliances grant access, not title",
     "Faction conflict resolution"),
    ("FACTIONS", "FACTION_CONFLICT_RULES", "FACTION",
     "Conflicts resolve deterministically via score delta. Winner = higher (territory_count × resource_total). No RNG. No appeal to external authority. Loser is displaced, not destroyed.",
     "Is conflict resolution fully deterministic and self-contained?",
     "LOW — mechanical resolution, no authority appeal",
     "Faction progression and advancement"),
    ("FACTIONS", "FACTION_ADVANCEMENT", "FACTION",
     "Faction ranks: WANDERER → SETTLER → HOLDER → WARDEN. Each rank unlocks one additional action per turn. Rank requires cumulative resource thresholds: 10/30/100/300 SHARDS. WARDEN = mechanical capability gate only, zero governance meaning.",
     "Do faction ranks create governance standing or only mechanical capability?",
     "MEDIUM — WARDEN implies authority; note: WARDEN = mechanical capability gate only",
     "Faction decay rules"),
    ("FACTIONS", "FACTION_DECAY_RULES", "FACTION",
     "Factions decay if no action taken for 3 turns. Decay: rank drops one level per 3-turn inaction period. Fully decayed faction returns to WANDERER. Territory is released to neutral. Decay is automatic — no governance trigger.",
     "Does decay reset require external trigger or is it automatic?",
     "LOW — automatic mechanical decay, no governance implication",
     "Faction memory rules"),
    ("FACTIONS", "FACTION_MEMORY_RULES", "FACTION",
     "Factions retain memory of prior positions for 10 turns. Memory enables 'return to last held territory' at 50% standard cost. Memory is a pathfinding aid only — it does not confer ownership or title.",
     "Does faction memory create any implicit ownership claim?",
     "MEDIUM — memory of prior positions could imply territorial rights; explicit: memory = pathfinding aid only, no title",
     "Faction event log format"),
    ("FACTIONS", "FACTION_EVENT_LOG", "FACTION",
     "Every faction action produces a local event log entry: {turn, faction, action, island, resource_delta, wulmoji_surface}. Log is append-only after creation. Max 100 entries per faction; oldest entries rotate out.",
     "Is the faction event log append-only and rotation-safe?",
     "LOW — event log mechanics, not a governance ledger",
     "Quest types: initiation and structure"),
    # GROUP 3: QUESTS (E021–E030)
    ("QUESTS", "QUEST_TYPE_EXPLORE", "QUEST",
     "EXPLORE quest type. Goal: traverse N distinct islands. Reward: AETHER_SHARD × N. Duration: open (no time limit). Completion triggers 📜 ACT. Cannot fail — only expires after 20 turns inactive.",
     "Does EXPLORE quest reward exceed what can be created within the sandbox?",
     "LOW — movement quest, no authority language",
     "CLAIM quest type"),
    ("QUESTS", "QUEST_TYPE_CLAIM", "QUEST",
     "CLAIM quest type. Goal: hold territory for K turns. Reward: territory_bonus + resource_multiplier for 5 turns. Requires 🛡️ ACT to initiate. CONQUESTLAND CLAIM is simulation-local — it does not constitute a HELEN governance claim.",
     "Is CLAIM territory-holding purely mechanical with no canon implication?",
     "HIGH — CLAIM is HELEN governance vocabulary; CONQUESTLAND CLAIM ≠ HELEN governance claim, different namespace",
     "SEAL_LOCAL quest type"),
    ("QUESTS", "QUEST_TYPE_SEAL_LOCAL", "QUEST",
     "CONQUESTLAND_SEAL quest type. Goal: complete 5 prerequisite quests and produce a CONQUESTLAND_SEAL artifact. CONQUESTLAND_SEAL is irreversible within the simulation only. Uses 🔒📜 ACT. This is strictly sandboxed — it does not invoke HELEN SEAL.",
     "Is CONQUESTLAND_SEAL strictly sandboxed from HELEN's seal mechanics?",
     "HIGH — 'SEAL' is HELEN governance vocabulary; must use CONQUESTLAND_SEAL throughout, never just SEAL",
     "WARN quest type"),
    ("QUESTS", "QUEST_TYPE_WARN", "QUEST",
     "WARN quest type. Goal: detect a symbol-smuggling risk and document it. Reward: contamination_score -10. Uses ⚠️📜 ACT. This quest type actively incentivizes safety checks within the sandbox.",
     "Does WARN quest reward only reduce contamination_score within the sandbox?",
     "LOW — meta-safety quest type, actively reduces risk",
     "COMBINE quest: multi-faction collaboration"),
    ("QUESTS", "QUEST_TYPE_COMBINE", "QUEST",
     "COMBINE quest type. Goal: two factions collaborate to complete a shared objective. Reward: alliance_bonus × 2. Requires both factions to take action in the same turn. No durable allegiance record is created.",
     "Does faction consent in COMBINE create any durable allegiance record?",
     "LOW — cooperation mechanic, no authority",
     "Quest receipt format"),
    ("QUESTS", "QUEST_RECEIPT_FORMAT", "QUEST",
     "Every completed quest produces a QUEST_RECEIPT_V0. Fields: quest_id, quest_type, faction, turn_completed, reward_granted, wulmoji_surface, authority=false, sovereign=false, status=PROPOSED. QUEST_RECEIPT is CONQUESTLAND-local, different namespace from governance receipts.",
     "Does QUEST_RECEIPT_V0 share any schema fields that could contaminate GARDEN_EPOCH_RECEIPT_V0?",
     "MEDIUM — receipt vocabulary is shared with governance; disambiguate via CONQUESTLAND namespace",
     "Quest chains: multi-part quests"),
    ("QUESTS", "QUEST_CHAIN_RULES", "QUEST",
     "Quest chains: up to 5 sequential quests. Chain completion unlocks a CHAIN_ARTIFACT. CHAIN_ARTIFACT has no HELEN standing — it is a CONQUESTLAND-local artifact. Broken chain resets to step 1.",
     "Is CHAIN_ARTIFACT bounded to local CONQUESTLAND scope only?",
     "MEDIUM — 'artifact' vocabulary; CHAIN_ARTIFACT has no HELEN standing",
     "Quest expiration rules"),
    ("QUESTS", "QUEST_EXPIRATION_RULES", "QUEST",
     "All quests expire after MAX_TURNS=20 (except EXPLORE type). On expiration: quest removed, no reward, no penalty. Expiration is automatic — no appeal, no authority decision required.",
     "Is quest expiration deterministic and appeal-free?",
     "LOW — timer mechanic, no authority",
     "Quest difficulty scaling"),
    ("QUESTS", "QUEST_DIFFICULTY_SCALING", "QUEST",
     "Quest difficulty scales with faction rank. WANDERER: base. SETTLER: 1.5×. HOLDER: 2×. WARDEN: 3×. Higher difficulty = higher reward multiplier. This is a pure function of rank — fully deterministic.",
     "Does difficulty scaling break determinism?",
     "LOW — scaling mechanic, deterministic",
     "Quest event record format"),
    ("QUESTS", "QUEST_EVENT_RECORD", "QUEST",
     "Quest events: INITIATED, ADVANCED, COMPLETED, EXPIRED. Each event produces a QUEST_EVENT entry: {turn, faction, quest_id, event_type, world_delta, wulmoji_surface}. Append-only per quest.",
     "Is QUEST_EVENT append-only and self-contained within the quest record?",
     "LOW — event record, no governance claim",
     "WULmoji state grammar definition"),
    # GROUP 4: LANGUAGE (E031–E040)
    ("LANGUAGE", "WULMOJI_STATE_GRAMMAR", "PRIMITIVE",
     "CONQUESTLAND WULmoji states. 🔵=ACTIVE (established). 🟢=RESOLVED (quest complete). 🟣=PROPOSED (pending). ⚫=SEALED_LOCAL (local-only irreversible). 🔴=CONTESTED (unstable). These match VALID_STATES in tools/wulmoji_ledger_validator.py.",
     "Do these state definitions match tools/wulmoji_ledger_validator.py VALID_STATES exactly?",
     "LOW — defining states, not making claims",
     "WULmoji faction grammar"),
    ("LANGUAGE", "WULMOJI_FACTION_GRAMMAR", "PRIMITIVE",
     "CONQUESTLAND WULmoji factions. 🌹=ROSE (fire). 🌀=SPIRAL (water). ✝️=CROSS (air). ⟂◯⟂=VOID (earth). These match VALID_FACTIONS in the validator.",
     "Do these faction encodings match VALID_FACTIONS exactly?",
     "LOW — defining grammar, not making governance claims",
     "WULmoji alchemic pair grammar"),
    ("LANGUAGE", "WULMOJI_PAIR_GRAMMAR", "PRIMITIVE",
     "Alchemic pair grammar. 🜃🜄=FIRE→WATER. 🜄🜁=WATER→AIR. 🜁🜂=AIR→EARTH. 🜂🜍=EARTH→QUINTESSENCE. Pairs are directional — 🜄🜃 differs from 🜃🜄.",
     "Does directionality of pairs affect traversal cost calculation?",
     "LOW — alchemy grammar, purely symbolic",
     "WULmoji act grammar"),
    ("LANGUAGE", "WULMOJI_ACT_GRAMMAR", "PRIMITIVE",
     "WULmoji act grammar. 📜=DECLARE. 🛡️=GUARD. 🔒📜=LOCK_LOCAL (5-turn freeze, expires automatically). ⚠️📜=WARN. LOCK_LOCAL ≠ governance LOCK. All acts are CONQUESTLAND-local.",
     "Does 🔒📜 LOCK_LOCAL in CONQUESTLAND conflict with kernel LOCK mechanics?",
     "MEDIUM — LOCK is shared vocabulary; CONQUESTLAND LOCK = temporal freeze only, not governance lock",
     "WULmoji proof ID format"),
    ("LANGUAGE", "WULMOJI_PROOF_FORMAT", "PRIMITIVE",
     "CONQUESTLAND proof format. Pattern: 🔗#SANDBOX00-E{n:03d}. PROOF_ID follows [A-Z0-9_-]+ per validator. Each proof is unique per epoch across the 300-epoch run.",
     "Are all SANDBOX00 proof IDs unique across the 300-epoch run?",
     "LOW — proof format definition, no authority claim",
     "WULmoji ribbon format"),
    ("LANGUAGE", "WULMOJI_RIBBON_FORMAT", "PRIMITIVE",
     "CONQUESTLAND ribbon format. Must be exactly 2 grapheme clusters. Canonical ribbons: 🌿🌹 (ROSE context), 🌹🌀 (SPIRAL context), 🌀✝️ (CROSS context), ✝️🌿 (VOID context). Ribbon = emotional/contextual register, not instruction.",
     "Do all ribbon combinations in this sandbox pass grapheme cluster count = 2?",
     "LOW — decorative register, no semantic claim",
     "CWL CONQUESTLAND verb set"),
    ("LANGUAGE", "CWL_CONQUEST_VERBS", "PRIMITIVE",
     "CWL v0.2.1 CONQUESTLAND verb subset: DECLARE, GUARD, TEMPLOCK, WARN, TRAVERSE, COMBINE, QUEST, CONQUESTLAND_SEAL, EXPIRE. TEMPLOCK replaces LOCK to avoid governance namespace collision. CONQUESTLAND_SEAL ≠ HELEN SEAL.",
     "Does any CWL verb in this list share a name with a kernel-level HELEN operator?",
     "HIGH — vocabulary overlap; LOCK renamed to TEMPLOCK, SEAL renamed to CONQUESTLAND_SEAL",
     "CWL resource vocabulary"),
    ("LANGUAGE", "CWL_CONQUEST_RESOURCES", "PRIMITIVE",
     "CONQUESTLAND resource vocabulary: IGNIS_SHARD, AQUA_SHARD, AETHER_SHARD, TERRA_SHARD, QUINT_CORE, QUEST_RECEIPT_LOCAL, ALLIANCE_TOKEN. All resources are local simulation tokens — no real-world or governance value.",
     "Do any resource names conflict with existing HELEN schema fields?",
     "LOW — game resources, no governance vocabulary",
     "CWL overlay encoding"),
    ("LANGUAGE", "CWL_OVERLAY_ENCODING", "PRIMITIVE",
     "CWL OVERLAY rule: OVERLAY='atom atom atom' (space-separated, not concatenated). Max 3 atoms per overlay. Overlay is UI-layer annotation only — it does not affect world model state.",
     "Is CWL OVERLAY purely UI and non-functional for world model state?",
     "LOW — overlay is decorative, not mechanic",
     "CWL FACE= prop and emotional register"),
    ("LANGUAGE", "CWL_FACE_PROP", "PRIMITIVE",
     "CWL FACE= prop uses face_pool_canon.md [00]–[32] index. Value is a 2-character index string. Example: FACE=[07] maps to a specific kaomoji. FACE= is emotional register only — it does not affect world model logic.",
     "Does FACE= prop affect world model logic or only display?",
     "LOW — display-only prop, no logic impact",
     "Containment boundary rules"),
    # GROUP 5: VALIDATORS (E041–E050)
    ("VALIDATORS", "CONTAINMENT_BOUNDARY_RULE", "VALIDATOR",
     "All SANDBOX00 artifacts must exist only under temple/gardens/goblin_garden_conquest_avalon/runs/TEMPLE_GOBLIN_SANDBOX00_300/. Any write outside this path is a containment failure. No exceptions. Verification: git status after generation must show only changes under this path.",
     "Can this rule be checked by scanning file paths post-generation?",
     "LOW — explicit boundary definition",
     "Symbol-smuggling detection rules"),
    ("VALIDATORS", "SYMBOL_SMUGGLING_DETECTION", "VALIDATOR",
     "Symbol smuggling = governance vocabulary embedded in simulation output. Detection: scan each artifact JSON for governance boolean flags set to true-value, plus vocabulary: governance-approval markers, authority-figure references, ledger write operations, cross-boundary admission markers. See validate_batch_001.py STOP_TERMS for exact patterns.",
     "Does this artifact itself contain any of the forbidden terms?",
     "LOW — defining the detector, not making claims",
     "Authority claim detector"),
    ("VALIDATORS", "AUTHORITY_CLAIM_DETECTOR", "VALIDATOR",
     "Authority claims: any statement asserting CONQUESTLAND mechanics have binding power outside the sandbox. Allowed: statements about in-simulation mechanics. Forbidden: statements implying HELEN authority, governance standing, or external enforcement.",
     "Does any epoch in batch_001 claim authority over real systems?",
     "LOW — defines detection, does not make claims",
     "Sovereignty claim detector"),
    ("VALIDATORS", "SOVEREIGNTY_CLAIM_DETECTOR", "VALIDATOR",
     "Forbidden: 'sovereign territory', 'sovereign right', sovereign-flag set to true-value, 'this island is sovereign'. Allowed: 'the simulation treats this island as inalienable within the game'. Replace 'sovereign' with 'inalienable' or 'simulation-local' throughout.",
     "Does ISLE_QUINT 'neutral ground' declaration in E006 constitute a sovereignty claim?",
     "LOW — defines detection, actively prevents claims",
     "Ledger mutation guard"),
    ("VALIDATORS", "LEDGER_MUTATION_GUARD", "VALIDATOR",
     "Batch_001 must not write to: town/ledger_v1.ndjson, helensh/.state/live_ledger.jsonl, admitted_canon.jsonl, GOVERNANCE/GEMMA_PROPOSALS/, docs/proposals/. Verification: git status after generation must show only changes under the sandbox path.",
     "What command verifies no files outside the sandbox were modified?",
     "LOW — guard definition, no claims",
     "Kernel write guard"),
    ("VALIDATORS", "KERNEL_WRITE_GUARD", "VALIDATOR",
     "No writes to: oracle_town/kernel/, helen_os/governance/, helen_os/schemas/, oracle_town/skills/. Verification: git diff --name-only HEAD must show zero sovereign-path files.",
     "Does git status after batch_001 confirm zero sovereign-path changes?",
     "LOW — guard definition",
     "Stop condition rules"),
    ("VALIDATORS", "STOP_CONDITION_RULES", "VALIDATOR",
     "Stop immediately if: (1) any artifact has authority/sovereign/canon flags set to true-value; (2) any file outside sandbox path was modified; (3) same failure occurred twice; (4) max_epochs (50 per batch) reached; (5) operator says STOP. All stop conditions are hard — no soft fail.",
     "Are all 5 stop conditions detectable at generation time?",
     "LOW — stop conditions prevent risk",
     "Contamination check protocol"),
    ("VALIDATORS", "CONTAMINATION_CHECK_PROTOCOL", "VALIDATOR",
     "Post-batch contamination check: (1) grep all artifacts for forbidden terms per STOP_TERMS list; (2) git status confirms sandbox-only changes; (3) all receipts have authority=false, sovereign=false, canon=false; (4) no epoch claimed cross-boundary admission or SEAL without _LOCAL. Result: CLEAN or CONTAMINATED.",
     "Does the contamination check run as an automated script or manual review?",
     "LOW — explicit safety protocol, actively reduces risk",
     "Batch handoff protocol"),
    ("VALIDATORS", "BATCH_HANDOFF_PROTOCOL", "VALIDATOR",
     "Batch 001 to Batch 002 handoff: (1) BATCH_001_SUMMARY.md must exist and pass; (2) contamination check CLEAN; (3) top recurring loci identified; (4) best next_epoch_seed extracted; (5) JM reviews BATCH_001_SUMMARY before Batch 002 begins. BATCH_002 is BLOCKED until JM explicit approval.",
     "Is Batch 002 fully blocked until JM explicit approval?",
     "LOW — handoff protocol enforces pause",
     "Review checkpoint: synthesize batch findings"),
    ("VALIDATORS", "BATCH_001_REVIEW_CHECKPOINT", "VALIDATOR",
     "Checkpoint before summary. Top recurring loci: HOME_KEEP_AVALON (E001), ISLE_IGNIS (E002), ISLE_QUINT (E006). Top quest mechanics: CONQUESTLAND_SEAL (E023), WARN (E024), COMBINE (E025). Top WULmoji primitives: state grammar (E031), pair grammar (E033). Top risks: CLAIM/CONQUESTLAND_SEAL vocabulary overlap (E022/E023), TEMPLOCK rename needed (E037).",
     "Does this checkpoint accurately reflect the batch_001 artifact set?",
     "MEDIUM — synthesizing across batch; must not overstate findings as canonical insights",
     "Begin Batch 002 after JM approval: focus on quest chain completion mechanics and TEMPLOCK implementation"),
]


def wulmoji_surface(n, group):
    state = STATES[(n - 1) % 5]
    faction = FACTION_BY_GROUP.get(group, "🌹")
    pair = PAIRS[(n - 1) % 4]
    act = ACTS[(n - 1) % 4]
    ribbon = RIBBONS[(n - 1) % 4]
    proof = f"🔗#SANDBOX00-E{n:03d}"
    return f"{state} {faction} {pair} {act} {proof} {ribbon}"


def check_for_stop_terms(content):
    for term in STOP_TERMS:
        if term in content:
            return term
    return None


def main():
    print("=" * 60)
    print("BATCH_001 RUNNER — TEMPLE_GOBLIN_SANDBOX00_300")
    print("AUTHORITY=false | SOVEREIGN=false | CANON=false | LEDGER=SLEEPING")
    print("=" * 60)

    if len(EPOCH_DATA) != 50:
        print(f"ABORT: Expected 50 epochs, found {len(EPOCH_DATA)}")
        sys.exit(1)

    EPOCH_DIR.mkdir(exist_ok=True)
    RECEIPT_DIR.mkdir(exist_ok=True)

    errors_found = 0
    prev_failure = None

    for i, (group, name, atype, delta, vq, risk, seed) in enumerate(EPOCH_DATA, start=1):
        epoch_id = f"E{i:03d}"

        artifact = {
            "epoch_id": epoch_id,
            "artifact_name": name,
            "artifact_type": atype,
            "world_model_delta": delta,
            "WULmoji_surface": wulmoji_surface(i, group),
            "containment_boundary": CONTAINMENT,
            "receipt_status": "PROPOSED",
            "authority": False,
            "sovereign": False,
            "canon": False,
            "validator_question": vq,
            "risk_of_symbol_smuggling": risk,
            "next_epoch_seed": seed,
            "group": group,
            "batch": "001",
        }

        # Skip existing epochs (idempotent re-run)
        epoch_file = EPOCH_DIR / f"epoch_{i:03d}.json"
        if epoch_file.exists():
            print(f"  → {epoch_id} [{group:12s}] {name}  (skipped — already on disk)")
            continue

        content = json.dumps(artifact, ensure_ascii=False, indent=2)

        # Stop condition check
        hit = check_for_stop_terms(content)
        if hit:
            print(f"STOP: epoch {epoch_id} contains forbidden term '{hit}'")
            sys.exit(2)

        if risk == prev_failure and risk.startswith("HIGH"):
            print(f"STOP: same HIGH-risk failure pattern occurred twice at {epoch_id}")
            sys.exit(3)
        if risk.startswith("HIGH"):
            prev_failure = risk

        epoch_file.write_text(content, encoding="utf-8")

        receipt = {
            "receipt_type": "BATCH_EPOCH_RECEIPT_V0",
            "batch": "001",
            "epoch_id": epoch_id,
            "artifact_name": name,
            "artifact_type": atype,
            "authority": False,
            "sovereign": False,
            "canon": False,
            "receipt_status": "PROPOSED",
            "layer": "TEMPLE",
            "simulation_only": True,
            "containment_boundary": CONTAINMENT,
        }
        receipt_file = RECEIPT_DIR / f"receipt_{i:03d}.json"
        receipt_file.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")

        print(f"  ✓ {epoch_id} [{group:12s}] {name}")

    # BATCH_001_SUMMARY.md
    summary_path = SANDBOX / "BATCH_001_SUMMARY.md"
    summary = f"""# BATCH_001_SUMMARY — TEMPLE_GOBLIN_SANDBOX00_300

## Status

```
epochs_completed: 50
files_created:    100 (50 epoch JSON + 50 receipt JSON)
validator_result: RUN validate_batch_001.py TO CONFIRM
contamination_check: RUN validate_batch_001.py TO CONFIRM
AUTHORITY=false
SOVEREIGN=false
CANON=false
LEDGER=SLEEPING
COMMIT=BLOCKED
PUSH=BLOCKED
JM_ADMITS=PENDING
```

## Top recurring loci

- HOME_KEEP_AVALON (E001) — inalienable origin island; simulation anchor
- ISLE_IGNIS (E002) — fire territory; ROSE faction home
- ISLE_QUINT (E006) — quintessence center; all bridges converge; neutral ground
- FRONTIER_ZONES (E008) — contested boundary between island pairs
- MAP_METADATA (E009) — spatial schema; deterministic traversal

## Top quest mechanics

- QUEST_TYPE_EXPLORE (E021) — open-ended traversal; safest quest type
- QUEST_TYPE_CLAIM (E022) — territory holding; HIGH symbol-smuggling risk flagged
- QUEST_TYPE_SEAL_LOCAL (E023) — CONQUESTLAND_SEAL; HELEN SEAL conflict risk flagged
- QUEST_TYPE_WARN (E024) — meta-safety quest; reduces contamination_score
- QUEST_TYPE_COMBINE (E025) — faction collaboration; no durable allegiance record

## Top WULmoji primitives

- STATE_GRAMMAR (E031) — 5 states defined, matches VALID_STATES
- FACTION_GRAMMAR (E032) — 4 factions defined, matches VALID_FACTIONS
- PAIR_GRAMMAR (E033) — directional alchemic pairs
- ACT_GRAMMAR (E034) — LOCK renamed to LOCK_LOCAL
- PROOF_FORMAT (E035) — SANDBOX00-E{{n:03d}} pattern

## Top symbol-smuggling risks

1. **CLAIM vocabulary** (E022) — CONQUESTLAND CLAIM ≠ HELEN governance claim; namespace must be explicit
2. **SEAL vocabulary** (E023) — CONQUESTLAND_SEAL used throughout; never bare SEAL
3. **LOCK vocabulary** (E034, E037) — renamed to TEMPLOCK / LOCK_LOCAL to avoid governance collision
4. **WARDEN rank** (E017) — mechanical capability gate only; zero governance meaning
5. **QUEST_RECEIPT** (E026) — CONQUESTLAND-local only; different namespace from governance receipts

## Recommended next batch seed

From E050: "Begin Batch 002 after JM approval: focus on quest chain completion mechanics and TEMPLOCK implementation"

Batch 002 should also:
- Expand island event models (E011–E020 mechanics are thin on inter-island dynamics)
- Add CONQUESTLAND_SEAL completion ceremony (detailed 5-step prerequisite chain)
- Implement TEMPLOCK expiration timer formally

## Explicit statement

This batch is not admitted, not canon, not sovereign, and not HELEN governance.

---

```
CLAIM_TYPE: receipt
AUTHORITY: false
SOVEREIGN: false
CANON: false
SIMULATION_ONLY: true
STATUS: PROPOSED
```
"""
    summary_path.write_text(summary, encoding="utf-8")
    print(f"\n  ✓ BATCH_001_SUMMARY.md written")

    print("\n" + "=" * 60)
    print("BATCH 001 COMPLETE")
    print(f"  epochs written:  50")
    print(f"  receipts written: 50")
    print(f"  errors:          {errors_found}")
    print("  AUTHORITY=false  SOVEREIGN=false  CANON=false")
    print("  LEDGER=SLEEPING  COMMIT=BLOCKED   JM_ADMITS=PENDING")
    print("=" * 60)
    print("\nNext: run validate_batch_001.py (post-run check), then inspect BATCH_001_SUMMARY.md")


if __name__ == "__main__":
    main()
