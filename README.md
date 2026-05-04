# Tic-Tac-Toe AI

An unbeatable Tic-Tac-Toe AI you can play against in the terminal.
The AI uses the minimax algorithm, so it will never lose — at best
you can force a draw.

## Install

```bash
git clone https://github.com/Abdulkhalek-1/Tic-Tac-Toe-AI.git
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

```text
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
hashable, the recursion can be memoized with `functools.cache`, so
the full search runs instantly.

## Project layout

```text
src/tic_tac_toe/
├── engine.py    # Board, Player, GameStatus — pure game state
├── ai.py        # find_best_move — pure function
└── cli.py       # interactive loop
```

## License

MIT — see [LICENSE](LICENSE).
