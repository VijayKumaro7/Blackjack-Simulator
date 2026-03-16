"""
Card counting systems module.
Implements Hi-Lo, KO (Knockout), Hi-Opt I, Omega II, and Zen Count systems.
"""

from enum import Enum
from dataclasses import dataclass, field


class CountingSystem(Enum):
    NONE    = "none"
    HILOW   = "hilow"    # Classic Hi-Lo  (balanced)
    KO      = "ko"       # Knockout       (unbalanced — no true count needed)
    HIOPT1  = "hiopt1"   # Hi-Opt I       (balanced, level 1)
    OMEGA2  = "omega2"   # Omega II       (balanced, level 2)
    ZEN     = "zen"      # Zen Count      (balanced, level 2)


# Card counting values per system.
# Keys are card pip values (2–11). 11 = Ace.
# Values are the count tag for that card.
_COUNT_VALUES: dict[CountingSystem, dict[int, int]] = {
    CountingSystem.HILOW: {
        2:+1, 3:+1, 4:+1, 5:+1, 6:+1,
        7: 0, 8: 0, 9: 0,
        10:-1, 11:-1,
    },
    CountingSystem.KO: {
        2:+1, 3:+1, 4:+1, 5:+1, 6:+1, 7:+1,
        8: 0, 9: 0,
        10:-1, 11:-1,
    },
    CountingSystem.HIOPT1: {
        2: 0, 3:+1, 4:+1, 5:+1, 6:+1,
        7: 0, 8: 0, 9: 0,
        10:-1, 11: 0,
    },
    CountingSystem.OMEGA2: {
        2:+1, 3:+1, 4:+2, 5:+2, 6:+2,
        7:+1, 8: 0, 9:-1,
        10:-2, 11: 0,
    },
    CountingSystem.ZEN: {
        2:+1, 3:+1, 4:+2, 5:+2, 6:+2,
        7:+1, 8: 0, 9: 0,
        10:-2, 11:-1,
    },
}

# Initial running count (IRC) for unbalanced systems
_IRC: dict[CountingSystem, int] = {
    CountingSystem.KO: 0,  # Adjust based on num_decks in practice; 0 simplifies
}


@dataclass
class CardCounter:
    """
    Tracks the running count and converts to true count.
    Also handles bet sizing via spread.
    """
    system: CountingSystem
    bet_spread: int = 4
    running_count: int = 0
    cards_seen: int = 0
    _tags: dict = field(default_factory=dict)

    def __post_init__(self):
        self._tags = _COUNT_VALUES.get(self.system, {})

    def update(self, card: int) -> None:
        """Update running count with a newly seen card."""
        self.running_count += self._tags.get(card, 0)
        self.cards_seen += 1

    def true_count(self, remaining_decks: float) -> float:
        """
        Convert running count to true count (per deck remaining).
        For unbalanced systems (KO), returns running count directly.
        """
        if self.system == CountingSystem.KO:
            return float(self.running_count)
        return self.running_count / max(remaining_decks, 0.5)

    def reset(self) -> None:
        """Called on shoe reshuffle."""
        self.running_count = 0
        self.cards_seen = 0

    def size_bet(self, base_bet: float, true_count: float) -> float:
        """
        Calculate bet based on true count and spread.

        Betting ramp:
          TC <= 0         → 1× base (minimum)
          TC 1            → 2× base
          TC 2            → spread/2 × base
          TC 3+           → spread × base (maximum)
        """
        if true_count <= 0:
            return base_bet
        if true_count == 1:
            return base_bet * 2
        if true_count == 2:
            return base_bet * max(2, self.bet_spread // 2)
        return base_bet * self.bet_spread

    @property
    def advantage_description(self) -> str:
        """Human-readable advantage description based on true count."""
        tc = self.running_count  # approximate; use true_count() for accuracy
        if tc >= 4:
            return "Strong player advantage"
        if tc >= 2:
            return "Moderate player advantage"
        if tc >= 0:
            return "Neutral / slight house edge"
        if tc >= -2:
            return "Moderate house edge"
        return "Strong house edge"
