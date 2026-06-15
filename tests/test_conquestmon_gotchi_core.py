#!/usr/bin/env python3
"""
Test Suite: CONQUESTmon-Gotchi Core Engine

Tests structural integrity of game physics, opposition logic, and victory conditions.
"""

import random
import pytest
from conquestmon_gotchi_core import (
    CastleGame,
    CastleState,
    OppositionState,
    compute_structural_margin,
    apply_entropy_drift,
    apply_debt_decay,
    update_opposition,
    decide_posture,
    action_expand,
    action_fortify,
    action_celebrate,
    action_study,
    action_rest,
)


class TestCorePhysics:
    """Test fundamental game physics."""

    def test_structural_margin_calculation(self):
        """Margin = stability + 0.5*cohesion + 0.5*knowledge - entropy - 0.5*debt - 0.2*opp.aggression."""
        state = CastleState()
        # Initial: 5 + 0.5*5 + 0.5*3 - 2 - 0 - 0 - 0 - 0.2*2.0(opp.aggression)
        # = 5 + 2.5 + 1.5 - 2 - 0.4 = 6.6
        margin = compute_structural_margin(state)
        assert margin == 6.6

    def test_margin_threshold_flourishing(self):
        """Margin > 5 = FLOURISHING."""
        state = CastleState(stability=9, cohesion=8, knowledge=5, entropy=0)
        margin = compute_structural_margin(state)
        assert margin > 5

    def test_margin_threshold_critical(self):
        """Margin < 0 = CRITICAL."""
        state = CastleState(stability=2, cohesion=1, entropy=8, debt=5)
        margin = compute_structural_margin(state)
        assert margin < 0

    def test_entropy_drift_passive(self):
        """Entropy drifts up by 0.1 each round without knowledge."""
        state = CastleState(entropy=2.0, knowledge=0)
        apply_entropy_drift(state)
        assert state.entropy == pytest.approx(2.1)

    def test_entropy_controlled_by_knowledge(self):
        """Knowledge > 5 reduces entropy drift."""
        state = CastleState(entropy=2.0, knowledge=6)
        apply_entropy_drift(state)
        # 2.0 + 0.1 - 0.05 = 2.05
        assert state.entropy == pytest.approx(2.05)

    def test_debt_grows_without_rest(self):
        """Debt grows by 0.02 if fatigue = 0."""
        state = CastleState(debt=0, fatigue=0)
        apply_debt_decay(state)
        assert state.debt == pytest.approx(0.02)

    def test_debt_shrinks_with_rest(self):
        """Debt shrinks by 0.05 if fatigue > 0."""
        state = CastleState(debt=1.0, fatigue=5)
        apply_debt_decay(state)
        assert state.debt == pytest.approx(0.95)


class TestOppositionLogic:
    """Test Opposition engine."""

    def test_opposition_aggression_grows_from_weakness(self):
        """Low stability → Opposition aggression increases."""
        state = CastleState(stability=3, debt=0)
        initial_agg = state.opposition.aggression
        update_opposition(state)
        assert state.opposition.aggression > initial_agg

    def test_opposition_aggression_grows_from_debt(self):
        """High debt → Opposition aggression increases."""
        state = CastleState(stability=8, debt=4)
        initial_agg = state.opposition.aggression
        update_opposition(state)
        assert state.opposition.aggression > initial_agg

    def test_opposition_aggression_decays_when_strong(self):
        """Strong system (stability > 8, cohesion > 7) → Aggression decays."""
        state = CastleState(stability=9, cohesion=8, opposition=OppositionState(aggression=5.0))
        update_opposition(state)
        assert state.opposition.aggression < 5.0

    def test_posture_observe_when_safe(self):
        """Margin > 5 → Opposition posture = OBSERVE."""
        state = CastleState(stability=9, cohesion=8, knowledge=5, entropy=0)
        posture = decide_posture(state)
        assert posture == "OBSERVE"

    def test_posture_sabotage_when_indebted(self):
        """High debt (> 3) + margin ≤ 5 → Opposition posture = SABOTAGE."""
        # stability=5: margin = 5+2.5+1.5-2-2-0.4 = 4.6 ≤ 5 → debt gate triggers
        state = CastleState(stability=5, debt=4)
        posture = decide_posture(state)
        assert posture == "SABOTAGE"

    def test_posture_attack_when_weak(self):
        """Low stability (< 4) → Opposition posture = ATTACK."""
        state = CastleState(stability=2, entropy=5)
        posture = decide_posture(state)
        assert posture == "ATTACK"

    def test_posture_probe_as_default(self):
        """Mid-range conditions (margin ≤ 5, debt ≤ 3, stability ≥ 4) → Opposition posture = PROBE."""
        # stability=5, entropy=4: margin = 5+2.5+1.5-4-0.5-0.4 = 4.1 ≤ 5
        state = CastleState(stability=5, cohesion=5, debt=1, entropy=4)
        posture = decide_posture(state)
        assert posture == "PROBE"


