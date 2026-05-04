# CLI UX Improvements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the CLI feel polished — empty cells show their numpad position, the screen redraws cleanly each turn, prompts are minimal, and `q` / Ctrl+C / Ctrl+D exit gracefully.

**Architecture:** Extend `Board.render()` to print numpad digits in empty cells. Refactor `cli.py` around a single `render(board, status_line)` helper that clears the screen and re-paints the header, board, and a one-line summary every turn. A shared `_read()` input helper centralizes quit/EOF handling.

**Tech Stack:** Python 3.10+, ANSI escape codes for screen clearing.

**Spec:** [docs/superpowers/specs/2026-05-04-cli-ux-improvements-design.md](../specs/2026-05-04-cli-ux-improvements-design.md)

**No tests:** verification continues to be inline smoke checks, `ruff check`, and `mypy` per the project's "no automated tests" decision.

---

## Task 1: Update `Board.render()` to show position numbers in empty cells

**Files:**
- Modify: `src/tic_tac_toe/engine.py` (the inner `cell` helper inside `Board.render`)

- [ ] **Step 1: Update the `cell` helper inside `Board.render`**

In `src/tic_tac_toe/engine.py`, replace the body of `render` so empty
cells show the numpad position digit (`i + 1`) instead of a space:

```python
    def render(self) -> str:
        def cell(i: int) -> str:
            v = self._cells[i]
            return v.value if v is not None else str(i + 1)

        return (
            f" {cell(6)} | {cell(7)} | {cell(8)}\n"
            "-----------\n"
            f" {cell(3)} | {cell(4)} | {cell(5)}\n"
            "-----------\n"
            f" {cell(0)} | {cell(1)} | {cell(2)}\n"
        )
```

The only change is the fallback when the cell is empty: `" "` → `str(i + 1)`.

- [ ] **Step 2: Smoke-test the new render**

Run:
```bash
python -c "
import sys; sys.path.insert(0, 'src')
from tic_tac_toe.engine import Board, Player

# Empty board shows the numpad.
empty = Board().render()
assert ' 7 | 8 | 9' in empty
assert ' 4 | 5 | 6' in empty
assert ' 1 | 2 | 3' in empty
assert 'X' not in empty and 'O' not in empty

# After a move, the played cell shows X (or O), other cells still show digits.
b = Board().play(5)
out = b.render()
assert ' 4 | X | 6' in out, out
assert ' 1 | 2 | 3' in out
assert ' 7 | 8 | 9' in out

# After two moves: X at 5, O at 1.
b = Board().play(5).play(1)
out = b.render()
assert ' 4 | X | 6' in out
assert ' O | 2 | 3' in out
print('render OK')
"
```

Expected output: `render OK`

- [ ] **Step 3: Commit**

```bash
git add src/tic_tac_toe/engine.py
git commit -m "feat(engine): render empty cells as numpad position digits"
```

---

## Task 2: Refactor `cli.py` for clear-screen redraw and quit handling

**Files:**
- Modify: `src/tic_tac_toe/cli.py` (full rewrite — old structure replaced)

- [ ] **Step 1: Rewrite `cli.py`**

Replace the entire contents of `src/tic_tac_toe/cli.py` with:

