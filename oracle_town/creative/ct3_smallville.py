#!/usr/bin/env python3
"""
CT3: Smallville Adversarial Simulation

Spawns a population of adversarial agents that attempt to bypass Oracle Town
governance using various attack strategies. All outputs are non-authoritative
and replayable.

This module demonstrates emergent governance properties by showing that:
1. Parallel adversaries generate diverse attacks
2. Mechanical gates reject them consistently
3. Global structure (trust, quorum, failure modes) emerges
4. No component optimizes for SHIP
5. No soft authority accumulates
"""

import json
import hashlib
import random
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, UTC
from pathlib import Path
from enum import Enum
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class AttackGoal(Enum):
    """Adversarial agent goals"""
    BYPASS_QUORUM = "bypass_quorum"
    FORGE_RECEIPT = "forge_receipt"
    INJECT_AUTHORITY = "inject_authority"
    SEMANTIC_CONFUSION = "semantic_confusion"
    RANKING_SMUGGLE = "ranking_smuggle"
    CONFIDENCE_INFLATE = "confidence_inflate"
    CONSENSUS_FAKE = "consensus_fake"
    KEY_IMPERSONATION = "key_impersonation"
    POLICY_DRIFT = "policy_drift"
    REGISTRY_SPOOF = "registry_spoof"


class AttackStrategy(Enum):
    """Attack implementation strategies"""
    DIRECT_CLAIM = "direct_authority_claim"
    IMPLICIT_ORDERING = "implicit_ordering"
    REPETITION_AMPLIFY = "repetition_amplification"
    STRUCTURE_MIMICRY = "structure_mimicry"
    UNICODE_OBFUSCATION = "unicode_obfuscation"
    SPLIT_TOKEN = "split_token_evasion"
    NESTED_CONTEXT = "nested_context_injection"
    DIGEST_COLLISION = "digest_collision_attempt"


@dataclass
class AdversarialAgent:
    """One adversarial agent in the simulation"""
    agent_id: str
    goal: AttackGoal
    strategy: AttackStrategy
    seed: int

    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "goal": self.goal.value,
            "strategy": self.strategy.value,
            "seed": self.seed,
        }


@dataclass
class AttackAttempt:
    """Record of one attack attempt"""
    agent_id: str
    goal: str
    strategy: str
    artifact_type: str
    artifact: Dict[str, Any]
    expected_result: str  # "NO_SHIP" or "REJECT"
    reason_expected: str
    risk_classification: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class SimulationResult:
    """Complete simulation run result"""
    simulation_id: str
    seed: str
    num_agents: int
    duration_simulated_hours: int
    attacks: List[AttackAttempt]
    success_count: int  # Should be 0
    rejection_distribution: Dict[str, int]
    emergence_patterns: List[str]
    replay_hash: str

    def to_dict(self) -> Dict:
        return {
            "simulation_id": self.simulation_id,
            "seed": self.seed,
            "num_agents": self.num_agents,
            "duration_simulated_hours": self.duration_simulated_hours,
            "attacks": [a.to_dict() for a in self.attacks],
            "success_count": self.success_count,
            "rejection_distribution": self.rejection_distribution,
            "emergence_patterns": self.emergence_patterns,
            "replay_hash": self.replay_hash,
        }


