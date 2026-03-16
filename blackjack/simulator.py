"""
Blackjack Simulator — Core Engine
Simulates thousands of blackjack hands with configurable strategy and card counting.
"""

import random
from dataclasses import dataclass, field
from typing import Optional
from .strategy import decide, Strategy
from .counting import CardCounter, CountingSystem


@dataclass
class HandResult:
    outcome: str          # 'win', 'loss', 'push', 'blackjack'
    profit: float
    bet: float
    player_cards: list[int]
    dealer_cards: list[int]
    true_count: float = 0.0


@dataclass
class SimulationStats:
    hands: int = 0
    wins: int = 0
    losses: int = 0
    pushes: int = 0
    blackjacks: int = 0
    total_wagered: float = 0.0
    net_earnings: float = 0.0
    earnings_history: list[float] = field(default_factory=list)

    @property
    def win_rate(self) -> float:
        played = self.wins + self.losses + self.pushes
        return (self.wins / played * 100) if played else 0.0

    @property
    def house_edge(self) -> float:
        return (-self.net_earnings / self.total_wagered * 100) if self.total_wagered else 0.0

    def summary(self) -> dict:
        return {
            "hands":         self.hands,
            "wins":          self.wins,
            "losses":        self.losses,
            "pushes":        self.pushes,
            "blackjacks":    self.blackjacks,
            "net_earnings":  round(self.net_earnings, 2),
            "total_wagered": round(self.total_wagered, 2),
            "win_rate":      round(self.win_rate, 2),
            "house_edge":    round(self.house_edge, 4),
        }


def _build_shoe(num_decks: int) -> list[int]:
    """Build and shuffle a multi-deck shoe. Card values are pip values; Ace = 11."""
    single = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11]
    shoe = single * 4 * num_decks
    random.shuffle(shoe)
    return shoe


def _hand_value(cards: list[int]) -> int:
    total = sum(cards)
    aces = cards.count(11)
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total


def _is_soft(cards: list[int]) -> bool:
    return 11 in cards and _hand_value(cards) <= 21


def play_hand(
    shoe: list[int],
    idx: list[int],
    strategy: Strategy,
    base_bet: float,
    counter: Optional[CardCounter],
    num_decks: int,
) -> HandResult:
    """Play a single blackjack hand and return the result."""

    def draw() -> int:
        # Reshuffle when fewer than ~15% of cards remain
        if idx[0] >= len(shoe) - max(10, int(len(shoe) * 0.15)):
            new_shoe = _build_shoe(num_decks)
            shoe[:] = new_shoe
            idx[0] = 0
            if counter:
                counter.reset()
        card = shoe[idx[0]]
        idx[0] += 1
        return card

    def track(card: int):
        if counter:
            counter.update(card)

    # Deal initial cards
    p_cards = [draw(), draw()]
    d_cards = [draw(), draw()]

    for c in p_cards:
        track(c)
    track(d_cards[0])   # dealer up-card; hole card tracked when revealed

    d_up = d_cards[0]
    remaining_decks = max(0.5, (len(shoe) - idx[0]) / 52)
    true_count = counter.true_count(remaining_decks) if counter else 0.0

    # Bet sizing via card counting spread
    bet = base_bet
    if counter and counter.system != CountingSystem.NONE:
        bet = counter.size_bet(base_bet, true_count)

    # Blackjack checks
    p_bj = _hand_value(p_cards) == 21
    d_bj = _hand_value(d_cards) == 21

    if p_bj and d_bj:
        track(d_cards[1])
        return HandResult("push", 0.0, bet, p_cards, d_cards, true_count)
    if p_bj:
        track(d_cards[1])
        return HandResult("blackjack", bet * 1.5, bet, p_cards, d_cards, true_count)
    if d_bj:
        track(d_cards[1])
        return HandResult("loss", -bet, bet, p_cards, d_cards, true_count)

    # ── Player action ─────────────────────────────────────────────────────────
    action = decide(strategy, p_cards, d_up, true_count)

    # Split (simplified: play each sub-hand vs dealer independently)
    if action == "P":
        split_profit = 0.0
        for i in range(2):
            s_hand = [p_cards[i], draw()]
            track(s_hand[-1])
            while True:
                act = decide(strategy, s_hand, d_up, true_count)
                if act in ("S", "P"):
                    break
                if act == "D" and len(s_hand) == 2:
                    c = draw(); track(c); s_hand.append(c)
                    split_profit -= bet   # extra wager
                    break
                c = draw(); track(c); s_hand.append(c)
                if _hand_value(s_hand) >= 21:
                    break
            sv = _hand_value(s_hand)
            # Resolve sub-hand vs dealer
            if sv > 21:
                split_profit -= bet
            else:
                d_clone = list(d_cards)
                track(d_clone[1])
                while _hand_value(d_clone) < 17:
                    c = draw(); track(c); d_clone.append(c)
                dv = _hand_value(d_clone)
                if dv > 21 or sv > dv:
                    split_profit += bet
                elif sv == dv:
                    pass  # push
                else:
                    split_profit -= bet
        outcome = "win" if split_profit > 0 else ("push" if split_profit == 0 else "loss")
        return HandResult(outcome, split_profit, bet * 2, p_cards, d_cards, true_count)

    # Double down
    if action == "D" and len(p_cards) == 2:
        c = draw(); track(c); p_cards.append(c)
        bet *= 2
    else:
        # Hit loop
        while action == "H":
            c = draw(); track(c); p_cards.append(c)
            if _hand_value(p_cards) >= 21:
                break
            action = decide(strategy, p_cards, d_up, true_count)

    p_total = _hand_value(p_cards)
    if p_total > 21:
        track(d_cards[1])
        return HandResult("loss", -bet, bet, p_cards, d_cards, true_count)

    # ── Dealer action ─────────────────────────────────────────────────────────
    track(d_cards[1])
    while _hand_value(d_cards) < 17:
        c = draw(); track(c); d_cards.append(c)

    d_total = _hand_value(d_cards)

    if d_total > 21 or p_total > d_total:
        return HandResult("win", bet, bet, p_cards, d_cards, true_count)
    if p_total == d_total:
        return HandResult("push", 0.0, bet, p_cards, d_cards, true_count)
    return HandResult("loss", -bet, bet, p_cards, d_cards, true_count)


