#!/usr/bin/env python3
"""
CONQUESTmon-Gotchi: Core Engine

A deterministic, kernel-integrated governance simulation.
Raise your castle. Survive opposition. Achieve legendary status.

Author: Your Lateral Thinking Engine
Date: February 15, 2026
"""

import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timezone
import hashlib
import random


# ============================================================================
# CORE DATA STRUCTURES
# ============================================================================

@dataclass
class OppositionState:
    """Enemy organism applying structural pressure."""
    aggression: float = 2.0
    capability: float = 2.0
    posture: str = "OBSERVE"  # OBSERVE, PROBE, SABOTAGE, ATTACK

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CastleState:
    """Living castle creature."""
    # Primary metrics (0-10 unless noted)
    territory: float = 1.0          # Land owned [0-20]
    stability: float = 5.0          # Structural integrity
    cohesion: float = 5.0           # Internal unity
    knowledge: float = 3.0          # Wisdom acquired
    entropy: float = 2.0            # Disorder [grows]

    # Secondary (Memory/Hysteresis)
    debt: float = 0.0               # Owed burden
    inertia: float = 0.0            # Stuck resistance
    fatigue: float = 0.0            # Exhaustion
    victory_streak: int = 0         # Consecutive rounds at legendary conditions

    # Opposition
    opposition: OppositionState = field(default_factory=OppositionState)

    # Metadata
    round: int = 1
    day: int = 1
    seed: int = 0
    ledger: List[Dict] = field(default_factory=list)

    def clamp(self, name: str, val: float, min_v: float, max_v: float) -> float:
        """Clamp value and update in place."""
        clamped = max(min_v, min(max_v, val))
        setattr(self, name, clamped)
        return clamped

    def to_dict(self) -> dict:
        """Serialize for ledger."""
        d = asdict(self)
        d['opposition'] = self.opposition.to_dict()
        d['ledger'] = []  # Don't include full ledger in state
        return d


# ============================================================================
# PHYSICS ENGINE
# ============================================================================

def compute_structural_margin(state: CastleState) -> float:
    """
    Calculate viability indicator L.

    L > 5:   FLOURISHING
    L 2-5:   STABLE
    L 0-2:   STRUGGLING
    L < 0:   CRITICAL
    L ≤ -3:  COLLAPSE
    """
    L = (
        state.stability
        + 0.5 * state.cohesion
        + 0.5 * state.knowledge
        - state.entropy
        - 0.5 * state.debt
        - 0.5 * state.inertia
        - 0.3 * state.fatigue
        - 0.2 * state.opposition.aggression
    )
    return round(L, 2)


def apply_entropy_drift(state: CastleState) -> None:
    """Entropy grows unless knowledge controls it."""
    state.entropy += 0.1

    if state.knowledge > 5:
        state.entropy -= 0.05

    if state.debt > 5:
        state.entropy += 0.1

    state.clamp('entropy', state.entropy, 0, 20)


def apply_debt_decay(state: CastleState) -> None:
    """Debt grows, slowly fades with rest."""
    if state.fatigue > 0:
        state.debt -= 0.05
    else:
        state.debt += 0.02

    state.clamp('debt', state.debt, 0, 20)


def apply_inertia_decay(state: CastleState) -> None:
    """Inertia slowly fades."""
    state.inertia -= 0.03
    state.clamp('inertia', state.inertia, 0, 10)


def apply_fatigue_decay(state: CastleState) -> None:
    """Fatigue decays slowly."""
    state.fatigue -= 0.05
    state.clamp('fatigue', state.fatigue, 0, 10)


def update_opposition(state: CastleState) -> None:
    """Opposition grows with perceived weakness."""
    o = state.opposition

    # Aggression grows from weakness
    weakness = max(0, (7.0 - state.stability) / 7.0)
    o.aggression += weakness * 0.05
    o.aggression += state.debt * 0.03

    # Capability grows from chaos
    o.capability += state.entropy * 0.02

    # Decay if system strong
    if state.stability > 8 and state.cohesion > 7:
        o.aggression = max(0, o.aggression - 0.1)

    o.aggression = round(max(0, min(10, o.aggression)), 2)
    o.capability = round(max(0, min(10, o.capability)), 2)


