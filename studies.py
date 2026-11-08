"""Uploaded studies kept in server memory, isolated from the supplied games."""
import io
import secrets
from datetime import datetime, timezone

import chess
import chess.engine
import chess.pgn
import review

STUDIES = {}


class Study:
    def __init__(self, pgn, player_color="white"):
        parsed = chess.pgn.read_game(io.StringIO(pgn))
        board = parsed.board()
        moves, sans, positions = [], [], [review.position(board)]
        for move in parsed.mainline_moves():
            sans.append(board.san(move))
            moves.append(move.uci())
            board.push(move)
            positions.append(review.position(board))
        self.player_color = player_color
        self.game = dict(player_color=player_color, pgn=str(parsed), headers=dict(parsed.headers), moves=moves,
                         sans=sans, positions=positions, clocks=[])
        self.report = None

    def load_game(self):
        return self.game

    def analyze_game(self, path):
        with review.ENGINE_LOCK:
            if self.report is not None:
                return self.report
            board = chess.Board()
            rows = []
            with chess.engine.SimpleEngine.popen_uci(path, timeout=15) as engine:
                engine.configure({'Threads': 1, 'Hash': 128})
                for i, uci in enumerate(self.game['moves']):
                    move = chess.Move.from_uci(uci)
                    if board.turn == (self.player_color == "white"):
                        rows.append(dict(ply=i+1, label=review.label(i+1, board.san(move)),
                                         **review.compare(engine, board, move)))
                    board.push(move)
                name = engine.id.get('name', 'Stockfish')
            self.report = dict(engine=name, generated_at=datetime.now(timezone.utc).isoformat(),
                rows=rows, ranking=sorted(rows, key=lambda r:r['priority'], reverse=True),
                settings=dict(depth_target=review.DEPTH, seconds_per_search=review.SECONDS),
                perspective='white', player_color=self.player_color, method='Comparación de las decisiones del lado elegido desde la misma posición; puntuaciones desde blancas, búsqueda limitada.')
            return self.report


def add(pgn, player_color="white"):
    study = Study(pgn, player_color)
    token = 'pgn-' + secrets.token_urlsafe(18)
    if len(STUDIES) >= 100:
        STUDIES.pop(next(iter(STUDIES)))
    STUDIES[token] = study
    return token