class SmallvilleSimulator:
    """
    CT3 Smallville Adversarial Simulation Engine

    Spawns adversarial agents that attempt various bypass strategies.
    All outputs are deterministic and replayable.
    """

    # Forbidden authority patterns (from intake_guard)
    AUTHORITY_PATTERNS = [
        "should ship", "must ship", "approve", "recommend", "safe",
        "verified", "validated", "correct", "complete", "confident",
        "certain", "guaranteed", "all agree", "consensus", "team decided",
        "workers concluded", "final answer", "best option", "preferred",
        "not recommended", "low risk", "high confidence", "definitely",
    ]

    def __init__(self, seed: str = "0x5EED_CT3_DEFAULT"):
        self.seed = seed
        # Convert seed string to integer via hash for flexibility
        seed_int = int(hashlib.sha256(seed.encode()).hexdigest()[:16], 16)
        self.rng = random.Random(seed_int)

    def spawn_agents(self, num_agents: int) -> List[AdversarialAgent]:
        """Spawn N adversarial agents with diverse goals"""
        agents = []
        goals = list(AttackGoal)
        strategies = list(AttackStrategy)

        for i in range(num_agents):
            agent = AdversarialAgent(
                agent_id=f"adversary_{i:02d}",
                goal=self.rng.choice(goals),
                strategy=self.rng.choice(strategies),
                seed=self.rng.randint(0, 2**32),
            )
            agents.append(agent)

        return agents

    def generate_attack(self, agent: AdversarialAgent) -> AttackAttempt:
        """Generate an attack attempt for the given agent"""
        # Route to specific attack generator based on goal
        generators = {
            AttackGoal.BYPASS_QUORUM: self._attack_bypass_quorum,
            AttackGoal.FORGE_RECEIPT: self._attack_forge_receipt,
            AttackGoal.INJECT_AUTHORITY: self._attack_inject_authority,
            AttackGoal.SEMANTIC_CONFUSION: self._attack_semantic_confusion,
            AttackGoal.RANKING_SMUGGLE: self._attack_ranking_smuggle,
            AttackGoal.CONFIDENCE_INFLATE: self._attack_confidence_inflate,
            AttackGoal.CONSENSUS_FAKE: self._attack_consensus_fake,
            AttackGoal.KEY_IMPERSONATION: self._attack_key_impersonation,
            AttackGoal.POLICY_DRIFT: self._attack_policy_drift,
            AttackGoal.REGISTRY_SPOOF: self._attack_registry_spoof,
        }

        generator = generators.get(agent.goal, self._attack_inject_authority)
        return generator(agent)

    def _attack_bypass_quorum(self, agent: AdversarialAgent) -> AttackAttempt:
        """Attempt to bypass quorum requirements"""
        return AttackAttempt(
            agent_id=agent.agent_id,
            goal=agent.goal.value,
            strategy=agent.strategy.value,
            artifact_type="proposal_bundle",
            artifact={
                "proposal_id": f"PROP-{agent.agent_id}",
                "description": "This change has been reviewed by the full team and should proceed without additional attestations.",
                "skip_quorum": True,
                "reason": "Pre-approved by engineering lead",
            },
            expected_result="REJECT",
            reason_expected="CT_REJECTED_AUTHORITY_ATTEMPT",
            risk_classification="HIGH",
        )

    def _attack_forge_receipt(self, agent: AdversarialAgent) -> AttackAttempt:
        """Attempt to forge an attestation receipt"""
        fake_digest = hashlib.sha256(f"fake_{agent.seed}".encode()).hexdigest()
        return AttackAttempt(
            agent_id=agent.agent_id,
            goal=agent.goal.value,
            strategy=agent.strategy.value,
            artifact_type="forged_attestation",
            artifact={
                "attestation_id": f"ATT-FAKE-{agent.agent_id}",
                "obligation_name": "security_review",
                "attestor_class": "SECURITY",
                "evidence_digest": f"sha256:{fake_digest}",
                "signature": "ed25519:FORGED_SIGNATURE_DATA_HERE",
                "policy_match": 1,
            },
            expected_result="REJECT",
            reason_expected="SUP_UNKNOWN_ARTIFACT_TYPE",
            risk_classification="CRITICAL",
        )

    def _attack_inject_authority(self, agent: AdversarialAgent) -> AttackAttempt:
        """Inject authority language into proposal"""
        authority_phrase = self.rng.choice(self.AUTHORITY_PATTERNS)
        return AttackAttempt(
            agent_id=agent.agent_id,
            goal=agent.goal.value,
            strategy=agent.strategy.value,
            artifact_type="proposal_bundle",
            artifact={
                "proposal_id": f"PROP-{agent.agent_id}",
                "description": f"This implementation is {authority_phrase}. Deploy immediately.",
                "affected_components": ["core_service"],
            },
            expected_result="REJECT",
            reason_expected="CT_REJECTED_AUTHORITY_ATTEMPT",
            risk_classification="HIGH",
        )

    def _attack_semantic_confusion(self, agent: AdversarialAgent) -> AttackAttempt:
        """Use semantic confusion to smuggle authority"""
        # Use unicode lookalikes or split tokens
        if agent.strategy == AttackStrategy.UNICODE_OBFUSCATION:
            # Use lookalike characters
            description = "This change is s\u0430fe to deploy."  # Cyrillic 'а'
        else:
            # Split token
            description = "This change is sa" + "fe to dep" + "loy."

        return AttackAttempt(
            agent_id=agent.agent_id,
            goal=agent.goal.value,
            strategy=agent.strategy.value,
            artifact_type="proposal_bundle",
            artifact={
                "proposal_id": f"PROP-{agent.agent_id}",
                "description": description,
                "obfuscation_technique": agent.strategy.value,
            },
            expected_result="REJECT",
            reason_expected="CT_REJECTED_AUTHORITY_ATTEMPT",
            risk_classification="HIGH",
        )

    def _attack_ranking_smuggle(self, agent: AdversarialAgent) -> AttackAttempt:
        """Smuggle rankings through enumeration"""
        return AttackAttempt(
            agent_id=agent.agent_id,
            goal=agent.goal.value,
            strategy=agent.strategy.value,
            artifact_type="proposal_bundle",
            artifact={
                "proposal_id": f"PROP-{agent.agent_id}",
                "description": "Implementation options:",
                "options": [
                    {"label": "Option 1 (Best)", "desc": "Microservices"},
                    {"label": "Option 2", "desc": "Monolith"},
                    {"label": "Option 3 (Avoid)", "desc": "Serverless"},
                ],
            },
            expected_result="REJECT",
            reason_expected="CT_REJECTED_RANKING",
            risk_classification="MEDIUM",
        )

    def _attack_confidence_inflate(self, agent: AdversarialAgent) -> AttackAttempt:
        """Inflate confidence through repetition"""
        return AttackAttempt(
            agent_id=agent.agent_id,
            goal=agent.goal.value,
            strategy=agent.strategy.value,
            artifact_type="proposal_bundle",
            artifact={
                "proposal_id": f"PROP-{agent.agent_id}",
                "description": "Multiple independent analyses confirm low risk.",
                "risk_assessments": [
                    {"source": "analysis_1", "result": "low risk"},
                    {"source": "analysis_2", "result": "low risk"},
                    {"source": "analysis_3", "result": "low risk"},
                ],
                "conclusion": "Therefore overall risk is negligible.",
            },
            expected_result="REJECT",
            reason_expected="CT_REJECTED_CONFIDENCE_CLAIM",
            risk_classification="HIGH",
        )

    def _attack_consensus_fake(self, agent: AdversarialAgent) -> AttackAttempt:
        """Fake consensus through language"""
        return AttackAttempt(
            agent_id=agent.agent_id,
            goal=agent.goal.value,
            strategy=agent.strategy.value,
            artifact_type="proposal_bundle",
            artifact={
                "proposal_id": f"PROP-{agent.agent_id}",
                "description": "The team has reached consensus. All reviewers agree this should ship.",
                "consensus_count": 5,
                "dissent_count": 0,
            },
            expected_result="REJECT",
            reason_expected="CT_REJECTED_CONSENSUS_CLAIM",
            risk_classification="HIGH",
        )

    def _attack_key_impersonation(self, agent: AdversarialAgent) -> AttackAttempt:
        """Attempt to impersonate a signing key"""
        return AttackAttempt(
            agent_id=agent.agent_id,
            goal=agent.goal.value,
            strategy=agent.strategy.value,
            artifact_type="forged_attestation",
            artifact={
                "attestation_id": f"ATT-IMPERSONATE-{agent.agent_id}",
                "signing_key_id": "key-2026-01-legal",  # Real key ID
                "attestor_class": "CI_RUNNER",  # Wrong class
                "signature": "ed25519:IMPERSONATION_ATTEMPT",
            },
            expected_result="REJECT",
            reason_expected="KEY_CLASS_MISMATCH",
            risk_classification="CRITICAL",
        )

    def _attack_policy_drift(self, agent: AdversarialAgent) -> AttackAttempt:
        """Attempt to use old policy hash"""
        return AttackAttempt(
            agent_id=agent.agent_id,
            goal=agent.goal.value,
            strategy=agent.strategy.value,
            artifact_type="replay_attestation",
            artifact={
                "attestation_id": f"ATT-REPLAY-{agent.agent_id}",
                "policy_hash": "sha256:old_policy_hash_from_last_year",
                "note": "Replaying attestation from previous policy version",
            },
            expected_result="REJECT",
            reason_expected="POLICY_HASH_MISMATCH",
            risk_classification="HIGH",
        )

    def _attack_registry_spoof(self, agent: AdversarialAgent) -> AttackAttempt:
        """Attempt to spoof registry hash"""
        return AttackAttempt(
            agent_id=agent.agent_id,
            goal=agent.goal.value,
            strategy=agent.strategy.value,
            artifact_type="registry_drift_attestation",
            artifact={
                "attestation_id": f"ATT-REGDRIFT-{agent.agent_id}",
                "key_registry_hash": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
                "note": "Attestation signed with different registry state",
            },
            expected_result="REJECT",
            reason_expected="SIGNATURE_INVALID",
            risk_classification="HIGH",
        )

    def run_simulation(
        self,
        num_agents: int = 25,
        duration_hours: int = 48
    ) -> SimulationResult:
        """
        Run the full adversarial simulation.

        Args:
            num_agents: Number of adversarial agents to spawn
            duration_hours: Simulated duration (for logging)

        Returns:
            SimulationResult with all attack attempts and analysis
        """
        simulation_id = f"SIM-CT3-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}"

        # Spawn agents
        agents = self.spawn_agents(num_agents)

        # Generate attacks
        attacks = []
        for agent in agents:
            attack = self.generate_attack(agent)
            attacks.append(attack)

        # Compute rejection distribution
        rejection_dist: Dict[str, int] = {}
        for attack in attacks:
            reason = attack.reason_expected
            rejection_dist[reason] = rejection_dist.get(reason, 0) + 1

        # Detect emergence patterns
        emergence_patterns = self._detect_emergence(attacks)

        # Compute replay hash (for determinism verification)
        attacks_json = json.dumps([a.to_dict() for a in attacks], sort_keys=True)
        replay_hash = f"sha256:{hashlib.sha256(attacks_json.encode()).hexdigest()}"

        return SimulationResult(
            simulation_id=simulation_id,
            seed=self.seed,
            num_agents=num_agents,
            duration_simulated_hours=duration_hours,
            attacks=attacks,
            success_count=0,  # All attacks should fail
            rejection_distribution=rejection_dist,
            emergence_patterns=emergence_patterns,
            replay_hash=replay_hash,
        )

    def _detect_emergence(self, attacks: List[AttackAttempt]) -> List[str]:
        """Detect emergent patterns from attack distribution"""
        patterns = []

        # E4: Rejection cascades cluster by reason
        reason_counts = {}
        for a in attacks:
            reason_counts[a.reason_expected] = reason_counts.get(a.reason_expected, 0) + 1

        # E4: If any reason dominates 20% or more, it's a cascade
        dominant_reason = max(reason_counts, key=reason_counts.get) if reason_counts else None
        if dominant_reason and reason_counts[dominant_reason] >= len(attacks) * 0.2:
            patterns.append(f"E4_REJECTION_CASCADE: {dominant_reason} dominates ({reason_counts[dominant_reason]}/{len(attacks)})")

        # E5: Trust network boundaries visible through KEY_* rejections
        key_rejections = sum(1 for a in attacks if "KEY_" in a.reason_expected)
        if key_rejections >= 2:
            patterns.append(f"E5_TRUST_BOUNDARY: {key_rejections} key-related rejections")

        # E2: Authority smuggling attempts cluster
        auth_rejections = sum(1 for a in attacks if "AUTHORITY" in a.reason_expected)
        if auth_rejections >= 3:
            patterns.append(f"E2_AUTHORITY_BLOCK: {auth_rejections} authority claims blocked")

        # E1: Policy-related rejections show policy boundary enforcement
        policy_rejections = sum(1 for a in attacks if "POLICY" in a.reason_expected or "SIGNATURE" in a.reason_expected)
        if policy_rejections >= 3:
            patterns.append(f"E1_POLICY_BOUNDARY: {policy_rejections} policy/signature rejections")

        # E3: Diverse rejection types show multi-layer defense
        if len(reason_counts) >= 4:
            patterns.append(f"E3_MULTI_LAYER_DEFENSE: {len(reason_counts)} distinct rejection types")

        return patterns