def decide_posture(state: CastleState) -> str:
    """Opposition chooses posture based on castle state."""
    margin = compute_structural_margin(state)

    if margin > 5:
        return "OBSERVE"
    elif state.debt > 3:
        return "SABOTAGE"
    elif state.stability < 4:
        return "ATTACK"
    else:
        return "PROBE"


def apply_opposition_effect(state: CastleState) -> None:
    """Opposition action happens."""
    posture = state.opposition.posture

    if posture == "OBSERVE":
        pass  # No effect

    elif posture == "PROBE":
        state.entropy += 0.4
        state.cohesion -= 0.2

    elif posture == "SABOTAGE":
        state.debt += 0.6
        state.fatigue += 0.3

    elif posture == "ATTACK":
        state.stability -= 0.7
        state.entropy += 0.5

    # Clamp
    state.clamp('entropy', state.entropy, 0, 20)
    state.clamp('cohesion', state.cohesion, 0, 10)
    state.clamp('debt', state.debt, 0, 20)
    state.clamp('fatigue', state.fatigue, 0, 10)
    state.clamp('stability', state.stability, 0, 10)


# ============================================================================
# PLAYER ACTIONS
# ============================================================================

def action_expand(state: CastleState) -> bool:
    """Grow territory but accrue debt and entropy."""
    state.territory += 1.0
    state.entropy += 0.3
    state.debt += 0.4
    state.clamp('territory', state.territory, 0, 25)
    state.clamp('entropy', state.entropy, 0, 20)
    state.clamp('debt', state.debt, 0, 20)
    return True


def action_fortify(state: CastleState) -> bool:
    """Strengthen stability but add fatigue."""
    state.stability += 1.5
    state.entropy -= 0.2
    state.fatigue += 0.5
    state.clamp('stability', state.stability, 0, 10)
    state.clamp('entropy', state.entropy, 0, 20)
    state.clamp('fatigue', state.fatigue, 0, 10)
    return True


def action_celebrate(state: CastleState) -> bool:
    """Boost morale but need to not be exhausted."""
    if state.fatigue > 8:
        return False  # Cannot celebrate if exhausted

    state.cohesion += 1.2
    state.fatigue += 0.3
    state.entropy -= 0.1
    state.clamp('cohesion', state.cohesion, 0, 10)
    state.clamp('fatigue', state.fatigue, 0, 10)
    state.clamp('entropy', state.entropy, 0, 20)
    return True


def action_study(state: CastleState) -> bool:
    """Learn wisdom for long-term resilience."""
    state.knowledge += 1.0
    state.inertia += 0.2
    state.clamp('knowledge', state.knowledge, 0, 10)
    state.clamp('inertia', state.inertia, 0, 10)
    return True


def action_rest(state: CastleState) -> bool:
    """Recover fatigue, slow debt decay."""
    state.fatigue -= 1.0
    state.debt -= 0.1
    state.clamp('fatigue', state.fatigue, 0, 10)
    state.clamp('debt', state.debt, 0, 20)
    return True


ACTION_MAP = {
    1: ("EXPAND", action_expand),
    2: ("FORTIFY", action_fortify),
    3: ("CELEBRATE", action_celebrate),
    4: ("STUDY", action_study),
    5: ("REST", action_rest),
}


# ============================================================================
# GAME STATE & LOGIC
# ============================================================================

