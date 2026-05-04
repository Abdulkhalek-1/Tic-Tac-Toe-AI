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
