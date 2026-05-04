# CLI UX Improvements Design

## Goal

Make the terminal CLI feel polished: the board doubles as the numpad
reference, each turn redraws cleanly, prompts are minimal, and the
user can quit gracefully.

## Pain points addressed

1. Board prints flush against the input prompt — no visual separation.
2. Empty cells are blank, forcing the user to remember the numpad mapping.
3. `Your move [2, 3, 4, 5, 6, 7, 8, 9]:` lists every legal move every turn.
4. Repeated bad input shows the same generic error.
5. No graceful quit — only `Ctrl+C` / `Ctrl+D`.

## Changes

### `engine.py` — `Board.render()`

Empty cells now show their numpad position digit (1–9). Filled cells
show `X` or `O`. The board is its own legend:

```text
 7 | 8 | 9
-----------
 4 | 5 | 6
-----------
 1 | 2 | 3
```

After moves are played, the digit is replaced by `X` or `O`. The
canonical text rendering of the `Board` is the right place for this —
no separate CLI-side renderer.

### `cli.py` — flow

#### Render loop

A single `render(board, status_line)` helper does:

1. Clear screen with ANSI `\033[2J\033[H`.
2. Print header `Tic-Tac-Toe AI` followed by a blank line.
3. Print `board.render()`.
4. Print a blank line, then `status_line` (e.g. `"AI played 8. Your move?"`).

Every turn boundary calls `render()` exactly once. Errors do not
trigger a redraw — they print inline and re-prompt.

#### Welcome / first render

Before any move, the first call to `render()` shows the empty
(numbered) board and the prompt `Who goes first? [H]uman / [A]I / [R]andom?`.
There is no separate welcome text — the numbered board is the
reference.

#### Status lines

| Trigger | Status line shown |
| --- | --- |
| Game start | (just the first prompt) |
| After human move (game continues) | `You played N. AI played M. Your move?` |
| After AI-first move (game continues) | `AI played N. Your move?` |
| Game over, human's move ended in human win | `You played N. You win!` |
| Game over, human's move ended in human loss ‡ | `You played N. AI wins.` |
| Game over, AI's move ended in AI win | `AI played M. AI wins.` |
| Game over, AI's move ended in AI loss ‡ | `AI played M. You win!` |
| Game over, draw on either side's last move | `<who> played N. Draw.` |

‡ Possible only if the AI is configured non-perfectly. With the
current unbeatable AI the human can never win on the AI's last move,
and the AI never picks a losing move. Listed for completeness so the
status-line builder handles every status.

After the result line, the next prompt is `Play again? [y/N]`. The
prompt itself is the status line of the post-game state — no separate
render call is needed for it.

#### Prompts

| Prompt | Text (trailing space is part of the prompt) |
| --- | --- |
| First player | `Who goes first? [H]uman / [A]I / [R]andom?` |
| Move | `Your move?` |
| Play again | `Play again? [y/N]` |

`Your move?` no longer dumps the legal-moves list — the board shows
empty positions.

#### Quit handling

Any prompt accepts `q`, `quit`, or `exit` (case-insensitive). The CLI
prints `Bye.` and calls `sys.exit(0)`. EOF / Ctrl+C does the same.

#### Inline errors

On invalid input, print one error line and re-prompt **without**
clearing the screen. Errors from bottom up:

| Cause | Message |
| --- | --- |
| Non-digit input | `That's not a number 1-9. Type 'q' to quit.` |
| Out of range | `Pick a position 1-9.` |
| Occupied position | `Position N is already taken.` |

The CLI may show the same prompt and one error line repeatedly; the
next valid input triggers a clean redraw.

### Compatibility

ANSI escape codes work in every modern terminal — Linux, macOS, and
Windows Terminal (default on Windows 11). The legacy Windows `cmd.exe`
without VT processing won't clear; it will instead print a stray
escape sequence. Documented as a known limitation; no subprocess
fallback.

## Out of scope

- Color output (no ANSI color codes).
- Mouse support.
- Animation (e.g., a delay before the AI move).
- Configurable AI strength — the AI remains "perfect minimax."

## Migration notes

- `Board.render()` is the only change to `engine.py`. The new output
  is a strict superset of the old (still a 5-line string with the
  same separator pattern).
- `cli.py` gains a `render(board, status_line)` helper, a `clear_screen()`
  helper, and quit handling spread across the three input prompts.
- The HELP_TEXT constant is removed.
