"""
Player strategy module.
Implements basic strategy (mathematically optimal) and several alternative strategies.
Also includes card-counting index play deviations (Illustrious 18).
"""

from enum import Enum


class Strategy(Enum):
    BASIC      = "basic"       # Mathematically optimal basic strategy
    ALWAYS17   = "always17"    # Stand on hard 17+, hit otherwise
    MIMIC      = "mimic"       # Copy dealer rules (no splits/doubles)
    NEVER_BUST = "never_bust"  # Stand on any 12+ (never risk busting)
    RANDOM     = "random"      # Random hit/stand (50-50)


# ── Hard total decision table ─────────────────────────────────────────────────
# Rows: player hard total (5–21). Columns: dealer up-card (2–11, where 11=Ace).
# Actions: H=Hit, S=Stand, D=Double, P=Split
# fmt: off
_HARD_TABLE: dict[int, dict[int, str]] = {
    #       2    3    4    5    6    7    8    9   10   11(A)
    5:  {2:'H', 3:'H', 4:'H', 5:'H', 6:'H', 7:'H', 8:'H', 9:'H',10:'H',11:'H'},
    6:  {2:'H', 3:'H', 4:'H', 5:'H', 6:'H', 7:'H', 8:'H', 9:'H',10:'H',11:'H'},
    7:  {2:'H', 3:'H', 4:'H', 5:'H', 6:'H', 7:'H', 8:'H', 9:'H',10:'H',11:'H'},
    8:  {2:'H', 3:'H', 4:'H', 5:'H', 6:'H', 7:'H', 8:'H', 9:'H',10:'H',11:'H'},
    9:  {2:'H', 3:'D', 4:'D', 5:'D', 6:'D', 7:'H', 8:'H', 9:'H',10:'H',11:'H'},
    10: {2:'D', 3:'D', 4:'D', 5:'D', 6:'D', 7:'D', 8:'D', 9:'D',10:'H',11:'H'},
    11: {2:'D', 3:'D', 4:'D', 5:'D', 6:'D', 7:'D', 8:'D', 9:'D',10:'D',11:'D'},
    12: {2:'H', 3:'H', 4:'S', 5:'S', 6:'S', 7:'H', 8:'H', 9:'H',10:'H',11:'H'},
    13: {2:'S', 3:'S', 4:'S', 5:'S', 6:'S', 7:'H', 8:'H', 9:'H',10:'H',11:'H'},
    14: {2:'S', 3:'S', 4:'S', 5:'S', 6:'S', 7:'H', 8:'H', 9:'H',10:'H',11:'H'},
    15: {2:'S', 3:'S', 4:'S', 5:'S', 6:'S', 7:'H', 8:'H', 9:'H',10:'H',11:'H'},
    16: {2:'S', 3:'S', 4:'S', 5:'S', 6:'S', 7:'H', 8:'H', 9:'H',10:'H',11:'H'},
    17: {2:'S', 3:'S', 4:'S', 5:'S', 6:'S', 7:'S', 8:'S', 9:'S',10:'S',11:'S'},
    18: {2:'S', 3:'S', 4:'S', 5:'S', 6:'S', 7:'S', 8:'S', 9:'S',10:'S',11:'S'},
    19: {2:'S', 3:'S', 4:'S', 5:'S', 6:'S', 7:'S', 8:'S', 9:'S',10:'S',11:'S'},
    20: {2:'S', 3:'S', 4:'S', 5:'S', 6:'S', 7:'S', 8:'S', 9:'S',10:'S',11:'S'},
    21: {2:'S', 3:'S', 4:'S', 5:'S', 6:'S', 7:'S', 8:'S', 9:'S',10:'S',11:'S'},
}

# ── Soft total decision table ─────────────────────────────────────────────────
# Soft total = Ace counted as 11 + other card (e.g. A+7 = soft 18)
_SOFT_TABLE: dict[int, dict[int, str]] = {
    #       2    3    4    5    6    7    8    9   10   11(A)
    13: {2:'H', 3:'H', 4:'H', 5:'D', 6:'D', 7:'H', 8:'H', 9:'H',10:'H',11:'H'},
    14: {2:'H', 3:'H', 4:'H', 5:'D', 6:'D', 7:'H', 8:'H', 9:'H',10:'H',11:'H'},
    15: {2:'H', 3:'H', 4:'D', 5:'D', 6:'D', 7:'H', 8:'H', 9:'H',10:'H',11:'H'},
    16: {2:'H', 3:'H', 4:'D', 5:'D', 6:'D', 7:'H', 8:'H', 9:'H',10:'H',11:'H'},
    17: {2:'H', 3:'D', 4:'D', 5:'D', 6:'D', 7:'H', 8:'H', 9:'H',10:'H',11:'H'},
    18: {2:'S', 3:'D', 4:'D', 5:'D', 6:'D', 7:'S', 8:'S', 9:'H',10:'H',11:'H'},
    19: {2:'S', 3:'S', 4:'S', 5:'S', 6:'S', 7:'S', 8:'S', 9:'S',10:'S',11:'S'},
    20: {2:'S', 3:'S', 4:'S', 5:'S', 6:'S', 7:'S', 8:'S', 9:'S',10:'S',11:'S'},
}