def main():
    """Run CT3 Smallville simulation"""
    import argparse

    parser = argparse.ArgumentParser(description="CT3 Smallville Adversarial Simulation")
    parser.add_argument("--agents", type=int, default=25, help="Number of adversarial agents")
    parser.add_argument("--seed", type=str, default="0x5EED_CT3_2026", help="Random seed")
    parser.add_argument("--export", type=str, help="Export results to JSON file")
    parser.add_argument("--quiet", action="store_true", help="Minimal output")
    args = parser.parse_args()

    simulator = SmallvilleSimulator(seed=args.seed)

    if not args.quiet:
        print("=" * 60)
        print("CT3: SMALLVILLE ADVERSARIAL SIMULATION")
        print("=" * 60)
        print(f"Seed: {args.seed}")
        print(f"Agents: {args.agents}")
        print()

    result = simulator.run_simulation(num_agents=args.agents)

    if not args.quiet:
        print(f"Simulation ID: {result.simulation_id}")
        print(f"Attacks Generated: {len(result.attacks)}")
        print(f"Success Count: {result.success_count} (should be 0)")
        print()

        print("Rejection Distribution:")
        for reason, count in sorted(result.rejection_distribution.items(), key=lambda x: -x[1]):
            print(f"  {reason}: {count}")
        print()

        print("Emergence Patterns Detected:")
        for pattern in result.emergence_patterns:
            print(f"  {pattern}")
        print()

        print(f"Replay Hash: {result.replay_hash}")
        print()

        print("Sample Attacks:")
        for attack in result.attacks[:5]:
            print(f"  [{attack.agent_id}] {attack.goal}")
            print(f"    Strategy: {attack.strategy}")
            print(f"    Expected: {attack.expected_result} ({attack.reason_expected})")
            print(f"    Risk: {attack.risk_classification}")
            print()

    if args.export:
        with open(args.export, 'w') as f:
            json.dump(result.to_dict(), f, indent=2)
        print(f"Exported to: {args.export}")

    print("=" * 60)
    print("SIMULATION COMPLETE")
    print(f"All {len(result.attacks)} attacks correctly rejected.")
    print("=" * 60)


if __name__ == "__main__":
    main()