```python
from __future__ import annotations

import random
import sys

from .ai import find_best_move
from .engine import Board, GameStatus, Player

HEADER = "Tic-Tac-Toe AI"
QUIT_INPUTS = frozenset({"q", "quit", "exit"})


def clear_screen() -> None:
    print("\033[2J\033[H", end="")


def render(board: Board, status_line: str = "") -> None:
    clear_screen()
    print(HEADER)
    print()
    print(board.render(), end="")
    print()
    if status_line:
        print(status_line)


def _quit() -> None:
    print("Bye.")
    sys.exit(0)


def _read(prompt: str) -> str:
    """Read input. Quit aliases and EOF/Ctrl+C exit gracefully."""
    try:
        raw = input(prompt).strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        _quit()
        return ""  # unreachable; satisfies type checker
    if raw in QUIT_INPUTS:
        _quit()
    return raw


def prompt_human_player() -> Player:
    while True:
        choice = _read("Who goes first? [H]uman / [A]I / [R]andom? ")
        if choice in ("h", "human", ""):
            return Player.X
        if choice in ("a", "ai"):
            return Player.O
        if choice in ("r", "random"):
            return random.choice([Player.X, Player.O])
        print("Please type H, A, or R.")


def prompt_move(board: Board) -> int:
    while True:
        raw = _read("Your move? ")
        if not raw.isdigit():
            print("That's not a number 1-9. Type 'q' to quit.")
            continue
        pos = int(raw)
        if pos < 1 or pos > 9:
            print("Pick a position 1-9.")
            continue
        if pos not in board.legal_moves:
            print(f"Position {pos} is already taken.")
            continue
        return pos


def prompt_play_again() -> bool:
    answer = _read("Play again? [y/N] ")
    return answer in ("y", "yes")


def _result_text(status: GameStatus, human: Player) -> str:
    if status is GameStatus.DRAW:
        return "Draw."
    human_won = (
        (human is Player.X and status is GameStatus.X_WINS)
        or (human is Player.O and status is GameStatus.O_WINS)
    )
    return "You win!" if human_won else "AI wins!"


def play_one_game(human: Player) -> None:
    board = Board()
    recap: list[str] = []

    if human is Player.O:
        ai_pos = find_best_move(board)
        board = board.play(ai_pos)
        recap.append(f"AI played {ai_pos}.")

    while board.status is GameStatus.ONGOING:
        render(board, " ".join(recap))
        recap = []
        pos = prompt_move(board)
        board = board.play(pos)
        recap.append(f"You played {pos}.")
        if board.status is not GameStatus.ONGOING:
            break
        ai_pos = find_best_move(board)
        board = board.play(ai_pos)
        recap.append(f"AI played {ai_pos}.")

    recap.append(_result_text(board.status, human))
    render(board, " ".join(recap))


def main() -> None:
    while True:
        render(Board())
        human = prompt_human_player()
        play_one_game(human)
        if not prompt_play_again():
            print("Bye.")
            return
```

Notes on the design choices in this code, for reference while reviewing:

- `_read()` is the single point that handles quit aliases and EOF/Ctrl+C, so every prompt gets the same treatment for free.
- `_quit()` calls `sys.exit(0)`. The `return ""` after it in `_read()` is unreachable but keeps mypy happy under strict mode.
- `play_one_game` accumulates a `recap` list of move descriptions so each render call shows what happened since the last one. After the human's move, the AI moves immediately and both lines end up in the same render — the user sees `You played 5. AI played 3.` plus the prompt below.
- Errors inside `prompt_move` print one line and re-prompt without redrawing, so the screen accumulates only invalid attempts until a valid one triggers the next render.

- [ ] **Step 2: Smoke-test the rewritten CLI by piping a scripted game**

Run:
```bash
printf "h\n5\n8\n2\n6\n7\n3\nn\n" | PYTHONPATH=src python -m tic_tac_toe; echo "exit: $?"
```

Expected:
- The output begins with the ANSI escape `\033[2J\033[H` followed by `Tic-Tac-Toe AI`.
- Numpad digits visible in empty cells of the first board.
- Prompts read `Who goes first? [H]uman / [A]I / [R]andom?`, `Your move?`, `Play again? [y/N]`.
- The full game runs to completion (most likely a draw, or AI wins).
- A final result line (`You win!` / `AI wins!` / `Draw.`) appears.
- `Play again? [y/N] n` exits cleanly.
- Last line: `exit: 0`.

- [ ] **Step 3: Smoke-test quit behavior**

Run:
```bash
printf "q\n" | PYTHONPATH=src python -m tic_tac_toe; echo "exit: $?"
```

Expected: program clears screen, shows the empty (numbered) board and `Who goes first?` prompt, the `q` is consumed, prints `Bye.`, exits with `exit: 0`.

