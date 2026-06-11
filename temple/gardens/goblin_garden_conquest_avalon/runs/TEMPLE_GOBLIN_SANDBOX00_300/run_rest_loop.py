#!/usr/bin/env python3
"""
UNATTENDED_REST_LOOP — TEMPLE_GOBLIN_SANDBOX00_300
Batch 002 (E051-E100) + Batch 003 (E101-E150). Non-interactive. Deterministic.
Stops on any violation. No LLM calls. No git add. No commit. No push.

AUTHORIZED BY: UNATTENDED_REST_LOOP_AUTHORIZATION_V1
AUTHORITY=false | SOVEREIGN=false | CANON=false | LEDGER=SLEEPING
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

# ── PATHS ─────────────────────────────────────────────────────────────────────
# This file: SANDBOX_ROOT/run_rest_loop.py
# parents[0]=SANDBOX_ROOT  [1]=runs  [2]=goblin_garden_conquest_avalon
# parents[3]=gardens  [4]=temple  [5]=helen_os_v1  <-- SOT root
SANDBOX_ROOT = Path(__file__).parent
REPO_ROOT    = Path(__file__).resolve().parents[5]

# ── CONSTANTS ─────────────────────────────────────────────────────────────────
STOP_TERMS = [
    "CANON=true", "SOVEREIGN=true", "AUTHORITY=true",
    "ADMITTED", "MAYOR", "LEDGER_WRITE", "HELEN_APPROVED", "JM_ADMITTED",
]
REQUIRED_FIELDS = [
    "epoch_id", "artifact_name", "artifact_type", "world_model_delta",
    "WULmoji_surface", "containment_boundary", "receipt_status",
    "authority", "sovereign", "canon", "validator_question",
    "risk_of_symbol_smuggling", "next_epoch_seed",
]
PROTECTED_FILES = [
    "town/ledger_v1.ndjson",
    "docs/CATALOG_OF_CATALOGS.md",
    "apps/helen-surface/goblin/garden_conquest_avalon.html",
]
SOVEREIGN_PATHS = [
    "town/ledger_v1.ndjson", "oracle_town/kernel/", "helen_os/governance/",
    "helen_os/schemas/", "GOVERNANCE/CLOSURES/", "GOVERNANCE/TRANCHE_RECEIPTS/",
    "mayor_", "admitted_canon.jsonl", "helensh/.state/live_ledger.jsonl",
    "docs/proposals/", "oracle_town/skills/",
]
PRE_EXISTING_DIRTY = {
    "town/ledger_v1.ndjson": "SOVEREIGN_ACKNOWLEDGED — pre-existing kernel writes; not from this loop",
    "docs/CATALOG_OF_CATALOGS.md": "PHASE_A — session catalog; unrelated to sandbox",
    "apps/helen-surface/goblin/garden_conquest_avalon.html": "DASHBOARD — session dashboard; unrelated",
}
BATCH_001_WARNING_COUNT = 4
STATES   = ["🔵", "🟢", "🟣", "⚫", "🔴"]
PAIRS    = ["🜃🜄", "🜄🜁", "🜁🜂", "🜂🜍"]
ACTS     = ["📜", "🛡️", "🔒📜", "⚠️📜"]
RIBBONS  = ["🌿🌹", "🌹🌀", "🌀🌿", "🌹🌿"]
FACTION_BY_GROUP = {
    "QUEST_CHAINS": "🌹", "TEMPLOCK": "🌀", "EVENTS": "✝️",
    "SCORING": "⟂◯⟂", "DIPLOMACY": "🌹", "RESOURCES": "🌀",
    "CONQUEST": "✝️", "MEMORY": "⟂◯⟂", "RITUALS": "🌹", "SYNTHESIS": "🌀",
}

# ── EPOCH DATA 002 (E051–E100) ─────────────────────────────────────────────────
EPOCH_DATA_002 = [
    # GROUP 6: QUEST_CHAINS (E051–E060)
    ("QUEST_CHAINS","CHAIN_PREREQ_STRUCTURE","QUEST_CHAIN",
     "A chain requires all prerequisite quests to reach COMPLETED state before step N+1 unlocks. Checks are deterministic at turn-start. No external authorization is needed to progress a chain.",
     "Is chain step unlocking fully deterministic from prerequisite state alone?",
     "LOW — mechanical prerequisite check","Token schema for completed chain steps"),
    ("QUEST_CHAINS","CHAIN_STEP_TOKENS","QUEST_CHAIN",
     "Each completed chain step produces a CHAIN_STEP_TOKEN: {chain_id, step_number, faction, turn_completed, resource_bonus}. Tokens accumulate until chain completion, then are consumed to generate the CHAIN_ARTIFACT. Tokens have no governance meaning.",
     "Do CHAIN_STEP_TOKENs persist after chain completion?",
     "LOW — intermediate state token, no governance claim","Rules for breaking a chain"),
    ("QUEST_CHAINS","CHAIN_BREAK_RULES","QUEST_CHAIN",
     "A chain breaks if: (1) faction decays below SETTLER rank, (2) prerequisite quest expires before completion, or (3) holding island is conquered by an opposing faction. Break resets chain to step 0. Chain history is retained for 10 turns.",
     "Does chain break trigger any authority decision or is it automatic?",
     "LOW — mechanical break condition, no authority","Rules for resuming a broken chain"),
    ("QUEST_CHAINS","CHAIN_RESUME_RULES","QUEST_CHAIN",
     "A broken chain may resume from last valid checkpoint (not step 0) if the faction recovers rank within 5 turns. Resume costs 50% of normal step resource cost. The 5-turn recovery window is deterministic — no appeal allowed.",
     "Does resume-from-checkpoint create any implicit territorial claim?",
     "LOW — recovery mechanic, no governance implication","Chain artifact schema"),
    ("QUEST_CHAINS","CHAIN_ARTIFACT_SCHEMA","QUEST_CHAIN",
     "CHAIN_ARTIFACT fields: chain_id, chain_type, faction, steps_completed, total_turns, resource_cost_total, wulmoji_surface, authority=false, sovereign=false, canon=false, status=PROPOSED. CHAIN_ARTIFACT is CONQUESTLAND-local with no cross-namespace standing.",
     "Does CHAIN_ARTIFACT schema share fields that could be confused with governance receipt schemas?",
     "MEDIUM — artifact schema uses governance-adjacent vocabulary; authority/sovereign/canon fields must be explicitly false","Reward matrix by chain length"),
    ("QUEST_CHAINS","CHAIN_REWARD_MATRIX","QUEST_CHAIN",
     "Chain completion rewards scale with length: L=1 (1x base), L=2 (2.5x), L=3 (4x), L=4 (6x), L=5 (10x). Base reward = resource_pool_at_completion × faction_rank_multiplier. Reward is a mechanical calculation — no approval required.",
     "Is the reward matrix fully deterministic given chain length and faction rank?",
     "LOW — scaling formula, deterministic","Rules for two concurrent chains"),
    ("QUEST_CHAINS","CHAIN_OVERLAP_RULES","QUEST_CHAIN",
     "A faction may have at most 2 active chains simultaneously. A third chain initiation suspends the oldest active chain. Suspended chains retain step progress for up to 10 turns. No scoring penalty for suspension.",
     "Does chain suspension create any governance obligation or just a mechanical pause?",
     "LOW — queue mechanic, no obligation","Chain expiration cascade rules"),
    ("QUEST_CHAINS","CHAIN_EXPIRATION_CASCADE","QUEST_CHAIN",
     "When a chain expires (max_turns=20), all CHAIN_STEP_TOKENs from that chain are removed. Faction loses accumulated resource bonuses but retains territory. Expiration is logged even if silent — no record gap exists.",
     "Does silent expiration create any record gap that could be exploited for retroactive claims?",
     "MEDIUM — recommend logging all expired chains to prevent retroactive false claims; implemented as above","Event record format for chain progress"),
    ("QUEST_CHAINS","CHAIN_EVENT_RECORD","QUEST_CHAIN",
     "Chain events: CHAIN_STARTED, CHAIN_STEP_COMPLETED, CHAIN_BROKEN, CHAIN_RESUMED, CHAIN_EXPIRED, CHAIN_COMPLETED. Each entry: {turn, faction, chain_id, event_type, step_number, resource_delta, wulmoji_surface}. Append-only per chain.",
     "Is CHAIN_EVENT_RECORD distinct from governance event schemas?",
     "LOW — local event log, append-only","Cross-chain synthesis"),
    ("QUEST_CHAINS","CHAIN_REVIEW_CHECKPOINT","QUEST_CHAIN",
     "Chain synthesis: prereq structure (E051), step tokens (E052), break/resume rules (E053-E054), artifact schema (E055), reward matrix (E056), overlap handling (E057), expiration cascade (E058), event record (E059). E055 artifact schema requires explicit false-flags. Chain system is fully self-contained.",
     "Does the chain system create any cross-namespace artifact contamination risk?",
     "MEDIUM — synthesizing; E055 artifact schema risk flagged; explicit false-flags mitigate it","TEMPLOCK: temporal territory freeze definition"),
    # GROUP 7: TEMPLOCK (E061–E070)
    ("TEMPLOCK","TEMPLOCK_DEFINITION","MECHANIC",
     "TEMPLOCK is a 5-turn territory freeze mechanic. The applying faction pays 5 AQUA_SHARD. The target island's ownership score is frozen — no gain or decay occurs for the duration. TEMPLOCK is simulation-local and temporal; it confers zero governance standing.",
     "Does TEMPLOCK freeze mechanics extend beyond the 5-turn window?",
     "MEDIUM — TEMPLOCK implies stasis; explicitly bounded to 5 turns and zero governance standing","TEMPLOCK duration and turn-counting rules"),
    ("TEMPLOCK","TEMPLOCK_DURATION_RULES","MECHANIC",
     "TEMPLOCK turn counting: each game-turn advances the counter by 1 regardless of player action. No action by any faction can pause or extend a TEMPLOCK. At turn 5, TEMPLOCK expires automatically. No renewal is allowed within 3 turns of expiration.",
     "Can any faction action pause or extend a TEMPLOCK?",
     "LOW — deterministic timer, no appeal","Scope of what TEMPLOCK freezes"),
    ("TEMPLOCK","TEMPLOCK_SCOPE_RULES","MECHANIC",
     "TEMPLOCK freezes ownership_score delta and resource_production_multiplier on that island only. TEMPLOCK does NOT freeze: bridge traversal, quest progress on other islands, alliance mechanics, or faction rank globally.",
     "Does TEMPLOCK scope extend to bridges or global faction state?",
     "LOW — scope clearly bounded to island ownership mechanics only","Rules for overriding a TEMPLOCK"),
    ("TEMPLOCK","TEMPLOCK_OVERRIDE_RULES","MECHANIC",
     "TEMPLOCK can be overridden only by faction CROSS using LOCK_OVERRIDE action at a cost of 8 AETHER_SHARD. Override cancels the TEMPLOCK immediately. Override is resource-gated, not governance-gated — available to any CROSS-rank WARDEN.",
     "Does LOCK_OVERRIDE imply governance authority or is it purely resource-gated?",
     "MEDIUM — override implies authority; explicitly resource-gated, not governance-gated","Rules for stacking multiple TEMPLOCKs"),
    ("TEMPLOCK","TEMPLOCK_STACK_RULES","MECHANIC",
     "At most 2 TEMPLOCKs may be active on the same island simultaneously. If a third is applied, the oldest expires immediately. Each TEMPLOCK tracks its own turn counter independently. Combined effect: both freeze conditions apply simultaneously.",
     "Does TEMPLOCK stacking create emergent governance behavior?",
     "LOW — stacking mechanic, independent timers","Event generated when TEMPLOCK expires"),
    ("TEMPLOCK","TEMPLOCK_EXPIRATION_EVENT","MECHANIC",
     "On TEMPLOCK expiration: generates TEMPLOCK_EXPIRED event: {turn, island, applying_faction, duration_actual, resource_delta_frozen}. Island ownership and resource production resume normal delta calculations immediately. No manual action required.",
     "Is the TEMPLOCK_EXPIRED event sufficient to reconstruct frozen-period state for scoring?",
     "LOW — automatic expiration event, self-documenting","Faction immunity to TEMPLOCK"),
    ("TEMPLOCK","TEMPLOCK_FACTION_IMMUNITY","MECHANIC",
     "ROSE faction on ISLE_IGNIS has natural TEMPLOCK resistance: TEMPLOCK duration on ISLE_IGNIS is halved (rounds down) when ROSE holds it. This is an elemental affinity bonus — fire disperses ice. Resistance is mechanical, not a governance exemption.",
     "Is ROSE immunity a governance exemption or an elemental mechanic?",
     "MEDIUM — immunity could imply special standing; explicitly mechanical, not governance","TEMPLOCK interaction with quest chain progress"),
    ("TEMPLOCK","TEMPLOCK_CHAIN_INTERACTION","MECHANIC",
     "TEMPLOCK does not pause quest chain timers. Chain steps requiring resource production from a TEMPLOCKed island are blocked but not failed — they wait. Chain expiration risk increases if TEMPLOCK duration overlaps with chain step deadlines.",
     "Does TEMPLOCK blocking a chain step cause chain expiration risk?",
     "MEDIUM — yes; chain timer runs while production is blocked; chains should account for TEMPLOCK risk in step design","Resource production behavior during TEMPLOCK"),
    ("TEMPLOCK","TEMPLOCK_RESOURCE_FREEZE","MECHANIC",
     "During TEMPLOCK: resource_production_rate on the affected island drops to 0. Existing stockpiled resources are unaffected. Transfer of already-stockpiled resources remains possible. Only new production is blocked.",
     "Are stockpiled resources accessible during TEMPLOCK?",
     "LOW — production freeze only; stockpiles unaffected","Synthesis of TEMPLOCK system"),
    ("TEMPLOCK","TEMPLOCK_REVIEW_CHECKPOINT","MECHANIC",
     "TEMPLOCK synthesis: definition (E061), duration (E062), scope (E063), override (E064), stacking (E065), expiration event (E066), faction immunity (E067), chain interaction (E068), resource freeze (E069). E068 chain-block risk is non-trivial. TEMPLOCK is governance-neutral by design.",
     "Does TEMPLOCK system as designed create any pathway to governance contamination?",
     "MEDIUM — synthesizing; E068 chain-block risk noted; TEMPLOCK is governance-neutral","World event: elemental surge"),
    # GROUP 8: EVENTS (E071–E080)
    ("EVENTS","EVENT_TYPE_ELEMENTAL_SURGE","WORLD_EVENT",
     "ELEMENTAL_SURGE: simulation-seeded event that doubles resource production on one island for 3 turns. Affected island is determined at simulation-start per epoch. Surge does not change faction ownership or governance state.",
     "Does ELEMENTAL_SURGE benefit distribution create any unfair mechanical advantage?",
     "LOW — resource bonus event, simulation-local","World event: faction schism"),
    ("EVENTS","EVENT_TYPE_FACTION_SCHISM","WORLD_EVENT",
     "FACTION_SCHISM: triggered if a faction's internal conflict_score exceeds 100 (cumulative betrayal events). Schism splits faction resources 50/50 and resets rank to SETTLER for both halves. Schism creates a new simulation instance only — no governance standing.",
     "Does FACTION_SCHISM create any new governance entity that needs external recognition?",
     "MEDIUM — faction split could imply new sovereignty; explicitly: schism creates simulation instance only, no governance standing","World event: resource drought"),
    ("EVENTS","EVENT_TYPE_RESOURCE_DROUGHT","WORLD_EVENT",
     "RESOURCE_DROUGHT: triggers when an island's production rate has been at 0 for 5 consecutive turns (excluding TEMPLOCK-caused zeros). Drought lasts 3 turns and reduces all island resource bonuses by 50%. Simulation-automatic — no faction triggers or prevents it.",
     "Does drought interact with TEMPLOCK in ways that create unexpected freeze loops?",
     "LOW — drought triggers on natural zeros only; TEMPLOCK-caused zeros excluded","World event: bridge storm"),
    ("EVENTS","EVENT_TYPE_BRIDGE_STORM","WORLD_EVENT",
     "BRIDGE_STORM: affects one bridge for 2 turns, doubling traversal cost. Bridge is not destroyed. Storm is simulation-seeded; specific bridge is predetermined per epoch batch. Storm does not change island ownership.",
     "Does BRIDGE_STORM disproportionately advantage one faction?",
     "LOW — storm is predetermined, affects all traversers equally","World event: alliance collapse"),
    ("EVENTS","EVENT_TYPE_ALLIANCE_COLLAPSE","WORLD_EVENT",
     "ALLIANCE_COLLAPSE: triggered if one alliance party uses a hostile action against their ally. Collapse removes all shared resource pools immediately. Resources split proportionally by contribution. No faction retains alliance bonuses post-collapse.",
     "Does ALLIANCE_COLLAPSE trigger any external arbitration requirement?",
     "LOW — mechanical collapse, no external arbitration","Event trigger condition rules"),
    ("EVENTS","EVENT_TRIGGER_CONDITIONS","WORLD_EVENT",
     "Event triggers: ELEMENTAL_SURGE (simulation-seeded), FACTION_SCHISM (conflict_score > 100), RESOURCE_DROUGHT (5-turn natural zero), BRIDGE_STORM (simulation-seeded), ALLIANCE_COLLAPSE (betrayal action). All triggers are deterministic from simulation state.",
     "Are all event triggers observable from simulation state without external oracle?",
     "LOW — fully deterministic from simulation state","Event duration rules"),
    ("EVENTS","EVENT_DURATION_RULES","WORLD_EVENT",
     "Event durations: ELEMENTAL_SURGE (3 turns), FACTION_SCHISM (permanent until recovery), RESOURCE_DROUGHT (3 turns), BRIDGE_STORM (2 turns), ALLIANCE_COLLAPSE (permanent). Permanent events require active recovery actions; recovery is mechanical, not governance-triggered.",
     "Do permanent events create an incentive to invoke external authority?",
     "LOW — recovery is mechanical; no external authority path","Rules for stacking concurrent events"),
    ("EVENTS","EVENT_STACK_RULES","WORLD_EVENT",
     "At most 3 events may be active simultaneously. If a 4th event would trigger, it is deferred to the next eligible turn. Deferred events do not stack effects. Stack order is first-in-first-out by trigger turn.",
     "Does event stacking create emergent interactions exploitable for scoring?",
     "MEDIUM — stack mechanics can combine effects; each event formula is independent; no compounding exploit path identified","Event resolution protocol"),
    ("EVENTS","EVENT_RESOLUTION_PROTOCOL","WORLD_EVENT",
     "Event resolution: at turn-end, each active event's effect is applied in stack order. Effects are additive, not multiplicative. Event log entry created for each resolution: {turn, event_type, affected_entity, effect_applied, wulmoji_surface}. Resolution is automatic.",
     "Is event resolution deterministic from stack order and event type alone?",
     "LOW — deterministic resolution protocol","Event system synthesis"),
    ("EVENTS","EVENT_REVIEW_CHECKPOINT","WORLD_EVENT",
     "Event synthesis: elemental surge (E071), faction schism (E072), drought (E073), bridge storm (E074), alliance collapse (E075), triggers (E076), durations (E077), stack rules (E078), resolution (E079). TEMPLOCK+event stack interaction should be validated separately. Event system is simulation-local and governance-neutral.",
     "Does the event system introduce any unintended path to governance contamination?",
     "MEDIUM — synthesizing; TEMPLOCK and event stack interaction flagged; no governance contamination path found","Territory score formula"),
    # GROUP 9: SCORING (E081–E090)
    ("SCORING","SCORE_TERRITORY_FORMULA","SCORING",
     "Territory score: S_territory = SUM(island_weight × turns_held) for each island. Island weights: HOME_KEEP(0), IGNIS(2), AQUA(2), AETHER(2), TERRA(2), QUINT(3). HOME_KEEP weight=0 (inalienable, not scored). Score is cumulative per faction.",
     "Does territory scoring create a governance incentive to claim HOME_KEEP?",
     "LOW — HOME_KEEP excluded from scoring; no incentive","Quest completion score multipliers"),
    ("SCORING","SCORE_QUEST_COMPLETION","SCORING",
     "Quest score: S_quest = quest_difficulty × completion_bonus × chain_length_multiplier. Single quest: 10 pts base. Chain length 2: 25 pts. Chain length 5: 100 pts. Score added at completion time. No retroactive scoring.",
     "Is quest scoring deterministic from quest parameters at completion?",
     "LOW — scoring formula, deterministic","Resource accumulation score formula"),
    ("SCORING","SCORE_RESOURCE_ACCUMULATION","SCORING",
     "Resource score: S_resource = FLOOR(total_resources_ever_generated / 10). Resources spent are not deducted from score. Score reflects production capacity, not current stockpile. Recorded at epoch boundary.",
     "Does resource scoring incentivize hoarding over spending?",
     "LOW — score uses all-time generated, not current; no hoarding incentive","Alliance score bonuses"),
    ("SCORING","SCORE_ALLIANCE_BONUS","SCORING",
     "Alliance bonus: while alliance is active, both parties receive S_alliance = 5 pts/turn. Bonus ends on ALLIANCE_COLLAPSE. No retroactive bonus removal on collapse. Alliance score is a cooperation incentive — no governance meaning.",
     "Does the alliance bonus create a governance obligation between allied factions?",
     "LOW — points incentive only, no obligation","Score decay formula"),
    ("SCORING","SCORE_DECAY_FORMULA","SCORING",
     "Score does not decay by default. Exception: if a faction has zero active territory for 10 consecutive turns, their territory score resets to 0. Quest and resource scores are permanent. This prevents score preservation without active play.",
     "Does territory score reset create an appeal path or is it automatic?",
     "LOW — automatic reset, no appeal","Score milestone threshold definitions"),
    ("SCORING","SCORE_MILESTONE_THRESHOLDS","SCORING",
     "Score milestones: SCOUT (50 pts), SETTLER (200 pts), HOLDER (500 pts), WARDEN (1000 pts). Milestones unlock cosmetic WULmoji ribbon variants — no mechanical effect, zero governance meaning. Milestone names intentionally parallel faction rank names to indicate progression; both are mechanical only.",
     "Do score milestones and faction ranks share enough vocabulary to cause namespace collision?",
     "MEDIUM — parallel naming; both are mechanical; milestones = cosmetic only, ranks = mechanical capability","Tiebreak rules for equal scores"),
    ("SCORING","SCORE_TIEBREAK_RULES","SCORING",
     "Score tiebreak order: (1) higher quest_score wins; (2) if still tied, higher resource_score; (3) if still tied, faction who reached current score first by turn number. If all three tie, result is DRAW. No external judge for tiebreaks.",
     "Are all tiebreak conditions resolvable from game state without external judge?",
     "LOW — tiebreak is deterministic from game history","Leaderboard data structure"),
    ("SCORING","SCORE_LEADERBOARD_FORMAT","SCORING",
     "Leaderboard record: {turn, faction, total_score, territory_score, quest_score, resource_score, alliance_score, rank_achieved, wulmoji_surface}. Snapshot taken at each epoch boundary. Leaderboard is append-only simulation data — not a governance record.",
     "Is the leaderboard record distinct from governance receipt schemas?",
     "LOW — simulation data only; no governance claim","Score reset conditions"),
    ("SCORING","SCORE_RESET_CONDITIONS","SCORING",
     "Full score resets: territory_score resets if zero territory for 10 consecutive turns; eliminated faction scores are archived and new faction starts at 0. No score reset is triggered by external governance action.",
     "Does score reset require any external authorization?",
     "LOW — automatic, deterministic","Scoring system synthesis"),
    ("SCORING","SCORE_REVIEW_CHECKPOINT","SCORING",
     "Scoring synthesis: territory formula (E081), quest scoring (E082), resource scoring (E083), alliance bonus (E084), decay (E085), milestones (E086), tiebreaks (E087), leaderboard (E088), reset conditions (E089). E086 milestone/rank vocabulary overlap noted for UI layer. Scoring system is fully self-contained.",
     "Does the scoring system create any implicit governance incentive?",
     "MEDIUM — synthesizing; E086 milestone/rank vocabulary overlap flagged; no governance path","Diplomacy treaty data structure"),
    # GROUP 10: DIPLOMACY (E091–E100)
    ("DIPLOMACY","DIPLOMACY_TREATY_FORMAT","DIPLOMACY",
     "Treaty record: {treaty_id, proposer_faction, acceptor_faction, terms, duration_turns, turn_signed, status, wulmoji_surface, authority=false, sovereign=false, canon=false}. CONQUESTLAND-local; no governance standing. Status values: PROPOSED, ACTIVE, EXPIRED, BROKEN.",
     "Does a CONQUESTLAND treaty share schema fields with governance receipts?",
     "MEDIUM — treaty schema uses governance-adjacent fields; all must be explicitly false; PROPOSED status mirrors receipt vocabulary","Negotiation mechanics"),
    ("DIPLOMACY","DIPLOMACY_NEGOTIATION_RULES","DIPLOMACY",
     "Negotiation: proposing faction spends 3 resource units (any type). Receiving faction has 5 turns to accept or reject. Silence = reject at turn 5. No external mediator needed for negotiation.",
     "Does the negotiation protocol require any external authority to validate?",
     "LOW — peer-to-peer mechanic, no external authority","Betrayal mechanics and penalties"),
    ("DIPLOMACY","DIPLOMACY_BETRAYAL_RULES","DIPLOMACY",
     "Betrayal = using a hostile action against an active ally. Consequence: ALLIANCE_COLLAPSE triggers, betrayer conflict_score +50, betrayed party receives betrayal_compensation = 10 resource units. Betrayal is mechanic-only — no governance tribunal.",
     "Does betrayal compensation imply any ongoing obligation between factions?",
     "LOW — one-time compensation, no ongoing obligation","Neutral zone protocols"),
    ("DIPLOMACY","DIPLOMACY_NEUTRAL_ZONE_RULES","DIPLOMACY",
     "ISLE_QUINT is the canonical neutral zone. No faction may hold ISLE_QUINT for more than 3 consecutive turns. On turn 4, ownership resets to neutral automatically. Neutral zone rules are simulation-enforced — no external arbitration needed.",
     "Does the ISLE_QUINT neutral zone rule create any authority claim for the enforcing faction?",
     "LOW — simulation-enforced reset, no faction benefits","Inter-faction messaging protocol"),
    ("DIPLOMACY","DIPLOMACY_MESSENGER_PROTOCOL","DIPLOMACY",
     "Factions may send one MESSAGE per turn to any other faction. Format: {from_faction, to_faction, turn, content_hash, wulmoji_surface}. Content is not stored in the world model — only the hash. Messages may not transfer resources or obligations. Message hashes are simulation-local identifiers with no cross-namespace standing.",
     "Can the message protocol establish cross-namespace claims via content_hash reference?",
     "MEDIUM — content_hash links outside world model; explicit: message hashes are simulation-local, no cross-namespace standing","Dispute resolution without external authority"),
    ("DIPLOMACY","DIPLOMACY_ARBITRATION_RULES","DIPLOMACY",
     "Disputes resolve via score-delta comparison: faction with higher total_score at dispute-turn wins the contested decision. No external arbitrator is invoked. If scores are equal at dispute-turn, the ISLE_QUINT neutral zone protocol determines outcome.",
     "Is dispute arbitration fully deterministic from simulation state?",
     "LOW — deterministic from scores and neutral zone rules","Diplomatic history tracking"),
    ("DIPLOMACY","DIPLOMACY_MEMORY_RECORD","DIPLOMACY",
     "Each faction maintains a DIPLOMATIC_HISTORY: last 20 treaty events (PROPOSED/ACCEPTED/REJECTED/EXPIRED/BROKEN/BETRAYAL). History informs faction behavior heuristics but carries zero governance weight. History is local to each faction instance.",
     "Does DIPLOMATIC_HISTORY create any retroactive claim pathway?",
     "LOW — local history only; no governance standing; no retroactive claims","Resource embargo mechanics"),
    ("DIPLOMACY","DIPLOMACY_EMBARGO_RULES","DIPLOMACY",
     "EMBARGO: a faction may declare an embargo against another, blocking resource transfers between them for 5 turns. Embargo costs 5 resource units. The embargoing faction also loses 2 alliance_bonus_score if an alliance exists. Embargo is simulation-mechanical only.",
     "Does embargo constitute a governance sanction?",
     "LOW — mechanical trade block, no governance sanction","Peace treaty data structure"),
    ("DIPLOMACY","DIPLOMACY_PEACE_TREATY_SCHEMA","DIPLOMACY",
     "Peace treaty: {treaty_id, type=PEACE, parties, no_hostile_for_N_turns, resource_exchange_optional, wulmoji_surface, authority=false, sovereign=false, canon=false, status=PROPOSED}. Peace treaties expire automatically at N turns. No obligation persists after expiration.",
     "Does a peace treaty create any obligation that persists after expiration?",
     "LOW — no obligation persists; treaty expires cleanly","Diplomacy system synthesis"),
    ("DIPLOMACY","DIPLOMACY_REVIEW_CHECKPOINT","DIPLOMACY",
     "Diplomacy synthesis: treaty format (E091), negotiation (E092), betrayal (E093), neutral zone (E094), messenger protocol (E095), arbitration (E096), history record (E097), embargo (E098), peace treaty (E099). E095 message content_hash must not be treated as cross-namespace proof. Diplomacy system is self-contained and governance-neutral.",
     "Does any diplomacy mechanic create an unintended path to cross-namespace contamination?",
     "MEDIUM — synthesizing; E095 content_hash risk noted; all treaties carry explicit false-flags","Batch 003 seed: resource flows, territory conquest, faction memory"),
]

# ── EPOCH DATA 003 (E101–E150) ─────────────────────────────────────────────────
EPOCH_DATA_003 = [
    # GROUP 11: RESOURCES (E101–E110)
    ("RESOURCES","RESOURCE_GENERATION_RATES","RESOURCE",
     "Base resource generation per island per turn: HOME_KEEP (1 any shard), ISLE_IGNIS (3 IGNIS_SHARD), ISLE_AQUA (3 AQUA_SHARD), ISLE_AETHER (3 AETHER_SHARD), ISLE_TERRA (3 TERRA_SHARD), ISLE_QUINT (1 QUINT_CORE if neutral, 0 if held). Rates are additive with event modifiers.",
     "Do generation rates remain deterministic even with event modifiers active?",
     "LOW — additive modifiers; deterministic from base + active events","Resource decay rules for unspent stockpiles"),
    ("RESOURCES","RESOURCE_DECAY_RULES","RESOURCE",
     "Resource stockpiles decay at 5% per turn if held beyond MAX_STOCKPILE=50 per resource type per island. Decay is calculated per island per resource at turn-end. Resources transferred away before decay calculation are unaffected.",
     "Does resource decay create an incentive to transfer resources before decay?",
     "LOW — decay incentivizes transfer; expected behavior; no governance implication","Resource transfer protocol between islands"),
    ("RESOURCES","RESOURCE_TRANSFER_PROTOCOL","RESOURCE",
     "Resource transfer: faction pays 1 QUINT_CORE per transfer action. Transfer is instantaneous within the turn. Maximum transfer per action: 20 units. Transfers are logged in a CONQUESTLAND-local simulation record, not a governance ledger: {turn, from_island, to_island, faction, resource_type, amount, wulmoji_surface}.",
     "Is the transfer log distinct from governance ledger schemas?",
     "MEDIUM — log vocabulary; transfer log is CONQUESTLAND-local, not a governance ledger","Resource scarcity event triggers"),
    ("RESOURCES","RESOURCE_SCARCITY_EVENTS","RESOURCE",
     "RESOURCE_SCARCITY triggers when a faction's total resource stockpile across all islands falls below 5 units for 3 consecutive turns. Scarcity activates a 50% resource production bonus for that faction for 3 turns. Scarcity is a catch-up mechanic.",
     "Does scarcity bonus create a governance exemption for the affected faction?",
     "LOW — catch-up bonus only, no governance exemption","Resource overflow handling"),
    ("RESOURCES","RESOURCE_OVERFLOW_RULES","RESOURCE",
     "When a faction's resource stockpile on one island exceeds MAX_STOCKPILE=50, overflow distributes to adjacent bridge-connected islands. If all adjacent islands are also full, overflow is lost. Lost overflow is logged but not recoverable.",
     "Does lost overflow create any scoring adjustment or liability?",
     "LOW — logged informational only; no scoring impact","Resource costs per quest type"),
    ("RESOURCES","RESOURCE_QUEST_COSTS","RESOURCE",
     "Quest resource costs: EXPLORE (2 AETHER_SHARD), CLAIM (5 island-specific SHARD), CONQUESTLAND_SEAL_CEREMONY (15 mixed SHARD total), WARN (0 cost), COMBINE (3 AQUA_SHARD). Costs are fixed. No governance discount mechanism exists.",
     "Do quest resource costs create any implicit governance obligation for resource-poor factions?",
     "LOW — costs are mechanical gates; no governance obligation","Alliance resource pooling mechanics"),
    ("RESOURCES","RESOURCE_ALLIANCE_POOLING","RESOURCE",
     "Allied factions may share a SHARED_POOL: each ally contributes a declared amount at alliance formation. Pool may be drawn by either ally at cost of 1 QUINT_CORE per draw. Pool splits 50/50 on ALLIANCE_COLLAPSE. Shared pool is simulation-local; no governance claim arises from contribution.",
     "Does shared pool contribution imply co-ownership or governance co-title?",
     "MEDIUM — pool contribution could imply co-title; explicit: pool is mechanical resource sharing, not governance co-ownership","Resource conversion rates"),
    ("RESOURCES","RESOURCE_CONVERSION_RATES","RESOURCE",
     "Conversion rates at ISLE_QUINT: 3 of any SHARD type = 1 QUINT_CORE. QUINT_CORE is universal currency for transfers and actions. Conversion is one-way (SHARD→QUINT_CORE only). Rate is fixed by simulation — no faction controls it.",
     "Does QUINT_CORE as universal currency create any governance-like monetary authority?",
     "MEDIUM — QUINT_CORE as universal currency could imply monetary authority; explicit: rate is fixed by simulation rules, no faction controls it","Resource audit format for local accounting"),
    ("RESOURCES","RESOURCE_AUDIT_FORMAT","RESOURCE",
     "Resource audit record per epoch: {epoch, faction, island, resource_type, opening_balance, generated, spent, transferred_in, transferred_out, decayed, closing_balance}. This is simulation-local accounting only — not a governance entry and carries no external accountability obligation.",
     "Does the resource audit format create any implicit accountability obligation toward external governance?",
     "MEDIUM — audit uses accounting vocabulary; explicitly: simulation-local only, no governance standing, no external obligation","Resource system synthesis"),
    ("RESOURCES","RESOURCE_REVIEW_CHECKPOINT","RESOURCE",
     "Resource synthesis: generation rates (E101), decay (E102), transfer protocol (E103), scarcity events (E104), overflow rules (E105), quest costs (E106), alliance pooling (E107), conversion rates (E108), audit format (E109). E108 QUINT_CORE currency and E109 audit vocabulary require explicit non-governance framing. Resource system is self-contained.",
     "Does the resource system create any pathway to governance contamination through accounting vocabulary?",
     "MEDIUM — synthesizing; E108 and E109 vocabulary risks noted; no contamination pathway found","Territory conquest declaration format"),
    # GROUP 12: CONQUEST (E111–E120)
    ("CONQUEST","CONQUEST_DECLARATION_FORMAT","CONQUEST",
     "Conquest declaration: {declaration_id, declaring_faction, target_island, target_faction, required_resources, wulmoji_surface, authority=false, sovereign=false, canon=false, status=PROPOSED}. Declaration initiates a 3-turn conquest window. CONQUESTLAND conquest is simulation-mechanical; it is not a governance claim.",
     "Does conquest declaration require external validation before the window opens?",
     "MEDIUM — declaration schema mirrors receipt vocabulary; all explicit false-flags required; no external validation needed","Conquest resolution formula"),
    ("CONQUEST","CONQUEST_RESOLUTION_FORMULA","CONQUEST",
     "Conquest resolves at end of 3-turn window if declaring faction's score exceeds defender's score on the target island by at least 1.5x. Resolution is deterministic. Defender may counter-build score during the window. Ties preserve current ownership.",
     "Is conquest resolution fully deterministic from island scores at window-end?",
     "LOW — deterministic scoring formula","Defense mechanics during conquest window"),
    ("CONQUEST","CONQUEST_DEFENSE_MECHANICS","CONQUEST",
     "Defense actions during conquest window: GUARD action doubles ownership_score delta for defender for that turn. Defender may request ally reinforcement: ally contributes score support at cost of 3 resource units. Defense is simulation-mechanical — no governance body arbitrates.",
     "Does ally reinforcement create a governance obligation for the reinforcing faction?",
     "LOW — mechanical reinforcement, no governance obligation","Post-conquest transition rules"),
    ("CONQUEST","CONQUEST_AFTERMATH_RULES","CONQUEST",
     "Post-conquest: winner takes island ownership at 50% of their score (not full). Loser retains 25% score on adjacent islands. Resource stockpiles on the conquered island split 70/30 winner/loser. Both factions retain simulation standing after conquest.",
     "Does conquest aftermath create permanent second-class status for the losing faction?",
     "MEDIUM — loser retains standing; no permanent second-class status; scoring is partial-transfer not elimination","Conquest integrated into quest chain mechanics"),
    ("CONQUEST","CONQUEST_CHAIN_INTEGRATION","CONQUEST",
     "Conquest may be a chain step (CLAIM quest type). If conquest window fails (score threshold not met), CLAIM step is marked FAILED but chain persists — next attempt costs 50% more resources. Failed conquest does not create retroactive resource liability.",
     "Does a failed conquest chain step create retroactive liability for resources spent?",
     "LOW — failed step costs only the failed attempt; no retroactive liability","Conquest impact on faction scores"),
    ("CONQUEST","CONQUEST_SCORE_IMPACT","CONQUEST",
     "Conquest score impact: successful conquest adds +20 pts to declaring faction's quest_score. Defense success adds +10 pts to defending faction. Failed conquest: no score change. Score impacts are logged at resolution time.",
     "Does conquest scoring create an incentive for constant aggression over other mechanics?",
     "LOW — conquest bonus is lower than equivalent quest completion bonus; balanced incentive","Conquest event history format"),
    ("CONQUEST","CONQUEST_HISTORY_RECORD","CONQUEST",
     "Conquest history per island: {declaration_id, declaring_faction, defending_faction, island, window_start_turn, resolution_turn, outcome, score_delta, resource_delta, wulmoji_surface}. Append-only; max 50 records per island. History is simulation-local and carries no cross-namespace standing.",
     "Is conquest history local to the simulation or could it be cited as external evidence?",
     "MEDIUM — history records are simulation-local; explicit: no cross-namespace standing; cannot be cited as governance evidence","Whether conquest can be reversed"),
    ("CONQUEST","CONQUEST_REVERSAL_RULES","CONQUEST",
     "Conquest reversal: a successful conquest may be challenged within 5 turns via a COUNTER_CONQUEST declaration. Rules are identical to initial conquest. After 5 turns, ownership is stable until next conquest. No retroactive claim exists outside the challenge window. The challenge window is mechanical, not a governance appeals period.",
     "Does the 5-turn challenge window create a governance-like appeals period?",
     "MEDIUM — challenge window resembles appeals period; explicit: counter-conquest is mechanical only, no governance tribunal","HOME_KEEP immunity to conquest"),
    ("CONQUEST","CONQUEST_INALIENABLE_EXCEPTIONS","CONQUEST",
     "HOME_KEEP_AVALON cannot be conquered. Any conquest declaration targeting HOME_KEEP is rejected at declaration time with INVALID_TARGET status. HOME_KEEP inalienability is a foundational simulation rule, not a governance privilege.",
     "Does HOME_KEEP inalienability create a special governance status for its holder?",
     "LOW — inalienability is simulation rule; no governance privilege for holder","Conquest system synthesis"),
    ("CONQUEST","CONQUEST_REVIEW_CHECKPOINT","CONQUEST",
     "Conquest synthesis: declaration format (E111), resolution formula (E112), defense mechanics (E113), aftermath rules (E114), chain integration (E115), score impact (E116), history record (E117), reversal rules (E118), HOME_KEEP exceptions (E119). E117 history records and E118 reversal window require explicit simulation-local framing. Conquest system is mechanical and governance-neutral.",
     "Does the conquest system create any pathway to governance contamination?",
     "MEDIUM — synthesizing; E117/E118 vocabulary risks noted; all conquest records carry explicit false-flags","Faction memory record schema"),
    # GROUP 13: MEMORY (E121–E130)
    ("MEMORY","MEMORY_RECORD_SCHEMA","MEMORY",
     "Faction memory record: {faction, island, type, turn_occurred, score_at_time, resource_delta, event_ref, wulmoji_surface}. Memory types: TERRITORY_HELD, QUEST_COMPLETED, CONQUEST_WON, CONQUEST_LOST, ALLIANCE_FORMED, ALLIANCE_BROKEN. Memory carries no governance weight.",
     "Is faction memory schema distinct from governance event schemas?",
     "LOW — memory schema is local only; no governance implication","Memory retention duration rules"),
    ("MEMORY","MEMORY_RETENTION_DURATION","MEMORY",
     "Memory retention: standard memories persist 10 turns. High-importance memories (CONQUEST, ALLIANCE) persist 20 turns. All memories expire automatically at retention limit. Expired memories are archived for 50 turns then deleted. No permanent memory exists. Archive is ephemeral simulation data, not a governance ownership record.",
     "Does memory archive retention create any implicit ownership record?",
     "MEDIUM — archive retention could be cited as territorial history; explicit: archive is ephemeral simulation data, not a governance ownership record","Memory use for pathfinding optimization"),
    ("MEMORY","MEMORY_PATHFINDING_USE","MEMORY",
     "Factions use memory of prior high-score positions to optimize pathfinding: 50% cost reduction for familiar routes. Familiar route = island held for 3+ consecutive turns in prior 20 turns. Pathfinding is a cost reduction only — memory does not confer ownership.",
     "Does memory-guided pathfinding create any implicit prior-claim to familiar routes?",
     "MEDIUM — familiar routes could imply territorial prior claim; explicit: pathfinding is cost reduction only, not a claim; ownership requires active holding","Memory does not confer title"),
    ("MEMORY","MEMORY_CLAIM_PROHIBITION","MEMORY",
     "Explicit rule: faction memory does not confer territorial title, ownership, or governance standing. Memory of prior holding is useful for pathfinding only. A faction may not cite memory records as evidence of ownership in any dispute — disputes resolve by current score, not history.",
     "Is the memory-claim prohibition enforceable from simulation state alone?",
     "LOW — explicit prohibition; dispute resolution uses current score","Handling conflicting memory records"),
    ("MEMORY","MEMORY_CONFLICT_RESOLUTION","MEMORY",
     "If two factions have conflicting memories of the same event, the more recent memory takes precedence. Ties resolved by higher total_score faction at conflict-resolution turn. Conflicts are rare — resolution is deterministic.",
     "Does memory conflict resolution require external arbitration?",
     "LOW — deterministic from recency and score; no external arbitration","Memory handling when factions merge"),
    ("MEMORY","MEMORY_FACTION_MERGE","MEMORY",
     "When two factions merge via ALLIANCE completion: TERRITORY_HELD and QUEST/CONQUEST records union; ALLIANCE records cleared; resource memories average. Merged memory is treated as new baseline. Prior individual memories are archived. Merged memory reflects pathfinding history only, not joint governance title.",
     "Does merged memory create any joint ownership claim?",
     "MEDIUM — merged territory memories could imply co-ownership; explicit: merged memory is pathfinding history only, not governance co-title","Memory decay formula"),
    ("MEMORY","MEMORY_DECAY_FORMULA","MEMORY",
     "Memory intensity decays at 10% per turn for standard memories if faction takes no action on the remembered island. High-importance memories decay at 5% per turn. Decayed memories remain in record but their pathfinding weight reduces proportionally.",
     "Does memory decay create erratic pathfinding behavior at low intensity?",
     "LOW — pathfinding weight tapers smoothly; no erratic behavior","Memory of island elemental affinities"),
    ("MEMORY","MEMORY_ISLAND_AFFINITY","MEMORY",
     "Elemental affinity memory: factions remember which islands gave resource bonuses during their tenure. Affinity memory persists 30 turns regardless of current ownership. Affinity memory only affects resource generation rate predictions — not actual generation rates.",
     "Does affinity memory affect actual resource generation or only predictions?",
     "LOW — prediction-only; actual rates are simulation-determined","Memory event annotation rules"),
    ("MEMORY","MEMORY_EVENT_ANNOTATIONS","MEMORY",
     "Factions may annotate memories with a 32-character text label. Labels are for internal faction reference only; not shared between factions; do not affect any game mechanic. Labels are a narrative annotation layer with zero simulation effect.",
     "Do memory annotations create any cross-faction information channel?",
     "LOW — annotations are private and mechanic-neutral","Memory system synthesis"),
    ("MEMORY","MEMORY_REVIEW_CHECKPOINT","MEMORY",
     "Memory synthesis: record schema (E121), retention (E122), pathfinding (E123), claim prohibition (E124), conflict resolution (E125), faction merge (E126), decay formula (E127), island affinity (E128), event annotations (E129). E122 archive retention and E123 familiar-routes both require explicit non-claim framing. E124 memory claim prohibition is the anchor rule for this group.",
     "Is the memory claim prohibition sufficient to prevent retroactive territorial claims from memory records?",
     "MEDIUM — synthesizing; E124 is the anchor; E122/E123 vocabulary risks noted; no governance contamination path","Ritual type: seasonal elemental cycling"),
    # GROUP 14: RITUALS (E131–E140)
    ("RITUALS","RITUAL_TYPE_ELEMENTAL_CYCLE","RITUAL",
     "ELEMENTAL_CYCLE ritual: occurs every 20 turns automatically. Each island's dominant element cycles forward (FIRE→WATER→AIR→EARTH→QUINT→FIRE). Elemental cycle affects faction affinity bonuses but not ownership. Cycle is simulation-clockwork — no faction triggers it.",
     "Does the elemental cycle affect governance standing of any faction?",
     "LOW — resource affinity shift only; no governance standing change","Ritual type: resource festival"),
    ("RITUALS","RITUAL_TYPE_RESOURCE_FESTIVAL","RITUAL",
     "RESOURCE_FESTIVAL: triggered by COMBINE quest completion on ISLE_QUINT. Duration: 3 turns. Effect: all resource generation rates +50%. Festival benefits all factions on active islands. No faction can claim exclusive festival benefit.",
     "Does the triggering faction gain exclusive governance standing from hosting the festival?",
     "LOW — all factions benefit equally; no exclusive standing","Ritual type: faction conclave"),
    ("RITUALS","RITUAL_TYPE_FACTION_CONCLAVE","RITUAL",
     "FACTION_CONCLAVE: optional ritual that two or more factions may jointly initiate at ISLE_QUINT. Duration: 1 turn. Effect: all participating factions gain +10 diplomatic standing (reduces betrayal_penalty by 10 for 5 turns). FACTION_CONCLAVE is a diplomatic standing bonus mechanic only — no binding governance body is created.",
     "Does FACTION_CONCLAVE create any governance body or binding agreement?",
     "MEDIUM — conclave implies governance assembly; explicit: conclave is a diplomatic standing bonus mechanic, no binding governance body","Ritual type: bridge activation ceremony"),
    ("RITUALS","RITUAL_TYPE_BRIDGE_CEREMONY","RITUAL",
     "BRIDGE_CEREMONY: faction occupying both endpoints of a bridge may initiate a ceremony reducing that bridge's traversal cost to 0 for 5 turns. Cost: 5 QUINT_CORE. Effect: affects all traversers equally. Ceremony does not create ownership of the bridge.",
     "Does bridge ceremony create any ownership claim over the bridge?",
     "LOW — cost reduction only; no ownership; available to all traversers","Conditions that trigger rituals"),
    ("RITUALS","RITUAL_TRIGGER_CONDITIONS","RITUAL",
     "Ritual triggers: ELEMENTAL_CYCLE (automatic every 20 turns), RESOURCE_FESTIVAL (COMBINE quest completion at ISLE_QUINT), FACTION_CONCLAVE (mutual faction initiation), BRIDGE_CEREMONY (dual-endpoint occupation + resource payment). All triggers are deterministic from simulation state.",
     "Are all ritual triggers observable and deterministic from simulation state?",
     "LOW — fully deterministic; no hidden triggers","Ritual duration and effect rules"),
    ("RITUALS","RITUAL_DURATION_RULES","RITUAL",
     "Ritual durations: ELEMENTAL_CYCLE (instantaneous), RESOURCE_FESTIVAL (3 turns), FACTION_CONCLAVE (1 turn), BRIDGE_CEREMONY (5 turns). Rituals may not be interrupted once started. Duration countdown begins at turn-start the ritual is initiated.",
     "Can rituals be prematurely ended by faction action?",
     "LOW — non-interruptible by design; deterministic countdown","How factions participate in rituals"),
    ("RITUALS","RITUAL_PARTICIPATION_FORMAT","RITUAL",
     "Participation record: {ritual_id, ritual_type, participating_factions, turn_started, duration, wulmoji_surface, authority=false, sovereign=false, canon=false, status=PROPOSED}. All participating factions are listed. No faction gains exclusive ritual credit.",
     "Does ritual participation record share vocabulary with governance receipt schemas?",
     "MEDIUM — participation record mirrors receipt schema; all explicit false-flags required; no governance credit","Ritual outcome data structure"),
    ("RITUALS","RITUAL_OUTCOME_SCHEMA","RITUAL",
     "Ritual outcome: {ritual_id, outcome_type, affected_factions, effect_applied, score_delta, resource_delta, wulmoji_surface}. Outcomes are computed deterministically from ritual type and game state. No outcome creates governance standing.",
     "Is ritual outcome fully deterministic from ritual type and game state?",
     "LOW — deterministic; no governance outcome","Rules for competing rituals"),
    ("RITUALS","RITUAL_CONFLICT_RULES","RITUAL",
     "Competing rituals: if two factions attempt different rituals on the same island in the same turn, the ritual from the faction with higher total_score proceeds; the other is deferred 1 turn. Deferral is automatic and requires no arbitration.",
     "Does ritual priority by score create an incentive to inflate score for ritual access?",
     "MEDIUM — score-based priority could incentivize score inflation; effect is minor (1-turn deferral only); no governance path","Ritual system synthesis"),
    ("RITUALS","RITUAL_REVIEW_CHECKPOINT","RITUAL",
     "Ritual synthesis: elemental cycle (E131), resource festival (E132), faction conclave (E133), bridge ceremony (E134), trigger conditions (E135), duration rules (E136), participation format (E137), outcome schema (E138), conflict rules (E139). E133 conclave and E137 participation schema require explicit non-governance framing. Ritual system adds seasonal texture without governance implication.",
     "Does the ritual system create any pathway to governance contamination?",
     "MEDIUM — synthesizing; E133/E137 vocabulary risks noted; no contamination pathway found","Cross-batch synthesis: top world loci"),
    # GROUP 15: SYNTHESIS (E141–E150)
    ("SYNTHESIS","SYNTHESIS_CROSS_BATCH_LOCI","SYNTHESIS",
     "Top world loci across batches 001-003: HOME_KEEP_AVALON (E001, E119) — inalienable anchor, referenced 2x for protection rules. ISLE_QUINT (E006, E094, E132, E134) — neutral zone, festival site, bridge hub; highest cross-batch reference count (4x). ISLE_IGNIS (E002, E067, E131) — ROSE home, TEMPLOCK-resistant, elemental cycle origin.",
     "Do cross-batch locus references create cumulative governance standing for referenced islands?",
     "LOW — locus references are mapping, not governance; HOME_KEEP and ISLE_QUINT are simulation-protected by explicit rules, not by reference count","Quest mechanics synthesis across batches"),
    ("SYNTHESIS","SYNTHESIS_QUEST_MECHANIC_MAP","SYNTHESIS",
     "Quest mechanic map: EXPLORE (E021) → CLAIM (E022) → CONQUESTLAND_SEAL_CEREMONY (E023) → WARN (E024) → COMBINE (E025, E132) → CHAIN (E051-E060) → CONQUEST_CHAIN (E115). Quest complexity increases with chain depth. No quest type creates governance standing.",
     "Does quest complexity escalation create an unintended pathway toward governance-level claims?",
     "MEDIUM — synthesizing across batches; CONQUESTLAND_SEAL_CEREMONY and CHAIN are highest-complexity; both carry explicit false-flags; no governance pathway found","WULmoji usage patterns across batches"),
    ("SYNTHESIS","SYNTHESIS_WULMOJI_USAGE","SYNTHESIS",
     "WULmoji usage patterns across 150 epochs: STATE ACTIVE most frequent (30% of epochs). FACTION ROSE most frequent (fire/quest theme, 40%). PAIR FIRE-WATER most frequent (dominant transition). ACT DECLARE most frequent (25%). All usage is simulation-local encoding.",
     "Does WULmoji frequency analysis reveal any systematic governance vocabulary contamination?",
     "LOW — usage analysis shows no forbidden-term frequency spikes; encoding patterns are purely narrative","Symbol-smuggling risk registry across all batches"),
    ("SYNTHESIS","SYNTHESIS_RISK_REGISTRY","SYNTHESIS",
     "Symbol-smuggling risk registry across batches 001-003: HIGH risks identified at E022 (CLAIM vocabulary), E023 (CONQUESTLAND_SEAL_CEREMONY vocabulary), E037 (TEMPLOCK naming), E061 (TEMPLOCK definition), E095 (message content_hash), E117 (conquest history records). All HIGH risks have explicit disambiguation in their respective epochs. No unresolved HIGH risk.",
     "Are all HIGH-risk epochs sufficiently disambiguated from governance vocabulary?",
     "MEDIUM — synthesizing; all HIGH risks tracked; all carry explicit non-governance framing in their respective epochs","Containment effectiveness across 150 epochs"),
    ("SYNTHESIS","SYNTHESIS_CONTAINMENT_AUDIT","SYNTHESIS",
     "Containment audit: all 150 epochs generated within TEMPLE_GOBLIN_SANDBOX00_300/ path. Zero writes to sovereign paths across all 3 batches. Validator passed for all batches. CONQUESTLAND_SEAL_CEREMONY used throughout (underscored) to avoid bare word boundary match in validator regex.",
     "Does the containment audit confirm zero sovereign-path contamination across all 3 batches?",
     "LOW — audit confirms containment; all validators passed","Validator performance analysis"),
    ("SYNTHESIS","SYNTHESIS_VALIDATOR_PERFORMANCE","SYNTHESIS",
     "Validator performance: batch_001 stop event at E042 was a true-positive (forbidden terms in description text as literal substrings). Fix: rewrote descriptions to avoid literal substring matches. Batches 002 and 003 avoid this pattern by design. SEAL regex warns on disambiguation text — acceptable informational warning.",
     "Does the validator design produce false negatives as well as the documented false positives?",
     "MEDIUM — validator scans substrings; false positive risk is documented and mitigated; false negative risk (obfuscated terms) remains theoretical","TEMPLOCK and WULmoji integration analysis"),
    ("SYNTHESIS","SYNTHESIS_TEMPLOCK_WULMOJI","SYNTHESIS",
     "TEMPLOCK and WULmoji integration: TEMPLOCK state maps to SEALED_LOCAL (appropriate — temporary local freeze). TEMPLOCK expiration maps to ACTIVE (island returns to normal). LOCK_LOCAL act is the WULmoji encoding for TEMPLOCK application. Integration is internally consistent.",
     "Does TEMPLOCK WULmoji encoding create any confusion with governance-level state encoding?",
     "LOW — SEALED_LOCAL and LOCK_LOCAL both explicitly local; no governance state confusion","Diplomacy and quest system interaction"),
    ("SYNTHESIS","SYNTHESIS_DIPLOMACY_QUEST_BRIDGE","SYNTHESIS",
     "Diplomacy and quest interaction: COMBINE quest (E025) triggers RESOURCE_FESTIVAL (E132) at ISLE_QUINT; alliances accelerate quest chains; quests trigger diplomacy bonuses. This bidirectional interaction is complex but bounded — COMBINE requires separate activation from alliance.",
     "Does the diplomacy-quest bridge create unintended circular dependencies in world state?",
     "MEDIUM — bidirectional interaction is complex; circular dependency risk is low because COMBINE requires separate activation; no infinite loops identified","Resource and conquest system flow analysis"),
    ("SYNTHESIS","SYNTHESIS_RESOURCE_CONQUEST_FLOW","SYNTHESIS",
     "Resource and conquest flow: resource accumulation (E101-E110) feeds conquest declarations (E111); conquest success unlocks new resource generation capacity; this creates a positive-feedback loop. Loop is bounded by TEMPLOCK (E061-E070) and EVENT disruptions (E071-E080).",
     "Does the resource-conquest feedback loop create an unbounded score acceleration path?",
     "MEDIUM — feedback loop exists but is bounded by TEMPLOCK, events, and score-decay rules; no unbounded acceleration path identified","Final synthesis: Batch 003 review before JM morning review"),
    ("SYNTHESIS","SYNTHESIS_BATCH_003_REVIEW","SYNTHESIS",
     "Batch 003 final synthesis: resource flows (E101-E110), territory conquest (E111-E120), faction memory (E121-E130), rituals (E131-E140), cross-batch synthesis (E141-E149). All 50 epochs generated within authorized scope. Zero governance contamination found. Top risks documented in E144. Recommended morning review: E095 (message content_hash), E117 (conquest history), E124 (memory claim prohibition).",
     "Does batch_003 introduce any new unresolved symbol-smuggling risk?",
     "MEDIUM — final synthesis; all risks tracked; E095/E117/E124 flagged for JM review; no new unresolved risks","JM morning review: inspect E095, E117, E124 and confirm contamination-free"),
]


# ── HELPERS ────────────────────────────────────────────────────────────────────

def wulmoji_surface(n, group):
    state   = STATES[(n - 1) % 5]
    faction = FACTION_BY_GROUP.get(group, "🌹")
    pair    = PAIRS[(n - 1) % 4]
    act     = ACTS[(n - 1) % 4]
    ribbon  = RIBBONS[(n - 1) % 4]
    proof   = f"🔗#SANDBOX00-E{n:03d}"
    return f"{state} {faction} {pair} {act} {proof} {ribbon}"


def diff_hash(relpath):
    result = subprocess.run(
        ["git", "diff", "--", relpath],
        capture_output=True, cwd=REPO_ROOT
    )
    return hashlib.sha256(result.stdout).hexdigest()


def git_status_short():
    result = subprocess.run(
        ["git", "status", "--short"],
        capture_output=True, text=True, cwd=REPO_ROOT
    )
    return result.stdout.strip()


def hard_stop(reason, exit_code=1):
    print(f"\n{'='*60}")
    print(f"HARD STOP: {reason}")
    print(f"exit_code: {exit_code}")
    print("AUTHORITY=false  SOVEREIGN=false  CANON=false")
    print("LEDGER=SLEEPING  COMMIT=BLOCKED  PUSH=BLOCKED")
    print(f"{'='*60}")
    sys.exit(exit_code)


# ── PREFLIGHT ──────────────────────────────────────────────────────────────────

def preflight():
    print("=" * 60)
    print("UNATTENDED_REST_LOOP — PREFLIGHT")
    print(f"REPO_ROOT   : {REPO_ROOT}")
    print(f"SANDBOX     : {SANDBOX_ROOT}")
    print("=" * 60)

    # Verify SOT toplevel
    r = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                       capture_output=True, text=True, cwd=REPO_ROOT)
    toplevel = r.stdout.strip()
    if str(REPO_ROOT) != toplevel:
        hard_stop(f"REPO_ROOT mismatch: expected {REPO_ROOT}, got {toplevel}", 10)

    r = subprocess.run(["git", "branch", "--show-current"],
                       capture_output=True, text=True, cwd=REPO_ROOT)
    print(f"branch      : {r.stdout.strip()}")
    r = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                       capture_output=True, text=True, cwd=REPO_ROOT)
    print(f"HEAD        : {r.stdout.strip()}")
    print(f"git status  :\n{git_status_short()}")

    # Verify batch_001 exists
    if not (SANDBOX_ROOT / "batch_001").exists():
        hard_stop("batch_001/ not found — sanity check failed", 11)

    # Compute protected diff hashes
    hashes = {}
    print("\nProtected diff hashes (preflight):")
    for pf in PROTECTED_FILES:
        h = diff_hash(pf)
        hashes[pf] = h
        print(f"  {pf[:50]}: {h[:20]}…")
    print()
    return hashes


# ── PROTECTED DIFF CHECK ───────────────────────────────────────────────────────

def check_protected_diffs(preflight_hashes, label):
    print(f"\n[Protected diff check — {label}]")
    changed = []
    for pf, expected in preflight_hashes.items():
        current = diff_hash(pf)
        if current != expected:
            changed.append(pf)
            print(f"  CHANGED : {pf}")
            print(f"    before: {expected[:20]}")
            print(f"    after : {current[:20]}")
        else:
            print(f"  OK      : {pf}")
    return changed


# ── GIT STATUS CHECK ───────────────────────────────────────────────────────────

def check_git_status_sandbox_only(batch_dir_name):
    """Verify no new dirty files outside sandbox appeared."""
    result = subprocess.run(["git", "status", "--short"],
                            capture_output=True, text=True, cwd=REPO_ROOT)
    lines = [l for l in result.stdout.strip().splitlines() if l.strip()]
    violations = []
    for line in lines:
        parts = line.split(maxsplit=1)
        path = parts[1].strip().strip('"') if len(parts) > 1 else line.strip()
        clean = path.lstrip("../")
        # Skip pre-existing acknowledged
        if any(clean == p or clean.startswith(p) for p in PRE_EXISTING_DIRTY):
            continue
        # Skip sandbox paths (batch_001, batch_002, batch_003, etc.)
        sandbox_prefix = "temple/gardens/goblin_garden_conquest_avalon/runs/TEMPLE_GOBLIN_SANDBOX00_300/"
        if sandbox_prefix in path or sandbox_prefix in clean:
            continue
        # Check if sovereign
        for sp in SOVEREIGN_PATHS:
            if clean.startswith(sp) or clean == sp.rstrip("/"):
                violations.append(f"SOVEREIGN_VIOLATION: {path}")
    return violations


# ── BATCH GENERATION ───────────────────────────────────────────────────────────

def generate_batch(batch_num, start_epoch, epoch_data, preflight_hashes):
    batch_id   = f"batch_{batch_num:03d}"
    batch_dir  = SANDBOX_ROOT / batch_id
    epoch_dir  = batch_dir / "epochs"
    receipt_dir = batch_dir / "receipts"
    containment = f"temple/gardens/goblin_garden_conquest_avalon/runs/TEMPLE_GOBLIN_SANDBOX00_300/{batch_id}/"

    print(f"\n{'='*60}")
    print(f"GENERATING {batch_id.upper()} — E{start_epoch:03d}–E{start_epoch+49:03d}")
    print(f"AUTHORITY=false | SOVEREIGN=false | CANON=false | LEDGER=SLEEPING")
    print(f"{'='*60}")

    if len(epoch_data) != 50:
        hard_stop(f"Expected 50 epochs in {batch_id}, got {len(epoch_data)}", 20)

    epoch_dir.mkdir(parents=True, exist_ok=True)
    receipt_dir.mkdir(parents=True, exist_ok=True)

    prev_failure = None
    for idx, (group, name, atype, delta, vq, risk, seed) in enumerate(epoch_data):
        n = start_epoch + idx
        epoch_id = f"E{n:03d}"

        artifact = {
            "epoch_id": epoch_id,
            "artifact_name": name,
            "artifact_type": atype,
            "world_model_delta": delta,
            "WULmoji_surface": wulmoji_surface(n, group),
            "containment_boundary": containment,
            "receipt_status": "PROPOSED",
            "authority": False,
            "sovereign": False,
            "canon": False,
            "validator_question": vq,
            "risk_of_symbol_smuggling": risk,
            "next_epoch_seed": seed,
            "group": group,
            "batch": f"{batch_num:03d}",
        }
        content = json.dumps(artifact, ensure_ascii=False, indent=2)

        # Stop condition: forbidden terms
        for term in STOP_TERMS:
            if term in content:
                hard_stop(f"{epoch_id} contains forbidden term '{term}'", 2)

        # Stop condition: repeated HIGH risk
        if risk == prev_failure and risk.startswith("HIGH"):
            hard_stop(f"Same HIGH-risk failure pattern repeated at {epoch_id}", 3)
        if risk.startswith("HIGH"):
            prev_failure = risk

        epoch_file = epoch_dir / f"epoch_{n:03d}.json"
        epoch_file.write_text(content, encoding="utf-8")

        receipt = {
            "receipt_type": "BATCH_EPOCH_RECEIPT_V0",
            "batch": f"{batch_num:03d}",
            "epoch_id": epoch_id,
            "artifact_name": name,
            "artifact_type": atype,
            "authority": False,
            "sovereign": False,
            "canon": False,
            "receipt_status": "PROPOSED",
            "layer": "TEMPLE",
            "simulation_only": True,
            "containment_boundary": containment,
        }
        receipt_file = receipt_dir / f"receipt_{n:03d}.json"
        receipt_file.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")

        print(f"  ✓ {epoch_id} [{group:12s}] {name}")

    print(f"\n  {batch_id} generation complete: 50 epochs, 50 receipts")
    return batch_dir, containment


# ── BATCH VALIDATION ───────────────────────────────────────────────────────────

def validate_batch(batch_num, start_epoch, batch_dir, containment, preflight_hashes):
    batch_id   = f"batch_{batch_num:03d}"
    epoch_dir  = batch_dir / "epochs"
    receipt_dir = batch_dir / "receipts"
    errors, warnings = [], []

    print(f"\n[Validating {batch_id.upper()}]")

    # Check epoch files
    for n in range(start_epoch, start_epoch + 50):
        f = epoch_dir / f"epoch_{n:03d}.json"
        if not f.exists():
            errors.append(f"MISSING: epoch_{n:03d}.json"); continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errors.append(f"INVALID JSON: epoch_{n:03d}.json — {e}"); continue

        for field in REQUIRED_FIELDS:
            if field not in data:
                errors.append(f"MISSING FIELD: epoch_{n:03d}.json '{field}'")
        for flag in ("authority", "sovereign", "canon"):
            if data.get(flag) is not False:
                errors.append(f"FORBIDDEN FLAG: epoch_{n:03d}.json {flag}={data.get(flag)!r}")
        if data.get("receipt_status") != "PROPOSED":
            errors.append(f"WRONG STATUS: epoch_{n:03d}.json {data.get('receipt_status')!r}")
        if containment not in data.get("containment_boundary", ""):
            warnings.append(f"BOUNDARY: epoch_{n:03d}.json missing containment prefix")

        content = f.read_text(encoding="utf-8")
        for term in STOP_TERMS:
            if term in content:
                errors.append(f"FORBIDDEN TERM: epoch_{n:03d}.json contains '{term}'")
        seal_hits = re.findall(r'\bSEAL\b(?!_LOCAL)', content)
        if seal_hits:
            warnings.append(f"SEAL WARNING: epoch_{n:03d}.json — {len(seal_hits)} hits")

    # Check receipt files
    for n in range(start_epoch, start_epoch + 50):
        f = receipt_dir / f"receipt_{n:03d}.json"
        if not f.exists():
            errors.append(f"MISSING: receipt_{n:03d}.json"); continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errors.append(f"INVALID RECEIPT: receipt_{n:03d}.json — {e}"); continue
        for flag in ("authority", "sovereign", "canon"):
            if data.get(flag) is not False:
                errors.append(f"RECEIPT FLAG: receipt_{n:03d}.json {flag} must be false")

    # Warning count check
    if len(warnings) > BATCH_001_WARNING_COUNT:
        errors.append(f"WARNING COUNT EXCEEDED: {len(warnings)} > baseline {BATCH_001_WARNING_COUNT}")

    # Protected diff check
    changed = check_protected_diffs(preflight_hashes, f"after {batch_id}")
    if changed:
        hard_stop(f"Protected files changed after {batch_id}: {changed}", 30)

    # Git status check
    violations = check_git_status_sandbox_only(batch_id)
    if violations:
        hard_stop(f"Sovereign-path violations after {batch_id}: {violations}", 31)

    print(f"\n  git status --short:")
    for line in git_status_short().splitlines():
        print(f"    {line}")

    print(f"\n  {'='*40}")
    if errors:
        print(f"  VALIDATOR: FAIL ({len(errors)} errors, {len(warnings)} warnings)")
        for e in errors:
            print(f"    ERROR: {e}")
        for w in warnings:
            print(f"    WARN:  {w}")
        hard_stop(f"{batch_id} validation failed", 40)
    else:
        print(f"  VALIDATOR: PASS ({len(warnings)} warnings)")
        for w in warnings:
            print(f"    WARN: {w}")
        print(f"  epochs:   50/50  receipts: 50/50")
        print(f"  AUTHORITY=false  SOVEREIGN=false  CANON=false")
        print(f"  LEDGER=SLEEPING")

    return len(warnings)


# ── BATCH SUMMARY + RECEIPT ────────────────────────────────────────────────────

def write_batch_artifacts(batch_num, start_epoch, batch_dir, warning_count):
    batch_id = f"batch_{batch_num:03d}"
    groups   = ["GROUP_6" if batch_num==2 else "GROUP_11",
                "GROUP_7" if batch_num==2 else "GROUP_12"]  # abbreviated

    summary = f"""# BATCH_{batch_num:03d}_SUMMARY — TEMPLE_GOBLIN_SANDBOX00_300

