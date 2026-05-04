# Tic-Tac-Toe AI — GitHub Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure the single-file `main.py` into a polished, professionally laid-out Python package with `src/` layout, MIT license, README, and locally-configured ruff/mypy — fixing existing bugs along the way.

**Architecture:** A `tic_tac_toe` package split into three modules with clear boundaries: `engine.py` (immutable `Board`, `Player`, `GameStatus`), `ai.py` (pure `find_best_move` using negamax with `lru_cache`), and `cli.py` (interactive loop). Immutability replaces the broken `@lru_cache` over mutating state in the original.

**Tech Stack:** Python 3.10+, hatchling (build backend), ruff (lint/format, local), mypy (typecheck, local). No tests, no CI.

**Spec:** [docs/superpowers/specs/2026-05-04-github-polish-design.md](../specs/2026-05-04-github-polish-design.md)

**Refinement of spec § "CLI flow":** the spec said "Human is X, AI is O regardless of who moves first." This plan adopts the cleaner interpretation: the first player plays X (per Tic-Tac-Toe convention), the second plays O. The CLI tracks which `Player` enum value is the human. This avoids needing the engine to support an "O moves first" mode.

**No tests:** verification is via inline smoke checks (`python -c "..."` with assertions), `ruff check`, and `mypy`. Per the user's explicit instruction, this project does not include `pytest` or CI.

---

## Task 1: Bootstrap the package skeleton

**Files:**
- Create: `src/tic_tac_toe/__init__.py`
- Create: `pyproject.toml`

- [ ] **Step 1: Create the package directory and `__init__.py`**

```bash
mkdir -p src/tic_tac_toe
```

Create `src/tic_tac_toe/__init__.py` with this content:

```python
"""Unbeatable Tic-Tac-Toe AI using minimax."""

__version__ = "0.1.0"
```

- [ ] **Step 2: Create `pyproject.toml`**

Create `pyproject.toml` at the repo root with this exact content:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "tic-tac-toe-ai"
version = "0.1.0"
description = "Unbeatable Tic-Tac-Toe AI using minimax."
readme = "README.md"
requires-python = ">=3.10"
license = { text = "MIT" }
authors = [{ name = "Abdulkhalek Muhammad" }]

[project.scripts]
tic-tac-toe = "tic_tac_toe.cli:main"

[tool.hatch.build.targets.wheel]
packages = ["src/tic_tac_toe"]

[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.mypy]
strict = true
python_version = "3.10"
files = ["src/tic_tac_toe"]
```

Note: `[tool.hatch.build.targets.wheel]` is required because the package lives under `src/`. README.md doesn't exist yet — that's OK, hatch only reads it at build time, not at install time. (If installation fails on the README, we'll create an empty README.md as a placeholder and replace it in Task 6.)

- [ ] **Step 3: Verify the package is importable**

Run:
```bash
python -c "import sys; sys.path.insert(0, 'src'); import tic_tac_toe; print(tic_tac_toe.__version__)"
```

Expected output: `0.1.0`

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml src/tic_tac_toe/__init__.py
git commit -m "chore: scaffold src/ layout package with pyproject.toml"
```

---

## Task 2: Add `.gitignore` and `LICENSE`

**Files:**
- Create: `.gitignore`
- Create: `LICENSE`

- [ ] **Step 1: Create `.gitignore`**

Create `.gitignore` at the repo root with this exact content:

```
__pycache__/
*.pyc
*.pyo
*.egg-info/
build/
dist/
.venv/
venv/
.mypy_cache/
.ruff_cache/
.idea/
.vscode/
```

- [ ] **Step 2: Create `LICENSE`**

Create `LICENSE` at the repo root with the standard MIT text:

```
MIT License

Copyright (c) 2026 Abdulkhalek Muhammad

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 3: Commit**

```bash
git add .gitignore LICENSE
git commit -m "chore: add .gitignore and MIT LICENSE"
```

---

## Task 3: Implement `engine.py`

**Files:**
- Create: `src/tic_tac_toe/engine.py`

- [ ] **Step 1: Create `engine.py`**

Create `src/tic_tac_toe/engine.py` with this exact content:

```python
from __future__ import annotations

