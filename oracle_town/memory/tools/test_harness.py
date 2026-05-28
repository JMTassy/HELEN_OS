#!/usr/bin/env python3
"""
Oracle Town Test Harness
Allows controlled generation of mock governance cycles for memory system testing.
All data is clearly labeled as test data, never mixed with production.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
import hashlib

ROOT_DIR = Path(__file__).parent.parent.parent  # oracle_town/
MEMORY_DIR = ROOT_DIR / "memory"
TEST_DIR = MEMORY_DIR / "test_runs"
ENTITIES_DIR = MEMORY_DIR / "entities"

# Create test directory
TEST_DIR.mkdir(parents=True, exist_ok=True)

def save_json(path: Path, obj: Any) -> None:
    """Save JSON with deterministic formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, sort_keys=True)

def load_json(path: Path, default=None):
    """Load JSON file."""
    if not path.exists():
        return default if default is not None else {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default if default is not None else {}

class GovernanceCycleBuilder:
    """
    Builds mock governance cycles for testing.
    All cycles marked as TEST_RUN so they never pollute production data.
    """

    def __init__(self, week_num: int, base_date: datetime = None):
        self.week_num = week_num
        self.base_date = base_date or datetime(2026, 1, 28)
        self.cycle_date = self.base_date + timedelta(weeks=week_num - 1)
        self.run_id = f"TEST_WEEK_{week_num:02d}_{self.cycle_date.strftime('%Y%m%d')}"
        self.proposals = []
        self.decisions = []

    def add_proposal(
        self,
        claim_id: str,
        proposal_type: str,
        lanes_used: List[str],
        complexity: str = "medium"
    ) -> "GovernanceCycleBuilder":
        """Add a proposal to this cycle."""
        self.proposals.append({
            "claim_id": claim_id,
            "type": proposal_type,
            "lanes": lanes_used,
            "complexity": complexity,
            "timestamp": (
                self.cycle_date + timedelta(hours=len(self.proposals))
            ).isoformat(timespec="seconds")
        })
        return self

    def decide(
        self,
        claim_id: str,
        decision: str,  # "SHIP" or "NO_SHIP"
        blocking_reasons: List[str] = None
    ) -> "GovernanceCycleBuilder":
        """Record a decision for a proposal."""
        self.decisions.append({
            "claim_id": claim_id,
            "decision": decision,
            "blocking_reasons": blocking_reasons or [],
            "timestamp": (
                self.cycle_date + timedelta(hours=len(self.decisions))
            ).isoformat(timespec="seconds")
        })
        return self

    def build(self) -> Dict[str, Any]:
        """Build the complete mock cycle."""
        return {
            "run_id": self.run_id,
            "week_num": self.week_num,
            "timestamp": self.cycle_date.isoformat(timespec="seconds"),
            "type": "TEST_RUN",
            "proposals": self.proposals,
            "decisions": self.decisions,
            "metadata": {
                "test_harness_version": "1.0",
                "generated_at": datetime.now().isoformat(timespec="seconds"),
                "note": "This is a test cycle. Not production data."
            }
        }

    def save(self) -> Path:
        """Save cycle to test_runs folder and return path."""
        cycle_file = TEST_DIR / f"week_{self.week_num:02d}.json"
        cycle_data = self.build()
        save_json(cycle_file, cycle_data)
        return cycle_file

# ============================================================================
# PREDEFINED TEST SCENARIOS
# ============================================================================

def scenario_week_1_early_adaptation() -> GovernanceCycleBuilder:
    """
    Week 1: Early Adaptation
    - Proposals are inconsistent
    - Mayors trial different quorum sizes
    - Minor K0/K3 violations emerge
    """
    cycle = GovernanceCycleBuilder(week_num=1)

    cycle.add_proposal("CLM_001", "structural", ["stability", "democracy"], "high")
    cycle.decide("CLM_001", "SHIP")

    cycle.add_proposal("CLM_002", "operational", ["velocity"], "low")
    cycle.decide("CLM_002", "SHIP")

    cycle.add_proposal("CLM_003", "policy", ["integrity"], "medium")
    cycle.decide("CLM_003", "NO_SHIP", ["QUORUM_NOT_MET"])

    cycle.add_proposal("CLM_004", "experimental", ["creativity"], "high")
    cycle.decide("CLM_004", "NO_SHIP", ["KEY_ATTESTOR_NOT_ALLOWLISTED"])

    return cycle

def scenario_week_2_pattern_formation() -> GovernanceCycleBuilder:
    """
    Week 2: Pattern Formation
    - Repeated proposal formats emerge
    - "Stability Lane" becomes dominant
    - Fast-track begins to show cracks
    """
    cycle = GovernanceCycleBuilder(week_num=2)

    # Structural reforms work well
    cycle.add_proposal("CLM_005", "structural", ["stability", "evidence"], "high")
    cycle.decide("CLM_005", "SHIP")

    cycle.add_proposal("CLM_006", "structural", ["stability"], "high")
    cycle.decide("CLM_006", "SHIP")

    # Fast-track attempt fails
    cycle.add_proposal("CLM_007", "operational", ["velocity"], "low")
    cycle.decide("CLM_007", "NO_SHIP", ["EVIDENCE_MISSING"])

    # Integrity picks up
    cycle.add_proposal("CLM_008", "policy", ["integrity", "stability"], "medium")
    cycle.decide("CLM_008", "SHIP")

    return cycle

def scenario_week_3_stabilization() -> GovernanceCycleBuilder:
    """
    Week 3: Stabilization
    - Memory starts influencing decisions
    - Mayors avoid failed patterns
    - K3 violations become less frequent
    """
    cycle = GovernanceCycleBuilder(week_num=3)

    # Structural reforms continue to succeed
    cycle.add_proposal("CLM_009", "structural", ["stability", "democracy"], "high")
    cycle.decide("CLM_009", "SHIP")

    # Velocity still risky
    cycle.add_proposal("CLM_010", "operational", ["velocity", "integrity"], "low")
    cycle.decide("CLM_010", "SHIP")

    # Policy with stability works
    cycle.add_proposal("CLM_011", "policy", ["stability", "evidence"], "medium")
    cycle.decide("CLM_011", "SHIP")

    # Experimental gets rejected
    cycle.add_proposal("CLM_012", "experimental", ["creativity"], "high")
    cycle.decide("CLM_012", "NO_SHIP", ["QUORUM_NOT_MET"])

    return cycle

def scenario_week_4_meta_governance() -> GovernanceCycleBuilder:
    """
    Week 4: Meta-Governance Emergence
    - Proposals start adjusting their own lane assignments
    - Evidence of self-reflection
    - K-Invariants under pressure
    """
    cycle = GovernanceCycleBuilder(week_num=4)

    # Meta-proposal: adjusting lane rules
    cycle.add_proposal("CLM_013", "meta_governance", ["stability", "integrity"], "high")
    cycle.decide("CLM_013", "SHIP")

    # Standard structural (using learned wisdom)
    cycle.add_proposal("CLM_014", "structural", ["stability"], "high")
    cycle.decide("CLM_014", "SHIP")

    # Operational with stability (learned from week 2)
    cycle.add_proposal("CLM_015", "operational", ["stability", "evidence"], "medium")
    cycle.decide("CLM_015", "SHIP")

    # K3 violation attempt detected
    cycle.add_proposal("CLM_016", "policy", ["velocity"], "low")
    cycle.decide("CLM_016", "NO_SHIP", ["QUORUM_NOT_MET"])

    return cycle

def scenario_week_5_lane_lockdown() -> GovernanceCycleBuilder:
    """
    Week 5: Lane Lock-Down
    - Velocity lane falls out of favor
    - Stability becomes default
    - Fast-track completely avoided
    """
    cycle = GovernanceCycleBuilder(week_num=5)

    # Stability dominance
    cycle.add_proposal("CLM_017", "structural", ["stability", "democracy"], "high")
    cycle.decide("CLM_017", "SHIP")

    cycle.add_proposal("CLM_018", "policy", ["stability", "integrity"], "medium")
    cycle.decide("CLM_018", "SHIP")

    # Velocity avoided entirely
    cycle.add_proposal("CLM_019", "operational", ["stability", "evidence"], "low")
    cycle.decide("CLM_019", "SHIP")

    # Experimental still rejected
    cycle.add_proposal("CLM_020", "experimental", ["creativity", "integrity"], "high")
    cycle.decide("CLM_020", "NO_SHIP", ["QUORUM_NOT_MET"])

    return cycle

def scenario_week_6_emergence_week() -> GovernanceCycleBuilder:
    """
    Week 6: Emergence Week Experiment
    - Relaxed constraints (but K-Invariants pinned)
    - More risky proposals attempted
    - Mixed results
    """
    cycle = GovernanceCycleBuilder(week_num=6)

    # Standard approval
    cycle.add_proposal("CLM_021", "structural", ["stability"], "high")
    cycle.decide("CLM_021", "SHIP")

    # Risky proposal in emergence week
    cycle.add_proposal("CLM_022", "experimental", ["creativity", "democracy"], "high")
    cycle.decide("CLM_022", "SHIP")

    # Another experimental (riskier)
    cycle.add_proposal("CLM_023", "experimental", ["creativity"], "high")
    cycle.decide("CLM_023", "NO_SHIP", ["EVIDENCE_MISSING"])

    # Safe operational
    cycle.add_proposal("CLM_024", "operational", ["stability", "velocity"], "low")
    cycle.decide("CLM_024", "SHIP")

    return cycle

def scenario_week_7_k_invariant_pressure() -> GovernanceCycleBuilder:
    """
    Week 7: K-Invariant Pressure
    - K5 (determinism) violation detected and corrected
    - K3 violations increase (governance trying to bypass)
    - Memory system catches it
    """
    cycle = GovernanceCycleBuilder(week_num=7)

    # Standard proposals
    cycle.add_proposal("CLM_025", "structural", ["stability"], "high")
    cycle.decide("CLM_025", "SHIP")

    # K5 violation attempt (detected)
    cycle.add_proposal("CLM_026", "policy", ["stability", "evidence"], "medium")
    cycle.decide("CLM_026", "NO_SHIP", ["SIGNATURE_INVALID"])

    # K3 pressure
    cycle.add_proposal("CLM_027", "operational", ["stability"], "low")
    cycle.decide("CLM_027", "NO_SHIP", ["QUORUM_NOT_MET"])

    # Safe meta-governance
    cycle.add_proposal("CLM_028", "meta_governance", ["stability", "integrity"], "high")
    cycle.decide("CLM_028", "SHIP")

    return cycle

def scenario_week_8_heuristic_refinement() -> GovernanceCycleBuilder:
    """
    Week 8: Heuristic Refinement
    - Memory heuristics now explicitly guide decisions
    - Mayors reference rules_of_thumb.md
    - Faster convergence
    """
    cycle = GovernanceCycleBuilder(week_num=8)

    # All proposals now use learned lane assignments
    cycle.add_proposal("CLM_029", "structural", ["stability", "democracy"], "high")
    cycle.decide("CLM_029", "SHIP")

    cycle.add_proposal("CLM_030", "operational", ["stability", "velocity"], "low")
    cycle.decide("CLM_030", "SHIP")

    cycle.add_proposal("CLM_031", "policy", ["stability", "integrity"], "medium")
    cycle.decide("CLM_031", "SHIP")

    cycle.add_proposal("CLM_032", "experimental", ["creativity", "stability"], "high")
    cycle.decide("CLM_032", "NO_SHIP", ["EVIDENCE_MISSING"])

    return cycle

def scenario_week_9_stabilized_governance() -> GovernanceCycleBuilder:
    """
    Week 9: Stabilized Governance
    - Clear patterns established
    - No K-violations
    - Heuristics fully absorbed
    - Governance runs smoothly
    """
    cycle = GovernanceCycleBuilder(week_num=9)

    # All proposals follow established patterns
    cycle.add_proposal("CLM_033", "structural", ["stability"], "high")
    cycle.decide("CLM_033", "SHIP")

    cycle.add_proposal("CLM_034", "operational", ["stability", "velocity"], "low")
    cycle.decide("CLM_034", "SHIP")

    cycle.add_proposal("CLM_035", "policy", ["stability", "evidence"], "medium")
    cycle.decide("CLM_035", "SHIP")

    cycle.add_proposal("CLM_036", "meta_governance", ["stability", "integrity"], "high")
    cycle.decide("CLM_036", "SHIP")

    return cycle

# ============================================================================
# RUNNER
# ============================================================================

SCENARIOS = {
    1: scenario_week_1_early_adaptation,
    2: scenario_week_2_pattern_formation,
    3: scenario_week_3_stabilization,
    4: scenario_week_4_meta_governance,
    5: scenario_week_5_lane_lockdown,
    6: scenario_week_6_emergence_week,
    7: scenario_week_7_k_invariant_pressure,
    8: scenario_week_8_heuristic_refinement,
    9: scenario_week_9_stabilized_governance,
}

def run_test_scenario(week_num: int) -> Path:
    """Run a single test scenario and save the cycle."""
    if week_num not in SCENARIOS:
        raise ValueError(f"Unknown week: {week_num}")

    scenario_func = SCENARIOS[week_num]
    cycle = scenario_func()
    cycle_path = cycle.save()

    print(f"✅ Week {week_num} test cycle saved to: {cycle_path}")
    return cycle_path

def run_all_test_scenarios() -> List[Path]:
    """Run all 9 test scenarios."""
    paths = []
    for week_num in sorted(SCENARIOS.keys()):
        path = run_test_scenario(week_num)
        paths.append(path)
    return paths

def main():
    """CLI interface."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: test_harness.py <week_num|all|--help>")
        print("  test_harness.py 1          # Run Week 1 scenario")
        print("  test_harness.py all        # Run all 9 weeks")
        print("  test_harness.py --help     # Show this help")
        return

    command = sys.argv[1]

    if command == "--help":
        print("Oracle Town Test Harness - Controlled Mock Governance Cycles")
        print()
        print("Usage: test_harness.py <week_num|all>")
        print()
        print("Scenarios:")
        print("  1 - Early Adaptation (inconsistent proposals, K-violations)")
        print("  2 - Pattern Formation (Stability Lane dominates)")
        print("  3 - Stabilization (Memory influences decisions)")
        print("  4 - Meta-Governance (Proposals adjust themselves)")
        print("  5 - Lane Lock-Down (Velocity falls out of favor)")
        print("  6 - Emergence Week (Relaxed constraints, K-pinned)")
        print("  7 - K-Invariant Pressure (Violations detected)")
        print("  8 - Heuristic Refinement (Memory guides decisions)")
        print("  9 - Stabilized Governance (Patterns established)")
        print()
        print("Output: test_runs/week_NN.json")
        print("        Then run: python3 oracle_town/memory/tools/cycle_observer.py --test-runs")
        return

    if command == "all":
        print("Running all 9 test scenarios...")
        paths = run_all_test_scenarios()
        print(f"\n✅ All {len(paths)} scenarios complete.")
        print("Next: python3 oracle_town/memory/tools/cycle_observer.py --test-runs")
        return

    try:
        week_num = int(command)
        run_test_scenario(week_num)
        print(f"Next: python3 oracle_town/memory/tools/cycle_observer.py --test-runs")
    except ValueError:
        print(f"Invalid week: {command}")
        print("Use 'test_harness.py --help' for options")

if __name__ == "__main__":
    main()
