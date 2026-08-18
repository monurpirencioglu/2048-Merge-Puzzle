"""
Quality gates and player simulations.

A generated candidate is only shipped if it survives every gate here.
The gates encode design decisions, not just correctness — the goal is a
level that teaches something and rewards thinking, not merely one that
happens to be solvable.
"""
import random
from engine import (build_board, solve_optimal, goals_met, move,
                    DIRS, NUMBER)


# ── Correctness gates ────────────────────────────────────────────────

def deadly_moves(board, goals, move_limit):
    """
    Count opening moves that silently make the level unwinnable.

    This is the gate I care about most. A move that quietly kills a level
    is the worst thing a puzzle can do: the player keeps going, loses six
    moves later, and never learns why. Early levels must return 0 here.
    """
    n = 0
    for d in DIRS:
        nb, moved, ib = move(board, d)
        if not moved or goals_met(nb, goals, ib):
            continue
        if solve_optimal(nb, goals, max_depth=move_limit - 1) is None:
            n += 1
    return n


def orphan_tiles(tiles, ice):
    """Tiles with no possible merge partner — pure visual noise."""
    counts = {}
    for t in tiles:
        counts[(t[2], t[3])] = counts.get((t[2], t[3]), 0) + 1
    for f in ice:
        counts[(f[2], f[3])] = counts.get((f[2], f[3]), 0) + 1
    return [k for k, v in counts.items() if v == 1]


# ── Design-quality gates ─────────────────────────────────────────────

def adjacent_colour_traps(tiles):
    """
    Neighbouring tiles with the same value but different colours.

    This is the single most valuable teaching moment in the game: the
    player sees "4" next to "4", swipes expecting a merge, and learns the
    colour rule by discovering it rather than being told.
    """
    grid = {(t[0], t[1]): (t[2], t[3]) for t in tiles}
    n = 0
    for (r, c), (v, col) in grid.items():
        for dr, dc in ((0, 1), (1, 0)):
            other = grid.get((r + dr, c + dc))
            if other and other[0] == v and other[1] != col:
                n += 1
    return n


def tempting_traps(board, goals, optimal):
    """
    Moves that produce a satisfying merge but lead away from the optimal path.

    Without at least one of these, a level is a maze rather than a puzzle —
    the player just follows the only sensible line.
    """
    def numbers(b):
        return sum(1 for row in b for cell in row if cell[0] == NUMBER)

    traps = 0
    for d in DIRS:
        nb, moved, ib = move(board, d)
        if not moved or goals_met(nb, goals, ib):
            continue
        if not (numbers(nb) < numbers(board) or ib > 0):
            continue                      # no merge happened, not tempting
        remaining = solve_optimal(nb, goals, max_depth=optimal)
        if remaining is None or remaining > optimal - 1:
            traps += 1
    return traps


def solution_count(board, goals, depth):
    """How many distinct optimal solutions exist. Many = loose puzzle."""
    count = 0
    stack = [(board, 0, 0)]
    while stack:
        b, ib, d = stack.pop()
        if d == depth:
            continue
        for direction in DIRS:
            nb, moved, dib = move(b, direction)
            if not moved:
                continue
            nib = ib + dib
            if goals_met(nb, goals, nib):
                if d + 1 == depth:
                    count += 1
                continue
            stack.append((nb, nib, d + 1))
    return count


# ── Player simulations ───────────────────────────────────────────────

def instinct_player_winrate(board, goals, move_limit, trials=2000, seed=7):
    """
    Simulates a casual player: merges whatever is visible, never plans ahead.

    This drives difficulty tuning. Optimal move count is not what a player
    feels — what they feel is how much room they have to be wrong. Each
    level's move budget is raised until this number lands in a target band.
    """
    rng = random.Random(seed)

    def numbers(b):
        return sum(1 for row in b for cell in row if cell[0] == NUMBER)

    wins = 0
    for _ in range(trials):
        b, ib = board, 0
        for _ in range(move_limit):
            merging, plain = [], []
            for d in DIRS:
                nb, moved, dib = move(b, d)
                if not moved:
                    continue
                did_merge = numbers(nb) < numbers(b) or dib > 0
                (merging if did_merge else plain).append((nb, dib))
            pool = merging or plain
            if not pool:
                break
            b, dib = rng.choice(pool)
            ib += dib
            if goals_met(b, goals, ib):
                wins += 1
                break
    return wins / trials


def fit_move_budget(board, goals, optimal, target_band, max_extra=12):
    """
    Raise the move limit until the instinct player's win rate enters the band.

    This inverts the usual approach: instead of guessing a buffer and hoping
    it feels right, we state the intended player experience and let the
    budget follow from it.
    """
    lo, hi = target_band
    best = None
    for extra in range(2, max_extra + 1):
        limit = optimal + extra
        rate = instinct_player_winrate(board, goals, limit, trials=900) * 100
        if lo <= rate <= hi:
            return limit, rate
        distance = min(abs(rate - lo), abs(rate - hi))
        if best is None or distance < best[2]:
            best = (limit, rate, distance)
        if rate > hi:
            break                          # already too easy, more won't help
    return best[0], best[1]