from enum import Enum


class Player(Enum):
    X = "X"
    O = "O"  # noqa: E741


class GameStatus(Enum):
    ONGOING = "ongoing"
    X_WINS = "x_wins"
    O_WINS = "o_wins"
    DRAW = "draw"


class InvalidMoveError(ValueError):
    """Raised when a move is illegal (out of range, occupied, or game over)."""


_LINES: tuple[tuple[int, int, int], ...] = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
)


class Board:
    """Immutable Tic-Tac-Toe board.

    Cells are stored in a 9-tuple indexed 0..8. The CLI numpad position n
    maps to index n - 1, where positions are laid out as::

        7 8 9
        4 5 6
        1 2 3
    """

    __slots__ = ("_cells",)

    def __init__(self, cells: tuple[Player | None, ...] | None = None) -> None:
        if cells is None:
            cells = (None,) * 9
        if len(cells) != 9:
            raise ValueError("Board requires exactly 9 cells")
        self._cells = cells

    @property
    def current_player(self) -> Player:
        x_count = sum(1 for c in self._cells if c is Player.X)
        o_count = sum(1 for c in self._cells if c is Player.O)
        return Player.O if x_count > o_count else Player.X

    @property
    def status(self) -> GameStatus:
        for a, b, c in _LINES:
            first = self._cells[a]
            if first is not None and first is self._cells[b] and first is self._cells[c]:
                return GameStatus.X_WINS if first is Player.X else GameStatus.O_WINS
        if all(c is not None for c in self._cells):
            return GameStatus.DRAW
        return GameStatus.ONGOING

    @property
    def legal_moves(self) -> frozenset[int]:
        if self.status is not GameStatus.ONGOING:
            return frozenset()
        return frozenset(i + 1 for i, c in enumerate(self._cells) if c is None)

    def play(self, pos: int) -> Board:
        if pos < 1 or pos > 9:
            raise InvalidMoveError(f"Position must be 1-9, got {pos}")
        if self.status is not GameStatus.ONGOING:
            raise InvalidMoveError("Game is already over")
        idx = pos - 1
        if self._cells[idx] is not None:
            raise InvalidMoveError(f"Position {pos} is already occupied")
        new_cells = self._cells[:idx] + (self.current_player,) + self._cells[idx + 1 :]
        return Board(new_cells)

    def render(self) -> str:
        def cell(i: int) -> str:
            v = self._cells[i]
            return v.value if v is not None else " "

        return (
            f" {cell(6)} | {cell(7)} | {cell(8)}\n"
            "-----------\n"
            f" {cell(3)} | {cell(4)} | {cell(5)}\n"
            "-----------\n"
            f" {cell(0)} | {cell(1)} | {cell(2)}\n"
        )

    def __hash__(self) -> int:
        return hash(self._cells)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Board):
            return NotImplemented
        return self._cells == other._cells

    def __repr__(self) -> str:
        return f"Board({self._cells!r})"
```

- [ ] **Step 2: Smoke-test the engine**

Run:
```bash
python -c "
import sys; sys.path.insert(0, 'src')
from tic_tac_toe.engine import Board, Player, GameStatus, InvalidMoveError

# Empty board: X to move, all 9 legal moves, ongoing.
b = Board()
assert b.current_player is Player.X
assert b.legal_moves == frozenset(range(1, 10))
assert b.status is GameStatus.ONGOING

# Play X at 5 -> O's turn, 8 legal moves.
b1 = b.play(5)
assert b1.current_player is Player.O
assert b1.legal_moves == frozenset({1, 2, 3, 4, 6, 7, 8, 9})
assert b is not b1, 'Board should be immutable'

# Diagonal win: X at 1, O at 2, X at 5, O at 3, X at 9.
g = Board().play(1).play(2).play(5).play(3).play(9)
assert g.status is GameStatus.X_WINS, g.status

