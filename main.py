from enum import Enum
from typing import List, Dict
from functools import lru_cache


class InvalidPositionException(Exception):
    def __init__(self, message: str = "Position Should be in range col[0-2]row[0-2]"):
        self.message = message
        super().__init__(self.message)


class Players(Enum):
    X = "X"
    O = "O"  # noqa: E741
    EMPTY = ""


class AITicTacToeGame:
    def __init__(self) -> None:
        self._board: Dict[str, Players] = {
            "22": Players.EMPTY,
            "12": Players.EMPTY,
            "02": Players.EMPTY,
            "01": Players.EMPTY,
            "11": Players.EMPTY,
            "21": Players.EMPTY,
            "00": Players.EMPTY,
            "10": Players.EMPTY,
            "20": Players.EMPTY,
        }
        self._current_turn: Players = Players.X

    def _get_empty_positions(self) -> List[str]:
        return [pos for pos, value in self._board.items() if value is Players.EMPTY]

    def _is_board_full(self) -> bool:
        return all(value != Players.EMPTY for value in self._board.values())

    @lru_cache
    def _minimax(self, player: Players) -> int:
        winner = self.check_winner()
        if winner is Players.X:
            return -1
        elif winner is Players.O:
            return 1
        elif self._is_board_full():
            return 0

        empty_positions = self._get_empty_positions()
        moves: List[Dict[str, int | str]] = []

        for pos in empty_positions:
            self._board[pos] = player
            score = self._minimax(Players.O if player == Players.X else Players.X)
            moves.append({"position": pos, "score": score})
            self._board[pos] = Players.EMPTY

        if player == Players.X:
            best_move = max(moves, key=lambda x: x["score"])
        else:
            best_move = min(moves, key=lambda x: x["score"])

        return int(best_move["score"])

    def _ai_move(self) -> str:
        empty_positions = self._get_empty_positions()
        moves: List[Dict[str, int | str]] = []

        for pos in empty_positions:
            self._board[pos] = Players.O
            score = self._minimax(Players.X)
            moves.append({"position": pos, "score": score})
            self._board[pos] = Players.EMPTY

        best_move = max(moves, key=lambda x: x["score"])
        return str(best_move["position"])

    def get_board(self):
        return self._board

    def print_board(self):
        print(
            f"""\
{self._board["02"].value} | {self._board["12"].value} | {self._board["22"].value}
{self._board["01"].value} | {self._board["11"].value} | {self._board["21"].value}
{self._board["00"].value} | {self._board["10"].value} | {self._board["20"].value}
""",
            end="\n",
        )

    def check_winner(self) -> Players | None | int:
        lines = [
            ["00", "01", "02"],
            ["10", "11", "12"],
            ["20", "21", "22"],
            ["00", "10", "20"],
            ["01", "11", "21"],
            ["02", "12", "22"],
            ["00", "11", "22"],
            ["02", "11", "20"],
        ]
        for line in lines:
            if all(self._board[pos] == Players.X for pos in line):
                return Players.X
            if all(self._board[pos] == Players.O for pos in line):
                return Players.O
        return 1 if self._is_board_full() else None

    def play(self, pos: str):
        if pos not in self._board.keys():
            raise InvalidPositionException()
        if self._board[pos] != Players.EMPTY:
            raise InvalidPositionException("Position already occupied")

        self._board[pos] = Players.X
        if not self._is_board_full():
            ai_pos = self._ai_move()
            self._board[ai_pos] = Players.O


game = AITicTacToeGame()
game.print_board()
while not game.check_winner():
    try:
        pos = input("Enter pos: ")
        game.play(pos)
        game.print_board()
    except (InvalidPositionException, ValueError) as e:
        print(e)

print(game.check_winner())