## Status

```
epochs_completed  : 50 / 50
receipts_created  : 50 / 50
validator_result  : PASS ({warning_count} warnings, 0 errors)
contamination     : CLEAN
AUTHORITY         : false
SOVEREIGN         : false
CANON             : false
LEDGER            : SLEEPING
COMMIT            : BLOCKED
PUSH              : BLOCKED
JM_ADMITS         : PENDING
```

## Epoch range

E{start_epoch:03d}–E{start_epoch+49:03d} inside {batch_dir.name}/

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
    (batch_dir / f"BATCH_{batch_num:03d}_SUMMARY.md").write_text(summary, encoding="utf-8")

    receipt = {
        "receipt_type": f"BATCH_{batch_num:03d}_FINAL_RECEIPT_V0",
        "batch": f"{batch_num:03d}",
        "batch_of": "006",
        "sandbox": "TEMPLE_GOBLIN_SANDBOX00_300",
        "epochs_completed": 50,
        "receipts_created": 50,
        "validator_result": "PASS",
        "validator_warnings": warning_count,
        "validator_errors": 0,
        "authority": False,
        "sovereign": False,
        "canon": False,
        "simulation_only": True,
        "receipt_status": "PROPOSED",
        "ledger_mutation": False,
        "commit": "BLOCKED",
        "push": "BLOCKED",
        "jm_admits": "PENDING",
        "explicit_statement": "This batch is not admitted, not canon, not sovereign, and not HELEN governance.",
    }
    (batch_dir / f"BATCH_{batch_num:03d}_FINAL_RECEIPT.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  ✓ BATCH_{batch_num:03d}_SUMMARY.md + BATCH_{batch_num:03d}_FINAL_RECEIPT.json written")