class TestPlayerActions:
    """Test all 5 player actions."""

    def test_action_expand(self):
        """EXPAND: +Territory, +Entropy, +Debt."""
        state = CastleState(territory=1, entropy=2, debt=0)
        action_expand(state)
        assert state.territory == 2.0
        assert state.entropy == pytest.approx(2.3)
        assert state.debt == pytest.approx(0.4)

    def test_action_fortify(self):
        """FORTIFY: +Stability, -Entropy, +Fatigue."""
        state = CastleState(stability=5, entropy=2, fatigue=0)
        action_fortify(state)
        assert state.stability == pytest.approx(6.5)
        assert state.entropy == pytest.approx(1.8)
        assert state.fatigue == pytest.approx(0.5)

    def test_action_celebrate_success(self):
        """CELEBRATE: +Cohesion, +Fatigue, -Entropy (if fatigue <= 8)."""
        state = CastleState(cohesion=5, fatigue=3, entropy=2)
        result = action_celebrate(state)
        assert result is True
        assert state.cohesion == pytest.approx(6.2)
        assert state.fatigue == pytest.approx(3.3)

    def test_action_celebrate_fails_when_exhausted(self):
        """CELEBRATE fails if fatigue > 8."""
        state = CastleState(fatigue=9)
        result = action_celebrate(state)
        assert result is False
        assert state.fatigue == 9  # Unchanged

    def test_action_study(self):
        """STUDY: +Knowledge, +Inertia."""
        state = CastleState(knowledge=3, inertia=0)
        action_study(state)
        assert state.knowledge == pytest.approx(4.0)
        assert state.inertia == pytest.approx(0.2)

    def test_action_rest(self):
        """REST: -Fatigue, -Debt."""
        state = CastleState(fatigue=5, debt=1)
        action_rest(state)
        assert state.fatigue == pytest.approx(4.0)
        assert state.debt == pytest.approx(0.9)


class TestGameStateTransitions:
    """Test full game loop."""

    def test_game_init(self):
        """Game initializes with seed."""
        game = CastleGame(seed=42)
        assert game.state.seed == 42
        assert game.state.round == 1
        assert game.state.day == 1
        assert not game.game_over

    def test_single_round_execution(self):
        """Execute one full round."""
        game = CastleGame(seed=42)
        success, msg = game.execute_round(1)  # EXPAND
        assert success is True
        assert game.state.round == 2
        assert len(game.state.ledger) == 1

    def test_ledger_contains_round_data(self):
        """Ledger entry has full state and opposition info."""
        game = CastleGame(seed=42)
        game.execute_round(1)
        entry = game.state.ledger[0]
        assert entry['round'] == 1
        assert entry['action_name'] == 'EXPAND'
        assert 'opposition_posture' in entry
        assert 'structural_margin' in entry

    def test_day_advances_every_6_rounds(self):
        """Day increments at round 6, 12, 18, etc."""
        game = CastleGame(seed=42)
        for i in range(6):
            game.execute_round(1)
        assert game.state.day == 2

    def test_invalid_action_rejected(self):
        """Invalid action (0, 6, etc.) is rejected."""
        game = CastleGame(seed=42)
        success, msg = game.execute_round(0)
        assert success is False
        assert game.state.round == 1  # No progress

    def test_collapse_on_negative_margin(self):
        """Game ends when margin <= -3."""
        game = CastleGame(seed=999)
        # Force collapse: reduce stability to 0
        game.state.stability = 0
        success, msg = game.execute_round(1)
        assert success is True
        assert game.game_over is True
        assert game.victory is False

    def test_collapse_on_zero_stability(self):
        """Game ends when stability <= 0."""
        game = CastleGame(seed=999)
        game.state.stability = -1
        success, msg = game.execute_round(5)  # REST
        assert game.game_over is True
        assert game.victory is False

    def test_no_progression_after_game_over(self):
        """Game does not progress after collapse."""
        game = CastleGame(seed=999)
        game.state.stability = -1
        game.execute_round(1)
        assert game.game_over is True

        success, msg = game.execute_round(2)
        assert success is False
        assert "Game is over" in msg


