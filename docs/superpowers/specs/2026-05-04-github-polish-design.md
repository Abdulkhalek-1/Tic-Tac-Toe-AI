# Tic-Tac-Toe AI — GitHub Polish Design

## Goal

Turn the current single-file `main.py` into a small, well-structured Python
project that looks professional on GitHub. Personal-project polish: clean
code, conventional packaging, working as both a CLI and an importable
library — but without testing or CI infrastructure.

## Scope

**In scope:**
- Restructure into a `src/` layout package: `tic_tac_toe.engine`, `tic_tac_toe.ai`, `tic_tac_toe.cli`.
- Fix bugs in the existing implementation (see "Bugs fixed" below).
- Improve UX: numpad-style coordinates, choose first player, play-again loop, friendly result messages.
- Add `pyproject.toml` (hatchling), with ruff and mypy configured for local use.
- Add `README.md`, MIT `LICENSE`, Python `.gitignore`.

**Out of scope:**
- Automated tests (`pytest`).
- Continuous integration (GitHub Actions).
- `pre-commit` hooks.
- GUI / web UI / network play.
- Difficulty levels other than "perfect minimax" (the AI is unbeatable; that is the point).

## Bugs fixed (from current `main.py`)

1. **Broken `@lru_cache` on `_minimax`.** The decorator caches by `(self, player)` while the board mutates between calls — cached scores become stale, and `self` is pinned in memory. Fixed structurally by making `Board` immutable and hashable, so memoization keys correctly include the full board state.
2. **Mixed return type from `check_winner` (`Players | None | int`).** Using `1` as a draw sentinel mixes the enum with an integer. Replaced with a `GameStatus` enum (`ONGOING`, `X_WINS`, `O_WINS`, `DRAW`).
3. **Awkward end-of-game output.** The current `print(game.check_winner())` shows `Players.X` or `1`. Replaced with explicit messages: `"You win!"` / `"AI wins!"` / `"Draw."`.
4. **Confusing position format (`"22"` for col=2, row=2).** Replaced with numpad layout (positions `1`–`9`).
5. **No replay or first-player choice.** Added a CLI prompt for who goes first and a play-again loop after each game.

## File layout

```
Tic-Tac-Toe-AI/
├── src/
│   └── tic_tac_toe/
│       ├── __init__.py
│       ├── __main__.py      # `python -m tic_tac_toe`
│       ├── engine.py        # Board, Player, GameStatus
│       ├── ai.py            # find_best_move(board)
│       └── cli.py           # interactive game loop
├── pyproject.toml           # hatchling build, ruff & mypy config
├── README.md
├── LICENSE                  # MIT, "Abdulkhalek Muhammad", 2026
└── .gitignore               # standard Python
```

## Module: `engine.py`

Pure game state, no I/O.

### Types

```python
class Player(Enum):
    X = "X"
    O = "O"

class GameStatus(Enum):
    ONGOING = "ongoing"
    X_WINS = "x_wins"
    O_WINS = "o_wins"
    DRAW = "draw"

class InvalidMoveError(ValueError):
    """Raised when a move is illegal (out of range, occupied, or game over)."""
```

### `Board` class

Immutable. Internally stores a 9-tuple of `Player | None`, indexed `0..8` corresponding to numpad positions:

```
index 6 7 8       position 7 8 9
index 3 4 5  <==>          4 5 6
index 0 1 2                1 2 3
```

Position `n` maps to index `n - 1`.

**API:**

| Member | Type | Description |
|--------|------|-------------|
| `Board()` | constructor | Empty board, X to move. |
| `current_player` | `Player` | Whose turn it is. |
| `status` | `GameStatus` | Computed each access from current cells. |
| `legal_moves` | `frozenset[int]` | Subset of `{1..9}` that are empty (empty if game is over). |
| `play(pos: int) -> Board` | method | Returns a new `Board` with the move applied. Raises `InvalidMoveError` if `pos` not in `1..9`, occupied, or game already over. |
| `render() -> str` | method | Returns the printable board string. No side effects. |
| `__hash__` / `__eq__` | dunder | Derived from the underlying tuple — required for memoization in `ai.py`. |

