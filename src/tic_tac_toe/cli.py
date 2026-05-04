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