# Invalid moves.
try:
    b.play(0); assert False, 'should reject 0'
except InvalidMoveError: pass
try:
    b.play(10); assert False, 'should reject 10'
except InvalidMoveError: pass
try:
    b.play(5).play(5); assert False, 'should reject occupied'
except InvalidMoveError: pass

# render() is a string, not None.
assert isinstance(b.render(), str)
assert 'X' in b.play(5).render()

# Hashable + equal.
assert hash(Board()) == hash(Board())
assert Board() == Board()
assert Board().play(1) != Board()

print('engine OK')
"
```

Expected output: `engine OK`

- [ ] **Step 3: Commit**

```bash
git add src/tic_tac_toe/engine.py
git commit -m "feat(engine): add immutable Board, Player, GameStatus"
```

---

## Task 4: Implement `ai.py`

**Files:**
- Create: `src/tic_tac_toe/ai.py`

- [ ] **Step 1: Create `ai.py`**

Create `src/tic_tac_toe/ai.py` with this exact content:

```python
from __future__ import annotations

from functools import lru_cache

from .engine import Board, GameStatus, Player


def find_best_move(board: Board) -> int:
    """Return the best legal move for ``board.current_player``.

    Pre-condition: ``board.status is GameStatus.ONGOING``.

    Ties are broken by preferring the lowest-numbered position, so the
    function is deterministic.
    """
    if board.status is not GameStatus.ONGOING:
        raise ValueError("No moves available: game is over")

    best_score = -2
    best_move = -1
    for pos in sorted(board.legal_moves):
        score = -_score(board.play(pos))
        if score > best_score:
            best_score = score
            best_move = pos
    return best_move


@lru_cache(maxsize=None)
def _score(board: Board) -> int:
    """Negamax score from the perspective of ``board.current_player``.

    Returns +1 if the current player wins with optimal play from this
    position, -1 if they lose, 0 for a draw.
    """
    status = board.status
    if status is GameStatus.X_WINS:
        return 1 if board.current_player is Player.X else -1
    if status is GameStatus.O_WINS:
        return 1 if board.current_player is Player.O else -1
    if status is GameStatus.DRAW:
        return 0

    best = -2
    for pos in board.legal_moves:
        s = -_score(board.play(pos))
        if s > best:
            best = s
    return best
```

- [ ] **Step 2: Smoke-test the AI**

The AI must (a) take an immediate winning move, (b) block an opponent threat, (c) draw against itself, and (d) draw or beat the user's existing scenarios. Run:

```bash
python -c "
import sys; sys.path.insert(0, 'src')
from tic_tac_toe.engine import Board, GameStatus, Player
from tic_tac_toe.ai import find_best_move

# 1) AI takes the immediate win.
#    X . X       X is to move. 2 completes the top row.
#    . O .
#    O . .
b = Board().play(1).play(5).play(3).play(7)  # cells: X..XO...O? let's just build it explicitly.
# Build by hand instead, to avoid confusion:
b = Board(( Player.O, None, None,
            None, Player.O, None,
            Player.X, None, Player.X ))
# Numpad 7,8,9 -> indices 6,7,8: positions 7=X, 8=None, 9=X. Position 8 wins.
assert b.current_player is Player.X, b.current_player
assert find_best_move(b) == 8, find_best_move(b)

# 2) AI blocks an opponent's threat.
#    Numpad: O has 1 and 2; X must play 3 to block.
b = Board(( Player.O, Player.O, None,   # idx 0,1,2 = pos 1,2,3
            None,    Player.X, None,
            None,    None,     None ))
assert b.current_player is Player.X
assert find_best_move(b) == 3, find_best_move(b)

# 3) Optimal vs optimal -> draw.
g = Board()
while g.status is GameStatus.ONGOING:
    g = g.play(find_best_move(g))
assert g.status is GameStatus.DRAW, g.status

# 4) Determinism: empty board -> always position 1 (lowest tied position).
assert find_best_move(Board()) == 1

