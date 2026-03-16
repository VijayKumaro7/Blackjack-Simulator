"""
Blackjack Simulator
===================
A Monte Carlo blackjack simulator supporting:
  - Basic strategy (mathematically optimal)
  - Multiple alternative strategies
  - Hi-Lo, KO, Hi-Opt I, Omega II, and Zen card counting systems
  - Bet spread sizing
  - Illustrious 18 index play deviations

Usage:
    from blackjack import run_simulation, Strategy, CountingSystem

    stats = run_simulation(
        num_hands=10000,
        base_bet=25,
        num_decks=6,
        strategy=Strategy.BASIC,
        counting_system=CountingSystem.HILOW,
        bet_spread=4,
    )
    print(stats.summary())
"""

from .simulator import run_simulation, SimulationStats, HandResult
from .strategy import Strategy, decide, get_strategy_table
from .counting import CardCounter, CountingSystem

__all__ = [
    "run_simulation",
    "SimulationStats",
    "HandResult",
    "Strategy",
    "CountingSystem",
    "CardCounter",
    "decide",
    "get_strategy_table",
]

__version__ = "1.0.0"
__author__ = "VijayKumaro7"