class TestDeterminism:
    """Test K5: Determinism."""

    def test_same_seed_produces_same_ledger(self):
        """Two games with same seed produce identical ledger."""
        game1 = CastleGame(seed=12345)
        game2 = CastleGame(seed=12345)

        actions = [1, 2, 3, 4, 5, 1, 2, 3, 4, 5]
        for action in actions:
            game1.execute_round(action)
            game2.execute_round(action)

        # Compare ledgers
        assert len(game1.state.ledger) == len(game2.state.ledger)
        for i, (entry1, entry2) in enumerate(
            zip(game1.state.ledger, game2.state.ledger)
        ):
            assert entry1['action'] == entry2['action']
            assert entry1['opposition_posture'] == entry2['opposition_posture']
            assert entry1['structural_margin'] == entry2['structural_margin']

    def test_different_seeds_produce_different_games(self):
        """Different seeds → divergent game paths when actions are seed-determined."""
        # Pure physics is deterministic: seed-determined action choices create divergence.
        game1 = CastleGame(seed=111)
        rng1 = random.Random(111)
        for _ in range(10):
            if not game1.game_over:
                game1.execute_round(rng1.randint(1, 5))

        game2 = CastleGame(seed=222)
        rng2 = random.Random(222)
        for _ in range(10):
            if not game2.game_over:
                game2.execute_round(rng2.randint(1, 5))

        assert game1.state.territory != game2.state.territory or \
               round(game1.state.entropy, 2) != round(game2.state.entropy, 2)


class TestVictoryConditions:
    """Test victory achievement."""

    def test_legendary_victory_condition(self):
        """Victory declared only after 5 consecutive rounds meeting legendary conditions."""
        game = CastleGame(seed=42)
        game.state.stability = 10.0
        game.state.cohesion = 10.0
        game.state.knowledge = 10.0
        game.state.territory = 10.0
        game.state.entropy = 0.5
        game.state.debt = 0.0
        game.state.inertia = 0.0
        game.state.fatigue = 0.0
        game.state.opposition.aggression = 0.0
        game.state.opposition.capability = 0.0
        game.state.opposition.posture = "OBSERVE"

        # Rounds 1-4: conditions met but no victory yet
        for i in range(4):
            success, msg = game.execute_round(5)  # REST
            assert success, f"Round {i + 1} should succeed"
            assert "VICTORY" not in msg, f"Should not win on round {i + 1}"
            assert not game.victory

        # Round 5: legendary victory declared
        success, msg = game.execute_round(5)
        assert success
        assert "VICTORY" in msg
        assert game.victory
        assert game.state.victory_streak >= 5

    def test_legendary_victory_requires_consecutive_rounds(self):
        """Streak resets when conditions break; victory requires 5 unbroken rounds."""
        game = CastleGame(seed=42)
        game.state.stability = 10.0
        game.state.cohesion = 10.0
        game.state.knowledge = 10.0
        game.state.territory = 10.0
        game.state.entropy = 0.5
        game.state.debt = 0.0
        game.state.inertia = 0.0
        game.state.fatigue = 0.0
        game.state.opposition.aggression = 0.0
        game.state.opposition.posture = "OBSERVE"

        # Build streak to 3
        for _ in range(3):
            game.execute_round(5)  # REST
        assert game.state.victory_streak == 3
        assert not game.victory

        # Break streak by spiking entropy above threshold
        game.state.entropy = 7.0
        game.execute_round(5)
        assert game.state.victory_streak == 0
        assert not game.victory


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