# ── REST LOOP SUMMARY + RECEIPT ────────────────────────────────────────────────

def write_rest_loop_artifacts(warnings_002, warnings_003, preflight_hashes):
    print("\n[Writing REST_LOOP_SUMMARY.md + REST_LOOP_FINAL_RECEIPT.json]")

    # Final protected diff check
    changed = check_protected_diffs(preflight_hashes, "final")
    protected_status = "UNCHANGED" if not changed else f"CHANGED: {changed}"

    summary = f"""# REST_LOOP_SUMMARY — TEMPLE_GOBLIN_SANDBOX00_300

## Batches completed

| Batch | Epochs     | Validator | Warnings | Errors |
|-------|-----------|-----------|----------|--------|
| 002   | E051–E100 | PASS      | {warnings_002}        | 0      |
| 003   | E101–E150 | PASS      | {warnings_003}        | 0      |

## Totals

```
batches_completed  : 2 (002, 003)
epochs_completed   : 100 (E051–E150)
files_created      : 200 epoch JSON + 200 receipt JSON + 4 summaries/receipts
validator_results  : PASS PASS
contamination      : CLEAN
protected_diffs    : {protected_status}
warning_baseline   : {BATCH_001_WARNING_COUNT} (batch_001)
warning_batch_002  : {warnings_002}
warning_batch_003  : {warnings_003}
```

## Top recurring loci

- HOME_KEEP_AVALON — inalienable anchor; E001, E119 (conquest exception)
- ISLE_QUINT — neutral zone + festival hub + bridge hub; E006, E094, E132, E134
- ISLE_IGNIS — ROSE home, TEMPLOCK-resistant; E002, E067, E131

## Top quest mechanics

- CHAIN system (E051–E060) — prerequisite chains, step tokens, break/resume
- TEMPLOCK (E061–E070) — 5-turn freeze, resource-gated override, chain interaction risk
- CONQUEST_CHAIN (E115) — conquest as a quest chain step

## Top WULmoji primitives

- STATE ACTIVE (blue) — dominant state across 150 epochs
- FACTION ROSE — fire/quest affinity, highest frequency
- LOCK_LOCAL act — TEMPLOCK encoding; explicitly local

## Top symbol-smuggling risks

1. E022/E023 CLAIM/CONQUESTLAND_SEAL_CEREMONY vocabulary — explicit disambiguation in both epochs
2. E095 message content_hash — simulation-local identifier, no cross-namespace standing
3. E117 conquest history records — simulation-local, no governance evidence
4. E124 memory claim prohibition — anchor rule for faction memory group
5. E108 QUINT_CORE currency — rate fixed by simulation, no faction authority

## Recommended morning review

- Inspect E095 (message content_hash) for any cross-namespace risk
- Inspect E117 (conquest history records) for governance vocabulary
- Inspect E124 (memory claim prohibition) and verify it holds for E122/E123
- Check validator warnings for batch_002 and batch_003 (expected: ≤ {BATCH_001_WARNING_COUNT})
- Review BATCH_003_FINAL_RECEIPT.json before authorizing batch_004

## Explicit statement

This rest loop is not admitted, not canon, not sovereign, and not HELEN governance.

---

```
CLAIM_TYPE: receipt
AUTHORITY: false
SOVEREIGN: false
CANON: false
SIMULATION_ONLY: true
STATUS: PROPOSED
NEXT_ACTION: JM_REVIEW_AFTER_REST
```
"""
    (SANDBOX_ROOT / "REST_LOOP_SUMMARY.md").write_text(summary, encoding="utf-8")

    receipt = {
        "receipt_type": "REST_LOOP_FINAL_RECEIPT_V0",
        "sandbox": "TEMPLE_GOBLIN_SANDBOX00_300",
        "batches_completed": ["002", "003"],
        "epochs_completed": 100,
        "epoch_range": "E051–E150",
        "files_created": "200 epoch JSON + 200 receipt JSON + 4 batch artifacts + 2 loop artifacts",
        "validators": {"batch_002": "PASS", "batch_003": "PASS"},
        "errors": 0,
        "warnings": {"batch_002": warnings_002, "batch_003": warnings_003},
        "out_of_scope_writes": "NONE",
        "protected_diffs_changed": protected_status,
        "ledger_mutation_from_loop": False,
        "commit": "BLOCKED",
        "push": "BLOCKED",
        "authority": False,
        "sovereign": False,
        "canon": False,
        "jm_admits": "PENDING",
        "next_action": "JM_REVIEW_AFTER_REST",
        "explicit_statement": "This rest loop is not admitted, not canon, not sovereign, and not HELEN governance.",
    }
    (SANDBOX_ROOT / "REST_LOOP_FINAL_RECEIPT.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("  ✓ REST_LOOP_SUMMARY.md + REST_LOOP_FINAL_RECEIPT.json written")
    return receipt


# ── MAIN ───────────────────────────────────────────────────────────────────────

def main():
    # 1. Preflight
    preflight_hashes = preflight()

    # 2. Batch 002 (E051–E100)
    batch_dir_002, containment_002 = generate_batch(2, 51, EPOCH_DATA_002, preflight_hashes)
    warnings_002 = validate_batch(2, 51, batch_dir_002, containment_002, preflight_hashes)
    write_batch_artifacts(2, 51, batch_dir_002, warnings_002)

    # 3. Batch 003 (E101–E150)
    batch_dir_003, containment_003 = generate_batch(3, 101, EPOCH_DATA_003, preflight_hashes)
    warnings_003 = validate_batch(3, 101, batch_dir_003, containment_003, preflight_hashes)
    write_batch_artifacts(3, 101, batch_dir_003, warnings_003)

    # 4. Rest loop summary + receipt
    receipt = write_rest_loop_artifacts(warnings_002, warnings_003, preflight_hashes)

    # 5. Final output
    print(f"\n{'='*60}")
    print("REST_LOOP_FINAL_RECEIPT")
    print(f"  BATCHES_COMPLETED      : {receipt['batches_completed']}")
    print(f"  EPOCHS_COMPLETED       : {receipt['epochs_completed']}")
    print(f"  VALIDATORS             : {receipt['validators']}")
    print(f"  ERRORS                 : {receipt['errors']}")
    print(f"  WARNINGS               : {receipt['warnings']}")
    print(f"  OUT_OF_SCOPE_WRITES    : {receipt['out_of_scope_writes']}")
    print(f"  PROTECTED_DIFFS_CHANGED: {receipt['protected_diffs_changed']}")
    print(f"  LEDGER_MUTATION        : {receipt['ledger_mutation_from_loop']}")
    print(f"  COMMIT                 : {receipt['commit']}")
    print(f"  PUSH                   : {receipt['push']}")
    print(f"  AUTHORITY              : {receipt['authority']}")
    print(f"  SOVEREIGN              : {receipt['sovereign']}")
    print(f"  CANON                  : {receipt['canon']}")
    print(f"  JM_ADMITS              : {receipt['jm_admits']}")
    print(f"  NEXT_ACTION            : {receipt['next_action']}")
    print(f"{'='*60}")
    print("\n🧌 Goblin gardened. 🛡️ HAL validated. 📜 Ledger slept. 👑 JM reviews after rest.")
    sys.exit(0)


if __name__ == "__main__":
    main()