# ── Pair splitting table ──────────────────────────────────────────────────────
# Key: card value (pip value of one card in the pair)
_PAIR_TABLE: dict[int, dict[int, str]] = {
    #         2    3    4    5    6    7    8    9   10   11(A)
    2:  {2:'P', 3:'P', 4:'P', 5:'P', 6:'P', 7:'P', 8:'H', 9:'H',10:'H',11:'H'},
    3:  {2:'P', 3:'P', 4:'P', 5:'P', 6:'P', 7:'P', 8:'H', 9:'H',10:'H',11:'H'},
    4:  {2:'H', 3:'H', 4:'H', 5:'P', 6:'P', 7:'H', 8:'H', 9:'H',10:'H',11:'H'},
    5:  {2:'D', 3:'D', 4:'D', 5:'D', 6:'D', 7:'D', 8:'D', 9:'D',10:'H',11:'H'},  # treat as 10 hard
    6:  {2:'P', 3:'P', 4:'P', 5:'P', 6:'P', 7:'H', 8:'H', 9:'H',10:'H',11:'H'},
    7:  {2:'P', 3:'P', 4:'P', 5:'P', 6:'P', 7:'P', 8:'H', 9:'H',10:'H',11:'H'},
    8:  {2:'P', 3:'P', 4:'P', 5:'P', 6:'P', 7:'P', 8:'P', 9:'P',10:'P',11:'P'},  # always split
    9:  {2:'P', 3:'P', 4:'P', 5:'P', 6:'P', 7:'S', 8:'P', 9:'P',10:'S',11:'S'},
    10: {2:'S', 3:'S', 4:'S', 5:'S', 6:'S', 7:'S', 8:'S', 9:'S',10:'S',11:'S'},  # never split tens
    11: {2:'P', 3:'P', 4:'P', 5:'P', 6:'P', 7:'P', 8:'P', 9:'P',10:'P',11:'P'},  # always split aces
}
# fmt: on


# ── Card-counting index deviations (subset of Illustrious 18) ─────────────────
# Each entry: (player_total, dealer_up, min_true_count, is_soft) → action override
_COUNT_DEVIATIONS: list[tuple] = [
    (16, 10, 0,  False, "S"),   # Stand 16 vs 10 at TC >= 0
    (15, 10, 4,  False, "S"),   # Stand 15 vs 10 at TC >= 4
    (12,  3, 2,  False, "S"),   # Stand 12 vs 3  at TC >= 2
    (12,  2, 3,  False, "S"),   # Stand 12 vs 2  at TC >= 3
    (10, 10, 4,  False, "D"),   # Double 10 vs 10 at TC >= 4
    (10, 11, 3,  False, "D"),   # Double 10 vs A  at TC >= 3
    (11, 11, 1,  False, "D"),   # Double 11 vs A  at TC >= 1
    (9,  2,  1,  False, "D"),   # Double 9  vs 2  at TC >= 1
    (9,  7,  3,  False, "D"),   # Double 9  vs 7  at TC >= 3
]


def _hand_value(cards: list[int]) -> int:
    total = sum(cards)
    aces = cards.count(11)
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total


def _is_soft(cards: list[int]) -> bool:
    return 11 in cards and _hand_value(cards) <= 21


def decide(
    strategy: Strategy,
    player_cards: list[int],
    dealer_up: int,
    true_count: float = 0.0,
) -> str:
    """
    Return the recommended action for a given game state.

    Returns:
        'H'  — Hit
        'S'  — Stand
        'D'  — Double (fall back to Hit if not available)
        'P'  — Split
    """
    total = _hand_value(player_cards)
    can_double = len(player_cards) == 2
    can_split  = len(player_cards) == 2 and player_cards[0] == player_cards[1]

    # ── Simple alternative strategies ─────────────────────────────────────────
    if strategy == Strategy.ALWAYS17:
        return "S" if total >= 17 else "H"

    if strategy == Strategy.MIMIC:
        return "S" if total >= 17 else "H"

    if strategy == Strategy.NEVER_BUST:
        return "S" if total >= 12 else "H"

    if strategy == Strategy.RANDOM:
        import random
        return random.choice(["H", "S"])

    # ── Basic strategy + counting deviations ──────────────────────────────────
    # Check counting deviations first (higher priority)
    if strategy == Strategy.BASIC:
        soft = _is_soft(player_cards)
        for p_tot, d_up, min_tc, is_soft_dev, action in _COUNT_DEVIATIONS:
            if (total == p_tot and dealer_up == d_up
                    and true_count >= min_tc and soft == is_soft_dev):
                if action == "D" and not can_double:
                    return "H"
                return action

        # Pairs
        if can_split and player_cards[0] in _PAIR_TABLE:
            action = _PAIR_TABLE[player_cards[0]].get(dealer_up, "H")
            if action == "P":
                return "P"

        # Soft totals
        if _is_soft(player_cards):
            soft_total = total  # already has ace counted as 11
            if soft_total in _SOFT_TABLE:
                action = _SOFT_TABLE[soft_total].get(dealer_up, "H")
                if action == "D" and not can_double:
                    return "H"
                return action
            return "S" if soft_total >= 19 else "H"

        # Hard totals
        hard_total = min(total, 21)
        if hard_total in _HARD_TABLE:
            action = _HARD_TABLE[hard_total].get(dealer_up, "H")
            if action == "D" and not can_double:
                return "H"
            return action

        return "S" if total >= 17 else "H"

    return "H"


def get_strategy_table(strategy: Strategy) -> dict:
    """Return the hard/soft tables for display purposes."""
    return {
        "hard": _HARD_TABLE,
        "soft": _SOFT_TABLE,
        "pair": _PAIR_TABLE,
        "deviations": _COUNT_DEVIATIONS,
    }
