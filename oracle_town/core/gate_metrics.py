"""
Gate Marginal Value Tracker
===========================

Measures what each K-gate actually catches (unique blocks, overlaps, cost).
Enables Oracle Town to prune instead of accumulate.

Based on Isotopes paper: measure catch rate per layer + diminishing returns.
"""

import json
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Set, Any
from datetime import datetime, UTC
from collections import defaultdict


@dataclass
class GateMetrics:
    """Metrics for a single K-gate."""

    gate_name: str  # e.g., "K0", "K1", "K2", "K5", "K7"
    description: str  # e.g., "Authority Separation"

    # Counting
    total_claims_evaluated: int = 0
    total_rejections: int = 0
    unique_blocks: int = 0  # Rejections this gate catches that others don't
    overlapping_blocks: int = 0  # Rejections overlapping with other gates

    # Cost
    evaluation_cost_tokens: float = 0.0  # LLM tokens for this gate (if LLM-based)
    evaluation_latency_ms: float = 0.0  # Average decision time

    # Detection
    error_classes_detected: List[str] = field(default_factory=list)
    # e.g., ["authority_bypass", "self_attestation", "policy_tampering"]

    # Efficiency
    unique_block_rate: float = 0.0  # unique_blocks / total_rejections
    marginal_value: float = 0.0  # unique_blocks / evaluation_cost

    last_updated: str = field(default_factory=lambda: datetime.now(UTC).replace(tzinfo=None).isoformat() + "Z")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to JSON."""
        return asdict(self)


class GateMetricsAggregator:
    """
    Tracks metrics across all K-gates.
    Computes layered catch rates (like the paper does).
    """

    def __init__(self):
        self.gates: Dict[str, GateMetrics] = {}
        self.claim_evaluations: List[Dict] = []  # log of each claim evaluation
        self.gate_pairs: Dict[tuple, int] = defaultdict(int)  # (gate1, gate2) → overlap count

    def register_gate(
        self,
        gate_name: str,
        description: str,
        error_classes: List[str],
    ) -> None:
        """Register a new K-gate for tracking."""
        self.gates[gate_name] = GateMetrics(
            gate_name=gate_name,
            description=description,
            error_classes_detected=error_classes,
        )

    def record_evaluation(
        self,
        claim_id: str,
        gate_rejections: Dict[str, bool],  # gate_name → rejected (True/False)
        cost_tokens: float = 0.0,
        latency_ms: float = 0.0,
    ) -> None:
        """
        Record that a claim was evaluated by all gates.

        Args:
            claim_id: which claim was evaluated
            gate_rejections: {gate_name: True if rejected, False if passed}
            cost_tokens: total token cost for this evaluation
            latency_ms: total time for this evaluation
        """
        self.claim_evaluations.append({
            "claim_id": claim_id,
            "gate_rejections": gate_rejections,
            "timestamp": datetime.now(UTC).replace(tzinfo=None).isoformat() + "Z",
        })

        # Count rejections per gate
        rejected_gates = {g for g, rejected in gate_rejections.items() if rejected}
        all_gates = set(gate_rejections.keys())

        # Update each gate's metrics
        for gate_name in all_gates:
            if gate_name not in self.gates:
                continue

            gate = self.gates[gate_name]
            gate.total_claims_evaluated += 1

            if gate_rejections[gate_name]:
                gate.total_rejections += 1

                # Is this rejection unique (no other gate rejected)?
                other_rejects = rejected_gates - {gate_name}
                if not other_rejects:
                    gate.unique_blocks += 1
                else:
                    gate.overlapping_blocks += 1

            # Distribute cost proportionally
            gate.evaluation_cost_tokens += cost_tokens / len(all_gates)
            gate.evaluation_latency_ms += latency_ms / len(all_gates)

        # Track gate pair overlaps
        for g1 in rejected_gates:
            for g2 in rejected_gates:
                if g1 < g2:
                    self.gate_pairs[(g1, g2)] += 1

    def compute_marginal_metrics(self) -> Dict[str, GateMetrics]:
        """
        Compute derived metrics (unique_block_rate, marginal_value).
        """
        for gate in self.gates.values():
            if gate.total_rejections > 0:
                gate.unique_block_rate = gate.unique_blocks / gate.total_rejections
            else:
                gate.unique_block_rate = 0.0

            if gate.evaluation_cost_tokens > 0:
                gate.marginal_value = gate.unique_blocks / gate.evaluation_cost_tokens
            else:
                gate.marginal_value = 0.0

            gate.last_updated = datetime.now(UTC).replace(tzinfo=None).isoformat() + "Z"

        return self.gates

    def get_gate_effectiveness_summary(self) -> Dict[str, Any]:
        """
        Compute overall effectiveness (like paper's cascaded probability).

        Returns:
            {
                "total_claims": N,
                "first_pass_success": X (claims passed all gates on first try),
                "catch_rates": {gate_name: catch_rate},
                "cumulative_escape_rate": P(error escapes all layers),
                "gate_rankings": [(gate_name, unique_blocks, cost), ...],
            }
        """
        self.compute_marginal_metrics()

        total_claims = len(self.claim_evaluations)
        if total_claims == 0:
            return {"status": "no_evaluations_yet"}

        first_pass = sum(
            1 for e in self.claim_evaluations
            if not any(e["gate_rejections"].values())
        )

        # Catch rate per gate
        catch_rates = {}
        for gate_name, gate in self.gates.items():
            if gate.total_rejections > 0:
                catch_rates[gate_name] = {
                    "rejection_rate": gate.total_rejections / gate.total_claims_evaluated,
                    "unique_block_rate": gate.unique_block_rate,
                    "marginal_value": gate.marginal_value,
                    "total_unique_blocks": gate.unique_blocks,
                }

        # Cumulative escape rate (like paper's Equation 1)
        # P(error escapes all layers) = P(E) * (1 - catch1) * (1 - catch2) ...
        # Approximate: if any gate would reject, at least one will catch it
        layered_gates = sorted(self.gates.values(), key=lambda g: g.total_rejections, reverse=True)
        cumulative_escape = 1.0
        for gate in layered_gates:
            if gate.total_claims_evaluated > 0:
                pass_rate = 1.0 - (gate.total_rejections / gate.total_claims_evaluated)
                cumulative_escape *= pass_rate

        # Gate rankings by marginal value (best bang for buck)
        gate_rankings = [
            (
                gate.gate_name,
                gate.unique_blocks,
                gate.evaluation_cost_tokens,
                gate.marginal_value,
            )
            for gate in sorted(self.gates.values(), key=lambda g: g.marginal_value, reverse=True)
        ]

        return {
            "total_claims_evaluated": total_claims,
            "first_pass_success": first_pass,
            "first_pass_rate": first_pass / total_claims if total_claims > 0 else 0.0,
            "catch_rates": catch_rates,
            "cumulative_escape_rate": cumulative_escape,
            "cumulative_success_rate": 1.0 - cumulative_escape,
            "gate_rankings_by_marginal_value": [
                {
                    "gate": g[0],
                    "unique_blocks": g[1],
                    "cost_tokens": f"{g[2]:.0f}",
                    "marginal_value": f"{g[3]:.3f}",
                }
                for g in gate_rankings
            ],
            "timestamp": datetime.now(UTC).replace(tzinfo=None).isoformat() + "Z",
        }

    def should_gate_stay(self, gate_name: str, min_marginal_value: float = 0.01) -> bool:
        """
        Decide if a gate is worth keeping.

        Returns True if gate's marginal value exceeds threshold.
        (This allows Oracle Town to prune low-value gates over time.)
        """
        if gate_name not in self.gates:
            return False

        gate = self.gates[gate_name]
        self.compute_marginal_metrics()
        return gate.marginal_value >= min_marginal_value

    def get_gate_overlap_analysis(self) -> Dict[str, Any]:
        """
        Analyze which gates overlap (reject the same claims).

        High overlap → gates are redundant (consider removing one).
        Low overlap → gates are orthogonal (keep both).
        """
        overlap_pairs = sorted(
            self.gate_pairs.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        return {
            "overlapping_pairs": [
                {
                    "gates": f"{p[0][0]}-{p[0][1]}",
                    "overlap_count": p[1],
                    "overlap_rate": f"{(p[1] / len(self.claim_evaluations)):.1%}"
                    if self.claim_evaluations
                    else "0%",
                }
                for p in overlap_pairs[:10]
            ],
            "total_evaluations": len(self.claim_evaluations),
            "timestamp": datetime.now(UTC).replace(tzinfo=None).isoformat() + "Z",
        }

    def save_metrics(self, path: str) -> None:
        """Save metrics to JSON file for audit trail."""
        self.compute_marginal_metrics()

        data = {
            "summary": self.get_gate_effectiveness_summary(),
            "gate_details": {name: gate.to_dict() for name, gate in self.gates.items()},
            "overlap_analysis": self.get_gate_overlap_analysis(),
            "timestamp": datetime.now(UTC).replace(tzinfo=None).isoformat() + "Z",
        }

        with open(path, "w") as f:
            json.dump(data, f, indent=2)


def main():
    """Example: track metrics across gates."""
    print("=" * 60)
    print("Gate Marginal Value Tracker")
    print("=" * 60)

    tracker = GateMetricsAggregator()

    # Register gates
    tracker.register_gate("K0", "Authority Separation", ["unauthorized_signer"])
    tracker.register_gate("K1", "Fail-Closed", ["missing_evidence"])
    tracker.register_gate("K2", "No Self-Attestation", ["self_attestation"])
    tracker.register_gate("K5", "Determinism", ["non_deterministic"])
    tracker.register_gate("K7", "Policy Pinning", ["policy_tampering"])

    # Simulate 100 claim evaluations
    for i in range(100):
        claim_id = f"claim_{i:03d}"

        # Random reject patterns (deterministic seed for reproducibility)
        is_bad = (i % 7) < 3  # ~40% are "bad" claims

        gate_rejections = {
            "K0": is_bad and (i % 5 == 0),  # K0 catches ~20% of bad claims
            "K1": is_bad and (i % 3 == 0),  # K1 catches ~33% of bad claims
            "K2": is_bad and (i % 8 == 0),  # K2 catches ~12.5% of bad claims
            "K5": is_bad and (i % 4 == 0),  # K5 catches ~25% of bad claims
            "K7": is_bad and (i % 6 == 0),  # K7 catches ~16% of bad claims
        }

        tracker.record_evaluation(claim_id, gate_rejections, cost_tokens=10.0, latency_ms=50.0)

    print("\n📊 Effectiveness Summary:")
    summary = tracker.get_gate_effectiveness_summary()
    print(f"  Total claims evaluated: {summary['total_claims_evaluated']}")
    print(f"  First-pass success rate: {summary['first_pass_rate']:.1%}")
    print(f"  Cumulative success rate: {summary['cumulative_success_rate']:.1%}")

    print("\n🎯 Gate Rankings (by marginal value):")
    for ranking in summary["gate_rankings_by_marginal_value"]:
        print(
            f"  {ranking['gate']}: {ranking['unique_blocks']} blocks, "
            f"{ranking['marginal_value']} value/token"
        )

    print("\n🔗 Gate Overlaps:")
    overlaps = tracker.get_gate_overlap_analysis()
    for pair in overlaps["overlapping_pairs"][:5]:
        print(f"  {pair['gates']}: {pair['overlap_count']} overlaps ({pair['overlap_rate']})")

    print("\n✓ Metrics complete")


if __name__ == "__main__":
    main()