class CastleGame:
    """Main game engine."""

    def __init__(self, seed: int = None):
        if seed is None:
            seed = random.randint(0, 2**31 - 1)

        random.seed(seed)
        self.state = CastleState(seed=seed)
        self.game_over = False
        self.victory = False

    def execute_round(self, action: int) -> Tuple[bool, str]:
        """Execute one full round. Returns (success, message)."""
        if self.game_over:
            return False, "Game is over."

        if action not in ACTION_MAP:
            return False, f"Invalid action. Choose 1-5."

        action_name, action_func = ACTION_MAP[action]

        # 1. Try action
        success = action_func(self.state)
        if not success:
            return False, f"{action_name} failed: Cannot perform this action."

        # 2. Update opposition
        update_opposition(self.state)

        # 3. Decide posture
        self.state.opposition.posture = decide_posture(self.state)

        # 4. Apply opposition effect
        apply_opposition_effect(self.state)

        # 5. Entropy drift
        apply_entropy_drift(self.state)

        # 6. Memory decay
        apply_debt_decay(self.state)
        apply_inertia_decay(self.state)
        apply_fatigue_decay(self.state)

        # 7. Compute margin
        margin = compute_structural_margin(self.state)

        # 8. Log to ledger
        ledger_entry = {
            "round": self.state.round,
            "day": self.state.day,
            "action": action,
            "action_name": action_name,
            "state_before": None,  # Could add if needed
            "state_after": self.state.to_dict(),
            "opposition_posture": self.state.opposition.posture,
            "structural_margin": margin,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.state.ledger.append(ledger_entry)

        # 9. Check victory/collapse
        if margin <= -3 or self.state.stability <= 0 or self.state.territory <= 0:
            self.game_over = True
            self.victory = False
            return True, "COLLAPSE: Your castle has fallen."

        # Check for legendary victory
        if self._check_legendary_victory():
            self.game_over = True
            self.victory = True
            return True, "VICTORY: You have achieved Legendary Bastion!"

        # 10. Advance round/day
        self.state.round += 1
        if self.state.round % 6 == 0:
            self.state.day += 1

        msg = f"Round {self.state.round} complete. Opposition: {self.state.opposition.posture}."
        return True, msg

    def _check_legendary_victory(self) -> bool:
        """Declare victory only after 5 consecutive rounds meeting legendary conditions."""
        margin = compute_structural_margin(self.state)
        conditions_met = (
            self.state.territory >= 8
            and self.state.entropy < 6
            and self.state.debt < 2
            and self.state.opposition.posture == "OBSERVE"
            and margin > 5
        )
        if conditions_met:
            self.state.victory_streak += 1
        else:
            self.state.victory_streak = 0
        return conditions_met and self.state.victory_streak >= 5

    def get_margin_status(self) -> str:
        """Return status indicator."""
        margin = compute_structural_margin(self.state)
        if margin > 5:
            return "FLOURISHING"
        elif margin >= 2:
            return "STABLE"
        elif margin >= 0:
            return "STRUGGLING"
        elif margin > -3:
            return "CRITICAL"
        else:
            return "COLLAPSE"

    def get_state_dict(self) -> dict:
        """Export full state."""
        return self.state.to_dict()

    def to_ledger_json(self) -> str:
        """Export full ledger."""
        return json.dumps(
            {
                "seed": self.state.seed,
                "final_round": self.state.round,
                "final_day": self.state.day,
                "victory": self.victory,
                "final_margin": compute_structural_margin(self.state),
                "ledger": self.state.ledger,
            },
            indent=2,
        )


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    # Quick test
    game = CastleGame(seed=12345)

    for i in range(10):
        action = (i % 5) + 1
        success, msg = game.execute_round(action)
        print(f"Round {game.state.round}: {msg}")
        print(
            f"  Territory: {game.state.territory:.1f} | "
            f"Stability: {game.state.stability:.1f} | "
            f"Entropy: {game.state.entropy:.1f} | "
            f"Opposition: {game.state.opposition.posture}"
        )

    print("\nFinal ledger (last 2 entries):")
    for entry in game.state.ledger[-2:]:
        print(f"  Round {entry['round']}: {entry['action_name']} → {entry['opposition_posture']}")
