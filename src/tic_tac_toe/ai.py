from __future__ import annotations

from functools import cache

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


@cache
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