**Why immutable:** (a) makes the board hashable for correct memoization, (b) eliminates the class of bugs that came from mutate-then-undo in the original `_minimax`.

## Module: `ai.py`

```python
def find_best_move(board: Board) -> int:
    """Return the best legal move for board.current_player."""
```

- Pure function. Pre-condition: `board.status == GameStatus.ONGOING`.
- Internal recursive `_score(board) -> int` returns:
  - `+1` if `board.current_player` wins from this position with optimal play,
  - `-1` if they lose,
  - `0` for a draw.
- Negamax form: at each level the score is negated when handed back up the recursion. Equivalent to the original "if X then max, else min" but symmetric.
- Memoized with `@lru_cache` keyed on the immutable `Board`. Correct because `Board` never mutates.
- **Tie-breaking:** when multiple moves share the best score, return the lowest-numbered position. Deterministic, no randomness.

## Module: `cli.py`

Interactive game loop.

### Coordinate scheme

Numpad layout (mirrors a numeric keypad):

```
 7 | 8 | 9
-----------
 4 | 5 | 6
-----------
 1 | 2 | 3
```

### Flow

1. Print greeting and the numpad reference once.
2. Prompt: who goes first — `[H]uman / [A]I / [R]andom`. Human is X; AI is O. "First player" only controls whether AI moves before the first human prompt.
3. Loop:
   - Print the board.
   - If it's the human's turn: prompt for a move, validate, apply.
   - Otherwise: compute AI move via `find_best_move`, announce it, apply.
   - If `board.status != ONGOING`, print the final board and break.
4. Announce result: "You win!" / "AI wins!" / "Draw."
5. Prompt "Play again? [y/N]". If yes, restart the loop with a fresh `Board`; else exit.

### Functions

All small, single-purpose:

| Function | Purpose |
|----------|---------|
| `prompt_move(board) -> int` | Input loop with validation; re-prompts on bad input. Handles `EOFError` / `KeyboardInterrupt` as graceful exit. |
| `prompt_first_player() -> Player` | Reads H/A/R, returns the `Player` enum. |
| `prompt_play_again() -> bool` | Reads y/N. Default is no. |
| `announce_result(status: GameStatus) -> None` | Prints the appropriate end-of-game message. |
| `main() -> None` | Wires the above into the full session loop. |

`__main__.py` is a one-liner: `from .cli import main; main()`.

## Packaging: `pyproject.toml`

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

[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.mypy]
strict = true
python_version = "3.10"
```

Notes:
- After `pip install -e .`, the `tic-tac-toe` shell command works in addition to `python -m tic_tac_toe`.
- No `[project.optional-dependencies]` table since there is no automated test/lint workflow.
- ruff and mypy are configured but not enforced — run manually.

## `README.md`

Standard sections, no badges:
- Title + one-line description.
- Install (clone + `pip install -e .`).
- Play (both invocation forms; numpad reference).
- "How it works" (2–3 sentences on minimax + memoization).
- License link.

## `LICENSE`

Standard MIT, year 2026, copyright "Abdulkhalek Muhammad".

## `.gitignore`

Standard Python entries:
```
__pycache__/
*.pyc
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

## Migration notes

- `main.py` at the repository root is removed. Its functionality is split across `engine.py`, `ai.py`, and `cli.py`.
- The original `InvalidPositionException` becomes `InvalidMoveError` (a `ValueError` subclass — more idiomatic) and lives in `engine.py`.
- The original `Players` enum (with three members `X`, `O`, `EMPTY`) is replaced by `Player` (two members: `X`, `O`); empty cells are represented as `None` in the internal board tuple.