# 5) Refuses to move on a finished game.
try:
    find_best_move(g)
    assert False, 'should refuse'
except ValueError: pass

print('ai OK')
"
```

Expected output: `ai OK`

- [ ] **Step 3: Commit**

```bash
git add src/tic_tac_toe/ai.py
git commit -m "feat(ai): add negamax find_best_move with lru_cache memoization"
```

---

## Task 5: Implement `cli.py` and `__main__.py`

**Files:**
- Create: `src/tic_tac_toe/cli.py`
- Create: `src/tic_tac_toe/__main__.py`

- [ ] **Step 1: Create `cli.py`**

Create `src/tic_tac_toe/cli.py` with this exact content:

```python
from __future__ import annotations

import random
import sys

from .ai import find_best_move
from .engine import Board, GameStatus, Player

HELP_TEXT = """\
Welcome to Tic-Tac-Toe AI.

Enter moves as numbers 1-9 in numpad layout:

     7 | 8 | 9
    -----------
     4 | 5 | 6
    -----------
     1 | 2 | 3

The first player plays X; the second plays O.
"""


def prompt_human_player() -> Player:
    """Ask who goes first. Returns the ``Player`` enum value the human controls."""
    while True:
        try:
            choice = input("Who goes first? [H]uman / [A]I / [R]andom: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            sys.exit(0)
        if choice in ("h", "human", ""):
            return Player.X
        if choice in ("a", "ai"):
            return Player.O
        if choice in ("r", "random"):
            return random.choice([Player.X, Player.O])
        print("Please enter H, A, or R.")


def prompt_move(board: Board) -> int:
    """Read a legal move from the user. Re-prompts on bad input."""
    legal = sorted(board.legal_moves)
    while True:
        try:
            raw = input(f"Your move {legal}: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            sys.exit(0)
        if not raw.isdigit():
            print("Enter a number 1-9.")
            continue
        pos = int(raw)
        if pos not in board.legal_moves:
            print("That position is not available.")
            continue
        return pos


def prompt_play_again() -> bool:
    try:
        answer = input("Play again? [y/N]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False
    return answer in ("y", "yes")


def announce_result(status: GameStatus, human: Player) -> None:
    if status is GameStatus.DRAW:
        print("Draw.")
        return
    human_won = (
        (human is Player.X and status is GameStatus.X_WINS)
        or (human is Player.O and status is GameStatus.O_WINS)
    )
    print("You win!" if human_won else "AI wins!")


def play_one_game(human: Player) -> None:
    board = Board()
    print(board.render())
    while board.status is GameStatus.ONGOING:
        if board.current_player is human:
            pos = prompt_move(board)
        else:
            pos = find_best_move(board)
            print(f"AI plays {pos}.")
        board = board.play(pos)
        print(board.render())
    announce_result(board.status, human)


def main() -> None:
    print(HELP_TEXT)
    while True:
        human = prompt_human_player()
        play_one_game(human)
        if not prompt_play_again():
            break
```

- [ ] **Step 2: Create `__main__.py`**

Create `src/tic_tac_toe/__main__.py` with this exact content:

```python
from .cli import main

main()
```

- [ ] **Step 3: Smoke-test the CLI by piping a scripted game**

We can't fully exercise interactive UX automatically, but we can confirm a full game runs end-to-end without exceptions. Pipe a sequence of inputs:

```bash
printf "h\n5\n1\n9\nn\n" | PYTHONPATH=src python -m tic_tac_toe
```

Expected: the program prints the welcome text, plays a game (human chooses moves 5, 1, 9; AI plays optimally and wins or draws — we don't care which, only that the loop terminates), prints a result line ("You win!" / "AI wins!" / "Draw."), prompts "Play again?", and exits cleanly with status 0.

Verify exit status:
```bash
echo "exit: $?"
```
Expected: `exit: 0`

- [ ] **Step 4: Commit**

```bash
git add src/tic_tac_toe/cli.py src/tic_tac_toe/__main__.py
git commit -m "feat(cli): add interactive game loop with numpad input"
```

---

## Task 6: Write `README.md`

**Files:**
- Create: `README.md`

- [ ] **Step 1: Create `README.md`**

Create `README.md` at the repo root with this exact content:

````markdown
# Tic-Tac-Toe AI

An unbeatable Tic-Tac-Toe AI you can play against in the terminal.
The AI uses the minimax algorithm, so it will never lose — at best
you can force a draw.

## Install

```bash
git clone https://github.com/<your-username>/Tic-Tac-Toe-AI.git
cd Tic-Tac-Toe-AI
pip install -e .
```

Requires Python 3.10 or newer.

## Play

```bash
tic-tac-toe
# or
python -m tic_tac_toe
```

Enter moves using a numpad layout:

```
 7 | 8 | 9
-----------
 4 | 5 | 6
-----------
 1 | 2 | 3
```

You can choose whether you, the AI, or a coin flip moves first. The
first player plays X; the second plays O.

## How it works

The AI evaluates every reachable game state with **minimax** in negamax
form: assume both players play optimally, and pick the move that leads
to the best guaranteed outcome. Because the `Board` is immutable and
hashable, the recursion can be memoized with `functools.lru_cache`, so
the full search runs instantly.

## Project layout

```
src/tic_tac_toe/
├── engine.py    # Board, Player, GameStatus — pure game state
├── ai.py        # find_best_move — pure function
└── cli.py       # interactive loop
```

## License

MIT — see [LICENSE](LICENSE).
````

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add README"
```

---

## Task 7: Final cleanup and quality pass

**Files:**
- Delete: `main.py`

- [ ] **Step 1: Delete the old `main.py`**

```bash
git rm main.py
```

- [ ] **Step 2: Install the package in editable mode and verify the entry point**

```bash
pip install -e .
```

Expected: installs successfully, no errors. Then:

```bash
which tic-tac-toe
```

Expected: prints a path to a `tic-tac-toe` executable in the active environment's `bin/`.

- [ ] **Step 3: Run ruff**

```bash
ruff check .
```

Expected: `All checks passed!` (or no output and exit 0). If issues are reported, fix them — they will most likely be import-order or unused-import issues; address each at its source rather than adding `noqa` comments.

- [ ] **Step 4: Run mypy**

```bash
mypy
```

Expected: `Success: no issues found in <N> source files`. If issues are reported, fix them inline. Common cases:
- Missing return type annotations — add them.
- `Any` leaks — narrow with explicit types.

- [ ] **Step 5: Final end-to-end smoke test**

```bash
printf "a\n5\nn\n" | tic-tac-toe
```

This makes the AI go first (it should play position 1 — the lowest-tied opening), then the human plays position 5, then the AI continues until the game ends, and the play-again prompt receives "n" (exit).

Expected: program prints welcome text, board states, AI moves, a final result, and exits with status 0.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "chore: remove old main.py and finalize polish"
```

---

## Self-Review

**Spec coverage:** Every section of the spec has a corresponding task — file layout (Task 1), engine.py (Task 3), ai.py (Task 4), cli.py + __main__.py (Task 5), pyproject.toml (Task 1), README (Task 6), LICENSE (Task 2), .gitignore (Task 2), main.py removal (Task 7). Quality tools (ruff, mypy) are configured in Task 1 and exercised in Task 7. The spec's "first player" language is refined in the plan header note above.

**Placeholders scan:** No "TBD", "TODO", or "fill in details" markers. Every code step contains the exact code to write. Every command has its expected output.

**Type consistency:** `Board.play` returns `Board`. `find_best_move` takes a `Board` and returns `int`. `Board.legal_moves` returns `frozenset[int]` and is used as such in `cli.py:prompt_move`. `Player` and `GameStatus` enum members are used identically across all three modules. `current_player` is a property in all references.

**One known difference from the spec:** the CLI uses "first player plays X" rather than "human always plays X." This is the cleanest way to support all three of [H]uman/[A]I/[R]andom first-player choices without modifying the engine, and is called out in the header of this plan.
