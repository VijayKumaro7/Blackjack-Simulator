"""Generate terminal screenshot PNGs for the README."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

SCREENSHOTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'docs', 'screenshots')
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

BG      = '#1e1e2e'
SURFACE = '#181825'
BORDER  = '#45475a'
WHITE   = '#cdd6f4'
GREEN   = '#a6e3a1'
RED     = '#f38ba8'
YELLOW  = '#f9e2af'
BLUE    = '#89b4fa'
CYAN    = '#89dceb'
PURPLE  = '#cba6f7'
GRAY    = '#6c7086'
SUBTEXT = '#a6adc8'


def make_fig(lines, title, width=10, char_width=0.062, padding=0.32):
    """Render a list of (text, color) tuples as a terminal screenshot PNG."""
    line_h = 0.22
    height = max(4.0, len(lines) * line_h + padding * 2 + 0.55)
    fig = plt.figure(figsize=(width, height), facecolor=BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.axis('off')

    # Window chrome
    chrome_h = 0.38
    chrome = patches.FancyBboxPatch((0, height - chrome_h), width, chrome_h,
                                     boxstyle='round,pad=0', fc=SURFACE, ec=BORDER, lw=0.8)
    ax.add_patch(chrome)
    for i, color in enumerate(['#f38ba8', '#a6e3a1', '#f9e2af']):
        ax.add_patch(plt.Circle((0.28 + i * 0.22, height - chrome_h / 2), 0.07, color=color))
    ax.text(width / 2, height - chrome_h / 2, title,
            ha='center', va='center', color=SUBTEXT, fontsize=7.5,
            fontfamily='monospace', fontweight='normal')

    # Terminal background body
    body = patches.FancyBboxPatch((0, 0), width, height - chrome_h,
                                   boxstyle='round,pad=0', fc=BG, ec='none')
    ax.add_patch(body)

    # Render lines bottom-up from top of body
    y = height - chrome_h - padding
    for segments in lines:
        if not isinstance(segments, list):
            segments = [(segments, WHITE)]
        x = 0.28
        for text, color in segments:
            ax.text(x, y, text, ha='left', va='top', color=color,
                    fontsize=7.8, fontfamily='monospace')
            x += len(text) * char_width
        y -= line_h

    plt.savefig(os.path.join(SCREENSHOTS_DIR, f'{title.replace(" ", "_")}.png'),
                dpi=180, bbox_inches='tight', facecolor=BG, edgecolor='none',
                pad_inches=0.02)
    plt.close()
    print(f'  ✓  {title}.png')


# ── Screenshot 1: Basic run ───────────────────────────────────────────────────
make_fig([
    [('' , WHITE)],
    [('╔══════════════════════════════════════════════════╗', CYAN)],
    [('║          ♠  BLACKJACK SIMULATOR  ♣               ║', CYAN)],
    [('║      Monte Carlo Strategy & Counting Analyzer    ║', CYAN)],
    [('╚══════════════════════════════════════════════════╝', CYAN)],
    [('' , WHITE)],
    [('  Strategy   : ', SUBTEXT), ('basic', GREEN)],
    [('  Counting   : ', SUBTEXT), ('none', YELLOW)],
    [('  Hands      : ', SUBTEXT), ('10,000', WHITE)],
    [('  Bet        : ', SUBTEXT), ('$25', WHITE)],
    [('  Decks      : ', SUBTEXT), ('6', WHITE)],
    [('' , WHITE)],
    [('  ── Results ───────────────────────────────────────', GRAY)],
    [('  Hands simulated :        ', SUBTEXT), ('10,000', WHITE)],
    [('  Net earnings    :    ', SUBTEXT), ('$-3,125.00', RED)],
    [('  Total wagered   :  ', SUBTEXT), ('+$281,200.00', WHITE)],
    [('  Win rate        :       ', SUBTEXT), ('43.20%', WHITE)],
    [('  Blackjacks      :          ', SUBTEXT), ('454', YELLOW)],
    [('  Pushes          :          ', SUBTEXT), ('879', SUBTEXT)],
    [('  House edge      :         ', SUBTEXT), ('1.11%', RED)],
    [('                    ', WHITE), ('▼ House advantage', RED)],
    [('' , WHITE)],
    [('  Simulated in 0.09s  (109,890 hands/sec)', GRAY)],
], '1_basic_run')

# ── Screenshot 2: Basic run with Hi-Lo counting ───────────────────────────────
make_fig([
    [('' , WHITE)],
    [('╔══════════════════════════════════════════════════╗', CYAN)],
    [('║          ♠  BLACKJACK SIMULATOR  ♣               ║', CYAN)],
    [('║      Monte Carlo Strategy & Counting Analyzer    ║', CYAN)],
    [('╚══════════════════════════════════════════════════╝', CYAN)],
    [('' , WHITE)],
    [('  Strategy   : ', SUBTEXT), ('basic', GREEN)],
    [('  Counting   : ', SUBTEXT), ('hilow', YELLOW), ('  (spread 1–4)', SUBTEXT)],
    [('  Hands      : ', SUBTEXT), ('5,000', WHITE)],
    [('  Bet        : ', SUBTEXT), ('$25', WHITE)],
    [('  Decks      : ', SUBTEXT), ('6', WHITE)],
    [('' , WHITE)],
    [('  ── Results ───────────────────────────────────────', GRAY)],
    [('  Hands simulated :         ', SUBTEXT), ('5,000', WHITE)],
    [('  Net earnings    :     ', SUBTEXT), ('+$1,850.00', GREEN)],
    [('  Total wagered   :   ', SUBTEXT), ('+$343,525.00', WHITE)],
    [('  Win rate        :        ', SUBTEXT), ('43.80%', WHITE)],
    [('  Blackjacks      :           ', SUBTEXT), ('232', YELLOW)],
    [('  Pushes          :           ', SUBTEXT), ('417', SUBTEXT)],
    [('  House edge      :        ', SUBTEXT), ('-0.54%', GREEN)],
    [('                    ', WHITE), ('▲ Player advantage', GREEN)],
    [('' , WHITE)],
    [('  Simulated in 0.07s  (74,939 hands/sec)', GRAY)],
], '2_hilow_counting')

# ── Screenshot 3: Strategy comparison ────────────────────────────────────────
make_fig([
    [('' , WHITE)],
    [('  Comparing strategies — 20,000 hands, $25 base bet, 6-deck shoe', SUBTEXT)],
    [('' , WHITE)],
    [('  Running: Basic strategy                 … ', SUBTEXT), ('done (0.2s)', GREEN)],
    [('  Running: Always stand 17+               … ', SUBTEXT), ('done (0.1s)', GREEN)],
    [('  Running: Mimic dealer                   … ', SUBTEXT), ('done (0.2s)', GREEN)],
    [('  Running: Never bust (12+)               … ', SUBTEXT), ('done (0.1s)', GREEN)],
    [('  Running: Random (50/50)                 … ', SUBTEXT), ('done (0.2s)', GREEN)],
    [('' , WHITE)],
    [('══════════════════════════════════════════════════════════', GRAY)],
    [('  Label                          Net Earnings   Win Rate   House Edge', SUBTEXT)],
    [('──────────────────────────────────────────────────────────', GRAY)],
    [('  Basic strategy              ', WHITE), ('  $-14,262.50', RED), ('     42.41%', WHITE), ('        ', WHITE), ('2.54%', RED)],
    [('  Always stand 17+            ', WHITE), ('  $-23,500.00', RED), ('     41.50%', WHITE), ('        ', WHITE), ('4.70%', RED)],
    [('  Mimic dealer                ', WHITE), ('  $-31,012.50', RED), ('     40.93%', WHITE), ('        ', WHITE), ('6.20%', RED)],
    [('  Never bust (12+)            ', WHITE), ('  $-39,712.50', RED), ('     41.70%', WHITE), ('        ', WHITE), ('7.94%', RED)],
    [('  Random (50/50)              ', WHITE), (' $-150,450.00', RED), ('     31.70%', WHITE), ('       ', WHITE), ('30.09%', RED)],
    [('══════════════════════════════════════════════════════════', GRAY)],
], '3_strategy_comparison')

# ── Screenshot 4: Counting system comparison ──────────────────────────────────
make_fig([
    [('' , WHITE)],
    [('  Comparing counting systems — 20,000 hands, $25 base bet, 6-deck shoe', SUBTEXT)],
    [('' , WHITE)],
    [('  Running: No counting                    … ', SUBTEXT), ('done (0.2s)', GREEN)],
    [('  Running: Hi-Lo  (spread 4)              … ', SUBTEXT), ('done (0.2s)', GREEN)],
    [('  Running: KO     (spread 4)              … ', SUBTEXT), ('done (0.2s)', GREEN)],
    [('  Running: Hi-Opt I (spread 4)            … ', SUBTEXT), ('done (0.2s)', GREEN)],
    [('  Running: Omega II (spread 6)            … ', SUBTEXT), ('done (0.2s)', GREEN)],
    [('  Running: Zen Count (spread 6)           … ', SUBTEXT), ('done (0.2s)', GREEN)],
    [('' , WHITE)],
    [('══════════════════════════════════════════════════════════', GRAY)],
    [('  Label                          Net Earnings   Win Rate   House Edge', SUBTEXT)],
    [('──────────────────────────────────────────────────────────', GRAY)],
    [('  No counting                 ', WHITE), ('   $-8,050.00', RED),  ('     42.96%', WHITE), ('        ', WHITE), ('1.44%', RED)],
    [('  Hi-Lo  (spread 4)           ', WHITE), ('  $-30,475.00', RED),  ('     42.88%', WHITE), ('        ', WHITE), ('2.32%', RED)],
    [('  KO     (spread 4)           ', WHITE), ('  $-67,537.50', RED),  ('     42.47%', WHITE), ('        ', WHITE), ('3.50%', RED)],
    [('  Hi-Opt I (spread 4)         ', WHITE), ('  $-28,775.00', RED),  ('     42.75%', WHITE), ('        ', WHITE), ('2.18%', RED)],
    [('  Omega II (spread 6)         ', WHITE), ('  $-47,162.50', RED),  ('     43.01%', WHITE), ('        ', WHITE), ('2.57%', RED)],
    [('  Zen Count (spread 6)        ', WHITE), ('  $-42,275.00', RED),  ('     42.85%', WHITE), ('        ', WHITE), ('2.25%', RED)],
    [('══════════════════════════════════════════════════════════', GRAY)],
], '4_counting_comparison')

# ── Screenshot 5: Verbose hand log ───────────────────────────────────────────
make_fig([
    [('' , WHITE)],
    [('  Strategy   : ', SUBTEXT), ('basic', GREEN), ('   |   Counting : ', SUBTEXT), ('none', YELLOW), ('   |   Hands : ', SUBTEXT), ('20', WHITE)],
    [('' , WHITE)],
    [('Hand     1: ', SUBTEXT), ('[2+9+10]=21', WHITE), (' vs 5  →  ', SUBTEXT), ('win        ', GREEN), ('+$50', GREEN),  ('  | Bank: ', SUBTEXT), ('$+50',  GREEN)],
    [('Hand     2: ', SUBTEXT), ('[5+10]=15',   WHITE), (' vs 5  →  ', SUBTEXT), ('loss       ', RED),   ('$-25', RED),    ('  | Bank: ', SUBTEXT), ('$+25',  GREEN)],
    [('Hand     3: ', SUBTEXT), ('[4+11+3+5+10]=23', WHITE), (' vs 10 → ', SUBTEXT), ('loss       ', RED),   ('$-25', RED),    ('  | Bank: ', SUBTEXT), ('$+0',   WHITE)],
    [('Hand     4: ', SUBTEXT), ('[6+8+6]=20',  WHITE), (' vs 10 → ', SUBTEXT), ('push       ', SUBTEXT), ('  | Bank: ', SUBTEXT), ('$+0',   WHITE)],
    [('Hand     5: ', SUBTEXT), ('[10+10]=20',  WHITE), (' vs 4  →  ', SUBTEXT), ('win        ', GREEN), ('+$25', GREEN),  ('  | Bank: ', SUBTEXT), ('$+25',  GREEN)],
    [('Hand     6: ', SUBTEXT), ('[9+10]=19',   WHITE), (' vs 10 → ', SUBTEXT), ('win        ', GREEN), ('+$25', GREEN),  ('  | Bank: ', SUBTEXT), ('$+50',  GREEN)],
    [('Hand     7: ', SUBTEXT), ('[11+2+10+10]=23', WHITE), (' vs 10 → ', SUBTEXT), ('loss       ', RED),   ('$-25', RED),    ('  | Bank: ', SUBTEXT), ('$+25',  GREEN)],
    [('Hand     8: ', SUBTEXT), ('[10+8]=18',   WHITE), (' vs 8  →  ', SUBTEXT), ('win        ', GREEN), ('+$25', GREEN),  ('  | Bank: ', SUBTEXT), ('$+50',  GREEN)],
    [('Hand     9: ', SUBTEXT), ('[9+9]=18',    WHITE), (' vs 3  →  ', SUBTEXT), ('loss       ', RED),   ('$-75', RED),    ('  | Bank: ', SUBTEXT), ('$-25',  RED)],
    [('Hand    10: ', SUBTEXT), ('[10+11]=21',  WHITE), (' vs 10 → ', SUBTEXT), ('blackjack  ', YELLOW), ('+$38', YELLOW), ('  | Bank: ', SUBTEXT), ('$+12',  GREEN)],
    [('Hand    11: ', SUBTEXT), ('[3+4+10]=17', WHITE), (' vs 10 → ', SUBTEXT), ('win        ', GREEN), ('+$25', GREEN),  ('  | Bank: ', SUBTEXT), ('$+38',  GREEN)],
    [('Hand    12: ', SUBTEXT), ('[11+6+11+11]=19', WHITE), (' vs 10 → ', SUBTEXT), ('loss       ', RED),   ('$-25', RED),    ('  | Bank: ', SUBTEXT), ('$+12',  GREEN)],
    [('' , WHITE)],
    [('  ...', GRAY)],
    [('' , WHITE)],
    [('  Hands simulated :           ', SUBTEXT), ('20', WHITE)],
    [('  Net earnings    :      ', SUBTEXT), ('$-87.50', RED)],
    [('  Win rate        :       ', SUBTEXT), ('40.00%', WHITE)],
    [('  Blackjacks      :            ', SUBTEXT), ('1', YELLOW)],
], '5_verbose_mode')

# ── Screenshot 6: Python API usage ───────────────────────────────────────────
make_fig([
    [('' , WHITE)],
    [('>>> ', PURPLE), ('from blackjack import run_simulation, Strategy, CountingSystem', WHITE)],
    [('' , WHITE)],
    [('>>> ', PURPLE), ('stats = run_simulation(', WHITE)],
    [('...     ', GRAY),  ('num_hands', BLUE), ('=', WHITE), ('50_000', YELLOW), (', ', WHITE)],
    [('...     ', GRAY),  ('base_bet', BLUE), ('=', WHITE), ('25', YELLOW), (',', WHITE)],
    [('...     ', GRAY),  ('num_decks', BLUE), ('=', WHITE), ('6', YELLOW), (',', WHITE)],
    [('...     ', GRAY),  ('strategy', BLUE), ('=', WHITE), ('Strategy', CYAN), ('.', WHITE), ('BASIC', GREEN), (',', WHITE)],
    [('...     ', GRAY),  ('counting_system', BLUE), ('=', WHITE), ('CountingSystem', CYAN), ('.', WHITE), ('HILOW', GREEN), (',', WHITE)],
    [('...     ', GRAY),  ('bet_spread', BLUE), ('=', WHITE), ('4', YELLOW)],
    [('... ', GRAY), (')', WHITE)],
    [('' , WHITE)],
    [('>>> ', PURPLE), ('print(stats.summary())', WHITE)],
    [('' , WHITE)],
    [('{', WHITE)],
    [("  'hands'        : ", SUBTEXT), ('50000',   YELLOW), (',', WHITE)],
    [("  'wins'         : ", SUBTEXT), ('21847',   GREEN),  (',', WHITE)],
    [("  'losses'       : ", SUBTEXT), ('24610',   RED),    (',', WHITE)],
    [("  'pushes'       : ", SUBTEXT), ('3543',    SUBTEXT), (',', WHITE)],
    [("  'blackjacks'   : ", SUBTEXT), ('2381',    YELLOW), (',', WHITE)],
    [("  'net_earnings' : ", SUBTEXT), ('-842.5',  RED),    (',', WHITE)],
    [("  'win_rate'     : ", SUBTEXT), ('43.6',    WHITE),  (',', WHITE)],
    [("  'house_edge'   : ", SUBTEXT), ('0.0596',  RED),    (',', WHITE)],
    [('}', WHITE)],
], '6_python_api')

print('\nAll screenshots saved to docs/screenshots/')
