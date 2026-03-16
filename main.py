#!/usr/bin/env python3
"""
Blackjack Simulator — Command Line Interface

Examples:
    python main.py
    python main.py --hands 10000 --strategy basic --count hilow --spread 4
    python main.py --hands 50000 --strategy never_bust --decks 1 --bet 100
    python main.py --compare-strategies
    python main.py --compare-counts
"""

import argparse
import sys
import time
from blackjack import run_simulation, Strategy, CountingSystem


def fmt_money(amount: float) -> str:
    sign = "+" if amount >= 0 else ""
    return f"{sign}${amount:,.2f}"


def fmt_pct(val: float) -> str:
    return f"{val:.2f}%"


def print_banner():
    print()
    print("╔══════════════════════════════════════════════════╗")
    print("║          ♠  BLACKJACK SIMULATOR  ♣               ║")
    print("║      Monte Carlo Strategy & Counting Analyzer    ║")
    print("╚══════════════════════════════════════════════════╝")
    print()


def print_stats(stats, label: str = ""):
    s = stats.summary()
    width = 50
    if label:
        print(f"\n  ── {label} {'─' * (width - len(label) - 5)}")
    print(f"  Hands simulated : {s['hands']:>12,}")
    print(f"  Net earnings    : {fmt_money(s['net_earnings']):>12}")
    print(f"  Total wagered   : {fmt_money(s['total_wagered']):>12}")
    print(f"  Win rate        : {fmt_pct(s['win_rate']):>12}")
    print(f"  Blackjacks      : {s['blackjacks']:>12,}")
    print(f"  Pushes          : {s['pushes']:>12,}")
    print(f"  House edge      : {fmt_pct(s['house_edge']):>12}")
    edge_note = "▲ Player advantage" if s['house_edge'] < 0 else "▼ House advantage"
    print(f"                    {edge_note}")


def run_comparison(mode: str, hands: int, bet: float, decks: int):
    """Compare all strategies or all counting systems."""
    print_banner()

    if mode == "strategies":
        configs = [
            (Strategy.BASIC,      CountingSystem.NONE, 1, "Basic strategy"),
            (Strategy.ALWAYS17,   CountingSystem.NONE, 1, "Always stand 17+"),
            (Strategy.MIMIC,      CountingSystem.NONE, 1, "Mimic dealer"),
            (Strategy.NEVER_BUST, CountingSystem.NONE, 1, "Never bust (12+)"),
            (Strategy.RANDOM,     CountingSystem.NONE, 1, "Random (50/50)"),
        ]
        print(f"  Comparing strategies — {hands:,} hands, ${bet:.0f} base bet, {decks}-deck shoe\n")
    else:
        configs = [
            (Strategy.BASIC, CountingSystem.NONE,   1, "No counting"),
            (Strategy.BASIC, CountingSystem.HILOW,  4, "Hi-Lo  (spread 4)"),
            (Strategy.BASIC, CountingSystem.KO,     4, "KO     (spread 4)"),
            (Strategy.BASIC, CountingSystem.HIOPT1, 4, "Hi-Opt I (spread 4)"),
            (Strategy.BASIC, CountingSystem.OMEGA2, 6, "Omega II (spread 6)"),
            (Strategy.BASIC, CountingSystem.ZEN,    6, "Zen Count (spread 6)"),
        ]
        print(f"  Comparing counting systems — {hands:,} hands, ${bet:.0f} base bet, {decks}-deck shoe\n")

    results = []
    for strategy, counting, spread, label in configs:
        sys.stdout.write(f"  Running: {label:<30} … ")
        sys.stdout.flush()
        t0 = time.time()
        stats = run_simulation(
            num_hands=hands,
            base_bet=bet,
            num_decks=decks,
            strategy=strategy,
            counting_system=counting,
            bet_spread=spread,
        )
        elapsed = time.time() - t0
        sys.stdout.write(f"done ({elapsed:.1f}s)\n")
        results.append((label, stats))

    print("\n" + "═" * 60)
    print(f"  {'Label':<28} {'Net Earnings':>14} {'Win Rate':>10} {'House Edge':>12}")
    print("─" * 60)
    for label, stats in results:
        s = stats.summary()
        print(
            f"  {label:<28} "
            f"{fmt_money(s['net_earnings']):>14} "
            f"{fmt_pct(s['win_rate']):>10} "
            f"{fmt_pct(s['house_edge']):>12}"
        )
    print("═" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Blackjack Monte Carlo simulator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--hands",    type=int,   default=10000, help="Number of hands (default: 10000)")
    parser.add_argument("--bet",      type=float, default=25.0,  help="Base bet in dollars (default: 25)")
    parser.add_argument("--decks",    type=int,   default=6,     help="Number of decks (default: 6)")
    parser.add_argument("--strategy", type=str,   default="basic",
                        choices=["basic", "always17", "mimic", "never_bust", "random"],
                        help="Player strategy (default: basic)")
    parser.add_argument("--count",    type=str,   default="none",
                        choices=["none", "hilow", "ko", "hiopt1", "omega2", "zen"],
                        help="Card counting system (default: none)")
    parser.add_argument("--spread",   type=int,   default=4,
                        help="Bet spread for counting (default: 4)")
    parser.add_argument("--verbose",  action="store_true",
                        help="Print every hand result")
    parser.add_argument("--compare-strategies", action="store_true",
                        help="Compare all strategies and exit")
    parser.add_argument("--compare-counts", action="store_true",
                        help="Compare all counting systems and exit")

    args = parser.parse_args()

    if args.compare_strategies:
        run_comparison("strategies", args.hands, args.bet, args.decks)
        return

    if args.compare_counts:
        run_comparison("counts", args.hands, args.bet, args.decks)
        return

    print_banner()

    strategy_map = {
        "basic":      Strategy.BASIC,
        "always17":   Strategy.ALWAYS17,
        "mimic":      Strategy.MIMIC,
        "never_bust": Strategy.NEVER_BUST,
        "random":     Strategy.RANDOM,
    }
    count_map = {
        "none":   CountingSystem.NONE,
        "hilow":  CountingSystem.HILOW,
        "ko":     CountingSystem.KO,
        "hiopt1": CountingSystem.HIOPT1,
        "omega2": CountingSystem.OMEGA2,
        "zen":    CountingSystem.ZEN,
    }

    strategy  = strategy_map[args.strategy]
    counting  = count_map[args.count]

    print(f"  Strategy   : {args.strategy}")
    print(f"  Counting   : {args.count}" + (f"  (spread 1–{args.spread})" if args.count != "none" else ""))
    print(f"  Hands      : {args.hands:,}")
    print(f"  Bet        : ${args.bet:.0f}")
    print(f"  Decks      : {args.decks}")
    print()

    t0 = time.time()
    stats = run_simulation(
        num_hands=args.hands,
        base_bet=args.bet,
        num_decks=args.decks,
        strategy=strategy,
        counting_system=counting,
        bet_spread=args.spread,
        verbose=args.verbose,
    )
    elapsed = time.time() - t0

    print_stats(stats)
    print(f"\n  Simulated in {elapsed:.2f}s  ({args.hands/elapsed:,.0f} hands/sec)")
    print()


if __name__ == "__main__":
    main()
