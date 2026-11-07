"""Conversation-specific checks; numeric evidence must come from a real engine."""
import chess
import pytest
from fastapi.testclient import TestClient

import interview
import review
from app import app, engine_path

client = TestClient(app)


def test_interview_metadata_and_selection():
    game = client.get('/api/review/game?game=entrevista').json()
    assert len(game['moves']) == 108
    assert game['headers']['GameId'] == 'sTNRsqPl'
    assert game['headers']['UTCTime'] == '15:49:48'
    assert game['headers']['Termination'] == 'Time forfeit'
    assert game['clocks'][40] == 105
    assert game['clocks'][88] == 6
    assert not game['positions'][-1]['checkmate']
    assert client.get('/api/review/game?game=mauricio').json()['headers']['White'] == 'Mauricio0120'
    assert client.get('/api/review/game?game=unknown').status_code == 422
    assert client.post('/api/review/query?game=mauricio', json={'question':'final','ply':108}).status_code == 422


def test_missing_engine_and_mismatched_pgn(monkeypatch):
    monkeypatch.setattr('app.engine_path', lambda: None)
    response = client.post('/api/review/analyze?game=entrevista', json={})
    assert response.status_code == 503
    assert 'Stockfish' in response.json()['detail']
    with pytest.raises(ValueError, match='no coincide'):
        interview.query('unused', 'Revisa\n'+review.load_game()['pgn'], 0)


@pytest.fixture(scope='module')
def evidence():
    path = engine_path()
    if not path:
        pytest.skip('Stockfish no instalado')
    return path, interview.analyze_game(path)


def test_all_white_moves_have_real_evidence(evidence):
    _, report = evidence
    game = interview.load_game()
    assert 'Stockfish' in report['engine']
    assert len(report['rows']) == 54
    assert {r['ply'] for r in report['rows']} == set(range(1,108,2))
    for row in report['rows']:
        assert row['played']['pv'][0] == game['moves'][row['ply']-1]
        for key in ('best','played'):
            assert row[key]['depth'] > 0
            review.board_for(game['moves'][:row['ply']-1] + row[key]['pv'])
    assert report['queen_check']['played']['pv'][0] == 'b7h1'
    assert report['actual_reply']['played']['pv'][0] == 'f6d5'
    assert {a['san'] for a in report['alternatives']} == {'Nc5','Ng7+'}
    board = review.board_for(game['moves'][:90])
    assert not board.pieces(chess.KNIGHT, chess.WHITE)


def test_conversation_queries_and_combined_objections(evidence):
    path, _ = evidence
    game = interview.load_game()
    for question, target in [('En la jugada 16 activo el alfil de b7',31),
                             ('21.Te2 era para activar mi torre',41),
                             ('29.Kf1 permite Qh1+?',57), ('45.Cc7?',89),
                             ('¿Cómo terminó la partida por tiempo?',108)]:
        answer = interview.query(path, question, 0)
        assert answer['target_ply'] == target and answer['supported']
        for line in answer['lines']:
            review.board_for(game['moves'][:line['base']] + line['moves'])
    answer = interview.query(path, 'Tengo dudas en la jugada 16, 21 y 29', 0)
    assert {line['base'] for line in answer['lines']} >= {30,40,56,57}
    assert 'no es forzada' in ' '.join(answer['paragraphs'])
    assert not interview.query(path, 'Quiero comprar un telescopio', 0)['supported']
    assert interview.query(path, '¿Mis errores?\n'+game['pgn'], 0)['supported']


def test_candidate_from_knight_ending(evidence):
    path, _ = evidence
    game = interview.load_game()
    result = review.practice(path, game['moves'][:88], 'e6c5')
    assert result['position']['pieces']['c5'] == 'N'
    assert result['played']['pv'][0] == 'e6c5'