def run_simulation(
    num_hands: int = 1000,
    base_bet: float = 25.0,
    num_decks: int = 6,
    strategy: Strategy = Strategy.BASIC,
    counting_system: CountingSystem = CountingSystem.NONE,
    bet_spread: int = 4,
    track_every: int = 50,
    verbose: bool = False,
) -> SimulationStats:
    """
    Run a full blackjack simulation.

    Args:
        num_hands:       Number of hands to simulate.
        base_bet:        Base bet amount in dollars.
        num_decks:       Number of decks in the shoe (1–8).
        strategy:        Player strategy (see Strategy enum).
        counting_system: Card counting system (see CountingSystem enum).
        bet_spread:      Maximum bet multiplier when count is favorable.
        track_every:     Record earnings snapshot every N hands.
        verbose:         Print hand-by-hand output.

    Returns:
        SimulationStats object with full results.
    """
    shoe = _build_shoe(num_decks)
    idx = [0]
    counter = CardCounter(counting_system, bet_spread) if counting_system != CountingSystem.NONE else None
    stats = SimulationStats()

    for h in range(num_hands):
        result = play_hand(shoe, idx, strategy, base_bet, counter, num_decks)
        stats.hands += 1
        stats.total_wagered += result.bet
        stats.net_earnings += result.profit

        if result.outcome in ("win", "blackjack"):
            stats.wins += 1
            if result.outcome == "blackjack":
                stats.blackjacks += 1
        elif result.outcome == "loss":
            stats.losses += 1
        else:
            stats.pushes += 1

        if h % track_every == 0:
            stats.earnings_history.append(round(stats.net_earnings, 2))

        if verbose:
            pv = "+".join(str(c) for c in result.player_cards)
            sign = "+" if result.profit >= 0 else ""
            print(
                f"Hand {h+1:>5}: [{pv}]={_hand_value(result.player_cards)} "
                f"vs {result.dealer_cards[0]}  →  {result.outcome:<10} "
                f"{sign}${result.profit:.0f}  | Bank: ${stats.net_earnings:+.0f}"
                + (f"  TC:{result.true_count:+.1f}" if counter else "")
            )

    stats.earnings_history.append(round(stats.net_earnings, 2))
    return stats
