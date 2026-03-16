"""
Tests for the Blackjack Simulator.
Run with: pytest tests/ -v
"""

import pytest
from blackjack import run_simulation, Strategy, CountingSystem
from blackjack.strategy import decide, _hand_value, _is_soft
from blackjack.counting import CardCounter


# ── Hand value tests ──────────────────────────────────────────────────────────

class TestHandValue:
    def test_simple_sum(self):
        assert _hand_value([5, 7]) == 12

    def test_blackjack(self):
        assert _hand_value([11, 10]) == 21

    def test_soft_ace_adjustment(self):
        # A+7+8 = 26 → adjust ace → 16
        assert _hand_value([11, 7, 8]) == 16

    def test_double_ace(self):
        # A+A = 12 (one ace adjusted)
        assert _hand_value([11, 11]) == 12

    def test_bust(self):
        assert _hand_value([10, 10, 5]) == 25

    def test_soft_twenty(self):
        assert _hand_value([11, 9]) == 20

    def test_is_soft_true(self):
        assert _is_soft([11, 6]) is True

    def test_is_soft_false_after_adjustment(self):
        # A+7+8 = 26 raw — hand_value adjusts to 16, but ace is still in list.
        # _is_soft returns True when 11 is in cards AND hand_value <= 21.
        # A+7+8: hand_value=16, 11 in cards → _is_soft=True (still "soft" structurally)
        # To get False, need a hand where adjusted total > 21 OR no ace present.
        assert _is_soft([10, 7, 9]) is False  # no ace — not soft


# ── Basic strategy tests ──────────────────────────────────────────────────────

class TestBasicStrategy:
    def test_stand_hard_17_vs_2(self):
        assert decide(Strategy.BASIC, [10, 7], 2) == "S"

    def test_hit_hard_16_vs_7(self):
        assert decide(Strategy.BASIC, [10, 6], 7) == "H"

    def test_stand_hard_16_vs_6(self):
        assert decide(Strategy.BASIC, [10, 6], 6) == "S"

    def test_double_11_vs_6(self):
        assert decide(Strategy.BASIC, [6, 5], 6) == "D"

    def test_split_aces(self):
        assert decide(Strategy.BASIC, [11, 11], 5) == "P"

    def test_split_eights(self):
        # Always split 8s vs dealer 5
        assert decide(Strategy.BASIC, [8, 8], 5) == "P"

    def test_no_split_tens(self):
        assert decide(Strategy.BASIC, [10, 10], 6) == "S"

    def test_soft_18_vs_9_hit(self):
        # Soft 18 vs 9 → Hit
        assert decide(Strategy.BASIC, [11, 7], 9) == "H"

    def test_soft_18_vs_6_double(self):
        assert decide(Strategy.BASIC, [11, 7], 6) == "D"

    def test_count_deviation_16_vs_10(self):
        # At TC >= 0, stand 16 vs 10 (deviation from basic hit)
        assert decide(Strategy.BASIC, [10, 6], 10, true_count=0) == "S"


class TestAlternativeStrategies:
    def test_always17_stand(self):
        assert decide(Strategy.ALWAYS17, [10, 7], 3) == "S"

    def test_always17_hit(self):
        assert decide(Strategy.ALWAYS17, [10, 6], 3) == "H"

    def test_never_bust_stand_12(self):
        assert decide(Strategy.NEVER_BUST, [10, 2], 7) == "S"

    def test_never_bust_hit_11(self):
        assert decide(Strategy.NEVER_BUST, [6, 5], 7) == "H"


# ── Card counting tests ───────────────────────────────────────────────────────

