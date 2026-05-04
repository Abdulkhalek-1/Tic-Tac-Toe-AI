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
            return v.value if v is not None else str(i + 1)

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
