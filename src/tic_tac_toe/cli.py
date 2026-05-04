from __future__ import annotations

import random
import sys
from enum import Enum

from .ai import find_best_move
from .engine import Board, GameStatus, Player

HEADER = "Tic-Tac-Toe AI"
QUIT_INPUTS = frozenset({"q", "quit", "exit"})


class GameMode(Enum):
    VS_AI = "vs_ai"
    PVP = "pvp"


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


def prompt_game_mode() -> GameMode:
    while True:
        choice = _read("Play vs [A]I or another [H]uman? ")
        if choice in ("a", "ai", ""):
            return GameMode.VS_AI
        if choice in ("h", "human"):
            return GameMode.PVP
        print("Please type A or H.")


def prompt_first_player_vs_ai() -> Player:
    """Returns which Player the human controls (X = human first)."""
    while True:
        choice = _read("Who goes first? [Y]ou / [A]I / [R]andom? ")
        if choice in ("y", "you", ""):
            return Player.X
        if choice in ("a", "ai"):
            return Player.O
        if choice in ("r", "random"):
            return random.choice([Player.X, Player.O])
        print("Please type Y, A, or R.")


def prompt_move(board: Board, prompt: str = "Your move? ") -> int:
    while True:
        raw = _read(prompt)
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


def _vs_ai_result_text(status: GameStatus, human: Player) -> str:
    if status is GameStatus.DRAW:
        return "Draw."
    human_won = (
        (human is Player.X and status is GameStatus.X_WINS)
        or (human is Player.O and status is GameStatus.O_WINS)
    )
    return "You win!" if human_won else "AI wins!"


def _pvp_result_text(status: GameStatus) -> str:
    if status is GameStatus.X_WINS:
        return "X wins!"
    if status is GameStatus.O_WINS:
        return "O wins!"
    return "Draw."


def play_vs_ai(human: Player) -> None:
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

    recap.append(_vs_ai_result_text(board.status, human))
    render(board, " ".join(recap))


def play_pvp() -> None:
    board = Board()
    recap: list[str] = []
    while board.status is GameStatus.ONGOING:
        render(board, " ".join(recap))
        recap = []
        mover = board.current_player
        pos = prompt_move(board, f"{mover.value}'s move? ")
        board = board.play(pos)
        recap.append(f"{mover.value} played {pos}.")

    recap.append(_pvp_result_text(board.status))
    render(board, " ".join(recap))


def main() -> None:
    while True:
        render(Board())
        mode = prompt_game_mode()
        if mode is GameMode.VS_AI:
            render(Board())
            human = prompt_first_player_vs_ai()
            play_vs_ai(human)
        else:
            play_pvp()
        if not prompt_play_again():
            print("Bye.")
            return