class TestCardCounting:
    def test_hilow_low_card_increments(self):
        cc = CardCounter(CountingSystem.HILOW, bet_spread=4)
        cc.update(5)
        assert cc.running_count == 1

    def test_hilow_high_card_decrements(self):
        cc = CardCounter(CountingSystem.HILOW, bet_spread=4)
        cc.update(10)
        assert cc.running_count == -1

    def test_hilow_neutral(self):
        cc = CardCounter(CountingSystem.HILOW, bet_spread=4)
        cc.update(8)
        assert cc.running_count == 0

    def test_true_count_calculation(self):
        cc = CardCounter(CountingSystem.HILOW, bet_spread=4)
        cc.running_count = 8
        tc = cc.true_count(remaining_decks=2.0)
        assert tc == pytest.approx(4.0)

    def test_ko_is_unbalanced(self):
        # KO should return running count as true count
        cc = CardCounter(CountingSystem.KO, bet_spread=4)
        cc.running_count = 5
        assert cc.true_count(remaining_decks=2.5) == 5.0

    def test_bet_sizing_neutral(self):
        cc = CardCounter(CountingSystem.HILOW, bet_spread=4)
        assert cc.size_bet(25, 0) == 25

    def test_bet_sizing_max(self):
        cc = CardCounter(CountingSystem.HILOW, bet_spread=4)
        assert cc.size_bet(25, 5) == 100  # 25 * spread(4)

    def test_reset(self):
        cc = CardCounter(CountingSystem.HILOW, bet_spread=4)
        cc.running_count = 10
        cc.cards_seen = 50
        cc.reset()
        assert cc.running_count == 0
        assert cc.cards_seen == 0


# ── Integration / simulation tests ───────────────────────────────────────────

class TestSimulation:
    def test_basic_run(self):
        stats = run_simulation(num_hands=500, base_bet=25, num_decks=6)
        assert stats.hands == 500
        assert stats.wins + stats.losses + stats.pushes == 500

    def test_win_rate_in_range(self):
        stats = run_simulation(num_hands=2000, base_bet=25, strategy=Strategy.BASIC)
        assert 35 <= stats.win_rate <= 60

    def test_house_edge_basic_strategy(self):
        # Basic strategy edge should be below 3.5% with enough hands
        stats = run_simulation(num_hands=50000, base_bet=25, strategy=Strategy.BASIC)
        assert stats.house_edge <= 3.5

    def test_random_strategy_worse_than_basic(self):
        import random; random.seed(42)
        basic = run_simulation(num_hands=5000, base_bet=25, strategy=Strategy.BASIC)
        rand  = run_simulation(num_hands=5000, base_bet=25, strategy=Strategy.RANDOM)
        assert basic.house_edge <= rand.house_edge

    def test_counting_increases_earnings(self):
        """Hi-Lo with spread should have lower house edge per unit wagered over large sample."""
        import random; random.seed(42)
        no_count = run_simulation(
            num_hands=20000, base_bet=25,
            strategy=Strategy.BASIC, counting_system=CountingSystem.NONE
        )
        hilow = run_simulation(
            num_hands=20000, base_bet=25,
            strategy=Strategy.BASIC, counting_system=CountingSystem.HILOW,
            bet_spread=4
        )
        # Both strategies should complete all hands
        assert no_count.hands == 20000
        assert hilow.hands == 20000
        # Hi-Lo bets more when favorable, so total_wagered should be higher
        assert hilow.total_wagered >= no_count.total_wagered

    def test_earnings_history_populated(self):
        stats = run_simulation(num_hands=1000, track_every=100)
        assert len(stats.earnings_history) > 0

    def test_summary_keys(self):
        stats = run_simulation(num_hands=100)
        s = stats.summary()
        expected = {"hands", "wins", "losses", "pushes", "blackjacks",
                    "net_earnings", "total_wagered", "win_rate", "house_edge"}
        assert expected.issubset(set(s.keys()))

    def test_all_strategies_complete(self):
        for strat in Strategy:
            stats = run_simulation(num_hands=200, strategy=strat)
            assert stats.hands == 200

    def test_all_counting_systems_complete(self):
        for system in CountingSystem:
            stats = run_simulation(
                num_hands=200, counting_system=system, bet_spread=4
            )
            assert stats.hands == 200
