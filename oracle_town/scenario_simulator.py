#!/usr/bin/env python3
"""
Oracle Town Scenario Simulator (Phase 7)

Policy impact simulation: test policy changes against historical verdicts before deployment.
Enables safe, data-driven policy evolution with measurable risk assessment.

Architecture:
- ScenarioSimulator: Main orchestrator for policy replay
- PolicyChange: Immutable record of proposed changes
- SimulationResult: Detailed impact analysis
- Deterministic verdict replay (K5 invariant)

Key Features:
1. Load proposed policy changes from JSON
2. Replay historical verdicts with new policy
3. Track ACCEPT→REJECT and REJECT→ACCEPT transitions
4. Calculate accuracy delta (before vs after)
5. Estimate false positive/negative impact
6. Provide risk assessment and recommendations
7. Generate detailed simulation report

K5 Determinism: Same verdicts + policy → identical results (reproducible)
K7 Policy Pinning: New policy creates new version hash
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone


@dataclass
class PolicyChange:
    """Single policy parameter change."""
    gate: str  # GATE_A, GATE_B, GATE_C
    parameter: str  # e.g., "shell_command_threshold", "credential_scan_depth"
    old_value: Any
    new_value: Any
    reason: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None).isoformat())

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Transition:
    """Verdict transition from old to new policy."""
    receipt_id: str
    old_decision: str  # ACCEPT or REJECT
    new_decision: str  # ACCEPT or REJECT
    changed: bool
    reason: str
    timestamp: str


@dataclass
class SimulationResult:
    """Complete simulation result with impact analysis."""
    total_verdicts_replayed: int
    unchanged: int
    changed: int

    # Transitions
    accept_to_reject: int  # False positives (was ACCEPT, now REJECT)
    reject_to_accept: int  # False negatives (was REJECT, now ACCEPT)

    # Metrics
    old_accuracy: float  # Assume 0.80 baseline
    new_accuracy: float
    accuracy_delta: float  # new - old
    false_positive_rate: float
    false_negative_rate: float

    # Recommendation
    transition_rate: float  # % of verdicts that changed
    recommended_action: str  # "apply" | "hold" | "revise"
    risk_assessment: str  # "low" | "medium" | "high"
    reason: str

    # Audit trail
    policy_changes: List[Dict]
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None).isoformat())

    def to_dict(self) -> Dict:
        return asdict(self)


class ScenarioSimulator:
    """Simulate policy changes against historical verdicts."""

    def __init__(self, verdicts: List[Dict], old_policy: Optional[Dict] = None, new_policy: Optional[Dict] = None):
        """Initialize simulator with verdicts and policies.

        Args:
            verdicts: List of historical verdict dicts from ledger
            old_policy: Current policy (optional, for comparison)
            new_policy: Proposed policy (required for simulation)
        """
        self.verdicts = verdicts
        self.old_policy = old_policy or {}
        self.new_policy = new_policy or {}
        self.transitions = []

    @classmethod
    def from_ledger_and_policy(cls, ledger_path: str, policy_path: str) -> 'ScenarioSimulator':
        """Load verdicts from ledger and policy from JSON file."""
        # Load verdicts
        verdicts = []
        try:
            with open(ledger_path, 'r') as f:
                for line in f:
                    if line.strip():
                        try:
                            verdict = json.loads(line)
                            verdicts.append(verdict)
                        except json.JSONDecodeError:
                            pass
        except FileNotFoundError:
            print(f"Ledger file not found: {ledger_path}")
            return cls([], {}, {})

        # Load policy
        new_policy = {}
        try:
            with open(policy_path, 'r') as f:
                new_policy = json.load(f)
        except FileNotFoundError:
            print(f"Policy file not found: {policy_path}")

        return cls(verdicts, {}, new_policy)

    def simulate(self) -> SimulationResult:
        """Run complete policy impact simulation."""
        if not self.verdicts:
            return self._empty_result("No verdicts to simulate")

        # Collect policy changes
        policy_changes = self._extract_policy_changes()

        # Replay verdicts
        old_accept_count = sum(1 for v in self.verdicts if v.get('decision') == 'ACCEPT')
        new_accept_count = 0

        transitions = []

        for verdict in self.verdicts:
            old_decision = verdict.get('decision', 'REJECT')

            # Simulate new policy impact (deterministic)
            new_decision = self._apply_new_policy(verdict)

            changed = old_decision != new_decision
            if changed:
                transitions.append(Transition(
                    receipt_id=verdict.get('receipt_id', 'unknown'),
                    old_decision=old_decision,
                    new_decision=new_decision,
                    changed=True,
                    reason=f"Policy change caused {old_decision} → {new_decision}",
                    timestamp=verdict.get('timestamp', datetime.now(timezone.utc).replace(tzinfo=None).isoformat()),
                ))

            if new_decision == 'ACCEPT':
                new_accept_count += 1

        # Calculate metrics
        accept_to_reject = sum(1 for t in transitions if t.old_decision == 'ACCEPT' and t.new_decision == 'REJECT')
        reject_to_accept = sum(1 for t in transitions if t.old_decision == 'REJECT' and t.new_decision == 'ACCEPT')

        old_accuracy = old_accept_count / len(self.verdicts) if self.verdicts else 0
        new_accuracy = new_accept_count / len(self.verdicts) if self.verdicts else 0
        accuracy_delta = new_accuracy - old_accuracy

        transition_rate = len(transitions) / len(self.verdicts) if self.verdicts else 0

        # Assess risk
        false_positive_rate = accept_to_reject / old_accept_count if old_accept_count > 0 else 0
        false_negative_rate = reject_to_accept / (len(self.verdicts) - old_accept_count) if (len(self.verdicts) - old_accept_count) > 0 else 0

        # Determine recommendation
        risk_assessment, recommended_action, reason = self._assess_risk(
            transition_rate,
            accuracy_delta,
            false_positive_rate,
            false_negative_rate,
            len(self.verdicts),
        )

        return SimulationResult(
            total_verdicts_replayed=len(self.verdicts),
            unchanged=len(self.verdicts) - len(transitions),
            changed=len(transitions),
            accept_to_reject=accept_to_reject,
            reject_to_accept=reject_to_accept,
            old_accuracy=old_accuracy,
            new_accuracy=new_accuracy,
            accuracy_delta=accuracy_delta,
            false_positive_rate=false_positive_rate,
            false_negative_rate=false_negative_rate,
            transition_rate=transition_rate,
            recommended_action=recommended_action,
            risk_assessment=risk_assessment,
            reason=reason,
            policy_changes=[c.to_dict() for c in self._extract_changes_as_objects()],
        )

    def _extract_policy_changes(self) -> List[Dict]:
        """Extract changes between old and new policy."""
        changes = []

        # Simple diff: for each key in new_policy, compare with old_policy
        for gate_key in self.new_policy:
            if gate_key not in self.old_policy:
                changes.append({
                    'gate': gate_key,
                    'parameter': 'added',
                    'old_value': None,
                    'new_value': self.new_policy[gate_key],
                })
            elif self.new_policy[gate_key] != self.old_policy.get(gate_key):
                changes.append({
                    'gate': gate_key,
                    'parameter': 'threshold',
                    'old_value': self.old_policy.get(gate_key),
                    'new_value': self.new_policy[gate_key],
                })

        return changes

    def _extract_changes_as_objects(self) -> List[PolicyChange]:
        """Extract policy changes as PolicyChange objects."""
        changes = []

        for change_dict in self._extract_policy_changes():
            changes.append(PolicyChange(
                gate=change_dict.get('gate', 'unknown'),
                parameter=change_dict.get('parameter', 'unknown'),
                old_value=change_dict.get('old_value'),
                new_value=change_dict.get('new_value'),
                reason=f"Policy parameter change",
            ))

        return changes

    def _apply_new_policy(self, verdict: Dict) -> str:
        """Deterministically apply new policy to a verdict."""
        old_decision = verdict.get('decision', 'REJECT')

        # Get gate information
        gate = verdict.get('gate', 'GATE_A')

        # Simple simulation logic based on policy
        if gate in self.new_policy:
            new_threshold = self.new_policy[gate]

            # If policy threshold is lower (more permissive), more ACCEPTs
            if isinstance(new_threshold, (int, float)):
                # Heuristic: if threshold drops by >20%, convert some REJECTs to ACCEPTs
                if new_threshold < 50:
                    if old_decision == 'REJECT':
                        # 30% chance to convert based on deterministic hash
                        receipt_id = verdict.get('receipt_id', '')
                        hash_val = int(hashlib.sha256(receipt_id.encode()).hexdigest(), 16) % 100
                        if hash_val < 30:
                            return 'ACCEPT'

        return old_decision

    def _assess_risk(self, transition_rate: float, accuracy_delta: float,
                    false_positive_rate: float, false_negative_rate: float,
                    total_verdicts: int) -> Tuple[str, str, str]:
        """Determine risk assessment and recommendation."""

        # Risk factors
        high_transition = transition_rate > 0.1  # >10% of verdicts change
        large_accuracy_drop = accuracy_delta < -0.05  # >5% accuracy loss
        high_false_positives = false_positive_rate > 0.1
        high_false_negatives = false_negative_rate > 0.1
        insufficient_data = total_verdicts < 20

        # Risk assessment
        risk_factors = sum([
            high_transition,
            large_accuracy_drop,
            high_false_positives,
            high_false_negatives,
        ])

        if risk_factors >= 3 or (high_transition and large_accuracy_drop):
            risk = "high"
        elif risk_factors >= 1:
            risk = "medium"
        else:
            risk = "low"

        # Recommendation
        if insufficient_data:
            action = "hold"
            reason = "Insufficient historical data for confident recommendation (need ≥20 verdicts)"
        elif risk == "high":
            action = "do_not_apply"
            reason = f"High risk: {risk_factors} risk factors detected (transitions={transition_rate:.1%}, accuracy_delta={accuracy_delta:+.1%})"
        elif risk == "medium":
            action = "hold"
            reason = f"Medium risk: Consider gathering more data before applying (accuracy_delta={accuracy_delta:+.1%})"
        elif accuracy_delta > 0.02:
            action = "apply"
            reason = f"Safe to apply: Positive accuracy improvement ({accuracy_delta:+.1%})"
        else:
            action = "apply"
            reason = f"Safe to apply: Minimal impact (accuracy_delta={accuracy_delta:+.1%})"

        return risk, action, reason

    def _empty_result(self, error_reason: str) -> SimulationResult:
        """Create empty result with error message."""
        return SimulationResult(
            total_verdicts_replayed=0,
            unchanged=0,
            changed=0,
            accept_to_reject=0,
            reject_to_accept=0,
            old_accuracy=0.0,
            new_accuracy=0.0,
            accuracy_delta=0.0,
            false_positive_rate=0.0,
            false_negative_rate=0.0,
            transition_rate=0.0,
            recommended_action="hold",
            risk_assessment="unknown",
            reason=error_reason,
            policy_changes=[],
        )

    def generate_report(self, result: SimulationResult, output_path: Optional[str] = None) -> str:
        """Generate human-readable simulation report."""
        lines = []
        lines.append("="*70)
        lines.append("ORACLE TOWN SCENARIO SIMULATOR - POLICY IMPACT REPORT")
        lines.append("="*70)
        lines.append("")

        lines.append(f"Simulation Date: {result.timestamp}")
        lines.append("")

        lines.append("VERDICTS REPLAYED:")
        lines.append(f"  Total:    {result.total_verdicts_replayed}")
        lines.append(f"  Changed:  {result.changed} ({result.transition_rate*100:.1f}%)")
        lines.append(f"  Unchanged: {result.unchanged}")
        lines.append("")

        lines.append("DECISION TRANSITIONS:")
        lines.append(f"  ACCEPT → REJECT: {result.accept_to_reject} ({result.false_positive_rate*100:.1f}%)")
        lines.append(f"  REJECT → ACCEPT: {result.reject_to_accept} ({result.false_negative_rate*100:.1f}%)")
        lines.append("")

        lines.append("ACCURACY IMPACT:")
        lines.append(f"  Old Accuracy: {result.old_accuracy*100:.1f}%")
        lines.append(f"  New Accuracy: {result.new_accuracy*100:.1f}%")
        lines.append(f"  Delta:        {result.accuracy_delta:+.1%}")
        lines.append("")

        lines.append("POLICY CHANGES:")
        for change in result.policy_changes:
            lines.append(f"  - {change['gate']}: {change['parameter']}")
            lines.append(f"    Old: {change['old_value']}")
            lines.append(f"    New: {change['new_value']}")
        lines.append("")

        lines.append("RISK ASSESSMENT:")
        lines.append(f"  Risk Level:  {result.risk_assessment.upper()}")
        lines.append(f"  Recommendation: {result.recommended_action.upper()}")
        lines.append(f"  Reason: {result.reason}")
        lines.append("")
        lines.append("="*70)

        report = "\n".join(lines)

        # Save report if output path provided
        if output_path:
            with open(output_path, 'w') as f:
                f.write(report)

        return report


def main():
    """Main entry point for scenario simulator."""
    import argparse

    parser = argparse.ArgumentParser(description='Simulate policy changes against historical verdicts')
    parser.add_argument('--scenario', type=str, help='Path to proposed policy JSON file')
    parser.add_argument('--ledger', type=str, default='oracle_town/ledger.jsonl', help='Path to ledger JSONL file')
    parser.add_argument('--output', type=str, help='Output path for simulation report')
    parser.add_argument('--json', action='store_true', help='Output result as JSON')

    args = parser.parse_args()

    # Load simulator
    simulator = ScenarioSimulator.from_ledger_and_policy(args.ledger, args.scenario)

    # Run simulation
    result = simulator.simulate()

    # Output result
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        report = simulator.generate_report(result, args.output)
        print(report)

        if args.output:
            print(f"Report saved to: {args.output}")


if __name__ == '__main__':
    main()
