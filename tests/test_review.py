"""Regression checks for the supplied game, evidence, and bounded query routes."""
from pathlib import Path

import chess
import pytest
from fastapi.testclient import TestClient

import review
from app import app, engine_path

client = TestClient(app)


def test_loaded_game_and_final_defense():
    game = client.get('/api/review/game').json()
    assert len(game['moves']) == 38
    assert game['headers']['White'] == 'Mauricio0120'
    assert game['headers']['Result'] == '0-1'
    final = game['positions'][-1]
    assert final['check'] and not final['checkmate']
    assert set(final['legal']) == {'c2b3', 'c2c1', 'c2b1', 'e2d2'}
    board = review.board_for(game['moves'])
    for san in ['Qxd2', 'Qxf3', 'gxf3', 'exd2', 'Kxd2']:
        board.push_san(san)
    assert len(board.pieces(chess.PAWN, chess.WHITE)) == 5
    assert len(board.pieces(chess.PAWN, chess.BLACK)) == 6
    assert game['positions'][18]['legal'] == ['e1e2']


def test_root_page_retains_approved_layout():
    response = client.get('/')
    assert response.content == Path('IAjedrez_prototipo_interactivo.html').read_bytes()
    assert '/static/review.js' in response.text
    assert client.get('/demo').status_code == 200


@pytest.mark.parametrize('white,best,played,expected', [(True,100,-100,200),(False,-100,100,200),(True,100,110,0)])
def test_score_perspective(white, best, played, expected):
    assert review.compare_scores(dict(cp_white=best,mate_white=None), dict(cp_white=played,mate_white=None), white)['loss_cp'] == expected


def test_mates_not_subtracted_as_centipawns():
    result = review.compare_scores(dict(cp_white=0,mate_white=None), dict(cp_white=None,mate_white=-3), True)
    assert result['loss_cp'] is None
    assert result['kind'] == 'Permite mate'


def test_missing_engine_and_bad_requests(monkeypatch):
    monkeypatch.setattr('app.engine_path', lambda: None)
    for url, payload in [('/api/review/analyze', {}),('/api/review/query', {'question':'¿Cuál fue mi error?'}),('/api/review/compare', {'moves':[], 'candidate':'e2e4'})]:
        result = client.post(url, json=payload)
        assert result.status_code == 503
        assert 'Stockfish' in result.json()['detail']
    assert client.post('/api/review/query', json={'question':' ','ply':0}).status_code == 422
    assert client.post('/api/review/query', json={'question':'hola','ply':39}).status_code == 422
    assert client.post('/api/review/compare', json={'candidate':'garbage'}).status_code == 422


@pytest.fixture(scope='module')
def real_evidence():
    path = engine_path()
    if not path:
        pytest.skip('Stockfish no instalado')
    return path, review.analyze_game(path)


def test_real_engine_variants_and_comparisons(real_evidence):
    _, report = real_evidence
    game = review.load_game()
    assert len(report['rows']) == 19
    assert 'Stockfish' in report['engine']
    assert {r['ply'] for r in report['rows']} == set(range(1,39,2))
    for row in report['rows']:
        assert row['played']['pv'][0] == game['moves'][row['ply']-1]
        for key in ['best','played']:
            board = review.board_for(game['moves'][:row['ply']-1])
            for move in row[key]['pv']:
                board.push_uci(move)
            assert row[key]['depth'] > 0
    assert report['qf3']['comparison']['best']['pv'][0] != 'd1f3'
    assert report['final']['best']['pv'][0] == 'e2d2'
    assert report['final']['material']['white']['P'] == 5
    assert report['final']['material']['black']['P'] == 6


def test_queries_are_grounded_and_unknown_is_explicit(real_evidence):
    path, report = real_evidence
    answer = review.query(path, '¿Cuál fue mi error en esta partida?', 0)
    assert answer['target_ply'] == report['ranking'][0]['ply']
    assert answer['supported']
    for question, target in [('¿Fue 9. Nd2 el primer error?',17),('¿Era mejor 9. Qf3?',17),('¿Era mate al final?',38)]:
        answer = review.query(path, question, 17)
        assert answer['target_ply'] == target
        assert answer['supported']
        for line in answer['lines']:
            review.board_for(review.load_game()['moves'][:line['base']] + line['moves'])
    answer = review.query(path, 'Quiero comprar un telescopio', 17)
    assert not answer['supported']
    assert not answer['lines']
    assert 'No he validado' in ' '.join(answer['paragraphs'])
    pasted = review.query(path, '¿Cuál fue mi error?\n'+review.load_game()['pgn'], 0)
    assert pasted['supported']
    with pytest.raises(ValueError, match='no coincide'):
        review.query(path, '¿Cuál fue mi error?\n[Site "Otra"]\n\n1. e4 e5 0-1', 0)


def test_practice_real_engine_and_illegal_move(real_evidence):
    path, _ = real_evidence
    moves = review.load_game()['moves'][:16]
    result = review.practice(path, moves, 'd1f3')
    assert result['played']['pv'][0] == 'd1f3'
    assert result['position']['pieces']['f3'] == 'Q'
    assert result['loss_cp'] is not None
    with pytest.raises(ValueError):
        review.practice(path, moves, 'd1d8')
