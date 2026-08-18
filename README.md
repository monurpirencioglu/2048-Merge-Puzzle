# 2048 Quest

A tropical merge puzzle for Android, built solo in Unity.
Tiles merge only when **both value and colour match** — a single rule change
that turns a familiar mechanic into a planning problem.

<p align="center">
  <img src="docs/screen-gameplay.png" width="240">
  <img src="docs/screen-home.png" width="240">
  <img src="docs/screen-win.png" width="240">
</p>

> This is a showcase repository. The full game source is private —
> selected systems are included below to illustrate the approach.

---

## The problem I set out to solve

Most merge puzzles generate boards randomly. That makes them cheap to produce
and impossible to balance: you can't tune difficulty you can't measure, and you
can't promise a player that the level in front of them is even solvable.

I wanted the opposite. Every level in this game is a fixed, hand-verified
puzzle with a known solution and a known minimum move count.

---

## How levels are made

Levels are not authored by hand and they are not random. They come out of a
generate-and-verify pipeline:

```
random candidate  →  BFS solver  →  quality gates  →  difficulty tuning  →  ship
```

**1. Candidate generation.** Tiles are placed in matched pairs so no tile can
ever be stranded without a merge partner. Blockers, obstacles and goals are
derived from what is actually reachable on that board.

**2. Solvability proof.** A breadth-first solver explores the full move tree and
returns the exact minimum number of moves. If it cannot find a solution, the
candidate is discarded. This is not a heuristic — a level ships only when its
optimal is *proven*.

**3. Quality gates.** A candidate is rejected if any of these fail:

| Gate | Why it matters |
|---|---|
| No orphan tiles | A tile that can never merge is visual noise |
| Not solved at start | Trivial levels waste the player's time |
| **No deadly first move** | Every direction must still leave the level winnable |
| Colour rule engaged | Same value, different colour must actually appear |
| Tempting wrong move exists | Without a trap it's a maze, not a puzzle |
| Low solution count | Many solutions means the player stumbles in by accident |

The "deadly move" gate is the one I care about most. A move that quietly makes
a level unwinnable is the worst thing a puzzle can do — the player keeps
playing, loses six moves later, and never learns why.

**4. Difficulty tuning.** This is the part I'd redo first if I started over,
because it changed how I think about difficulty.

Optimal move count is *not* what a player feels. What they feel is how much
room they have to be wrong. So instead of assigning a fixed move budget, each
level is played thousands of times by a simulated **instinct player** — a bot
that merges whatever it can see and never plans ahead. The move limit is then
raised until that bot's win rate lands inside a target band for that slot in
the curve.

The result: puzzles get objectively harder while the player's experience stays
steady.

| Levels | Avg. optimal moves | Instinct-player win rate |
|---|---|---|
| 1–10 | 2.9 | 70% |
| 11–20 | 4.6 | 32% |
| 21–30 | 5.6 | 26% |
| 31–40 | 6.6 | 25% |
| 41–50 | 7.6 | 24% |

Depth nearly triples. Frustration doesn't move.

---

## Design principles the data forced on me

**Introduce mechanics on easy levels.** The first version taught the ice
blocker on a level where two of four opening moves were fatal. Teaching a rule
while punishing exploration is a contradiction. New mechanics now land on
relief levels.

**Buffer is the real difficulty dial.** Two levels with identical optimal move
counts feel completely different at +2 versus +5 spare moves. Depth sets the
ceiling; buffer sets the feeling.

**Boss levels need generous buffers.** Every block-ending level failed its
target band on the first pass. They now get significantly more room than their
depth suggests.

**Show the player what the blocker wants.** Ice hides the tile underneath it,
so the player couldn't tell which colour would break it — an unfair guess.
Blockers now carry a coloured aura and a colour-matched number.

---

## What's in this repository

| Path | What it shows |
|---|---|
| [`solver/Solver.cs`](solver/Solver.cs) | BFS solvability proof used in-game by the Shuffle booster |
| [`solver/engine.py`](solver/engine.py) | Rule-exact Python replica of the game engine |
| [`solver/quality.py`](solver/quality.py) | Quality gates and player simulations |

The Python engine is a line-by-line replica of the C# game logic. It was
validated by re-deriving the optimal move count of every previously existing
level independently — 35 out of 35 matched, which is what made it safe to
generate new content with.

---

## Built with

Unity 6.3 LTS · C# · DOTween · TextMeshPro
Level pipeline in Python · Firebase Analytics · GameAnalytics

## Status

50 levels shipped. Android release in preparation.