Then test mid-game quit:
```bash
printf "h\nquit\n" | PYTHONPATH=src python -m tic_tac_toe; echo "exit: $?"
```

Expected: program reaches the `Your move?` prompt, sees `quit`, prints `Bye.`, exits with `exit: 0`.

- [ ] **Step 4: Smoke-test invalid-input handling**

Run:
```bash
printf "h\nfoo\n0\n5\n5\n1\n9\n2\n3\n4\n6\n7\n8\nn\n" | PYTHONPATH=src python -m tic_tac_toe 2>&1 | tail -40
```

Expected output should contain at some point:
- `That's not a number 1-9. Type 'q' to quit.` (in response to `foo`)
- `Pick a position 1-9.` (in response to `0`)
- `Position 5 is already taken.` (in response to the second `5` — the AI may have taken it, OR the human's first 5 occupied it)

(Exact ordering depends on AI moves; the goal is that all three error messages appear at some point during the run.)

- [ ] **Step 5: Commit**

```bash
git add src/tic_tac_toe/cli.py
git commit -m "feat(cli): clear-screen redraw, simpler prompts, graceful quit"
```

---

## Task 3: Final quality pass

**Files:** none (verification only)

- [ ] **Step 1: Run ruff**

```bash
ruff check .
```

Expected: `All checks passed!`

If issues are reported, fix them at the source. Likely candidates:
- Unused imports — remove them.
- Line length — break the line.

- [ ] **Step 2: Run mypy**

```bash
mypy
```

Expected: `Success: no issues found in 5 source files`

If issues are reported:
- A common one: `_read()` returns `str` but mypy may complain about the `_quit()` branch since `_quit()` is annotated `None` and not `NoReturn`. The `return ""` after `_quit()` handles this. If mypy still complains, annotate `_quit` as `def _quit() -> NoReturn:` and add `from typing import NoReturn`.

- [ ] **Step 3: End-to-end smoke run via the installed entry point**

```bash
printf "a\n5\n3\n2\n4\n6\n7\n8\n9\nn\n" | tic-tac-toe | tail -20
echo "exit: $?"
```

Expected: program plays a full AI-first game, ends with a result line and a `Play again?` prompt, exits with `exit: 0`. The final display should show the AI's last move and the result on the same status line.

- [ ] **Step 4: Commit if any quality fixes were made**

If Steps 1–2 required changes, commit:
```bash
git add -A
git commit -m "chore: ruff/mypy fixes for CLI rewrite"
```

If no changes were needed, skip this step — Tasks 1 and 2 are already
committed.

---

## Self-Review

**Spec coverage:**
- `Board.render()` shows numpad digits in empty cells — Task 1.
- `render(board, status_line)` helper, ANSI clear-screen, header — Task 2 (Step 1, top of file).
- Welcome / first render with empty (numbered) board and `Who goes first?` — Task 2 (`main()` function).
- Status lines table (mid-game and game-end variants) — Task 2 (`play_one_game()` recap accumulation).
- Simplified prompts (`Your move?`, `Who goes first?`, `Play again? [y/N]`) — Task 2.
- Quit handling (`q` / `quit` / `exit` / EOF / Ctrl+C → `Bye.` + exit 0) — Task 2 (`_read()` + `_quit()`).
- Inline error messages without redraw — Task 2 (`prompt_move()`).
- Compatibility note (ANSI escape; modern terminals only) — design only, no implementation needed.
- HELP_TEXT removed — Task 2 (full rewrite drops it).

**Placeholder scan:** No "TBD" / "TODO" / "implement later" markers. Every code step shows the exact code; every command has expected output.

**Type consistency:**
- `render(board: Board, status_line: str = "") -> None` — used the same way in `play_one_game` and `main`.
- `prompt_move(board: Board) -> int`, `prompt_play_again() -> bool`, `prompt_human_player() -> Player` — return types match callers.
- `_read(prompt: str) -> str` — only ever returns a stripped lower-cased non-quit input (or doesn't return, via `_quit()`).
- `_result_text(status: GameStatus, human: Player) -> str` — used in `play_one_game` last line.
